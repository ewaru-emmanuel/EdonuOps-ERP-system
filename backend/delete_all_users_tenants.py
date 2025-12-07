"""Delete all users and tenants from the database - FRESH START"""
from app import create_app, db
from modules.core.models import User
from modules.core.tenant_models import Tenant
from sqlalchemy import text, inspect
import sys

app = create_app()
with app.app_context():
    print('\n' + '='*80)
    print('⚠️  WARNING: DELETING ALL USERS AND TENANTS')
    print('='*80 + '\n')
    
    # Confirm deletion
    response = input('Are you SURE you want to delete ALL users and tenants? (type "DELETE ALL" to confirm): ')
    if response.upper().strip() != "DELETE ALL":
        print('❌ Deletion cancelled.')
        sys.exit(0)
    
    print('\n🗑️  Starting deletion process...\n')
    
    try:
        # Get counts before deletion
        user_count = User.query.count()
        tenant_count = Tenant.query.count()
        
        print(f'📊 Current counts:')
        print(f'   Users: {user_count}')
        print(f'   Tenants: {tenant_count}')
        print()
        
        if user_count == 0 and tenant_count == 0:
            print('✅ Database is already empty. Nothing to delete.')
            sys.exit(0)
        
        # Get list of all users and tenants for reference
        all_users = User.query.all()
        all_tenants = Tenant.query.all()
        
        print('👥 Users to be deleted:')
        for user in all_users:
            print(f'   - User {user.id}: {user.username} ({user.email}) - Tenant: {user.tenant_id}')
        print()
        
        print('🏢 Tenants to be deleted:')
        for tenant in all_tenants:
            print(f'   - {tenant.id}: {tenant.name}')
        print()
        
        # Delete in order to handle foreign key constraints
        # First, delete data that references users/tenants
        
        print('🗑️  Step 1: Deleting data that references users/tenants...')
        
        # Delete all tables that reference users (in dependency order)
        # Common tables that reference user_id
        user_reference_tables = [
            'login_history',
            'audit_logs',
            'user_data',
            'onboarding_progress',
            'user_modules',
        ]
        
        for table in user_reference_tables:
            try:
                result = db.session.execute(text(f"DELETE FROM {table}"))
                print(f'   ✅ Deleted {result.rowcount} {table} records')
                db.session.commit()  # Commit immediately
            except Exception as e:
                if 'does not exist' not in str(e).lower():
                    print(f'   ⚠️  Error deleting {table}: {e}')
                db.session.rollback()
        
        # Delete onboarding_progress (references user_id and tenant_id)
        try:
            result = db.session.execute(text("DELETE FROM onboarding_progress"))
            print(f'   ✅ Deleted {result.rowcount} onboarding_progress records')
            db.session.commit()  # Commit immediately
        except Exception as e:
            print(f'   ⚠️  Error deleting onboarding_progress: {e}')
            db.session.rollback()
        
        # Delete user_modules (references user_id)
        try:
            result = db.session.execute(text("DELETE FROM user_modules"))
            print(f'   ✅ Deleted {result.rowcount} user_modules records')
            db.session.commit()  # Commit immediately
        except Exception as e:
            print(f'   ⚠️  Error deleting user_modules: {e}')
            db.session.rollback()
        
        # Delete accounts (references tenant_id)
        try:
            result = db.session.execute(text("DELETE FROM accounts WHERE tenant_id IS NOT NULL"))
            print(f'   ✅ Deleted {result.rowcount} account records')
            db.session.commit()  # Commit immediately
        except Exception as e:
            print(f'   ⚠️  Error deleting accounts: {e}')
            db.session.rollback()
        
        # Delete chart_of_accounts (references tenant_id)
        try:
            result = db.session.execute(text("DELETE FROM chart_of_accounts WHERE tenant_id IS NOT NULL"))
            print(f'   ✅ Deleted {result.rowcount} chart_of_accounts records')
        except Exception as e:
            if 'does not exist' not in str(e).lower():
                print(f'   ⚠️  Error deleting chart_of_accounts: {e}')
        
        # Delete tenant_modules (references tenant_id)
        try:
            db.session.rollback()  # Reset transaction if previous error
            result = db.session.execute(text("DELETE FROM tenant_modules"))
            print(f'   ✅ Deleted {result.rowcount} tenant_modules records')
        except Exception as e:
            if 'does not exist' not in str(e).lower():
                print(f'   ⚠️  Error deleting tenant_modules: {e}')
        
        # Delete user_tenants (references user_id and tenant_id)
        try:
            db.session.rollback()  # Reset transaction if previous error
            result = db.session.execute(text("DELETE FROM user_tenants"))
            print(f'   ✅ Deleted {result.rowcount} user_tenants records')
        except Exception as e:
            if 'does not exist' not in str(e).lower():
                print(f'   ⚠️  Error deleting user_tenants: {e}')
        
        # Delete tenant_settings (references tenant_id)
        try:
            db.session.rollback()  # Reset transaction if previous error
            result = db.session.execute(text("DELETE FROM tenant_settings"))
            print(f'   ✅ Deleted {result.rowcount} tenant_settings records')
        except Exception as e:
            if 'does not exist' not in str(e).lower():
                print(f'   ⚠️  Error deleting tenant_settings: {e}')
        
        # Delete any other tables that might reference users/tenants
        # Try to delete from common tables
        tables_to_check = [
            'journal_entries', 'transactions', 'invoices', 'payments',
            'inventory_items', 'products', 'customers', 'suppliers',
            'tickets', 'contacts', 'leads', 'opportunities'
        ]
        
        for table in tables_to_check:
            try:
                # Check if table exists and has tenant_id or user_id
                result = db.session.execute(
                    text(f"""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    """)
                )
                if result.scalar() > 0:
                    # Try to delete if table has tenant_id
                    try:
                        result = db.session.execute(
                            text(f"DELETE FROM {table} WHERE tenant_id IS NOT NULL")
                        )
                        if result.rowcount > 0:
                            print(f'   ✅ Deleted {result.rowcount} {table} records')
                    except:
                        # Table might not have tenant_id, try without
                        try:
                            result = db.session.execute(text(f"DELETE FROM {table}"))
                            if result.rowcount > 0:
                                print(f'   ✅ Deleted {result.rowcount} {table} records')
                        except:
                            pass  # Skip if table doesn't exist or has constraints
            except:
                pass  # Skip if we can't check the table
        
        # Final commit for any remaining deletes
        try:
            db.session.commit()
        except:
            db.session.rollback()
        print('   ✅ Step 1 complete\n')
        
        # Step 2: Delete all users
        print('🗑️  Step 2: Deleting all users...')
        deleted_users = 0
        for user in all_users:
            try:
                db.session.delete(user)
                deleted_users += 1
            except Exception as e:
                print(f'   ⚠️  Error deleting user {user.id}: {e}')
        
        db.session.commit()
        print(f'   ✅ Deleted {deleted_users} users\n')
        
        # Step 3: Delete all tenants
        print('🗑️  Step 3: Deleting all tenants...')
        deleted_tenants = 0
        for tenant in all_tenants:
            try:
                db.session.delete(tenant)
                deleted_tenants += 1
            except Exception as e:
                print(f'   ⚠️  Error deleting tenant {tenant.id}: {e}')
        
        db.session.commit()
        print(f'   ✅ Deleted {deleted_tenants} tenants\n')
        
        # Verify deletion
        print('🔍 Verifying deletion...')
        remaining_users = User.query.count()
        remaining_tenants = Tenant.query.count()
        
        print(f'   Remaining users: {remaining_users}')
        print(f'   Remaining tenants: {remaining_tenants}')
        print()
        
        if remaining_users == 0 and remaining_tenants == 0:
            print('='*80)
            print('✅ SUCCESS: All users and tenants deleted!')
            print('='*80)
            print()
            print('The database is now clean and ready for fresh registrations.')
            print('Users can now register and go through the onboarding process.')
            print('The tenant name will be updated from the actual company name')
            print('they enter during onboarding (not a default name).')
            print()
        else:
            print('='*80)
            print('⚠️  WARNING: Some records may still exist')
            print('='*80)
            print(f'   Remaining users: {remaining_users}')
            print(f'   Remaining tenants: {remaining_tenants}')
            print()
        
    except Exception as e:
        db.session.rollback()
        print(f'\n❌ ERROR during deletion: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

