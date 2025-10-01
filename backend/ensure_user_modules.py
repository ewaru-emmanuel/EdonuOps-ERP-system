#!/usr/bin/env python3
"""
Ensure user has modules activated
This script will activate default modules for the user if they don't have any
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:5000"

def ensure_user_modules():
    """Ensure user has modules activated"""
    
    print("🔧 Ensuring User Has Modules Activated")
    print("=" * 40)
    
    # Test headers for user
    headers = {'Content-Type': 'application/json', 'X-User-ID': '1'}
    
    try:
        # Step 1: Check if backend is running
        print("\n1️⃣ Checking backend connectivity")
        try:
            response = requests.get(f"{BASE_URL}/api/dashboard/modules/available", headers=headers, timeout=5)
            if response.status_code == 200:
                print("✅ Backend is running")
            else:
                print(f"❌ Backend error: {response.status_code}")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Backend is not running. Please start the backend server first.")
            print("Run: cd backend && python app.py")
            return
        
        # Step 2: Check current user modules
        print("\n2️⃣ Checking current user modules")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Current modules: {len(data)}")
            
            if len(data) > 0:
                print("✅ User already has modules activated:")
                for module in data:
                    print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')} (Active: {module.get('is_active', False)})")
                print("\n🎉 User modules are already activated!")
                return
            else:
                print("❌ No modules found - this is why you see 0 modules enabled")
        
        # Step 3: Activate default modules
        print("\n3️⃣ Activating default modules for user")
        default_modules = [
            {'id': 'finance', 'name': 'Finance Module'},
            {'id': 'crm', 'name': 'CRM Module'},
            {'id': 'inventory', 'name': 'Inventory Module'},
            {'id': 'procurement', 'name': 'Procurement Module'}
        ]
        
        activated_count = 0
        for module in default_modules:
            print(f"Activating {module['id']}...")
            try:
                response = requests.post(f"{BASE_URL}/api/dashboard/modules/activate", 
                                        headers=headers, 
                                        json={
                                            'module_id': module['id'],
                                            'permissions': {
                                                'can_view': True,
                                                'can_edit': True,
                                                'can_delete': False
                                            }
                                        })
                
                if response.status_code == 200:
                    print(f"  ✅ {module['id']} activated successfully")
                    activated_count += 1
                else:
                    print(f"  ❌ Error activating {module['id']}: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Exception activating {module['id']}: {e}")
            
            # Small delay between activations
            time.sleep(0.5)
        
        # Step 4: Verify activation
        print(f"\n4️⃣ Verifying activation ({activated_count} modules activated)")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"User modules after activation: {len(data)}")
            
            if len(data) > 0:
                print("✅ Modules successfully activated:")
                for module in data:
                    print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')} (Active: {module.get('is_active', False)})")
                
                print("\n🎉 SUCCESS! User modules are now activated!")
                print("The user should now see their modules in the navigation sidebar.")
                print("Refresh the frontend page to see the changes.")
            else:
                print("❌ Still no modules found after activation")
                print("There might be an issue with the backend module activation system")
        else:
            print(f"❌ Error verifying activation: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Step 5: Additional troubleshooting
        print("\n5️⃣ Additional troubleshooting")
        print("If modules still don't show up:")
        print("1. Check browser console for errors")
        print("2. Clear localStorage: localStorage.clear()")
        print("3. Refresh the page")
        print("4. Check if backend is running on http://localhost:5000")
        print("5. Check backend logs for errors")
        
    except Exception as e:
        print(f"❌ Error during module activation: {e}")
        print("Make sure the backend server is running and accessible")

if __name__ == "__main__":
    ensure_user_modules()



