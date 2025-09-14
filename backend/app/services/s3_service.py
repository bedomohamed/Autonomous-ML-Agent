import boto3
import os
from datetime import datetime
import uuid
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME', 'csv-preprocessing-bucket')
        self._ensure_bucket_exists()

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
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            s3_key = f"uploads/{timestamp}_{unique_id}_{original_filename}"

            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'text/csv',
                    'Metadata': {
                        'original_filename': original_filename,
                        'upload_timestamp': timestamp
                    }
                }
            )

            logger.info(f"File uploaded to S3: {s3_key}")
            return s3_key

        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")

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
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise Exception(f"Failed to generate download URL: {str(e)}")

    def delete_file(self, s3_key):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"File deleted from S3: {s3_key}")

        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            raise Exception(f"Failed to delete file from S3: {str(e)}")

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