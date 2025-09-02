#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:5000"
results = {'passed': 0, 'failed': 0, 'errors': []}

def test_endpoint(method, endpoint, data=None, params=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return True, None
        else:
            return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)

def log_test(name, success, error=None):
    if success:
        results['passed'] += 1
        print(f"✅ {name}")
    else:
        results['failed'] += 1
        print(f"❌ {name}: {error}")
        results['errors'].append(f"{name}: {error}")

print("🚀 Testing Advanced APIs in Batches...")

# Batch 1: Finance Core
print("\n🏦 Batch 1: Finance Core")
log_test("GET Chart of Accounts", *test_endpoint('GET', '/api/finance/chart-of-accounts'))
log_test("GET General Ledger", *test_endpoint('GET', '/api/finance/general-ledger'))
log_test("GET Accounts Payable", *test_endpoint('GET', '/api/finance/accounts-payable'))
log_test("GET Accounts Receivable", *test_endpoint('GET', '/api/finance/accounts-receivable'))

# Batch 2: Finance Advanced
print("\n💰 Batch 2: Finance Advanced")
log_test("GET Fixed Assets", *test_endpoint('GET', '/api/finance/fixed-assets'))
log_test("GET Budgets", *test_endpoint('GET', '/api/finance/budgets'))
log_test("GET Tax Records", *test_endpoint('GET', '/api/finance/tax-records'))
log_test("GET Bank Reconciliations", *test_endpoint('GET', '/api/finance/bank-reconciliations'))

# Batch 3: Finance Reports
print("\n📈 Batch 3: Finance Reports")
log_test("GET Profit Loss Report", *test_endpoint('GET', '/api/finance/reports/profit-loss', params={'start_date': '2024-01-01', 'end_date': '2024-12-31'}))
log_test("GET Balance Sheet Report", *test_endpoint('GET', '/api/finance/reports/balance-sheet', params={'as_of_date': '2024-12-31'}))
log_test("GET Dashboard Metrics", *test_endpoint('GET', '/api/finance/dashboard-metrics'))
log_test("GET KPIs", *test_endpoint('GET', '/api/finance/kpis'))

# Batch 4: Inventory Core
print("\n🏭 Batch 4: Inventory Core")
log_test("GET UoM", *test_endpoint('GET', '/api/inventory/advanced/uom'))
log_test("GET Categories", *test_endpoint('GET', '/api/inventory/advanced/categories'))
log_test("GET Products", *test_endpoint('GET', '/api/inventory/advanced/products'))
log_test("GET Stock Levels", *test_endpoint('GET', '/api/inventory/advanced/stock-levels'))

# Batch 5: Inventory Operations
print("\n📦 Batch 5: Inventory Operations")
log_test("GET Pick Lists", *test_endpoint('GET', '/api/inventory/advanced/pick-lists'))
log_test("GET Warehouse Activity", *test_endpoint('GET', '/api/inventory/advanced/warehouse-activity'))
log_test("GET Predictive Stockouts", *test_endpoint('GET', '/api/inventory/advanced/predictive-stockouts'))
log_test("GET Picker Performance", *test_endpoint('GET', '/api/inventory/advanced/picker-performance'))

# Batch 6: Data Integrity
print("\n🔍 Batch 6: Data Integrity")
log_test("GET Admin Panel", *test_endpoint('GET', '/api/inventory/data-integrity/admin-panel'))
log_test("GET Health Check", *test_endpoint('GET', '/api/inventory/data-integrity/health'))
log_test("GET Reconciliation Status", *test_endpoint('GET', '/api/inventory/data-integrity/reconciliation/status'))
log_test("GET Discrepancies", *test_endpoint('GET', '/api/inventory/data-integrity/discrepancies'))

print(f"\n📊 Results: {results['passed']} passed, {results['failed']} failed")
success_rate = (results['passed'] / (results['passed'] + results['failed'])) * 100 if (results['passed'] + results['failed']) > 0 else 0
print(f"📈 Success Rate: {success_rate:.1f}%")
