import boto3
import datetime
import os

# AWS S3 setup
s3 = boto3.client('s3')
bucket_name = "hasintha-cloudbackup-2025"  # change to your bucket name

# Path to log file (on EC2, this will be /var/log/nginx/access.log)
log_file = "test.log"  # for local testing, we will create this dummy file

# Create timestamped filename for S3
timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
filename_in_s3 = f"access-{timestamp}.log"

# Upload file to S3
s3.upload_file(log_file, bucket_name, filename_in_s3)
print(f"Backup uploaded to s3://{bucket_name}/{filename_in_s3}")
