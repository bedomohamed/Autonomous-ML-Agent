import boto3
import os
from datetime import datetime
import uuid
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
import logging
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        # Validate required environment variables
        self._validate_credentials()

        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_BUCKET_NAME', 'csv-preprocessing-bucket')
            self._ensure_bucket_exists()
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise Exception("AWS credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def _validate_credentials(self):
        """Validate that required AWS credentials are present"""
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_BUCKET_NAME']
        missing_vars = []

        for var in required_vars:
            value = os.getenv(var)
            if not value or value in ['your_access_key_here', 'your_secret_key_here', 'your_bucket_name']:
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"Missing AWS credentials: {missing_vars}")
            raise Exception(f"Missing AWS environment variables: {', '.join(missing_vars)}")

        logger.info("AWS credentials validated successfully")

    def _ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise

    def upload_file(self, file_path, original_filename):
        """Upload file to S3 with enhanced error handling and security"""
        try:
            # Validate file exists and is readable
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path}")

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise Exception("Cannot upload empty file")

            # Security: Sanitize filename to prevent path traversal
            safe_filename = os.path.basename(original_filename).replace('..',  '')
            if not safe_filename:
                raise Exception("Invalid filename")

            # Validate file extension for security
            allowed_extensions = {'.csv', '.txt'}
            file_ext = Path(safe_filename).suffix.lower()
            if file_ext not in allowed_extensions:
                raise Exception(f"File type not allowed: {file_ext}")

            # Generate secure S3 key
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            s3_key = f"uploads/{timestamp}_{unique_id}_{safe_filename}"

            # Determine content type
            content_type, _ = mimetypes.guess_type(safe_filename)
            if not content_type:
                content_type = 'text/csv' if file_ext == '.csv' else 'text/plain'

            # Upload with metadata and security settings
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'original_filename': safe_filename,
                        'upload_timestamp': timestamp,
                        'file_size': str(file_size)
                    },
                    'ServerSideEncryption': 'AES256',  # Encrypt at rest
                    'ACL': 'private'  # Ensure file is private
                }
            )

            logger.info(f"File uploaded to S3: {s3_key} (size: {file_size} bytes)")
            return s3_key

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDenied':
                logger.error("S3 access denied - check IAM permissions")
                raise Exception("Access denied to S3 bucket")
            elif error_code == 'NoSuchBucket':
                logger.error(f"S3 bucket does not exist: {self.bucket_name}")
                raise Exception("S3 bucket not found")
            else:
                logger.error(f"S3 upload failed: {e}")
                raise Exception(f"Failed to upload file to S3: {str(e)}")
        except Exception as e:
            logger.error(f"File upload error: {e}")
            raise

    def download_file(self, s3_key):
        try:
            local_path = f"/tmp/{os.path.basename(s3_key)}"

            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                local_path
            )

            logger.info(f"File downloaded from S3: {s3_key}")
            return local_path

        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise Exception(f"Failed to download file from S3: {str(e)}")

    def generate_presigned_url(self, s3_key, expiration=3600):
        """Generate secure presigned URL with validation and time limits"""
        try:
            # Security: Validate S3 key format and prevent path traversal
            if not s3_key or '..' in s3_key or s3_key.startswith('/'):
                raise Exception("Invalid S3 key format")

            # Security: Ensure key starts with allowed prefix
            if not s3_key.startswith('uploads/'):
                raise Exception("Access denied: Invalid file path")

            # Security: Limit expiration time (max 1 hour)
            max_expiration = 3600  # 1 hour
            if expiration > max_expiration:
                expiration = max_expiration
                logger.warning(f"Expiration time limited to {max_expiration} seconds")

            # Check if file exists before generating URL
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise Exception("File not found")
                raise

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )

            logger.info(f"Generated presigned URL for {s3_key} (expires in {expiration}s)")
            return url

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDenied':
                logger.error("Access denied when generating presigned URL")
                raise Exception("Access denied to file")
            else:
                logger.error(f"Failed to generate presigned URL: {e}")
                raise Exception(f"Failed to generate download URL: {str(e)}")
        except Exception as e:
            logger.error(f"Presigned URL generation error: {e}")
            raise

    def delete_file(self, s3_key):
        """Securely delete file from S3 with validation"""
        try:
            # Security: Validate S3 key format and prevent unauthorized deletion
            if not s3_key or '..' in s3_key or s3_key.startswith('/'):
                raise Exception("Invalid S3 key format")

            # Security: Only allow deletion of files in uploads folder
            if not s3_key.startswith('uploads/'):
                raise Exception("Access denied: Cannot delete system files")

            # Verify file exists before attempting deletion
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    logger.warning(f"File not found for deletion: {s3_key}")
                    return  # File already doesn't exist
                raise

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"File deleted from S3: {s3_key}")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDenied':
                logger.error("Access denied when deleting file")
                raise Exception("Access denied to delete file")
            else:
                logger.error(f"S3 deletion failed: {e}")
                raise Exception(f"Failed to delete file from S3: {str(e)}")
        except Exception as e:
            logger.error(f"File deletion error: {e}")
            raise

    def list_files(self, prefix='uploads/'):
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })

            return files

        except ClientError as e:
            logger.error(f"Failed to list S3 files: {e}")
            raise Exception(f"Failed to list files: {str(e)}")