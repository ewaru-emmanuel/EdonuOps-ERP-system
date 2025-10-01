#!/usr/bin/env python3
"""
Test script for onboarding data persistence
This script tests that all onboarding data is saved to database with user isolation
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_onboarding_data_persistence():
    """Test onboarding data persistence with user isolation"""
    
    print("🧪 Testing Onboarding Data Persistence")
    print("=" * 50)
    
    # Test headers for user 1
    headers_user1 = {
        'Content-Type': 'application/json',
        'X-User-ID': '1'
    }
    
    # Test headers for user 2
    headers_user2 = {
        'Content-Type': 'application/json',
        'X-User-ID': '2'
    }
    
    try:
        # Test 1: Save onboarding data for user 1
        print("\n1️⃣ Testing onboarding data save for user 1")
        
        onboarding_data_user1 = {
            "user_id": 1,
            "data_type": "onboarding_complete",
            "data": {
                "businessProfile": {
                    "companyName": "Test Company 1",
                    "industry": "Technology",
                    "employeeCount": "11-50",
                    "annualRevenue": "$1M - $5M",
                    "challenges": ["Manual processes taking too much time", "Cash flow management"]
                },
                "selectedModules": ["financials", "crm", "inventory"],
                "coaTemplate": "retail",
                "organizationSetup": {
                    "organizationType": "single_owner",
                    "departments": ["Management", "Finance"],
                    "userPermissions": {
                        "defaultUserRole": "admin",
                        "restrictionLevel": "flexible",
                        "allowRoleOverride": True
                    }
                },
                "onboardingMetadata": {
                    "activatedAt": "2024-01-01T00:00:00Z",
                    "version": "1.0"
                }
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/user-data/save", 
                                headers=headers_user1, 
                                json=onboarding_data_user1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Onboarding data saved for user 1: {result.get('message', 'Success')}")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 2: Save onboarding data for user 2
        print("\n2️⃣ Testing onboarding data save for user 2")
        
        onboarding_data_user2 = {
            "user_id": 2,
            "data_type": "onboarding_complete",
            "data": {
                "businessProfile": {
                    "companyName": "Test Company 2",
                    "industry": "Manufacturing",
                    "employeeCount": "51-200",
                    "annualRevenue": "$5M - $10M",
                    "challenges": ["Difficulty tracking inventory", "Scaling operations"]
                },
                "selectedModules": ["financials", "inventory", "procurement"],
                "coaTemplate": "manufacturing",
                "organizationSetup": {
                    "organizationType": "corporation",
                    "departments": ["Management", "Finance", "Operations"],
                    "userPermissions": {
                        "defaultUserRole": "manager",
                        "restrictionLevel": "strict",
                        "allowRoleOverride": False
                    }
                },
                "onboardingMetadata": {
                    "activatedAt": "2024-01-02T00:00:00Z",
                    "version": "1.0"
                }
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/user-data/save", 
                                headers=headers_user2, 
                                json=onboarding_data_user2)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Onboarding data saved for user 2: {result.get('message', 'Success')}")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 3: Load onboarding data for user 1
        print("\n3️⃣ Testing onboarding data load for user 1")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", 
                                headers=headers_user1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                data = result['data']
                print(f"✅ Loaded onboarding data for user 1:")
                print(f"   Company: {data.get('businessProfile', {}).get('companyName', 'N/A')}")
                print(f"   Industry: {data.get('businessProfile', {}).get('industry', 'N/A')}")
                print(f"   Modules: {data.get('selectedModules', [])}")
                print(f"   COA Template: {data.get('coaTemplate', 'N/A')}")
            else:
                print(f"❌ No data found for user 1")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 4: Load onboarding data for user 2
        print("\n4️⃣ Testing onboarding data load for user 2")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=2", 
                                headers=headers_user2)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                data = result['data']
                print(f"✅ Loaded onboarding data for user 2:")
                print(f"   Company: {data.get('businessProfile', {}).get('companyName', 'N/A')}")
                print(f"   Industry: {data.get('businessProfile', {}).get('industry', 'N/A')}")
                print(f"   Modules: {data.get('selectedModules', [])}")
                print(f"   COA Template: {data.get('coaTemplate', 'N/A')}")
            else:
                print(f"❌ No data found for user 2")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 5: Verify user isolation - user 1 cannot access user 2's data
        print("\n5️⃣ Testing user isolation - user 1 trying to access user 2's data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=2", 
                                headers=headers_user1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                print(f"❌ SECURITY ISSUE: User 1 can access user 2's data!")
                print(f"   Company: {result['data'].get('businessProfile', {}).get('companyName', 'N/A')}")
            else:
                print(f"✅ SECURITY OK: User 1 cannot access user 2's data")
        else:
            print(f"✅ SECURITY OK: Access denied (Status: {response.status_code})")
        
        # Test 6: Get all data for user 1
        print("\n6️⃣ Testing get all data for user 1")
        response = requests.get(f"{BASE_URL}/api/user-data/all?user_id=1", 
                                headers=headers_user1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data_types = result.get('data_types', [])
                print(f"✅ User 1 has {len(data_types)} data types: {data_types}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 7: Export user data
        print("\n7️⃣ Testing export user data for user 1")
        response = requests.get(f"{BASE_URL}/api/user-data/export?user_id=1", 
                                headers=headers_user1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                export_data = result.get('data', {})
                print(f"✅ Exported data for user 1:")
                print(f"   User ID: {export_data.get('user_id')}")
                print(f"   Data types: {list(export_data.get('data', {}).keys())}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Error: {response.text}")
        
        print("\n✅ Onboarding data persistence tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend server")
        print("Make sure the backend server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_onboarding_data_persistence()



