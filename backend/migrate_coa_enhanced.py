#!/usr/bin/env python3
"""
Chart of Accounts Migration Script for EdonuOps
Migrates existing basic CoA to QuickBooks-compatible structure while preserving data
"""

from app import create_app, db
from modules.finance.models import ChartOfAccount
from sqlalchemy import text
import json

def backup_existing_accounts():
    """Backup existing accounts before migration"""
    existing_accounts = ChartOfAccount.query.all()
    backup_data = []
    
    for account in existing_accounts:
        backup_data.append({
            'id': account.id,
            'code': account.code,
            'name': account.account_name,
            'type': account.account_type,
            'balance': account.get_balance(),
            'currency': account.currency,
            'parent_id': account.parent_id,
            'is_active': account.is_active,
            'allowed_dimensions': account.allowed_dimensions
        })
    
    # Save backup to file
    with open('coa_backup.json', 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"✅ Backed up {len(backup_data)} existing accounts to coa_backup.json")
    return backup_data

def enhance_existing_accounts():
    """Add EdonuOps advanced features to existing accounts"""
    accounts = ChartOfAccount.query.all()
    enhanced_count = 0
    
    for account in accounts:
        # Add dimensional accounting if not present
        if not account.allowed_dimensions:
            account.allowed_dimensions = ["department", "project", "location", "cost_center"]
            enhanced_count += 1
            print(f"✅ Enhanced account {account.code} - {account.account_name} with dimensions")
    
    db.session.commit()
    print(f"🚀 Enhanced {enhanced_count} existing accounts with dimensional accounting")

def add_missing_quickbooks_accounts():
    """Add missing QuickBooks-standard accounts"""
    
    # Get existing account codes to avoid duplicates
    existing_codes = {acc.code for acc in ChartOfAccount.query.all()}
    
    # Additional QuickBooks-standard accounts not in our basic setup
    additional_accounts = [
        # Missing Asset Accounts
        {'code': '1040', 'name': 'Money Market Account', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1050', 'name': 'Undeposited Funds', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1115', 'name': 'Other Receivables', 'type': 'asset', 'parent_code': '1100'},
        {'code': '1240', 'name': 'Inventory Asset', 'type': 'asset', 'parent_code': '1200'},
        {'code': '1300', 'name': 'Other Current Assets', 'type': 'asset'},
        {'code': '1310', 'name': 'Prepaid Expenses', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1315', 'name': 'Prepaid Insurance', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1320', 'name': 'Prepaid Rent', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1330', 'name': 'Deposits', 'type': 'asset', 'parent_code': '1300'},
        {'code': '1340', 'name': 'Tax Refunds Receivable', 'type': 'asset', 'parent_code': '1300'},
        
        # Enhanced Fixed Assets with Accumulated Depreciation
        {'code': '1510', 'name': 'Land', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1525', 'name': 'Accumulated Depreciation - Buildings', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1535', 'name': 'Accumulated Depreciation - Equipment', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1540', 'name': 'Furniture & Fixtures', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1545', 'name': 'Accumulated Depreciation - Furniture', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1550', 'name': 'Vehicles', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1555', 'name': 'Accumulated Depreciation - Vehicles', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1560', 'name': 'Computer Equipment', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1565', 'name': 'Accumulated Depreciation - Computer Equipment', 'type': 'asset', 'parent_code': '1500'},
        
        # Other Assets
        {'code': '1700', 'name': 'Other Assets', 'type': 'asset'},
        {'code': '1710', 'name': 'Intangible Assets', 'type': 'asset', 'parent_code': '1700'},
        {'code': '1720', 'name': 'Goodwill', 'type': 'asset', 'parent_code': '1700'},
        
        # Credit Cards (separate from AP)
        {'code': '2110', 'name': 'Business Credit Card', 'type': 'liability', 'parent_code': '2100'},
        {'code': '2115', 'name': 'Corporate Credit Card', 'type': 'liability', 'parent_code': '2100'},
        
        # Tax Liabilities
        {'code': '2200', 'name': 'Tax Liabilities', 'type': 'liability'},
        {'code': '2210', 'name': 'Federal Income Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2215', 'name': 'State Income Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2220', 'name': 'Sales Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2225', 'name': 'Payroll Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2230', 'name': 'Social Security Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2235', 'name': 'Medicare Payable', 'type': 'liability', 'parent_code': '2200'},
        {'code': '2240', 'name': 'Unemployment Tax Payable', 'type': 'liability', 'parent_code': '2200'},
        
        # Enhanced Equity Structure
        {'code': '3015', 'name': 'Preferred Stock', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3025', 'name': 'Additional Paid-in Capital', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3035', 'name': 'Current Year Earnings', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3040', 'name': 'Treasury Stock', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3050', 'name': 'Owner\'s Equity', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3060', 'name': 'Owner Withdrawals', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3070', 'name': 'Dividends', 'type': 'equity', 'parent_code': '3000'},
        
        # Enhanced Revenue Structure
        {'code': '4025', 'name': 'Consulting Revenue', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4035', 'name': 'Sales Discounts', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4040', 'name': 'Shipping & Handling Revenue', 'type': 'revenue', 'parent_code': '4000'},
        
        # Other Income
        {'code': '4800', 'name': 'Other Income', 'type': 'revenue'},
        {'code': '4810', 'name': 'Interest Income', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4820', 'name': 'Dividend Income', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4830', 'name': 'Rental Income', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4840', 'name': 'Gain on Sale of Assets', 'type': 'revenue', 'parent_code': '4800'},
        {'code': '4850', 'name': 'Foreign Exchange Gain', 'type': 'revenue', 'parent_code': '4800'},
        
        # Enhanced Cost of Sales
        {'code': '5040', 'name': 'Freight & Shipping', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5050', 'name': 'Cost of Services', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5060', 'name': 'Subcontractor Costs', 'type': 'expense', 'parent_code': '5000'},
        
        # Detailed Operating Expenses
        {'code': '6100', 'name': 'Facility Expenses', 'type': 'expense'},
        {'code': '6115', 'name': 'Property Taxes', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6125', 'name': 'Electricity', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6130', 'name': 'Gas', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6135', 'name': 'Water & Sewer', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6140', 'name': 'Telecommunications', 'type': 'expense', 'parent_code': '6100'},
        {'code': '6145', 'name': 'Internet & Phone', 'type': 'expense', 'parent_code': '6100'},
        
        # Technology Expenses
        {'code': '6200', 'name': 'Technology Expenses', 'type': 'expense'},
        {'code': '6210', 'name': 'Software Licenses', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6215', 'name': 'Software Subscriptions', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6225', 'name': 'IT Support & Maintenance', 'type': 'expense', 'parent_code': '6200'},
        {'code': '6230', 'name': 'Cloud Services', 'type': 'expense', 'parent_code': '6200'},
        
        # Professional Services
        {'code': '6300', 'name': 'Professional Services', 'type': 'expense'},
        {'code': '6310', 'name': 'Accounting & Bookkeeping', 'type': 'expense', 'parent_code': '6300'},
        {'code': '6315', 'name': 'Legal Fees', 'type': 'expense', 'parent_code': '6300'},
        {'code': '6320', 'name': 'Consulting Fees', 'type': 'expense', 'parent_code': '6300'},
        {'code': '6325', 'name': 'Audit Fees', 'type': 'expense', 'parent_code': '6300'},
        
        # Marketing & Sales
        {'code': '6400', 'name': 'Marketing & Sales', 'type': 'expense'},
        {'code': '6410', 'name': 'Advertising', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6415', 'name': 'Digital Marketing', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6420', 'name': 'Trade Shows & Events', 'type': 'expense', 'parent_code': '6400'},
        {'code': '6425', 'name': 'Sales Commissions', 'type': 'expense', 'parent_code': '6400'},
        
        # Travel & Transportation
        {'code': '6500', 'name': 'Travel & Transportation', 'type': 'expense'},
        {'code': '6510', 'name': 'Business Travel', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6515', 'name': 'Airfare', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6520', 'name': 'Hotels & Lodging', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6525', 'name': 'Meals & Entertainment', 'type': 'expense', 'parent_code': '6500'},
        {'code': '6530', 'name': 'Vehicle Expenses', 'type': 'expense', 'parent_code': '6500'},
        
        # Office & Administrative
        {'code': '6600', 'name': 'Office & Administrative', 'type': 'expense'},
        {'code': '6625', 'name': 'Bank Fees', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6630', 'name': 'Credit Card Fees', 'type': 'expense', 'parent_code': '6600'},
        {'code': '6635', 'name': 'Merchant Processing Fees', 'type': 'expense', 'parent_code': '6600'},
        
        # Insurance
        {'code': '6700', 'name': 'Insurance', 'type': 'expense'},
        {'code': '6710', 'name': 'General Liability Insurance', 'type': 'expense', 'parent_code': '6700'},
        {'code': '6715', 'name': 'Professional Liability Insurance', 'type': 'expense', 'parent_code': '6700'},
        {'code': '6720', 'name': 'Property Insurance', 'type': 'expense', 'parent_code': '6700'},
        {'code': '6725', 'name': 'Vehicle Insurance', 'type': 'expense', 'parent_code': '6700'},
        
        # Other Operating Expenses
        {'code': '6900', 'name': 'Other Operating Expenses', 'type': 'expense'},
        {'code': '6910', 'name': 'Research & Development', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6915', 'name': 'Licenses & Permits', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6925', 'name': 'Bad Debt Expense', 'type': 'expense', 'parent_code': '6900'},
        {'code': '6930', 'name': 'Charitable Contributions', 'type': 'expense', 'parent_code': '6900'},
        
        # Non-Operating Expenses
        {'code': '7000', 'name': 'Non-Operating Expenses', 'type': 'expense'},
        {'code': '7010', 'name': 'Interest Expense', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7015', 'name': 'Bank Interest Expense', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7030', 'name': 'Loss on Sale of Assets', 'type': 'expense', 'parent_code': '7000'},
        {'code': '7040', 'name': 'Foreign Exchange Loss', 'type': 'expense', 'parent_code': '7000'},
        
        # Income Tax Expense
        {'code': '8000', 'name': 'Income Tax Expense', 'type': 'expense'},
        {'code': '8010', 'name': 'Federal Income Tax', 'type': 'expense', 'parent_code': '8000'},
        {'code': '8015', 'name': 'State Income Tax', 'type': 'expense', 'parent_code': '8000'},
    ]
    
    # Find parent account IDs
    parent_accounts = {}
    for account in ChartOfAccount.query.all():
        parent_accounts[account.code] = account.id
    
    added_count = 0
    
    # First pass: Add parent accounts
    for account_data in additional_accounts:
        if account_data['code'] not in existing_codes and 'parent_code' not in account_data:
            account = ChartOfAccount(
                code=account_data['code'],
                account_name=account_data['name'],
                account_type=account_data['type'],
                currency='USD',
                allowed_dimensions=["department", "project", "location", "cost_center"]
            )
            db.session.add(account)
            db.session.flush()
            parent_accounts[account_data['code']] = account.id
            existing_codes.add(account_data['code'])
            added_count += 1
            print(f"✅ Added parent account: {account_data['code']} - {account_data['name']}")
    
    # Second pass: Add child accounts
    for account_data in additional_accounts:
        if account_data['code'] not in existing_codes and 'parent_code' in account_data:
            parent_id = parent_accounts.get(account_data['parent_code'])
            if parent_id:
                account = ChartOfAccount(
                    code=account_data['code'],
                    account_name=account_data['name'],
                    account_type=account_data['type'],
                    currency='USD',
                    parent_id=parent_id,
                    allowed_dimensions=["department", "project", "location", "cost_center"]
                )
                db.session.add(account)
                added_count += 1
                print(f"✅ Added child account: {account_data['code']} - {account_data['name']} (parent: {account_data['parent_code']})")
    
    db.session.commit()
    print(f"🚀 Added {added_count} new QuickBooks-standard accounts")

def main():
    """Run the Chart of Accounts migration"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting Chart of Accounts Enhancement Migration...")
        print("📋 This will enhance your existing CoA with QuickBooks-standard accounts")
        
        # Step 1: Backup existing accounts
        backup_data = backup_existing_accounts()
        
        # Step 2: Enhance existing accounts with dimensions
        enhance_existing_accounts()
        
        # Step 3: Add missing QuickBooks-standard accounts
        add_missing_quickbooks_accounts()
        
        # Final report
        total_accounts = ChartOfAccount.query.count()
        print("\n🎉 Chart of Accounts Enhancement Complete!")
        print(f"📊 Total accounts in system: {total_accounts}")
        print("🚀 Your enhanced CoA now includes:")
        print("   ✅ QuickBooks-compatible numbering system")
        print("   ✅ Detailed expense categorization")
        print("   ✅ Proper contra-asset accounts")
        print("   ✅ Credit card separation from AP")
        print("   ✅ Tax liability breakdown")
        print("   ✅ Multi-dimensional accounting (EdonuOps advantage)")
        print("   ✅ Multi-currency support (EdonuOps advantage)")
        print("   ✅ Hierarchical structure (EdonuOps advantage)")
        print(f"📁 Backup saved to: coa_backup.json")

if __name__ == '__main__':
    main()


