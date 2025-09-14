import pandas as pd
import numpy as np
import json
import os
from anthropic import Anthropic
from e2b import Sandbox
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PreprocessingService:
    def __init__(self):
        self.claude_client = Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.e2b_api_key = os.getenv('E2B_API_KEY')

    def generate_preprocessing_code(self, df_sample: pd.DataFrame, target_column: str) -> str:
        df_info = {
            'columns': df_sample.columns.tolist(),
            'dtypes': df_sample.dtypes.astype(str).to_dict(),
            'sample_data': df_sample.head(10).to_dict('records'),
            'shape': df_sample.shape,
            'null_counts': df_sample.isnull().sum().to_dict(),
            'target_column': target_column
        }

        prompt = f"""Generate a Python function to preprocess this dataset for machine learning.

Dataset Information:
{json.dumps(df_info, indent=2)}

Requirements:
1. Handle missing values appropriately (imputation or removal)
2. Detect and handle outliers using IQR or Z-score method
3. Standardize/normalize numerical features
4. Encode categorical variables if present
5. Drop the target column: {target_column}
6. Return the cleaned DataFrame

The function should be named 'preprocess_data' and take a pandas DataFrame as input.
Return only the Python code, no explanations. Include all necessary imports.
The code should be production-ready and handle edge cases."""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            code = response.content[0].text
            code = code.replace("```python", "").replace("```", "").strip()

            logger.info("Preprocessing code generated successfully")
            return code

        except Exception as e:
            logger.error(f"Failed to generate preprocessing code: {e}")
            raise Exception(f"Code generation failed: {str(e)}")

    def execute_preprocessing_code(self, code: str, df: pd.DataFrame) -> pd.DataFrame:
        try:
            sandbox = Sandbox(api_key=self.e2b_api_key)

            setup_code = """
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import json
"""

            sandbox.run_python(setup_code)

            df_json = df.to_json(orient='records')
            load_data_code = f"""
import json
data = json.loads('''{df_json}''')
df = pd.DataFrame(data)
"""
            sandbox.run_python(load_data_code)

            sandbox.run_python(code)

            result_code = """
result = preprocess_data(df)
result_json = result.to_json(orient='records')
print("RESULT_START")
print(result_json)
print("RESULT_END")
"""
            output = sandbox.run_python(result_code)

            result_str = output.stdout
            start_idx = result_str.find("RESULT_START") + len("RESULT_START")
            end_idx = result_str.find("RESULT_END")

            if start_idx == -1 or end_idx == -1:
                raise Exception("Failed to extract result from sandbox execution")

            result_json = result_str[start_idx:end_idx].strip()
            cleaned_df = pd.read_json(result_json, orient='records')

            sandbox.close()

            logger.info("Preprocessing code executed successfully")
            return cleaned_df

        except Exception as e:
            logger.error(f"Failed to execute preprocessing code: {e}")
            if 'sandbox' in locals():
                sandbox.close()
            raise Exception(f"Code execution failed: {str(e)}")

    def preprocess(self, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        try:
            initial_shape = df.shape
            initial_columns = df.columns.tolist()

            code = self.generate_preprocessing_code(df, target_column)

            cleaned_df = self.execute_preprocessing_code(code, df)

            statistics = {
                'original_shape': initial_shape,
                'cleaned_shape': cleaned_df.shape,
                'removed_rows': initial_shape[0] - cleaned_df.shape[0],
                'removed_columns': len(initial_columns) - len(cleaned_df.columns),
                'null_values_before': df.isnull().sum().sum(),
                'null_values_after': cleaned_df.isnull().sum().sum()
            }

            steps_applied = [
                'Missing value imputation',
                'Outlier detection and removal',
                'Feature standardization',
                'Target column removal',
                'Data type optimization'
            ]

            return {
                'cleaned_data': cleaned_df,
                'statistics': statistics,
                'steps_applied': steps_applied,
                'preprocessing_code': code
            }

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            raise Exception(f"Preprocessing failed: {str(e)}")