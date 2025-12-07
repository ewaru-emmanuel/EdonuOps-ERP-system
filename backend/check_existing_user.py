#!/usr/bin/env python3
"""
Check if user already exists in database
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from modules.core.models import User

def check_existing_user():
    """Check if the user already exists"""
    try:
        print("🔍 Checking for existing user...")
        
        app = create_app()
        
        with app.app_context():
            # Check for username
            username = "emmanuel"
            email = "ewaruemmanuel01@gmail.com"
            
            existing_username = User.query.filter_by(username=username).first()
            existing_email = User.query.filter_by(email=email).first()
            
            if existing_username:
                print(f"❌ Username '{username}' already exists (ID: {existing_username.id})")
                print(f"   Email: {existing_username.email}")
                print(f"   Created: {existing_username.created_at}")
                print(f"   Email verified: {existing_username.email_verified}")
                print(f"   Is active: {existing_username.is_active}")
            else:
                print(f"✅ Username '{username}' is available")
            
            if existing_email:
                print(f"❌ Email '{email}' already exists (ID: {existing_email.id})")
                print(f"   Username: {existing_email.username}")
                print(f"   Created: {existing_email.created_at}")
                print(f"   Email verified: {existing_email.email_verified}")
                print(f"   Is active: {existing_email.is_active}")
            else:
                print(f"✅ Email '{email}' is available")
            
            return existing_username or existing_email
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    existing_user = check_existing_user()
    if existing_user:
        print(f"\n🔧 Solution: Delete existing user or use different credentials")
    else:
        print(f"\n✅ No existing user found - registration should work")










































