#!/usr/bin/env python3
"""
Comprehensive Test for All Inventory Features
Tests UoM, Zones, Aisles, Categories, and other missing features
"""

import requests
import time

BASE_URL = 'http://localhost:5000'

def test_uom_crud():
    """Test UoM CRUD operations"""
    print("🧪 Testing UoM CRUD Operations...")
    
    # Test CREATE
    print("  📝 Testing CREATE...")
    uom_data = {
        'name': 'Test UoM',
        'code': f'TEST{int(time.time())}',
        'description': 'Test unit of measure',
        'is_base_unit': False
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/advanced/uom', json=uom_data)
    if response.status_code == 201:
        uom_id = response.json().get('id')
        print(f"    ✅ UoM created with ID: {uom_id}")
    else:
        print(f"    ❌ Failed to create UoM: {response.status_code} - {response.text}")
        return False
    
    # Test READ
    print("  📖 Testing READ...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/uom')
    if response.status_code == 200:
        uoms = response.json()
        test_uom = next((u for u in uoms if u.get('id') == uom_id), None)
        if test_uom:
            print(f"    ✅ UoM retrieved: {test_uom.get('name')}")
        else:
            print(f"    ❌ UoM not found in list")
            return False
    else:
        print(f"    ❌ Failed to read UoMs: {response.status_code} - {response.text}")
        return False
    
    # Test UPDATE
    print("  ✏️ Testing UPDATE...")
    update_data = {
        'name': 'Updated Test UoM',
        'description': 'Updated test unit of measure'
    }
    response = requests.put(f'{BASE_URL}/api/inventory/advanced/uom/{uom_id}', json=update_data)
    if response.status_code == 200:
        print(f"    ✅ UoM updated successfully")
    else:
        print(f"    ❌ Failed to update UoM: {response.status_code} - {response.text}")
        return False
    
    # Test DELETE
    print("  🗑️ Testing DELETE...")
    response = requests.delete(f'{BASE_URL}/api/inventory/advanced/uom/{uom_id}')
    if response.status_code == 200:
        print(f"    ✅ UoM deleted successfully")
    else:
        print(f"    ❌ Failed to delete UoM: {response.status_code} - {response.text}")
        return False
    
    return True

def test_zones_crud():
    """Test Warehouse Zones CRUD operations"""
    print("\n🧪 Testing Warehouse Zones CRUD Operations...")
    
    # Test CREATE
    print("  📝 Testing CREATE...")
    zone_data = {
        'name': 'Test Zone',
        'description': 'Test warehouse zone',
        'capacity': 1500
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/advanced/warehouse-zones', json=zone_data)
    if response.status_code == 201:
        zone_id = response.json().get('zone', {}).get('id')
        print(f"    ✅ Zone created with ID: {zone_id}")
    else:
        print(f"    ❌ Failed to create zone: {response.status_code} - {response.text}")
        return False
    
    # Test READ
    print("  📖 Testing READ...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/warehouse-zones')
    if response.status_code == 200:
        zones = response.json()
        test_zone = next((z for z in zones if z.get('id') == zone_id), None)
        if test_zone:
            print(f"    ✅ Zone retrieved: {test_zone.get('name')}")
        else:
            print(f"    ❌ Zone not found in list")
            return False
    else:
        print(f"    ❌ Failed to read zones: {response.status_code} - {response.text}")
        return False
    
    return True

def test_aisles_crud():
    """Test Warehouse Aisles CRUD operations"""
    print("\n🧪 Testing Warehouse Aisles CRUD Operations...")
    
    # Test CREATE
    print("  📝 Testing CREATE...")
    aisle_data = {
        'name': 'Test Aisle',
        'zone_id': 1,
        'zone_name': 'Zone A - Picking',
        'length': 120,
        'width': 15,
        'height': 25
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/advanced/warehouse-aisles', json=aisle_data)
    if response.status_code == 201:
        aisle_id = response.json().get('aisle', {}).get('id')
        print(f"    ✅ Aisle created with ID: {aisle_id}")
    else:
        print(f"    ❌ Failed to create aisle: {response.status_code} - {response.text}")
        return False
    
    # Test READ
    print("  📖 Testing READ...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/warehouse-aisles')
    if response.status_code == 200:
        aisles = response.json()
        test_aisle = next((a for a in aisles if a.get('id') == aisle_id), None)
        if test_aisle:
            print(f"    ✅ Aisle retrieved: {test_aisle.get('name')}")
        else:
            print(f"    ❌ Aisle not found in list")
            return False
    else:
        print(f"    ❌ Failed to read aisles: {response.status_code} - {response.text}")
        return False
    
    return True

def test_categories():
    """Test Categories operations"""
    print("\n🧪 Testing Categories Operations...")
    
    # Test READ
    print("  📖 Testing READ...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/categories')
    if response.status_code == 200:
        categories = response.json()
        print(f"    ✅ Categories retrieved: {len(categories)} categories")
    else:
        print(f"    ❌ Failed to read categories: {response.status_code} - {response.text}")
        return False
    
    return True

def test_locations():
    """Test Warehouse Locations operations"""
    print("\n🧪 Testing Warehouse Locations Operations...")
    
    # Test READ
    print("  📖 Testing READ...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/warehouse-locations')
    if response.status_code == 200:
        locations = response.json()
        print(f"    ✅ Locations retrieved: {len(locations)} locations")
    else:
        print(f"    ❌ Failed to read locations: {response.status_code} - {response.text}")
        return False
    
    # Test CREATE
    print("  📝 Testing CREATE...")
    location_data = {
        'location_code': 'A1-01-03',
        'aisle_id': 1,
        'aisle_name': 'Aisle A1',
        'rack_number': 1,
        'level': 1,
        'position': 3,
        'capacity': 100
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/advanced/warehouse-locations', json=location_data)
    if response.status_code == 201:
        print(f"    ✅ Location created successfully")
    else:
        print(f"    ❌ Failed to create location: {response.status_code} - {response.text}")
        return False
    
    return True

def main():
    """Run all inventory feature tests"""
    print("🚀 Starting Comprehensive Inventory Features Test")
    print("=" * 60)
    
    tests = [
        ("UoM CRUD", test_uom_crud),
        ("Zones CRUD", test_zones_crud),
        ("Aisles CRUD", test_aisles_crud),
        ("Categories", test_categories),
        ("Locations", test_locations)
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
    print("📊 Inventory Features Test Summary")
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
        print("🎉 ALL INVENTORY FEATURES ARE WORKING PERFECTLY!")
    else:
        print("⚠️ Some features need attention")
    
    return passed == total

if __name__ == "__main__":
    main()
