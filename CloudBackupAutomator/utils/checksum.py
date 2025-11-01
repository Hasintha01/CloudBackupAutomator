"""
Checksum utilities for incremental backups.

Provides file checksum calculation and comparison to enable incremental backups.
"""

import hashlib
import json
import os
from typing import Optional, Dict
from pathlib import Path


def calculate_file_checksum(file_path: str, algorithm: str = 'sha256') -> str:
	"""
	Calculate checksum hash of a file.
	
	Args:
		file_path: Path to the file
		algorithm: Hash algorithm to use (md5, sha1, sha256)
		
	Returns:
		str: Hexadecimal hash string
		
	Raises:
		FileNotFoundError: If file doesn't exist
		
	Example:
		>>> checksum = calculate_file_checksum('backup.log')
		>>> print(f"SHA256: {checksum}")
	"""
	if not os.path.exists(file_path):
		raise FileNotFoundError(f"File not found: {file_path}")
	
	hash_func = hashlib.new(algorithm)
	
	# Read file in chunks to handle large files efficiently
	with open(file_path, 'rb') as f:
		while chunk := f.read(8192):
			hash_func.update(chunk)
	
	return hash_func.hexdigest()


def load_checksums(checksum_file: str = '.backup_checksums.json') -> Dict[str, str]:
	"""
	Load previously stored file checksums.
	
	Args:
		checksum_file: Path to checksum storage file
		
	Returns:
		Dict[str, str]: Dictionary mapping file paths to checksums
	"""
	if not os.path.exists(checksum_file):
		return {}
	
	try:
		with open(checksum_file, 'r') as f:
			return json.load(f)
	except (json.JSONDecodeError, IOError):
		return {}


def save_checksums(checksums: Dict[str, str], 
				   checksum_file: str = '.backup_checksums.json') -> None:
	"""
	Save file checksums to storage.
	
	Args:
		checksums: Dictionary mapping file paths to checksums
		checksum_file: Path to checksum storage file
	"""
	try:
		with open(checksum_file, 'w') as f:
			json.dump(checksums, f, indent=2)
	except IOError as e:
		raise IOError(f"Failed to save checksums: {e}")


def file_has_changed(file_path: str, checksum_file: str = '.backup_checksums.json') -> bool:
	"""
	Check if a file has changed since last backup.
	
	Args:
		file_path: Path to the file to check
		checksum_file: Path to checksum storage file
		
	Returns:
		bool: True if file has changed or is new, False if unchanged
		
	Example:
		>>> if file_has_changed('backup.log'):
		...     print("File needs backup")
		... else:
		...     print("File unchanged, skipping backup")
	"""
	current_checksum = calculate_file_checksum(file_path)
	stored_checksums = load_checksums(checksum_file)
	
	# Convert to absolute path for consistent storage
	abs_path = os.path.abspath(file_path)
	
	# If file is new or checksum differs, it has changed
	if abs_path not in stored_checksums:
		return True
	
	return stored_checksums[abs_path] != current_checksum


def update_checksum(file_path: str, checksum_file: str = '.backup_checksums.json') -> None:
	"""
	Update stored checksum for a file after successful backup.
	
	Args:
		file_path: Path to the file
		checksum_file: Path to checksum storage file
		
	Example:
		>>> # After successful backup
		>>> update_checksum('backup.log')
	"""
	current_checksum = calculate_file_checksum(file_path)
	stored_checksums = load_checksums(checksum_file)
	
	# Convert to absolute path for consistent storage
	abs_path = os.path.abspath(file_path)
	
	stored_checksums[abs_path] = current_checksum
	save_checksums(stored_checksums, checksum_file)


def get_file_info(file_path: str) -> Dict[str, any]:
	"""
	Get comprehensive file information including checksum and metadata.
	
	Args:
		file_path: Path to the file
		
	Returns:
		Dict containing:
			- path: Absolute file path
			- size: File size in bytes
			- checksum: SHA256 checksum
			- modified: Last modification timestamp
			
	Example:
		>>> info = get_file_info('backup.log')
		>>> print(f"Size: {info['size']} bytes, Checksum: {info['checksum']}")
	"""
	abs_path = os.path.abspath(file_path)
	stat = os.stat(abs_path)
	
	return {
		'path': abs_path,
		'size': stat.st_size,
		'checksum': calculate_file_checksum(abs_path),
		'modified': stat.st_mtime
	}
