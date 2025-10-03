#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import json

def test_create_transaction():
    """Test creating a transaction via API"""
    try:
        url = "http://localhost:5000/api/finance/transactions/create"
        headers = {
            'X-User-ID': '3',
            'Content-Type': 'application/json'
        }
        data = {
            'template_id': 'cash_sales',
            'amount': 50.0,
            'description': 'API test transaction'
        }
        
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Transaction created successfully!")
            print(f"   Entry ID: {result['transaction']['entry_id']}")
            print(f"   Reference: {result['transaction']['reference']}")
        else:
            print("❌ Transaction creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_create_transaction()

