#!/usr/bin/env python3
"""
Fix email_verification_tokens token column to VARCHAR
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from sqlalchemy import text

def fix_token_column():
    """Change token column from UUID to VARCHAR"""
    try:
        print("🔧 Fixing email_verification_tokens token column...")
        
        app = create_app()
        
        with app.app_context():
            # Change token column from UUID to VARCHAR(255)
            db.session.execute(text("""
                ALTER TABLE email_verification_tokens 
                ALTER COLUMN token TYPE VARCHAR(255)
            """))
            
            db.session.commit()
            print("✅ Token column changed to VARCHAR(255)")
            
            # Verify the change
            result = db.session.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'email_verification_tokens' 
                AND column_name = 'token'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Verification:")
                print(f"   Column: {row[0]}")
                print(f"   Data Type: {row[1]}")
                print(f"   Max Length: {row[2]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = fix_token_column()
    if success:
        print("\n🎉 Token column fixed successfully!")
        print("📧 Email verification should now work!")
    else:
        print("\n❌ Failed to fix token column!")











































