
# CloudBackupAutomator
**Automated Cloud Backup Solution using AWS EC2 & S3**

---

## 🌟 Project Overview
CloudBackupAutomator is a professional-grade Python project that automates the backup of server logs to AWS S3. It demonstrates hands-on experience with AWS cloud services, Python scripting, virtual environments, and automation practices commonly used in real-world DevOps workflows.

**Key Features:**
- Deploys a web server (Nginx) on AWS EC2.
- Automatically uploads server log files to AWS S3 using a Python script.
- Timestamped backups for versioned storage.
- Cron job integration for scheduled backups.
- Full project structured using virtual environments for Python dependencies.

---

## 🏗 Architecture Diagram
[EC2 Instance] –(Python Script)–> [AWS S3 Bucket]

- EC2 hosts Nginx server and log files.  
- Python script (`backup_to_s3.py`) reads logs and uploads to S3.  
- Cron job triggers automation periodically.  

*(Add a visual diagram screenshot here for LinkedIn)*

---

## ⚡ Prerequisites
- AWS account with **programmatic access** (IAM user with access key & secret key).  
- Ubuntu / Linux environment (or VM).  
- Python 3.12+  
- Virtual Environment (`venv`)  

**AWS Resources Used:**
- EC2 Instance (Ubuntu / Amazon Linux)  
- S3 Bucket for log storage  

**Python Packages:**
- boto3  
- python-dotenv  

---

## 🛠️ Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/Hasintha01/CloudBackupAutomator
cd CloudBackupAutomator
````

2. **Create and activate virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure AWS credentials**
   Create a `.env` file in the root folder:

```
AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_KEY>
AWS_REGION=us-east-1
S3_BUCKET=<YOUR_S3_BUCKET_NAME>
```

5. **Run the backup script manually**

```bash
python scripts/backup_to_s3.py
```

6. **Set up cron job for automation (optional)**

```bash
crontab -e
# Add this line to run hourly:
0 * * * * /home/ubuntu/CloudBackupAutomator/venv/bin/python /home/ubuntu/CloudBackupAutomator/scripts/backup_to_s3.py
```

---

✅ **Demonstrated Skills**

* Cloud Computing – EC2, S3, IAM roles
* Python Scripting – boto3, dotenv
* Automation – Cron jobs for scheduled tasks
* DevOps Practices – Virtual environments, version control, deployment workflow
* Documentation & Project Management – Professional GitHub repo with clear README

---

📌 **Future Enhancements**

* Add Lambda function to automatically stop/start EC2 based on usage or schedule.
* Integrate CloudWatch metrics to trigger backup only when specific conditions are met.
* Add email notifications for backup success/failure.

---

📝 **License**
MIT License


