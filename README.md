
# CloudBackupAutomator
**Automated Cloud Backup Solution with AWS S3**

---

## 🌟 Project Overview
CloudBackupAutomator is a professional-grade Python application that automates secure file backups to AWS S3. This production-ready solution includes encryption, incremental backups, restore functionality, and comprehensive error handling - demonstrating enterprise-level development practices.

**Key Features:**
- ✅ **Secure Backups**: Optional AES-256 encryption for files before upload
- ✅ **Incremental Backups**: Smart checksum comparison - only uploads changed files
- ✅ **Restore Functionality**: Interactive recovery tool to restore from any backup
- ✅ **Progress Tracking**: Real-time upload/download progress bars
- ✅ **Environment-based Config**: Secure credential management using .env files
- ✅ **Comprehensive Logging**: Detailed logs for monitoring and troubleshooting
- ✅ **Type-safe Code**: Full type hints for better maintainability
- ✅ **Timestamped Backups**: Automatic versioning with timestamps

---

## 🏗 Architecture

```
Local Files → [Checksum] → [Encryption (optional)] → [S3 Upload with Progress]
                                                              ↓
                                                        AWS S3 Bucket
                                                              ↓
                                                   [Restore & Decrypt] → Local Files
```

**Components:**
- `backup_to_s3.py` - Main backup script with encryption and incremental support
- `restore_from_s3.py` - Interactive restore tool with automatic decryption
- `utils/encryption.py` - AES-256 file encryption/decryption utilities
- `utils/checksum.py` - SHA-256 checksums for incremental backups
- `utils/progress.py` - Upload/download progress tracking

---

## ⚡ Prerequisites

- **Python 3.8+** (Python 3.8, 3.9, 3.10, 3.11, or 3.12)
- **AWS Account** with programmatic access (IAM user with S3 permissions)
- **AWS S3 Bucket** for backup storage

**Python Packages** (auto-installed from requirements.txt):
- boto3 - AWS SDK for Python
- python-dotenv - Environment variable management
- cryptography - File encryption
- tqdm - Progress bars

---

## 🛠️ Setup Instructions

### 1. **Clone the repository**
```bash
git clone https://github.com/Hasintha01/CloudBackupAutomator
cd CloudBackupAutomator
```

### 2. **Create and activate virtual environment**

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. **Install dependencies**
```bash
pip install -r CloudBackupAutomator/requirements.txt
```

### 4. **Configure environment variables**

Copy the example environment file and edit it:
```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials and settings:
```ini
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Backup Configuration
BACKUP_FILE_PATH=test.log
ENABLE_ENCRYPTION=false
ENABLE_INCREMENTAL_BACKUP=true

# Optional: Only needed if encryption is enabled
ENCRYPTION_KEY=generate_using_command_below
```

### 5. **Generate encryption key (optional)**

If you want to enable encryption, generate a key and add it to your `.env` file:

**Windows (PowerShell):**
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Linux/Mac:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the generated key to your `.env` file:
```ini
ENABLE_ENCRYPTION=true
ENCRYPTION_KEY=<paste_generated_key_here>
```

---

## 🚀 Usage

### **Backup Files**

Run a manual backup:
```bash
python CloudBackupAutomator/backup_to_s3.py
```

**Features:**
- Automatically skips upload if file hasn't changed (incremental)
- Shows real-time upload progress
- Encrypts file before upload (if enabled)
- Logs all operations to `backup_to_s3.log`

### **Restore Files**

Launch interactive restore tool:
```bash
python CloudBackupAutomator/restore_from_s3.py
```

**Features:**
- Lists all available backups with size and date
- Download individual or all backups
- Automatically decrypts encrypted files
- Shows download progress

### **Automated Backups**

**Linux/Mac (cron):**
```bash
crontab -e
# Add this line to run hourly:
0 * * * * /path/to/venv/bin/python /path/to/CloudBackupAutomator/backup_to_s3.py
```

**Windows (Task Scheduler):**
```powershell
# Run hourly backup
schtasks /create /tn "CloudBackup" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\CloudBackupAutomator\backup_to_s3.py" /sc hourly
```

---

## 📁 Project Structure

```
CloudBackupAutomator/
├── .env.example              # Environment variables template
├── .python-version           # Python version specification
├── README.md                 # This file
├── CloudBackupAutomator/
│   ├── backup_to_s3.py      # Main backup script
│   ├── restore_from_s3.py   # Restore utility
│   ├── requirements.txt     # Python dependencies
│   └── utils/
│       ├── __init__.py
│       ├── checksum.py      # Incremental backup logic
│       ├── encryption.py    # AES-256 encryption
│       └── progress.py      # Progress bars
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use IAM roles** - In production, use EC2 IAM roles instead of access keys
3. **Rotate encryption keys** - Periodically update your encryption key
4. **Limit S3 permissions** - Use least-privilege IAM policies
5. **Enable S3 versioning** - Protect against accidental deletions

---

## ✅ Demonstrated Skills

- **Cloud Computing** - AWS S3, IAM, secure credential management
- **Python Development** - Type hints, docstrings, modular architecture
- **Security** - AES-256 encryption, environment-based secrets
- **DevOps Practices** - Virtual environments, automation, logging
- **Error Handling** - Comprehensive exception handling with actionable messages
- **Documentation** - Professional README, code documentation
- **Best Practices** - Incremental backups, progress tracking, restore capability

---

## 📝 License
MIT License

---

## 👤 Author
**Hasintha**  
GitHub: [@Hasintha01](https://github.com/Hasintha01)

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!




