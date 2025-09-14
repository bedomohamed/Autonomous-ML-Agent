import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_csv_file(df: pd.DataFrame) -> dict:
    validation_result = {
        'valid': True,
        'message': 'CSV file is valid',
        'warnings': []
    }

    if df.empty:
        validation_result['valid'] = False
        validation_result['message'] = 'CSV file is empty'
        return validation_result

    if len(df.columns) < 2:
        validation_result['valid'] = False
        validation_result['message'] = 'CSV must have at least 2 columns'
        return validation_result

    if len(df) < 10:
        validation_result['warnings'].append('CSV has less than 10 rows')

    if df.duplicated().sum() > 0:
        validation_result['warnings'].append(f'{df.duplicated().sum()} duplicate rows detected')

    null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if null_percentage > 50:
        validation_result['valid'] = False
        validation_result['message'] = f'CSV has {null_percentage:.1f}% missing values (>50% threshold)'
        return validation_result
    elif null_percentage > 20:
        validation_result['warnings'].append(f'CSV has {null_percentage:.1f}% missing values')

    for col in df.columns:
        if df[col].nunique() == 1:
            validation_result['warnings'].append(f"Column '{col}' has only one unique value")

    if validation_result['warnings']:
        logger.warning(f"CSV validation warnings: {validation_result['warnings']}")

    return validation_result

def validate_target_column(df: pd.DataFrame, target_column: str) -> dict:
    validation_result = {
        'valid': True,
        'message': 'Target column is valid',
        'target_type': None
    }

    if target_column not in df.columns:
        validation_result['valid'] = False
        validation_result['message'] = f"Target column '{target_column}' not found in dataset"
        return validation_result

    target_data = df[target_column]

    if target_data.isnull().all():
        validation_result['valid'] = False
        validation_result['message'] = 'Target column contains only null values'
        return validation_result

    null_percentage = (target_data.isnull().sum() / len(target_data)) * 100
    if null_percentage > 10:
        validation_result['valid'] = False
        validation_result['message'] = f'Target column has {null_percentage:.1f}% missing values (>10% threshold)'
        return validation_result

    unique_values = target_data.nunique()

    if unique_values == 1:
        validation_result['valid'] = False
        validation_result['message'] = 'Target column has only one unique value'
        return validation_result

    if unique_values == 2:
        validation_result['target_type'] = 'binary_classification'
    elif unique_values < 10:
        validation_result['target_type'] = 'multiclass_classification'
    elif target_data.dtype in ['float64', 'int64']:
        validation_result['target_type'] = 'regression'
    else:
        validation_result['target_type'] = 'unknown'

    return validation_result