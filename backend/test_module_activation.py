#!/usr/bin/env python3
"""
Test script for module activation system
This script tests the module activation API endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_module_activation():
    """Test the module activation endpoints"""
    
    print("🧪 Testing Module Activation System")
    print("=" * 50)
    
    # Test headers
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': '1'  # Test user ID
    }
    
    try:
        # Test 1: Get available modules
        print("\n1️⃣ Testing GET /api/dashboard/modules/available")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/available", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            modules = response.json()
            print(f"Available modules: {len(modules)}")
            for module in modules:
                print(f"  - {module['id']}: {module['name']} (enabled: {module['is_enabled']})")
        else:
            print(f"Error: {response.text}")
        
        # Test 2: Get user modules
        print("\n2️⃣ Testing GET /api/dashboard/modules/user")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_modules = response.json()
            print(f"User modules: {len(user_modules)}")
            for module in user_modules:
                print(f"  - {module['id']}: {module['name']} (active: {module['is_active']})")
        else:
            print(f"Error: {response.text}")
        
        # Test 3: Activate a module
        print("\n3️⃣ Testing POST /api/dashboard/modules/activate")
        activate_data = {
            "module_id": "finance",
            "permissions": {
                "can_view": True,
                "can_edit": True,
                "can_delete": False
            }
        }
        response = requests.post(f"{BASE_URL}/api/dashboard/modules/activate", 
                                headers=headers, 
                                json=activate_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Activation result: {result.get('message', 'Success')}")
        else:
            print(f"Error: {response.text}")
        
        # Test 4: Check module access
        print("\n4️⃣ Testing GET /api/dashboard/modules/check/finance")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/check/finance", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Has access to finance: {result.get('has_access', False)}")
        else:
            print(f"Error: {response.text}")
        
        # Test 5: Bulk activate modules
        print("\n5️⃣ Testing POST /api/dashboard/modules/bulk-activate")
        bulk_data = {
            "module_ids": ["crm", "inventory"],
            "permissions": {
                "crm": {"can_view": True, "can_edit": True},
                "inventory": {"can_view": True, "can_edit": False}
            }
        }
        response = requests.post(f"{BASE_URL}/api/dashboard/modules/bulk-activate", 
                                headers=headers, 
                                json=bulk_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Bulk activation: {result.get('message', 'Success')}")
            print(f"Activated: {len(result.get('activated_modules', []))}")
            print(f"Failed: {len(result.get('failed_modules', []))}")
        else:
            print(f"Error: {response.text}")
        
        # Test 6: Deactivate a module
        print("\n6️⃣ Testing POST /api/dashboard/modules/deactivate")
        deactivate_data = {
            "module_id": "crm"
        }
        response = requests.post(f"{BASE_URL}/api/dashboard/modules/deactivate", 
                                headers=headers, 
                                json=deactivate_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Deactivation result: {result.get('message', 'Success')}")
        else:
            print(f"Error: {response.text}")
        
        print("\n✅ Module activation tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend server")
        print("Make sure the backend server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_module_activation()




