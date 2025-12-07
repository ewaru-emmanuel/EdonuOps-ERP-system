#!/usr/bin/env python3
"""
Fix password_reset_tokens token column to VARCHAR
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from sqlalchemy import text

def fix_password_reset_token_column():
    """Change password_reset_tokens token column from UUID to VARCHAR"""
    try:
        print("Fixing password_reset_tokens token column...")
        
        app = create_app()
        
        with app.app_context():
            # Check current column type
            result = db.session.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'password_reset_tokens' 
                AND column_name = 'token'
            """))
            
            row = result.fetchone()
            if row:
                print(f"Current token column:")
                print(f"   Column: {row[0]}")
                print(f"   Data Type: {row[1]}")
                print(f"   Max Length: {row[2]}")
                
                # Check if it's UUID type
                if 'uuid' in row[1].lower():
                    print("Token column is UUID type - changing to VARCHAR(255)...")
                    
                    # Drop the default constraint first if it exists
                    try:
                        db.session.execute(text("""
                            ALTER TABLE password_reset_tokens 
                            ALTER COLUMN token DROP DEFAULT
                        """))
                        db.session.commit()
                        print("Dropped default constraint")
                    except Exception as e:
                        print(f"No default constraint to drop: {e}")
                        db.session.rollback()
                    
                    # Change token column from UUID to VARCHAR(255)
                    db.session.execute(text("""
                        ALTER TABLE password_reset_tokens 
                        ALTER COLUMN token TYPE VARCHAR(255) USING token::text
                    """))
                    
                    db.session.commit()
                    print("Token column changed to VARCHAR(255)")
                    
                    # Verify the change
                    result = db.session.execute(text("""
                        SELECT column_name, data_type, character_maximum_length 
                        FROM information_schema.columns 
                        WHERE table_name = 'password_reset_tokens' 
                        AND column_name = 'token'
                    """))
                    
                    row = result.fetchone()
                    if row:
                        print(f"Verification:")
                        print(f"   Column: {row[0]}")
                        print(f"   Data Type: {row[1]}")
                        print(f"   Max Length: {row[2]}")
                    
                    return True
                else:
                    print("Token column is already VARCHAR type - no changes needed")
                    return True
            else:
                print("Token column not found in password_reset_tokens table")
                return False
                
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = fix_password_reset_token_column()
    if success:
        print("\nPassword reset token column fix completed successfully!")
    else:
        print("\nPassword reset token column fix failed!")
        sys.exit(1)

