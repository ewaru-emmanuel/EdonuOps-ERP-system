#!/usr/bin/env python3
"""
Verification Script: Chart of Accounts System
=============================================
Verifies that:
1. Default accounts are created during onboarding
2. Chart of Accounts can READ from database
3. Chart of Accounts can WRITE to database
"""

from app import create_app, db
from modules.core.models import User
from modules.finance.models import Account
from modules.core.tenant_query_helper import tenant_query
from sqlalchemy import func

app = create_app()

def verify_default_accounts_creation():
    """Verify that default accounts are created for tenants"""
    print("\n" + "="*60)
    print("VERIFICATION 1: Default Accounts Creation")
    print("="*60)
    
    with app.app_context():
        # Get all users with onboarding completed
        users = User.query.filter(User.onboarding_completed == True).all()
        
        if not users:
            print("❌ No users with completed onboarding found")
            return False
        
        print(f"Found {len(users)} user(s) with completed onboarding")
        
        all_verified = True
        for user in users:
            tenant_id = user.tenant_id
            if not tenant_id:
                print(f"⚠️  User {user.id} ({user.username}) has no tenant_id")
                continue
            
            # Count accounts for this tenant
            account_count = Account.query.filter_by(tenant_id=tenant_id).count()
            
            if account_count >= 20:  # Should have at least 20 of the 25 default accounts
                print(f"✅ User {user.id} ({user.username}): Tenant {tenant_id} has {account_count} accounts")
            else:
                print(f"❌ User {user.id} ({user.username}): Tenant {tenant_id} has only {account_count} accounts (expected ~25)")
                all_verified = False
        
        return all_verified

def verify_coa_read():
    """Verify that Chart of Accounts can READ accounts"""
    print("\n" + "="*60)
    print("VERIFICATION 2: Chart of Accounts READ Capability")
    print("="*60)
    
    with app.app_context():
        # Get a user with completed onboarding
        user = User.query.filter(User.onboarding_completed == True).first()
        
        if not user:
            print("❌ No user with completed onboarding found")
            return False
        
        tenant_id = user.tenant_id
        if not tenant_id:
            print(f"❌ User {user.id} has no tenant_id")
            return False
        
        # Simulate what the GET /api/finance/double-entry/accounts endpoint does
        try:
            accounts = tenant_query(Account).order_by(Account.code).all()
            
            if not accounts:
                print(f"❌ No accounts found for tenant {tenant_id}")
                return False
            
            print(f"✅ Successfully read {len(accounts)} accounts for tenant {tenant_id}")
            print(f"   Sample accounts:")
            for acc in accounts[:5]:
                print(f"   - {acc.code}: {acc.name} ({acc.type})")
            
            return True
        except Exception as e:
            print(f"❌ Error reading accounts: {e}")
            return False

def verify_coa_write():
    """Verify that Chart of Accounts can WRITE (create) accounts"""
    print("\n" + "="*60)
    print("VERIFICATION 3: Chart of Accounts WRITE Capability")
    print("="*60)
    
    with app.app_context():
        # Get a user with completed onboarding
        user = User.query.filter(User.onboarding_completed == True).first()
        
        if not user:
            print("❌ No user with completed onboarding found")
            return False
        
        tenant_id = user.tenant_id
        if not tenant_id:
            print(f"❌ User {user.id} has no tenant_id")
            return False
        
        # Simulate what the POST /api/finance/double-entry/accounts endpoint does
        try:
            # Check if test account already exists
            test_code = "9999"
            existing = tenant_query(Account).filter_by(code=test_code).first()
            
            if existing:
                print(f"⚠️  Test account {test_code} already exists, deleting it first...")
                db.session.delete(existing)
                db.session.commit()
            
            # Create a test account (simulating POST request)
            test_account = Account(
                code=test_code,
                name="Test Account (Verification)",
                type="expense",
                balance=0.0,
                currency="USD",
                is_active=True,
                tenant_id=tenant_id,
                created_by=user.id
            )
            
            db.session.add(test_account)
            db.session.commit()
            
            # Verify it was created
            created = tenant_query(Account).filter_by(code=test_code).first()
            if created:
                print(f"✅ Successfully created test account: {created.code} - {created.name}")
                
                # Clean up - delete the test account
                db.session.delete(created)
                db.session.commit()
                print(f"✅ Cleaned up test account")
                
                return True
            else:
                print(f"❌ Test account was not created")
                return False
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating account: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run all verifications"""
    print("\n" + "="*60)
    print("CHART OF ACCOUNTS SYSTEM VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run verifications
    results.append(("Default Accounts Creation", verify_default_accounts_creation()))
    results.append(("CoA READ Capability", verify_coa_read()))
    results.append(("CoA WRITE Capability", verify_coa_write()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("✅ ALL VERIFICATIONS PASSED")
    else:
        print("❌ SOME VERIFICATIONS FAILED")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())

