#!/usr/bin/env python3
"""
Debug script for transaction API
"""

import requests
import json

def test_transaction_api():
    """Test the transaction API with detailed debugging"""
    
    url = "http://localhost:5000/api/finance/transactions/create"
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "1"
    }
    data = {
        "template_id": "simple_transaction",
        "amount": 100.0,
        "description": "Test transaction",
        "account_id": 1,
        "is_debit": True
    }
    
    print("Testing transaction API...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print("❌ Error!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == '__main__':
    test_transaction_api()

