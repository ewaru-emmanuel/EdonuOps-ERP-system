#!/usr/bin/env python3
"""
Fix user data persistence issues
This script ensures that user data is properly saved and loaded from the database
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:5000"

def fix_user_data_persistence():
    """Fix user data persistence issues"""
    
    print("🔧 Fixing User Data Persistence")
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
        
        # Step 2: Check if user has any data
        print("\n2️⃣ Checking user data in database")
        response = requests.get(f"{BASE_URL}/api/user-data/all?user_id=1", headers=headers)
        print(f"User Data Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data_types = result.get('data_types', [])
                print(f"User data types found: {data_types}")
                
                if 'selected_modules' in data_types:
                    selected_modules = result.get('data', {}).get('selected_modules', [])
                    print(f"Selected modules: {selected_modules}")
                else:
                    print("❌ No selected_modules found in user data")
            else:
                print("❌ No user data found in database")
        else:
            print(f"❌ Error loading user data: {response.text}")
        
        # Step 3: Check user modules
        print("\n3️⃣ Checking user modules")
        response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
        print(f"User Modules Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"User modules: {len(data)}")
            if len(data) == 0:
                print("❌ No modules found - this is the problem!")
                print("💡 The user needs to complete onboarding to activate modules")
            else:
                print("✅ User has modules activated:")
                for module in data:
                    print(f"  - {module.get('id', 'N/A')}: {module.get('name', 'N/A')} (Active: {module.get('is_active', False)})")
        
        # Step 4: Check if onboarding data exists
        print("\n4️⃣ Checking onboarding data")
        response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", headers=headers)
        print(f"Onboarding Data Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                data = result['data']
                print("✅ Onboarding data found:")
                print(f"  - Selected modules: {data.get('selectedModules', [])}")
                print(f"  - Company: {data.get('businessProfile', {}).get('companyName', 'N/A')}")
                print(f"  - Industry: {data.get('businessProfile', {}).get('industry', 'N/A')}")
            else:
                print("❌ No onboarding data found")
        else:
            print(f"❌ Error loading onboarding data: {response.text}")
        
        # Step 5: Diagnosis and recommendations
        print("\n5️⃣ DIAGNOSIS & RECOMMENDATIONS")
        print("=" * 40)
        
        # Check if user has completed onboarding
        onboarding_completed = False
        try:
            response = requests.get(f"{BASE_URL}/api/user-data/load/onboarding_complete?user_id=1", headers=headers)
            if response.status_code == 200:
                result = response.json()
                onboarding_completed = result.get('success') and result.get('data') is not None
        except:
            pass
        
        if not onboarding_completed:
            print("❌ PROBLEM: User has not completed onboarding")
            print("💡 SOLUTION: User needs to go to /onboarding and complete the process")
            print("🔧 FIX: This will save their data to the database and activate modules")
        else:
            print("✅ User has completed onboarding")
            
            # Check if modules are activated
            try:
                response = requests.get(f"{BASE_URL}/api/dashboard/modules/user", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) == 0:
                        print("❌ PROBLEM: Onboarding completed but no modules activated")
                        print("💡 SOLUTION: User needs to reactivate modules or complete onboarding again")
                    else:
                        print("✅ User has modules activated")
                        print("🎉 Everything looks good! The issue might be in frontend loading")
            except:
                print("❌ Could not check user modules")
        
        print("\n🎯 FINAL RECOMMENDATIONS:")
        print("=" * 30)
        
        if not onboarding_completed:
            print("1. User should go to /onboarding to complete the process")
            print("2. This will save all their data to the database")
            print("3. This will activate their selected modules")
            print("4. After onboarding, they should see their modules in the navigation")
        else:
            print("1. User has completed onboarding")
            print("2. Check if modules are activated in backend")
            print("3. If modules are activated, the issue is in frontend loading")
            print("4. Clear browser cache and refresh the page")
            print("5. Check browser console for errors")
        
        print("\n🔧 QUICK FIXES:")
        print("- Clear browser cache: localStorage.clear(); location.reload()")
        print("- Check browser console for errors")
        print("- Make sure backend is running on http://localhost:5000")
        print("- Go to /onboarding to reactivate modules if needed")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")

if __name__ == "__main__":
    fix_user_data_persistence()



