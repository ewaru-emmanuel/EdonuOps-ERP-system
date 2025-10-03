#!/usr/bin/env python3
"""
Test Simple Multi-Currency Journal Entry
========================================

This script creates a simple multi-currency journal entry for testing.
"""

import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:5000/api/finance/double-entry"
USER_ID = "3"  # Assuming user 3 exists
HEADERS = {"X-User-ID": USER_ID, "Content-Type": "application/json"}

def test_simple_multi_currency():
    print('🧪 TESTING SIMPLE MULTI-CURRENCY JOURNAL ENTRY')
    print('=' * 50)
    
    # Create a simple multi-currency journal entry
    simple_entry = {
        "date": date.today().isoformat(),
        "reference": f"MC-SIMPLE-{datetime.now().strftime('%H%M%S')}",
        "description": "Simple Multi-Currency Test Entry",
        "currency": "USD",
        "lines": [
            {
                "account_id": 1,
                "description": "Cash in USD",
                "debit_amount": 100.0,
                "credit_amount": 0.0
            },
            {
                "account_id": 2,
                "description": "Sales in USD",
                "debit_amount": 0.0,
                "credit_amount": 100.0
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/journal-entries", headers=HEADERS, data=json.dumps(simple_entry))
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 201:
            data = response.json()
            print(f'   ✅ Simple Entry Created: {data["reference"]}')
            print(f'   Entry ID: {data["entry_id"]}')
            print(f'   Currency: {data["currency"]}')
            print(f'   Base Currency: {data["base_currency"]}')
            print(f'   Functional Debits: {data["total_functional_debits"]:.2f}')
            print(f'   Functional Credits: {data["total_functional_credits"]:.2f}')
            print(f'   Is Balanced: {data["is_balanced"]}')
            
        else:
            print(f'   ❌ Failed: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('   ❌ Connection Error: Make sure the server is running on localhost:5000')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    print('\n🎯 SIMPLE MULTI-CURRENCY TEST COMPLETE!')

if __name__ == "__main__":
    test_simple_multi_currency()

