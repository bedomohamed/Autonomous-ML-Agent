import os
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
import joblib
import json

# Create storage directories
os.makedirs('storage/models', exist_ok=True)

# Load cleaned data
try:
    data = pd.read_csv('cleaned_data.csv')
    print(f"Dataset Shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")
except FileNotFoundError:
    print("Error: cleaned_data.csv not found")
    exit(1)

# Validate target column
if 'Exited' not in data.columns:
    print("Error: 'Exited' column not found")
    exit(1)

# Prepare data
X = data.drop('Exited', axis=1)
y = data['Exited']

# Split data
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
X_test, X_val, y_test, y_val = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

print(f"Train set size: {X_train.shape[0]}")
print(f"Test set size: {X_test.shape[0]}")
print(f"Validation set size: {X_val.shape[0]}")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_val_scaled = scaler.transform(X_val)

# Save scaler
joblib.dump(scaler, 'storage/models/scaler.pkl')

# Define models
models = {
    'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss'),
    'Random_Forest': RandomForestClassifier(random_state=42),
    'Decision_Tree': DecisionTreeClassifier(random_state=42),
    'Naive_Bayes': GaussianNB()
}

# Results dictionary
results = {}
best_model = {'name': None, 'score': 0}

# Train and evaluate models
for name, model in models.items():
    try:
        # Train model
        start_time = time.time()
        model.fit(X_train_scaled, y_train)
        end_time = time.time()
        training_time = end_time - start_time

        # Predict
        y_pred = model.predict(X_test_scaled)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        # Store results
        results[name] = {
            'accuracy': round(accuracy, 4),
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4),
            'training_time': round(training_time, 2)
        }

        # Track best model
        if f1 > best_model['score']:
            best_model['name'] = name
            best_model['score'] = f1

        # Save model
        joblib.dump(model, f'storage/models/{name}_model.pkl')

        print(f"{name} Training Complete")
    except Exception as e:
        print(f"Error training {name}: {e}")

# Save results JSON
with open('storage/models/model_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Save best model info
with open('storage/models/best_model_info.json', 'w') as f:
    json.dump(best_model, f, indent=2)

print("Model Training Complete")