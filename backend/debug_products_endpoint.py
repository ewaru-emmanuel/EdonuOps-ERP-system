#!/usr/bin/env python3
"""
Debug Products Endpoint
Tests the products endpoint to see what's causing the 500 error
"""

import urllib.request
import json

BASE_URL = 'http://localhost:5000'

def test_products_endpoint():
    """Test the products endpoint"""
    try:
        print("Testing products endpoint...")
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/products')
        response = urllib.request.urlopen(req)
        products = json.loads(response.read())
        print(f"✅ Products endpoint works! Found {len(products)} products")
        return True
    except Exception as e:
        print(f"❌ Products endpoint failed: {e}")
        return False

def test_categories_endpoint():
    """Test the categories endpoint"""
    try:
        print("Testing categories endpoint...")
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/categories')
        response = urllib.request.urlopen(req)
        categories = json.loads(response.read())
        print(f"✅ Categories endpoint works! Found {len(categories)} categories")
        return True
    except Exception as e:
        print(f"❌ Categories endpoint failed: {e}")
        return False

def test_uom_endpoint():
    """Test the UoM endpoint"""
    try:
        print("Testing UoM endpoint...")
        req = urllib.request.Request(f'{BASE_URL}/api/inventory/advanced/uom')
        response = urllib.request.urlopen(req)
        uoms = json.loads(response.read())
        print(f"✅ UoM endpoint works! Found {len(uoms)} UoMs")
        return True
    except Exception as e:
        print(f"❌ UoM endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debugging Inventory Endpoints")
    print("=" * 40)
    
    test_categories_endpoint()
    test_uom_endpoint()
    test_products_endpoint()

