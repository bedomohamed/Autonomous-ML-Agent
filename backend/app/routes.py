from flask import Blueprint, request, jsonify, current_app
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app.services.s3_service import S3Service
from app.services.preprocessing_service import PreprocessingService
from app.utils.validators import validate_csv_file

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

@api_bp.route('/upload', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV files are allowed'}), 400

        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        try:
            df = pd.read_csv(temp_path)
            validation_result = validate_csv_file(df)

            if not validation_result['valid']:
                os.remove(temp_path)
                return jsonify({'error': validation_result['message']}), 400

            s3_service = S3Service()
            s3_key = s3_service.upload_file(temp_path, filename)

            preview_data = {
                'columns': df.columns.tolist(),
                'preview': df.head(50).to_dict('records'),
                'shape': {'rows': len(df), 'columns': len(df.columns)},
                's3_key': s3_key,
                'filename': filename
            }

            os.remove(temp_path)

            return jsonify({
                'success': True,
                'data': preview_data,
                'message': 'File uploaded successfully'
            }), 200

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': f'Error processing CSV: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@api_bp.route('/preprocess', methods=['POST'])
def preprocess_data():
    try:
        data = request.json

        if not data or 's3_key' not in data or 'target_column' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400

        s3_key = data['s3_key']
        target_column = data['target_column']

        s3_service = S3Service()
        csv_path = s3_service.download_file(s3_key)

        df = pd.read_csv(csv_path)

        if target_column not in df.columns:
            return jsonify({'error': f'Target column {target_column} not found in CSV'}), 400

        preprocessing_service = PreprocessingService()
        result = preprocessing_service.preprocess(df, target_column)

        processed_filename = f"processed_{s3_key}"
        result['cleaned_data'].to_csv(f"/tmp/{processed_filename}", index=False)
        processed_s3_key = s3_service.upload_file(f"/tmp/{processed_filename}", processed_filename)

        os.remove(csv_path)
        os.remove(f"/tmp/{processed_filename}")

        return jsonify({
            'success': True,
            'data': {
                'processed_s3_key': processed_s3_key,
                'statistics': result['statistics'],
                'preprocessing_steps': result['steps_applied'],
                'shape': {
                    'rows': len(result['cleaned_data']),
                    'columns': len(result['cleaned_data'].columns)
                }
            },
            'message': 'Data preprocessed successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Preprocessing failed: {str(e)}'}), 500

@api_bp.route('/download/<s3_key>', methods=['GET'])
def download_file(s3_key):
    try:
        s3_service = S3Service()
        presigned_url = s3_service.generate_presigned_url(s3_key)

        return jsonify({
            'success': True,
            'download_url': presigned_url
        }), 200

    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500