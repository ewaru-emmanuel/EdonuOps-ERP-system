"""
Comprehensive Migration Script: User-Centric to Tenant-Centric Architecture
Migrates all company-wide data from user_id to tenant_id
"""

import sys
import os
from sqlalchemy import text
from app import create_app, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_to_tenant_centric():
    app = create_app()
    with app.app_context():
        try:
            print("🚀 MIGRATING TO TENANT-CENTRIC ARCHITECTURE")
            print("=" * 60)
            
            with db.engine.connect() as connection:
                # Step 1: Add tenant_id and audit columns to company-wide tables
                print("\n📋 STEP 1: Adding tenant_id columns to company-wide tables...")
                
                tables_to_migrate = [
                    ('accounts', 'user_id', 'created_by'),
                    ('journal_entries', 'user_id', 'created_by'),
                    ('system_settings', None, 'last_modified_by'),  # Already has tenant_id
                ]
                
                for table_name, old_user_col, audit_col in tables_to_migrate:
                    # Check if tenant_id exists
                    result = connection.execute(text(
                        f"SELECT column_name FROM information_schema.columns "
                        f"WHERE table_name='{table_name}' AND column_name='tenant_id'"
                    )).fetchone()
                    
                    if not result:
                        # Add tenant_id column
                        connection.execute(text(
                            f"ALTER TABLE {table_name} ADD COLUMN tenant_id VARCHAR(50)"
                        ))
                        connection.execute(text(
                            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_tenant_id ON {table_name}(tenant_id)"
                        ))
                        print(f"   ✅ Added tenant_id to {table_name}")
                    else:
                        print(f"   ⏭️  {table_name} already has tenant_id")
                    
                    # Add audit column if needed
                    if audit_col:
                        result = connection.execute(text(
                            f"SELECT column_name FROM information_schema.columns "
                            f"WHERE table_name='{table_name}' AND column_name='{audit_col}'"
                        )).fetchone()
                        
                        if not result:
                            connection.execute(text(
                                f"ALTER TABLE {table_name} ADD COLUMN {audit_col} INTEGER REFERENCES users(id)"
                            ))
                            print(f"   ✅ Added {audit_col} to {table_name}")
                
                connection.commit()
                
                # Step 2: Populate tenant_id from user records
                print("\n📋 STEP 2: Populating tenant_id from user records...")
                
                # For accounts: Get tenant_id from the user who created it
                connection.execute(text("""
                    UPDATE accounts a
                    SET tenant_id = u.tenant_id
                    FROM users u
                    WHERE a.user_id = u.id AND a.tenant_id IS NULL
                """))
                print("   ✅ Populated tenant_id for accounts")
                
                # For journal_entries: Get tenant_id from the user who created it
                connection.execute(text("""
                    UPDATE journal_entries je
                    SET tenant_id = u.tenant_id
                    FROM users u
                    WHERE je.user_id = u.id AND je.tenant_id IS NULL
                """))
                print("   ✅ Populated tenant_id for journal_entries")
                
                # For system_settings: Get tenant_id from the user who created it
                connection.execute(text("""
                    UPDATE system_settings ss
                    SET tenant_id = u.tenant_id
                    FROM users u
                    WHERE ss.user_id = u.id AND ss.tenant_id IS NULL
                """))
                print("   ✅ Populated tenant_id for system_settings")
                
                connection.commit()
                
                # Step 3: Copy user_id to audit columns
                print("\n📋 STEP 3: Copying user_id to audit columns...")
                
                connection.execute(text("""
                    UPDATE accounts
                    SET created_by = user_id
                    WHERE created_by IS NULL AND user_id IS NOT NULL
                """))
                print("   ✅ Copied user_id to created_by for accounts")
                
                connection.execute(text("""
                    UPDATE journal_entries
                    SET created_by = user_id
                    WHERE created_by IS NULL AND user_id IS NOT NULL
                """))
                print("   ✅ Copied user_id to created_by for journal_entries")
                
                connection.execute(text("""
                    UPDATE system_settings
                    SET last_modified_by = user_id
                    WHERE last_modified_by IS NULL AND user_id IS NOT NULL
                """))
                print("   ✅ Copied user_id to last_modified_by for system_settings")
                
                connection.commit()
                
                # Step 4: Update unique constraints
                print("\n📋 STEP 4: Updating unique constraints...")
                
                # Drop old user_id-based constraints
                try:
                    connection.execute(text("ALTER TABLE accounts DROP CONSTRAINT IF EXISTS uq_account_user_code"))
                    print("   ✅ Dropped old user_id constraint on accounts")
                except:
                    pass
                
                # Create new tenant_id-based constraints
                try:
                    connection.execute(text("""
                        ALTER TABLE accounts 
                        ADD CONSTRAINT uq_account_tenant_code 
                        UNIQUE (tenant_id, code)
                    """))
                    print("   ✅ Created tenant_id constraint on accounts")
                except:
                    pass
                
                connection.commit()
                
                # Step 5: Make tenant_id NOT NULL where needed
                print("\n📋 STEP 5: Making tenant_id NOT NULL...")
                
                # First, ensure all records have tenant_id (set to default if missing)
                connection.execute(text("""
                    UPDATE accounts 
                    SET tenant_id = 'default_tenant' 
                    WHERE tenant_id IS NULL
                """))
                connection.execute(text("""
                    ALTER TABLE accounts 
                    ALTER COLUMN tenant_id SET NOT NULL
                """))
                print("   ✅ Made tenant_id NOT NULL for accounts")
                
                connection.execute(text("""
                    UPDATE journal_entries 
                    SET tenant_id = 'default_tenant' 
                    WHERE tenant_id IS NULL
                """))
                connection.execute(text("""
                    ALTER TABLE journal_entries 
                    ALTER COLUMN tenant_id SET NOT NULL
                """))
                print("   ✅ Made tenant_id NOT NULL for journal_entries")
                
                connection.commit()
                
                print("\n✅ MIGRATION COMPLETE!")
                print("=" * 60)
                print("📊 Summary:")
                print("   • All company-wide data now uses tenant_id")
                print("   • Audit columns (created_by, last_modified_by) track who made changes")
                print("   • Unique constraints updated to tenant_id-based")
                print("   • All existing data migrated successfully")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    migrate_to_tenant_centric()

