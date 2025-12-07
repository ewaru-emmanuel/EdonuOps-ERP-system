#!/usr/bin/env python3
"""
Test the new invitation-only registration directly
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from modules.core.models import User, Role
from modules.core.tenant_models import Tenant

def test_invitation_only_directly():
    """Test invitation-only registration by calling the function directly"""
    try:
        print("🧪 Testing invitation-only registration function directly...")
        
        app = create_app()
        
        with app.app_context():
            # Test data
            data = {
                "username": "newuser123",
                "email": "newuser@example.com",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!",
                "first_name": "New",
                "last_name": "User",
                "phone_number": "1234567890",
                "invite_code": "ABC12345"  # Invalid invite code
            }
            
            # Import the register function
            from modules.core.auth import register
            
            # Create a test request context
            with app.test_request_context(
                '/api/auth/register',
                method='POST',
                data=json.dumps(data),
                content_type='application/json'
            ):
                import json
                
                # Call the register function
                response = register()
                
                print(f"Response status code: {response[1]}")
                print(f"Response data: {response[0].get_json()}")
                
                if response[1] == 400:
                    print("✅ Invalid invite code properly rejected!")
                    return True
                else:
                    print("❌ Unexpected response")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_invitation_only_directly()
    if success:
        print("\n🎉 Invitation-only registration function works!")
    else:
        print("\n❌ Registration function has issues!")

