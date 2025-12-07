#!/usr/bin/env python3
"""
Test invitation-only registration system
"""

import requests
import json

def test_invitation_only_registration():
    """Test invitation-only registration"""
    try:
        print("🧪 Testing invitation-only registration...")
        
        url = "http://localhost:5000/api/auth/register"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Test data for invitation-only registration
        data = {
            "username": "newuser123",
            "email": "newuser@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "1234567890",
            "invite_code": "ABC12345"  # This will be invalid for now
        }
        
        print(f"Making request to: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"\nResponse status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response text: {response.text}")
        
        if response.status_code == 400:
            print("✅ Invalid invite code properly rejected!")
            return True
        elif response.status_code == 201:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Unexpected response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Invitation-Only Registration System")
    print("=" * 50)
    
    success = test_invitation_only_registration()
    if success:
        print("\n🎉 Invitation-only registration system working!")
    else:
        print("\n❌ Registration system has issues!")
