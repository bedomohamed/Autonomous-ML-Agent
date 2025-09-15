import os
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic
import json
import re

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        """Initialize Claude API client"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key or self.api_key == 'your_anthropic_key_here':
            raise ValueError("ANTHROPIC_API_KEY environment variable not set or is placeholder")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-haiku-20241022"

        logger.info("Claude API service initialized successfully")

    def generate_preprocessing_code(self, analysis_prompt: str, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate preprocessing code using Claude API"""
        try:
            logger.info(f"Generating preprocessing code for experiment: {dataset_info.get('experiment_id', 'unknown')}")

            # Enhanced prompt with specific instructions and dataset context
            enhanced_prompt = f"""
{analysis_prompt}

Dataset Information:
- File: {dataset_info.get('storage_key', 'input_data.csv')}
- Target Column: {dataset_info.get('target_column', 'target')}
- Shape: {dataset_info.get('shape', 'unknown')}

🚨 CRITICAL REQUIREMENTS - CODE WILL FAIL IF THESE ARE NOT FOLLOWED:
1. Generate COMPLETE, EXECUTABLE Python code only
2. Include ALL necessary imports at the top
3. Use MODERN scikit-learn API (version 1.0+):
   - Use sparse_output=False instead of sparse=False in OneHotEncoder
   - Use feature_names_out parameter where applicable
   - Handle deprecated parameters correctly
4. Add comprehensive comments explaining each step
5. Handle edge cases and errors gracefully with try-catch blocks
6. Use print statements to show progress and results
7. 🔥 MANDATORY: Save the final cleaned dataset as 'cleaned_data.csv' using: cleaned_df.to_csv('cleaned_data.csv', index=False)
8. Assign the final result to variable 'cleaned_df'
9. 🔥 CRITICAL: Your code MUST include the line: cleaned_df.to_csv('cleaned_data.csv', index=False)
10. Add data validation checks before and after processing
11. MUST work with actual dataset - detect column types automatically, don't hardcode column names
12. Handle any dataset structure - analyze columns automatically

MODERN SKLEARN SYNTAX EXAMPLES:
- OneHotEncoder(sparse_output=False, drop='first')
- LabelEncoder() (unchanged)
- StandardScaler() (unchanged)
- Use ColumnTransformer with feature_names_out parameter

CODE STRUCTURE (FOLLOW THIS EXACT ORDER):
1. Load data from 'input_data.csv'
2. Print original shape and column info
3. FIRST: Drop columns that won't be used (IDs, names, high-cardinality columns)
4. AFTER dropping: Identify numeric and categorical columns from REMAINING columns only
5. Create preprocessing pipeline using ONLY the remaining columns after dropping
6. Exclude the target column '{dataset_info.get('target_column', 'target')}' from features
7. Apply preprocessing to the cleaned dataset
8. Print final shape before saving
9. 🔥 Save final cleaned dataset as 'cleaned_data.csv'
10. 🔥 Print confirmation that file was saved

⚠️ CRITICAL ORDERING:
- Drop unwanted columns FIRST
- Define numeric/categorical column lists AFTER dropping
- Create preprocessor using ONLY remaining columns
- This prevents "column not found" errors

EXAMPLE FLOW:
```python
# WRONG - causes "column not found" errors:
numeric_cols = ['RowNumber', 'Age', 'Balance']  # includes RowNumber
df = df.drop(['RowNumber'], axis=1)  # RowNumber no longer exists
preprocessor = ColumnTransformer([('num', StandardScaler(), numeric_cols)])  # ERROR!

# CORRECT - identify columns AFTER dropping:
df = df.drop(['RowNumber'], axis=1)  # drop first
numeric_cols = ['Age', 'Balance']  # only remaining columns
preprocessor = ColumnTransformer([('num', StandardScaler(), numeric_cols)])  # works!
```

CRITICAL: Do NOT one-hot encode columns like:
- Names (FirstName, LastName, Surname, etc.)
- IDs (CustomerID, UserID, RowNumber, etc.)
- Unique identifiers with many unique values
- Columns with >50 unique values

Instead, DROP these columns as they don't contribute to prediction.

IMPORTANT: DO NOT hardcode column names. Use dynamic analysis:
- Check if columns exist before dropping them
- Use pattern matching to identify ID/name columns (e.g., contains 'id', 'name', 'surname')
- Analyze cardinality programmatically

🚨 DEBUGGING REQUIREMENTS:
- Print the dataframe shape before and after each major transformation
- Print column names and their data types
- Print which columns are being dropped and why
- Print which columns are being encoded
- Use try-catch blocks with detailed error messages
- Print success messages for each major step

🔥 FINAL CRITICAL REMINDER: Your code MUST end with these EXACT lines:
print(f"Final cleaned dataframe shape: {{cleaned_df.shape}}")
print(f"Final columns: {{list(cleaned_df.columns)}}")
cleaned_df.to_csv('cleaned_data.csv', index=False)
print("✅ Cleaned dataset saved to 'cleaned_data.csv'")
import os
print(f"✅ File exists: {{os.path.exists('cleaned_data.csv')}}")
print(f"✅ File size: {{os.path.getsize('cleaned_data.csv') if os.path.exists('cleaned_data.csv') else 'File not found'}}")

RESPONSE FORMAT:
- Return ONLY executable Python code
- NO markdown code blocks (```python)
- NO explanations, comments, or text before/after the code
- Start directly with import statements
- End with the file verification lines above
            """

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,  # Low temperature for consistent code generation
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ]
            )

            generated_code = response.content[0].text

            # Clean and validate the generated code
            cleaned_code = self._clean_code(generated_code)
            validation_result = self._validate_code(cleaned_code)

            # Generate code explanation
            explanation = self._generate_code_explanation(cleaned_code)

            result = {
                'preprocessing_code': cleaned_code,
                'code_explanation': explanation,
                'validation_passed': validation_result['valid'],
                'validation_issues': validation_result.get('issues', []),
                'estimated_execution_time': self._estimate_execution_time(cleaned_code),
                'code_metrics': self._analyze_code_metrics(cleaned_code)
            }

            logger.info("Preprocessing code generated successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to generate preprocessing code: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")

    def generate_training_code(self, dataset_info: Dict[str, Any], cleaned_data_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate model training code using Claude API"""
        try:
            logger.info(f"Generating training code for {dataset_info.get('task_type', 'unknown')} task")

            training_prompt = self._build_training_prompt(dataset_info, cleaned_data_analysis)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": training_prompt}
                ]
            )

            generated_code = response.content[0].text
            cleaned_code = self._clean_code(generated_code)

            result = {
                'training_code': cleaned_code,
                'models_included': self._extract_models_from_code(cleaned_code),
                'evaluation_metrics': self._extract_metrics_from_code(cleaned_code),
                'estimated_training_time': self._estimate_training_time(dataset_info),
                'code_explanation': self._generate_training_explanation(cleaned_code)
            }

            logger.info("Training code generated successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to generate training code: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")

    def generate_hyperparameter_tuning_code(self, baseline_results: Dict[str, Any], top_models: list) -> Dict[str, Any]:
        """Generate hyperparameter tuning code for best performing models"""
        try:
            logger.info(f"Generating hyperparameter tuning code for models: {top_models}")

            tuning_prompt = self._build_tuning_prompt(baseline_results, top_models)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": tuning_prompt}
                ]
            )

            generated_code = response.content[0].text
            cleaned_code = self._clean_code(generated_code)

            result = {
                'tuning_code': cleaned_code,
                'models_to_tune': top_models,
                'search_strategy': self._extract_search_strategy(cleaned_code),
                'parameter_grids': self._extract_parameter_grids(cleaned_code),
                'estimated_tuning_time': self._estimate_tuning_time(len(top_models))
            }

            logger.info("Hyperparameter tuning code generated successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to generate tuning code: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")

    def _clean_code(self, raw_code: str) -> str:
        """Clean and format the generated code"""
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```python\n?', '', raw_code)
        cleaned = re.sub(r'```\n?', '', cleaned)

        # Basic cleanup - just strip whitespace and normalize line endings
        cleaned = cleaned.strip()

        # Remove any duplicate empty lines
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)

        return cleaned

    def _validate_code(self, code: str) -> Dict[str, Any]:
        """Basic validation of generated code"""
        issues = []

        # First check Python syntax
        try:
            import ast
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Python syntax error at line {e.lineno}: {e.msg}")

        # Check for required imports
        required_imports = ['pandas', 'numpy', 'sklearn']
        for imp in required_imports:
            if imp not in code:
                issues.append(f"Missing {imp} import")

        # Check for final CSV save
        if 'to_csv(' not in code:
            issues.append("Missing final CSV save operation")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def _generate_code_explanation(self, code: str) -> str:
        """Generate a brief explanation of what the code does"""
        try:
            explanation_prompt = f"""
Analyze this preprocessing code and provide a brief explanation of what it does:

{code[:1000]}...

Provide a concise 2-3 sentence explanation focusing on the main preprocessing steps.
            """

            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": explanation_prompt}
                ]
            )

            return response.content[0].text.strip()

        except Exception:
            return "Preprocessing code that cleans and prepares the dataset for machine learning."

    def _analyze_code_metrics(self, code: str) -> Dict[str, Any]:
        """Analyze basic metrics of the generated code"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith('#')]

        return {
            'total_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'comment_lines': len(comment_lines),
            'comment_ratio': len(comment_lines) / max(len(non_empty_lines), 1)
        }

    def _estimate_execution_time(self, code: str) -> int:
        """Estimate execution time based on code complexity"""
        # Simple heuristic based on operations
        base_time = 10  # seconds

        if 'StandardScaler' in code:
            base_time += 5
        if 'OneHotEncoder' in code:
            base_time += 10
        if 'fillna' in code:
            base_time += 5
        if 'drop' in code:
            base_time += 2

        return base_time

    def _build_training_prompt(self, dataset_info: Dict[str, Any], cleaned_data_analysis: Optional[Dict] = None) -> str:
        """Build comprehensive training prompt"""
        task_type = dataset_info.get('task_type', 'classification')
        target_column = dataset_info.get('target_column', 'target')
        shape = dataset_info.get('shape', {})

        if task_type == 'classification':
            model_imports = """
import time
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
            """
            model_init = """
models = {
    'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss'),
    'Random_Forest': RandomForestClassifier(random_state=42),
    'Decision_Tree': DecisionTreeClassifier(random_state=42),
    'Naive_Bayes': GaussianNB()
}
            """
        else:
            model_imports = """
import time
import json
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
            """
            model_init = """
models = {
    'XGBoost': XGBRegressor(random_state=42),
    'Random_Forest': RandomForestRegressor(random_state=42),
    'Decision_Tree': DecisionTreeRegressor(random_state=42),
    'Linear_Regression': LinearRegression()
}
            """

        return f"""
You are a machine learning expert. Create comprehensive model training code for this dataset:

## Dataset Information:
- **Target Column**: {target_column}
- **Task Type**: {task_type}
- **Dataset Shape**: {shape.get('rows', 'unknown')} rows × {shape.get('columns', 'unknown')} columns

## CRITICAL REQUIREMENTS:

### File Organization:
1. Create 'storage/models' directory if it doesn't exist: `os.makedirs('storage/models', exist_ok=True)`
2. Save ALL model files (.pkl) in the 'storage/models/' directory
3. Save results JSON in 'storage/models/' directory
4. Save scaler in 'storage/models/' directory

### Data Handling:
1. Load cleaned data from 'cleaned_data.csv'
2. CRITICAL: The target column is named '{target_column}' - DO NOT use 'target' as the column name
3. Use X = data.drop('{target_column}', axis=1) and y = data['{target_column}']
4. Check if '{target_column}' column exists before using it
5. Print dataset shape and column names for debugging

### Data Splitting:
1. Split: 70% train, 15% test, 15% validation
2. Use stratified sampling for classification: `stratify=y`
3. Print split sizes for verification
4. Scale features using StandardScaler and save the scaler

### Model Training:
{model_init.strip()}

### Error Handling:
1. Use try-except blocks for all major operations
2. Check if files exist before loading
3. Validate data shapes and types
4. Handle missing columns gracefully

### Model Training & Timing:
1. CRITICAL: Track training time for each model using time.time()
2. Train each model separately and measure individual training times
3. Use this EXACT pattern for each model:
   ```
   start_time = time.time()
   model.fit(X_train_scaled, y_train)
   end_time = time.time()
   training_time = end_time - start_time
   ```
4. Store training_time in results dictionary for each model

### Output Requirements:
1. Print detailed progress for each step
2. Show model performance metrics
3. Save each model with descriptive filename: 'storage/models/{{model_name}}_model.pkl'
4. Save scaler as 'storage/models/scaler.pkl'
5. CRITICAL: Save results as 'storage/models/model_results.json' with EXACT format:
   {{
     "XGBoost": {{
       "accuracy": 0.85,
       "precision": 0.82,
       "recall": 0.88,
       "f1_score": 0.85,
       "training_time": 12.5
     }},
     "Random_Forest": {{
       "accuracy": 0.83,
       "precision": 0.80,
       "recall": 0.86,
       "f1_score": 0.83,
       "training_time": 8.2
     }}
   }}
6. Save best model info as 'storage/models/best_model_info.json'
7. MANDATORY: Include 'training_time' field for each model in the JSON results

## RESPONSE FORMAT:
- Return ONLY executable Python code
- NO markdown code blocks (```python)
- NO explanations, comments, or text before/after the code
- Start directly with import statements
- End with the last line of actual Python code

Generate COMPLETE, EXECUTABLE Python code with proper error handling and file organization.
        """

    def _build_tuning_prompt(self, baseline_results: Dict[str, Any], top_models: list) -> str:
        """Build hyperparameter tuning prompt"""
        return f"""
You are a machine learning optimization expert. Create hyperparameter tuning code for these top-performing models:

## Top Models to Tune:
{', '.join(top_models)}

## Baseline Results:
{json.dumps(baseline_results, indent=2)[:500]}...

## CRITICAL REQUIREMENTS:

### File Organization:
1. Create 'storage/models' directory if it doesn't exist: `os.makedirs('storage/models', exist_ok=True)`
2. Load baseline models from 'storage/models/' directory
3. Save all tuned models in 'storage/models/' directory
4. Save tuning results as 'storage/models/hyperparameter_tuning_results.json'
5. Save comparison report as 'storage/models/tuning_comparison_report.json'

### Data and Model Loading:
1. Load cleaned data from 'cleaned_data.csv' with target column 'Exited' (NOT 'target')
2. Load baseline models from 'storage/models/{{model_name}}_model.pkl'
3. Load scaler from 'storage/models/scaler.pkl' if it exists
4. IMPORTANT: Use 'Exited' as the target column name, not 'target'

### Hyperparameter Tuning:
1. Use GridSearchCV with 3-fold cross-validation and scoring='f1_weighted' for classification
2. Use comprehensive parameter grids (provided below)
3. Track improvement over baseline performance
4. Print progress and intermediate results
5. Use n_jobs=1 in GridSearchCV to avoid memory issues
6. Add timeout protection and early stopping if needed
7. Split data properly: 70% train, 30% test (use same random_state=42 for consistency)
8. Scale features using StandardScaler if scaler doesn't exist

### Parameter Grids (Optimized for Speed):

#### XGBoost:
- n_estimators: [100, 200]
- max_depth: [3, 5, 7]
- learning_rate: [0.1, 0.2]

#### Random Forest:
- n_estimators: [100, 200]
- max_depth: [10, 20]
- min_samples_split: [2, 5]

#### Decision Tree:
- max_depth: [10, 15, 20]
- min_samples_split: [2, 5]
- min_samples_leaf: [1, 2]

### Baseline Results (for comparison):
{json.dumps(baseline_results, indent=2)}

### Output Requirements:
1. Save tuned models with descriptive filenames: 'storage/models/{{model_name}}_tuned_model.pkl'
2. Print detailed comparison between baseline and tuned models
3. Save comprehensive results including best parameters and performance improvements
4. Generate summary report with recommendations
5. DO NOT try to load baseline_results.json - the baseline results are provided above

## CRITICAL: Dependencies Installation
MUST START with dependency installation BEFORE any other imports:

EXACT code structure required:
1. First: import subprocess, sys
2. Second: install packages with pip
3. Third: import all other packages (sklearn, xgboost, etc.)
4. Fourth: import time and add progress tracking
5. Fifth: actual hyperparameter tuning code with time monitoring

## RESPONSE FORMAT:
- Return ONLY executable Python code
- NO markdown code blocks (```python)
- NO explanations, comments, or text before/after the code
- MUST start with: import subprocess, sys
- MUST install dependencies BEFORE importing xgboost
- End with the last line of actual Python code

Generate COMPLETE, EXECUTABLE Python code with dependency installation and proper error handling.
        """

    def _extract_models_from_code(self, code: str) -> list:
        """Extract model names from training code"""
        models = []
        if 'XGBoost' in code:
            models.append('XGBoost')
        if 'Random_Forest' in code:
            models.append('Random_Forest')
        if 'Decision_Tree' in code:
            models.append('Decision_Tree')
        if 'Naive_Bayes' in code:
            models.append('Naive_Bayes')
        if 'Linear_Regression' in code:
            models.append('Linear_Regression')
        return models

    def _extract_metrics_from_code(self, code: str) -> list:
        """Extract evaluation metrics from training code"""
        metrics = []
        if 'accuracy_score' in code:
            metrics.append('accuracy')
        if 'f1_score' in code:
            metrics.append('f1_score')
        if 'precision_score' in code:
            metrics.append('precision')
        if 'recall_score' in code:
            metrics.append('recall')
        if 'r2_score' in code:
            metrics.append('r2_score')
        if 'mean_squared_error' in code:
            metrics.append('mse')
        return metrics

    def _generate_training_explanation(self, code: str) -> str:
        """Generate explanation for training code"""
        models = self._extract_models_from_code(code)
        return f"Trains {len(models)} machine learning models ({', '.join(models)}) with proper data splitting, evaluation, and model persistence."

    def _estimate_training_time(self, dataset_info: Dict[str, Any]) -> int:
        """Estimate training time based on dataset size"""
        shape = dataset_info.get('shape', {})
        rows = shape.get('rows', 1000)
        cols = shape.get('columns', 10)

        # Base time for 4 models
        base_time = 30  # seconds

        # Scale with data size
        if rows > 10000:
            base_time += 30
        if rows > 50000:
            base_time += 60
        if cols > 50:
            base_time += 20

        return base_time

    def _extract_search_strategy(self, code: str) -> str:
        """Extract hyperparameter search strategy from code"""
        if 'GridSearchCV' in code:
            return 'GridSearch'
        elif 'RandomizedSearchCV' in code:
            return 'RandomizedSearch'
        else:
            return 'Unknown'

    def _extract_parameter_grids(self, code: str) -> Dict[str, Any]:
        """Extract parameter grids from tuning code"""
        # Simple extraction - in a real implementation, you'd parse the actual grids
        return {
            'note': 'Parameter grids defined in the generated code',
            'strategy': self._extract_search_strategy(code)
        }

    def _estimate_tuning_time(self, num_models: int) -> int:
        """Estimate hyperparameter tuning time"""
        # Base time per model with grid search
        base_time_per_model = 300  # 5 minutes
        return num_models * base_time_per_model

    def health_check(self) -> Dict[str, Any]:
        """Check if Claude API is accessible"""
        try:
            # Simple test call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Respond with 'OK'"}
                ]
            )

            return {
                'status': 'healthy',
                'api_accessible': True,
                'model': self.model,
                'test_response': response.content[0].text.strip()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'api_accessible': False,
                'error': str(e)
            }