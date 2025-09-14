# Comprehensive ML Pipeline Design

## 🔄 Complete Workflow

```
Raw CSV → Data Analysis → Preprocessing → Model Training → Hyperparameter Tuning → Leaderboard
    ↓           ↓              ↓              ↓                    ↓               ↓
 Upload     Statistics    Clean CSV    Multiple Models      Best Models     Rankings
```

## 📊 Stage 1: Data Analysis & Preprocessing Prompt

### Enhanced Prompt Structure for Data Preprocessing:

```python
PREPROCESSING_PROMPT_TEMPLATE = """
You are an expert data scientist. Analyze this dataset and create comprehensive preprocessing code.

## Dataset Information:
- **Filename**: {filename}
- **Target Column**: {target_column}
- **Target Type**: {target_type} (classification/regression)
- **Dataset Shape**: {rows} rows × {columns} columns

## Dataset Summary Statistics:
{summary_statistics}

## Column Details:
{column_analysis}

## Missing Data Analysis:
{missing_data_info}

## Data Quality Issues Detected:
{data_quality_issues}

## Target Variable Analysis:
{target_analysis}

## Your Task:
Create Python code that:
1. **Handles Missing Values**: Use appropriate strategies (mean/mode/forward-fill/drop)
2. **Encodes Categorical Variables**: Label encoding, one-hot encoding, or target encoding
3. **Handles Outliers**: Detect and treat using IQR, Z-score, or domain knowledge
4. **Feature Engineering**: Create new meaningful features if beneficial
5. **Scaling/Normalization**: Apply when needed for the target ML problem
6. **Data Validation**: Ensure data integrity and consistency
7. **Export Clean Dataset**: Save as 'cleaned_data.csv'

## Requirements:
- Use pandas, numpy, sklearn for preprocessing
- Add comments explaining each preprocessing step
- Handle edge cases and provide error handling
- Optimize for the specific target variable type: {target_type}
- Consider the following ML algorithms will be used: XGBoost, Random Forest, Naive Bayes, Decision Tree

## Expected Output Format:
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
# ... other imports

# Load and analyze data
df = pd.read_csv('uploaded_data.csv')

# Preprocessing steps with explanations
# ... your comprehensive preprocessing code ...

# Save cleaned dataset
df_cleaned.to_csv('cleaned_data.csv', index=False)
print("Dataset preprocessing completed successfully!")
```
"""
```

### Data Analysis Components to Extract:

#### 1. **Summary Statistics**
```python
def generate_summary_statistics(df):
    return {
        'shape': df.shape,
        'numeric_summary': df.describe(include=[np.number]).to_dict(),
        'categorical_summary': df.describe(include=['object']).to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'dtypes': df.dtypes.to_dict()
    }
```

#### 2. **Column Analysis**
```python
def analyze_columns(df):
    analysis = {}
    for col in df.columns:
        analysis[col] = {
            'dtype': str(df[col].dtype),
            'null_count': df[col].isnull().sum(),
            'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
            'unique_values': df[col].nunique(),
            'is_numeric': pd.api.types.is_numeric_dtype(df[col]),
            'sample_values': df[col].dropna().head(5).tolist()
        }
    return analysis
```

#### 3. **Target Variable Analysis**
```python
def analyze_target_variable(df, target_column):
    target = df[target_column]

    analysis = {
        'column_name': target_column,
        'data_type': str(target.dtype),
        'unique_values': target.nunique(),
        'null_count': target.isnull().sum(),
    }

    if pd.api.types.is_numeric_dtype(target):
        analysis.update({
            'task_type': 'regression',
            'min_value': target.min(),
            'max_value': target.max(),
            'mean': target.mean(),
            'std': target.std(),
            'distribution': 'continuous'
        })
    else:
        analysis.update({
            'task_type': 'classification',
            'class_distribution': target.value_counts().to_dict(),
            'class_balance': target.value_counts(normalize=True).to_dict()
        })

    return analysis
```

## 🤖 Stage 2: Model Training Prompt

### Comprehensive Model Training Prompt:

```python
MODEL_TRAINING_PROMPT_TEMPLATE = """
You are a machine learning expert. Create comprehensive model training code for this cleaned dataset.

## Dataset Information:
- **Cleaned Dataset**: cleaned_data.csv
- **Target Column**: {target_column}
- **Problem Type**: {task_type}
- **Features**: {feature_columns}
- **Dataset Shape**: {shape}

## Data Split Requirements:
- **Training**: 80% of data
- **Testing**: 15% of data
- **Validation**: 5% of data

## Models to Implement:
1. **XGBoost** - Gradient boosting ensemble
2. **Random Forest** - Bagging ensemble
3. **Naive Bayes** - Probabilistic classifier
4. **Decision Tree** - Interpretable tree-based model
{additional_models}

## Your Task:
Create Python code that:
1. **Loads cleaned data** and prepares features
2. **Splits data** into train/test/validation (80%/15%/5%)
3. **Trains all models** with baseline hyperparameters
4. **Evaluates performance** on test set
5. **Validates on validation set**
6. **Saves trained models** as .pkl files
7. **Generates performance report**

## Evaluation Metrics:
{evaluation_metrics}

## Expected Output Format:
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, r2_score
import pickle
import json

# Load cleaned data
df = pd.read_csv('cleaned_data.csv')

# Prepare features and target
X = df.drop('{target_column}', axis=1)
y = df['{target_column}']

# Split data
X_temp, X_val, y_temp, y_val = train_test_split(X, y, test_size=0.05, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X_temp, y_temp, test_size=0.1875, random_state=42)

# Initialize models
models = {{
    'XGBoost': XGB{model_type}(),
    'Random_Forest': RandomForest{model_type}(),
    'Decision_Tree': DecisionTree{model_type}(),
    'Naive_Bayes': GaussianNB()
}}

# Training and evaluation
results = {{}}
for name, model in models.items():
    # Train model
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)
    y_val_pred = model.predict(X_val)

    # Evaluate performance
    # ... evaluation code based on task type ...

    # Save model
    with open(f'{{name}}_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    results[name] = evaluation_results

# Save results
with open('model_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Model training completed!")
```
"""
```

## 🎯 Stage 3: Hyperparameter Tuning Prompt

```python
HYPERPARAMETER_TUNING_PROMPT_TEMPLATE = """
You are an expert in ML optimization. Tune hyperparameters for the best performing models.

## Previous Results:
{previous_results}

## Top Performing Models (to tune):
{top_models}

## Hyperparameter Search Spaces:

### XGBoost:
- n_estimators: [100, 200, 300, 500]
- max_depth: [3, 5, 7, 9]
- learning_rate: [0.01, 0.1, 0.2, 0.3]
- subsample: [0.8, 0.9, 1.0]
- colsample_bytree: [0.8, 0.9, 1.0]

### Random Forest:
- n_estimators: [100, 200, 300, 500]
- max_depth: [None, 10, 20, 30]
- min_samples_split: [2, 5, 10]
- min_samples_leaf: [1, 2, 4]
- max_features: ['sqrt', 'log2', None]

### Decision Tree:
- max_depth: [3, 5, 10, 15, None]
- min_samples_split: [2, 5, 10, 20]
- min_samples_leaf: [1, 2, 5, 10]
- criterion: ['{criterion_options}']

## Your Task:
Create code that:
1. **Loads cleaned data and best models**
2. **Performs GridSearchCV or RandomizedSearchCV**
3. **Uses cross-validation** for robust evaluation
4. **Finds optimal hyperparameters**
5. **Trains final models** with best parameters
6. **Compares with baseline results**
7. **Saves tuned models and results**

## Expected Output:
- Tuned model files (.pkl)
- Hyperparameter optimization results (.json)
- Performance comparison report
- Feature importance analysis
```

## 📊 Stage 4: Results Dashboard Structure

### Leaderboard Data Structure:
```python
{
  "experiment_id": "exp_20240314_143052",
  "dataset_info": {
    "name": "customer_churn.csv",
    "target": "churn",
    "task_type": "classification",
    "features": 15,
    "samples": 5000
  },
  "results": {
    "baseline_models": {
      "XGBoost": {
        "accuracy": 0.85,
        "precision": 0.82,
        "recall": 0.88,
        "f1_score": 0.85,
        "training_time": 2.3,
        "model_size": "1.2MB"
      },
      // ... other models
    },
    "tuned_models": {
      "XGBoost_tuned": {
        "accuracy": 0.89,
        "precision": 0.87,
        "recall": 0.91,
        "f1_score": 0.89,
        "best_params": {
          "n_estimators": 300,
          "max_depth": 7,
          "learning_rate": 0.1
        },
        "improvement": "+4.7%",
        "training_time": 15.2,
        "model_size": "3.8MB"
      }
      // ... other tuned models
    }
  },
  "leaderboard": [
    {
      "rank": 1,
      "model": "XGBoost_tuned",
      "score": 0.89,
      "improvement": "+4.7%",
      "status": "tuned"
    }
    // ... rankings
  ]
}
```

## 🎨 Frontend Components Needed

### 1. **DataAnalysis Component**
- Dataset overview cards
- Summary statistics visualization
- Missing data heatmap
- Target variable distribution

### 2. **ModelTraining Component**
- Training progress indicator
- Real-time model performance
- Model comparison table
- Download links for models

### 3. **HyperparameterTuning Component**
- Tuning progress visualization
- Parameter space exploration
- Performance improvement tracking
- Best parameters display

### 4. **ResultsLeaderboard Component**
- Sortable model rankings
- Performance metrics comparison
- Model improvement indicators
- Download buttons for models/code

## 🔧 Implementation Strategy

### Backend Endpoints:
```python
POST /api/analyze-dataset     # Stage 1: Data analysis
POST /api/preprocess-data     # Stage 1: Generate preprocessing code
POST /api/train-models        # Stage 2: Train baseline models
POST /api/tune-hyperparams    # Stage 3: Hyperparameter tuning
GET  /api/results/{exp_id}    # Stage 4: Get experiment results
GET  /api/download/model/{id} # Download trained models
GET  /api/download/code/{id}  # Download generated code
```

### Data Flow:
```
CSV Upload → Data Analysis → Preprocessing Code Generation → E2B Execution →
Clean CSV → Model Training Code → E2B Execution → Models & Results →
Hyperparameter Tuning → Final Models → Leaderboard Display
```

This comprehensive approach will create a full-featured AutoML platform with explainable preprocessing, multiple model training, optimization, and results comparison!