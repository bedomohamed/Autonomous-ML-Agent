import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import logging
from scipy import stats
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class DataAnalysisService:
    def __init__(self):
        self.df = None
        self.target_column = None
        self.analysis_results = {}

    def analyze_dataset(self, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """
        Comprehensive dataset analysis for ML pipeline prompting
        """
        self.df = df.copy()
        self.target_column = target_column

        logger.info(f"Starting comprehensive analysis for dataset with shape {df.shape}")

        try:
            analysis = {
                'basic_info': self._get_basic_info(),
                'summary_statistics': self._get_summary_statistics(),
                'column_analysis': self._analyze_columns(),
                'missing_data_info': self._analyze_missing_data(),
                'data_quality_issues': self._detect_data_quality_issues(),
                'target_analysis': self._analyze_target_variable(),
                'correlation_analysis': self._analyze_correlations(),
                'feature_recommendations': self._get_feature_recommendations(),
                'preprocessing_suggestions': self._suggest_preprocessing_steps()
            }

            self.analysis_results = analysis
            logger.info("Dataset analysis completed successfully")
            return analysis

        except Exception as e:
            logger.error(f"Dataset analysis failed: {e}")
            raise Exception(f"Failed to analyze dataset: {str(e)}")

    def _get_basic_info(self) -> Dict[str, Any]:
        """Basic dataset information"""
        return {
            'shape': {
                'rows': len(self.df),
                'columns': len(self.df.columns)
            },
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2),
            'column_names': list(self.df.columns),
            'dtypes_summary': {
                'numeric': len(self.df.select_dtypes(include=[np.number]).columns),
                'categorical': len(self.df.select_dtypes(include=['object']).columns),
                'datetime': len(self.df.select_dtypes(include=['datetime64']).columns),
                'boolean': len(self.df.select_dtypes(include=['bool']).columns)
            }
        }

    def _get_summary_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns

        summary = {
            'numeric_summary': {},
            'categorical_summary': {}
        }

        # Numeric statistics
        if len(numeric_cols) > 0:
            numeric_stats = self.df[numeric_cols].describe()
            summary['numeric_summary'] = {
                'statistics': numeric_stats.to_dict(),
                'additional_metrics': {}
            }

            # Additional numeric metrics
            for col in numeric_cols:
                col_data = self.df[col].dropna()
                summary['numeric_summary']['additional_metrics'][col] = {
                    'skewness': float(stats.skew(col_data)),
                    'kurtosis': float(stats.kurtosis(col_data)),
                    'outliers_iqr': self._count_outliers_iqr(col_data),
                    'outliers_zscore': self._count_outliers_zscore(col_data),
                    'zeros_count': int((col_data == 0).sum()),
                    'negative_count': int((col_data < 0).sum())
                }

        # Categorical statistics
        if len(categorical_cols) > 0:
            summary['categorical_summary'] = {}
            for col in categorical_cols:
                col_data = self.df[col].dropna()
                value_counts = col_data.value_counts()

                summary['categorical_summary'][col] = {
                    'unique_values': int(col_data.nunique()),
                    'most_frequent': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'distribution': value_counts.head(10).to_dict(),
                    'cardinality': 'high' if col_data.nunique() > len(col_data) * 0.5 else 'low'
                }

        return summary

    def _analyze_columns(self) -> Dict[str, Dict[str, Any]]:
        """Detailed analysis of each column"""
        analysis = {}

        for col in self.df.columns:
            col_data = self.df[col]

            analysis[col] = {
                'dtype': str(col_data.dtype),
                'null_count': int(col_data.isnull().sum()),
                'null_percentage': round((col_data.isnull().sum() / len(col_data)) * 100, 2),
                'unique_values': int(col_data.nunique()),
                'unique_percentage': round((col_data.nunique() / len(col_data)) * 100, 2),
                'is_numeric': pd.api.types.is_numeric_dtype(col_data),
                'is_categorical': pd.api.types.is_object_dtype(col_data),
                'sample_values': col_data.dropna().head(5).tolist(),
                'data_quality_score': self._calculate_column_quality_score(col_data)
            }

            # Additional analysis based on data type
            if pd.api.types.is_numeric_dtype(col_data):
                analysis[col].update({
                    'min_value': float(col_data.min()) if not col_data.empty else None,
                    'max_value': float(col_data.max()) if not col_data.empty else None,
                    'range': float(col_data.max() - col_data.min()) if not col_data.empty else None,
                    'has_outliers': self._has_outliers(col_data),
                    'distribution_type': self._guess_distribution_type(col_data)
                })
            elif pd.api.types.is_object_dtype(col_data):
                analysis[col].update({
                    'avg_string_length': col_data.dropna().astype(str).str.len().mean() if not col_data.dropna().empty else 0,
                    'contains_numbers': col_data.dropna().astype(str).str.contains(r'\d').any() if not col_data.dropna().empty else False,
                    'contains_special_chars': col_data.dropna().astype(str).str.contains(r'[^a-zA-Z0-9\s]').any() if not col_data.dropna().empty else False,
                    'encoding_recommendation': self._recommend_encoding_method(col_data)
                })

        return analysis

    def _analyze_missing_data(self) -> Dict[str, Any]:
        """Comprehensive missing data analysis"""
        missing_data = self.df.isnull()

        analysis = {
            'total_missing': int(missing_data.sum().sum()),
            'percentage_missing': round((missing_data.sum().sum() / (len(self.df) * len(self.df.columns))) * 100, 2),
            'columns_with_missing': {},
            'missing_data_patterns': {},
            'imputation_recommendations': {}
        }

        # Per-column missing data analysis
        for col in self.df.columns:
            missing_count = missing_data[col].sum()
            if missing_count > 0:
                analysis['columns_with_missing'][col] = {
                    'count': int(missing_count),
                    'percentage': round((missing_count / len(self.df)) * 100, 2),
                    'pattern': self._analyze_missing_pattern(self.df[col]),
                    'recommended_strategy': self._recommend_imputation_strategy(col)
                }

        # Missing data patterns (combinations)
        if analysis['total_missing'] > 0:
            missing_combinations = missing_data.groupby(list(missing_data.columns)).size()
            analysis['missing_data_patterns'] = missing_combinations.head(10).to_dict()

        return analysis

    def _detect_data_quality_issues(self) -> List[Dict[str, Any]]:
        """Detect various data quality issues"""
        issues = []

        # Check for duplicate rows
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            issues.append({
                'type': 'duplicate_rows',
                'severity': 'medium',
                'count': int(duplicate_count),
                'description': f"Found {duplicate_count} duplicate rows",
                'recommendation': "Consider removing duplicate rows or investigating if they are legitimate"
            })

        # Check for constant columns
        for col in self.df.columns:
            if self.df[col].nunique() <= 1:
                issues.append({
                    'type': 'constant_column',
                    'severity': 'high',
                    'column': col,
                    'description': f"Column '{col}' has constant or single value",
                    'recommendation': "Remove this column as it provides no information"
                })

        # Check for high cardinality categorical columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_ratio = self.df[col].nunique() / len(self.df)
            if unique_ratio > 0.9:
                issues.append({
                    'type': 'high_cardinality',
                    'severity': 'medium',
                    'column': col,
                    'unique_ratio': round(unique_ratio, 2),
                    'description': f"Column '{col}' has very high cardinality ({self.df[col].nunique()} unique values)",
                    'recommendation': "Consider feature engineering or grouping rare categories"
                })

        # Check for potential ID columns
        for col in self.df.columns:
            if self.df[col].nunique() == len(self.df) and col != self.target_column:
                issues.append({
                    'type': 'potential_id_column',
                    'severity': 'low',
                    'column': col,
                    'description': f"Column '{col}' appears to be an identifier (all unique values)",
                    'recommendation': "Consider removing if not needed for prediction"
                })

        return issues

    def _analyze_target_variable(self) -> Dict[str, Any]:
        """Comprehensive target variable analysis"""
        if self.target_column not in self.df.columns:
            raise ValueError(f"Target column '{self.target_column}' not found in dataset")

        target = self.df[self.target_column]

        analysis = {
            'column_name': self.target_column,
            'data_type': str(target.dtype),
            'null_count': int(target.isnull().sum()),
            'null_percentage': round((target.isnull().sum() / len(target)) * 100, 2),
            'unique_values': int(target.nunique())
        }

        # Determine task type and add specific analysis
        if pd.api.types.is_numeric_dtype(target) and target.nunique() > 10:
            # Regression task
            analysis.update({
                'task_type': 'regression',
                'min_value': float(target.min()),
                'max_value': float(target.max()),
                'mean': float(target.mean()),
                'median': float(target.median()),
                'std': float(target.std()),
                'skewness': float(stats.skew(target.dropna())),
                'kurtosis': float(stats.kurtosis(target.dropna())),
                'distribution_type': self._guess_distribution_type(target),
                'outliers_count': self._count_outliers_iqr(target),
                'transformation_suggestions': self._suggest_target_transformations(target)
            })
        else:
            # Classification task
            value_counts = target.value_counts()

            analysis.update({
                'task_type': 'classification',
                'num_classes': int(target.nunique()),
                'class_distribution': value_counts.to_dict(),
                'class_percentages': (value_counts / len(target) * 100).round(2).to_dict(),
                'is_balanced': self._check_class_balance(target),
                'minority_class_percentage': round((value_counts.min() / len(target)) * 100, 2),
                'majority_class_percentage': round((value_counts.max() / len(target)) * 100, 2),
                'balance_recommendations': self._get_balance_recommendations(target)
            })

        return analysis

    def _analyze_correlations(self) -> Dict[str, Any]:
        """Analyze correlations with target variable"""
        correlations = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        if self.target_column in numeric_cols:
            # Numeric correlations
            target_corr = self.df[numeric_cols].corr()[self.target_column].drop(self.target_column)

            correlations['numeric_correlations'] = {
                'high_positive': target_corr[target_corr > 0.7].to_dict(),
                'moderate_positive': target_corr[(target_corr > 0.3) & (target_corr <= 0.7)].to_dict(),
                'weak_positive': target_corr[(target_corr > 0.1) & (target_corr <= 0.3)].to_dict(),
                'weak_negative': target_corr[(target_corr < -0.1) & (target_corr >= -0.3)].to_dict(),
                'moderate_negative': target_corr[(target_corr < -0.3) & (target_corr >= -0.7)].to_dict(),
                'high_negative': target_corr[target_corr < -0.7].to_dict()
            }

        # Categorical associations (for classification targets)
        if self.df[self.target_column].dtype == 'object' or self.df[self.target_column].nunique() < 10:
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            correlations['categorical_associations'] = {}

            for col in categorical_cols:
                if col != self.target_column:
                    # Use Cramér's V for categorical association
                    cramers_v = self._calculate_cramers_v(self.df[col], self.df[self.target_column])
                    correlations['categorical_associations'][col] = round(cramers_v, 3)

        return correlations

    def _get_feature_recommendations(self) -> List[Dict[str, Any]]:
        """Generate feature engineering recommendations"""
        recommendations = []

        # Date/time features
        for col in self.df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                recommendations.append({
                    'type': 'datetime_features',
                    'column': col,
                    'suggestion': f"Extract date/time features from '{col}' (year, month, day, weekday, hour, etc.)",
                    'priority': 'high'
                })

        # Interaction features
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            recommendations.append({
                'type': 'interaction_features',
                'suggestion': "Consider creating interaction features between numeric variables",
                'columns': list(numeric_cols[:5]),  # Limit to first 5
                'priority': 'medium'
            })

        # Text features
        text_cols = []
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].dropna().astype(str).str.len().mean() > 20:  # Likely text data
                text_cols.append(col)

        if text_cols:
            recommendations.append({
                'type': 'text_features',
                'columns': text_cols,
                'suggestion': "Extract text features like length, word count, sentiment, etc.",
                'priority': 'medium'
            })

        return recommendations

    def _suggest_preprocessing_steps(self) -> List[Dict[str, Any]]:
        """Generate preprocessing step recommendations"""
        steps = []

        # Missing data handling
        missing_cols = self.df.isnull().sum()
        missing_cols = missing_cols[missing_cols > 0]

        if len(missing_cols) > 0:
            steps.append({
                'step': 'handle_missing_data',
                'priority': 1,
                'description': f"Handle missing data in {len(missing_cols)} columns",
                'affected_columns': list(missing_cols.index),
                'strategies': ['imputation', 'removal', 'indicator_variables']
            })

        # Outlier handling
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        outlier_cols = []
        for col in numeric_cols:
            if self._has_outliers(self.df[col]):
                outlier_cols.append(col)

        if outlier_cols:
            steps.append({
                'step': 'handle_outliers',
                'priority': 2,
                'description': f"Handle outliers in {len(outlier_cols)} numeric columns",
                'affected_columns': outlier_cols,
                'strategies': ['winsorization', 'transformation', 'removal']
            })

        # Categorical encoding
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            steps.append({
                'step': 'encode_categorical',
                'priority': 3,
                'description': f"Encode {len(categorical_cols)} categorical columns",
                'affected_columns': list(categorical_cols),
                'strategies': ['label_encoding', 'one_hot_encoding', 'target_encoding']
            })

        # Feature scaling
        if len(numeric_cols) > 1:
            steps.append({
                'step': 'feature_scaling',
                'priority': 4,
                'description': "Scale numeric features for model compatibility",
                'affected_columns': list(numeric_cols),
                'strategies': ['standard_scaler', 'min_max_scaler', 'robust_scaler']
            })

        return steps

    # Helper methods
    def _count_outliers_iqr(self, series: pd.Series) -> int:
        """Count outliers using IQR method"""
        if series.empty or not pd.api.types.is_numeric_dtype(series):
            return 0

        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        return int(((series < lower_bound) | (series > upper_bound)).sum())

    def _count_outliers_zscore(self, series: pd.Series, threshold: float = 3) -> int:
        """Count outliers using Z-score method"""
        if series.empty or not pd.api.types.is_numeric_dtype(series):
            return 0

        z_scores = np.abs(stats.zscore(series.dropna()))
        return int((z_scores > threshold).sum())

    def _has_outliers(self, series: pd.Series) -> bool:
        """Check if series has outliers"""
        return self._count_outliers_iqr(series) > 0

    def _calculate_column_quality_score(self, series: pd.Series) -> float:
        """Calculate data quality score for a column (0-100)"""
        score = 100

        # Penalize for missing data
        missing_penalty = (series.isnull().sum() / len(series)) * 30
        score -= missing_penalty

        # Penalize for low variability (constant or near-constant)
        if series.nunique() <= 1:
            score -= 50
        elif series.nunique() / len(series) < 0.01:  # Very low variability
            score -= 20

        return max(0, round(score, 1))

    def _guess_distribution_type(self, series: pd.Series) -> str:
        """Guess the distribution type of numeric data"""
        if not pd.api.types.is_numeric_dtype(series) or series.empty:
            return 'unknown'

        clean_series = series.dropna()
        if len(clean_series) < 10:
            return 'insufficient_data'

        skewness = stats.skew(clean_series)

        if abs(skewness) < 0.5:
            return 'normal'
        elif skewness > 1:
            return 'right_skewed'
        elif skewness < -1:
            return 'left_skewed'
        else:
            return 'moderately_skewed'

    def _recommend_encoding_method(self, series: pd.Series) -> str:
        """Recommend encoding method for categorical data"""
        unique_count = series.nunique()
        total_count = len(series.dropna())

        if unique_count <= 2:
            return 'label_encoding'
        elif unique_count <= 10:
            return 'one_hot_encoding'
        elif unique_count / total_count < 0.1:
            return 'target_encoding'
        else:
            return 'frequency_encoding'

    def _analyze_missing_pattern(self, series: pd.Series) -> str:
        """Analyze the pattern of missing data"""
        if series.isnull().sum() == 0:
            return 'no_missing'

        # Check if missing data is at the beginning, end, or random
        null_positions = series.isnull()

        if null_positions.head(len(series)//4).all():
            return 'missing_at_start'
        elif null_positions.tail(len(series)//4).all():
            return 'missing_at_end'
        else:
            return 'random_missing'

    def _recommend_imputation_strategy(self, column: str) -> str:
        """Recommend imputation strategy based on column characteristics"""
        series = self.df[column]

        if pd.api.types.is_numeric_dtype(series):
            if self._has_outliers(series):
                return 'median_imputation'
            else:
                return 'mean_imputation'
        else:
            return 'mode_imputation'

    def _check_class_balance(self, series: pd.Series) -> bool:
        """Check if classes are balanced (within 20% of each other)"""
        value_counts = series.value_counts()
        proportions = value_counts / len(series)

        return proportions.max() - proportions.min() <= 0.2

    def _get_balance_recommendations(self, series: pd.Series) -> List[str]:
        """Get recommendations for handling class imbalance"""
        value_counts = series.value_counts()
        proportions = value_counts / len(series)

        recommendations = []

        if proportions.max() > 0.8:
            recommendations.append('severe_imbalance_detected')
            recommendations.append('consider_smote_oversampling')
            recommendations.append('use_stratified_sampling')

        elif proportions.max() > 0.6:
            recommendations.append('moderate_imbalance_detected')
            recommendations.append('consider_class_weights')
            recommendations.append('use_stratified_cv')

        return recommendations

    def _suggest_target_transformations(self, series: pd.Series) -> List[str]:
        """Suggest transformations for regression targets"""
        suggestions = []

        skewness = abs(stats.skew(series.dropna()))

        if skewness > 1:
            suggestions.append('log_transformation')
            suggestions.append('box_cox_transformation')

        if (series <= 0).any():
            suggestions.append('add_constant_before_log')

        return suggestions

    def _calculate_cramers_v(self, series1: pd.Series, series2: pd.Series) -> float:
        """Calculate Cramér's V for categorical association"""
        try:
            confusion_matrix = pd.crosstab(series1, series2)
            chi2 = stats.chi2_contingency(confusion_matrix)[0]
            n = confusion_matrix.sum().sum()
            phi2 = chi2 / n
            r, k = confusion_matrix.shape
            phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
            rcorr = r - ((r-1)**2)/(n-1)
            kcorr = k - ((k-1)**2)/(n-1)
            return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))
        except:
            return 0.0

    def generate_preprocessing_prompt(self) -> str:
        """Generate comprehensive preprocessing prompt based on analysis"""
        if not self.analysis_results:
            raise ValueError("Must run analyze_dataset first")

        analysis = self.analysis_results

        # Format the comprehensive prompt
        prompt = f"""You are an expert data scientist. Analyze this dataset and create comprehensive preprocessing code.

## Dataset Information:
- **Filename**: {analysis['basic_info']['shape']['rows']} rows × {analysis['basic_info']['shape']['columns']} columns
- **Target Column**: {self.target_column}
- **Target Type**: {analysis['target_analysis']['task_type']}
- **Memory Usage**: {analysis['basic_info']['memory_usage_mb']} MB

## Summary Statistics:
{self._format_summary_statistics()}

## Column Details:
{self._format_column_analysis()}

## Missing Data Analysis:
{self._format_missing_data()}

## Data Quality Issues:
{self._format_quality_issues()}

## Target Variable Analysis:
{self._format_target_analysis()}

## Preprocessing Recommendations:
{self._format_preprocessing_steps()}

## Your Task:
Create Python code that addresses all identified issues and prepares the data for ML training:

1. **Handle Missing Values**: {self._get_missing_strategy()}
2. **Encode Categorical Variables**: {self._get_encoding_strategy()}
3. **Handle Outliers**: {self._get_outlier_strategy()}
4. **Feature Engineering**: {self._get_feature_engineering_suggestions()}
5. **Scaling/Normalization**: {self._get_scaling_strategy()}
6. **Data Validation**: Ensure data integrity and consistency
7. **Export Clean Dataset**: Save as 'cleaned_data.csv'

## Requirements:
- Use pandas, numpy, sklearn for preprocessing
- Add detailed comments explaining each step
- Handle edge cases with proper error handling
- Optimize for {analysis['target_analysis']['task_type']} task
- Prepare data for: XGBoost, Random Forest, Naive Bayes, Decision Tree

## Expected Output Format:
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

# Load the dataset
df = pd.read_csv('uploaded_data.csv')
print(f"Original dataset shape: {{df.shape}}")

# Your comprehensive preprocessing code here...

# Final validation and export
print(f"Cleaned dataset shape: {{df_cleaned.shape}}")
df_cleaned.to_csv('cleaned_data.csv', index=False)
print("Dataset preprocessing completed successfully!")
```

Please provide complete, executable code that addresses all the analysis findings."""

        return prompt

    def _format_summary_statistics(self) -> str:
        """Format summary statistics for prompt"""
        stats = self.analysis_results['summary_statistics']

        formatted = []
        if stats['numeric_summary']:
            formatted.append("**Numeric Features:**")
            for col, metrics in list(stats['numeric_summary']['additional_metrics'].items())[:3]:
                formatted.append(f"  - {col}: skew={metrics['skewness']:.2f}, outliers={metrics['outliers_iqr']}")

        if stats['categorical_summary']:
            formatted.append("**Categorical Features:**")
            for col, info in list(stats['categorical_summary'].items())[:3]:
                formatted.append(f"  - {col}: {info['unique_values']} unique values, cardinality={info['cardinality']}")

        return "\\n".join(formatted)

    def _format_column_analysis(self) -> str:
        """Format column analysis for prompt"""
        analysis = self.analysis_results['column_analysis']

        formatted = []
        for col, info in list(analysis.items())[:5]:  # Limit to first 5 columns
            formatted.append(f"- **{col}**: {info['dtype']}, {info['null_percentage']:.1f}% missing, quality_score={info['data_quality_score']}")

        return "\\n".join(formatted)

    def _format_missing_data(self) -> str:
        """Format missing data info for prompt"""
        missing = self.analysis_results['missing_data_info']

        if missing['total_missing'] == 0:
            return "No missing data detected."

        formatted = [f"Total missing: {missing['total_missing']} values ({missing['percentage_missing']:.1f}%)"]

        for col, info in list(missing['columns_with_missing'].items())[:3]:
            formatted.append(f"  - {col}: {info['count']} missing ({info['percentage']:.1f}%)")

        return "\\n".join(formatted)

    def _format_quality_issues(self) -> str:
        """Format data quality issues for prompt"""
        issues = self.analysis_results['data_quality_issues']

        if not issues:
            return "No significant data quality issues detected."

        formatted = []
        for issue in issues[:3]:  # Limit to top 3 issues
            formatted.append(f"- {issue['type']}: {issue['description']}")

        return "\\n".join(formatted)

    def _format_target_analysis(self) -> str:
        """Format target analysis for prompt"""
        target = self.analysis_results['target_analysis']

        formatted = [f"**Target Variable**: {target['column_name']} ({target['task_type']})"]

        if target['task_type'] == 'classification':
            formatted.append(f"- Classes: {target['num_classes']}")
            formatted.append(f"- Balance: {'balanced' if target['is_balanced'] else 'imbalanced'}")
            if not target['is_balanced']:
                formatted.extend([f"  - {rec}" for rec in target['balance_recommendations'][:2]])
        else:
            formatted.append(f"- Range: {target['min_value']:.2f} to {target['max_value']:.2f}")
            formatted.append(f"- Distribution: {target['distribution_type']}")
            if target['transformation_suggestions']:
                formatted.append(f"- Suggested transforms: {', '.join(target['transformation_suggestions'][:2])}")

        return "\\n".join(formatted)

    def _format_preprocessing_steps(self) -> str:
        """Format preprocessing steps for prompt"""
        steps = self.analysis_results['preprocessing_suggestions']

        formatted = []
        for step in steps:
            formatted.append(f"{step['priority']}. **{step['step']}**: {step['description']}")

        return "\\n".join(formatted)

    def _get_missing_strategy(self) -> str:
        """Get specific missing data strategy"""
        missing = self.analysis_results['missing_data_info']

        if missing['total_missing'] == 0:
            return "No missing data to handle"

        strategies = []
        for col, info in missing['columns_with_missing'].items():
            strategies.append(f"{col} → {info['recommended_strategy']}")

        return "; ".join(strategies[:3])

    def _get_encoding_strategy(self) -> str:
        """Get specific encoding strategy"""
        analysis = self.analysis_results['column_analysis']

        strategies = []
        for col, info in analysis.items():
            if info['is_categorical']:
                strategies.append(f"{col} → {info.get('encoding_recommendation', 'one_hot_encoding')}")

        return "; ".join(strategies[:3]) if strategies else "No categorical variables to encode"

    def _get_outlier_strategy(self) -> str:
        """Get specific outlier handling strategy"""
        analysis = self.analysis_results['column_analysis']

        outlier_cols = []
        for col, info in analysis.items():
            if info['is_numeric'] and info.get('has_outliers', False):
                outlier_cols.append(col)

        if not outlier_cols:
            return "No significant outliers detected"

        return f"Apply IQR method to {len(outlier_cols)} columns: {', '.join(outlier_cols[:3])}"

    def _get_feature_engineering_suggestions(self) -> str:
        """Get feature engineering suggestions"""
        recommendations = self.analysis_results['feature_recommendations']

        if not recommendations:
            return "Basic feature set is sufficient"

        suggestions = []
        for rec in recommendations[:2]:
            suggestions.append(rec['suggestion'])

        return "; ".join(suggestions)

    def _get_scaling_strategy(self) -> str:
        """Get scaling strategy recommendation"""
        target = self.analysis_results['target_analysis']

        if target['task_type'] == 'classification':
            return "StandardScaler for tree-based models compatibility"
        else:
            return "StandardScaler for regression models"