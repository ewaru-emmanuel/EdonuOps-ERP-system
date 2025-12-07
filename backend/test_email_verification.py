#!/usr/bin/env python3
"""
Test the complete email verification flow
"""

import requests
import json

def test_registration_with_verification():
    """Test registration with email verification"""
    try:
        print("🧪 Testing registration with email verification...")
        
        url = "http://localhost:5000/api/auth/register"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Test data
        data = {
            "username": "testuser789",
            "email": "testuser789@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890"
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
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            print("📧 Verification email should be sent to:", data["email"])
            return True
        else:
            print("❌ Registration failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login_without_verification():
    """Test login before email verification"""
    try:
        print("\n🧪 Testing login before email verification...")
        
        url = "http://localhost:5000/api/auth/login"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {
            "email": "testuser789@example.com",
            "password": "TestPassword123!"
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Response status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response text: {response.text}")
        
        if response.status_code == 401 and "email_verification_required" in str(response_data):
            print("✅ Login properly blocked - email verification required!")
            return True
        else:
            print("❌ Login should be blocked before verification")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Email Verification Flow")
    print("=" * 50)
    
    # Test registration
    reg_success = test_registration_with_verification()
    
    if reg_success:
        # Test login before verification
        login_test = test_login_without_verification()
        
        if login_test:
            print("\n🎉 Email verification flow working correctly!")
            print("\n📋 Next steps:")
            print("1. Check email for verification link")
            print("2. Click link to verify email")
            print("3. User should be auto-logged in")
        else:
            print("\n❌ Login verification check failed!")
    else:
        print("\n❌ Registration failed - cannot test verification flow")

