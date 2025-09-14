from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app(config=None):
    app = Flask(__name__)

    if config:
        app.config.update(config)
    else:
        app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
        app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
        app.config['AWS_BUCKET_NAME'] = os.getenv('AWS_BUCKET_NAME', 'csv-preprocessing-bucket')
        app.config['AWS_REGION'] = os.getenv('AWS_REGION', 'us-east-1')

    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app