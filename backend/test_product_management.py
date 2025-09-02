#!/usr/bin/env python3
"""
Test script for Product Management functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_product_management_endpoints():
    """Test all product management endpoints"""
    
    print("🧪 Testing Product Management Endpoints...")
    
    # Test 1: Get Products
    print("\n1. Testing Get Products...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/advanced/products")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Get Products: SUCCESS - Found {len(products)} products")
            if products:
                print(f"   Sample product: {products[0].get('name', 'Unknown')}")
        else:
            print(f"❌ Get Products: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Get Products: ERROR - {e}")
    
    # Test 2: Get Categories
    print("\n2. Testing Get Categories...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/advanced/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Get Categories: SUCCESS - Found {len(categories)} categories")
        else:
            print(f"❌ Get Categories: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Get Categories: ERROR - {e}")
    
    # Test 3: Get UoM
    print("\n3. Testing Get UoM...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/advanced/uom")
        if response.status_code == 200:
            uoms = response.json()
            print(f"✅ Get UoM: SUCCESS - Found {len(uoms)} units of measure")
        else:
            print(f"❌ Get UoM: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Get UoM: ERROR - {e}")
    
    # Test 4: Create Product
    print("\n4. Testing Create Product...")
    try:
        product_data = {
            "name": "Test Product",
            "sku": "TEST001",
            "description": "A test product for API testing",
            "category_id": 1,
            "base_uom_id": 1,
            "status": "active",
            "track_serial_numbers": False,
            "track_lots": False,
            "track_expiry": False,
            "cost_method": "standard",
            "standard_cost": 10.00,
            "current_cost": 10.00,
            "min_stock": 10,
            "max_stock": 100,
            "reorder_point": 20
        }
        
        response = requests.post(
            f"{BASE_URL}/api/inventory/advanced/products",
            json=product_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Create Product: SUCCESS")
            print(f"   Product ID: {result.get('id')}")
            product_id = result.get('id')
        else:
            print(f"❌ Create Product: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            product_id = None
    except Exception as e:
        print(f"❌ Create Product: ERROR - {e}")
        product_id = None
    
    # Test 5: Update Product (if we have a product_id)
    if product_id:
        print(f"\n5. Testing Update Product (ID: {product_id})...")
        try:
            update_data = {
                "name": "Updated Test Product",
                "description": "Updated description",
                "current_cost": 15.00,
                "min_stock": 15
            }
            
            response = requests.put(
                f"{BASE_URL}/api/inventory/advanced/products/{product_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Update Product: SUCCESS")
            else:
                print(f"❌ Update Product: FAILED - Status {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Update Product: ERROR - {e}")
    
    # Test 6: Delete Product (if we have a product_id)
    if product_id:
        print(f"\n6. Testing Delete Product (ID: {product_id})...")
        try:
            response = requests.delete(
                f"{BASE_URL}/api/inventory/advanced/products/{product_id}",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Delete Product: SUCCESS")
            else:
                print(f"❌ Delete Product: FAILED - Status {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Delete Product: ERROR - {e}")
    
    print("\n🎉 Product Management Tests Complete!")

if __name__ == "__main__":
    test_product_management_endpoints()
