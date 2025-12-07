"""
Script to create default accounts for existing users who don't have them
This is a one-time migration script to fix existing users
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import User
from modules.finance.models import Account
from modules.finance.default_accounts_service import create_default_accounts, check_user_has_accounts

def create_accounts_for_existing_users():
    """Create default accounts for all existing users who don't have them"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            
            if not users:
                print("⚠️  No users found in database")
                return
            
            print(f"👥 Found {len(users)} user(s) in database\n")
            
            users_without_accounts = []
            users_with_accounts = []
            users_processed = []
            
            for user in users:
                has_accounts = check_user_has_accounts(user.id)
                
                if not has_accounts:
                    users_without_accounts.append(user)
                else:
                    # Count accounts for this user
                    account_count = Account.query.filter_by(user_id=user.id).count()
                    users_with_accounts.append((user, account_count))
            
            print(f"📊 Summary:")
            print(f"   Users without accounts: {len(users_without_accounts)}")
            print(f"   Users with accounts: {len(users_with_accounts)}\n")
            
            if users_with_accounts:
                print("✅ Users who already have accounts:")
                for user, count in users_with_accounts:
                    print(f"   User {user.id} ({user.email}): {count} accounts")
                print()
            
            if not users_without_accounts:
                print("✅ All users already have default accounts!")
                return
            
            print(f"📝 Creating default accounts for {len(users_without_accounts)} user(s)...\n")
            
            # Create accounts for users without them
            for user in users_without_accounts:
                try:
                    print(f"👤 Processing user {user.id} ({user.email})...")
                    result = create_default_accounts(user.id, force=False)
                    
                    if result['new_count'] > 0:
                        print(f"   ✅ Created {result['new_count']} default accounts")
                        users_processed.append((user, result['new_count'], 'success'))
                    else:
                        print(f"   ⚠️  No new accounts created (may already exist)")
                        users_processed.append((user, 0, 'skipped'))
                    
                except Exception as e:
                    print(f"   ❌ Error creating accounts: {e}")
                    users_processed.append((user, 0, 'error'))
                    import traceback
                    traceback.print_exc()
            
            print("\n" + "="*60)
            print("📊 FINAL SUMMARY:")
            print("="*60)
            
            successful = [u for u in users_processed if u[2] == 'success']
            skipped = [u for u in users_processed if u[2] == 'skipped']
            errors = [u for u in users_processed if u[2] == 'error']
            
            print(f"✅ Successfully created accounts: {len(successful)}")
            for user, count, status in successful:
                print(f"   User {user.id} ({user.email}): {count} accounts")
            
            if skipped:
                print(f"\n⚠️  Skipped (already had accounts): {len(skipped)}")
                for user, count, status in skipped:
                    print(f"   User {user.id} ({user.email})")
            
            if errors:
                print(f"\n❌ Errors: {len(errors)}")
                for user, count, status in errors:
                    print(f"   User {user.id} ({user.email})")
            
            print("\n✅ Migration complete!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    create_accounts_for_existing_users()


