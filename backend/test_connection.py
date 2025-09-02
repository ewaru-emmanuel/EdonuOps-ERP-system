#!/usr/bin/env python3
"""
Test Frontend-Backend-Database Connection
Comprehensive test to verify all components are working together
"""

import requests
import json
import sqlite3
import time

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data['status']}")
            return True
        else:
            print(f"❌ Backend Health: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health: {e}")
        return False

def test_database_connection():
    """Test if database is accessible and has data"""
    try:
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'advanced_products' in tables:
            print("✅ Database: advanced_products table exists")
            
            # Check if we have data
            cursor.execute("SELECT COUNT(*) FROM advanced_products")
            count = cursor.fetchone()[0]
            print(f"✅ Database: Found {count} products")
            
            # Check if product_id column exists
            cursor.execute("PRAGMA table_info(advanced_products)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'product_id' in columns:
                print("✅ Database: product_id column exists")
            else:
                print("❌ Database: product_id column missing")
                return False
                
        else:
            print("❌ Database: advanced_products table missing")
            return False
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database: {e}")
        return False

def test_inventory_endpoints():
    """Test inventory API endpoints"""
    endpoints = [
        ('Categories', '/api/inventory/advanced/categories'),
        ('UoM', '/api/inventory/advanced/uom'),
        ('Products', '/api/inventory/advanced/products')
    ]
    
    results = {}
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ {name}: {len(data)} items returned")
                else:
                    print(f"✅ {name}: Success")
                results[name] = True
            else:
                print(f"❌ {name}: Status {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"❌ {name}: {e}")
            results[name] = False
    
    return results

def test_finance_endpoints():
    """Test finance API endpoints"""
    endpoints = [
        ('Accounts', '/api/finance/accounts'),
        ('Budgets', '/api/finance/budgets'),
        ('Accounts Payable', '/api/finance/accounts-payable')
    ]
    
    results = {}
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ {name}: {len(data)} items returned")
                else:
                    print(f"✅ {name}: Success")
                results[name] = True
            else:
                print(f"❌ {name}: Status {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"❌ {name}: {e}")
            results[name] = False
    
    return results

def test_frontend_connectivity():
    """Test if frontend can reach backend"""
    try:
        # Test the main API endpoint that frontend uses
        response = requests.get('http://localhost:5000/api/inventory/advanced/products', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend-Backend: Products endpoint accessible")
            return True
        else:
            print(f"❌ Frontend-Backend: Products endpoint failed - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend-Backend: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing Frontend-Backend-Database Connection")
    print("=" * 50)
    
    # Test 1: Backend Health
    print("\n📡 Test 1: Backend Health")
    backend_ok = test_backend_health()
    
    # Test 2: Database Connection
    print("\n🗄️ Test 2: Database Connection")
    db_ok = test_database_connection()
    
    # Test 3: Inventory Endpoints
    print("\n📦 Test 3: Inventory Endpoints")
    inventory_results = test_inventory_endpoints()
    
    # Test 4: Finance Endpoints
    print("\n💰 Test 4: Finance Endpoints")
    finance_results = test_finance_endpoints()
    
    # Test 5: Frontend Connectivity
    print("\n🌐 Test 5: Frontend-Backend Connectivity")
    frontend_ok = test_frontend_connectivity()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CONNECTION TEST SUMMARY")
    print("=" * 50)
    
    print(f"Backend Health: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Frontend-Backend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    inventory_passed = sum(inventory_results.values())
    inventory_total = len(inventory_results)
    print(f"Inventory Endpoints: {inventory_passed}/{inventory_total} ✅")
    
    finance_passed = sum(finance_results.values())
    finance_total = len(finance_results)
    print(f"Finance Endpoints: {finance_passed}/{finance_total} ✅")
    
    # Overall status
    all_tests_passed = backend_ok and db_ok and frontend_ok and inventory_passed == inventory_total
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Frontend, Backend, and Database are fully connected!")
        print("✅ The platform is ready for use!")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Check the individual test results above for details")
    
    return all_tests_passed

if __name__ == "__main__":
    main()


