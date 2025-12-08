#!/usr/bin/env python3
"""
Create Default Accounts for User Script
========================================

This script creates the 25 default accounts for a specific user's tenant.
Used to fix accounts that weren't created during onboarding.

Usage:
    python create_accounts_for_user.py <user_id>
    Example: python create_accounts_for_user.py 35
"""

import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import User
from modules.finance.default_accounts_service import create_default_accounts

def create_accounts_for_user(user_id):
    """Create default accounts for a user's tenant"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print(f"CREATING DEFAULT ACCOUNTS FOR USER {user_id}")
        print("=" * 60)
        print()
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User {user_id} not found")
            return False
        
        print(f"✅ User found: {user.username} ({user.email})")
        print(f"   Role: {user.role.role_name if user.role else 'No role'}")
        print(f"   Tenant ID: {user.tenant_id}")
        print()
        
        if not user.tenant_id:
            print("❌ User has no tenant_id")
            return False
        
        # Check if accounts already exist
        from modules.finance.models import Account
        existing_count = Account.query.filter_by(tenant_id=user.tenant_id).count()
        
        if existing_count > 0:
            print(f"⚠️  User's tenant already has {existing_count} accounts")
            response = input("   Do you want to create additional accounts anyway? (y/N): ")
            if response.lower() != 'y':
                print("   Skipping account creation")
                return False
        
        print(f"🔨 Creating 25 default accounts for tenant: {user.tenant_id}")
        print()
        
        try:
            result = create_default_accounts(
                tenant_id=user.tenant_id,
                created_by=user_id,
                force=False
            )
            
            print()
            print("=" * 60)
            print("ACCOUNT CREATION SUMMARY")
            print("=" * 60)
            print(f"Total accounts: {result['total']}")
            print(f"New accounts created: {result['new_count']}")
            print(f"Accounts skipped (already exist): {len(result['skipped'])}")
            print()
            
            if result['new_count'] > 0:
                print("✅ Successfully created accounts:")
                for acc in result['created']:
                    print(f"   - {acc['code']}: {acc['name']}")
                print()
            
            if result['skipped']:
                print("ℹ️  Skipped accounts (already exist):")
                for acc in result['skipped']:
                    print(f"   - {acc['code']}: {acc['name']}")
                print()
            
            # Verify final count
            final_count = Account.query.filter_by(tenant_id=user.tenant_id).count()
            print(f"📊 Final account count for tenant: {final_count}")
            
            if final_count >= 25:
                print("✅ All 25 default accounts are now present!")
            else:
                print(f"⚠️  Expected 25 accounts, but found {final_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating accounts: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python create_accounts_for_user.py <user_id>")
        print("Example: python create_accounts_for_user.py 35")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        success = create_accounts_for_user(user_id)
        sys.exit(0 if success else 1)
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

