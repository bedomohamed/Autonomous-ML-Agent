# Preprocessing Code for 20250914_225940_c0777995_churn
# Generated on: 2025-09-14 23:00:07
# Experiment ID: exp_20250914_225952
# Original file: uploads/20250914_225940_c0777995_churn.csv

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import warnings

warnings.filterwarnings('ignore')

def preprocess_data(input_file='input_data.csv'):
    # Load dataset
    df = pd.read_csv(input_file)
    print(f"Original dataset shape: {df.shape}")

    # Identify column types dynamically
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

    # Remove high-cardinality and ID-like columns
    columns_to_drop = [
        col for col in df.columns 
        if (df[col].nunique() > 50 or 
            any(x in col.lower() for x in ['id', 'name', 'surname', 'row']))
    ]
    
    # Separate features and target
    target_column = 'Exited'
    X = df.drop(columns=[target_column] + columns_to_drop)
    y = df[target_column]

    # Update column lists after dropping
    numeric_columns = [col for col in numeric_columns if col in X.columns]
    categorical_columns = [col for col in categorical_columns if col in X.columns]

    # Preprocessing steps
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(sparse_output=False, handle_unknown='ignore'))
    ])

    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_columns),
            ('cat', categorical_transformer, categorical_columns)
        ],
        remainder='drop'
    )

    # Fit and transform the data
    try:
        X_transformed = preprocessor.fit_transform(X)
        feature_names = (
            numeric_columns + 
            list(preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(categorical_columns))
        )

        # Create cleaned dataframe
        cleaned_df = pd.DataFrame(X_transformed, columns=feature_names)
        cleaned_df[target_column] = y.values

        # Validate transformed data
        print(f"Cleaned dataset shape: {cleaned_df.shape}")
        print(f"Columns: {list(cleaned_df.columns)}")

        # Save cleaned dataset
        cleaned_df.to_csv('cleaned_data.csv', index=False)
        print("Dataset preprocessing completed successfully!")

        return cleaned_df

    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return None

# Execute preprocessing
cleaned_df = preprocess_data()