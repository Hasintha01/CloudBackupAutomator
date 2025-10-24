
import boto3
import datetime
import os
import logging

# Setup logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s %(levelname)s %(message)s',
	handlers=[logging.FileHandler("backup_to_s3.log"), logging.StreamHandler()]
)

def main():
	# AWS S3 setup
	try:
		s3 = boto3.client('s3')
		bucket_name = "hasintha-cloudbackup-2025"  # change to your bucket name
		log_file = "test.log"  # for local testing, we will create this dummy file

		if not os.path.exists(log_file):
			logging.error(f"Log file '{log_file}' does not exist.")
			return

		# Create timestamped filename for S3
		timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
		filename_in_s3 = f"access-{timestamp}.log"

		# Upload file to S3
		try:
			s3.upload_file(log_file, bucket_name, filename_in_s3)
			logging.info(f"Backup uploaded to s3://{bucket_name}/{filename_in_s3}")
		except Exception as e:
			logging.error(f"Failed to upload file to S3: {e}")
	except Exception as e:
		logging.critical(f"Unexpected error: {e}")

if __name__ == "__main__":
	main()
