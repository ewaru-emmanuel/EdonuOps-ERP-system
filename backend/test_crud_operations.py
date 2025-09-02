#!/usr/bin/env python3
"""
Comprehensive CRUD Operations Test for Inventory Module
Tests all Create, Read, Update, Delete operations across all inventory features
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_product_crud():
    """Test Product CRUD operations"""
    print("\n🧪 Testing Product CRUD Operations...")
    
    # Test CREATE
    print("  📝 Testing CREATE...")
    product_data = {
        'name': 'Test Product CRUD',
        'sku': f'CRUD{int(time.time())}',
        'category_id': 1,
        'description': 'Test product for CRUD operations',
        'base_uom_id': 1,
        'current_cost': 100.00,
        'min_stock': 10,
        'max_stock': 100,
        'reorder_point': 20
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/advanced/products', json=product_data)
    if response.status_code == 201:
        product_id = response.json().get('id')
        print(f"    ✅ Product created with ID: {product_id}")
    else:
        print(f"    ❌ Failed to create product: {response.status_code} - {response.text}")
        return False
    
    # Test READ
    print("  📖 Testing READ...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
    if response.status_code == 200:
        product = response.json()
        print(f"    ✅ Product retrieved: {product.get('name')}")
    else:
        print(f"    ❌ Failed to read product: {response.status_code} - {response.text}")
        return False
    
    # Test UPDATE
    print("  ✏️ Testing UPDATE...")
    update_data = {
        'name': 'Updated Test Product CRUD',
        'current_cost': 150.00
    }
    response = requests.put(f'{BASE_URL}/api/inventory/advanced/products/{product_id}', json=update_data)
    if response.status_code == 200:
        print(f"    ✅ Product updated successfully")
    else:
        print(f"    ❌ Failed to update product: {response.status_code} - {response.text}")
        return False
    
    # Test DELETE
    print("  🗑️ Testing DELETE...")
    response = requests.delete(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
    if response.status_code == 200:
        print(f"    ✅ Product deleted successfully")
    else:
        print(f"    ❌ Failed to delete product: {response.status_code} - {response.text}")
        return False
    
    return True

def test_inventory_taking_crud():
    """Test Inventory Taking CRUD operations"""
    print("\n🧪 Testing Inventory Taking CRUD Operations...")
    
    # Test CREATE (Save Draft)
    print("  📝 Testing CREATE (Save Draft)...")
    count_data = {
        'items': [
            {
                'itemCode': 'SKU001',
                'countedQuantity': 15,
                'batchLotNumber': 'BATCH001',
                'serialNumber': '',
                'locationBin': 'A1-01',
                'itemStatus': 'good',
                'expiryDate': '2025-12-31',
                'manufacturingDate': '2024-01-01',
                'itemRemarks': 'Test count item'
            }
        ]
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/taking/counts', json=count_data)
    if response.status_code == 200:
        count_id = response.json().get('count_id')
        print(f"    ✅ Draft saved with ID: {count_id}")
    else:
        print(f"    ❌ Failed to save draft: {response.status_code} - {response.text}")
        return False
    
    # Test UPDATE (Submit Count)
    print("  ✏️ Testing UPDATE (Submit Count)...")
    submit_data = {
        'items': [
            {
                'itemCode': 'SKU001',
                'countedQuantity': 15,
                'batchLotNumber': 'BATCH001',
                'serialNumber': '',
                'locationBin': 'A1-01',
                'itemStatus': 'good',
                'expiryDate': '2025-12-31',
                'manufacturingDate': '2024-01-01',
                'itemRemarks': 'Test count item - submitted'
            }
        ]
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/taking/counts/{count_id}/submit', json=submit_data)
    if response.status_code == 200:
        print(f"    ✅ Count submitted successfully")
    else:
        print(f"    ❌ Failed to submit count: {response.status_code} - {response.text}")
        return False
    
    # Test READ (Export Template)
    print("  📖 Testing READ (Export Template)...")
    response = requests.get(f'{BASE_URL}/api/inventory/taking/export-template')
    if response.status_code == 200:
        print(f"    ✅ Template exported successfully")
    else:
        print(f"    ❌ Failed to export template: {response.status_code} - {response.text}")
        return False
    
    return True

def test_data_integrity_operations():
    """Test Data Integrity operations"""
    print("\n🧪 Testing Data Integrity Operations...")
    
    # Test Health Check
    print("  🔍 Testing Health Check...")
    response = requests.get(f'{BASE_URL}/api/inventory/data-integrity/health-check')
    if response.status_code == 200:
        print(f"    ✅ Health check completed")
    else:
        print(f"    ❌ Failed health check: {response.status_code} - {response.text}")
        return False
    
    # Test Reconciliation
    print("  🔄 Testing Reconciliation...")
    response = requests.get(f'{BASE_URL}/api/inventory/data-integrity/reconciliation')
    if response.status_code == 200:
        print(f"    ✅ Reconciliation data retrieved")
    else:
        print(f"    ❌ Failed reconciliation: {response.status_code} - {response.text}")
        return False
    
    # Test Audit Trail
    print("  📋 Testing Audit Trail...")
    response = requests.get(f'{BASE_URL}/api/inventory/data-integrity/audit-trail')
    if response.status_code == 200:
        print(f"    ✅ Audit trail retrieved")
    else:
        print(f"    ❌ Failed audit trail: {response.status_code} - {response.text}")
        return False
    
    return True

def test_analytics_operations():
    """Test Analytics operations"""
    print("\n🧪 Testing Analytics Operations...")
    
    # Test KPIs
    print("  📊 Testing KPIs...")
    response = requests.get(f'{BASE_URL}/api/inventory/analytics/kpis')
    if response.status_code == 200:
        print(f"    ✅ KPIs retrieved")
    else:
        print(f"    ❌ Failed KPIs: {response.status_code} - {response.text}")
        return False
    
    # Test Trends
    print("  📈 Testing Trends...")
    response = requests.get(f'{BASE_URL}/api/inventory/analytics/trends')
    if response.status_code == 200:
        print(f"    ✅ Trends retrieved")
    else:
        print(f"    ❌ Failed trends: {response.status_code} - {response.text}")
        return False
    
    # Test Stock Levels Report
    print("  📦 Testing Stock Levels Report...")
    response = requests.get(f'{BASE_URL}/api/inventory/analytics/reports/stock-levels')
    if response.status_code == 200:
        print(f"    ✅ Stock levels report retrieved")
    else:
        print(f"    ❌ Failed stock levels report: {response.status_code} - {response.text}")
        return False
    
    return True

def test_manager_dashboard_operations():
    """Test Manager Dashboard operations"""
    print("\n🧪 Testing Manager Dashboard Operations...")
    
    # Test Warehouse Map
    print("  🗺️ Testing Warehouse Map...")
    response = requests.get(f'{BASE_URL}/api/inventory/manager/warehouse-map')
    if response.status_code == 200:
        print(f"    ✅ Warehouse map retrieved")
    else:
        print(f"    ❌ Failed warehouse map: {response.status_code} - {response.text}")
        return False
    
    # Test Predictive Alerts
    print("  ⚠️ Testing Predictive Alerts...")
    response = requests.get(f'{BASE_URL}/api/inventory/manager/predictive-alerts')
    if response.status_code == 200:
        print(f"    ✅ Predictive alerts retrieved")
    else:
        print(f"    ❌ Failed predictive alerts: {response.status_code} - {response.text}")
        return False
    
    # Test Picker Performance
    print("  👥 Testing Picker Performance...")
    response = requests.get(f'{BASE_URL}/api/inventory/manager/picker-performance')
    if response.status_code == 200:
        print(f"    ✅ Picker performance retrieved")
    else:
        print(f"    ❌ Failed picker performance: {response.status_code} - {response.text}")
        return False
    
    return True

def test_warehouse_operations():
    """Test Warehouse Operations"""
    print("\n🧪 Testing Warehouse Operations...")
    
    # Test Pick Lists
    print("  📋 Testing Pick Lists...")
    response = requests.get(f'{BASE_URL}/api/inventory/warehouse/pick-lists')
    if response.status_code == 200:
        print(f"    ✅ Pick lists retrieved")
    else:
        print(f"    ❌ Failed pick lists: {response.status_code} - {response.text}")
        return False
    
    # Test Cycle Counts
    print("  🔢 Testing Cycle Counts...")
    response = requests.get(f'{BASE_URL}/api/inventory/warehouse/cycle-counts')
    if response.status_code == 200:
        print(f"    ✅ Cycle counts retrieved")
    else:
        print(f"    ❌ Failed cycle counts: {response.status_code} - {response.text}")
        return False
    
    # Test Live Activity
    print("  🏃 Testing Live Activity...")
    response = requests.get(f'{BASE_URL}/api/inventory/warehouse/live-activity')
    if response.status_code == 200:
        print(f"    ✅ Live activity retrieved")
    else:
        print(f"    ❌ Failed live activity: {response.status_code} - {response.text}")
        return False
    
    return True

def main():
    """Run all CRUD tests"""
    print("🚀 Starting Comprehensive CRUD Operations Test")
    print("=" * 60)
    
    tests = [
        ("Product CRUD", test_product_crud),
        ("Inventory Taking CRUD", test_inventory_taking_crud),
        ("Data Integrity Operations", test_data_integrity_operations),
        ("Analytics Operations", test_analytics_operations),
        ("Manager Dashboard Operations", test_manager_dashboard_operations),
        ("Warehouse Operations", test_warehouse_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 CRUD Operations Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CRUD OPERATIONS ARE WORKING PERFECTLY!")
    else:
        print("⚠️ Some operations need attention")
    
    return passed == total

if __name__ == "__main__":
    main()
