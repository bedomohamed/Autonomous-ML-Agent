# Preprocessing Code for 20250915_042319_953089d7_churn
# Generated on: 2025-09-15 04:23:54
# Experiment ID: exp_20250915_042340
# Original file: uploads/20250915_042319_953089d7_churn.csv

import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Load the dataset
df = pd.read_csv('input_data.csv')
print(f"Original dataset shape: {df.shape}")
print(f"Original columns: {list(df.columns)}")

# Drop unnecessary columns
columns_to_drop = [col for col in df.columns if 'id' in col.lower() or 'name' in col.lower() or 'number' in col.lower()]
df = df.drop(columns=columns_to_drop, axis=1)
print(f"Columns dropped: {columns_to_drop}")

# Separate features and target
target_column = 'Exited'
X = df.drop(columns=[target_column])
y = df[target_column]

# Identify numeric and categorical columns dynamically
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

print(f"Numeric columns: {numeric_cols}")
print(f"Categorical columns: {categorical_cols}")

# Create preprocessing steps
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
        ('num', numeric_transformer, numeric_cols),
        ('cat', categorical_transformer, categorical_cols)
    ])

# Fit and transform the data
try:
    X_cleaned = preprocessor.fit_transform(X)
    
    # Convert to DataFrame with proper column names
    feature_names = (
        numeric_cols + 
        list(preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(categorical_cols))
    )
    cleaned_df = pd.DataFrame(X_cleaned, columns=feature_names)
    
    # Add back the target column
    cleaned_df[target_column] = y.values
    
    print(f"Final cleaned dataframe shape: {cleaned_df.shape}")
    print(f"Final columns: {list(cleaned_df.columns)}")
    
    # Save the cleaned dataset
    cleaned_df.to_csv('cleaned_data.csv', index=False)
    print("✅ Cleaned dataset saved to 'cleaned_data.csv'")
    
    print(f"✅ File exists: {os.path.exists('cleaned_data.csv')}")
    print(f"✅ File size: {os.path.getsize('cleaned_data.csv') if os.path.exists('cleaned_data.csv') else 'File not found'}")

except Exception as e:
    print(f"An error occurred during preprocessing: {e}")
    raise