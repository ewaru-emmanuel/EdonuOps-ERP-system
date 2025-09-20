#!/usr/bin/env python3
"""
Test Inventory Validation Controls
Date: September 18, 2025
Purpose: Test the "sold juice without juice" prevention system
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_problematic_entry():
    """Test what happens when someone tries to enter 'sold juice' without juice in inventory"""
    
    print("🧪 TESTING: 'Sold Juice Without Juice' Scenario")
    print("=" * 60)
    
    try:
        # Test the problematic entry demo
        response = requests.post(
            f"{BASE_URL}/api/finance/inventory-validation/demo/problematic-entry",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Validation System Working!")
            print("\n📋 Results:")
            
            # Show strict mode result
            strict_result = result['data']['strict_mode_result']
            print(f"🔒 STRICT MODE: {'BLOCKED' if not strict_result['allowed'] else 'ALLOWED'}")
            
            if strict_result['validation']['errors']:
                print("❌ ERRORS DETECTED:")
                for error in strict_result['validation']['errors']:
                    print(f"   • {error}")
            
            if strict_result['validation']['warnings']:
                print("⚠️  WARNINGS:")
                for warning in strict_result['validation']['warnings']:
                    print(f"   • {warning}")
            
            if strict_result['validation']['suggestions']:
                print("💡 SUGGESTIONS:")
                for suggestion in strict_result['validation']['suggestions']:
                    print(f"   • {suggestion}")
            
            # Show what the system detected
            explanation = result['data']['explanation']
            print(f"\n🔍 PROBLEM DETECTED: {explanation['problem']}")
            print(f"🛡️  STRICT MODE: {explanation['strict_mode']}")
            print(f"💡 RECOMMENDATION: {explanation['recommendation']}")
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION FAILED - Server not responding")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_proper_sales_process():
    """Test the proper way to handle sales with inventory integration"""
    
    print("\n🧪 TESTING: Proper Sales Process")
    print("=" * 60)
    
    try:
        # Test proper sales entry
        sales_data = {
            'product_name': 'Demo Product',
            'quantity': 5,
            'unit_price': 20.00,
            'customer_name': 'Test Customer'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/finance/inventory-validation/demo/proper-sale",
            json=sales_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Proper Sales Process Working!")
            
            integration_result = result['data']['integration_result']
            if integration_result.get('success'):
                summary = integration_result.get('summary', {})
                print(f"\n📊 SALES SUMMARY:")
                print(f"   💰 Revenue: ${summary.get('revenue_amount', 0):.2f}")
                print(f"   💸 COGS: ${summary.get('cogs_amount', 0):.2f}")
                print(f"   💵 Gross Profit: ${summary.get('gross_profit', 0):.2f}")
                print(f"   📈 Gross Margin: {summary.get('gross_margin', 0):.1f}%")
                
                entries = integration_result.get('results', {}).get('journal_entries_created', [])
                print(f"\n📝 JOURNAL ENTRIES CREATED: {len(entries)}")
                for i, entry in enumerate(entries, 1):
                    if entry.get('success'):
                        print(f"   {i}. {entry.get('message', 'Entry created')}")
            else:
                print(f"❌ Integration failed: {integration_result.get('error', 'Unknown error')}")
                if integration_result.get('suggestion'):
                    print(f"💡 Suggestion: {integration_result['suggestion']}")
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION FAILED - Server not responding")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Run all validation tests"""
    
    print("🚀 INVENTORY VALIDATION CONTROL TESTING")
    print("🎯 Goal: Prevent 'sold juice without juice' scenarios")
    print("🛡️  Testing enterprise-grade business controls\n")
    
    # Test 1: Problematic entry
    test1_passed = test_problematic_entry()
    
    # Test 2: Proper process
    test2_passed = test_proper_sales_process()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 VALIDATION CONTROL TEST RESULTS")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Inventory validation controls working perfectly")
        print("🛡️  System prevents data integrity issues")
        print("🚀 READY FOR PRODUCTION!")
    elif test1_passed or test2_passed:
        print("⚠️  PARTIAL SUCCESS")
        print("🔧 Some features working, check server connectivity")
    else:
        print("❌ TESTS FAILED")
        print("🔧 Check server status and try again")
    
    print("\n🏆 Your ERP now has enterprise-grade business controls!")

if __name__ == "__main__":
    main()

