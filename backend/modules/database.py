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
    """Drop all database tables"""
    db.drop_all()


