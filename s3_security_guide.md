# S3 Security Best Practices Guide

This document outlines the security measures implemented in your S3 integration to protect data and prevent unauthorized access.

## 🛡️ Security Features Implemented

### 1. **Environment Variable Validation**
- ✅ **Credential Verification**: Validates AWS credentials are present and not placeholder values
- ✅ **Required Variables**: Ensures `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_BUCKET_NAME` are set
- ✅ **Startup Validation**: Fails fast if credentials are missing or invalid

```python
def _validate_credentials(self):
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_BUCKET_NAME']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value in ['your_access_key_here', 'your_secret_key_here']:
            missing_vars.append(var)

    if missing_vars:
        raise Exception(f"Missing AWS environment variables: {', '.join(missing_vars)}")
```

### 2. **File Upload Security**

#### **Path Traversal Prevention**
- ✅ **Filename Sanitization**: Removes dangerous characters like `../`
- ✅ **Basename Only**: Uses only the filename, ignoring directory paths
- ✅ **Safe Characters**: Strips potentially harmful filename components

```python
# Security: Sanitize filename to prevent path traversal
safe_filename = os.path.basename(original_filename).replace('..', '')
```

#### **File Type Validation**
- ✅ **Extension Whitelist**: Only allows `.csv` and `.txt` files
- ✅ **Content-Type Detection**: Automatically determines MIME type
- ✅ **Security Headers**: Sets proper content type for downloads

```python
allowed_extensions = {'.csv', '.txt'}
file_ext = Path(safe_filename).suffix.lower()
if file_ext not in allowed_extensions:
    raise Exception(f"File type not allowed: {file_ext}")
```

#### **File Validation**
- ✅ **Existence Check**: Verifies file exists before upload
- ✅ **Empty File Prevention**: Rejects zero-byte files
- ✅ **Size Logging**: Records file size for audit trail

### 3. **S3 Storage Security**

#### **Encryption at Rest**
- ✅ **AES-256 Encryption**: All files encrypted server-side in S3
- ✅ **AWS Managed Keys**: Uses AWS-managed encryption keys
- ✅ **Automatic Encryption**: Applied to all uploads

```python
ExtraArgs={
    'ServerSideEncryption': 'AES256',  # Encrypt at rest
    'ACL': 'private'  # Ensure file is private
}
```

#### **Access Control**
- ✅ **Private ACL**: All files are private by default
- ✅ **No Public Access**: Files cannot be accessed without credentials
- ✅ **Bucket Policies**: Only authorized IAM users can access

#### **Unique File Names**
- ✅ **Timestamp Prefix**: `YYYYMMDD_HHMMSS` format prevents collisions
- ✅ **UUID Component**: 8-character unique identifier
- ✅ **Organized Structure**: All uploads in `uploads/` folder

Example S3 key: `uploads/20240314_143052_a1b2c3d4_data.csv`

### 4. **Download Security**

#### **Presigned URL Security**
- ✅ **Time Limits**: URLs expire after 1 hour maximum
- ✅ **Path Validation**: Prevents access to system files
- ✅ **Prefix Enforcement**: Only allows downloads from `uploads/` folder

```python
# Security: Ensure key starts with allowed prefix
if not s3_key.startswith('uploads/'):
    raise Exception("Access denied: Invalid file path")

# Security: Limit expiration time (max 1 hour)
max_expiration = 3600  # 1 hour
if expiration > max_expiration:
    expiration = max_expiration
```

#### **File Existence Verification**
- ✅ **Pre-check**: Verifies file exists before generating URL
- ✅ **Error Handling**: Returns appropriate error for missing files
- ✅ **Audit Logging**: Logs all URL generation attempts

### 5. **Deletion Security**

#### **Restricted Deletion**
- ✅ **Path Validation**: Only allows deletion of files in `uploads/` folder
- ✅ **Traversal Prevention**: Blocks attempts to delete system files
- ✅ **Existence Check**: Verifies file exists before deletion attempt

```python
# Security: Only allow deletion of files in uploads folder
if not s3_key.startswith('uploads/'):
    raise Exception("Access denied: Cannot delete system files")
```

### 6. **Error Handling & Logging**

#### **Secure Error Messages**
- ✅ **Generic Errors**: Doesn't expose internal system details
- ✅ **Detailed Logging**: Records full error details in server logs
- ✅ **User-Safe Messages**: Returns safe error messages to frontend

#### **Audit Trail**
- ✅ **All Operations Logged**: Upload, download, delete operations tracked
- ✅ **Error Logging**: Failed operations recorded with details
- ✅ **Timestamp Tracking**: All operations include precise timestamps

## 🔒 IAM Security Best Practices

### Minimal Permissions Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:HeadBucket",
                "s3:HeadObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### What This Policy Does:
- ✅ **GetObject**: Download files from your bucket only
- ✅ **PutObject**: Upload files to your bucket only
- ✅ **DeleteObject**: Delete files from your bucket only
- ✅ **ListBucket**: List contents of your bucket only
- ✅ **HeadBucket/HeadObject**: Check if bucket/objects exist
- ❌ **No Admin Access**: Cannot modify bucket policies or settings
- ❌ **No Cross-Bucket**: Cannot access other S3 buckets

## 🚨 Security Monitoring

### Things to Monitor:
1. **Failed Authentication**: Watch for repeated credential failures
2. **Unusual Access Patterns**: Large number of downloads/uploads
3. **Error Rates**: High error rates might indicate attacks
4. **File Size Anomalies**: Unusually large uploads
5. **Access from Unexpected IPs**: Geographic anomalies

### AWS CloudTrail Integration:
```json
{
    "eventSource": "s3.amazonaws.com",
    "eventName": "GetObject",
    "userIdentity": {
        "type": "IAMUser",
        "userName": "csv-app-user"
    }
}
```

## 🔧 Environment Security

### Required Environment Variables:
```bash
# Never commit these to version control!
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_BUCKET_NAME=your-unique-bucket-name
```

### Security Checklist:
- ✅ Use `.env` file that's in `.gitignore`
- ✅ Never commit credentials to repository
- ✅ Use different credentials for development/production
- ✅ Rotate access keys regularly (every 90 days)
- ✅ Monitor AWS CloudTrail for API usage
- ✅ Enable S3 bucket logging
- ✅ Set up billing alerts for unexpected usage

## 🛠️ Testing Security

### Security Test Scenarios:

1. **Path Traversal Test**:
   ```python
   # Should fail
   s3_service.generate_presigned_url("../../../etc/passwd")
   ```

2. **Invalid File Type Test**:
   ```python
   # Should fail
   s3_service.upload_file("/tmp/malicious.exe", "virus.exe")
   ```

3. **Unauthorized Deletion Test**:
   ```python
   # Should fail
   s3_service.delete_file("system/config.json")
   ```

4. **Missing Credentials Test**:
   ```python
   # Should fail at initialization
   os.environ.pop('AWS_ACCESS_KEY_ID')
   S3Service()  # Should raise exception
   ```

### Running Security Tests:
```bash
# Test with invalid credentials
export AWS_ACCESS_KEY_ID="invalid"
python test_s3_integration.py  # Should fail gracefully

# Test file type restrictions
echo "malicious content" > /tmp/test.exe
# Upload should be rejected
```

## 🎯 Security Summary

Your S3 integration implements defense-in-depth security:

1. **Authentication**: Valid AWS credentials required
2. **Authorization**: Minimal IAM permissions
3. **Input Validation**: File type and path validation
4. **Encryption**: Data encrypted at rest in S3
5. **Access Control**: Private files with time-limited access
6. **Audit Logging**: Complete operation tracking
7. **Error Handling**: Secure error messages
8. **File Organization**: Structured S3 key naming

These security measures protect against:
- ✅ **Path Traversal Attacks**
- ✅ **Unauthorized File Access**
- ✅ **Malicious File Uploads**
- ✅ **Credential Exposure**
- ✅ **Data Breaches**
- ✅ **Unauthorized Deletions**

Your application follows security best practices for cloud storage integration! 🛡️