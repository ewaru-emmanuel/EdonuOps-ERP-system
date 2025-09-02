#!/usr/bin/env python3
"""
Simple Test
Quick test to check current status
"""

import urllib.request
import json

def test_products():
    """Test products endpoint"""
    try:
        req = urllib.request.Request('http://localhost:5000/api/inventory/advanced/products')
        response = urllib.request.urlopen(req)
        products = json.loads(response.read())
        print(f"✅ Products endpoint works! Found {len(products)} products")
        
        # Check if any product has product_id
        for product in products:
            if 'product_id' in product:
                print(f"✅ Found product with product_id: {product['product_id']}")
                return True
        
        print("⚠️ No products have product_id field")
        return True
        
    except Exception as e:
        print(f"❌ Products endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Test")
    print("=" * 20)
    test_products()

