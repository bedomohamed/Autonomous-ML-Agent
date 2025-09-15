from flask import Blueprint, request, jsonify, current_app
import os
import pandas as pd
import numpy as np
import logging
import uuid
from werkzeug.utils import secure_filename
from app.services.local_storage_service import LocalStorageService
# from app.services.preprocessing_service import PreprocessingService  # Deprecated - using Claude/E2B services
from app.services.data_analysis_service import DataAnalysisService
from app.services.claude_service import ClaudeService
from app.services.e2b_service import E2BService
from app.utils.validators import validate_csv_file
from app.utils.code_validator import CodeValidator
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def convert_to_serializable(obj):
    """Convert numpy/pandas types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj.to_dict()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

@api_bp.route('/upload', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV files are allowed'}), 400

        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        try:
            df = pd.read_csv(temp_path)
            validation_result = validate_csv_file(df)

            if not validation_result['valid']:
                os.remove(temp_path)
                return jsonify({'error': validation_result['message']}), 400

            storage_service = LocalStorageService()
            storage_key = storage_service.upload_file(temp_path, filename)

            preview_data = {
                'columns': df.columns.tolist(),
                'preview': df.head(50).to_dict('records'),
                'shape': {'rows': len(df), 'columns': len(df.columns)},
                'storage_key': storage_key,
                'filename': filename
            }

            os.remove(temp_path)

            return jsonify({
                'success': True,
                'data': preview_data,
                'message': 'File uploaded successfully'
            }), 200

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': f'Error processing CSV: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@api_bp.route('/preprocess', methods=['POST'])
def preprocess_data():
    """Simple preprocessing endpoint for basic data cleaning"""
    try:
        data = request.json

        if not data or ('storage_key' not in data and 's3_key' not in data) or 'target_column' not in data:
            return jsonify({'error': 'Missing required parameters: storage_key/s3_key, target_column'}), 400

        storage_key = data.get('storage_key') or data.get('s3_key')  # Support both for compatibility
        target_column = data['target_column']

        storage_service = LocalStorageService()
        csv_path = storage_service.download_file(storage_key)

        df = pd.read_csv(csv_path)

        if target_column not in df.columns:
            return jsonify({'error': f'Target column {target_column} not found in CSV'}), 400

        # Simple preprocessing without Claude/E2B for basic functionality
        initial_shape = df.shape

        # Basic preprocessing steps
        # 1. Remove target column from features
        features_df = df.drop(columns=[target_column])

        # 2. Handle missing values (simple imputation)
        numeric_columns = features_df.select_dtypes(include=[np.number]).columns
        categorical_columns = features_df.select_dtypes(exclude=[np.number]).columns

        # Fill numeric columns with median
        for col in numeric_columns:
            features_df[col].fillna(features_df[col].median(), inplace=True)

        # Fill categorical columns with mode
        for col in categorical_columns:
            features_df[col].fillna(features_df[col].mode()[0] if not features_df[col].mode().empty else 'Unknown', inplace=True)

        # 3. Remove duplicate rows
        features_df = features_df.drop_duplicates()

        # Save processed file
        processed_filename = f"processed_{os.path.basename(storage_key)}"
        temp_processed_path = f"/tmp/{processed_filename}"
        features_df.to_csv(temp_processed_path, index=False)
        processed_storage_key = storage_service.store_processed_file(temp_processed_path, storage_key)
        os.remove(temp_processed_path)  # Remove temp file
        # Note: Keep original file for future operations

        # Create statistics (convert numpy types to Python types for JSON serialization)
        statistics = {
            'original_shape': [int(initial_shape[0]), int(initial_shape[1])],
            'cleaned_shape': [int(features_df.shape[0]), int(features_df.shape[1])],
            'removed_rows': int(initial_shape[0] - features_df.shape[0]),
            'removed_columns': int(initial_shape[1] - features_df.shape[1]),
            'null_values_before': int(df.isnull().sum().sum()),
            'null_values_after': int(features_df.isnull().sum().sum())
        }

        steps_applied = [
            f'Removed target column: {target_column}',
            'Handled missing values with median/mode imputation',
            'Removed duplicate rows',
            'Basic data cleaning completed'
        ]

        return jsonify({
            'success': True,
            'data': {
                'processed_storage_key': processed_storage_key,
                'statistics': statistics,
                'preprocessing_steps': steps_applied,
                'shape': {
                    'rows': len(features_df),
                    'columns': len(features_df.columns)
                }
            },
            'message': 'Data preprocessed successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Preprocessing failed: {str(e)}'}), 500

@api_bp.route('/download/<storage_key>', methods=['GET'])
def download_file(storage_key):
    try:
        # Convert URL-safe key back to path
        actual_key = storage_key.replace('__', '/')
        storage_service = LocalStorageService()
        download_url = storage_service.generate_download_url(actual_key)

        return jsonify({
            'success': True,
            'download_url': download_url
        }), 200

    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@api_bp.route('/download-local/<path:storage_key>', methods=['GET'])
def download_local_file(storage_key):
    """Direct file download for local storage"""
    try:
        # Convert URL-safe key back to path
        actual_key = storage_key.replace('__', '/')
        storage_service = LocalStorageService()
        file_path = storage_service.download_file(actual_key)

        from flask import send_file
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))

    except Exception as e:
        return jsonify({'error': f'File download failed: {str(e)}'}), 500

@api_bp.route('/analyze-dataset', methods=['POST'])
def analyze_dataset():
    """Comprehensive dataset analysis for ML pipeline"""
    try:
        data = request.json

        if not data or ('storage_key' not in data and 's3_key' not in data) or 'target_column' not in data:
            return jsonify({'error': 'Missing required parameters: storage_key/s3_key, target_column'}), 400

        storage_key = data.get('storage_key') or data.get('s3_key')
        target_column = data['target_column']

        # Download file from local storage
        storage_service = LocalStorageService()
        logger.info(f"Analysis request - storage_key: {storage_key}, target_column: {target_column}")
        csv_path = storage_service.download_file(storage_key)

        # Load dataset
        df = pd.read_csv(csv_path)

        if target_column not in df.columns:
            return jsonify({'error': f'Target column {target_column} not found in dataset'}), 400

        # Perform comprehensive analysis
        analysis_service = DataAnalysisService()
        analysis_results = analysis_service.analyze_dataset(df, target_column)

        # Generate preprocessing prompt
        preprocessing_prompt = analysis_service.generate_preprocessing_prompt()

        # Create experiment ID
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Convert analysis results to serializable format
        analysis_results_serializable = convert_to_serializable(analysis_results)

        # Store experiment metadata
        experiment_data = {
            'experiment_id': experiment_id,
            'dataset_info': {
                'filename': os.path.basename(csv_path),
                'storage_key': storage_key,
                'target_column': target_column,
                'shape': analysis_results_serializable['basic_info']['shape'],
                'task_type': analysis_results_serializable['target_analysis']['task_type']
            },
            'analysis_results': analysis_results_serializable,
            'preprocessing_prompt': preprocessing_prompt,
            'created_at': datetime.now().isoformat()
        }

        # Note: Do not delete the original uploaded file here
        # The file should remain available for future operations (preprocessing, training, etc.)

        return jsonify({
            'success': True,
            'data': {
                'experiment_id': experiment_id,
                'analysis': analysis_results_serializable,
                'preprocessing_prompt': preprocessing_prompt,
                'dataset_info': experiment_data['dataset_info']
            },
            'message': 'Dataset analysis completed successfully'
        }), 200

    except Exception as e:
        # Note: Do not delete the original uploaded file on error
        # The file should remain available for retry attempts
        logger.error(f"Dataset analysis failed: {str(e)}")
        return jsonify({'error': f'Dataset analysis failed: {str(e)}'}), 500

@api_bp.route('/generate-preprocessing', methods=['POST'])
def generate_preprocessing_code():
    """Generate preprocessing code using Claude API"""
    try:
        data = request.json

        if not data or 'preprocessing_prompt' not in data or 'dataset_info' not in data:
            return jsonify({'error': 'Missing preprocessing_prompt or dataset_info'}), 400

        preprocessing_prompt = data['preprocessing_prompt']
        dataset_info = data['dataset_info']

        # Use real Claude API service
        claude_service = ClaudeService()
        result = claude_service.generate_preprocessing_code(preprocessing_prompt, dataset_info)

        # Validate and fix the generated code BEFORE saving
        if result.get('preprocessing_code'):
            validation_result = CodeValidator.validate_and_fix_code(result['preprocessing_code'])

            if validation_result['fixes_applied']:
                logger.info(f"Applied code fixes during generation: {validation_result['fixes_applied']}")
                result['preprocessing_code'] = validation_result['fixed_code']
                # Add validation info to result
                result['code_validation'] = {
                    'issues_found': validation_result['issues'],
                    'fixes_applied': validation_result['fixes_applied'],
                    'validation_passed': validation_result['validation_passed']
                }

            # Automatically save the FIXED Python code to processed folder
            try:
                storage_service = LocalStorageService()
                original_key = dataset_info.get('storage_key', 'unknown_dataset')
                experiment_id = data.get('experiment_id', dataset_info.get('experiment_id'))

                code_key = storage_service.store_preprocessing_code(
                    result['preprocessing_code'],  # This is now the fixed code
                    original_key,
                    experiment_id
                )

                # Add the code storage key to the response
                result['preprocessing_code_key'] = code_key
                logger.info(f"Preprocessing code automatically saved to: {code_key}")

            except Exception as e:
                logger.warning(f"Failed to save preprocessing code: {e}")
                # Don't fail the request if code saving fails

        return jsonify({
            'success': True,
            'data': result,
            'message': 'Preprocessing code generated successfully with Claude AI'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Code generation failed: {str(e)}'}), 500

@api_bp.route('/generate-training-code', methods=['POST'])
def generate_training_code():
    """Generate model training code using Claude API"""
    try:
        data = request.json

        if not data or 'dataset_info' not in data:
            return jsonify({'error': 'Missing dataset_info'}), 400

        dataset_info = data['dataset_info']
        cleaned_data_analysis = data.get('cleaned_data_analysis')

        # Use real Claude API service
        claude_service = ClaudeService()
        result = claude_service.generate_training_code(dataset_info, cleaned_data_analysis)

        return jsonify({
            'success': True,
            'data': result,
            'message': 'Training code generated successfully with Claude AI'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Training code generation failed: {str(e)}'}), 500

@api_bp.route('/claude/health', methods=['GET'])
def claude_health_check():
    """Check Claude API health"""
    try:
        claude_service = ClaudeService()
        health_status = claude_service.health_check()

        return jsonify({
            'success': True,
            'data': health_status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Claude health check failed: {str(e)}'
        }), 500

@api_bp.route('/execute-preprocessing', methods=['POST'])
def execute_preprocessing():
    """Execute preprocessing code in E2B sandbox"""
    try:
        data = request.json

        if not data or 'preprocessing_code' not in data or ('storage_key' not in data and 's3_key' not in data):
            return jsonify({'error': 'Missing preprocessing_code or storage_key/s3_key'}), 400

        preprocessing_code = data['preprocessing_code']
        storage_key = data.get('storage_key') or data.get('s3_key')

        # Download original file from local storage
        storage_service = LocalStorageService()
        csv_path = storage_service.download_file(storage_key)

        # Validate and fix preprocessing code before execution
        validation_result = CodeValidator.validate_and_fix_code(preprocessing_code)

        if validation_result['fixes_applied']:
            logger.info(f"Applied code fixes: {validation_result['fixes_applied']}")
            preprocessing_code = validation_result['fixed_code']

        # Execute preprocessing in E2B sandbox
        e2b_service = E2BService()
        execution_result = e2b_service.execute_preprocessing_code(preprocessing_code, csv_path)

        # Add validation info to execution result
        execution_result['code_validation'] = {
            'issues_found': validation_result['issues'],
            'fixes_applied': validation_result['fixes_applied'],
            'validation_passed': validation_result['validation_passed']
        }

        if execution_result['success']:
            cleaned_storage_key = None
            execution_status = 'partial_success'  # Default to partial success

            # Check if there were errors in the execution output
            stderr_content = execution_result.get('stderr', '')
            has_errors = False
            if stderr_content:
                if isinstance(stderr_content, dict):
                    has_errors = 'TypeError' in str(stderr_content) or 'Error' in str(stderr_content)
                else:
                    has_errors = 'Error' in str(stderr_content) or 'Exception' in str(stderr_content)

            # Save cleaned data if it was created
            if execution_result.get('cleaned_data_exists') and execution_result.get('cleaned_data_content'):
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
                    temp_file.write(execution_result['cleaned_data_content'])
                    temp_path = temp_file.name

                cleaned_storage_key = storage_service.store_processed_file(temp_path, storage_key)
                os.remove(temp_path)
                execution_status = 'success'  # Full success with data
            elif has_errors:
                execution_status = 'failed_with_errors'

            # Determine success status and appropriate message
            is_successful = cleaned_storage_key is not None
            status_messages = {
                'success': 'Preprocessing executed successfully with cleaned data generated',
                'partial_success': 'Preprocessing executed but no cleaned data was produced',
                'failed_with_errors': 'Preprocessing executed with errors - check output for details'
            }

            return jsonify({
                'success': is_successful,
                'data': {
                    'cleaned_storage_key': cleaned_storage_key,
                    'execution_result': execution_result,
                    'execution_status': execution_status,
                    'has_errors': has_errors,
                    'preprocessing_summary': {
                        'execution_time': execution_result['execution_time'],
                        'files_created': execution_result.get('files_created', []),
                        'stdout': execution_result.get('stdout', ''),
                        'stderr': execution_result.get('stderr', ''),
                        'cleaned_data_generated': cleaned_storage_key is not None
                    }
                },
                'message': status_messages.get(execution_status, 'Preprocessing completed in E2B sandbox'),
                'warning': 'Check execution output for errors' if has_errors and is_successful else None
            }), 200 if is_successful else 400
        else:
            return jsonify({
                'success': False,
                'error': 'Preprocessing execution failed in E2B sandbox',
                'execution_result': execution_result,
                'message': 'E2B sandbox execution failed - check logs for details'
            }), 500

    except Exception as e:
        return jsonify({'error': f'Preprocessing execution failed: {str(e)}'}), 500

@api_bp.route('/execute-training', methods=['POST'])
def execute_training():
    """Execute model training code in E2B sandbox"""
    try:
        data = request.json

        if not data or 'training_code' not in data or ('cleaned_storage_key' not in data and 'cleaned_s3_key' not in data):
            return jsonify({'error': 'Missing training_code or cleaned_storage_key/cleaned_s3_key'}), 400

        training_code = data['training_code']
        cleaned_storage_key = data.get('cleaned_storage_key') or data.get('cleaned_s3_key')

        # Download cleaned data from local storage
        storage_service = LocalStorageService()
        cleaned_csv_path = storage_service.download_file(cleaned_storage_key)

        # Save training code to models directory before execution
        backend_dir = os.path.dirname(current_app.root_path)  # Go up from app to backend
        models_dir = os.path.join(backend_dir, 'storage', 'models')
        os.makedirs(models_dir, exist_ok=True)  # Ensure directory exists
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        execution_id = str(uuid.uuid4())[:8]
        training_code_filename = f"training_code_{timestamp}_{execution_id}.py"
        training_code_path = os.path.join(models_dir, training_code_filename)

        try:
            with open(training_code_path, 'w', encoding='utf-8') as f:
                f.write(training_code)
            logger.info(f"Training code saved to: {training_code_path}")
        except Exception as e:
            logger.error(f"Failed to save training code: {str(e)}")

        # Execute training in E2B sandbox
        e2b_service = E2BService()
        execution_result = e2b_service.execute_training_code(training_code, cleaned_csv_path)

        # Add saved file path to execution result
        execution_result['saved_training_code_path'] = training_code_path
        execution_result['training_code_filename'] = training_code_filename

        # Note: Keep cleaned data file for potential re-training or analysis

        if execution_result['success']:
            return jsonify({
                'success': True,
                'data': {
                    'execution_result': execution_result,
                    'training_summary': {
                        'execution_time': execution_result['execution_time'],
                        'models_trained': execution_result.get('models_trained', 0),
                        'model_files': execution_result.get('model_files', []),
                        'results': execution_result.get('results', {}),
                        'stdout': execution_result.get('stdout', ''),
                        'stderr': execution_result.get('stderr', ''),
                        'saved_training_code_path': execution_result.get('saved_training_code_path', ''),
                        'training_code_filename': execution_result.get('training_code_filename', '')
                    }
                },
                'message': 'Model training executed successfully in E2B sandbox'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Model training execution failed',
                'execution_result': execution_result
            }), 500

    except Exception as e:
        return jsonify({'error': f'Model training execution failed: {str(e)}'}), 500

@api_bp.route('/saved-training-codes', methods=['GET'])
def list_saved_training_codes():
    """List all saved training code files"""
    try:
        backend_dir = os.path.dirname(current_app.root_path)  # Go up from app to backend
        models_dir = os.path.join(backend_dir, 'storage', 'models')

        if not os.path.exists(models_dir):
            os.makedirs(models_dir, exist_ok=True)
            return jsonify({
                'success': True,
                'data': [],
                'message': 'No training codes saved yet'
            }), 200

        training_files = []
        for filename in os.listdir(models_dir):
            if filename.endswith('.py') and filename.startswith('training_code_'):
                file_path = os.path.join(models_dir, filename)
                file_stats = os.stat(file_path)

                training_files.append({
                    'filename': filename,
                    'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    'size_bytes': file_stats.st_size,
                    'full_path': file_path
                })

        # Sort by creation time (newest first)
        training_files.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            'success': True,
            'data': training_files,
            'message': f'Found {len(training_files)} saved training code files'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to list training codes: {str(e)}'}), 500

@api_bp.route('/e2b/health', methods=['GET'])
def e2b_health_check():
    """Check E2B sandbox health"""
    try:
        e2b_service = E2BService()
        health_status = e2b_service.health_check()

        return jsonify({
            'success': True,
            'data': health_status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'E2B health check failed: {str(e)}'
        }), 500

@api_bp.route('/e2b/info', methods=['GET'])
def e2b_info():
    """Get E2B sandbox environment information"""
    try:
        e2b_service = E2BService()
        info = e2b_service.get_sandbox_info()

        return jsonify({
            'success': True,
            'data': info
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'E2B info request failed: {str(e)}'
        }), 500

@api_bp.route('/storage/health', methods=['GET'])
def storage_health_check():
    """Check local storage health"""
    try:
        storage_service = LocalStorageService()
        health_status = storage_service.health_check()

        return jsonify({
            'success': True,
            'data': health_status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Storage health check failed: {str(e)}'
        }), 500

@api_bp.route('/storage/stats', methods=['GET'])
def storage_stats():
    """Get storage usage statistics"""
    try:
        storage_service = LocalStorageService()
        stats = storage_service.get_storage_stats()

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Storage stats request failed: {str(e)}'
        }), 500

@api_bp.route('/processed-files', methods=['GET'])
def list_processed_files():
    """List all files in the processed folder"""
    try:
        storage_service = LocalStorageService()

        # Get both processed CSV files and Python code files
        files = storage_service.list_files(prefix='processed/')

        # Categorize files
        csv_files = []
        python_files = []
        other_files = []

        for file_info in files:
            file_key = file_info['key']
            if file_key.endswith('.csv'):
                csv_files.append(file_info)
            elif file_key.endswith('.py'):
                python_files.append(file_info)
            else:
                other_files.append(file_info)

        return jsonify({
            'success': True,
            'data': {
                'total_files': len(files),
                'csv_files': csv_files,
                'python_files': python_files,
                'other_files': other_files,
                'all_files': files
            },
            'message': f'Found {len(files)} processed files'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to list processed files: {str(e)}'}), 500

@api_bp.route('/tune-hyperparameters', methods=['POST'])
def tune_hyperparameters():
    """Generate hyperparameter tuning code for best performing models"""
    try:
        data = request.get_json()

        # Required parameters
        baseline_results = data.get('baseline_results', {})
        top_models = data.get('top_models', [])
        experiment_id = data.get('experiment_id')

        if not baseline_results or not top_models:
            return jsonify({
                'error': 'Missing required parameters: baseline_results and top_models'
            }), 400

        logger.info(f"Generating hyperparameter tuning code for models: {top_models}")

        # Initialize Claude service
        claude_service = ClaudeService()

        # Generate hyperparameter tuning code
        tuning_result = claude_service.generate_hyperparameter_tuning_code(
            baseline_results=baseline_results,
            top_models=top_models
        )

        # Initialize local storage service
        storage_service = LocalStorageService()

        # Generate unique filename for tuning code
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        tuning_filename = f"{timestamp}_{unique_id}_hyperparameter_tuning_{experiment_id}.py"

        # Save tuning code to storage/models directory
        tuning_storage_key = f"models/{tuning_filename}"
        tuning_code_with_header = f"""# Hyperparameter Tuning Code
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Experiment ID: {experiment_id}
# Models to tune: {', '.join(top_models)}

{tuning_result['tuning_code']}
"""

        # Store the tuning code directly to file system
        storage_path = os.path.join(storage_service.storage_root, tuning_storage_key)
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)

        with open(storage_path, 'w', encoding='utf-8') as f:
            f.write(tuning_code_with_header)

        logger.info(f"Hyperparameter tuning code saved to: {tuning_storage_key}")

        # Prepare response
        response_data = {
            'tuning_code': tuning_result['tuning_code'],
            'models_to_tune': tuning_result['models_to_tune'],
            'search_strategy': tuning_result.get('search_strategy', 'GridSearchCV'),
            'parameter_grids': tuning_result.get('parameter_grids', {}),
            'estimated_tuning_time': tuning_result.get('estimated_tuning_time', 300),  # 5 minutes default
            'tuning_storage_key': tuning_storage_key,
            'experiment_id': experiment_id,
            'message': f'Hyperparameter tuning code generated for {len(top_models)} models'
        }

        return jsonify(convert_to_serializable(response_data)), 200

    except Exception as e:
        logger.error(f"Failed to generate hyperparameter tuning code: {str(e)}")
        return jsonify({
            'error': f'Failed to generate hyperparameter tuning code: {str(e)}'
        }), 500

@api_bp.route('/execute-hyperparameter-tuning', methods=['POST'])
def execute_hyperparameter_tuning():
    """Execute hyperparameter tuning code in E2B sandbox"""
    try:
        data = request.get_json()

        # Required parameters
        tuning_storage_key = data.get('tuning_storage_key')
        cleaned_data_key = data.get('cleaned_data_key', 'cleaned_data.csv')
        experiment_id = data.get('experiment_id')

        if not tuning_storage_key:
            return jsonify({
                'error': 'Missing required parameter: tuning_storage_key'
            }), 400

        logger.info(f"Executing hyperparameter tuning code: {tuning_storage_key}")

        # Initialize services
        storage_service = LocalStorageService()
        e2b_service = E2BService()

        # Get the tuning code file path
        tuning_code_path = os.path.join(storage_service.storage_root, tuning_storage_key)

        if not os.path.exists(tuning_code_path):
            return jsonify({
                'error': f'Hyperparameter tuning code not found: {tuning_storage_key}'
            }), 404

        # Read the tuning code
        with open(tuning_code_path, 'r', encoding='utf-8') as f:
            tuning_code = f.read()

        # Find the most recent cleaned data file if cleaned_data_key is generic
        if cleaned_data_key == 'cleaned_data.csv':
            # Look for the most recent processed cleaned file
            processed_files = []
            processed_dir = os.path.join(storage_service.storage_root, 'processed')
            if os.path.exists(processed_dir):
                for file in os.listdir(processed_dir):
                    if 'cleaned' in file and file.endswith('.csv'):
                        file_path = os.path.join(processed_dir, file)
                        processed_files.append((file_path, os.path.getmtime(file_path)))

                if processed_files:
                    # Get the most recent cleaned file
                    cleaned_data_path = max(processed_files, key=lambda x: x[1])[0]
                    logger.info(f"Using most recent cleaned data file: {cleaned_data_path}")
                else:
                    return jsonify({
                        'error': 'No cleaned data files found in processed directory'
                    }), 404
            else:
                return jsonify({
                    'error': 'Processed directory not found'
                }), 404
        else:
            # Use the specific cleaned data key provided
            cleaned_data_path = os.path.join(storage_service.storage_root, cleaned_data_key)
            if not os.path.exists(cleaned_data_path):
                return jsonify({
                    'error': f'Cleaned data file not found: {cleaned_data_key}'
                }), 404

        logger.info("Starting hyperparameter tuning execution in E2B sandbox")

        # Execute tuning code in E2B
        execution_result = e2b_service.execute_hyperparameter_tuning(
            tuning_code=tuning_code,
            data_file_path=cleaned_data_path,
            experiment_id=experiment_id
        )

        # Process the execution results
        tuning_summary = {
            'execution_successful': execution_result['success'],
            'execution_time': execution_result.get('execution_time', 0),
            'tuning_results': execution_result.get('tuning_results', {}),
            'improvements': execution_result.get('improvements', {}),
            'tuned_models_created': execution_result.get('files_created', []),
            'execution_log': execution_result.get('stdout', ''),
            'errors': execution_result.get('stderr', '')
        }

        # If successful, try to load and return the detailed results
        if execution_result['success']:
            try:
                # Try to get the tuning results JSON from E2B
                results_content = execution_result.get('tuning_results_content')
                if results_content:
                    tuning_summary['detailed_results'] = json.loads(results_content)
            except Exception as e:
                logger.warning(f"Could not parse detailed tuning results: {e}")

        response_data = {
            'tuning_summary': tuning_summary,
            'execution_status': 'completed' if execution_result['success'] else 'failed',
            'tuning_storage_key': tuning_storage_key,
            'experiment_id': experiment_id,
            'message': 'Hyperparameter tuning executed successfully' if execution_result['success']
                      else 'Hyperparameter tuning execution failed'
        }

        status_code = 200 if execution_result['success'] else 400
        return jsonify(convert_to_serializable(response_data)), status_code

    except Exception as e:
        logger.error(f"Failed to execute hyperparameter tuning: {str(e)}")
        return jsonify({
            'error': f'Failed to execute hyperparameter tuning: {str(e)}'
        }), 500

@api_bp.route('/download-model/<model_name>', methods=['GET'])
def download_model(model_name):
    """Download a trained model file"""
    try:
        # Initialize storage service
        storage_service = LocalStorageService()

        # Construct model file path (try both baseline and tuned models)
        possible_files = [
            f"models/{model_name}_tuned_model.pkl",  # Try tuned model first
            f"models/{model_name}_model.pkl"          # Fallback to baseline model
        ]

        model_file_path = None
        for file_path in possible_files:
            full_path = os.path.join(storage_service.storage_root, file_path)
            if os.path.exists(full_path):
                model_file_path = full_path
                storage_key = file_path
                break

        if not model_file_path:
            return jsonify({
                'error': f'Model file not found for {model_name}. Available models: {possible_files}'
            }), 404

        logger.info(f"Downloading model: {model_name} from {storage_key}")

        # Generate download URL/response
        try:
            # For local storage, we'll send the file directly
            from flask import send_file
            return send_file(
                model_file_path,
                as_attachment=True,
                download_name=f"{model_name}_model.pkl",
                mimetype='application/octet-stream'
            )

        except Exception as e:
            logger.error(f"Failed to send model file: {e}")
            return jsonify({
                'error': f'Failed to download model: {str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"Failed to download model {model_name}: {str(e)}")
        return jsonify({
            'error': f'Failed to download model: {str(e)}'
        }), 500

def _get_evaluation_metrics(task_type):
    """Get evaluation metrics based on task type"""
    if task_type == 'classification':
        return """
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall"""
    else:
        return """
- **R² Score**: Coefficient of determination
- **Mean Squared Error (MSE)**: Average squared differences
- **Mean Absolute Error (MAE)**: Average absolute differences
- **Root Mean Squared Error (RMSE)**: Square root of MSE"""