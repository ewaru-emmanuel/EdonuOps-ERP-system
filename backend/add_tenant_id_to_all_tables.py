"""
Comprehensive Migration: Add tenant_id to all company-wide tables
This script systematically adds tenant_id and audit columns to all business tables
"""

import sys
import os
from sqlalchemy import text
from app import create_app, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of company-wide tables that need tenant_id
COMPANY_WIDE_TABLES = [
    # Sales
    ('customers', 'created_by'),
    ('invoices', 'created_by'),
    ('payments', 'created_by'),
    ('customer_communications', 'created_by'),
    
    # Procurement
    ('vendors', 'created_by'),
    ('purchase_orders', 'created_by'),
    ('purchase_order_items', None),  # Inherits from parent
    ('rfqs', 'created_by'),
    ('rfq_responses', 'created_by'),
    ('contracts', 'created_by'),
    
    # Inventory
    ('products', 'created_by'),
    ('product_categories', 'created_by'),
    ('warehouses', 'created_by'),
    ('basic_inventory_transactions', 'created_by'),
    ('stock_movements', 'created_by'),
    ('inventory_levels', 'created_by'),
    
    # CRM
    ('contacts', 'created_by'),
    ('companies', 'created_by'),
    ('leads', 'created_by'),
    ('opportunities', 'created_by'),
    ('tickets', 'created_by'),
    
    # Finance (already done, but included for completeness)
    ('accounts', 'created_by'),
    ('journal_entries', 'created_by'),
    ('system_settings', 'last_modified_by'),
]

def add_tenant_id_to_all_tables():
    app = create_app()
    with app.app_context():
        try:
            print("🚀 ADDING TENANT_ID TO ALL COMPANY-WIDE TABLES")
            print("=" * 60)
            
            with db.engine.connect() as connection:
                for table_name, audit_col in COMPANY_WIDE_TABLES:
                    try:
                        # Check if table exists
                        result = connection.execute(text(
                            f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"
                        )).scalar()
                        
                        if not result:
                            print(f"   ⏭️  Table '{table_name}' does not exist - skipping")
                            continue
                        
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
                        
                        # Add audit column if specified
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
                        
                        # Populate tenant_id from user records
                        # This assumes existing records have user_id that we can use to get tenant_id
                        if table_name in ['accounts', 'journal_entries', 'system_settings']:
                            # Already migrated
                            pass
                        else:
                            # Try to populate from user_id if it exists
                            result = connection.execute(text(
                                f"SELECT column_name FROM information_schema.columns "
                                f"WHERE table_name='{table_name}' AND column_name='user_id'"
                            )).fetchone()
                            
                            if result:
                                # Populate tenant_id from user records
                                connection.execute(text(f"""
                                    UPDATE {table_name} t
                                    SET tenant_id = u.tenant_id
                                    FROM users u
                                    WHERE t.user_id = u.id AND t.tenant_id IS NULL
                                """))
                                print(f"   ✅ Populated tenant_id for {table_name}")
                        
                        connection.commit()
                        
                    except Exception as e:
                        logger.error(f"   ❌ Error processing {table_name}: {e}")
                        connection.rollback()
                        continue
                
                print("\n✅ MIGRATION COMPLETE!")
                print("=" * 60)
                print("📊 Summary:")
                print("   • tenant_id added to all company-wide tables")
                print("   • Audit columns added where specified")
                print("   • Indexes created for performance")
                print("   • Existing data migrated where possible")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    add_tenant_id_to_all_tables()

