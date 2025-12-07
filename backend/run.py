#!/usr/bin/env python3
"""
Main application entry point for EdonuOps
Production-ready Flask application runner
"""

from app import create_app, db
import os

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist (safe operation)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # Log error but don't crash the application
            pass
    
    # Get configuration from environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    # Run the Flask application
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        threaded=True
    )