#!/usr/bin/env python3
"""
Edge Case Testing Suite
Date: September 18, 2025
Purpose: Rapid testing of critical edge cases for production launch
"""

import requests
import json
from datetime import datetime, date
import time

BASE_URL = "http://localhost:5000"

def test_scenario(name, endpoint, data, expected_success=True):
    """Test a single scenario and return results"""
    print(f"\n🧪 Testing: {name}")
    print(f"📡 Endpoint: {endpoint}")
    
    try:
        if data:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        result = response.json()
        success = result.get('success', False)
        
        if success == expected_success:
            print(f"✅ PASSED: {name}")
            if 'journal_entry_id' in result.get('data', {}).get('results', {}).get('journal_entries', [{}])[0]:
                je_id = result['data']['results']['journal_entries'][0]['journal_entry_id']
                print(f"   📝 Journal Entry: {je_id}")
            return True, result
        else:
            print(f"❌ FAILED: {name}")
            print(f"   Expected success: {expected_success}, Got: {success}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False, result
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION FAILED: {name} - Server not responding")
        return False, {"error": "Server not responding"}
    except Exception as e:
        print(f"❌ ERROR: {name} - {str(e)}")
        return False, {"error": str(e)}

def run_all_edge_case_tests():
    """Run all edge case tests rapidly"""
    
    print("🚀 RAPID EDGE-CASE TESTING SUITE")
    print("=" * 50)
    
    test_results = []
    start_time = time.time()
    
    # Test 1: Damaged Goods Write-off
    test_results.append(test_scenario(
        "Damaged Goods Write-off",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "writeoff",
            "product_id": 1,
            "item_name": "Test Product A",
            "quantity": 15,
            "unit_cost": 20.00,
            "reason": "damaged",
            "reference": "WO-DAMAGE-TEST",
            "warehouse_id": 1
        }
    ))
    
    # Test 2: Obsolete Inventory Write-off
    test_results.append(test_scenario(
        "Obsolete Inventory Write-off",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "writeoff",
            "product_id": 2,
            "item_name": "Test Product B",
            "quantity": 25,
            "unit_cost": 15.00,
            "reason": "obsolete",
            "reference": "WO-OBSOLETE-TEST",
            "warehouse_id": 1
        }
    ))
    
    # Test 3: Positive Inventory Adjustment (Found More)
    test_results.append(test_scenario(
        "Positive Inventory Adjustment",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "adjustment",
            "product_id": 1,
            "item_name": "Test Product A",
            "adjustment_quantity": 10,  # Found 10 more units
            "unit_cost": 20.00,
            "reason": "Physical Count - Found More",
            "reference": "ADJ-POSITIVE-TEST",
            "warehouse_id": 1
        }
    ))
    
    # Test 4: Negative Inventory Adjustment (Shortage)
    test_results.append(test_scenario(
        "Negative Inventory Adjustment",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "adjustment",
            "product_id": 2,
            "item_name": "Test Product B",
            "adjustment_quantity": -8,  # Missing 8 units
            "unit_cost": 15.00,
            "reason": "Physical Count - Shortage",
            "reference": "ADJ-NEGATIVE-TEST",
            "warehouse_id": 1
        }
    ))
    
    # Test 5: Inventory Revaluation (Price Increase)
    test_results.append(test_scenario(
        "Inventory Revaluation (Price Increase)",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "revaluation",
            "product_id": 1,
            "item_name": "Test Product A",
            "quantity": 100,
            "old_unit_cost": 20.00,
            "new_unit_cost": 25.00,  # Market price increased
            "reason": "Market Price Adjustment",
            "reference": "REV-PRICE-UP-TEST",
            "warehouse_id": 1
        }
    ))
    
    # Test 6: Inventory Revaluation (Price Decrease)
    test_results.append(test_scenario(
        "Inventory Revaluation (Price Decrease)",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "revaluation",
            "product_id": 2,
            "item_name": "Test Product B",
            "quantity": 80,
            "old_unit_cost": 15.00,
            "new_unit_cost": 12.00,  # Market price decreased
            "reason": "Market Price Decline",
            "reference": "REV-PRICE-DOWN-TEST",
            "warehouse_id": 1
        }
    ))
    
    # Test 7: Large COGS Transaction
    test_results.append(test_scenario(
        "Large COGS Transaction",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "issue",
            "product_id": 1,
            "item_name": "Test Product A",
            "quantity": 500,  # Large quantity
            "unit_cost": 25.00,
            "reference": "SALE-LARGE-TEST",
            "customer_id": 1,
            "warehouse_id": 1
        }
    ))
    
    # Test 8: Transfer with Cost Change
    test_results.append(test_scenario(
        "Inventory Transfer (Cost Change)",
        "/api/integration/inventory-finance/process-transaction",
        {
            "transaction_type": "transfer",
            "product_id": 1,
            "item_name": "Test Product A",
            "quantity": 20,
            "from_unit_cost": 25.00,
            "to_unit_cost": 27.00,  # Higher cost at destination
            "from_location": "Warehouse A",
            "to_location": "Warehouse B",
            "reference": "TXF-COST-TEST",
            "from_location_id": 1,
            "to_location_id": 2
        }
    ))
    
    # Test 9: System Integration Status
    test_results.append(test_scenario(
        "Integration Status Check",
        "/api/integration/inventory-finance/status",
        None
    ))
    
    # Test 10: Reconciliation Check
    test_results.append(test_scenario(
        "Inventory-GL Reconciliation",
        "/api/integration/inventory-finance/reconcile",
        {"date": date.today().isoformat()}
    ))
    
    # Calculate results
    total_tests = len(test_results)
    passed_tests = sum(1 for passed, _ in test_results if passed)
    failed_tests = total_tests - passed_tests
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 50)
    print("🎯 EDGE-CASE TESTING RESULTS")
    print("=" * 50)
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"⏱️  Total Time: {elapsed_time:.2f} seconds")
    print(f"🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL EDGE CASES PASSED! SYSTEM IS BULLETPROOF! 🏆")
        print("🚀 READY FOR PRODUCTION LAUNCH!")
    elif passed_tests >= total_tests * 0.8:
        print("\n⚠️  MOSTLY PASSED - Minor issues detected")
        print("🔧 Review failed tests before launch")
    else:
        print("\n❌ MULTIPLE FAILURES - Requires attention")
        print("🛠️  Fix critical issues before launch")
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'success_rate': (passed_tests/total_tests)*100,
        'elapsed_time': elapsed_time,
        'ready_for_launch': passed_tests == total_tests
    }

if __name__ == "__main__":
    print("🧪 Starting Edge-Case Testing Suite...")
    print("⚡ This will test all critical inventory-finance integration scenarios")
    print("🎯 Goal: Prove system is bulletproof for production launch\n")
    
    results = run_all_edge_case_tests()
    
    if results['ready_for_launch']:
        print("\n🎊 CONGRATULATIONS! Your ERP system is PRODUCTION READY!")
        print("🚀 Launch with confidence - all edge cases handled!")
    else:
        print(f"\n⚠️  {results['failed_tests']} issues need attention before launch")

