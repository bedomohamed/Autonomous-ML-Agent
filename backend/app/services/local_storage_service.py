import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class LocalStorageService:
    def __init__(self):
        """Initialize Local Storage service"""
        # Create storage directories
        self.storage_root = os.path.join(os.getcwd(), 'storage')
        self.uploads_dir = os.path.join(self.storage_root, 'uploads')
        self.processed_dir = os.path.join(self.storage_root, 'processed')
        self.models_dir = os.path.join(self.storage_root, 'models')

        # Create directories if they don't exist
        for directory in [self.storage_root, self.uploads_dir, self.processed_dir, self.models_dir]:
            os.makedirs(directory, exist_ok=True)

        logger.info("Local storage service initialized successfully")

    def upload_file(self, file_path: str, original_filename: str) -> str:
        """Store file locally and return storage key"""
        try:
            # Validate file exists and is readable
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path}")

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise Exception("Cannot store empty file")

            # Security: Sanitize filename
            safe_filename = os.path.basename(original_filename).replace('..', '')
            if not safe_filename:
                raise Exception("Invalid filename")

            # Validate file extension
            allowed_extensions = {'.csv', '.txt'}
            file_ext = Path(safe_filename).suffix.lower()
            if file_ext not in allowed_extensions:
                raise Exception(f"File type not allowed: {file_ext}")

            # Generate unique storage key
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            storage_key = f"uploads/{timestamp}_{unique_id}_{safe_filename}"

            # Full path for storage
            storage_path = os.path.join(self.storage_root, storage_key)

            # Ensure directory exists
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)

            # Copy file to storage location
            shutil.copy2(file_path, storage_path)

            logger.info(f"File stored locally: {storage_key} (size: {file_size} bytes)")
            return storage_key

        except Exception as e:
            logger.error(f"File upload error: {e}")
            raise Exception(f"Failed to store file locally: {str(e)}")

    def download_file(self, storage_key: str) -> str:
        """Get local file path for a stored file"""
        try:
            # Security: Validate storage key
            if not storage_key or '..' in storage_key or storage_key.startswith('/'):
                raise Exception("Invalid storage key format")

            # Security: Ensure key starts with allowed prefix
            if not storage_key.startswith('uploads/') and not storage_key.startswith('processed/'):
                raise Exception("Access denied: Invalid file path")

            storage_path = os.path.join(self.storage_root, storage_key)

            # Check if file exists
            if not os.path.exists(storage_path):
                # Try to find a similar file (for debugging/development)
                available_files = []
                try:
                    upload_dir = os.path.join(self.storage_root, 'uploads')
                    if os.path.exists(upload_dir):
                        available_files = os.listdir(upload_dir)
                        # Check if there's a similar file with the same base name
                        requested_basename = os.path.basename(storage_key)
                        if '_' in requested_basename:
                            # Extract the original filename part (after the timestamp and UUID)
                            parts = requested_basename.split('_')
                            if len(parts) >= 4:
                                original_name = '_'.join(parts[3:])  # Get everything after timestamp_uuid_
                                # Look for any file ending with the same original name
                                for available_file in available_files:
                                    if available_file.endswith(original_name):
                                        logger.warning(f"File {storage_key} not found, using similar file: {available_file}")
                                        return os.path.join(upload_dir, available_file)
                except Exception as e:
                    logger.error(f"Error searching for similar files: {e}")
                    pass
                raise Exception(f"File not found at path: {storage_path}. Available files: {available_files}")

            logger.info(f"File accessed: {storage_key}")
            return storage_path

        except Exception as e:
            logger.error(f"File download error: {e}")
            raise Exception(f"Failed to access file: {str(e)}")

    def generate_download_url(self, storage_key: str, expiration: int = 3600) -> str:
        """Generate a local file download URL (for API compatibility)"""
        try:
            # Validate file exists
            storage_path = self.download_file(storage_key)

            # For local storage, we'll return a special URL that the API can handle
            download_url = f"/api/download-local/{storage_key.replace('/', '__')}"

            logger.info(f"Generated local download URL for {storage_key}")
            return download_url

        except Exception as e:
            logger.error(f"URL generation error: {e}")
            raise Exception(f"Failed to generate download URL: {str(e)}")

    def delete_file(self, storage_key: str) -> None:
        """Delete a file from local storage"""
        try:
            # Security validations
            if not storage_key or '..' in storage_key or storage_key.startswith('/'):
                raise Exception("Invalid storage key format")

            if not storage_key.startswith('uploads/') and not storage_key.startswith('processed/'):
                raise Exception("Access denied: Cannot delete system files")

            storage_path = os.path.join(self.storage_root, storage_key)

            if os.path.exists(storage_path):
                os.remove(storage_path)
                logger.info(f"File deleted: {storage_key}")
            else:
                logger.warning(f"File not found for deletion: {storage_key}")

        except Exception as e:
            logger.error(f"File deletion error: {e}")
            raise Exception(f"Failed to delete file: {str(e)}")

    def list_files(self, prefix: str = 'uploads/') -> list:
        """List files in storage directory"""
        try:
            search_dir = os.path.join(self.storage_root, prefix.rstrip('/'))
            files = []

            if os.path.exists(search_dir):
                for filename in os.listdir(search_dir):
                    file_path = os.path.join(search_dir, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        files.append({
                            'key': f"{prefix}{filename}",
                            'size': stat.st_size,
                            'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })

            return sorted(files, key=lambda x: x['last_modified'], reverse=True)

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise Exception(f"Failed to list files: {str(e)}")

    def get_file_info(self, storage_key: str) -> dict:
        """Get information about a stored file"""
        try:
            storage_path = self.download_file(storage_key)
            stat = os.stat(storage_path)

            return {
                'key': storage_key,
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': True,
                'path': storage_path
            }

        except Exception as e:
            return {
                'key': storage_key,
                'exists': False,
                'error': str(e)
            }

    def store_processed_file(self, file_path: str, original_key: str) -> str:
        """Store processed file and return new key"""
        try:
            # Generate processed file key
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            original_filename = os.path.basename(original_key)
            processed_key = f"processed/{timestamp}_{unique_id}_cleaned_{original_filename}"

            storage_path = os.path.join(self.storage_root, processed_key)
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)

            # Copy processed file
            shutil.copy2(file_path, storage_path)

            logger.info(f"Processed file stored: {processed_key}")
            return processed_key

        except Exception as e:
            logger.error(f"Failed to store processed file: {e}")
            raise Exception(f"Failed to store processed file: {str(e)}")

    def store_preprocessing_code(self, code: str, original_key: str, experiment_id: str = None) -> str:
        """Store preprocessing Python code to processed folder and return new key"""
        try:
            # Generate code file key
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            original_filename = os.path.basename(original_key).replace('.csv', '')

            # Include experiment ID if provided
            exp_suffix = f"_{experiment_id}" if experiment_id else ""
            code_key = f"processed/{timestamp}_{unique_id}_preprocessing{exp_suffix}_{original_filename}.py"

            storage_path = os.path.join(self.storage_root, code_key)
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)

            # Write Python code to file
            with open(storage_path, 'w', encoding='utf-8') as f:
                # Add header comment
                f.write(f"""# Preprocessing Code for {original_filename}
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Experiment ID: {experiment_id or 'N/A'}
# Original file: {original_key}

""")
                f.write(code)

            logger.info(f"Preprocessing code stored: {code_key}")
            return code_key

        except Exception as e:
            logger.error(f"Failed to store preprocessing code: {e}")
            raise Exception(f"Failed to store preprocessing code: {str(e)}")

    def cleanup_old_files(self, days_old: int = 7) -> int:
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            removed_count = 0

            for directory in [self.uploads_dir, self.processed_dir]:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            if os.path.getmtime(file_path) < cutoff_time:
                                os.remove(file_path)
                                removed_count += 1

            logger.info(f"Cleaned up {removed_count} old files")
            return removed_count

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

    def get_storage_stats(self) -> dict:
        """Get storage usage statistics"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'uploads_count': 0,
                'uploads_size': 0,
                'processed_count': 0,
                'processed_size': 0
            }

            for directory, prefix in [(self.uploads_dir, 'uploads'), (self.processed_dir, 'processed')]:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            size = os.path.getsize(file_path)
                            stats['total_files'] += 1
                            stats['total_size'] += size
                            stats[f'{prefix}_count'] += 1
                            stats[f'{prefix}_size'] += size

            return stats

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {'error': str(e)}

    def health_check(self) -> dict:
        """Check local storage health"""
        try:
            # Check if directories exist and are writable
            test_file = os.path.join(self.uploads_dir, 'health_check_test.txt')

            with open(test_file, 'w') as f:
                f.write('health check')

            # Read it back
            with open(test_file, 'r') as f:
                content = f.read()

            # Clean up
            os.remove(test_file)

            stats = self.get_storage_stats()

            return {
                'status': 'healthy',
                'storage_accessible': True,
                'test_write': content == 'health check',
                'storage_root': self.storage_root,
                'stats': stats
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'storage_accessible': False,
                'error': str(e)
            }