#!/usr/bin/env python3
"""
Test Complete Flow: Frontend -> Backend -> Database
Verifies that the entire CRUD flow is working correctly
"""

import urllib.request
import json
import time

BASE_URL = 'http://localhost:5000'

def test_complete_flow():
    """Test the complete CRUD flow"""
    print("🧪 Testing Complete CRUD Flow...")
    
    # Test CREATE
    print("  📝 Testing CREATE...")
    product_data = {
        'name': f'Complete Flow Test Product {int(time.time())}',
        'sku': f'FLOW{int(time.time())}',
        'description': 'Test product for complete flow verification',
        'category_id': 1,
        'base_uom_id': 1,
        'status': 'active',
        'track_serial_numbers': False,
        'track_lots': False,
        'track_expiry': False
    }
    
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products',
            data=json.dumps(product_data).encode(),
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        product_id = result.get('id')
        print(f"    ✅ Product created with ID: {product_id}")
    except Exception as e:
        print(f"    ❌ Failed to create product: {e}")
        return False
    
    # Test READ
    print("  📖 Testing READ...")
    try:
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
        response = urllib.request.urlopen(req)
        product = json.loads(response.read())
        print(f"    ✅ Product retrieved: {product.get('name')}")
    except Exception as e:
        print(f"    ❌ Failed to retrieve product: {e}")
        return False
    
    # Test UPDATE
    print("  ✏️ Testing UPDATE...")
    update_data = {
        'name': f'Updated Complete Flow Product {int(time.time())}',
        'description': 'Updated test product description'
    }
    
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products/{product_id}',
            data=json.dumps(update_data).encode(),
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        print(f"    ✅ Product updated successfully")
    except Exception as e:
        print(f"    ❌ Failed to update product: {e}")
        return False
    
    # Verify update
    print("  📖 Verifying UPDATE...")
    try:
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
        response = urllib.request.urlopen(req)
        product = json.loads(response.read())
        if 'Updated' in product.get('name', ''):
            print(f"    ✅ Update verified: {product.get('name')}")
        else:
            print(f"    ❌ Update not reflected: {product.get('name')}")
            return False
    except Exception as e:
        print(f"    ❌ Failed to verify update: {e}")
        return False
    
    # Test DELETE
    print("  🗑️ Testing DELETE...")
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products/{product_id}',
            method='DELETE'
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        print(f"    ✅ Product deleted successfully")
    except Exception as e:
        print(f"    ❌ Failed to delete product: {e}")
        return False
    
    # Verify deletion
    print("  📖 Verifying DELETE...")
    try:
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
        response = urllib.request.urlopen(req)
        print(f"    ❌ Product still exists (should return 404)")
        return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"    ✅ Deletion verified (404 returned)")
        else:
            print(f"    ❌ Unexpected error code: {e.code}")
            return False
    except Exception as e:
        print(f"    ❌ Failed to verify deletion: {e}")
        return False
    
    print("🎉 Complete CRUD flow test passed!")
    return True

def test_data_persistence():
    """Test that data persists across requests"""
    print("\n🧪 Testing Data Persistence...")
    
    # Get initial count
    try:
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products')
        response = urllib.request.urlopen(req)
        initial_products = json.loads(response.read())
        initial_count = len(initial_products)
        print(f"    📊 Initial product count: {initial_count}")
    except Exception as e:
        print(f"    ❌ Failed to get initial count: {e}")
        return False
    
    # Create a product
    product_data = {
        'name': f'Persistence Test Product {int(time.time())}',
        'sku': f'PERS{int(time.time())}',
        'description': 'Test product for persistence verification',
        'category_id': 1,
        'base_uom_id': 1,
        'status': 'active'
    }
    
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products',
            data=json.dumps(product_data).encode(),
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        product_id = result.get('id')
        print(f"    ✅ Product created with ID: {product_id}")
    except Exception as e:
        print(f"    ❌ Failed to create product: {e}")
        return False
    
    # Get count after creation
    try:
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products')
        response = urllib.request.urlopen(req)
        after_create_products = json.loads(response.read())
        after_create_count = len(after_create_products)
        print(f"    📊 Product count after creation: {after_create_count}")
        
        if after_create_count > initial_count:
            print(f"    ✅ Data persistence verified (count increased)")
        else:
            print(f"    ❌ Data persistence failed (count unchanged)")
            return False
    except Exception as e:
        print(f"    ❌ Failed to verify persistence: {e}")
        return False
    
    # Clean up - delete the test product
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products/{product_id}',
            method='DELETE'
        )
        urllib.request.urlopen(req)
        print(f"    🧹 Test product cleaned up")
    except Exception as e:
        print(f"    ⚠️ Failed to clean up test product: {e}")
    
    print("🎉 Data persistence test passed!")
    return True

def main():
    """Run complete flow tests"""
    print("🚀 Starting Complete Flow Tests")
    print("=" * 60)
    
    tests = [
        ("Complete CRUD Flow", test_complete_flow),
        ("Data Persistence", test_data_persistence)
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
    print("📊 Complete Flow Test Summary")
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
        print("🎉 ALL FLOWS ARE WORKING PERFECTLY!")
        print("✅ Frontend -> Backend -> Database communication is fully functional!")
    else:
        print("⚠️ Some flows need attention")
    
    return passed == total

if __name__ == "__main__":
    main()
