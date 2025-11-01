"""
Progress tracking utilities for file uploads and downloads.
"""

import os
import sys
from typing import Optional
from tqdm import tqdm


class ProgressPercentage:
	"""
	Progress callback for boto3 file transfers.
	
	Displays a progress bar using tqdm for S3 upload/download operations.
	
	Example:
		>>> s3.upload_file('file.txt', 'bucket', 'key', 
		...                Callback=ProgressPercentage('file.txt'))
	"""
	
	def __init__(self, filename: str, file_size: Optional[int] = None):
		"""
		Initialize progress tracker.
		
		Args:
			filename: Name of the file being transferred (for display)
			file_size: Size of file in bytes (auto-detected if not provided)
		"""
		self._filename = filename
		self._size = file_size or os.path.getsize(filename)
		self._seen_so_far = 0
		self._lock = None
		
		# Create progress bar
		self._pbar = tqdm(
			total=self._size,
			unit='B',
			unit_scale=True,
			unit_divisor=1024,
			desc=f"Uploading {os.path.basename(filename)}",
			ncols=100
		)
	
	def __call__(self, bytes_amount: int) -> None:
		"""
		Update progress bar with transferred bytes.
		
		Args:
			bytes_amount: Number of bytes transferred in this chunk
		"""
		self._seen_so_far += bytes_amount
		self._pbar.update(bytes_amount)
		
		# Close progress bar when complete
		if self._seen_so_far >= self._size:
			self._pbar.close()


class DownloadProgressPercentage:
	"""
	Progress callback for boto3 file downloads.
	
	Example:
		>>> s3.download_file('bucket', 'key', 'local.txt',
		...                  Callback=DownloadProgressPercentage('local.txt', size))
	"""
	
	def __init__(self, filename: str, file_size: int):
		"""
		Initialize download progress tracker.
		
		Args:
			filename: Name of the file being downloaded (for display)
			file_size: Size of file in bytes
		"""
		self._filename = filename
		self._size = file_size
		self._seen_so_far = 0
		
		# Create progress bar
		self._pbar = tqdm(
			total=self._size,
			unit='B',
			unit_scale=True,
			unit_divisor=1024,
			desc=f"Downloading {os.path.basename(filename)}",
			ncols=100
		)
	
	def __call__(self, bytes_amount: int) -> None:
		"""
		Update progress bar with downloaded bytes.
		
		Args:
			bytes_amount: Number of bytes downloaded in this chunk
		"""
		self._seen_so_far += bytes_amount
		self._pbar.update(bytes_amount)
		
		# Close progress bar when complete
		if self._seen_so_far >= self._size:
			self._pbar.close()
