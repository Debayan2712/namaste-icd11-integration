"""
NAMASTE-ICD11 Integration API
Main Flask application entry point
"""

import os
import logging
from flask import Flask, render_template
from flask_jwt_extended import JWTManager

from config import config
from app.api.endpoints import create_api

def create_app(config_name=None):
    """Create Flask application factory"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format=app.config['LOG_FORMAT']
    )
    
    # Initialize extensions
    jwt = JWTManager(app)
    
    # Create API endpoints
    api = create_api(app)
    
    # Add web interface route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Add custom error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'resourceType': 'OperationOutcome',
            'issue': [
                {
                    'severity': 'error',
                    'code': 'not-found',
                    'details': {
                        'text': 'Resource not found'
                    }
                }
            ]
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'resourceType': 'OperationOutcome',
            'issue': [
                {
                    'severity': 'error',
                    'code': 'exception',
                    'details': {
                        'text': 'Internal server error'
                    }
                }
            ]
        }, 500
    
    return app

def main():
    """Main entry point for development server"""
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
