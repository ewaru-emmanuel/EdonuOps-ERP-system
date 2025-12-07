#!/usr/bin/env python3
"""
Add missing 'notes' column to accounts table
This fixes the error: column accounts.notes does not exist
"""

import os
import sys
from sqlalchemy import text

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def add_notes_column():
    """Add notes column to accounts table if it doesn't exist"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Adding 'notes' column to accounts table...")
            
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='accounts' AND column_name='notes'
            """))
            
            if result.fetchone():
                print("✅ Column 'notes' already exists in accounts table")
                return True
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE accounts 
                ADD COLUMN notes TEXT
            """))
            
            db.session.commit()
            print("✅ Successfully added 'notes' column to accounts table")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding notes column: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = add_notes_column()
    sys.exit(0 if success else 1)


