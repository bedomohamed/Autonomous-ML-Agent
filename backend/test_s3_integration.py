#!/usr/bin/env python3
"""
S3 Integration Test Script

This script tests the S3Service functionality to ensure your AWS credentials
and S3 configuration are working correctly.

Run this script AFTER setting up your AWS credentials in the .env file.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.s3_service import S3Service

def create_test_csv():
    """Create a temporary CSV file for testing"""
    test_data = """name,age,city,salary
Alice,25,New York,50000
Bob,30,San Francisco,75000
Charlie,35,Chicago,60000
Diana,28,Seattle,65000"""

    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    temp_file.write(test_data)
    temp_file.close()

    print(f"✅ Created test CSV file: {temp_file.name}")
    return temp_file.name

def test_s3_integration():
    """Test all S3Service functionality"""

    print("🧪 Starting S3 Integration Test")
    print("=" * 50)

    # Check environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_BUCKET_NAME']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f'your_{var.lower()}_here':
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing or placeholder environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please update your .env file with real AWS credentials")
        return False

    print("✅ Environment variables configured")

    try:
        # Initialize S3 service
        print("\n🔧 Initializing S3 service...")
        s3_service = S3Service()
        print(f"✅ S3 service initialized with bucket: {s3_service.bucket_name}")

        # Test 1: Create test file
        print("\n📄 Creating test CSV file...")
        test_file_path = create_test_csv()

        # Test 2: Upload file
        print("\n📤 Testing file upload...")
        s3_key = s3_service.upload_file(test_file_path, "test_data.csv")
        print(f"✅ File uploaded successfully with key: {s3_key}")

        # Test 3: List files
        print("\n📋 Testing file listing...")
        files = s3_service.list_files()
        print(f"✅ Found {len(files)} files in bucket:")
        for file in files[-3:]:  # Show last 3 files
            print(f"   - {file['key']} ({file['size']} bytes)")

        # Test 4: Generate download URL
        print("\n🔗 Testing presigned URL generation...")
        download_url = s3_service.generate_presigned_url(s3_key, expiration=300)  # 5 minutes
        print(f"✅ Generated download URL (expires in 5 minutes)")
        print(f"   URL: {download_url[:50]}...")

        # Test 5: Download file
        print("\n📥 Testing file download...")
        downloaded_path = s3_service.download_file(s3_key)
        print(f"✅ File downloaded to: {downloaded_path}")

        # Verify downloaded content
        with open(downloaded_path, 'r') as f:
            content = f.read()
            if "Alice,25,New York" in content:
                print("✅ Downloaded content verified")
            else:
                print("❌ Downloaded content verification failed")

        # Test 6: Delete test file from S3
        print("\n🗑️  Cleaning up - deleting test file from S3...")
        s3_service.delete_file(s3_key)
        print("✅ Test file deleted from S3")

        # Clean up local files
        os.unlink(test_file_path)
        os.unlink(downloaded_path)
        print("✅ Local test files cleaned up")

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Your S3 integration is working correctly!")
        print("\n💡 Next steps:")
        print("   1. Your backend can now upload CSV files to S3")
        print("   2. Files are stored with unique timestamps and IDs")
        print("   3. You can generate secure download URLs for users")
        print("   4. Files can be retrieved for processing")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("\n🔍 Common issues:")
        print("   - Check your AWS credentials in .env file")
        print("   - Ensure your IAM user has S3 permissions")
        print("   - Verify bucket name is available and valid")
        print("   - Check your internet connection")

        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    success = test_s3_integration()
    sys.exit(0 if success else 1)