from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"Bad request: {error}")
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"Not found: {error}")
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        logger.error(f"File too large: {error}")
        return jsonify({'error': 'File too large. Maximum size is 50MB'}), 413

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}")
        return jsonify({'error': 'An unexpected error occurred'}), 500