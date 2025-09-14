"""
Code validation utilities for preprocessing code
"""
import re
import logging
import ast
import sys
from io import StringIO
import tempfile
import os

logger = logging.getLogger(__name__)

class CodeValidator:
    """Validate and fix common issues in generated preprocessing code"""

    @staticmethod
    def validate_sklearn_syntax(code: str) -> dict:
        """Validate and fix common scikit-learn syntax issues"""
        issues = []
        fixes = []
        fixed_code = code

        # Check for deprecated sparse parameter in OneHotEncoder
        sparse_pattern = r'OneHotEncoder\([^)]*sparse=False[^)]*\)'
        if re.search(sparse_pattern, code):
            issues.append("Deprecated 'sparse=False' parameter in OneHotEncoder")
            fixed_code = re.sub(
                r'sparse=False',
                'sparse_output=False',
                fixed_code
            )
            fixes.append("Replaced 'sparse=False' with 'sparse_output=False'")

        # Check for common import issues
        required_imports = [
            'import pandas as pd',
            'import numpy as np'
        ]

        for imp in required_imports:
            if imp not in code:
                issues.append(f"Missing required import: {imp}")

        # Check for cleaned_df assignment
        if 'cleaned_df' not in code and 'cleaned_data' not in code:
            issues.append("No 'cleaned_df' or 'cleaned_data' variable found")

        # Check for proper CSV saving
        if 'to_csv(' not in code:
            issues.append("No CSV saving operation found")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'fixes': fixes,
            'fixed_code': fixed_code
        }

    @staticmethod
    def add_error_handling(code: str) -> str:
        """Add basic error handling wrapper to code"""
        wrapped_code = f"""
try:
    # Original preprocessing code
{CodeValidator._indent_code(code, '    ')}
except Exception as e:
    print(f"❌ Error during preprocessing: {{str(e)}}")
    import traceback
    traceback.print_exc()
    raise e
"""
        return wrapped_code

    @staticmethod
    def _indent_code(code: str, indent: str) -> str:
        """Add indentation to each line of code"""
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)

    @staticmethod
    def ensure_cleaned_df_variable(code: str) -> str:
        """Ensure the code creates a 'cleaned_df' variable"""
        if 'cleaned_df' in code:
            return code

        # Look for other common variable names and alias them
        variable_mappings = [
            ('processed_data', 'cleaned_df = processed_data'),
            ('cleaned_data', 'cleaned_df = cleaned_data'),
            ('final_data', 'cleaned_df = final_data'),
            ('X_processed', 'cleaned_df = X_processed'),
            ('df_processed', 'cleaned_df = df_processed')
        ]

        modified_code = code
        for old_var, new_assignment in variable_mappings:
            if old_var in code and 'cleaned_df' not in code:
                modified_code += f'\n\n# Ensure cleaned_df is available for saving\n{new_assignment}'
                break

        return modified_code

    @staticmethod
    def validate_python_syntax(code: str) -> dict:
        """Validate Python syntax and fix common issues"""
        issues = []
        fixes = []
        fixed_code = code

        try:
            # Try to parse the code with AST
            ast.parse(code)
            return {
                'valid': True,
                'issues': issues,
                'fixes': fixes,
                'fixed_code': fixed_code
            }
        except SyntaxError as e:
            issues.append(f"Syntax Error at line {e.lineno}: {e.msg}")

            # Try to fix common syntax issues
            lines = code.split('\n')

            # Fix incomplete try/except blocks
            if 'expected \'except\' or \'finally\' block' in str(e):
                fixed_lines = []
                in_try_block = False
                indent_level = 0

                for i, line in enumerate(lines):
                    stripped = line.strip()

                    if stripped.startswith('try:'):
                        in_try_block = True
                        indent_level = len(line) - len(line.lstrip())
                        fixed_lines.append(line)
                        continue

                    if in_try_block and stripped and not line.startswith(' ' * (indent_level + 4)) and not stripped.startswith(('except', 'finally')):
                        # Add except block before this line
                        except_line = ' ' * indent_level + 'except Exception as e:'
                        pass_line = ' ' * (indent_level + 4) + 'print(f"Error: {e}")'
                        fixed_lines.extend([except_line, pass_line, ''])
                        in_try_block = False

                    fixed_lines.append(line)

                # If we ended while still in a try block
                if in_try_block:
                    except_line = ' ' * indent_level + 'except Exception as e:'
                    pass_line = ' ' * (indent_level + 4) + 'print(f"Error: {e}")'
                    fixed_lines.extend(['', except_line, pass_line])

                fixed_code = '\n'.join(fixed_lines)
                fixes.append("Added missing except block to incomplete try statement")

                # Try to parse the fixed code
                try:
                    ast.parse(fixed_code)
                    issues = []  # Clear syntax error if fixed
                except SyntaxError:
                    # If still broken, keep the original
                    fixed_code = code

            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'fixes': fixes,
                'fixed_code': fixed_code
            }
        except Exception as e:
            issues.append(f"Code validation error: {str(e)}")
            return {
                'valid': False,
                'issues': issues,
                'fixes': fixes,
                'fixed_code': fixed_code
            }

    @staticmethod
    def validate_and_fix_code(code: str) -> dict:
        """Main validation function that applies all fixes"""
        try:
            # Step 1: Validate Python syntax first
            syntax_result = CodeValidator.validate_python_syntax(code)
            fixed_code = syntax_result['fixed_code']
            all_issues = syntax_result['issues'][:]
            all_fixes = syntax_result['fixes'][:]

            # Step 2: Fix sklearn syntax issues only if syntax is valid
            if syntax_result['valid']:
                sklearn_result = CodeValidator.validate_sklearn_syntax(fixed_code)
                fixed_code = sklearn_result['fixed_code']
                all_issues.extend(sklearn_result['issues'])
                all_fixes.extend(sklearn_result['fixes'])

                # Step 3: Ensure cleaned_df variable exists
                fixed_code = CodeValidator.ensure_cleaned_df_variable(fixed_code)

            return {
                'valid': len(all_issues) == 0,
                'issues': all_issues,
                'fixes_applied': all_fixes,
                'original_code': code,
                'fixed_code': fixed_code,
                'code_length': len(fixed_code),
                'validation_passed': True
            }

        except Exception as e:
            logger.error(f"Code validation failed: {e}")
            return {
                'valid': False,
                'issues': [f"Code validation failed: {str(e)}"],
                'fixes_applied': [],
                'original_code': code,
                'fixed_code': code,
                'validation_passed': False
            }