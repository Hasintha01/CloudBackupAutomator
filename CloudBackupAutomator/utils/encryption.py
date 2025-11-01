"""
Encryption utilities for secure file backup.

This module provides AES-256 encryption for files before uploading to cloud storage.
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


def generate_encryption_key() -> str:
	"""
	Generate a new encryption key.
	
	Returns:
		str: Base64-encoded encryption key suitable for Fernet encryption
		
	Example:
		>>> key = generate_encryption_key()
		>>> print(f"Add this to your .env file: ENCRYPTION_KEY={key}")
	"""
	return Fernet.generate_key().decode('utf-8')


def get_fernet_cipher(encryption_key: Optional[str] = None) -> Fernet:
	"""
	Create a Fernet cipher instance from the encryption key.
	
	Args:
		encryption_key: Base64-encoded encryption key. If None, reads from environment
		
	Returns:
		Fernet: Cipher instance for encryption/decryption
		
	Raises:
		ValueError: If encryption key is not provided or invalid
	"""
	if not encryption_key:
		encryption_key = os.getenv('ENCRYPTION_KEY')
		
	if not encryption_key:
		raise ValueError(
			"Encryption key not found. Generate one using:\n"
			"  python -c 'from CloudBackupAutomator.utils.encryption import generate_encryption_key; "
			"print(generate_encryption_key())'\n"
			"Then add it to your .env file as ENCRYPTION_KEY=<generated_key>"
		)
	
	try:
		return Fernet(encryption_key.encode('utf-8'))
	except Exception as e:
		raise ValueError(f"Invalid encryption key format: {e}")


def encrypt_file(file_path: str, encryption_key: Optional[str] = None) -> str:
	"""
	Encrypt a file and save it with .encrypted extension.
	
	Args:
		file_path: Path to the file to encrypt
		encryption_key: Optional encryption key (reads from env if not provided)
		
	Returns:
		str: Path to the encrypted file
		
	Raises:
		FileNotFoundError: If the input file doesn't exist
		ValueError: If encryption key is invalid
		
	Example:
		>>> encrypted_path = encrypt_file('backup.log')
		>>> print(f"Encrypted file: {encrypted_path}")
	"""
	if not os.path.exists(file_path):
		raise FileNotFoundError(f"File not found: {file_path}")
	
	cipher = get_fernet_cipher(encryption_key)
	encrypted_path = f"{file_path}.encrypted"
	
	# Read and encrypt file
	with open(file_path, 'rb') as f:
		file_data = f.read()
	
	encrypted_data = cipher.encrypt(file_data)
	
	# Write encrypted file
	with open(encrypted_path, 'wb') as f:
		f.write(encrypted_data)
	
	return encrypted_path


def decrypt_file(encrypted_file_path: str, output_path: Optional[str] = None, 
				 encryption_key: Optional[str] = None) -> str:
	"""
	Decrypt an encrypted file.
	
	Args:
		encrypted_file_path: Path to the encrypted file
		output_path: Where to save decrypted file (default: removes .encrypted extension)
		encryption_key: Optional encryption key (reads from env if not provided)
		
	Returns:
		str: Path to the decrypted file
		
	Raises:
		FileNotFoundError: If the encrypted file doesn't exist
		ValueError: If encryption key is invalid
		cryptography.fernet.InvalidToken: If decryption fails (wrong key or corrupted file)
		
	Example:
		>>> decrypted_path = decrypt_file('backup.log.encrypted')
		>>> print(f"Decrypted file: {decrypted_path}")
	"""
	if not os.path.exists(encrypted_file_path):
		raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
	
	cipher = get_fernet_cipher(encryption_key)
	
	# Determine output path
	if not output_path:
		if encrypted_file_path.endswith('.encrypted'):
			output_path = encrypted_file_path[:-10]  # Remove .encrypted extension
		else:
			output_path = f"{encrypted_file_path}.decrypted"
	
	# Read and decrypt file
	with open(encrypted_file_path, 'rb') as f:
		encrypted_data = f.read()
	
	try:
		decrypted_data = cipher.decrypt(encrypted_data)
	except Exception as e:
		raise ValueError(
			f"Decryption failed: {e}\n"
			"This could mean:\n"
			"  1. Wrong encryption key\n"
			"  2. File is corrupted\n"
			"  3. File was not encrypted with this tool"
		)
	
	# Write decrypted file
	with open(output_path, 'wb') as f:
		f.write(decrypted_data)
	
	return output_path
