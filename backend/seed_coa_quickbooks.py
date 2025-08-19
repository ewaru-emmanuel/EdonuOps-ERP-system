#!/usr/bin/env python3
"""
QuickBooks-Style Chart of Accounts Seeder
Creates a professionally organized CoA matching QuickBooks structure
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from modules.finance.models import ChartOfAccount

def create_quickbooks_coa():
    """Create a QuickBooks-style Chart of Accounts"""
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing accounts first
            print("🧹 Clearing existing Chart of Accounts...")
            existing_count = ChartOfAccount.query.count()
            if existing_count > 0:
                ChartOfAccount.query.delete()
                db.session.commit()
                print(f"✅ Cleared {existing_count} existing accounts")
            
            print("🏗️  Creating QuickBooks-style Chart of Accounts...")
            
            # QuickBooks Standard Chart of Accounts
            accounts_data = [
                # ========== ASSETS (1000-1999) ==========
                {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': 'asset', 'parent': None},
                {'code': '1001', 'name': 'Checking Account', 'type': 'asset', 'parent': '1000'},
                {'code': '1002', 'name': 'Savings Account', 'type': 'asset', 'parent': '1000'},
                {'code': '1003', 'name': 'Money Market Account', 'type': 'asset', 'parent': '1000'},
                {'code': '1010', 'name': 'Petty Cash', 'type': 'asset', 'parent': '1000'},
                {'code': '1020', 'name': 'Undeposited Funds', 'type': 'asset', 'parent': '1000'},
                
                {'code': '1100', 'name': 'Accounts Receivable', 'type': 'asset', 'parent': None},
                {'code': '1110', 'name': 'Trade Receivables', 'type': 'asset', 'parent': '1100'},
                {'code': '1120', 'name': 'Employee Advances', 'type': 'asset', 'parent': '1100'},
                {'code': '1130', 'name': 'Allowance for Doubtful Accounts', 'type': 'asset', 'parent': '1100'},
                
                {'code': '1200', 'name': 'Inventory', 'type': 'asset', 'parent': None},
                {'code': '1210', 'name': 'Inventory Asset', 'type': 'asset', 'parent': '1200'},
                {'code': '1220', 'name': 'Work in Progress', 'type': 'asset', 'parent': '1200'},
                {'code': '1230', 'name': 'Finished Goods', 'type': 'asset', 'parent': '1200'},
                
                {'code': '1300', 'name': 'Other Current Assets', 'type': 'asset', 'parent': None},
                {'code': '1310', 'name': 'Prepaid Expenses', 'type': 'asset', 'parent': '1300'},
                {'code': '1320', 'name': 'Prepaid Insurance', 'type': 'asset', 'parent': '1300'},
                {'code': '1330', 'name': 'Prepaid Rent', 'type': 'asset', 'parent': '1300'},
                {'code': '1340', 'name': 'Security Deposits', 'type': 'asset', 'parent': '1300'},
                {'code': '1350', 'name': 'Short-term Investments', 'type': 'asset', 'parent': '1300'},
                
                {'code': '1500', 'name': 'Fixed Assets', 'type': 'asset', 'parent': None},
                {'code': '1510', 'name': 'Furniture & Fixtures', 'type': 'asset', 'parent': '1500'},
                {'code': '1511', 'name': 'Accumulated Depreciation - Furniture', 'type': 'asset', 'parent': '1500'},
                {'code': '1520', 'name': 'Equipment', 'type': 'asset', 'parent': '1500'},
                {'code': '1521', 'name': 'Accumulated Depreciation - Equipment', 'type': 'asset', 'parent': '1500'},
                {'code': '1530', 'name': 'Vehicles', 'type': 'asset', 'parent': '1500'},
                {'code': '1531', 'name': 'Accumulated Depreciation - Vehicles', 'type': 'asset', 'parent': '1500'},
                {'code': '1540', 'name': 'Buildings', 'type': 'asset', 'parent': '1500'},
                {'code': '1541', 'name': 'Accumulated Depreciation - Buildings', 'type': 'asset', 'parent': '1500'},
                {'code': '1550', 'name': 'Computer Equipment', 'type': 'asset', 'parent': '1500'},
                {'code': '1551', 'name': 'Accumulated Depreciation - Computer Equipment', 'type': 'asset', 'parent': '1500'},
                
                {'code': '1700', 'name': 'Other Assets', 'type': 'asset', 'parent': None},
                {'code': '1710', 'name': 'Long-term Investments', 'type': 'asset', 'parent': '1700'},
                {'code': '1720', 'name': 'Intangible Assets', 'type': 'asset', 'parent': '1700'},
                {'code': '1721', 'name': 'Accumulated Amortization - Intangibles', 'type': 'asset', 'parent': '1700'},
                {'code': '1730', 'name': 'Goodwill', 'type': 'asset', 'parent': '1700'},
                
                # ========== LIABILITIES (2000-2999) ==========
                {'code': '2000', 'name': 'Accounts Payable', 'type': 'liability', 'parent': None},
                {'code': '2010', 'name': 'Trade Payables', 'type': 'liability', 'parent': '2000'},
                {'code': '2020', 'name': 'Accrued Expenses', 'type': 'liability', 'parent': '2000'},
                
                {'code': '2100', 'name': 'Credit Cards', 'type': 'liability', 'parent': None},
                {'code': '2110', 'name': 'Business Credit Card', 'type': 'liability', 'parent': '2100'},
                {'code': '2120', 'name': 'Company Credit Line', 'type': 'liability', 'parent': '2100'},
                
                {'code': '2200', 'name': 'Tax Liabilities', 'type': 'liability', 'parent': None},
                {'code': '2210', 'name': 'Sales Tax Payable', 'type': 'liability', 'parent': '2200'},
                {'code': '2220', 'name': 'Federal Income Tax Payable', 'type': 'liability', 'parent': '2200'},
                {'code': '2230', 'name': 'State Income Tax Payable', 'type': 'liability', 'parent': '2200'},
                {'code': '2240', 'name': 'Payroll Tax Payable', 'type': 'liability', 'parent': '2200'},
                {'code': '2250', 'name': 'Employment Tax Payable', 'type': 'liability', 'parent': '2200'},
                
                {'code': '2300', 'name': 'Payroll Liabilities', 'type': 'liability', 'parent': None},
                {'code': '2310', 'name': 'Wages Payable', 'type': 'liability', 'parent': '2300'},
                {'code': '2320', 'name': 'Vacation Payable', 'type': 'liability', 'parent': '2300'},
                {'code': '2330', 'name': 'Employee Benefits Payable', 'type': 'liability', 'parent': '2300'},
                
                {'code': '2500', 'name': 'Long-term Debt', 'type': 'liability', 'parent': None},
                {'code': '2510', 'name': 'Notes Payable', 'type': 'liability', 'parent': '2500'},
                {'code': '2520', 'name': 'Bank Loans', 'type': 'liability', 'parent': '2500'},
                {'code': '2530', 'name': 'Equipment Loans', 'type': 'liability', 'parent': '2500'},
                
                # ========== EQUITY (3000-3999) ==========
                {'code': '3000', 'name': 'Equity', 'type': 'equity', 'parent': None},
                {'code': '3010', 'name': 'Common Stock', 'type': 'equity', 'parent': '3000'},
                {'code': '3020', 'name': 'Preferred Stock', 'type': 'equity', 'parent': '3000'},
                {'code': '3030', 'name': 'Retained Earnings', 'type': 'equity', 'parent': '3000'},
                {'code': '3040', 'name': 'Owner\'s Equity', 'type': 'equity', 'parent': '3000'},
                {'code': '3050', 'name': 'Owner\'s Draw', 'type': 'equity', 'parent': '3000'},
                {'code': '3060', 'name': 'Dividends Paid', 'type': 'equity', 'parent': '3000'},
                
                # ========== REVENUE (4000-4999) ==========
                {'code': '4000', 'name': 'Revenue', 'type': 'revenue', 'parent': None},
                {'code': '4010', 'name': 'Product Sales', 'type': 'revenue', 'parent': '4000'},
                {'code': '4020', 'name': 'Service Revenue', 'type': 'revenue', 'parent': '4000'},
                {'code': '4030', 'name': 'Consulting Revenue', 'type': 'revenue', 'parent': '4000'},
                {'code': '4040', 'name': 'Subscription Revenue', 'type': 'revenue', 'parent': '4000'},
                {'code': '4050', 'name': 'License Revenue', 'type': 'revenue', 'parent': '4000'},
                
                {'code': '4800', 'name': 'Other Income', 'type': 'revenue', 'parent': None},
                {'code': '4810', 'name': 'Interest Income', 'type': 'revenue', 'parent': '4800'},
                {'code': '4820', 'name': 'Dividend Income', 'type': 'revenue', 'parent': '4800'},
                {'code': '4830', 'name': 'Gain on Sale of Assets', 'type': 'revenue', 'parent': '4800'},
                {'code': '4840', 'name': 'Miscellaneous Income', 'type': 'revenue', 'parent': '4800'},
                
                # ========== COST OF GOODS SOLD (5000-5999) ==========
                {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'expense', 'parent': None},
                {'code': '5010', 'name': 'Cost of Materials', 'type': 'expense', 'parent': '5000'},
                {'code': '5020', 'name': 'Direct Labor', 'type': 'expense', 'parent': '5000'},
                {'code': '5030', 'name': 'Manufacturing Overhead', 'type': 'expense', 'parent': '5000'},
                {'code': '5040', 'name': 'Subcontractor Costs', 'type': 'expense', 'parent': '5000'},
                {'code': '5050', 'name': 'Freight & Shipping', 'type': 'expense', 'parent': '5000'},
                
                # ========== OPERATING EXPENSES (6000-6999) ==========
                {'code': '6000', 'name': 'Payroll Expenses', 'type': 'expense', 'parent': None},
                {'code': '6010', 'name': 'Salaries & Wages', 'type': 'expense', 'parent': '6000'},
                {'code': '6020', 'name': 'Employee Benefits', 'type': 'expense', 'parent': '6000'},
                {'code': '6030', 'name': 'Payroll Taxes', 'type': 'expense', 'parent': '6000'},
                {'code': '6040', 'name': 'Workers Compensation', 'type': 'expense', 'parent': '6000'},
                {'code': '6050', 'name': 'Retirement Contributions', 'type': 'expense', 'parent': '6000'},
                
                {'code': '6100', 'name': 'Facility Expenses', 'type': 'expense', 'parent': None},
                {'code': '6110', 'name': 'Rent Expense', 'type': 'expense', 'parent': '6100'},
                {'code': '6120', 'name': 'Utilities', 'type': 'expense', 'parent': '6100'},
                {'code': '6130', 'name': 'Building Maintenance', 'type': 'expense', 'parent': '6100'},
                {'code': '6140', 'name': 'Property Taxes', 'type': 'expense', 'parent': '6100'},
                {'code': '6150', 'name': 'Security Services', 'type': 'expense', 'parent': '6100'},
                
                {'code': '6200', 'name': 'Technology Expenses', 'type': 'expense', 'parent': None},
                {'code': '6210', 'name': 'Software Subscriptions', 'type': 'expense', 'parent': '6200'},
                {'code': '6220', 'name': 'Cloud Computing', 'type': 'expense', 'parent': '6200'},
                {'code': '6230', 'name': 'IT Support & Maintenance', 'type': 'expense', 'parent': '6200'},
                {'code': '6240', 'name': 'Computer Equipment', 'type': 'expense', 'parent': '6200'},
                {'code': '6250', 'name': 'Internet & Communications', 'type': 'expense', 'parent': '6200'},
                
                {'code': '6300', 'name': 'Professional Services', 'type': 'expense', 'parent': None},
                {'code': '6310', 'name': 'Legal Fees', 'type': 'expense', 'parent': '6300'},
                {'code': '6320', 'name': 'Accounting & Tax Preparation', 'type': 'expense', 'parent': '6300'},
                {'code': '6330', 'name': 'Consulting Fees', 'type': 'expense', 'parent': '6300'},
                {'code': '6340', 'name': 'Audit Fees', 'type': 'expense', 'parent': '6300'},
                {'code': '6350', 'name': 'Professional Development', 'type': 'expense', 'parent': '6300'},
                
                {'code': '6400', 'name': 'Marketing & Sales', 'type': 'expense', 'parent': None},
                {'code': '6410', 'name': 'Advertising', 'type': 'expense', 'parent': '6400'},
                {'code': '6420', 'name': 'Digital Marketing', 'type': 'expense', 'parent': '6400'},
                {'code': '6430', 'name': 'Trade Shows & Events', 'type': 'expense', 'parent': '6400'},
                {'code': '6440', 'name': 'Sales Commissions', 'type': 'expense', 'parent': '6400'},
                {'code': '6450', 'name': 'Marketing Materials', 'type': 'expense', 'parent': '6400'},
                
                {'code': '6500', 'name': 'Travel & Transportation', 'type': 'expense', 'parent': None},
                {'code': '6510', 'name': 'Business Travel', 'type': 'expense', 'parent': '6500'},
                {'code': '6520', 'name': 'Meals & Entertainment', 'type': 'expense', 'parent': '6500'},
                {'code': '6530', 'name': 'Vehicle Expenses', 'type': 'expense', 'parent': '6500'},
                {'code': '6540', 'name': 'Fuel & Gas', 'type': 'expense', 'parent': '6500'},
                
                {'code': '6600', 'name': 'Office & Administrative', 'type': 'expense', 'parent': None},
                {'code': '6610', 'name': 'Office Supplies', 'type': 'expense', 'parent': '6600'},
                {'code': '6620', 'name': 'Postage & Shipping', 'type': 'expense', 'parent': '6600'},
                {'code': '6630', 'name': 'Telephone & Internet', 'type': 'expense', 'parent': '6600'},
                {'code': '6640', 'name': 'Bank Fees', 'type': 'expense', 'parent': '6600'},
                {'code': '6650', 'name': 'Licenses & Permits', 'type': 'expense', 'parent': '6600'},
                
                {'code': '6700', 'name': 'Insurance', 'type': 'expense', 'parent': None},
                {'code': '6710', 'name': 'General Liability Insurance', 'type': 'expense', 'parent': '6700'},
                {'code': '6720', 'name': 'Professional Liability Insurance', 'type': 'expense', 'parent': '6700'},
                {'code': '6730', 'name': 'Property Insurance', 'type': 'expense', 'parent': '6700'},
                {'code': '6740', 'name': 'Vehicle Insurance', 'type': 'expense', 'parent': '6700'},
                {'code': '6750', 'name': 'Health Insurance', 'type': 'expense', 'parent': '6700'},
                
                {'code': '6800', 'name': 'Depreciation & Amortization', 'type': 'expense', 'parent': None},
                {'code': '6810', 'name': 'Depreciation Expense', 'type': 'expense', 'parent': '6800'},
                {'code': '6820', 'name': 'Amortization Expense', 'type': 'expense', 'parent': '6800'},
                
                {'code': '6900', 'name': 'Other Operating Expenses', 'type': 'expense', 'parent': None},
                {'code': '6910', 'name': 'Research & Development', 'type': 'expense', 'parent': '6900'},
                {'code': '6920', 'name': 'Bad Debt Expense', 'type': 'expense', 'parent': '6900'},
                {'code': '6930', 'name': 'Miscellaneous Expenses', 'type': 'expense', 'parent': '6900'},
                
                # ========== NON-OPERATING EXPENSES (7000-7999) ==========
                {'code': '7000', 'name': 'Non-Operating Expenses', 'type': 'expense', 'parent': None},
                {'code': '7010', 'name': 'Interest Expense', 'type': 'expense', 'parent': '7000'},
                {'code': '7020', 'name': 'Loss on Sale of Assets', 'type': 'expense', 'parent': '7000'},
                {'code': '7030', 'name': 'Foreign Exchange Loss', 'type': 'expense', 'parent': '7000'},
                
                # ========== INCOME TAX (8000-8999) ==========
                {'code': '8000', 'name': 'Income Tax Expense', 'type': 'expense', 'parent': None},
                {'code': '8010', 'name': 'Federal Income Tax', 'type': 'expense', 'parent': '8000'},
                {'code': '8020', 'name': 'State Income Tax', 'type': 'expense', 'parent': '8000'},
                {'code': '8030', 'name': 'Local Income Tax', 'type': 'expense', 'parent': '8000'},
            ]
            
            # First pass: Create parent accounts
            parent_accounts = {}
            created_count = 0
            
            print("📋 Creating parent accounts...")
            for account_data in accounts_data:
                if account_data['parent'] is None:
                    account = ChartOfAccount(
                        code=account_data['code'],
                        account_name=account_data['name'],
                        account_type=account_data['type'],
                        currency='USD',
                        is_active=True,
                        allowed_dimensions=["department", "project", "location", "cost_center"]
                    )
                    db.session.add(account)
                    db.session.flush()
                    parent_accounts[account_data['code']] = account.id
                    created_count += 1
            
            print("📂 Creating child accounts...")
            # Second pass: Create child accounts
            for account_data in accounts_data:
                if account_data['parent'] is not None:
                    parent_id = parent_accounts.get(account_data['parent'])
                    if parent_id:
                        account = ChartOfAccount(
                            code=account_data['code'],
                            account_name=account_data['name'],
                            account_type=account_data['type'],
                            currency='USD',
                            is_active=True,
                            parent_id=parent_id,
                            allowed_dimensions=["department", "project", "location", "cost_center"]
                        )
                        db.session.add(account)
                        created_count += 1
            
            db.session.commit()
            
            print(f"✅ Successfully created {created_count} accounts")
            print("🎯 QuickBooks-style Chart of Accounts is ready!")
            print("\n📊 Account Summary:")
            print("  • Assets: 1000-1999")
            print("  • Liabilities: 2000-2999") 
            print("  • Equity: 3000-3999")
            print("  • Revenue: 4000-4999")
            print("  • Cost of Goods Sold: 5000-5999")
            print("  • Operating Expenses: 6000-6999")
            print("  • Non-Operating Expenses: 7000-7999")
            print("  • Income Tax: 8000-8999")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating Chart of Accounts: {e}")
            raise

if __name__ == "__main__":
    print("🏦 EdonuOps - QuickBooks-Style Chart of Accounts")
    print("=" * 60)
    create_quickbooks_coa()



