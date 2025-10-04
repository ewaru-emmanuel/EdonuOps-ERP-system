# backend/modules/database.py

from app import db

# Simple database utilities
def get_db():
    """Get database instance"""
    return db

def init_db():
    """Initialize database tables"""
    db.create_all()

def drop_db():
    """Drop all database tables - DANGER: This will delete ALL data!"""
    import os
    import sys
    
    # Safety check - only allow in development
    if os.getenv('FLASK_ENV') == 'production':
        raise RuntimeError("Cannot drop database in production environment!")
    
    # Additional safety check
    response = input("⚠️  WARNING: This will delete ALL data! Type 'DELETE_ALL_DATA' to confirm: ")
    if response != 'DELETE_ALL_DATA':
        print("Operation cancelled.")
        return False
    
    print("🗑️  Dropping all database tables...")
    db.drop_all()
    print("✅ All tables dropped.")
    return True


