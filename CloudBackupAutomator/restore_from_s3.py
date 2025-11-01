"""
Restore files from AWS S3 backups.

This script allows you to:
1. List all available backups in your S3 bucket
2. Download and restore specific backups
3. Automatically decrypt files if they were encrypted
"""

import boto3
import os
import logging
from typing import List, Optional, Dict
from datetime import datetime
from dotenv import load_dotenv
from utils.encryption import decrypt_file
from utils.progress import DownloadProgressPercentage

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s %(levelname)s %(message)s',
	handlers=[logging.FileHandler("restore_from_s3.log"), logging.StreamHandler()]
)


def get_s3_client():
	"""
	Create and return an authenticated S3 client using environment variables.
	
	Returns:
		boto3.client: Configured S3 client
		
	Raises:
		ValueError: If required AWS credentials are not set
	"""
	aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
	aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
	aws_region = os.getenv('AWS_REGION', 'us-east-1')
	
	if not aws_access_key or not aws_secret_key:
		raise ValueError(
			"AWS credentials not found. Please set AWS_ACCESS_KEY_ID and "
			"AWS_SECRET_ACCESS_KEY in your .env file or environment variables."
		)
	
	return boto3.client(
		's3',
		aws_access_key_id=aws_access_key,
		aws_secret_access_key=aws_secret_key,
		region_name=aws_region
	)


def list_backups(bucket_name: Optional[str] = None, prefix: str = "") -> List[Dict]:
	"""
	List all backup files in the S3 bucket.
	
	Args:
		bucket_name: S3 bucket name (reads from env if not provided)
		prefix: Optional prefix to filter backups
		
	Returns:
		List[Dict]: List of backup file information including:
			- key: S3 object key (filename)
			- size: File size in bytes
			- last_modified: Last modification timestamp
			- is_encrypted: Whether the file is encrypted
			
	Raises:
		ValueError: If bucket name is not provided and not in environment
	"""
	if not bucket_name:
		bucket_name = os.getenv('S3_BUCKET_NAME')
		
	if not bucket_name:
		raise ValueError("S3_BUCKET_NAME not found in environment variables")
	
	s3 = get_s3_client()
	
	try:
		response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
		
		if 'Contents' not in response:
			logging.info(f"No backups found in bucket '{bucket_name}'")
			return []
		
		backups = []
		for obj in response['Contents']:
			backups.append({
				'key': obj['Key'],
				'size': obj['Size'],
				'last_modified': obj['LastModified'],
				'is_encrypted': obj['Key'].endswith('.encrypted')
			})
		
		# Sort by last modified date (newest first)
		backups.sort(key=lambda x: x['last_modified'], reverse=True)
		
		return backups
		
	except Exception as e:
		logging.error(f"Failed to list backups: {e}")
		raise


def download_backup(s3_key: str, local_path: Optional[str] = None, 
					bucket_name: Optional[str] = None) -> str:
	"""
	Download a backup file from S3.
	
	Args:
		s3_key: The S3 object key (filename) to download
		local_path: Where to save the file locally (default: ./restored/<filename>)
		bucket_name: S3 bucket name (reads from env if not provided)
		
	Returns:
		str: Path to the downloaded file
		
	Raises:
		ValueError: If bucket name is not provided and not in environment
		Exception: If download fails
	"""
	if not bucket_name:
		bucket_name = os.getenv('S3_BUCKET_NAME')
		
	if not bucket_name:
		raise ValueError("S3_BUCKET_NAME not found in environment variables")
	
	# Create restored directory if it doesn't exist
	restore_dir = "restored"
	os.makedirs(restore_dir, exist_ok=True)
	
	# Determine local file path
	if not local_path:
		local_path = os.path.join(restore_dir, os.path.basename(s3_key))
	
	s3 = get_s3_client()
	
	try:
		logging.info(f"Downloading s3://{bucket_name}/{s3_key} to {local_path}...")
		
		# Get file size for progress bar
		response = s3.head_object(Bucket=bucket_name, Key=s3_key)
		file_size = response['ContentLength']
		
		# Download with progress bar
		s3.download_file(
			bucket_name, 
			s3_key, 
			local_path,
			Callback=DownloadProgressPercentage(local_path, file_size)
		)
		
		logging.info(f"✓ Download completed: {local_path}")
		return local_path
		
	except Exception as e:
		logging.error(f"Failed to download backup: {e}")
		raise


def restore_backup(s3_key: str, output_path: Optional[str] = None, 
				   bucket_name: Optional[str] = None, auto_decrypt: bool = True) -> str:
	"""
	Restore a backup file from S3, automatically decrypting if needed.
	
	Args:
		s3_key: The S3 object key (filename) to restore
		output_path: Where to save the restored file (default: ./restored/<filename>)
		bucket_name: S3 bucket name (reads from env if not provided)
		auto_decrypt: Automatically decrypt .encrypted files
		
	Returns:
		str: Path to the restored file
		
	Example:
		>>> restored_file = restore_backup('access-2025-11-01-1200.log.encrypted')
		>>> print(f"File restored to: {restored_file}")
	"""
	# Download the file
	downloaded_file = download_backup(s3_key, output_path, bucket_name)
	
	# Decrypt if needed
	if auto_decrypt and downloaded_file.endswith('.encrypted'):
		try:
			logging.info("File is encrypted. Attempting to decrypt...")
			decrypted_file = decrypt_file(downloaded_file)
			logging.info(f"✓ File decrypted successfully: {decrypted_file}")
			
			# Remove the encrypted file after successful decryption
			os.remove(downloaded_file)
			logging.info(f"✓ Removed encrypted file: {downloaded_file}")
			
			return decrypted_file
			
		except Exception as e:
			logging.error(
				f"Decryption failed: {e}\n"
				f"The encrypted file is still available at: {downloaded_file}"
			)
			return downloaded_file
	
	return downloaded_file


def display_backups(backups: List[Dict]) -> None:
	"""
	Display a formatted list of backups to the console.
	
	Args:
		backups: List of backup dictionaries from list_backups()
	"""
	if not backups:
		print("\n📦 No backups found.")
		return
	
	print(f"\n📦 Found {len(backups)} backup(s):\n")
	print(f"{'#':<4} {'Filename':<50} {'Size':<12} {'Date':<20} {'Encrypted':<10}")
	print("-" * 100)
	
	for idx, backup in enumerate(backups, 1):
		size_mb = backup['size'] / (1024 * 1024)
		size_str = f"{size_mb:.2f} MB" if size_mb > 1 else f"{backup['size'] / 1024:.2f} KB"
		date_str = backup['last_modified'].strftime('%Y-%m-%d %H:%M:%S')
		encrypted_str = "Yes" if backup['is_encrypted'] else "No"
		filename = backup['key'][:47] + "..." if len(backup['key']) > 50 else backup['key']
		
		print(f"{idx:<4} {filename:<50} {size_str:<12} {date_str:<20} {encrypted_str:<10}")


def main() -> None:
	"""
	Main function for interactive backup restoration.
	"""
	try:
		bucket_name = os.getenv('S3_BUCKET_NAME')
		
		if not bucket_name:
			logging.critical(
				"S3_BUCKET_NAME not found in environment variables. "
				"Please create a .env file based on .env.example"
			)
			return
		
		# List all backups
		logging.info(f"Listing backups from bucket: {bucket_name}")
		backups = list_backups(bucket_name)
		
		# Display backups
		display_backups(backups)
		
		if not backups:
			return
		
		# Interactive restoration
		print("\nRestore Options:")
		print("  - Enter a number to restore that backup")
		print("  - Enter 'all' to restore all backups")
		print("  - Enter 'q' to quit")
		
		choice = input("\nYour choice: ").strip().lower()
		
		if choice == 'q':
			print("Exiting...")
			return
		
		if choice == 'all':
			print(f"\n🔄 Restoring all {len(backups)} backup(s)...")
			for backup in backups:
				try:
					restored = restore_backup(backup['key'], bucket_name=bucket_name)
					print(f"✓ Restored: {restored}")
				except Exception as e:
					print(f"✗ Failed to restore {backup['key']}: {e}")
		else:
			try:
				idx = int(choice) - 1
				if 0 <= idx < len(backups):
					backup = backups[idx]
					print(f"\n🔄 Restoring: {backup['key']}")
					restored = restore_backup(backup['key'], bucket_name=bucket_name)
					print(f"\n✓ Successfully restored to: {restored}")
				else:
					print("Invalid backup number!")
			except ValueError:
				print("Invalid input!")
				
	except ValueError as e:
		logging.critical(f"Configuration error: {e}")
	except Exception as e:
		logging.critical(f"Unexpected error: {e}")


if __name__ == "__main__":
	main()
