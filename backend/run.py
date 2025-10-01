#!/usr/bin/env python3
"""
Main application entry point for EdonuOps
This file simply runs the Flask application created by the app factory
"""

from app import create_app, db

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Warning: Could not create database tables: {e}")
    
    # Run the Flask application
    print("Starting EdonuOps backend server...")
    print("Server will be available at: http://localhost:5000")
    print("Health check: http://localhost:5000/health")
    print("Test endpoint: http://localhost:5000/test")
    
    app.run(
        debug=True,
        host='localhost',
        port=5000,
        threaded=True
    )
