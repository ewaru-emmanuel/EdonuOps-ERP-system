#!/usr/bin/env python3
"""
Comprehensive test script for all four inventory features
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_all_features():
    """Test all four features"""
    
    print("🧪 Testing All Four Inventory Features...")
    
    # Test 1: Manager's Dashboard
    print("\n1. Testing Manager's Dashboard...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/manager/warehouse-map")
        if response.status_code == 200:
            print("✅ Warehouse Map: SUCCESS")
        else:
            print(f"❌ Warehouse Map: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Warehouse Map: ERROR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/manager/predictive-alerts")
        if response.status_code == 200:
            print("✅ Predictive Alerts: SUCCESS")
        else:
            print(f"❌ Predictive Alerts: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Predictive Alerts: ERROR - {e}")
    
    # Test 2: Warehouse Operations
    print("\n2. Testing Warehouse Operations...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/warehouse/pick-lists")
        if response.status_code == 200:
            print("✅ Pick Lists: SUCCESS")
        else:
            print(f"❌ Pick Lists: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Pick Lists: ERROR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/warehouse/cycle-counts")
        if response.status_code == 200:
            print("✅ Cycle Counts: SUCCESS")
        else:
            print(f"❌ Cycle Counts: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Cycle Counts: ERROR - {e}")
    
    # Test 3: Data Integrity Admin Panel
    print("\n3. Testing Data Integrity Admin Panel...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/data-integrity/health-check")
        if response.status_code == 200:
            print("✅ Health Check: SUCCESS")
        else:
            print(f"❌ Health Check: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/data-integrity/reconciliation")
        if response.status_code == 200:
            print("✅ Reconciliation: SUCCESS")
        else:
            print(f"❌ Reconciliation: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Reconciliation: ERROR - {e}")
    
    # Test 4: Smart Analytics
    print("\n4. Testing Smart Analytics...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/analytics/kpis")
        if response.status_code == 200:
            print("✅ KPIs: SUCCESS")
        else:
            print(f"❌ KPIs: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ KPIs: ERROR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/analytics/trends")
        if response.status_code == 200:
            print("✅ Trends: SUCCESS")
        else:
            print(f"❌ Trends: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Trends: ERROR - {e}")
    
    print("\n🎉 All Features Test Complete!")

if __name__ == "__main__":
    test_all_features()
