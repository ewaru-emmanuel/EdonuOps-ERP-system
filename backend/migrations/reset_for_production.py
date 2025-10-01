#!/usr/bin/env python3
"""
Reset database for production deployment.
This script drops all tables and recreates them with proper structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.database import db
from app import create_app

def reset_database():
    """Drop all tables and recreate the database structure."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting database reset...")
            
            # Drop all tables
            print("🗑️  Dropping all tables...")
            db.drop_all()
            
            # Create all tables
            print("🏗️  Creating database structure...")
            db.create_all()
            
            # Commit the changes
            db.session.commit()
            
            print("✅ Database reset completed successfully!")
            print("🎯 Database is now ready for production deployment!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during database reset: {e}")
            raise

if __name__ == "__main__":
    reset_database()







