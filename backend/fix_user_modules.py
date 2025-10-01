#!/usr/bin/env python3
"""
Fix script to ensure user has modules activated
This will activate default modules for the user if they don't have any
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def fix_user_modules():
    """Fix user modules by activating default modules"""
    
    print("🔧 Fixing User Modules")
    print("=" * 30)
    
    # Test headers for user
    headers = {'Content-Type': 'application/json', 'X-User-ID': '1'}
    
    try:
        # Check current user modules
        print("\n1️⃣ Checking current user modules")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Current modules: {len(data)}")
            if len(data) > 0:
                print("✅ User already has modules activated:")
                for module in data:
                    print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')}")
                return
            else:
                print("❌ No modules found - activating default modules")
        
        # Activate default modules
        print("\n2️⃣ Activating default modules")
        default_modules = ['finance', 'crm', 'inventory', 'procurement']
        
        for module_id in default_modules:
            print(f"Activating {module_id}...")
            response = requests.post(f"{BASE_URL}/api/dashboard/modules/activate", 
                                    headers=headers, 
                                    json={
                                        'module_id': module_id,
                                        'permissions': {
                                            'can_view': True,
                                            'can_edit': True,
                                            'can_delete': False
                                        }
                                    })
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ {module_id} activated")
            else:
                print(f"  ❌ Error: {response.text}")
        
        # Check user modules again
        print("\n3️⃣ Verifying user modules")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"User modules after activation: {len(data)}")
            for module in data:
                print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')} (Active: {module.get('is_active', False)})")
        
        print("\n🎉 User modules fixed!")
        print("The user should now see their modules in the navigation")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend server")
        print("Make sure the backend server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_user_modules()



