# AWS S3 Setup Guide

## Method 1: AWS Console (Web Interface)

1. **Login to AWS Console**: https://console.aws.amazon.com/
2. **Navigate to S3**: Search for "S3" in the services
3. **Create Bucket**:
   - Click "Create bucket"
   - Choose a unique bucket name (e.g., `your-app-csv-storage-12345`)
   - Select region (e.g., `us-east-1`)
   - Keep default settings for now
   - Click "Create bucket"

## Method 2: AWS CLI (Command Line)

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Create bucket
aws s3 mb s3://your-unique-bucket-name --region us-east-1
```

## Method 3: Python Code (What our app does)

```python
import boto3

s3_client = boto3.client('s3')
bucket_name = 'your-unique-bucket-name'

# Create bucket
s3_client.create_bucket(Bucket=bucket_name)
```

## Important Bucket Naming Rules:
- Must be globally unique across all AWS accounts
- 3-63 characters long
- Only lowercase letters, numbers, and hyphens
- Cannot start/end with hyphen
- Cannot contain consecutive hyphens

## Recommended Naming Pattern:
`company-app-purpose-randomnumber`
Example: `mycompany-csvapp-storage-7829`