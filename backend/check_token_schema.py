#!/usr/bin/env python3
"""
Check email_verification_tokens table schema
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from sqlalchemy import text

def check_token_schema():
    """Check the token column data type"""
    try:
        print("🔍 Checking email_verification_tokens table schema...")
        
        app = create_app()
        
        with app.app_context():
            # Check token column data type
            result = db.session.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'email_verification_tokens' 
                AND column_name = 'token'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Token column found:")
                print(f"   Column: {row[0]}")
                print(f"   Data Type: {row[1]}")
                print(f"   Max Length: {row[2]}")
                
                # Check if it's UUID type
                if 'uuid' in row[1].lower():
                    print("❌ Token column is UUID type - need to change to VARCHAR")
                    return 'uuid'
                else:
                    print("✅ Token column is not UUID type")
                    return 'varchar'
            else:
                print("❌ Token column not found")
                return None
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    schema_type = check_token_schema()
    if schema_type == 'uuid':
        print("\n🔧 Solution: Change token column to VARCHAR or generate UUID tokens")
    elif schema_type == 'varchar':
        print("\n✅ Schema is correct - issue might be elsewhere")
    else:
        print("\n❌ Could not determine schema")












































