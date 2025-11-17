"""
Flask API application for SoundWound card game platform.

This module provides the RESTful API endpoints for the Flutter
frontend to communicate with the Python game engine and database.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import logging
import traceback
from pathlib import Path

from ..database.database import get_database_manager
from .routes.auth import auth_bp
from .routes.games import games_bp
from .routes.users import users_bp
from .routes.statistics import statistics_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name: str = 'development') -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration environment name

    Returns:
        Configured Flask application
    """
    # Get the project root directory (two levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    static_folder = project_root / 'static'

    app = Flask(__name__, static_folder=str(static_folder))

    # Load configuration
    app.config.update({
        'SECRET_KEY': 'soundwound-dev-key-change-in-production',
        'DEBUG': config_name == 'development',
        'TESTING': config_name == 'testing',
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': True
    })

    # Enable CORS for Flutter web development
    CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*'])

    # Initialize database
    try:
        db_manager = get_database_manager()
        if not db_manager.health_check():
            logger.error("Database health check failed during startup")
        else:
            logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(games_bp, url_prefix='/api/games')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors."""
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid or malformed',
            'status_code': 400
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server errors."""
        logger.error(f"Internal server error: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500

    # Root endpoint - serve web interface
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint that serves the web interface."""
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except Exception as e:
            logger.error(f"Failed to serve index.html: {e}")
            # Fallback to JSON API info
            return jsonify({
                'message': 'Welcome to SoundWound Card Game Platform API',
                'version': '1.0.0',
                'status': 'online',
                'timestamp': datetime.utcnow().isoformat(),
                'endpoints': {
                    'info': '/api/info',
                    'health': '/api/health',
                    'auth': '/api/auth',
                    'games': '/api/games',
                    'users': '/api/users',
                    'statistics': '/api/statistics'
                },
                'documentation': 'Visit /api/info for detailed API information'
            })

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        try:
            db_manager = get_database_manager()
            db_healthy = db_manager.health_check()
            db_stats = db_manager.get_stats()

            return jsonify({
                'status': 'healthy' if db_healthy else 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': {
                    'healthy': db_healthy,
                    'stats': db_stats
                },
                'version': '1.0.0'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    # API info endpoint
    @app.route('/api/info', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'name': 'SoundWound API',
            'version': '1.0.0',
            'description': 'RESTful API for SoundWound card game platform',
            'endpoints': {
                'auth': '/api/auth',
                'games': '/api/games',
                'users': '/api/users',
                'statistics': '/api/statistics',
                'health': '/api/health'
            },
            'supported_games': ['fool', '101', 'blackjack', 'uno'],
            'documentation': 'https://github.com/soundwound/api-docs'
        })

    # Request logging middleware
    @app.before_request
    def log_request_info():
        """Log incoming requests for debugging."""
        if app.config['DEBUG']:
            logger.debug(f"Request: {request.method} {request.url}")
            logger.debug(f"Content-Type: {request.content_type}")
            logger.debug(f"Has data: {bool(request.data)}")
            if request.is_json:
                logger.debug(f"Request body: {request.json}")

    @app.after_request
    def log_response_info(response):
        """Log outgoing responses for debugging."""
        if app.config['DEBUG']:
            logger.debug(f"Response: {response.status_code}")
        return response

    # Add custom JSON encoder for datetime objects
    from json import JSONEncoder

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)

    app.json_encoder = CustomJSONEncoder

    logger.info(f"SoundWound API application created (config: {config_name})")
    return app


# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)