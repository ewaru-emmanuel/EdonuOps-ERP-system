#!/usr/bin/env python3
"""
Advanced API Testing Script
Tests all advanced module endpoints in batches for efficiency
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:5000"
TEST_RESULTS = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def log_test(test_name, success, error=None):
    """Log test results"""
    if success:
        TEST_RESULTS['passed'] += 1
        print(f"✅ {test_name}")
    else:
        TEST_RESULTS['failed'] += 1
        print(f"❌ {test_name}: {error}")
        TEST_RESULTS['errors'].append(f"{test_name}: {error}")

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        if response.status_code == expected_status:
            return True, None
        else:
            return False, f"Status {response.status_code}, Expected {expected_status}"
    except Exception as e:
        return False, str(e)

def test_finance_endpoints():
    """Test all advanced finance endpoints"""
    print("\n🏦 Testing Advanced Finance Endpoints...")
    
    # Batch 1: Core Financial Data
    print("\n📊 Batch 1: Core Financial Data")
    
    # Chart of Accounts
    log_test("GET /api/finance/advanced/chart-of-accounts", 
             *test_endpoint('GET', '/api/finance/advanced/chart-of-accounts'))
    
    # Create sample chart of account
    coa_data = {
        "account_code": "1000",
        "account_name": "Cash",
        "account_type": "asset",
        "parent_account_id": None,
        "description": "Cash and cash equivalents"
    }
    log_test("POST /api/finance/advanced/chart-of-accounts", 
             *test_endpoint('POST', '/api/finance/advanced/chart-of-accounts', coa_data))
    
    # General Ledger
    log_test("GET /api/finance/advanced/general-ledger", 
             *test_endpoint('GET', '/api/finance/advanced/general-ledger'))
    
    # Create sample ledger entry
    gl_data = {
        "account_id": 1,
        "transaction_date": datetime.now().isoformat(),
        "debit_amount": 1000.00,
        "credit_amount": 0.00,
        "description": "Test entry",
        "reference_number": "TEST-001"
    }
    log_test("POST /api/finance/advanced/general-ledger", 
             *test_endpoint('POST', '/api/finance/advanced/general-ledger', gl_data))
    
    # Batch 2: Accounts Payable/Receivable
    print("\n💰 Batch 2: Accounts Payable/Receivable")
    
    # Accounts Payable
    log_test("GET /api/finance/advanced/accounts-payable", 
             *test_endpoint('GET', '/api/finance/advanced/accounts-payable'))
    
    # Create sample AP
    ap_data = {
        "vendor_id": 1,
        "invoice_number": "INV-001",
        "invoice_date": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "amount": 5000.00,
        "description": "Test invoice"
    }
    log_test("POST /api/finance/advanced/accounts-payable", 
             *test_endpoint('POST', '/api/finance/advanced/accounts-payable', ap_data))
    
    # Accounts Receivable
    log_test("GET /api/finance/advanced/accounts-receivable", 
             *test_endpoint('GET', '/api/finance/advanced/accounts-receivable'))
    
    # Create sample AR
    ar_data = {
        "customer_id": 1,
        "invoice_number": "AR-001",
        "invoice_date": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "amount": 3000.00,
        "description": "Test AR invoice"
    }
    log_test("POST /api/finance/advanced/accounts-receivable", 
             *test_endpoint('POST', '/api/finance/advanced/accounts-receivable', ar_data))
    
    # Batch 3: Fixed Assets & Budgeting
    print("\n🏢 Batch 3: Fixed Assets & Budgeting")
    
    # Fixed Assets
    log_test("GET /api/finance/advanced/fixed-assets", 
             *test_endpoint('GET', '/api/finance/advanced/fixed-assets'))
    
    # Create sample asset
    asset_data = {
        "asset_code": "FA-001",
        "asset_name": "Office Building",
        "asset_type": "building",
        "purchase_date": datetime.now().isoformat(),
        "purchase_cost": 500000.00,
        "useful_life_years": 30,
        "depreciation_method": "straight_line"
    }
    log_test("POST /api/finance/advanced/fixed-assets", 
             *test_endpoint('POST', '/api/finance/advanced/fixed-assets', asset_data))
    
    # Budgets
    log_test("GET /api/finance/advanced/budgets", 
             *test_endpoint('GET', '/api/finance/advanced/budgets'))
    
    # Create sample budget
    budget_data = {
        "budget_name": "2024 Operating Budget",
        "fiscal_year": 2024,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "total_amount": 1000000.00,
        "description": "Annual operating budget"
    }
    log_test("POST /api/finance/advanced/budgets", 
             *test_endpoint('POST', '/api/finance/advanced/budgets', budget_data))
    
    # Batch 4: Tax & Bank Reconciliation
    print("\n🏛️ Batch 4: Tax & Bank Reconciliation")
    
    # Tax Records
    log_test("GET /api/finance/advanced/tax-records", 
             *test_endpoint('GET', '/api/finance/advanced/tax-records'))
    
    # Bank Reconciliations
    log_test("GET /api/finance/advanced/bank-reconciliations", 
             *test_endpoint('GET', '/api/finance/advanced/bank-reconciliations'))
    
    # Batch 5: Reports & Analytics
    print("\n📈 Batch 5: Reports & Analytics")
    
    # Financial Reports
    log_test("GET /api/finance/advanced/reports/profit-loss", 
             *test_endpoint('GET', '/api/finance/advanced/reports/profit-loss'))
    
    log_test("GET /api/finance/advanced/reports/balance-sheet", 
             *test_endpoint('GET', '/api/finance/advanced/reports/balance-sheet'))
    
    # Dashboard Metrics
    log_test("GET /api/finance/advanced/dashboard-metrics", 
             *test_endpoint('GET', '/api/finance/advanced/dashboard-metrics'))
    
    # KPIs
    log_test("GET /api/finance/advanced/kpis", 
             *test_endpoint('GET', '/api/finance/advanced/kpis'))

def test_inventory_endpoints():
    """Test all advanced inventory endpoints"""
    print("\n🏭 Testing Advanced Inventory Endpoints...")
    
    # Batch 1: Foundational Data
    print("\n📏 Batch 1: Foundational Data")
    
    # UoM
    log_test("GET /api/inventory/advanced/uom", 
             *test_endpoint('GET', '/api/inventory/advanced/uom'))
    
    # Create sample UoM
    uom_data = {
        "name": "Test UoM",
        "code": "TEST",
        "description": "Test unit of measure"
    }
    log_test("POST /api/inventory/advanced/uom", 
             *test_endpoint('POST', '/api/inventory/advanced/uom', uom_data))
    
    # UoM Conversions
    log_test("GET /api/inventory/advanced/uom-conversions", 
             *test_endpoint('GET', '/api/inventory/advanced/uom-conversions'))
    
    # Categories
    log_test("GET /api/inventory/advanced/categories", 
             *test_endpoint('GET', '/api/inventory/advanced/categories'))
    
    # Create sample category
    category_data = {
        "name": "Test Category",
        "description": "Test product category",
        "abc_class": "A"
    }
    log_test("POST /api/inventory/advanced/categories", 
             *test_endpoint('POST', '/api/inventory/advanced/categories', category_data))
    
    # Batch 2: Products & Variants
    print("\n📦 Batch 2: Products & Variants")
    
    # Products
    log_test("GET /api/inventory/advanced/products", 
             *test_endpoint('GET', '/api/inventory/advanced/products'))
    
    # Create sample product
    product_data = {
        "sku": "TEST-PROD-001",
        "name": "Test Product",
        "description": "Test product description",
        "category_id": 1,
        "base_uom_id": 1,
        "cost_method": "FIFO",
        "standard_cost": 100.00,
        "current_cost": 100.00,
        "min_stock": 10,
        "max_stock": 100,
        "reorder_point": 20,
        "product_type": "standard",
        "track_serial_numbers": False,
        "track_lots": False,
        "track_expiry": False
    }
    log_test("POST /api/inventory/advanced/products", 
             *test_endpoint('POST', '/api/inventory/advanced/products', product_data))
    
    # Batch 3: Warehouse Operations
    print("\n🏢 Batch 3: Warehouse Operations")
    
    # Stock Levels
    log_test("GET /api/inventory/advanced/stock-levels", 
             *test_endpoint('GET', '/api/inventory/advanced/stock-levels'))
    
    # Pick Lists
    log_test("GET /api/inventory/advanced/pick-lists", 
             *test_endpoint('GET', '/api/inventory/advanced/pick-lists'))
    
    # Warehouse Activities
    log_test("GET /api/inventory/advanced/warehouse-activity", 
             *test_endpoint('GET', '/api/inventory/advanced/warehouse-activity'))
    
    # Batch 4: Analytics & Intelligence
    print("\n📊 Batch 4: Analytics & Intelligence")
    
    # Predictive Stockouts
    log_test("GET /api/inventory/advanced/predictive-stockouts", 
             *test_endpoint('GET', '/api/inventory/advanced/predictive-stockouts'))
    
    # Picker Performance
    log_test("GET /api/inventory/advanced/picker-performance", 
             *test_endpoint('GET', '/api/inventory/advanced/picker-performance'))

def test_data_integrity_endpoints():
    """Test data integrity endpoints"""
    print("\n🔍 Testing Data Integrity Endpoints...")
    
    # Admin Panel
    log_test("GET /api/inventory/data-integrity/admin-panel", 
             *test_endpoint('GET', '/api/inventory/data-integrity/admin-panel'))
    
    # Health Check
    log_test("GET /api/inventory/data-integrity/health", 
             *test_endpoint('GET', '/api/inventory/data-integrity/health'))
    
    # Reconciliation Status
    log_test("GET /api/inventory/data-integrity/reconciliation/status", 
             *test_endpoint('GET', '/api/inventory/data-integrity/reconciliation/status'))
    
    # Discrepancies
    log_test("GET /api/inventory/data-integrity/discrepancies", 
             *test_endpoint('GET', '/api/inventory/data-integrity/discrepancies'))
    
    # Recommendations
    log_test("GET /api/inventory/data-integrity/recommendations", 
             *test_endpoint('GET', '/api/inventory/data-integrity/recommendations'))

def test_cross_module_endpoints():
    """Test cross-module integration endpoints"""
    print("\n🔗 Testing Cross-Module Integration...")
    
    # Test finance-inventory integration
    log_test("GET /api/finance/advanced/dashboard-metrics", 
             *test_endpoint('GET', '/api/finance/advanced/dashboard-metrics'))
    
    # Test inventory-finance integration
    log_test("GET /api/inventory/advanced/stock-levels", 
             *test_endpoint('GET', '/api/inventory/advanced/stock-levels'))

def run_all_tests():
    """Run all API tests"""
    print("🚀 Starting Advanced API Testing...")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Test all modules
        test_finance_endpoints()
        test_inventory_endpoints()
        test_data_integrity_endpoints()
        test_cross_module_endpoints()
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        TEST_RESULTS['errors'].append(f"Test suite error: {str(e)}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {TEST_RESULTS['passed']}")
    print(f"❌ Failed: {TEST_RESULTS['failed']}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    
    if TEST_RESULTS['errors']:
        print(f"\n🔍 Errors Found:")
        for error in TEST_RESULTS['errors']:
            print(f"  - {error}")
    
    success_rate = (TEST_RESULTS['passed'] / (TEST_RESULTS['passed'] + TEST_RESULTS['failed'])) * 100 if (TEST_RESULTS['passed'] + TEST_RESULTS['failed']) > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Excellent! API endpoints are working well!")
    elif success_rate >= 70:
        print("👍 Good! Most endpoints are working, some issues to address.")
    else:
        print("⚠️  Needs attention! Multiple endpoint issues detected.")

if __name__ == '__main__':
    run_all_tests()

