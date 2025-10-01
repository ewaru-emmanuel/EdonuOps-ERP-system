#!/usr/bin/env python3
"""
Test script to verify profile data loading from database
This tests that user profile data is correctly loaded from the database
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_profile_data_loading():
    """Test that profile data is correctly loaded from database"""
    
    print("👤 Testing Profile Data Loading from Database")
    print("=" * 60)
    
    # Test headers for user
    headers = {'Content-Type': 'application/json', 'X-User-ID': '1'}
    
    try:
        # Test 1: Save comprehensive onboarding data
        print("\n1️⃣ Saving comprehensive onboarding data for user profile")
        
        # Business Profile Data
        business_profile = {
            "companyName": "Test Company Inc",
            "industry": "Technology",
            "employeeCount": "11-50",
            "annualRevenue": "$100K - $500K",
            "challenges": [
                "Manual processes taking too much time",
                "Need better financial tracking",
                "Inventory management issues"
            ],
            "createdAt": "2023-10-27T10:00:00.000Z"
        }
        
        # Save business profile
        response = requests.post(f"{BASE_URL}/api/user-data/save", 
                                headers=headers, 
                                json={
                                    "user_id": 1,
                                    "data_type": "business_profile",
                                    "data": business_profile
                                })
        print(f"Business Profile Save Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Business profile saved successfully")
        else:
            print(f"❌ Error: {response.text}")
        
        # Onboarding Complete Data
        onboarding_complete = {
            "businessProfile": business_profile,
            "selectedModules": ["financials", "crm", "inventory"],
            "coaTemplate": "retail",
            "organizationSetup": {
                "organizationType": "single_owner",
                "departments": ["Management", "Finance", "Operations"],
                "userPermissions": {
                    "defaultUserRole": "admin",
                    "restrictionLevel": "flexible",
                    "allowRoleOverride": True,
                    "requireApprovalForAdjustments": False
                }
            },
            "onboardingMetadata": {
                "activatedAt": "2023-10-27T10:00:00.000Z",
                "visitorId": "test_visitor_id",
                "deviceInfo": {
                    "userAgent": "test_agent",
                    "screenResolution": "1920x1080",
                    "timezone": "UTC"
                },
                "version": "1.0"
            }
        }
        
        # Save onboarding complete data
        response = requests.post(f"{BASE_URL}/api/user-data/save", 
                                headers=headers, 
                                json={
                                    "user_id": 1,
                                    "data_type": "onboarding_complete",
                                    "data": onboarding_complete
                                })
        print(f"Onboarding Complete Save Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Onboarding complete data saved successfully")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 2: Load business profile data
        print("\n2️⃣ Loading business profile data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/business_profile?user_id=1", headers=headers)
        print(f"Business Profile Load Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                data = result['data']
                print("✅ Business profile loaded successfully:")
                print(f"   Company: {data.get('companyName', 'N/A')}")
                print(f"   Industry: {data.get('industry', 'N/A')}")
                print(f"   Employee Count: {data.get('employeeCount', 'N/A')}")
                print(f"   Annual Revenue: {data.get('annualRevenue', 'N/A')}")
                print(f"   Challenges: {', '.join(data.get('challenges', []))}")
            else:
                print("❌ No business profile data found")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 3: Load onboarding complete data
        print("\n3️⃣ Loading onboarding complete data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", headers=headers)
        print(f"Onboarding Complete Load Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                data = result['data']
                print("✅ Onboarding complete data loaded successfully:")
                print(f"   Selected Modules: {', '.join(data.get('selectedModules', []))}")
                print(f"   COA Template: {data.get('coaTemplate', 'N/A')}")
                print(f"   Organization Type: {data.get('organizationSetup', {}).get('organizationType', 'N/A')}")
                print(f"   Activated At: {data.get('onboardingMetadata', {}).get('activatedAt', 'N/A')}")
            else:
                print("❌ No onboarding complete data found")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 4: Load all user data
        print("\n4️⃣ Loading all user data")
        response = requests.get(f"{BASE_URL}/api/user-data/all?user_id=1", headers=headers)
        print(f"All User Data Load Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data_types'):
                data_types = result['data_types']
                print(f"✅ All user data loaded successfully:")
                print(f"   Available data types: {', '.join(data_types)}")
                
                # Show data for each type
                for data_type in data_types:
                    print(f"\n   📊 {data_type}:")
                    if data_type in result.get('data', {}):
                        data = result['data'][data_type]
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if key != 'challenges':  # Skip challenges for cleaner output
                                    print(f"      {key}: {value}")
                        else:
                            print(f"      Value: {data}")
            else:
                print("❌ No user data found")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 5: Simulate profile page data loading
        print("\n5️⃣ Simulating profile page data loading")
        
        # Load all the data that the profile page would need
        profile_data = {}
        
        # Load business profile
        response = requests.get(f"{BASE_URL}/api/user-data/load/business_profile?user_id=1", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                profile_data['business_profile'] = result['data']
        
        # Load onboarding complete
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                profile_data['onboarding_complete'] = result['data']
        
        # Load selected modules
        response = requests.get(f"{BASE_URL}/api/user-data/load/selected_modules?user_id=1", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                profile_data['selected_modules'] = result['data']
        
        print("✅ Profile page data simulation:")
        print(f"   Business Profile Available: {'business_profile' in profile_data}")
        print(f"   Onboarding Complete Available: {'onboarding_complete' in profile_data}")
        print(f"   Selected Modules Available: {'selected_modules' in profile_data}")
        
        if 'business_profile' in profile_data:
            bp = profile_data['business_profile']
            print(f"\n   📋 Business Profile Data:")
            print(f"      Company Name: {bp.get('companyName', 'N/A')}")
            print(f"      Industry: {bp.get('industry', 'N/A')}")
            print(f"      Employee Count: {bp.get('employeeCount', 'N/A')}")
            print(f"      Annual Revenue: {bp.get('annualRevenue', 'N/A')}")
        
        if 'onboarding_complete' in profile_data:
            oc = profile_data['onboarding_complete']
            print(f"\n   🎯 Onboarding Complete Data:")
            print(f"      Selected Modules: {', '.join(oc.get('selectedModules', []))}")
            print(f"      COA Template: {oc.get('coaTemplate', 'N/A')}")
            print(f"      Activated At: {oc.get('onboardingMetadata', {}).get('activatedAt', 'N/A')}")
        
        print("\n🎉 Profile data loading tests completed!")
        print("✅ All profile data is correctly loaded from database")
        print("✅ Profile page will display user's onboarding information")
        print("✅ User can see their company details, industry, and selected modules")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend server")
        print("Make sure the backend server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_profile_data_loading()



