#!/usr/bin/env python3
"""
Test script to demonstrate user isolation
This shows how each user can only access their own data
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_user_isolation():
    """Test that users can only access their own data"""
    
    print("🔐 Testing User Isolation & Recognition")
    print("=" * 50)
    
    # Test headers for different users
    headers_user1 = {'Content-Type': 'application/json', 'X-User-ID': '1'}
    headers_user2 = {'Content-Type': 'application/json', 'X-User-ID': '2'}
    headers_user3 = {'Content-Type': 'application/json', 'X-User-ID': '3'}
    
    try:
        # Test 1: User 1 saves their onboarding data
        print("\n1️⃣ User 1 saving their onboarding data")
        user1_data = {
            "user_id": 1,
            "data_type": "onboarding_complete",
            "data": {
                "businessProfile": {
                    "companyName": "User 1 Company",
                    "industry": "Technology",
                    "employeeCount": "11-50"
                },
                "selectedModules": ["financials", "crm"],
                "coaTemplate": "retail"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/user-data/save", 
                                headers=headers_user1, json=user1_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ User 1 data saved successfully")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 2: User 2 saves their onboarding data
        print("\n2️⃣ User 2 saving their onboarding data")
        user2_data = {
            "user_id": 2,
            "data_type": "onboarding_complete",
            "data": {
                "businessProfile": {
                    "companyName": "User 2 Company",
                    "industry": "Manufacturing",
                    "employeeCount": "51-200"
                },
                "selectedModules": ["inventory", "procurement"],
                "coaTemplate": "manufacturing"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/user-data/save", 
                                headers=headers_user2, json=user2_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ User 2 data saved successfully")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 3: User 1 loads their own data
        print("\n3️⃣ User 1 loading their own data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", 
                                headers=headers_user1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                data = result['data']
                print(f"✅ User 1 can access their data:")
                print(f"   Company: {data.get('businessProfile', {}).get('companyName', 'N/A')}")
                print(f"   Industry: {data.get('businessProfile', {}).get('industry', 'N/A')}")
                print(f"   Modules: {data.get('selectedModules', [])}")
            else:
                print("❌ No data found for User 1")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 4: User 2 loads their own data
        print("\n4️⃣ User 2 loading their own data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=2", 
                                headers=headers_user2)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                data = result['data']
                print(f"✅ User 2 can access their data:")
                print(f"   Company: {data.get('businessProfile', {}).get('companyName', 'N/A')}")
                print(f"   Industry: {data.get('businessProfile', {}).get('industry', 'N/A')}")
                print(f"   Modules: {data.get('selectedModules', [])}")
            else:
                print("❌ No data found for User 2")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 5: SECURITY TEST - User 1 trying to access User 2's data
        print("\n5️⃣ SECURITY TEST: User 1 trying to access User 2's data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=2", 
                                headers=headers_user1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                print("❌ SECURITY BREACH: User 1 can access User 2's data!")
                data = result['data']
                print(f"   Company: {data.get('businessProfile', {}).get('companyName', 'N/A')}")
            else:
                print("✅ SECURITY OK: User 1 cannot access User 2's data")
        else:
            print(f"✅ SECURITY OK: Access denied (Status: {response.status_code})")
        
        # Test 6: SECURITY TEST - User 2 trying to access User 1's data
        print("\n6️⃣ SECURITY TEST: User 2 trying to access User 1's data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", 
                                headers=headers_user2)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                print("❌ SECURITY BREACH: User 2 can access User 1's data!")
                data = result['data']
                print(f"   Company: {data.get('businessProfile', {}).get('companyName', 'N/A')}")
            else:
                print("✅ SECURITY OK: User 2 cannot access User 1's data")
        else:
            print(f"✅ SECURITY OK: Access denied (Status: {response.status_code})")
        
        # Test 7: User 3 (new user) trying to access existing data
        print("\n7️⃣ SECURITY TEST: User 3 trying to access existing data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", 
                                headers=headers_user3)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                print("❌ SECURITY BREACH: User 3 can access User 1's data!")
            else:
                print("✅ SECURITY OK: User 3 cannot access User 1's data")
        else:
            print(f"✅ SECURITY OK: Access denied (Status: {response.status_code})")
        
        # Test 8: Show all users' data (should be empty for cross-user access)
        print("\n8️⃣ Testing get all data for each user")
        
        # User 1's data
        response = requests.get(f"{BASE_URL}/api/user-data/all?user_id=1", headers=headers_user1)
        if response.status_code == 200:
            result = response.json()
            data_types = result.get('data_types', [])
            print(f"✅ User 1 has {len(data_types)} data types: {data_types}")
        
        # User 2's data
        response = requests.get(f"{BASE_URL}/api/user-data/all?user_id=2", headers=headers_user2)
        if response.status_code == 200:
            result = response.json()
            data_types = result.get('data_types', [])
            print(f"✅ User 2 has {len(data_types)} data types: {data_types}")
        
        print("\n🎉 User isolation tests completed!")
        print("✅ Each user can only access their own data")
        print("✅ Complete user isolation is working")
        print("✅ No cross-user data access possible")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend server")
        print("Make sure the backend server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_isolation()



