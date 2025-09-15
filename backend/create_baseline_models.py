#!/usr/bin/env python3
"""
Script to create baseline model files for download functionality
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def create_baseline_models():
    """Create baseline model files for download"""

    # Create models directory
    models_dir = os.path.join('storage', 'models')
    os.makedirs(models_dir, exist_ok=True)

    # Load the cleaned data
    try:
        cleaned_data_path = 'cleaned_data.csv'
        if not os.path.exists(cleaned_data_path):
            # Try to find the most recent cleaned data file
            processed_dir = os.path.join('storage', 'processed')
            if os.path.exists(processed_dir):
                cleaned_files = [f for f in os.listdir(processed_dir) if 'cleaned' in f and f.endswith('.csv')]
                if cleaned_files:
                    # Get the most recent file
                    cleaned_files.sort()
                    cleaned_data_path = os.path.join(processed_dir, cleaned_files[-1])
                else:
                    print("No cleaned data files found")
                    return
            else:
                print("No processed directory found")
                return

        print(f"Loading data from: {cleaned_data_path}")
        data = pd.read_csv(cleaned_data_path)

        # Prepare features and target
        X = data.drop('Exited', axis=1)
        y = data['Exited']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Save scaler
        scaler_path = os.path.join(models_dir, 'scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        print(f"Saved scaler to: {scaler_path}")

        # Create and train baseline models
        models = {
            'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss'),
            'Random_Forest': RandomForestClassifier(random_state=42),
            'Decision_Tree': DecisionTreeClassifier(random_state=42),
            'Naive_Bayes': GaussianNB()
        }

        for model_name, model in models.items():
            print(f"Training {model_name}...")

            # Train the model
            if model_name in ['XGBoost', 'Random_Forest', 'Decision_Tree']:
                model.fit(X_train_scaled, y_train)
            else:  # Naive Bayes
                model.fit(X_train_scaled, y_train)

            # Save the model
            model_path = os.path.join(models_dir, f'{model_name}_model.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)

            print(f"Saved {model_name} model to: {model_path}")

            # Calculate and print baseline metrics
            y_pred = model.predict(X_test_scaled)
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')

            print(f"{model_name} baseline metrics:")
            print(f"  Accuracy: {accuracy:.3f}")
            print(f"  F1-Score: {f1:.3f}")
            print(f"  Precision: {precision:.3f}")
            print(f"  Recall: {recall:.3f}")
            print()

    except Exception as e:
        print(f"Error creating baseline models: {e}")

if __name__ == "__main__":
    create_baseline_models()