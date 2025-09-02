#!/usr/bin/env python3
"""
Test Delete Functionality for Inventory Products
"""

import requests
import time

BASE_URL = 'http://localhost:5000'

def test_delete_functionality():
    """Test the complete delete workflow"""
    print("🧪 Testing Delete Functionality...")
    
    # Step 1: Create a test product
    print("  📝 Creating test product...")
    product_data = {
        'name': 'Test Delete Product',
        'sku': f'DEL{int(time.time())}',
        'category_id': 1,
        'description': 'Test product for deletion',
        'base_uom_id': 1,
        'current_cost': 25.00,
        'min_stock': 5,
        'max_stock': 50,
        'reorder_point': 10
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/advanced/products', json=product_data)
    if response.status_code == 201:
        product_id = response.json().get('id')
        print(f"    ✅ Product created with ID: {product_id}")
    else:
        print(f"    ❌ Failed to create product: {response.status_code} - {response.text}")
        return False
    
    # Step 2: Verify the product exists
    print("  📖 Verifying product exists...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
    if response.status_code == 200:
        product = response.json()
        print(f"    ✅ Product retrieved: {product.get('name')}")
    else:
        print(f"    ❌ Failed to retrieve product: {response.status_code} - {response.text}")
        return False
    
    # Step 3: Delete the product
    print("  🗑️ Deleting product...")
    response = requests.delete(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
    if response.status_code == 200:
        print(f"    ✅ Product deleted successfully")
    else:
        print(f"    ❌ Failed to delete product: {response.status_code} - {response.text}")
        return False
    
    # Step 4: Verify the product is deleted (should return 404)
    print("  🔍 Verifying product is deleted...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
    if response.status_code == 404:
        print(f"    ✅ Product successfully deleted (404 returned)")
    else:
        print(f"    ❌ Product still exists: {response.status_code} - {response.text}")
        return False
    
    print("🎉 Delete functionality test completed successfully!")
    return True

if __name__ == "__main__":
    test_delete_functionality()
