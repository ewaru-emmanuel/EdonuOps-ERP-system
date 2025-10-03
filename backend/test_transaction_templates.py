#!/usr/bin/env python3
"""
Test script for Transaction Templates API
"""

import requests
import json

def test_transaction_templates():
    """Test the transaction templates API"""
    base_url = "http://localhost:5000/api/finance/transactions"
    headers = {'X-User-ID': '3', 'Content-Type': 'application/json'}
    
    print("🧪 Testing Transaction Templates API")
    print("=" * 50)
    
    # Test 1: Get all templates
    print("\n1️⃣ Testing GET /templates")
    try:
        response = requests.get(f"{base_url}/templates", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data['templates'])} templates")
            
            for template_id, template in data['templates'].items():
                print(f"      📋 {template['name']}: {template['description']}")
                print(f"         Required fields: {', '.join(template['required_fields'])}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Get examples
    print("\n2️⃣ Testing GET /examples")
    try:
        response = requests.get(f"{base_url}/examples", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data['examples'])} examples")
            
            for template_id, example in data['examples'].items():
                print(f"      📋 {example['name']}:")
                print(f"         Example: {example['example']}")
                print(f"         Creates: {example['explanation']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Validate a transaction
    print("\n3️⃣ Testing POST /validate (Cash Sales)")
    try:
        validate_data = {
            "template_id": "cash_sales",
            "amount": 250.00,
            "description": "Test cash sale validation"
        }
        
        response = requests.post(f"{base_url}/validate", 
                               headers=headers, 
                               json=validate_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['valid']:
                print(f"   ✅ Transaction is valid")
                preview = data['preview']
                print(f"      Description: {preview['description']}")
                print(f"      Payment Method: {preview['payment_method']}")
                print(f"      Total Debits: ${preview['total_debits']}")
                print(f"      Total Credits: ${preview['total_credits']}")
                print(f"      Is Balanced: {preview['is_balanced']}")
                print(f"      Lines: {len(preview['lines'])}")
                
                for line in preview['lines']:
                    print(f"        Line: {line['account_name']} - Debit: ${line['debit_amount']}, Credit: ${line['credit_amount']}")
            else:
                print(f"   ❌ Transaction is invalid: {data['error']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Create a real transaction
    print("\n4️⃣ Testing POST /create (Cash Sales)")
    try:
        create_data = {
            "template_id": "cash_sales",
            "amount": 150.00,
            "description": "Test cash sale transaction"
        }
        
        response = requests.post(f"{base_url}/create", 
                               headers=headers, 
                               json=create_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Transaction created successfully")
            transaction = data['transaction']
            print(f"      Entry ID: {transaction['entry_id']}")
            print(f"      Reference: {transaction['reference']}")
            print(f"      Template Used: {transaction['template_used']}")
            print(f"      Total Debits: ${transaction['total_debits']}")
            print(f"      Total Credits: ${transaction['total_credits']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Create an expense payment
    print("\n5️⃣ Testing POST /create (Expense Payment)")
    try:
        create_data = {
            "template_id": "expense_payment",
            "amount": 75.00,
            "description": "Office supplies purchase",
            "payment_method": "cash"
        }
        
        response = requests.post(f"{base_url}/create", 
                               headers=headers, 
                               json=create_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Expense payment created successfully")
            transaction = data['transaction']
            print(f"      Entry ID: {transaction['entry_id']}")
            print(f"      Reference: {transaction['reference']}")
            print(f"      Template Used: {transaction['template_used']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n🎯 Transaction Templates API Test Complete!")

if __name__ == "__main__":
    test_transaction_templates()

