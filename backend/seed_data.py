#!/usr/bin/env python3
"""
Seed data script for EdonuOps
Creates initial Chart of Accounts and other essential data
"""

from app import create_app, db
from modules.finance.models import ChartOfAccount
from modules.core.models import User, Role, Organization
from werkzeug.security import generate_password_hash

def seed_chart_of_accounts():
    """Create standard Chart of Accounts structure"""
    
    # Check if accounts already exist
    if ChartOfAccount.query.first():
        print("Chart of Accounts already exists, skipping...")
        return
    
    accounts = [
        # ASSETS (1000-1999)
        {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': 'asset'},
        {'code': '1010', 'name': 'Petty Cash', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1020', 'name': 'Checking Account', 'type': 'asset', 'parent_code': '1000'},
        {'code': '1030', 'name': 'Savings Account', 'type': 'asset', 'parent_code': '1000'},
        
        {'code': '1100', 'name': 'Accounts Receivable', 'type': 'asset'},
        {'code': '1110', 'name': 'Trade Receivables', 'type': 'asset', 'parent_code': '1100'},
        {'code': '1120', 'name': 'Allowance for Doubtful Accounts', 'type': 'asset', 'parent_code': '1100'},
        
        {'code': '1200', 'name': 'Inventory', 'type': 'asset'},
        {'code': '1210', 'name': 'Raw Materials', 'type': 'asset', 'parent_code': '1200'},
        {'code': '1220', 'name': 'Work in Process', 'type': 'asset', 'parent_code': '1200'},
        {'code': '1230', 'name': 'Finished Goods', 'type': 'asset', 'parent_code': '1200'},
        
        {'code': '1500', 'name': 'Fixed Assets', 'type': 'asset'},
        {'code': '1510', 'name': 'Property, Plant & Equipment', 'type': 'asset', 'parent_code': '1500'},
        {'code': '1520', 'name': 'Accumulated Depreciation', 'type': 'asset', 'parent_code': '1500'},
        
        # LIABILITIES (2000-2999)
        {'code': '2000', 'name': 'Current Liabilities', 'type': 'liability'},
        {'code': '2010', 'name': 'Accounts Payable', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2020', 'name': 'Accrued Expenses', 'type': 'liability', 'parent_code': '2000'},
        {'code': '2030', 'name': 'Short-term Debt', 'type': 'liability', 'parent_code': '2000'},
        
        {'code': '2100', 'name': 'Payroll Liabilities', 'type': 'liability'},
        {'code': '2110', 'name': 'Salaries Payable', 'type': 'liability', 'parent_code': '2100'},
        {'code': '2120', 'name': 'Payroll Tax Payable', 'type': 'liability', 'parent_code': '2100'},
        
        {'code': '2500', 'name': 'Long-term Liabilities', 'type': 'liability'},
        {'code': '2510', 'name': 'Long-term Debt', 'type': 'liability', 'parent_code': '2500'},
        
        # EQUITY (3000-3999)
        {'code': '3000', 'name': 'Equity', 'type': 'equity'},
        {'code': '3010', 'name': 'Common Stock', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3020', 'name': 'Retained Earnings', 'type': 'equity', 'parent_code': '3000'},
        {'code': '3030', 'name': 'Owner Drawings', 'type': 'equity', 'parent_code': '3000'},
        
        # REVENUE (4000-4999)
        {'code': '4000', 'name': 'Revenue', 'type': 'revenue'},
        {'code': '4010', 'name': 'Sales Revenue', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4020', 'name': 'Service Revenue', 'type': 'revenue', 'parent_code': '4000'},
        {'code': '4030', 'name': 'Other Revenue', 'type': 'revenue', 'parent_code': '4000'},
        
        # EXPENSES (5000-5999)
        {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'expense'},
        {'code': '5010', 'name': 'Materials Cost', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5020', 'name': 'Labor Cost', 'type': 'expense', 'parent_code': '5000'},
        {'code': '5030', 'name': 'Manufacturing Overhead', 'type': 'expense', 'parent_code': '5000'},
        
        {'code': '6000', 'name': 'Operating Expenses', 'type': 'expense'},
        {'code': '6010', 'name': 'Salaries and Wages', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6020', 'name': 'Rent Expense', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6030', 'name': 'Utilities Expense', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6040', 'name': 'Office Supplies', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6050', 'name': 'Professional Services', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6060', 'name': 'Marketing and Advertising', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6070', 'name': 'Travel and Entertainment', 'type': 'expense', 'parent_code': '6000'},
        {'code': '6080', 'name': 'Depreciation Expense', 'type': 'expense', 'parent_code': '6000'},
    ]
    
    # Create parent accounts first, then children
    parent_accounts = {}
    
    # First pass: create accounts without parents
    for account_data in accounts:
        if 'parent_code' not in account_data:
            account = ChartOfAccount(
                code=account_data['code'],
                account_name=account_data['name'],
                account_type=account_data['type'],
                currency='USD'
            )
            db.session.add(account)
            db.session.flush()  # Get the ID
            parent_accounts[account_data['code']] = account.id
            print(f"Created parent account: {account_data['code']} - {account_data['name']}")
    
    # Second pass: create child accounts
    for account_data in accounts:
        if 'parent_code' in account_data:
            parent_id = parent_accounts.get(account_data['parent_code'])
            account = ChartOfAccount(
                code=account_data['code'],
                account_name=account_data['name'],
                account_type=account_data['type'],
                currency='USD',
                parent_id=parent_id
            )
            db.session.add(account)
            print(f"Created child account: {account_data['code']} - {account_data['name']} (parent: {account_data['parent_code']})")
    
    db.session.commit()
    print(f"✅ Created {len(accounts)} Chart of Accounts entries")

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
        print(f"Created role: {role_data['role_name']}")
    
    db.session.commit()
    
    # Create default organization
    if not Organization.query.first():
        org = Organization(name="Default Organization")
        db.session.add(org)
        db.session.flush()
        org_id = org.id
        print("Created default organization")
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
    """Run all seed operations"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Seed data
        seed_users_and_roles()
        seed_chart_of_accounts()
        
        print("🎉 Database seeding completed!")

if __name__ == '__main__':
    main()
