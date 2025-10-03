#!/usr/bin/env python3
"""
Test Currency Conversion Only
============================

This script tests just the currency conversion endpoint.
"""

import requests
import json

BASE_URL = "http://localhost:5000/api/finance/double-entry"
USER_ID = "3"  # Assuming user 3 exists
HEADERS = {"X-User-ID": USER_ID, "Content-Type": "application/json"}

def test_currency_conversion():
    print('🧪 TESTING CURRENCY CONVERSION ENDPOINT')
    print('=' * 50)
    
    # Test currency conversion
    conversion_data = {
        "amount": 100.0,
        "from_currency": "USD",
        "to_currency": "EUR"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/convert-currency", headers=HEADERS, data=json.dumps(conversion_data))
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            conversion = response.json()
            print(f'   ✅ Currency Conversion: {conversion["original_amount"]} {conversion["from_currency"]} = {conversion["converted_amount"]:.2f} {conversion["to_currency"]}')
            print(f'   Exchange Rate: {conversion["exchange_rate"]:.4f}')
            print(f'   Success: {conversion["success"]}')
        else:
            print(f'   ❌ Failed: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('   ❌ Connection Error: Make sure the server is running on localhost:5000')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    print('\n🎯 CURRENCY CONVERSION TEST COMPLETE!')

if __name__ == "__main__":
    test_currency_conversion()

