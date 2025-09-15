import os
import logging
import json
import time
from typing import Dict, Any, List, Optional
from e2b_code_interpreter import Sandbox
import tempfile
import uuid

logger = logging.getLogger(__name__)

class E2BService:
    def __init__(self):
        """Initialize E2B Sandbox service"""
        self.api_key = os.getenv('E2B_API_KEY')
        if not self.api_key or self.api_key == 'your_e2b_key_here':
            raise ValueError("E2B_API_KEY environment variable not set or is placeholder")

        logger.info("E2B service initialized successfully")

    def execute_preprocessing_code(self, code: str, csv_data_path: str) -> Dict[str, Any]:
        """Execute preprocessing code in E2B sandbox"""
        try:
            logger.info("Starting preprocessing code execution in E2B sandbox")
            execution_id = str(uuid.uuid4())[:8]

            # Create sandbox using the new E2B v2 API
            sandbox = Sandbox.create(api_key=self.api_key)

            try:
                # Upload the CSV file to sandbox
                logger.info("Uploading CSV file to sandbox")
                with open(csv_data_path, 'rb') as f:
                    csv_content = f.read()
                    sandbox.files.write('uploaded_data.csv', csv_content)

                # Create execution tracking
                execution_log = []
                start_time = time.time()

                # Prepare the user code by replacing file paths and ensuring proper indentation
                # Replace any references to the original file path with the sandbox file
                import re
                # Extract the original file path from the code
                file_path_pattern = r"['\"](?:uploads/)?[^'\"]*\.csv['\"]"
                processed_code = re.sub(file_path_pattern, "'uploaded_data.csv'", code)

                # Prepare the full code with minimal overhead
                full_code = f"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# Load the uploaded data
df = pd.read_csv('uploaded_data.csv')
print(f"Data loaded. Shape: {{df.shape}}")

# Execute user's preprocessing code
{processed_code}

# Save the cleaned data
if 'cleaned_df' in locals():
    print(f"Cleaned data shape: {{cleaned_df.shape}}")
    cleaned_df.to_csv('cleaned_data.csv', index=False)
    print("Data saved to cleaned_data.csv")
else:
    print("Warning: cleaned_df not found")

print("Preprocessing completed")
"""

                # Execute the code
                logger.info("Executing preprocessing code")
                result = sandbox.run_code(full_code)

                # Extract output from various possible result attributes
                stdout_output = ""
                stderr_output = ""

                # Try different possible attributes for output
                if hasattr(result, 'stdout') and result.stdout:
                    stdout_output = result.stdout
                elif hasattr(result, 'text') and result.text:
                    stdout_output = result.text
                elif hasattr(result, 'output') and result.output:
                    stdout_output = result.output
                elif hasattr(result, 'content') and result.content:
                    stdout_output = result.content
                else:
                    # Parse structured result if it's an Execution object
                    result_str = str(result)
                    if 'stdout:' in result_str:
                        # Extract stdout from structured output like "Execution(Results: [], Logs: Logs(stdout: ['...']))"
                        import re
                        stdout_match = re.search(r"stdout:\s*\['([^']*)'", result_str)
                        if stdout_match:
                            stdout_output = stdout_match.group(1).replace('\\n', '\n')
                        else:
                            stdout_output = result_str
                    else:
                        # Log available attributes for debugging
                        available_attrs = [attr for attr in dir(result) if not attr.startswith('_')]
                        logger.info(f"Result object attributes: {available_attrs}")
                        stdout_output = result_str

                # Try different possible attributes for errors
                if hasattr(result, 'stderr') and result.stderr:
                    stderr_output = result.stderr
                elif hasattr(result, 'error') and result.error:
                    stderr_output = result.error
                elif hasattr(result, 'errors') and result.errors:
                    stderr_output = str(result.errors)
                else:
                    # Try to extract stderr from structured output
                    result_str = str(result)
                    if 'stderr:' in result_str:
                        import re
                        stderr_match = re.search(r"stderr:\s*\[([^\]]*)\]", result_str)
                        if stderr_match:
                            stderr_output = stderr_match.group(1).strip("'\"").replace('\\n', '\n')
                        else:
                            stderr_output = ""

                execution_log.append({
                    'timestamp': time.time(),
                    'type': 'execution_complete',
                    'status': 'success',
                    'stdout': stdout_output,
                    'stderr': stderr_output
                })

                # Check if cleaned data was created
                cleaned_data_exists = False
                cleaned_data_content = None

                try:
                    cleaned_data_content = sandbox.files.read('cleaned_data.csv')
                    cleaned_data_exists = True
                    logger.info("Cleaned dataset successfully created")
                except Exception as e:
                    logger.warning(f"Cleaned data file not found: {e}")
                    cleaned_data_content = None

                # Get execution statistics
                execution_time = time.time() - start_time

                # List files created
                files_created = []
                try:
                    list_code = "import os; print(os.listdir('.'))"
                    ls_result = sandbox.run_code(list_code)
                    if hasattr(ls_result, 'text'):
                        files_created = eval(ls_result.text.strip()) if ls_result.text.strip().startswith('[') else []
                except:
                    pass

                # Handle cleaned data content properly
                cleaned_content = None
                if cleaned_data_content:
                    try:
                        if isinstance(cleaned_data_content, bytes):
                            cleaned_content = cleaned_data_content.decode('utf-8')
                        elif isinstance(cleaned_data_content, str):
                            cleaned_content = cleaned_data_content
                        else:
                            cleaned_content = str(cleaned_data_content)
                    except Exception as decode_error:
                        logger.warning(f"Error handling cleaned data content: {decode_error}")
                        cleaned_content = str(cleaned_data_content) if cleaned_data_content else None

                return {
                    'success': True,
                    'execution_id': execution_id,
                    'execution_time': round(execution_time, 2),
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'cleaned_data_exists': cleaned_data_exists,
                    'cleaned_data_content': cleaned_content,
                    'files_created': files_created,
                    'execution_log': execution_log
                }

            except Exception as exec_error:
                logger.error(f"Code execution failed: {exec_error}")
                return {
                    'success': False,
                    'execution_id': execution_id,
                    'error': str(exec_error),
                    'execution_time': time.time() - start_time
                }
            finally:
                # Sandbox cleanup is handled automatically in E2B v2
                pass

        except Exception as e:
            logger.error(f"E2B sandbox execution failed: {e}")
            return {
                'success': False,
                'error': f"Sandbox initialization failed: {str(e)}"
            }

    def execute_training_code(self, code: str, cleaned_data_path: str) -> Dict[str, Any]:
        """Execute model training code in E2B sandbox"""
        try:
            logger.info("Starting model training code execution in E2B sandbox")
            execution_id = str(uuid.uuid4())[:8]

            # Create sandbox using the new E2B v2 API
            sandbox = Sandbox.create(api_key=self.api_key)

            try:
                # Upload the cleaned CSV file
                logger.info("Uploading cleaned data to sandbox")
                with open(cleaned_data_path, 'rb') as f:
                    csv_content = f.read()
                    sandbox.files.write('cleaned_data.csv', csv_content)

                execution_log = []
                start_time = time.time()

                # Install required packages first
                install_code = """
import subprocess
import sys

# Install XGBoost and other required packages
packages = ['xgboost', 'scikit-learn', 'pandas', 'numpy']
for package in packages:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Installed {package}")
    except Exception as e:
        print(f"Failed to install {package}: {e}")
"""
                sandbox.run_code(install_code)

                # Prepare the full code with imports and data loading
                full_code = f"""
import pandas as pd
import numpy as np
import pickle
import json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression, LogisticRegression
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import json

# Load the cleaned data
df = pd.read_csv('cleaned_data.csv')

# Execute user's training code
{code}

# Save results if available
if 'results' in locals() or 'results' in globals():
    with open('model_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print("✅ Model results saved successfully")
"""

                # Execute training code
                result = sandbox.run_code(full_code)

                # Extract output from various possible result attributes
                stdout_output = ""
                stderr_output = ""

                if hasattr(result, 'stdout') and result.stdout:
                    stdout_output = result.stdout
                elif hasattr(result, 'text') and result.text:
                    stdout_output = result.text
                elif hasattr(result, 'output') and result.output:
                    stdout_output = result.output
                else:
                    stdout_output = str(result)

                if hasattr(result, 'stderr') and result.stderr:
                    stderr_output = result.stderr
                elif hasattr(result, 'error') and result.error:
                    stderr_output = result.error

                execution_log.append({
                    'timestamp': time.time(),
                    'type': 'training_complete',
                    'status': 'success',
                    'stdout': stdout_output,
                    'stderr': stderr_output
                })

                # Check for model files and results
                model_files = []
                results_file = None

                try:
                    # Look for model files
                    list_code = "import os; print([f for f in os.listdir('.') if f.endswith(('.pkl', '.joblib', '.h5', '.json'))])"
                    ls_result = sandbox.run_code(list_code)
                    if hasattr(ls_result, 'text') and ls_result.text.strip().startswith('['):
                        model_files = eval(ls_result.text.strip())
                except:
                    pass

                # Initialize parsed results
                parsed_model_results = []

                try:
                    # Look for results JSON file FIRST (most reliable)
                    logger.info("Attempting to read model_results.json from storage/models/")
                    results_content = sandbox.files.read('storage/models/model_results.json')
                    # Handle both string and bytes content
                    if isinstance(results_content, bytes):
                        results_content = results_content.decode('utf-8')
                    results_file = json.loads(results_content)
                    logger.info(f"Model results successfully loaded from JSON file: {results_file}")

                    # Convert results_file dict to the expected array format
                    if results_file and isinstance(results_file, dict):
                        for model_name, metrics in results_file.items():
                            # Use JSON names directly with minimal formatting
                            clean_name = model_name.replace('_', ' ')
                            parsed_model_results.append({
                                'name': clean_name,
                                'accuracy': metrics.get('accuracy', 0),
                                'precision': metrics.get('precision', 0),
                                'recall': metrics.get('recall', 0),
                                'f1_score': metrics.get('f1_score', 0),
                                'roc_auc': metrics.get('roc_auc', 0),
                                'training_time': 0
                            })
                        logger.info(f"Converted {len(parsed_model_results)} model results from JSON file")
                except Exception as e:
                    logger.warning(f"Model results file not found at storage/models/: {e}")
                    # Try alternative path
                    try:
                        logger.info("Attempting to read model_results.json from root directory")
                        results_content = sandbox.files.read('model_results.json')
                        # Handle both string and bytes content
                        if isinstance(results_content, bytes):
                            results_content = results_content.decode('utf-8')
                        results_file = json.loads(results_content)
                        logger.info(f"Model results loaded from root directory: {results_file}")
                        if results_file and isinstance(results_file, dict):
                            parsed_model_results = []
                            for model_name, metrics in results_file.items():
                                # Use JSON names directly with minimal formatting
                                clean_name = model_name.replace('_', ' ')
                                parsed_model_results.append({
                                    'name': clean_name,
                                    'accuracy': metrics.get('accuracy', 0),
                                    'precision': metrics.get('precision', 0),
                                    'recall': metrics.get('recall', 0),
                                    'f1_score': metrics.get('f1_score', 0),
                                    'roc_auc': metrics.get('roc_auc', 0),
                                    'training_time': 0
                                })
                    except Exception as e2:
                        logger.warning(f"Alternative model results file not found: {e2}")
                        # List files to see what's available
                        try:
                            list_code = "import os; print('Files in root:', os.listdir('.')); print('Files in storage:', os.listdir('storage') if os.path.exists('storage') else 'No storage dir'); print('Files in storage/models:', os.listdir('storage/models') if os.path.exists('storage/models') else 'No storage/models dir')"
                            ls_result = sandbox.run_code(list_code)
                            logger.info(f"Directory listing: {ls_result}")
                        except Exception as e3:
                            logger.warning(f"Failed to list directories: {e3}")

                execution_time = time.time() - start_time

                return {
                    'success': True,
                    'execution_id': execution_id,
                    'execution_time': round(execution_time, 2),
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'model_files': model_files,
                    'results': results_file,
                    'model_results': parsed_model_results or results_file,  # Use parsed results if JSON file not available
                    'execution_log': execution_log,
                    'models_trained': len(parsed_model_results) if parsed_model_results else len(model_files)
                }

            except Exception as exec_error:
                logger.error(f"Training execution failed: {exec_error}")
                return {
                    'success': False,
                    'execution_id': execution_id,
                    'error': str(exec_error),
                    'execution_time': time.time() - start_time
                }
            finally:
                # Sandbox cleanup is handled automatically in E2B v2
                pass

        except Exception as e:
            logger.error(f"E2B training execution failed: {e}")
            return {
                'success': False,
                'error': f"Training sandbox failed: {str(e)}"
            }

    def _parse_model_results_from_stdout(self, stdout_output):
        """Parse model results from E2B stdout output"""
        try:
            import re

            # Extract stdout array from nested Execution object string
            model_results = []

            # Handle both direct stdout and nested Execution object format
            text_to_parse = stdout_output

            # If it's a nested Execution object, extract the stdout array
            stdout_match = re.search(r'stdout: \[(.*?)\]', stdout_output, re.DOTALL)
            if stdout_match:
                # Parse the array content and join strings
                array_content = stdout_match.group(1)
                string_matches = re.findall(r'"([^"]*)"', array_content)
                if string_matches:
                    # Unescape and join all strings
                    text_to_parse = ' '.join(
                        s.replace('\\n', '\n').replace('\\"', '"') for s in string_matches
                    )

            # Extract model results using regex
            model_pattern = r'(\w+)\s+(?:Results|Model Performance):\s*({[^}]+})'
            matches = re.findall(model_pattern, text_to_parse)

            for model_name, results_str in matches:
                try:
                    # Clean and parse JSON
                    clean_results = results_str.replace("'", '"')
                    model_data = json.loads(clean_results)

                    # Use model names directly with minimal formatting
                    clean_name = model_name.replace('_', ' ')

                    model_results.append({
                        'name': clean_name,
                        'accuracy': model_data.get('accuracy', 0),
                        'precision': model_data.get('precision', 0),
                        'recall': model_data.get('recall', 0),
                        'f1_score': model_data.get('f1_score', 0),
                        'roc_auc': model_data.get('roc_auc', model_data.get('auc', 0)),
                        'training_time': 0  # Not available in stdout
                    })
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse results for {model_name}: {e}")
                    continue

            if model_results:
                logger.info(f"Successfully parsed {len(model_results)} model results from stdout")
                return model_results
            else:
                logger.warning("No model results found in stdout")
                return None

        except Exception as e:
            logger.error(f"Error parsing model results from stdout: {e}")
            return None

    def health_check(self) -> Dict[str, Any]:
        """Check if E2B service is accessible"""
        try:
            # Create a test sandbox using the new E2B v2 API
            sandbox = Sandbox.create(api_key=self.api_key)

            try:
                # Simple test execution
                result = sandbox.run_code("""
print('E2B Health Check OK')
import pandas
import numpy
import sklearn
print(f'pandas version: {pandas.__version__}')
print(f'numpy version: {numpy.__version__}')
print(f'sklearn version: {sklearn.__version__}')
""")

                # Extract output using improved method
                output = ""
                if hasattr(result, 'stdout') and result.stdout:
                    output = result.stdout
                elif hasattr(result, 'text') and result.text:
                    output = result.text
                elif hasattr(result, 'output') and result.output:
                    output = result.output
                else:
                    # Parse structured result if it's an Execution object
                    result_str = str(result)
                    if 'stdout:' in result_str:
                        # Extract stdout from structured output
                        import re
                        stdout_matches = re.findall(r"'([^']*)'", result_str)
                        if stdout_matches:
                            output = ''.join(stdout_matches).replace('\\n', '\n')
                        else:
                            output = result_str
                    else:
                        output = result_str

                output = output or ""  # Ensure output is not None

                return {
                    'status': 'healthy',
                    'sandbox_accessible': True,
                    'test_output': output,
                    'ml_libraries_available': all(lib in output for lib in ['pandas', 'numpy', 'sklearn']) if output else False
                }
            finally:
                # Sandbox cleanup is automatic in E2B v2
                pass

        except Exception as e:
            return {
                'status': 'unhealthy',
                'sandbox_accessible': False,
                'error': str(e)
            }

    def execute_hyperparameter_tuning(self, tuning_code: str, data_file_path: str, experiment_id: str = None) -> Dict[str, Any]:
        """Execute hyperparameter tuning code in E2B sandbox"""
        execution_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting hyperparameter tuning execution {execution_id}")
        start_time = time.time()

        try:
            # Create sandbox using the E2B v2 API
            sandbox = Sandbox.create(api_key=self.api_key)

            try:
                # Upload cleaned data file
                logger.info("Uploading cleaned data to sandbox")
                with open(data_file_path, 'rb') as f:
                    sandbox.files.write('cleaned_data.csv', f.read())

                # Install required dependencies first
                logger.info("Installing required dependencies in sandbox")
                install_code = """
import subprocess
import sys

# Install required packages
packages = ['xgboost', 'joblib']
for package in packages:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Successfully installed {package}")
    except Exception as e:
        print(f"Failed to install {package}: {e}")

print("Dependencies installation completed.")
"""

                # First install dependencies
                install_result = sandbox.run_code(install_code)

                # Log dependency installation results
                install_output = ""
                if hasattr(install_result, 'stdout') and install_result.stdout:
                    install_output = install_result.stdout
                elif hasattr(install_result, 'text') and install_result.text:
                    install_output = install_result.text
                else:
                    install_output = str(install_result)

                logger.info(f"Dependencies installed: {install_output[:200]}...")  # Log first 200 chars

                # Then execute the tuning code
                logger.info("Executing hyperparameter tuning code")
                result = sandbox.run_code(tuning_code, timeout=900)  # 15 minutes timeout

                # Extract output from various possible result attributes
                stdout_output = ""
                stderr_output = ""

                # Try different possible attributes for output
                if hasattr(result, 'stdout') and result.stdout:
                    stdout_output = result.stdout
                elif hasattr(result, 'text') and result.text:
                    stdout_output = result.text
                elif hasattr(result, 'output') and result.output:
                    stdout_output = result.output
                elif hasattr(result, 'content') and result.content:
                    stdout_output = result.content
                else:
                    stdout_output = str(result)

                # Try to get stderr
                if hasattr(result, 'stderr') and result.stderr:
                    stderr_output = result.stderr
                elif hasattr(result, 'error') and result.error:
                    stderr_output = result.error

                execution_log = [
                    {
                        'type': 'execution_complete',
                        'status': 'success',
                        'stdout': stdout_output,
                        'stderr': stderr_output,
                        'timestamp': time.time()
                    }
                ]

                # Check for tuning results file
                tuning_results = {}
                tuning_results_content = None
                try:
                    tuning_results_content = sandbox.files.read('storage/models/hyperparameter_tuning_results.json')
                    if isinstance(tuning_results_content, bytes):
                        tuning_results_content = tuning_results_content.decode('utf-8')
                    tuning_results = json.loads(tuning_results_content)
                    logger.info("Successfully loaded tuning results")
                except Exception as e:
                    logger.warning(f"Could not load tuning results: {e}")

                # Check for comparison report
                comparison_report = {}
                try:
                    report_content = sandbox.files.read('storage/models/tuning_comparison_report.json')
                    if isinstance(report_content, bytes):
                        report_content = report_content.decode('utf-8')
                    comparison_report = json.loads(report_content)
                    logger.info("Successfully loaded comparison report")
                except Exception as e:
                    logger.warning(f"Could not load comparison report: {e}")

                # List and download tuned model files from sandbox
                files_created = []
                try:
                    # More robust file listing with better error handling
                    list_code = """
import os
import json
try:
    if os.path.exists('storage/models'):
        files = [f for f in os.listdir('storage/models') if f.endswith('_tuned_model.pkl')]
        print(json.dumps(files))
    else:
        print(json.dumps([]))
except Exception as e:
    print(json.dumps([]))
"""
                    ls_result = sandbox.run_code(list_code)

                    files_list = []
                    result_text = ""
                    if hasattr(ls_result, 'text') and ls_result.text.strip():
                        result_text = ls_result.text.strip()
                    elif hasattr(ls_result, 'stdout') and ls_result.stdout.strip():
                        result_text = ls_result.stdout.strip()

                    # Parse JSON response
                    if result_text:
                        try:
                            files_list = json.loads(result_text)
                        except:
                            # Fallback to old method
                            if result_text.startswith('['):
                                files_list = eval(result_text)

                    # Download each tuned model file from sandbox to local storage
                    import os
                    import json
                    local_storage_path = os.path.join(os.getcwd(), 'storage', 'models')
                    os.makedirs(local_storage_path, exist_ok=True)

                    for file_name in files_list:
                        try:
                            # Read file from sandbox
                            file_content = sandbox.files.read(f'storage/models/{file_name}')

                            # Write to local storage
                            local_file_path = os.path.join(local_storage_path, file_name)
                            with open(local_file_path, 'wb') as f:
                                f.write(file_content)

                            files_created.append(file_name)
                            logger.info(f"Downloaded tuned model: {file_name}")

                        except Exception as download_error:
                            logger.warning(f"Failed to download {file_name}: {download_error}")

                    # Also try to download the scaler if it was created
                    try:
                        scaler_content = sandbox.files.read('storage/models/scaler.pkl')
                        local_scaler_path = os.path.join(local_storage_path, 'scaler.pkl')
                        with open(local_scaler_path, 'wb') as f:
                            f.write(scaler_content)
                        logger.info("Downloaded scaler.pkl")
                    except:
                        pass  # Scaler might already exist

                except Exception as e:
                    logger.warning(f"Could not list or download created files: {e}")

                execution_time = time.time() - start_time

                # Calculate improvements if available
                improvements = {}
                if comparison_report and 'overall_improvement' in comparison_report:
                    improvements = comparison_report['overall_improvement']

                return {
                    'success': True,
                    'execution_id': execution_id,
                    'execution_time': round(execution_time, 2),
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'tuning_results': tuning_results,
                    'tuning_results_content': tuning_results_content,
                    'comparison_report': comparison_report,
                    'improvements': improvements,
                    'files_created': files_created,
                    'execution_log': execution_log
                }

            except Exception as exec_error:
                logger.error(f"Hyperparameter tuning execution failed: {exec_error}")
                return {
                    'success': False,
                    'execution_id': execution_id,
                    'error': str(exec_error),
                    'execution_time': time.time() - start_time,
                    'stdout': "",
                    'stderr': str(exec_error)
                }

            finally:
                # Sandbox cleanup is automatic in E2B v2
                pass

        except Exception as e:
            logger.error(f"Failed to create sandbox for hyperparameter tuning: {e}")
            return {
                'success': False,
                'execution_id': execution_id,
                'error': str(e),
                'execution_time': time.time() - start_time
            }

    def get_sandbox_info(self) -> Dict[str, Any]:
        """Get information about the sandbox environment"""
        try:
            sandbox = Sandbox.create(api_key=self.api_key)

            try:
                # Get system info
                info_code = """
import sys, os, platform
import pandas as pd
import numpy as np
import sklearn

info = {
    'python_version': sys.version,
    'platform': platform.platform(),
    'pandas_version': pd.__version__,
    'numpy_version': np.__version__,
    'sklearn_version': sklearn.__version__,
    'working_directory': os.getcwd()
}

import json
print(json.dumps(info, indent=2))
"""

                result = sandbox.run_code(info_code)
                output = result.text if hasattr(result, 'text') else str(result)

                try:
                    info = json.loads(output)
                    return {
                        'success': True,
                        'sandbox_info': info
                    }
                except:
                    return {
                        'success': True,
                        'sandbox_info': {'raw_output': output}
                    }
            finally:
                # Sandbox cleanup is automatic in E2B v2
                pass

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }