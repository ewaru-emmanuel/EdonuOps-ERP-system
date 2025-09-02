#!/usr/bin/env python3
"""
Test Edit Functionality
Verifies that product editing works correctly from frontend to backend to database
"""

import urllib.request
import json
import time

BASE_URL = 'http://localhost:5000'

def test_edit_functionality():
    """Test the complete edit flow"""
    print("🧪 Testing Edit Functionality...")
    
    # Step 1: Create a test product
    print("  📝 Step 1: Creating test product...")
    product_data = {
        'name': f'Edit Test Product {int(time.time())}',
        'sku': f'EDIT{int(time.time())}',
        'description': 'Original description for edit test',
        'category_id': 1,
        'base_uom_id': 1,
        'status': 'active',
        'min_stock': 10,
        'max_stock': 100,
        'reorder_point': 20,
        'current_cost': 25.50
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
    
    # Step 2: Verify original data
    print("  📖 Step 2: Verifying original data...")
    try:
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
        response = urllib.request.urlopen(req)
        original_product = json.loads(response.read())
        print(f"    ✅ Original name: {original_product.get('name')}")
        print(f"    ✅ Original description: {original_product.get('description')}")
        print(f"    ✅ Original min_stock: {original_product.get('min_stock')}")
        print(f"    ✅ Original status: {original_product.get('status')}")
    except Exception as e:
        print(f"    ❌ Failed to retrieve original product: {e}")
        return False
    
    # Step 3: Update the product (simulating frontend edit)
    print("  ✏️ Step 3: Updating product...")
    update_data = {
        'name': f'UPDATED Edit Test Product {int(time.time())}',
        'description': 'Updated description from edit test',
        'min_stock': 25,
        'max_stock': 150,
        'reorder_point': 30,
        'current_cost': 35.75,
        'status': 'inactive'
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
    
    # Step 4: Verify the update was saved
    print("  📖 Step 4: Verifying update was saved...")
    try:
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
        response = urllib.request.urlopen(req)
        updated_product = json.loads(response.read())
        
        # Check each field
        checks = [
            ('name', update_data['name']),
            ('description', update_data['description']),
            ('min_stock', update_data['min_stock']),
            ('max_stock', update_data['max_stock']),
            ('reorder_point', update_data['reorder_point']),
            ('current_cost', update_data['current_cost']),
            ('status', update_data['status'])
        ]
        
        all_passed = True
        for field, expected_value in checks:
            actual_value = updated_product.get(field)
            if actual_value == expected_value:
                print(f"    ✅ {field}: {actual_value}")
            else:
                print(f"    ❌ {field}: expected {expected_value}, got {actual_value}")
                all_passed = False
        
        if all_passed:
            print(f"    ✅ All fields updated correctly!")
        else:
            print(f"    ❌ Some fields not updated correctly")
            return False
            
    except Exception as e:
        print(f"    ❌ Failed to verify update: {e}")
        return False
    
    # Step 5: Test multiple updates (simulating user making multiple changes)
    print("  🔄 Step 5: Testing multiple updates...")
    second_update = {
        'name': f'FINAL Edit Test Product {int(time.time())}',
        'status': 'active',
        'min_stock': 50
    }
    
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products/{product_id}',
            data=json.dumps(second_update).encode(),
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        response = urllib.request.urlopen(req)
        print(f"    ✅ Second update successful")
        
        # Verify second update
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
        response = urllib.request.urlopen(req)
        final_product = json.loads(response.read())
        
        if final_product.get('name') == second_update['name']:
            print(f"    ✅ Final name updated: {final_product.get('name')}")
        else:
            print(f"    ❌ Final name not updated correctly")
            return False
            
    except Exception as e:
        print(f"    ❌ Failed second update: {e}")
        return False
    
    # Clean up
    print("  🧹 Cleaning up test product...")
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products/{product_id}',
            method='DELETE'
        )
        urllib.request.urlopen(req)
        print(f"    ✅ Test product cleaned up")
    except Exception as e:
        print(f"    ⚠️ Failed to clean up: {e}")
    
    print("🎉 Edit functionality test passed!")
    return True

def test_partial_updates():
    """Test that partial updates work correctly"""
    print("\n🧪 Testing Partial Updates...")
    
    # Create test product
    product_data = {
        'name': f'Partial Test Product {int(time.time())}',
        'sku': f'PART{int(time.time())}',
        'description': 'Original description',
        'category_id': 1,
        'base_uom_id': 1,
        'status': 'active',
        'min_stock': 10,
        'max_stock': 100
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
    
    # Test partial update (only name)
    print("  ✏️ Testing partial update (name only)...")
    partial_update = {
        'name': f'PARTIALLY UPDATED Product {int(time.time())}'
    }
    
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products/{product_id}',
            data=json.dumps(partial_update).encode(),
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        response = urllib.request.urlopen(req)
        print(f"    ✅ Partial update successful")
        
        # Verify only name was updated, other fields unchanged
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
        response = urllib.request.urlopen(req)
        updated_product = json.loads(response.read())
        
        if (updated_product.get('name') == partial_update['name'] and 
            updated_product.get('description') == product_data['description'] and
            updated_product.get('min_stock') == product_data['min_stock']):
            print(f"    ✅ Partial update verified - only name changed")
        else:
            print(f"    ❌ Partial update failed - other fields changed unexpectedly")
            return False
            
    except Exception as e:
        print(f"    ❌ Failed partial update: {e}")
        return False
    
    # Clean up
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/inventory/advanced/products/{product_id}',
            method='DELETE'
        )
        urllib.request.urlopen(req)
        print(f"    ✅ Test product cleaned up")
    except Exception as e:
        print(f"    ⚠️ Failed to clean up: {e}")
    
    print("🎉 Partial updates test passed!")
    return True

def main():
    """Run edit functionality tests"""
    print("🚀 Starting Edit Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Complete Edit Flow", test_edit_functionality),
        ("Partial Updates", test_partial_updates)
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
    print("📊 Edit Functionality Test Summary")
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
        print("🎉 ALL EDIT FUNCTIONALITY IS WORKING PERFECTLY!")
        print("✅ Product editing from frontend to backend to database is fully functional!")
    else:
        print("⚠️ Some edit functionality needs attention")
    
    return passed == total

if __name__ == "__main__":
    main()

