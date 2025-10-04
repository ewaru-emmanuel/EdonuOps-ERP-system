#!/usr/bin/env python3
"""
Main application entry point for EdonuOps
This file simply runs the Flask application created by the app factory
"""

from app import create_app, db

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist (safe operation)
    with app.app_context():
        try:
            # Check if database already has data
            from modules.core.models import User
            has_users = User.query.first() is not None
            
            if has_users:
                print("✅ Database already contains data - tables are up to date")
            else:
                print("🔧 Creating database tables for new installation...")
                db.create_all()
                print("✅ Database tables created successfully")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not create database tables: {e}")
    
    # Run the Flask application
    print("\n🚀 Starting EdonuOps backend server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("🧪 Test endpoint: http://localhost:5000/test")
    print("\n💡 Database Safety:")
    print("   - Only 'db.create_all()' is used (safe, non-destructive)")
    print("   - No 'db.drop_all()' operations in startup")
    print("   - Use 'python database_safety.py backup' to create backups")
    
    app.run(
        debug=True,
        host='localhost',
        port=5000,
        threaded=True
    )
