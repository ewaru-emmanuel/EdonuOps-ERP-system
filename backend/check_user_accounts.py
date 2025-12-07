#!/usr/bin/env python3
"""
Check User Accounts Script
===========================

This script checks if accounts exist in the database for a specific user.
Used to verify default accounts creation and tenant isolation.
"""

import os
import sys
from sqlalchemy import text

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import User
from modules.core.tenant_helpers import get_current_user_tenant_id
from modules.finance.models import Account

def check_user_accounts(user_id):
    """Check accounts for a specific user"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print(f"CHECKING ACCOUNTS FOR USER {user_id}")
        print("=" * 60)
        print()
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User {user_id} not found")
            return
        
        print(f"✅ User found: {user.username} ({user.email})")
        print(f"   Role: {user.role.role_name if user.role else 'No role'}")
        print(f"   Tenant ID: {user.tenant_id}")
        print()
        
        # Get accounts for this tenant
        if not user.tenant_id:
            print("❌ User has no tenant_id")
            return
        
        print(f"🔍 Searching for accounts with tenant_id: {user.tenant_id}")
        print()
        
        # Query accounts using tenant_query helper
        try:
            from modules.core.tenant_query_helper import tenant_query
            
            # Temporarily set tenant context for this user
            from flask import g
            g.current_user_id = str(user_id)
            g.current_user_tenant_id = user.tenant_id
            
            accounts = tenant_query(Account).order_by(Account.code).all()
            
            print(f"📊 Found {len(accounts)} accounts for tenant {user.tenant_id}")
            print()
            
            if accounts:
                print("ACCOUNTS LIST:")
                print("-" * 60)
                for account in accounts:
                    print(f"  Code: {account.code:6} | Name: {account.name:40} | Type: {account.type:15} | Active: {account.is_active}")
                print("-" * 60)
                print()
                
                # Check for default account codes
                default_codes = {
                    '1000', '1100', '1200', '1300', '1400', '1500',  # Assets
                    '2000', '2100', '2200', '2300',  # Liabilities
                    '3000', '3100', '3200',  # Equity
                    '4000', '4100',  # Revenue
                    '5000', '6000', '6100', '6200', '6300', '6400', '6500', '6600', '6700', '6800'  # Expenses
                }
                
                found_codes = {acc.code for acc in accounts}
                missing_codes = default_codes - found_codes
                
                print(f"✅ Default accounts found: {len(found_codes & default_codes)}/{len(default_codes)}")
                if missing_codes:
                    print(f"⚠️  Missing default account codes: {sorted(missing_codes)}")
                else:
                    print("✅ All 25 default accounts are present!")
            else:
                print("❌ No accounts found for this tenant")
                print("   This means default accounts were not created during onboarding")
            
        except Exception as e:
            print(f"❌ Error querying accounts: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: direct query
            print()
            print("Trying direct query...")
            try:
                accounts = Account.query.filter_by(tenant_id=user.tenant_id).order_by(Account.code).all()
                print(f"📊 Found {len(accounts)} accounts (direct query)")
                if accounts:
                    for account in accounts:
                        print(f"  Code: {account.code} | Name: {account.name} | Type: {account.type}")
            except Exception as e2:
                print(f"❌ Direct query also failed: {e2}")
        
        print()
        print("=" * 60)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python check_user_accounts.py <user_id>")
        print("Example: python check_user_accounts.py 35")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        check_user_accounts(user_id)
    except ValueError:
        print("❌ Invalid user_id. Must be a number.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

