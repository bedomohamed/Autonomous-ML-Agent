#!/usr/bin/env python3
"""
Quick S3 Connection Test

Before running the full integration test, this script quickly checks if your
AWS credentials can connect to S3 and access/create your bucket.
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def quick_s3_test():
    # Load environment variables
    load_dotenv()

    print("🔍 Quick S3 Connection Test")
    print("=" * 30)

    # Get credentials from environment
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    bucket_name = os.getenv('AWS_BUCKET_NAME')

    # Check if credentials are set
    if not access_key or access_key == 'your_access_key_here':
        print("❌ AWS_ACCESS_KEY_ID not set or still placeholder")
        return False

    if not secret_key or secret_key == 'your_secret_key_here':
        print("❌ AWS_SECRET_ACCESS_KEY not set or still placeholder")
        return False

    if not bucket_name or bucket_name == 'csv-preprocessing-demo-bucket':
        print("❌ AWS_BUCKET_NAME not set or still using demo name")
        return False

    print(f"✅ Credentials found for bucket: {bucket_name}")
    print(f"✅ Using region: {region}")

    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Test connection by checking if bucket exists
        print(f"\n🔌 Testing connection to S3...")
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Successfully connected to bucket '{bucket_name}'")

        # Test listing objects (should work even if bucket is empty)
        print(f"\n📋 Testing bucket permissions...")
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        print(f"✅ Successfully listed objects in bucket")

        object_count = response.get('KeyCount', 0)
        if object_count > 0:
            print(f"📄 Found {object_count} existing objects in bucket")
        else:
            print(f"📄 Bucket is empty (this is fine for new setups)")

        print(f"\n🎉 S3 connection test PASSED!")
        print(f"\n💡 Your S3 integration is ready to use!")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == '404':
            print(f"❌ Bucket '{bucket_name}' does not exist")
            print(f"💡 The S3Service will try to create it automatically")
        elif error_code == 'InvalidAccessKeyId':
            print(f"❌ Invalid AWS Access Key ID")
        elif error_code == 'SignatureDoesNotMatch':
            print(f"❌ Invalid AWS Secret Access Key")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied - check your IAM permissions")
        else:
            print(f"❌ S3 Error: {error_code} - {e}")

        return False

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_s3_test()
    if success:
        print(f"\n✅ Ready to run: python test_s3_integration.py")
    else:
        print(f"\n❌ Fix the issues above before running the full integration test")