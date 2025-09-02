#!/usr/bin/env python3
"""
Test Database Operations for Products
Verifies that CRUD operations are properly saving to and reading from the database
"""

import requests
import time
import sqlite3
import os

BASE_URL = 'http://localhost:5000'
DB_PATH = 'edonuops.db'  # Adjust path as needed

def test_database_operations():
    """Test that database operations are working correctly"""
    print("🧪 Testing Database Operations...")
    
    # Test CREATE
    print("  📝 Testing CREATE...")
    product_data = {
        'name': f'Test Product {int(time.time())}',
        'sku': f'TEST{int(time.time())}',
        'description': 'Test product for database verification',
        'category_id': 1,
        'base_uom_id': 1,
        'status': 'active',
        'track_serial_numbers': False,
        'track_lots': False,
        'track_expiry': False
    }
    
    response = requests.post(f'{BASE_URL}/api/inventory/advanced/products', json=product_data)
    if response.status_code == 201:
        product_id = response.json().get('id')
        print(f"    ✅ Product created with ID: {product_id}")
    else:
        print(f"    ❌ Failed to create product: {response.status_code} - {response.text}")
        return False
    
    # Test READ from API
    print("  📖 Testing READ from API...")
    response = requests.get(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
    if response.status_code == 200:
        product = response.json()
        print(f"    ✅ Product retrieved from API: {product.get('name')}")
    else:
        print(f"    ❌ Failed to retrieve product from API: {response.status_code} - {response.text}")
        return False
    
    # Test READ from Database directly
    print("  📖 Testing READ from Database...")
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, sku FROM advanced_products WHERE id = ?", (product_id,))
            db_product = cursor.fetchone()
            conn.close()
            
            if db_product:
                print(f"    ✅ Product found in database: {db_product[1]} (SKU: {db_product[2]})")
            else:
                print(f"    ❌ Product not found in database")
                return False
        except Exception as e:
            print(f"    ❌ Database error: {e}")
            return False
    else:
        print(f"    ⚠️ Database file not found at {DB_PATH}")
    
    # Test UPDATE
    print("  ✏️ Testing UPDATE...")
    update_data = {
        'name': f'Updated Test Product {int(time.time())}',
        'description': 'Updated test product description'
    }
    
    response = requests.put(f'{BASE_URL}/api/inventory/advanced/products/{product_id}', json=update_data)
    if response.status_code == 200:
        print(f"    ✅ Product updated successfully")
    else:
        print(f"    ❌ Failed to update product: {response.status_code} - {response.text}")
        return False
    
    # Verify update in database
    print("  📖 Verifying update in Database...")
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM advanced_products WHERE id = ?", (product_id,))
            db_product = cursor.fetchone()
            conn.close()
            
            if db_product and 'Updated' in db_product[0]:
                print(f"    ✅ Update verified in database: {db_product[0]}")
            else:
                print(f"    ❌ Update not found in database")
                return False
        except Exception as e:
            print(f"    ❌ Database error: {e}")
            return False
    
    # Test DELETE
    print("  🗑️ Testing DELETE...")
    response = requests.delete(f'{BASE_URL}/api/inventory/advanced/products/{product_id}')
    if response.status_code == 200:
        print(f"    ✅ Product deleted successfully")
    else:
        print(f"    ❌ Failed to delete product: {response.status_code} - {response.text}")
        return False
    
    # Verify deletion in database
    print("  📖 Verifying deletion in Database...")
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM advanced_products WHERE id = ? AND is_active = 1", (product_id,))
            db_product = cursor.fetchone()
            conn.close()
            
            if not db_product:
                print(f"    ✅ Deletion verified in database (product marked as inactive)")
            else:
                print(f"    ❌ Product still active in database")
                return False
        except Exception as e:
            print(f"    ❌ Database error: {e}")
            return False
    
    print("🎉 Database operations test completed successfully!")
    return True

def check_database_schema():
    """Check if the database schema is correct"""
    print("\n🔍 Checking Database Schema...")
    
    if not os.path.exists(DB_PATH):
        print(f"    ❌ Database file not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if advanced_products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='advanced_products'")
        if cursor.fetchone():
            print("    ✅ advanced_products table exists")
        else:
            print("    ❌ advanced_products table not found")
            return False
        
        # Check table structure
        cursor.execute("PRAGMA table_info(advanced_products)")
        columns = cursor.fetchall()
        required_columns = ['id', 'name', 'sku', 'description', 'category_id', 'base_uom_id', 'status', 'is_active']
        
        existing_columns = [col[1] for col in columns]
        missing_columns = [col for col in required_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"    ❌ Missing columns: {missing_columns}")
            return False
        else:
            print("    ✅ All required columns exist")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"    ❌ Database schema check error: {e}")
        return False

def main():
    """Run database tests"""
    print("🚀 Starting Database Operations Test")
    print("=" * 60)
    
    # Check database schema first
    if not check_database_schema():
        print("❌ Database schema check failed")
        return False
    
    # Test database operations
    if test_database_operations():
        print("\n🎉 ALL DATABASE OPERATIONS ARE WORKING CORRECTLY!")
        return True
    else:
        print("\n❌ Database operations test failed")
        return False

if __name__ == "__main__":
    main()
