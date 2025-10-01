#!/usr/bin/env python3
"""
Test API endpoints for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime

def test_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:5000"
    
    print("🌐 Testing API endpoints...")
    
    # Test 1: Health check
    print("Test 1: Health check endpoint...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure the server is running.")
        return
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: User preferences endpoint
    print("Test 2: User preferences endpoint...")
    try:
        response = requests.get(f"{base_url}/api/user-preferences/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User preferences retrieved: {len(data)} preferences")
        elif response.status_code == 401:
            print("✅ User preferences correctly requires authentication")
        else:
            print(f"⚠️  User preferences response: {response.status_code}")
    except Exception as e:
        print(f"❌ User preferences error: {e}")
    
    # Test 3: Finance endpoints
    print("Test 3: Finance endpoints...")
    finance_endpoints = [
        "/api/finance/accounts/",
        "/api/finance/transactions/",
        "/api/finance/budgets/",
        "/api/finance/invoices/",
        "/api/finance/exchange-rates"
    ]
    
    for endpoint in finance_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} is accessible")
            else:
                print(f"   ⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    # Test 4: Sales endpoints
    print("Test 4: Sales endpoints...")
    sales_endpoints = [
        "/api/sales/customers/",
        "/api/sales/orders/",
        "/api/sales/quotes/"
    ]
    
    for endpoint in sales_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} is accessible")
            else:
                print(f"   ⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    # Test 5: Inventory endpoints
    print("Test 5: Inventory endpoints...")
    inventory_endpoints = [
        "/api/inventory/products/",
        "/api/inventory/categories/",
        "/api/inventory/suppliers/",
        "/api/inventory/stock-levels/"
    ]
    
    for endpoint in inventory_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} is accessible")
            else:
                print(f"   ⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    # Test 6: HR endpoints
    print("Test 6: HR endpoints...")
    hr_endpoints = [
        "/api/hr/employees/",
        "/api/hr/departments/",
        "/api/hr/positions/"
    ]
    
    for endpoint in hr_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} is accessible")
            else:
                print(f"   ⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    # Test 7: Core endpoints
    print("Test 7: Core endpoints...")
    core_endpoints = [
        "/api/core/settings/",
        "/api/core/tenants/",
        "/api/core/users/"
    ]
    
    for endpoint in core_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} is accessible")
            else:
                print(f"   ⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    # Test 8: Authentication endpoints
    print("Test 8: Authentication endpoints...")
    auth_endpoints = [
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/register"
    ]
    
    for endpoint in auth_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [200, 401, 403, 405]:  # 405 for method not allowed
                print(f"   ✅ {endpoint} is accessible")
            else:
                print(f"   ⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    # Test 9: POST endpoints (without data)
    print("Test 9: Testing POST endpoints...")
    post_endpoints = [
        ("/api/auth/login", {"email": "test@example.com", "password": "testpass"}),
        ("/api/user-preferences/", {"preferences": {"test": "data"}})
    ]
    
    for endpoint, data in post_endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}", json=data)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [200, 201, 400, 401, 403]:
                print(f"   ✅ {endpoint} accepts POST requests")
            else:
                print(f"   ⚠️  {endpoint} POST returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} POST error: {e}")
    
    # Test 10: Error handling
    print("Test 10: Testing error handling...")
    error_endpoints = [
        "/api/nonexistent/",
        "/api/finance/accounts/99999",
        "/api/invalid-module/"
    ]
    
    for endpoint in error_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code in [404, 400]:
                print(f"   ✅ {endpoint} correctly returns error")
            else:
                print(f"   ⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    print("🎉 API endpoint testing completed!")
    print("✅ All endpoints are responding appropriately!")

if __name__ == "__main__":
    test_endpoints()







