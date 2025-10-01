#!/usr/bin/env python3
"""
Debug script to check user modules and why they might not be showing
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def debug_user_modules():
    """Debug user modules to see what's happening"""
    
    print("🔍 Debugging User Modules Issue")
    print("=" * 50)
    
    # Test headers for user
    headers = {'Content-Type': 'application/json', 'X-User-ID': '1'}
    
    try:
        # Test 1: Check if backend is running
        print("\n1️⃣ Testing backend connectivity")
        try:
            response = requests.get(f"{BASE_URL}/api/dashboard/modules/available", headers=headers, timeout=5)
            print(f"Backend Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Backend is running")
            else:
                print(f"❌ Backend error: {response.text}")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Backend is not running. Please start the backend server.")
            return
        
        # Test 2: Check available modules
        print("\n2️⃣ Checking available modules")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/available", headers=headers)
        print(f"Available Modules Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available modules: {len(data)}")
            for module in data:
                print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')} (Active: {module.get('is_active', False)})")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 3: Check user modules
        print("\n3️⃣ Checking user modules")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        print(f"User Modules Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User modules: {len(data)}")
            if len(data) == 0:
                print("❌ No modules found for user - this is the problem!")
            else:
                for module in data:
                    print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')} (Active: {module.get('is_active', False)})")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 4: Check if user has any data in database
        print("\n4️⃣ Checking user data in database")
        response = requests.get(f"{BASE_URL}/api/user-data/all?user_id=1", headers=headers)
        print(f"User Data Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data_types = result.get('data_types', [])
                print(f"User data types: {data_types}")
                if 'selected_modules' in data_types:
                    selected_modules = result.get('data', {}).get('selected_modules', [])
                    print(f"Selected modules from user data: {selected_modules}")
                else:
                    print("❌ No selected_modules found in user data")
            else:
                print("❌ No user data found")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 5: Try to activate a module
        print("\n5️⃣ Testing module activation")
        test_module = 'finance'
        response = requests.post(f"{BASE_URL}/api/dashboard/modules/activate", 
                                headers=headers, 
                                json={'module_id': test_module})
        print(f"Module Activation Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Module {test_module} activated successfully")
            
            # Check user modules again
            response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"User modules after activation: {len(data)}")
                for module in data:
                    print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')}")
        else:
            print(f"❌ Error activating module: {response.text}")
        
        # Test 6: Check localStorage fallback
        print("\n6️⃣ Checking localStorage fallback")
        print("This would be checked in the browser console:")
        print("localStorage.getItem('edonuops_user_preferences')")
        print("localStorage.getItem('edonuops_user_modules')")
        
        print("\n🎯 DIAGNOSIS:")
        print("=" * 30)
        
        # Final diagnosis
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if len(data) == 0:
                print("❌ PROBLEM: No modules are activated for this user")
                print("💡 SOLUTION: User needs to activate modules through onboarding or manually")
                print("🔧 FIX: Go to /onboarding to activate modules")
            else:
                print("✅ Modules are activated, issue might be in frontend loading")
        else:
            print("❌ PROBLEM: Backend API error")
            print("💡 SOLUTION: Check backend logs for errors")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")

if __name__ == "__main__":
    debug_user_modules()



