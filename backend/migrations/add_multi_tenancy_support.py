#!/usr/bin/env python3
"""
Multi-Tenancy Migration Script
Adds tenant support to existing database schema
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text, inspect
from modules.core.tenant_models import Tenant, UserTenant, TenantModule, TenantSettings

def get_existing_tables():
    """Get list of existing tables in the database"""
    inspector = inspect(db.engine)
    return inspector.get_table_names()

def table_has_column(table_name, column_name):
    """Check if a table has a specific column"""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"Error checking column {column_name} in table {table_name}: {e}")
        return False

def add_tenant_id_to_table(table_name):
    """Add tenant_id column to a specific table"""
    try:
        if not table_has_column(table_name, 'tenant_id'):
            print(f"➕ Adding tenant_id to {table_name}...")
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN tenant_id VARCHAR(50)"))
            db.session.commit()
            print(f"✅ Added tenant_id to {table_name}")
        else:
            print(f"ℹ️  {table_name} already has tenant_id column")
    except Exception as e:
        print(f"❌ Error adding tenant_id to {table_name}: {e}")
        db.session.rollback()

def create_tenant_indexes():
    """Create indexes for tenant_id columns"""
    try:
        # Get all tables that now have tenant_id
        tables_with_tenant_id = []
        inspector = inspect(db.engine)
        
        for table_name in inspector.get_table_names():
            if table_has_column(table_name, 'tenant_id'):
                tables_with_tenant_id.append(table_name)
        
        # Create composite indexes for performance
        for table_name in tables_with_tenant_id:
            try:
                # Create composite index (tenant_id, id) for main tables
                if table_name in ['advanced_general_ledger_entries', 'bank_accounts', 'reconciliation_sessions', 'bank_transactions']:
                    index_name = f"idx_{table_name}_tenant"
                    db.session.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON {table_name}(tenant_id, id)
                    """))
                    print(f"✅ Created index {index_name}")
            except Exception as e:
                print(f"⚠️  Could not create index for {table_name}: {e}")
        
        db.session.commit()
        print("✅ All tenant indexes created")
        
    except Exception as e:
        print(f"❌ Error creating tenant indexes: {e}")
        db.session.rollback()

def create_default_tenant():
    """Create a default tenant for existing data"""
    try:
        # Check if default tenant already exists
        existing_tenant = Tenant.query.filter_by(id='default_tenant').first()
        if existing_tenant:
            print("ℹ️  Default tenant already exists")
            return existing_tenant
        
        # Create default tenant
        default_tenant = Tenant(
            id='default_tenant',
            name='Default Company',
            domain='default',
            subscription_plan='enterprise',
            status='active',
            settings={
                'currency': 'USD',
                'timezone': 'UTC',
                'date_format': 'YYYY-MM-DD',
                'auto_reconciliation': True,
                'email_notifications': True
            },
            tenant_metadata={
                'migration_created': True,
                'migration_date': datetime.utcnow().isoformat()
            },
            created_by='system_migration'
        )
        
        db.session.add(default_tenant)
        db.session.commit()
        print("✅ Created default tenant")
        return default_tenant
        
    except Exception as e:
        print(f"❌ Error creating default tenant: {e}")
        db.session.rollback()
        raise

def migrate_existing_data_to_default_tenant():
    """Migrate all existing data to the default tenant"""
    try:
        # Get all tables that have tenant_id
        tables_to_migrate = []
        inspector = inspect(db.engine)
        
        for table_name in inspector.get_table_names():
            if table_has_column(table_name, 'tenant_id'):
                # Check if table has any data
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE tenant_id IS NULL"))
                count = result.scalar()
                if count > 0:
                    tables_to_migrate.append((table_name, count))
        
        if not tables_to_migrate:
            print("ℹ️  No tables need data migration")
            return
        
        print(f"📊 Found {len(tables_to_migrate)} tables with data to migrate:")
        for table_name, count in tables_to_migrate:
            print(f"   - {table_name}: {count} records")
        
        # Migrate data to default tenant
        for table_name, count in tables_to_migrate:
            print(f"🔄 Migrating {count} records in {table_name}...")
            db.session.execute(text(f"""
                UPDATE {table_name} 
                SET tenant_id = 'default_tenant' 
                WHERE tenant_id IS NULL
            """))
            db.session.commit()
            print(f"✅ Migrated {table_name}")
        
        print("✅ All existing data migrated to default tenant")
        
    except Exception as e:
        print(f"❌ Error migrating existing data: {e}")
        db.session.rollback()
        raise

def create_default_tenant_modules():
    """Create default module activations for the default tenant"""
    try:
        # Define available modules
        available_modules = [
            'finance',
            'inventory', 
            'sales',
            'purchasing',
            'manufacturing',
            'crm',
            'hr',
            'reporting',
            'analytics'
        ]
        
        # Activate all modules for default tenant
        for module_name in available_modules:
            existing_module = TenantModule.query.filter_by(
                tenant_id='default_tenant',
                module_name=module_name
            ).first()
            
            if not existing_module:
                module = TenantModule(
                    tenant_id='default_tenant',
                    module_name=module_name,
                    enabled=True,
                    activated_at=datetime.utcnow(),
                    configuration={}
                )
                db.session.add(module)
                print(f"✅ Activated module: {module_name}")
        
        db.session.commit()
        print("✅ All modules activated for default tenant")
        
    except Exception as e:
        print(f"❌ Error creating default tenant modules: {e}")
        db.session.rollback()
        raise

def create_default_user_tenant_mapping():
    """Create default user-tenant mapping for existing users"""
    try:
        # This would typically be done based on your user management system
        # For now, we'll create a placeholder that can be updated later
        print("ℹ️  User-tenant mapping will be handled by your authentication system")
        print("   You'll need to create UserTenant records for each user-tenant combination")
        
    except Exception as e:
        print(f"❌ Error creating user-tenant mapping: {e}")

def main():
    """Main migration function"""
    print("🚀 Starting Multi-Tenancy Migration...")
    print("=" * 50)
    
    try:
        # Step 1: Create tenant tables
        print("\n📋 Step 1: Creating tenant tables...")
        # Create tables for tenant models
        from modules.core.tenant_models import Tenant, UserTenant, TenantModule, TenantSettings
        db.create_all()
        print("✅ Tenant tables created")
        
        # Step 2: Add tenant_id to existing tables
        print("\n📋 Step 2: Adding tenant_id to existing tables...")
        existing_tables = get_existing_tables()
        
        # Tables that need tenant_id (exclude system tables)
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
                add_tenant_id_to_table(table_name)
            else:
                print(f"ℹ️  Table {table_name} not found, skipping")
        
        # Step 3: Create tenant indexes
        print("\n📋 Step 3: Creating tenant indexes...")
        create_tenant_indexes()
        
        # Step 4: Create default tenant
        print("\n📋 Step 4: Creating default tenant...")
        create_default_tenant()
        
        # Step 5: Migrate existing data
        print("\n📋 Step 5: Migrating existing data to default tenant...")
        migrate_existing_data_to_default_tenant()
        
        # Step 6: Create default tenant modules
        print("\n📋 Step 6: Activating default tenant modules...")
        create_default_tenant_modules()
        
        # Step 7: Create user-tenant mapping
        print("\n📋 Step 7: Setting up user-tenant mapping...")
        create_default_user_tenant_mapping()
        
        print("\n" + "=" * 50)
        print("🎉 Multi-Tenancy Migration Completed Successfully!")
        print("\n📝 Next Steps:")
        print("   1. Update your authentication system to include tenant context")
        print("   2. Add tenant filtering to all API endpoints")
        print("   3. Update frontend components to be tenant-aware")
        print("   4. Test tenant isolation thoroughly")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.session.rollback()
        sys.exit(1)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        main()
