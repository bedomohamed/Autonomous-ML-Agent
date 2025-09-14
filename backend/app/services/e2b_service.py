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
                processed_code = code.replace("'input_data.csv'", "'uploaded_data.csv'")
                processed_code = processed_code.replace('"input_data.csv"', '"uploaded_data.csv"')

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

                # Prepare the full code with imports and data loading
                full_code = f"""
import pandas as pd
import numpy as np
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

                try:
                    # Look for results JSON file
                    results_content = sandbox.files.read('model_results.json')
                    results_file = json.loads(results_content.decode('utf-8'))
                    logger.info("Model results successfully loaded")
                except Exception as e:
                    logger.warning(f"Model results file not found: {e}")

                execution_time = time.time() - start_time

                return {
                    'success': True,
                    'execution_id': execution_id,
                    'execution_time': round(execution_time, 2),
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'model_files': model_files,
                    'results': results_file,
                    'execution_log': execution_log,
                    'models_trained': len(model_files)
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