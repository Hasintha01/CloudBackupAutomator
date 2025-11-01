
import boto3
import datetime
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from utils.encryption import encrypt_file
from utils.progress import ProgressPercentage
from utils.checksum import file_has_changed, update_checksum

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s %(levelname)s %(message)s',
	handlers=[logging.FileHandler("backup_to_s3.log"), logging.StreamHandler()]
)


def get_s3_client():
	"""
	Create and return an authenticated S3 client using environment variables.
	
	Returns:
		boto3.client: Configured S3 client
		
	Raises:
		ValueError: If required AWS credentials are not set in environment variables
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


def validate_environment() -> tuple[str, str]:
	"""
	Validate that all required environment variables are set.
	
	Returns:
		tuple[str, str]: Bucket name and backup file path
		
	Raises:
		ValueError: If required environment variables are missing
	"""
	bucket_name = os.getenv('S3_BUCKET_NAME')
	backup_file = os.getenv('BACKUP_FILE_PATH', 'test.log')
	
	if not bucket_name:
		raise ValueError(
			"S3_BUCKET_NAME not found in environment variables. "
			"Please create a .env file based on .env.example and configure it."
		)
	
	return bucket_name, backup_file


def main() -> None:
	"""
	Main function to backup a file to AWS S3 with timestamped filename.
	
	This function reads configuration from environment variables, validates them,
	and uploads the specified file to S3 with a timestamp in the filename.
	Optionally encrypts the file before upload if ENABLE_ENCRYPTION is true.
	Supports incremental backups - only uploads if file has changed.
	"""
	file_to_upload = None
	encrypted_file_created = False
	
	try:
		# Validate environment variables
		bucket_name, log_file = validate_environment()
		enable_encryption = os.getenv('ENABLE_ENCRYPTION', 'false').lower() == 'true'
		enable_incremental = os.getenv('ENABLE_INCREMENTAL_BACKUP', 'true').lower() == 'true'
		
		# Check if file exists
		if not os.path.exists(log_file):
			logging.error(
				f"Backup file '{log_file}' does not exist. "
				f"Please ensure the file path is correct in your .env file."
			)
			return

		# Check if file has changed (incremental backup)
		if enable_incremental:
			if not file_has_changed(log_file):
				logging.info(f"⏭️  File '{log_file}' unchanged since last backup. Skipping upload.")
				return
			else:
				logging.info(f"📝 File has changed. Proceeding with backup...")

		# Encrypt file if enabled
		if enable_encryption:
			try:
				logging.info("Encryption enabled. Encrypting file before upload...")
				file_to_upload = encrypt_file(log_file)
				encrypted_file_created = True
				logging.info(f"✓ File encrypted successfully: {file_to_upload}")
			except Exception as e:
				logging.error(f"Encryption failed: {e}")
				return
		else:
			file_to_upload = log_file

		# Get authenticated S3 client
		s3 = get_s3_client()
		
		# Create timestamped filename for S3
		timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
		file_basename = os.path.basename(log_file)
		filename_in_s3 = f"{os.path.splitext(file_basename)[0]}-{timestamp}{os.path.splitext(file_basename)[1]}"
		
		# Add .encrypted suffix if file was encrypted
		if enable_encryption:
			filename_in_s3 += ".encrypted"

		# Upload file to S3
		try:
			logging.info(f"Starting backup of '{file_to_upload}' to S3...")
			
			# Upload with progress bar
			s3.upload_file(
				file_to_upload, 
				bucket_name, 
				filename_in_s3,
				Callback=ProgressPercentage(file_to_upload)
			)
			
			logging.info(f"✓ Backup uploaded successfully to s3://{bucket_name}/{filename_in_s3}")
			
			# Update checksum after successful backup
			if enable_incremental:
				update_checksum(log_file)
				logging.info(f"✓ Updated backup checksum for incremental backups")
				
		except Exception as e:
			logging.error(
				f"Failed to upload file to S3: {e}\n"
				f"Please verify:\n"
				f"  1. Your AWS credentials are correct\n"
				f"  2. The S3 bucket '{bucket_name}' exists\n"
				f"  3. You have write permissions to the bucket"
			)
		finally:
			# Clean up temporary encrypted file
			if encrypted_file_created and file_to_upload and os.path.exists(file_to_upload):
				try:
					os.remove(file_to_upload)
					logging.info(f"✓ Cleaned up temporary encrypted file: {file_to_upload}")
				except Exception as e:
					logging.warning(f"Could not remove temporary encrypted file: {e}")
					
	except ValueError as e:
		logging.critical(f"Configuration error: {e}")
	except Exception as e:
		logging.critical(f"Unexpected error: {e}")
		# Clean up on error
		if encrypted_file_created and file_to_upload and os.path.exists(file_to_upload):
			try:
				os.remove(file_to_upload)
			except:
				pass


if __name__ == "__main__":
	main()
