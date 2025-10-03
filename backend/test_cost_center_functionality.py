#!/usr/bin/env python3
"""
Test Cost Center Functionality
=============================

This script tests the cost center, department, and project functionality.
"""

import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:5000/api/finance/cost-centers"
USER_ID = "3"  # Assuming user 3 exists
HEADERS = {"X-User-ID": USER_ID, "Content-Type": "application/json"}

def test_cost_center_functionality():
    print('🧪 TESTING COST CENTER FUNCTIONALITY')
    print('=' * 50)
    
    # Test 1: Get all cost centers, departments, and projects
    print('🔍 Test 1: Get All Cost Centers, Departments, and Projects')
    
    try:
        response = requests.get(f"{BASE_URL}/all", headers=HEADERS)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   ✅ Cost Centers: {len(data["cost_centers"])}')
            print(f'   ✅ Departments: {len(data["departments"])}')
            print(f'   ✅ Projects: {len(data["projects"])}')
            
            # Show sample data
            if data["cost_centers"]:
                print(f'   Sample Cost Center: {data["cost_centers"][0]["code"]} - {data["cost_centers"][0]["name"]}')
            if data["departments"]:
                print(f'   Sample Department: {data["departments"][0]["code"]} - {data["departments"][0]["name"]}')
            if data["projects"]:
                print(f'   Sample Project: {data["projects"][0]["code"]} - {data["projects"][0]["name"]}')
        else:
            print(f'   ❌ Failed: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('   ❌ Connection Error: Make sure the server is running on localhost:5000')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    # Test 2: Create a new cost center
    print('\n🔍 Test 2: Create New Cost Center')
    
    new_cost_center = {
        "code": "TEST",
        "name": "Test Cost Center",
        "description": "Test cost center for API testing",
        "cost_center_type": "department",
        "budget_amount": 10000.0,
        "responsible_manager": "Test Manager"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/cost-centers", headers=HEADERS, data=json.dumps(new_cost_center))
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 201:
            data = response.json()
            print(f'   ✅ Cost Center Created: {data["cost_center"]["code"]} - {data["cost_center"]["name"]}')
            cost_center_id = data["cost_center"]["id"]
        else:
            print(f'   ❌ Failed: {response.text}')
            cost_center_id = None
            
    except Exception as e:
        print(f'   ❌ Error: {e}')
        cost_center_id = None
    
    # Test 3: Create a new department
    print('\n🔍 Test 3: Create New Department')
    
    new_department = {
        "code": "TEST",
        "name": "Test Department",
        "description": "Test department for API testing",
        "department_head": "Test Head",
        "location": "Test Location"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/departments", headers=HEADERS, data=json.dumps(new_department))
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 201:
            data = response.json()
            print(f'   ✅ Department Created: {data["department"]["code"]} - {data["department"]["name"]}')
            department_id = data["department"]["id"]
        else:
            print(f'   ❌ Failed: {response.text}')
            department_id = None
            
    except Exception as e:
        print(f'   ❌ Error: {e}')
        department_id = None
    
    # Test 4: Create a new project
    print('\n🔍 Test 4: Create New Project')
    
    new_project = {
        "code": "TEST",
        "name": "Test Project",
        "description": "Test project for API testing",
        "project_type": "internal",
        "budget_amount": 50000.0,
        "project_manager": "Test PM"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects", headers=HEADERS, data=json.dumps(new_project))
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 201:
            data = response.json()
            print(f'   ✅ Project Created: {data["project"]["code"]} - {data["project"]["name"]}')
            project_id = data["project"]["id"]
        else:
            print(f'   ❌ Failed: {response.text}')
            project_id = None
            
    except Exception as e:
        print(f'   ❌ Error: {e}')
        project_id = None
    
    # Test 5: Get summaries
    print('\n🔍 Test 5: Get Cost Center Summary')
    
    try:
        response = requests.get(f"{BASE_URL}/cost-centers/summary", headers=HEADERS)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   ✅ Cost Center Summary Retrieved')
            print(f'   Total Expenses: ${data["total_expenses"]:.2f}')
            print(f'   Cost Centers: {len(data["cost_centers"])}')
        else:
            print(f'   ❌ Failed: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    print('\n🎯 COST CENTER FUNCTIONALITY TEST COMPLETE!')

if __name__ == "__main__":
    test_cost_center_functionality()
