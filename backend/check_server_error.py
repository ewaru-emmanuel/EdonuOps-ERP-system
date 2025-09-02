#!/usr/bin/env python3
"""
Check Server Error
Gets detailed error information from the products endpoint
"""

import urllib.request
import urllib.error
import json

BASE_URL = 'http://localhost:5000'

def check_products_endpoint_error():
    """Check the products endpoint error in detail"""
    try:
        print("Testing products endpoint...")
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products')
        response = urllib.request.urlopen(req)
        products = json.loads(response.read())
        print(f"✅ Products endpoint works! Found {len(products)} products")
        return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Error details: {error_body}")
        except:
            print("Could not read error details")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def check_database_connection():
    """Check if we can connect to the database directly"""
    try:
        import sqlite3
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        # Check if advanced_products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='advanced_products'")
        if cursor.fetchone():
            print("✅ advanced_products table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(advanced_products)")
            columns = cursor.fetchall()
            print("Table columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check if there are any products
            cursor.execute("SELECT COUNT(*) FROM advanced_products")
            count = cursor.fetchone()[0]
            print(f"✅ Found {count} products in database")
            
            # Check a sample product
            cursor.execute("SELECT id, name, sku, product_id FROM advanced_products LIMIT 1")
            product = cursor.fetchone()
            if product:
                print(f"Sample product: ID={product[0]}, Name='{product[1]}', SKU='{product[2]}', ProductID='{product[3]}'")
            
        else:
            print("❌ advanced_products table does not exist")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Server Error Details")
    print("=" * 40)
    
    check_database_connection()
    print()
    check_products_endpoint_error()

