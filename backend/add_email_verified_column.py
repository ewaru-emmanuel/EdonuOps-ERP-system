#!/usr/bin/env python3
"""
Add email_verified column to users table
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from sqlalchemy import text

def add_email_verified_column():
    """Add email_verified column to users table"""
    try:
        print("🔧 Adding email_verified column to users table...")
        
        app = create_app()
        
        with app.app_context():
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'email_verified'
            """))
            
            if result.fetchone():
                print("✅ email_verified column already exists")
                return True
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN email_verified BOOLEAN DEFAULT FALSE
            """))
            
            db.session.commit()
            print("✅ email_verified column added successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error adding email_verified column: {e}")
        return False

if __name__ == "__main__":
    success = add_email_verified_column()
    if success:
        print("\n🎉 Database migration completed!")
    else:
        print("\n❌ Database migration failed!")

