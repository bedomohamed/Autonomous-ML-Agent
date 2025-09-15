# Preprocessing Code for 20250915_045048_78478c3b_churn
# Generated on: 2025-09-15 04:51:34
# Experiment ID: exp_20250915_045120
# Original file: uploads/20250915_045048_78478c3b_churn.csv

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

# Identify columns to drop (IDs, names, high cardinality)
columns_to_drop = [col for col in df.columns if 
                   col.lower() in ['rownumber', 'customerid', 'surname'] or 
                   df[col].nunique() > df.shape[0] * 0.5]

# Drop unnecessary columns
df = df.drop(columns=columns_to_drop, axis=1)
print(f"Columns dropped: {columns_to_drop}")

# Identify numeric and categorical columns dynamically
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

# Remove target variable from feature columns
if 'Exited' in numeric_cols:
    numeric_cols.remove('Exited')
if 'Exited' in categorical_cols:
    categorical_cols.remove('Exited')

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

# Separate features and target
X = df.drop('Exited', axis=1)
y = df['Exited']

# Fit and transform the data
try:
    X_transformed = preprocessor.fit_transform(X)
    
    # Reconstruct dataframe with transformed features
    feature_names = (
        numeric_cols + 
        list(preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(categorical_cols))
    )
    
    cleaned_df = pd.DataFrame(X_transformed, columns=feature_names)
    cleaned_df['Exited'] = y.values
    
    print(f"Final cleaned dataframe shape: {cleaned_df.shape}")
    print(f"Final columns: {list(cleaned_df.columns)}")
    
    cleaned_df.to_csv('cleaned_data.csv', index=False)
    print("✅ Cleaned dataset saved to 'cleaned_data.csv'")
    
    print(f"✅ File exists: {os.path.exists('cleaned_data.csv')}")
    print(f"✅ File size: {os.path.getsize('cleaned_data.csv') if os.path.exists('cleaned_data.csv') else 'File not found'}")

except Exception as e:
    print(f"Error during preprocessing: {e}")
    raise