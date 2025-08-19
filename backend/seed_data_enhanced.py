#!/usr/bin/env python3
"""
Enhanced Seed data script for EdonuOps
Creates QuickBooks-compatible Chart of Accounts with EdonuOps advanced features
"""

from app import create_app, db
from modules.finance.models import ChartOfAccount
from modules.core.models import User, Role, Organization
from werkzeug.security import generate_password_hash

def seed_enhanced_chart_of_accounts():
    """Create QuickBooks-compatible Chart of Accounts with EdonuOps advanced features"""
    
    # Check if accounts already exist
    if ChartOfAccount.query.first():
        print("Chart of Accounts already exists, skipping...")
        return
    
    accounts = [
        # ASSETS (1000-1999)
        # ===================
        
        # Cash & Cash Equivalents (1000-1099)
        {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': 'asset'},
        {'code': '1010', 'name': 'Petty Cash', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1020', 'name': 'Checking Account', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1030', 'name': 'Savings Account', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1040', 'name': 'Money Market Account', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1050', 'name': 'Undeposited Funds', 'type': 'asset', 'parent_code': '1000'},
        
        # Accounts Receivable (1100-1199)
        {'code': '1100', 'name': 'Accounts Receivable', 'type': 'asset'},
        {'code': '1110', 'name': 'Trade Receivables', 'type': 'asset', 'parent_code': '1100'},
        {'code': '1115', 'name': 'Other Receivables', 'type': 'asset', 'parent_code': '1100'},
        {'code': '1120', 'name': 'Employee Advances', 'type': 'asset', 'parent_code': '1100'},
        {'code': '1130', 'name': 'Allowance for Doubtful Accounts', 'type': 'asset', 'parent_code': '1100'},
        
        # Inventory (1200-1299)
        {'code': '1200', 'name': 'Inventory', 'type': 'asset'},
        {'code': '1210', 'name': 'Raw Materials', 'type': 'asset', 'parent_code': '1200'},
        {'code': '1220', 'name': 'Work in Process', 'type': 'asset', 'parent_code': '1200'},
        {'code': '1230', 'name': 'Finished Goods', 'type': 'asset', 'parent_code': '1200'},
        {'code': '1240', 'name': 'Inventory Asset', 'type': 'asset', 'parent_code': '1200'},
        
        # Other Current Assets (1300-1399)
        {'code': '1300', 'name': 'Other Current Assets', 'type': 'asset'},
        {'code': '1310', 'name': 'Prepaid Expenses', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1315', 'name': 'Prepaid Insurance', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1320', 'name': 'Prepaid Rent', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1330', 'name': 'Deposits', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1340', 'name': 'Tax Refunds Receivable', 'type': 'asset', 'parent_code': '1300'},
        
        # Fixed Assets (1500-1599)
        {'code': '1500', 'name': 'Fixed Assets', 'type': 'asset'},
        {'code': '1510', 'name': 'Land', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1520', 'name': 'Buildings', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1525', 'name': 'Accumulated Depreciation - Buildings', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1530', 'name': 'Equipment', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1535', 'name': 'Accumulated Depreciation - Equipment', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1540', 'name': 'Furniture & Fixtures', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1545', 'name': 'Accumulated Depreciation - Furniture', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1550', 'name': 'Vehicles', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1555', 'name': 'Accumulated Depreciation - Vehicles', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1560', 'name': 'Computer Equipment', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1565', 'name': 'Accumulated Depreciation - Computer Equipment', 'type': 'asset', 'parent_code': '1500'},
        
        # Other Assets (1700-1799)
        {'code': '1700', 'name': 'Other Assets', 'type': 'asset'},
        {'code': '1710', 'name': 'Intangible Assets', 'type': 'asset', 'parent_code': '1700'},
        {'code': '1720', 'name': 'Goodwill', 'type': 'asset', 'parent_code': '1700'},
        {'code': '1730', 'name': 'Patents & Trademarks', 'type': 'asset', 'parent_code': '1700'},
        
        # LIABILITIES (2000-2999)
        # ========================
        
        # Current Liabilities (2000-2099)
        {'code': '2000', 'name': 'Current Liabilities', 'type': 'liability'},
        {'code': '2010', 'name': 'Accounts Payable', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2015', 'name': 'Trade Payables', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2020', 'name': 'Accrued Liabilities', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2025', 'name': 'Accrued Wages', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2030', 'name': 'Short-term Loans', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2035', 'name': 'Line of Credit', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2040', 'name': 'Current Portion of Long-term Debt', 'type': 'liability', 'parent_code': '2000'},
        
        # Credit Cards (2100-2199)
        {'code': '2100', 'name': 'Credit Cards', 'type': 'liability'},
        {'code': '2110', 'name': 'Business Credit Card', 'type': 'liability', 'parent_code': '2100'},
        {'code': '2115', 'name': 'Corporate Credit Card', 'type': 'liability', 'parent_code': '2100'},
        {'code': '2120', 'name': 'Fuel Credit Card', 'type': 'liability', 'parent_code': '2100'},
        
        # Tax Liabilities (2200-2299)
        {'code': '2200', 'name': 'Tax Liabilities', 'type': 'liability'},
        {'code': '2210', 'name': 'Federal Income Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2215', 'name': 'State Income Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2220', 'name': 'Sales Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2225', 'name': 'Payroll Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2230', 'name': 'Social Security Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2235', 'name': 'Medicare Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2240', 'name': 'Unemployment Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2245', 'name': 'Workers Compensation Payable', 'type': 'liability', 'parent_code': '2200'},
        
        # Other Current Liabilities (2300-2399)
        {'code': '2300', 'name': 'Other Current Liabilities', 'type': 'liability'},
        {'code': '2310', 'name': 'Deferred Revenue', 'type': 'liability', 'parent_code': '2300'},
        {'code': '2315', 'name': 'Customer Deposits', 'type': 'liability', 'parent_code': '2300'},
        {'code': '2320', 'name': 'Accrued Interest', 'type': 'liability', 'parent_code': '2300'},
        {'code': '2330', 'name': 'Dividends Payable', 'type': 'liability', 'parent_code': '2300'},
        
        # Long-term Liabilities (2500-2599)
        {'code': '2500', 'name': 'Long-term Liabilities', 'type': 'liability'},
        {'code': '2510', 'name': 'Long-term Debt', 'type': 'liability', 'parent_code': '2500'},
        {'code': '2515', 'name': 'Notes Payable', 'type': 'liability', 'parent_code': '2500'},
        {'code': '2520', 'name': 'Equipment Loans', 'type': 'liability', 'parent_code': '2500'},
        {'code': '2525', 'name': 'Mortgage Payable', 'type': 'liability', 'parent_code': '2500'},
        {'code': '2530', 'name': 'Bonds Payable', 'type': 'liability', 'parent_code': '2500'},
        
        # EQUITY (3000-3999)
        # ===================
        
        {'code': '3000', 'name': 'Equity', 'type': 'equity'},
        {'code': '3010', 'name': 'Common Stock', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3015', 'name': 'Preferred Stock', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3020', 'name': 'Additional Paid-in Capital', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3030', 'name': 'Retained Earnings', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3035', 'name': 'Current Year Earnings', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3040', 'name': 'Treasury Stock', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3050', 'name': 'Owner\'s Equity', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3055', 'name': 'Partner\'s Equity', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3060', 'name': 'Owner Withdrawals', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3070', 'name': 'Dividends', 'type': 'equity', 'parent_code': '3000'},
        
        # REVENUE (4000-4999)
        # ====================
        
        # Sales Revenue (4000-4099)
        {'code': '4000', 'name': 'Sales Revenue', 'type': 'revenue'},
        {'code': '4010', 'name': 'Product Sales', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4020', 'name': 'Service Revenue', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4025', 'name': 'Consulting Revenue', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4030', 'name': 'Sales Returns & Allowances', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4035', 'name': 'Sales Discounts', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4040', 'name': 'Shipping & Handling Revenue', 'type': 'revenue', 'parent_code': '4000'},
        
        # Other Income (4800-4999)
        {'code': '4800', 'name': 'Other Income', 'type': 'revenue'},
        {'code': '4810', 'name': 'Interest Income', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4820', 'name': 'Dividend Income', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4830', 'name': 'Rental Income', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4840', 'name': 'Gain on Sale of Assets', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4850', 'name': 'Foreign Exchange Gain', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4890', 'name': 'Miscellaneous Income', 'type': 'revenue', 'parent_code': '4800'},
        
        # COST OF SALES (5000-5999)
        # ==========================
        
        {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'expense'},
        {'code': '5010', 'name': 'Direct Materials', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5020', 'name': 'Direct Labor', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5030', 'name': 'Manufacturing Overhead', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5040', 'name': 'Freight & Shipping', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5050', 'name': 'Cost of Services', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5060', 'name': 'Subcontractor Costs', 'type': 'expense', 'parent_code': '5000'},
        
        # OPERATING EXPENSES (6000-6999)
        # ===============================
        
        # Personnel Expenses (6000-6099)
        {'code': '6000', 'name': 'Personnel Expenses', 'type': 'expense'},
        {'code': '6010', 'name': 'Salaries and Wages', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6015', 'name': 'Payroll Taxes', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6020', 'name': 'Employee Benefits', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6025', 'name': 'Health Insurance', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6030', 'name': 'Retirement Plan', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6035', 'name': 'Workers Compensation', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6040', 'name': 'Training & Development', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6045', 'name': 'Recruitment Costs', 'type': 'expense', 'parent_code': '6000'},
        
        # Facility Expenses (6100-6199)
        {'code': '6100', 'name': 'Facility Expenses', 'type': 'expense'},
        {'code': '6110', 'name': 'Rent Expense', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6115', 'name': 'Property Taxes', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6120', 'name': 'Utilities', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6125', 'name': 'Electricity', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6130', 'name': 'Gas', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6135', 'name': 'Water & Sewer', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6140', 'name': 'Telecommunications', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6145', 'name': 'Internet & Phone', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6150', 'name': 'Building Maintenance', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6155', 'name': 'Janitorial Services', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6160', 'name': 'Security Services', 'type': 'expense', 'parent_code': '6100'},
        
        # Technology Expenses (6200-6299)
        {'code': '6200', 'name': 'Technology Expenses', 'type': 'expense'},
        {'code': '6210', 'name': 'Software Licenses', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6215', 'name': 'Software Subscriptions', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6220', 'name': 'Computer Equipment', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6225', 'name': 'IT Support & Maintenance', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6230', 'name': 'Cloud Services', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6235', 'name': 'Website & Domain', 'type': 'expense', 'parent_code': '6200'},
        
        # Professional Services (6300-6399)
        {'code': '6300', 'name': 'Professional Services', 'type': 'expense'},
        {'code': '6310', 'name': 'Accounting & Bookkeeping', 'type': 'expense', 'parent_code': '6300'},
        {'code': '6315', 'name': 'Legal Fees', 'type': 'expense', 'parent_code': '6300'},
        {'code': '6320', 'name': 'Consulting Fees', 'type': 'expense', 'parent_code': '6300'},
        {'code': '6325', 'name': 'Audit Fees', 'type': 'expense', 'parent_code': '6300'},
        {'code': '6330', 'name': 'Tax Preparation', 'type': 'expense', 'parent_code': '6300'},
        
        # Marketing & Sales (6400-6499)
        {'code': '6400', 'name': 'Marketing & Sales', 'type': 'expense'},
        {'code': '6410', 'name': 'Advertising', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6415', 'name': 'Digital Marketing', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6420', 'name': 'Trade Shows & Events', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6425', 'name': 'Sales Commissions', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6430', 'name': 'Customer Entertainment', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6435', 'name': 'Promotional Materials', 'type': 'expense', 'parent_code': '6400'},
        
        # Travel & Transportation (6500-6599)
        {'code': '6500', 'name': 'Travel & Transportation', 'type': 'expense'},
        {'code': '6510', 'name': 'Business Travel', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6515', 'name': 'Airfare', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6520', 'name': 'Hotels & Lodging', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6525', 'name': 'Meals & Entertainment', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6530', 'name': 'Vehicle Expenses', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6535', 'name': 'Fuel & Gas', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6540', 'name': 'Vehicle Maintenance', 'type': 'expense', 'parent_code': '6500'},
        
        # Office & Administrative (6600-6699)
        {'code': '6600', 'name': 'Office & Administrative', 'type': 'expense'},
        {'code': '6610', 'name': 'Office Supplies', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6615', 'name': 'Postage & Shipping', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6620', 'name': 'Printing & Copying', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6625', 'name': 'Bank Fees', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6630', 'name': 'Credit Card Fees', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6635', 'name': 'Merchant Processing Fees', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6640', 'name': 'Subscription Services', 'type': 'expense', 'parent_code': '6600'},
        
        # Insurance (6700-6799)
        {'code': '6700', 'name': 'Insurance', 'type': 'expense'},
        {'code': '6710', 'name': 'General Liability Insurance', 'type': 'expense', 'parent_code': '6700'},
        {'code': '6715', 'name': 'Professional Liability Insurance', 'type': 'expense', 'parent_code': '6700'},
        {'code': '6720', 'name': 'Property Insurance', 'type': 'expense', 'parent_code': '6700'},
        {'code': '6725', 'name': 'Vehicle Insurance', 'type': 'expense', 'parent_code': '6700'},
        {'code': '6730', 'name': 'Director & Officer Insurance', 'type': 'expense', 'parent_code': '6700'},
        
        # Depreciation & Amortization (6800-6899)
        {'code': '6800', 'name': 'Depreciation & Amortization', 'type': 'expense'},
        {'code': '6810', 'name': 'Depreciation Expense', 'type': 'expense', 'parent_code': '6800'},
        {'code': '6815', 'name': 'Amortization Expense', 'type': 'expense', 'parent_code': '6800'},
        
        # Other Operating Expenses (6900-6999)
        {'code': '6900', 'name': 'Other Operating Expenses', 'type': 'expense'},
        {'code': '6910', 'name': 'Research & Development', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6915', 'name': 'Licenses & Permits', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6920', 'name': 'Dues & Subscriptions', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6925', 'name': 'Bad Debt Expense', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6930', 'name': 'Charitable Contributions', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6935', 'name': 'Penalties & Fines', 'type': 'expense', 'parent_code': '6900'},
        
        # NON-OPERATING INCOME/EXPENSE (7000-7999)
        # =========================================
        
        # Other Expenses (7000-7999)
        {'code': '7000', 'name': 'Non-Operating Expenses', 'type': 'expense'},
        {'code': '7010', 'name': 'Interest Expense', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7015', 'name': 'Bank Interest Expense', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7020', 'name': 'Loan Interest Expense', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7030', 'name': 'Loss on Sale of Assets', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7040', 'name': 'Foreign Exchange Loss', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7050', 'name': 'Extraordinary Loss', 'type': 'expense', 'parent_code': '7000'},
        
        # Income Tax Expense (8000-8999)
        {'code': '8000', 'name': 'Income Tax Expense', 'type': 'expense'},
        {'code': '8010', 'name': 'Federal Income Tax', 'type': 'expense', 'parent_code': '8000'},
        {'code': '8015', 'name': 'State Income Tax', 'type': 'expense', 'parent_code': '8000'},
        {'code': '8020', 'name': 'Deferred Tax Expense', 'type': 'expense', 'parent_code': '8000'},
    ]
    
    # Create parent accounts first, then children
    parent_accounts = {}
    
    # First pass: create accounts without parents
    for account_data in accounts:
        if 'parent_code' not in account_data:
            # Add EdonuOps advanced features to all accounts
            allowed_dimensions = ["department", "project", "location", "cost_center"]
            
            account = ChartOfAccount(
                code=account_data['code'],
                account_name=account_data['name'],
                account_type=account_data['type'],
                currency='USD',
                allowed_dimensions=allowed_dimensions  # EdonuOps advanced feature
            )
            db.session.add(account)
            db.session.flush()  # Get the ID
            parent_accounts[account_data['code']] = account.id
            print(f"✅ Created parent account: {account_data['code']} - {account_data['name']}")
    
    # Second pass: create child accounts
    for account_data in accounts:
        if 'parent_code' in account_data:
            parent_id = parent_accounts.get(account_data['parent_code'])
            
            # Add EdonuOps advanced features to all child accounts too
            allowed_dimensions = ["department", "project", "location", "cost_center"]
            
            account = ChartOfAccount(
                code=account_data['code'],
                account_name=account_data['name'],
                account_type=account_data['type'],
                currency='USD',
                parent_id=parent_id,
                allowed_dimensions=allowed_dimensions  # EdonuOps advanced feature
            )
            db.session.add(account)
            print(f"✅ Created child account: {account_data['code']} - {account_data['name']} (parent: {account_data['parent_code']})")
    
    db.session.commit()
    print(f"🎉 Created {len(accounts)} Enhanced Chart of Accounts entries with EdonuOps advanced features!")
    print("📊 Features included:")
    print("   ✅ QuickBooks-compatible numbering system")
    print("   ✅ Detailed expense categorization")
    print("   ✅ Proper contra-asset accounts")
    print("   ✅ Credit card separation from AP")
    print("   ✅ Tax liability breakdown")
    print("   ✅ Multi-dimensional accounting (EdonuOps advantage)")
    print("   ✅ Multi-currency support (EdonuOps advantage)")
    print("   ✅ Hierarchical structure (EdonuOps advantage)")

def seed_users_and_roles():
    """Create initial users and roles"""
    
    # Check if roles already exist
    if Role.query.first():
        print("Roles already exist, skipping...")
        return
    
    # Create roles
    roles = [
        {'role_name': 'admin', 'permissions': ['*']},
        {'role_name': 'accountant', 'permissions': ['finance.*', 'reporting.*']},
        {'role_name': 'manager', 'permissions': ['inventory.*', 'crm.*', 'hr.*']},
        {'role_name': 'user', 'permissions': ['read.*']},
    ]
    
    for role_data in roles:
        role = Role(
            role_name=role_data['role_name'],
            permissions=role_data['permissions']
        )
        db.session.add(role)
        print(f"✅ Created role: {role_data['role_name']}")
    
    db.session.commit()
    
    # Create default organization
    if not Organization.query.first():
        org = Organization(name="EdonuOps Corporation")
        db.session.add(org)
        db.session.flush()
        org_id = org.id
        print("✅ Created default organization: EdonuOps Corporation")
    else:
        org_id = Organization.query.first().id
    
    # Create admin user
    if not User.query.filter_by(email='admin@edonuops.com').first():
        admin_role = Role.query.filter_by(role_name='admin').first()
        admin_user = User(
            username='admin',
            email='admin@edonuops.com',
            password_hash=generate_password_hash('password'),
            role_id=admin_role.id,
            organization_id=org_id
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Created admin user: admin@edonuops.com (password: password)")

def main():
    """Run all enhanced seed operations"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting ENHANCED EdonuOps database seeding...")
        print("📋 This will create a QuickBooks-compatible CoA with EdonuOps advanced features")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Seed data
        seed_users_and_roles()
        seed_enhanced_chart_of_accounts()
        
        print("🎉 Enhanced EdonuOps database seeding completed!")
        print("🚀 Your CoA now has:")
        print("   📊 150+ QuickBooks-standard accounts")
        print("   🌐 Multi-currency support")
        print("   📈 Dimensional accounting")
        print("   🏗️ Hierarchical structure")
        print("   💼 Enterprise-grade features")

if __name__ == '__main__':
    main()


