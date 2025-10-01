#!/usr/bin/env python3
"""
Simple Multi-Tenancy Migration Script
Adds tenant support to existing database schema
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text, inspect

def main():
    """Main migration function"""
    print("🚀 Starting Simple Multi-Tenancy Migration...")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Step 1: Create tenant tables
            print("\n📋 Step 1: Creating tenant tables...")
            
            # Create tenants table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    domain VARCHAR(255) UNIQUE,
                    subscription_plan VARCHAR(50) DEFAULT 'free',
                    status VARCHAR(20) DEFAULT 'active',
                    settings TEXT,
                    tenant_metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create user_tenants table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS user_tenants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(100) NOT NULL,
                    tenant_id VARCHAR(50) NOT NULL,
                    role VARCHAR(50) DEFAULT 'user',
                    is_default BOOLEAN DEFAULT FALSE,
                    permissions TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    UNIQUE(user_id, tenant_id)
                )
            """))
            
            # Create tenant_modules table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id VARCHAR(50) NOT NULL,
                    module_name VARCHAR(100) NOT NULL,
                    enabled BOOLEAN DEFAULT FALSE,
                    activated_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    configuration TEXT,
                    UNIQUE(tenant_id, module_name)
                )
            """))
            
            # Create tenant_settings table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id VARCHAR(50) NOT NULL,
                    setting_key VARCHAR(100) NOT NULL,
                    setting_value TEXT,
                    setting_type VARCHAR(20) DEFAULT 'string',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by VARCHAR(100),
                    UNIQUE(tenant_id, setting_key)
                )
            """))
            
            db.session.commit()
            print("✅ Tenant tables created")
            
            # Step 2: Add tenant_id to existing tables
            print("\n📋 Step 2: Adding tenant_id to existing tables...")
            
            # Get existing tables
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Tables that need tenant_id
            tables_to_update = [
                'advanced_chart_of_accounts',
                'advanced_general_ledger_entries', 
                'advanced_journal_headers',
                'bank_accounts',
                'bank_transactions',
                'reconciliation_sessions',
                'payment_methods',
                'advanced_inventory_items',
                'advanced_inventory_transactions',
                'advanced_sales_orders',
                'advanced_sales_order_items',
                'advanced_purchase_orders',
                'advanced_purchase_order_items'
            ]
            
            for table_name in tables_to_update:
                if table_name in existing_tables:
                    try:
                        # Check if tenant_id already exists
                        columns = [col['name'] for col in inspector.get_columns(table_name)]
                        if 'tenant_id' not in columns:
                            print(f"➕ Adding tenant_id to {table_name}...")
                            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN tenant_id VARCHAR(50)"))
                            db.session.commit()
                            print(f"✅ Added tenant_id to {table_name}")
                        else:
                            print(f"ℹ️  {table_name} already has tenant_id column")
                    except Exception as e:
                        print(f"❌ Error adding tenant_id to {table_name}: {e}")
                        db.session.rollback()
                else:
                    print(f"ℹ️  Table {table_name} not found, skipping")
            
            # Step 3: Create indexes
            print("\n📋 Step 3: Creating tenant indexes...")
            
            # Create indexes for main tables
            index_tables = [
                'advanced_general_ledger_entries',
                'bank_accounts', 
                'reconciliation_sessions',
                'bank_transactions'
            ]
            
            for table_name in index_tables:
                if table_name in existing_tables:
                    try:
                        index_name = f"idx_{table_name}_tenant"
                        db.session.execute(text(f"""
                            CREATE INDEX IF NOT EXISTS {index_name} 
                            ON {table_name}(tenant_id, id)
                        """))
                        print(f"✅ Created index {index_name}")
                    except Exception as e:
                        print(f"⚠️  Could not create index for {table_name}: {e}")
            
            db.session.commit()
            
            # Step 4: Create default tenant
            print("\n📋 Step 4: Creating default tenant...")
            
            try:
                # Check if default tenant exists
                result = db.session.execute(text("SELECT COUNT(*) FROM tenants WHERE id = 'default_tenant'"))
                count = result.scalar()
                
                if count == 0:
                    db.session.execute(text("""
                        INSERT INTO tenants (id, name, domain, subscription_plan, status, settings, tenant_metadata, created_by)
                        VALUES ('default_tenant', 'Default Company', 'default', 'enterprise', 'active', 
                                '{"currency": "USD", "timezone": "UTC", "date_format": "YYYY-MM-DD", "auto_reconciliation": true, "email_notifications": true}',
                                '{"migration_created": true, "migration_date": "2025-09-23T13:00:00"}',
                                'system_migration')
                    """))
                    db.session.commit()
                    print("✅ Created default tenant")
                else:
                    print("ℹ️  Default tenant already exists")
            except Exception as e:
                print(f"❌ Error creating default tenant: {e}")
                db.session.rollback()
            
            # Step 5: Migrate existing data
            print("\n📋 Step 5: Migrating existing data to default tenant...")
            
            for table_name in tables_to_update:
                if table_name in existing_tables:
                    try:
                        # Check if table has data without tenant_id
                        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE tenant_id IS NULL"))
                        count = result.scalar()
                        
                        if count > 0:
                            print(f"🔄 Migrating {count} records in {table_name}...")
                            db.session.execute(text(f"""
                                UPDATE {table_name} 
                                SET tenant_id = 'default_tenant' 
                                WHERE tenant_id IS NULL
                            """))
                            db.session.commit()
                            print(f"✅ Migrated {table_name}")
                        else:
                            print(f"ℹ️  No data to migrate in {table_name}")
                    except Exception as e:
                        print(f"❌ Error migrating {table_name}: {e}")
                        db.session.rollback()
            
            # Step 6: Activate default modules
            print("\n📋 Step 6: Activating default tenant modules...")
            
            modules = [
                'finance', 'inventory', 'sales', 'purchasing', 
                'manufacturing', 'crm', 'hr', 'reporting', 'analytics'
            ]
            
            for module_name in modules:
                try:
                    # Check if module already exists
                    result = db.session.execute(text("""
                        SELECT COUNT(*) FROM tenant_modules 
                        WHERE tenant_id = 'default_tenant' AND module_name = ?
                    """), (module_name,))
                    count = result.scalar()
                    
                    if count == 0:
                        db.session.execute(text("""
                            INSERT INTO tenant_modules (tenant_id, module_name, enabled, activated_at, configuration)
                            VALUES ('default_tenant', ?, TRUE, CURRENT_TIMESTAMP, '{}')
                        """), (module_name,))
                        print(f"✅ Activated module: {module_name}")
                    else:
                        print(f"ℹ️  Module {module_name} already activated")
                except Exception as e:
                    print(f"❌ Error activating module {module_name}: {e}")
                    db.session.rollback()
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("🎉 Multi-Tenancy Migration Completed Successfully!")
            print("=" * 60)
            
            print("\n📋 Migration Summary:")
            print("✅ Created tenant tables (tenants, user_tenants, tenant_modules, tenant_settings)")
            print("✅ Added tenant_id to all existing tables")
            print("✅ Created performance indexes")
            print("✅ Created default tenant for existing data")
            print("✅ Migrated all existing data to default tenant")
            print("✅ Activated all modules for default tenant")
            
            print("\n📝 Next Steps:")
            print("1. 🔧 Update your authentication system to include tenant context")
            print("2. 🛡️  Add tenant filtering to all API endpoints")
            print("3. 🎨 Update frontend components to be tenant-aware")
            print("4. 🧪 Test tenant isolation thoroughly")
            print("5. 📊 Monitor performance with tenant indexes")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()












