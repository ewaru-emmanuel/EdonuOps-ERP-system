#!/usr/bin/env python3
"""
Test script for the new double-entry API
"""

import requests
import json

def test_double_entry_api():
    """Test the new double-entry API endpoints"""
    base_url = "http://localhost:5000/api/finance/double-entry"
    headers = {'X-User-ID': '3'}
    
    print("🧪 Testing Double-Entry API")
    print("=" * 40)
    
    # Test 1: Get journal entries
    print("\n1️⃣ Testing GET /journal-entries")
    try:
        response = requests.get(f"{base_url}/journal-entries", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} journal entries")
            
            if data:
                entry = data[0]
                print(f"   📋 Sample Entry:")
                print(f"      ID: {entry['id']}")
                print(f"      Description: {entry['description']}")
                print(f"      Total Debits: ${entry['total_debits']}")
                print(f"      Total Credits: ${entry['total_credits']}")
                print(f"      Is Balanced: {entry['is_balanced']}")
                print(f"      Lines: {len(entry['lines'])}")
                
                for line in entry['lines']:
                    print(f"        Line: {line['account_name']} - Debit: ${line['debit_amount']}, Credit: ${line['credit_amount']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Get accounts
    print("\n2️⃣ Testing GET /accounts")
    try:
        response = requests.get(f"{base_url}/accounts", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} accounts")
            
            if data:
                account = data[0]
                print(f"   📊 Sample Account:")
                print(f"      Code: {account['code']}")
                print(f"      Name: {account['name']}")
                print(f"      Type: {account['type']}")
                print(f"      Balance: ${account['balance']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Get trial balance
    print("\n3️⃣ Testing GET /trial-balance")
    try:
        response = requests.get(f"{base_url}/trial-balance", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Trial Balance Generated")
            print(f"      Total Debits: ${data['total_debits']}")
            print(f"      Total Credits: ${data['total_credits']}")
            print(f"      Is Balanced: {data['is_balanced']}")
            print(f"      Accounts with Balances: {len(data['trial_balance'])}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n🎯 Double-Entry API Test Complete!")

if __name__ == "__main__":
    test_double_entry_api()

