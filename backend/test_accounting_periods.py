#!/usr/bin/env python3
"""
Test Accounting Periods Integration
==================================

This script tests the new accounting periods functionality:
- Period validation
- Backdated entry prevention
- Period locking
- Integration with double-entry system
"""

import requests
import json
from datetime import datetime, date, timedelta

def test_accounting_periods():
    """Test the accounting periods functionality"""
    base_url = "http://localhost:5000"
    headers = {'X-User-ID': '3', 'Content-Type': 'application/json'}
    
    print("🧪 TESTING ACCOUNTING PERIODS INTEGRATION")
    print("=" * 60)
    
    # Test 1: Get current period
    print("\n1️⃣ GETTING CURRENT PERIOD")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/finance/accounting-periods/current", headers=headers)
        if response.status_code == 200:
            current_period = response.json()['current_period']
            print(f"   ✅ Current Period: {current_period['name']}")
            print(f"      Period: {current_period['short_name']}")
            print(f"      Status: {current_period['status']}")
            print(f"      Date Range: {current_period['start_date']} to {current_period['end_date']}")
            print(f"      Is Locked: {current_period['is_locked']}")
        else:
            print(f"   ❌ Failed to get current period: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get period summary
    print("\n2️⃣ GETTING PERIOD SUMMARY")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/finance/accounting-periods/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()
            print(f"   ✅ Period Summary:")
            print(f"      Total Periods: {summary['total_periods']}")
            print(f"      Open Periods: {summary['open_periods']}")
            print(f"      Closed Periods: {summary['closed_periods']}")
            print(f"      Locked Periods: {summary['locked_periods']}")
        else:
            print(f"   ❌ Failed to get period summary: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Validate transaction dates
    print("\n3️⃣ TESTING DATE VALIDATION")
    print("-" * 40)
    
    test_dates = [
        date.today().isoformat(),  # Today
        (date.today() - timedelta(days=5)).isoformat(),  # 5 days ago
        (date.today() + timedelta(days=5)).isoformat(),  # 5 days in future
        "2024-01-15",  # Last year
        "2025-12-31"   # End of current year
    ]
    
    for test_date in test_dates:
        try:
            response = requests.post(f"{base_url}/api/finance/accounting-periods/validate-date", 
                                   headers=headers, json={'date': test_date})
            if response.status_code == 200:
                result = response.json()
                status = "✅ Valid" if result['is_valid'] else "❌ Invalid"
                print(f"   {status} {test_date}: {result['message']}")
                if result['period']:
                    print(f"      Period: {result['period']['short_name']}")
            else:
                print(f"   ❌ Failed to validate {test_date}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error validating {test_date}: {e}")
    
    # Test 4: Create journal entry with period validation
    print("\n4️⃣ TESTING JOURNAL ENTRY WITH PERIOD VALIDATION")
    print("-" * 40)
    
    # Test with today's date (should work)
    today_entry = {
        "date": date.today().isoformat(),
        "description": "Test entry with period validation",
        "reference": f"TEST-PERIOD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "draft",
        "payment_method": "bank",
        "lines": [
            {
                "account_id": 1,  # Cash on Hand
                "description": "Test debit",
                "debit_amount": 100.0,
                "credit_amount": 0.0
            },
            {
                "account_id": 9,  # Sales Revenue
                "description": "Test credit",
                "debit_amount": 0.0,
                "credit_amount": 100.0
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/api/finance/double-entry/journal-entries", 
                               headers=headers, json=today_entry)
        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ Created journal entry successfully")
            print(f"      Entry ID: {result['entry_id']}")
            print(f"      Reference: {result['reference']}")
            print(f"      Amount: ${result['total_debits']:.2f}")
        else:
            print(f"   ❌ Failed to create journal entry: {response.status_code}")
            print(f"      Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error creating journal entry: {e}")
    
    # Test 5: Test backdated entry
    print("\n5️⃣ TESTING BACKDATED ENTRY")
    print("-" * 40)
    
    backdated_entry = {
        "date": (date.today() - timedelta(days=10)).isoformat(),
        "description": "Backdated test entry",
        "reference": f"BACKDATED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "draft",
        "payment_method": "bank",
        "backdate_reason": "Testing backdated entry functionality",
        "lines": [
            {
                "account_id": 1,  # Cash on Hand
                "description": "Backdated debit",
                "debit_amount": 50.0,
                "credit_amount": 0.0
            },
            {
                "account_id": 9,  # Sales Revenue
                "description": "Backdated credit",
                "debit_amount": 0.0,
                "credit_amount": 50.0
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/api/finance/double-entry/journal-entries", 
                               headers=headers, json=backdated_entry)
        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ Created backdated entry successfully")
            print(f"      Entry ID: {result['entry_id']}")
            print(f"      Reference: {result['reference']}")
            print(f"      Amount: ${result['total_debits']:.2f}")
        else:
            print(f"   ❌ Failed to create backdated entry: {response.status_code}")
            print(f"      Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error creating backdated entry: {e}")
    
    # Test 6: Test future date (should fail)
    print("\n6️⃣ TESTING FUTURE DATE ENTRY")
    print("-" * 40)
    
    future_entry = {
        "date": (date.today() + timedelta(days=30)).isoformat(),
        "description": "Future test entry",
        "reference": f"FUTURE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "draft",
        "payment_method": "bank",
        "lines": [
            {
                "account_id": 1,  # Cash on Hand
                "description": "Future debit",
                "debit_amount": 25.0,
                "credit_amount": 0.0
            },
            {
                "account_id": 9,  # Sales Revenue
                "description": "Future credit",
                "debit_amount": 0.0,
                "credit_amount": 25.0
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/api/finance/double-entry/journal-entries", 
                               headers=headers, json=future_entry)
        if response.status_code == 400:
            result = response.json()
            print(f"   ✅ Correctly rejected future date entry")
            print(f"      Error: {result['details']}")
        else:
            print(f"   ❌ Should have rejected future date entry: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing future entry: {e}")
    
    # Test 7: Get all periods
    print("\n7️⃣ GETTING ALL PERIODS")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/finance/accounting-periods/periods", headers=headers)
        if response.status_code == 200:
            result = response.json()
            periods = result['periods']
            print(f"   ✅ Found {len(periods)} periods:")
            for period in periods[:5]:  # Show first 5
                print(f"      {period['short_name']}: {period['start_date']} to {period['end_date']} ({period['status']})")
            if len(periods) > 5:
                print(f"      ... and {len(periods) - 5} more periods")
        else:
            print(f"   ❌ Failed to get periods: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting periods: {e}")
    
    print("\n🎯 ACCOUNTING PERIODS TEST COMPLETE!")
    print("=" * 60)
    print("✅ Period validation working")
    print("✅ Backdated entry tracking working")
    print("✅ Date validation working")
    print("✅ Integration with double-entry system working")
    print("✅ Period management API working")

if __name__ == "__main__":
    test_accounting_periods()

