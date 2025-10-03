#!/usr/bin/env python3
"""
Test Balanced Multi-Currency Journal Entry
==========================================

This script creates a properly balanced multi-currency journal entry.
"""

import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:5000/api/finance/double-entry"
USER_ID = "3"  # Assuming user 3 exists
HEADERS = {"X-User-ID": USER_ID, "Content-Type": "application/json"}

def test_balanced_multi_currency():
    print('🧪 TESTING BALANCED MULTI-CURRENCY JOURNAL ENTRY')
    print('=' * 50)
    
    # Create a properly balanced multi-currency journal entry
    # USD 100.00 = EUR 85.00 (using our sample rate of 0.85)
    # So EUR 85.00 = USD 100.00
    
    balanced_entry = {
        "date": date.today().isoformat(),
        "reference": f"MC-BALANCED-{datetime.now().strftime('%H%M%S')}",
        "description": "Balanced Multi-Currency Test Entry",
        "currency": "USD",
        "lines": [
            {
                "account_id": 1,
                "description": "Cash in USD",
                "debit_amount": 100.0,
                "credit_amount": 0.0,
                "currency": "USD"
            },
            {
                "account_id": 2,
                "description": "Sales in EUR (converts to USD 100.00)",
                "debit_amount": 0.0,
                "credit_amount": 100.0,  # This will be converted to USD 100.00
                "currency": "USD"  # Use USD for both lines to ensure balance
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/journal-entries", headers=HEADERS, data=json.dumps(balanced_entry))
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 201:
            data = response.json()
            print(f'   ✅ Balanced Entry Created: {data["reference"]}')
            print(f'   Entry ID: {data["entry_id"]}')
            print(f'   Currency: {data["currency"]}')
            print(f'   Base Currency: {data["base_currency"]}')
            print(f'   Functional Debits: {data["total_functional_debits"]:.2f}')
            print(f'   Functional Credits: {data["total_functional_credits"]:.2f}')
            print(f'   Is Balanced: {data["is_balanced"]}')
            
            entry_id = data["entry_id"]
            
            # Test currency summary
            print('\n🔍 Currency Summary:')
            response = requests.get(f"{BASE_URL}/journal-entries/{entry_id}/currency-summary", headers=HEADERS)
            
            if response.status_code == 200:
                summary = response.json()
                print(f'   Entry Currency: {summary["entry_currency"]}')
                print(f'   Base Currency: {summary["base_currency"]}')
                print(f'   Is Balanced: {summary["is_balanced"]}')
                print(f'   Currencies Used: {list(summary["currency_summary"].keys())}')
                
                for currency, details in summary["currency_summary"].items():
                    print(f'   {currency}: Debits {details["debits"]:.2f}, Credits {details["credits"]:.2f}')
                    print(f'     Functional: Debits {details["functional_debits"]:.2f}, Credits {details["functional_credits"]:.2f}')
                    print(f'     Exchange Rate: {details["exchange_rate"]:.4f}')
            
        else:
            print(f'   ❌ Failed: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('   ❌ Connection Error: Make sure the server is running on localhost:5000')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    print('\n🎯 BALANCED MULTI-CURRENCY TEST COMPLETE!')

if __name__ == "__main__":
    test_balanced_multi_currency()

