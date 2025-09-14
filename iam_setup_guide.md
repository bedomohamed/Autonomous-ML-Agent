# AWS IAM Setup for S3 Access

## Step 1: Create IAM User

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Navigate to Users**: Click "Users" in left sidebar
3. **Create User**:
   - Click "Create user"
   - Username: `csv-app-user`
   - Access type: ✅ Programmatic access
   - Click "Next"

## Step 2: Attach Permissions

### Option A: Use Existing Policy (Simple)
- Search for `AmazonS3FullAccess`
- Check the box and click "Next"
- Review and create user

### Option B: Create Custom Policy (Recommended)

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
                "s3:CreateBucket",
                "s3:HeadBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

## Step 3: Get Access Keys

After creating user:
1. Click on the user name
2. Go to "Security credentials" tab
3. Click "Create access key"
4. Choose "Application running outside AWS"
5. **IMPORTANT**: Download and save the Access Key ID and Secret Access Key
6. **NEVER share these keys publicly!**

## Step 4: Configure Environment Variables

Create `.env` file in your backend directory:

```bash
AWS_ACCESS_KEY_ID=AKIA...your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=your-bucket-name
```