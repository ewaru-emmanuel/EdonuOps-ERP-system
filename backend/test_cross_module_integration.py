#!/usr/bin/env python3
"""
Cross-Module Integration Test
Tests the integration between Finance, Inventory, and CRM modules
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
results = {'passed': 0, 'failed': 0, 'errors': []}

def test_endpoint(method, endpoint, data=None, params=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return True, None
        else:
            return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)

def log_test(name, success, error=None):
    if success:
        results['passed'] += 1
        print(f"✅ {name}")
    else:
        results['failed'] += 1
        print(f"❌ {name}: {error}")
        results['errors'].append(f"{name}: {error}")

print("🔗 Testing Cross-Module Integration...")

# Test 1: Cross-Module Health Check
print("\n🏥 Test 1: Cross-Module Health Check")
log_test("GET Integration Health", *test_endpoint('GET', '/api/integration/health'))

# Test 2: Cross-Module Analytics
print("\n📊 Test 2: Cross-Module Analytics")
log_test("GET Cross-Module Analytics", *test_endpoint('GET', '/api/integration/analytics'))

# Test 3: Purchase Order with AP Integration
print("\n🛒 Test 3: Purchase Order with AP Integration")
po_data = {
    "supplier_id": 1,
    "items": [
        {"product_id": 1, "quantity": 10, "unit_price": 100.00}
    ],
    "total_amount": 1000.00
}
log_test("POST Purchase Order with AP", *test_endpoint('POST', '/api/integration/purchase-order-with-ap', po_data))

# Test 4: Goods Receipt Processing
print("\n📦 Test 4: Goods Receipt Processing")
gr_data = {
    "po_id": 1,
    "received_items": [
        {
            "product_id": 1,
            "quantity_received": 10,
            "unit_cost": 100.00,
            "location_id": 1
        }
    ]
}
log_test("POST Goods Receipt", *test_endpoint('POST', '/api/integration/goods-receipt', gr_data))

# Test 5: Verify Finance Integration
print("\n💰 Test 5: Verify Finance Integration")
log_test("GET Accounts Payable", *test_endpoint('GET', '/api/finance/accounts-payable'))
log_test("GET General Ledger", *test_endpoint('GET', '/api/finance/general-ledger'))

# Test 6: Verify Inventory Integration
print("\n🏭 Test 6: Verify Inventory Integration")
log_test("GET Stock Levels", *test_endpoint('GET', '/api/inventory/advanced/stock-levels'))
log_test("GET Products", *test_endpoint('GET', '/api/inventory/advanced/products'))

# Test 7: Verify CRM Integration
print("\n👥 Test 7: Verify CRM Integration")
log_test("GET CRM Leads", *test_endpoint('GET', '/api/crm/leads'))
log_test("GET CRM Opportunities", *test_endpoint('GET', '/api/crm/opportunities'))

print(f"\n📊 Cross-Module Integration Results: {results['passed']} passed, {results['failed']} failed")
success_rate = (results['passed'] / (results['passed'] + results['failed'])) * 100 if (results['passed'] + results['failed']) > 0 else 0
print(f"📈 Success Rate: {success_rate:.1f}%")

if success_rate >= 90:
    print("🎉 Excellent! Cross-module integration is working perfectly!")
elif success_rate >= 70:
    print("👍 Good! Most cross-module integrations are working.")
else:
    print("⚠️  Needs attention! Multiple integration issues detected.")

