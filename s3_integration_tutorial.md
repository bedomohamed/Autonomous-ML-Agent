# Complete S3 Integration Tutorial

This guide walks you through integrating AWS S3 with your CSV preprocessing application.

## 🎯 What We're Building

Your application will:
1. **Upload** CSV files to S3 for secure storage
2. **Download** files from S3 for processing
3. **Generate** secure download URLs for users
4. **Manage** file lifecycle (upload → process → download → cleanup)

## 📋 Prerequisites

✅ AWS Account created
✅ S3 bucket created
✅ IAM user with proper permissions
✅ AWS credentials configured in `.env`

---

## 🧪 Step 1: Test Your S3 Connection

First, let's verify your AWS setup is working:

### Quick Connection Test
```bash
cd backend
python quick_s3_test.py
```

**Expected Output:**
```
🔍 Quick S3 Connection Test
==============================
✅ Credentials found for bucket: your-bucket-name
✅ Using region: us-east-1

🔌 Testing connection to S3...
✅ Successfully connected to bucket 'your-bucket-name'

📋 Testing bucket permissions...
✅ Successfully listed objects in bucket
📄 Bucket is empty (this is fine for new setups)

🎉 S3 connection test PASSED!

💡 Your S3 integration is ready to use!
```

### Full Integration Test
If the quick test passes, run the comprehensive test:

```bash
python test_s3_integration.py
```

This will test:
- ✅ File upload to S3
- ✅ File listing
- ✅ Presigned URL generation
- ✅ File download from S3
- ✅ File deletion
- ✅ Content verification

---

## 🔧 Step 2: Understanding the S3Service

Let's examine how our S3Service works:

### Key Methods

#### 1. **Upload File**
```python
s3_key = s3_service.upload_file(local_file_path, original_filename)
```
- Takes a local file and uploads it to S3
- Generates unique S3 key with timestamp and UUID
- Returns the S3 key for later retrieval

#### 2. **Download File**
```python
local_path = s3_service.download_file(s3_key)
```
- Downloads file from S3 to local temporary directory
- Returns local path for processing

#### 3. **Generate Download URL**
```python
url = s3_service.generate_presigned_url(s3_key, expiration=3600)
```
- Creates secure, time-limited download URL
- Users can download directly from S3 without exposing credentials

---

## 🔄 Step 3: File Upload Workflow

Here's how file upload works in your application:

### Frontend → Backend → S3

1. **User uploads CSV** via React frontend
2. **Backend receives file** and saves temporarily
3. **Validates CSV format** (pandas reads it successfully)
4. **Uploads to S3** using S3Service
5. **Returns preview data** with S3 key to frontend
6. **Deletes temporary file** from server

### Code Flow in `/upload` endpoint:

```python
# 1. Receive and validate file
file = request.files['file']
temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
file.save(temp_path)

# 2. Validate CSV format
df = pd.read_csv(temp_path)
validation_result = validate_csv_file(df)

# 3. Upload to S3
s3_service = S3Service()
s3_key = s3_service.upload_file(temp_path, filename)

# 4. Return preview data
preview_data = {
    'columns': df.columns.tolist(),
    'preview': df.head(50).to_dict('records'),
    's3_key': s3_key,  # ← This is key for later operations
    'filename': filename
}

# 5. Clean up
os.remove(temp_path)
```

---

## ⚙️ Step 4: Data Processing Workflow

When user selects target column and starts preprocessing:

### S3 → Processing → S3

1. **Download original file** from S3 using stored s3_key
2. **Process the data** (clean, transform, etc.)
3. **Upload processed file** back to S3 with new key
4. **Return results** with new s3_key for download

### Code Flow in `/preprocess` endpoint:

```python
# 1. Get original file from S3
s3_service = S3Service()
csv_path = s3_service.download_file(s3_key)

# 2. Process the data
df = pd.read_csv(csv_path)
preprocessing_service = PreprocessingService()
result = preprocessing_service.preprocess(df, target_column)

# 3. Save processed data back to S3
processed_filename = f"processed_{s3_key}"
result['cleaned_data'].to_csv(f"/tmp/{processed_filename}", index=False)
processed_s3_key = s3_service.upload_file(f"/tmp/{processed_filename}", processed_filename)

# 4. Clean up local files
os.remove(csv_path)
os.remove(f"/tmp/{processed_filename}")
```

---

## 🔗 Step 5: Download Workflow

When user wants to download processed data:

### Generate Secure URL

```python
# `/download/<s3_key>` endpoint
s3_service = S3Service()
presigned_url = s3_service.generate_presigned_url(s3_key)

return jsonify({
    'success': True,
    'download_url': presigned_url  # ← Frontend redirects here
})
```

**Why presigned URLs?**
- ✅ **Secure**: No need to expose AWS credentials to frontend
- ✅ **Time-limited**: URLs expire (default 1 hour)
- ✅ **Direct access**: User downloads directly from S3 (fast)

---

## 🛡️ Step 6: Security Best Practices

### Environment Variables
```bash
# ❌ NEVER commit these to git!
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=secret...
```

### IAM Permissions (Minimum Required)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",      // Download files
                "s3:PutObject",      // Upload files
                "s3:DeleteObject",   // Clean up files
                "s3:ListBucket"      // List bucket contents
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### File Naming Strategy
```python
# Our S3 keys look like:
"uploads/20240314_143052_a1b2c3d4_data.csv"
#        ^timestamp  ^uuid    ^original
```

Benefits:
- ✅ **Unique**: No file collisions
- ✅ **Organized**: All uploads in `uploads/` folder
- ✅ **Traceable**: Timestamp for debugging

---

## 🧪 Step 7: Test the Full Workflow

Let's test the complete application workflow:

### 1. Start the Backend
```bash
cd backend
python run.py
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Upload Flow
1. Visit http://localhost:5173
2. Upload a CSV file
3. Check browser network tab → should see successful upload
4. Check backend logs → should see S3 upload success

### 4. Test Processing Flow
1. Select target column
2. Click "Start Processing"
3. Check logs → should see S3 download/upload operations

### 5. Verify in AWS Console
1. Go to S3 console: https://s3.console.aws.amazon.com/
2. Open your bucket
3. Should see files in `uploads/` folder

---

## 🎯 Key Takeaways

### What S3 Gives You:
- ✅ **Scalable storage**: Handle files of any size
- ✅ **Reliability**: 99.999999999% (11 9's) durability
- ✅ **Security**: IAM permissions, encryption at rest
- ✅ **Cost-effective**: Pay only for what you use
- ✅ **Global access**: CDN-like performance worldwide

### Your Architecture:
```
React Frontend ←→ Flask Backend ←→ AWS S3
     ↑                ↑              ↑
   UI/UX        Business Logic   File Storage
```

### File Lifecycle:
1. **Upload**: User → Frontend → Backend → S3
2. **Process**: S3 → Backend → Processing → S3
3. **Download**: S3 → Presigned URL → User

---

## 🔧 Troubleshooting

### Common Issues:

#### "Access Denied" Error
```bash
# Check IAM permissions
aws iam list-attached-user-policies --user-name csv-app-user
```

#### "Bucket does not exist" Error
```bash
# Check bucket name in .env
AWS_BUCKET_NAME=your-actual-bucket-name
```

#### Import Error
```bash
# Install missing dependencies
pip install boto3 python-dotenv
```

### Debug Commands:
```bash
# Test AWS CLI access
aws s3 ls s3://your-bucket-name

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('AWS_BUCKET_NAME'))"
```

---

Your S3 integration is now complete! 🎉

The application can handle file uploads, processing, and downloads using AWS S3 as the storage backend. The frontend gets instant preview data while files are securely stored in the cloud for processing.