#!/usr/bin/env python3
"""
🔒 EDONUOPS ERP - TENANT ISOLATION IMPLEMENTATION
============================================================

Implements hybrid RLS + Query-Level isolation strategy:
- RLS: Strict tenant boundaries for core business data
- Query-Level: Complex permissions, role-based access, business rules
- Audit: Comprehensive logging for compliance

Author: EdonuOps Team
Date: 2024
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TenantIsolationImplementer:
    def __init__(self):
        """Initialize the tenant isolation implementer"""
        self.engine = None
        self.connection = None
        
    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            # Load environment variables from config.env
            load_dotenv('config.env')
            
            # Get database URL from environment
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL environment variable not set")
            
            # Create SQLAlchemy engine
            self.engine = create_engine(database_url, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Connected to PostgreSQL database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def get_business_tables(self):
        """Get all business tables that need tenant isolation"""
        business_tables = {
            # CORE BUSINESS DATA (RLS Required)
            'core_business': [
                'users', 'organizations', 'roles', 'permissions', 'role_permissions',
                'user_sessions', 'user_preferences', 'user_data', 'user_modules'
            ],
            
            # FINANCE MODULE (RLS Required)
            'finance': [
                'accounts', 'journal_entries', 'journal_lines', 'bank_accounts',
                'bank_transactions', 'payments', 'payment_transactions', 'partial_payments',
                'payment_methods', 'cost_centers', 'departments', 'projects',
                'cost_allocations', 'cost_allocation_details', 'cost_layer_transactions',
                'accounting_periods', 'fiscal_years', 'budgets', 'budget_scenarios',
                'reconciliation_sessions', 'inventory_cost_layers'
            ],
            
            # INVENTORY MODULE (RLS Required)
            'inventory': [
                'products', 'product_categories', 'warehouses', 'stock_movements',
                'basic_inventory_transactions', 'inventory_products', 'inventory_product_categories',
                'inventory_product_variants', 'inventory_simple_warehouses', 'inventory_advanced_warehouses',
                'inventory_basic_locations', 'inventory_advanced_locations', 'inventory_aisles',
                'inventory_racks', 'inventory_zones', 'inventory_stock_levels', 'inventory_levels',
                'inventory_transactions', 'inventory_adjustment_entries', 'inventory_audit_trail',
                'inventory_cost_layers', 'inventory_lot_batches', 'inventory_serial_numbers',
                'inventory_uom', 'inventory_uom_conversions', 'inventory_warehouse_activities',
                'inventory_picker_performances', 'inventory_predictive_stockouts',
                'inventory_reports', 'inventory_system_config', 'inventory_valuation_snapshots',
                'daily_inventory_balances', 'daily_inventory_cycle_audit_logs',
                'daily_inventory_cycle_status', 'daily_inventory_transaction_summaries',
                'inventory_customers', 'inventory_suppliers'
            ],
            
            # CRM MODULE (RLS Required)
            'crm': [
                'customers', 'contacts', 'leads', 'opportunities', 'pipelines',
                'lead_intakes', 'crm_users', 'follow_ups', 'communications',
                'contracts', 'contract_documents', 'companies', 'vendors',
                'vendor_documents', 'vendor_communications'
            ],
            
            # PROCUREMENT MODULE (RLS Required)
            'procurement': [
                'purchase_orders', 'purchase_order_items', 'rfqs', 'rfq_invitations',
                'rfq_items', 'rfq_responses', 'rfq_response_items', 'po_attachments'
            ],
            
            # SALES MODULE (RLS Required)
            'sales': [
                'invoices', 'invoice_line_items'
            ],
            
            # SYSTEM TABLES (Query-Level Only)
            'system_tables': [
                'tenants', 'tenant_settings', 'tenant_modules', 'tenant_usage_stats',
                'system_settings', 'system_events', 'audit_logs', 'login_history',
                'security_events', 'security_policies', 'permission_changes',
                'password_history', 'account_lockouts', 'two_factor_auth',
                'platform_metrics', 'behavioral_events'
            ],
            
            # WORKFLOW TABLES (Query-Level Only)
            'workflow': [
                'workflow_templates', 'workflow_rules', 'workflow_actions',
                'workflow_executions', 'tickets', 'time_entries', 'knowledge_base_articles',
                'knowledge_base_attachments', 'dashboard_templates', 'dashboard_widgets',
                'dashboards', 'widget_templates'
            ],
            
            # CURRENCY TABLES (Query-Level Only)
            'currency': [
                'currencies', 'currency_conversions', 'exchange_rates'
            ]
        }
        
        return business_tables
    
    def add_tenant_id_columns(self):
        """Add tenant_id column to all business tables"""
        logger.info("🏢 ADDING TENANT_ID COLUMNS TO BUSINESS TABLES")
        logger.info("=" * 60)
        
        business_tables = self.get_business_tables()
        
        # Combine all tables that need tenant_id
        tables_needing_tenant_id = []
        for category, tables in business_tables.items():
            if category != 'system_tables':  # System tables don't need tenant_id
                tables_needing_tenant_id.extend(tables)
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for table in tables_needing_tenant_id:
                try:
                    # Check if table exists
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name
                        )
                    """), {"table_name": table})
                    
                    table_exists = result.scalar()
                    
                    if not table_exists:
                        logger.warning(f"⚠️  Table '{table}' does not exist, skipping...")
                        continue
                    
                    # Check if tenant_id column already exists
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name 
                            AND column_name = 'tenant_id'
                        )
                    """), {"table_name": table})
                    
                    tenant_id_exists = result.scalar()
                    
                    if tenant_id_exists:
                        logger.info(f"✅ Table '{table}' already has tenant_id column")
                        success_count += 1
                        continue
                    
                    # Add tenant_id column
                    conn.execute(text(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default_tenant'
                    """))
                    
                    # Add foreign key constraint to tenants table
                    conn.execute(text(f"""
                        ALTER TABLE {table} 
                        ADD CONSTRAINT fk_{table}_tenant_id 
                        FOREIGN KEY (tenant_id) REFERENCES tenants(id) 
                        ON DELETE CASCADE
                    """))
                    
                    # Add index for performance
                    conn.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS idx_{table}_tenant_id 
                        ON {table} (tenant_id)
                    """))
                    
                    conn.commit()
                    logger.info(f"✅ Added tenant_id to table '{table}'")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add tenant_id to table '{table}': {e}")
                    error_count += 1
                    conn.rollback()
        
        logger.info(f"\n📊 TENANT_ID COLUMN ADDITION SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} tables")
        logger.info(f"   ❌ Errors: {error_count} tables")
        
        return success_count, error_count
    
    def create_rls_policies(self):
        """Create Row Level Security policies for core business tables"""
        logger.info("\n🔒 CREATING ROW LEVEL SECURITY POLICIES")
        logger.info("=" * 60)
        
        business_tables = self.get_business_tables()
        
        # Tables that need RLS (core business data)
        rls_tables = []
        for category, tables in business_tables.items():
            if category in ['core_business', 'finance', 'inventory', 'crm', 'procurement', 'sales']:
                rls_tables.extend(tables)
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for table in rls_tables:
                try:
                    # Check if table exists
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name
                        )
                    """), {"table_name": table})
                    
                    table_exists = result.scalar()
                    
                    if not table_exists:
                        logger.warning(f"⚠️  Table '{table}' does not exist, skipping RLS...")
                        continue
                    
                    # Enable RLS on table
                    conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
                    
                    # Create tenant isolation policy
                    policy_name = f"tenant_isolation_{table}"
                    
                    # Drop existing policy if it exists
                    conn.execute(text(f"""
                        DROP POLICY IF EXISTS {policy_name} ON {table}
                    """))
                    
                    # Create new policy
                    conn.execute(text(f"""
                        CREATE POLICY {policy_name} ON {table}
                        USING (tenant_id = current_setting('my.tenant_id', true))
                    """))
                    
                    conn.commit()
                    logger.info(f"✅ Created RLS policy for table '{table}'")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create RLS policy for table '{table}': {e}")
                    error_count += 1
                    conn.rollback()
        
        logger.info(f"\n📊 RLS POLICY CREATION SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} tables")
        logger.info(f"   ❌ Errors: {error_count} tables")
        
        return success_count, error_count
    
    def create_tenant_context_functions(self):
        """Create PostgreSQL functions for tenant context management"""
        logger.info("\n🔧 CREATING TENANT CONTEXT FUNCTIONS")
        logger.info("=" * 60)
        
        functions = [
            # Function to set tenant context
            """
            CREATE OR REPLACE FUNCTION set_tenant_context(tenant_uuid VARCHAR(50))
            RETURNS VOID AS $$
            BEGIN
                PERFORM set_config('my.tenant_id', tenant_uuid, false);
            END;
            $$ LANGUAGE plpgsql;
            """,
            
            # Function to get current tenant
            """
            CREATE OR REPLACE FUNCTION get_current_tenant()
            RETURNS VARCHAR(50) AS $$
            BEGIN
                RETURN current_setting('my.tenant_id', true);
            END;
            $$ LANGUAGE plpgsql;
            """,
            
            # Function to validate tenant access
            """
            CREATE OR REPLACE FUNCTION validate_tenant_access(user_id INTEGER, tenant_id VARCHAR(50))
            RETURNS BOOLEAN AS $$
            DECLARE
                has_access BOOLEAN := FALSE;
            BEGIN
                SELECT EXISTS(
                    SELECT 1 FROM user_tenants ut
                    WHERE ut.user_id = validate_tenant_access.user_id
                    AND ut.tenant_id = validate_tenant_access.tenant_id
                    AND ut.is_active = TRUE
                ) INTO has_access;
                
                RETURN has_access;
            END;
            $$ LANGUAGE plpgsql;
            """,
            
            # Function to audit tenant access
            """
            CREATE OR REPLACE FUNCTION audit_tenant_access(
                user_id INTEGER,
                tenant_id VARCHAR(50),
                action VARCHAR(100),
                table_name VARCHAR(100),
                record_id VARCHAR(100) DEFAULT NULL
            )
            RETURNS VOID AS $$
            BEGIN
                INSERT INTO audit_logs (
                    user_id, tenant_id, action, table_name, record_id, 
                    timestamp, ip_address, user_agent
                ) VALUES (
                    audit_tenant_access.user_id,
                    audit_tenant_access.tenant_id,
                    audit_tenant_access.action,
                    audit_tenant_access.table_name,
                    audit_tenant_access.record_id,
                    NOW(),
                    inet_client_addr(),
                    current_setting('my.user_agent', true)
                );
            END;
            $$ LANGUAGE plpgsql;
            """
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for i, function_sql in enumerate(functions, 1):
                try:
                    conn.execute(text(function_sql))
                    conn.commit()
                    logger.info(f"✅ Created tenant context function {i}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create tenant context function {i}: {e}")
                    error_count += 1
                    conn.rollback()
        
        logger.info(f"\n📊 TENANT CONTEXT FUNCTIONS SUMMARY:")
        logger.info(f"   ✅ Successfully created: {success_count} functions")
        logger.info(f"   ❌ Errors: {error_count} functions")
        
        return success_count, error_count
    
    def create_audit_triggers(self):
        """Create audit triggers for tenant isolation monitoring"""
        logger.info("\n📝 CREATING AUDIT TRIGGERS FOR TENANT ISOLATION")
        logger.info("=" * 60)
        
        # Core business tables that need audit triggers
        audit_tables = [
            'users', 'accounts', 'journal_entries', 'products', 'customers',
            'invoices', 'purchase_orders', 'payments', 'bank_accounts'
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            # Create audit function
            audit_function = """
            CREATE OR REPLACE FUNCTION audit_tenant_changes()
            RETURNS TRIGGER AS $$
            DECLARE
                old_tenant_id VARCHAR(50);
                new_tenant_id VARCHAR(50);
            BEGIN
                -- Get tenant IDs
                IF TG_OP = 'DELETE' THEN
                    old_tenant_id := OLD.tenant_id;
                    new_tenant_id := NULL;
                ELSIF TG_OP = 'INSERT' THEN
                    old_tenant_id := NULL;
                    new_tenant_id := NEW.tenant_id;
                ELSE -- UPDATE
                    old_tenant_id := OLD.tenant_id;
                    new_tenant_id := NEW.tenant_id;
                END IF;
                
                -- Log the change
                INSERT INTO audit_logs (
                    user_id, tenant_id, action, table_name, record_id,
                    old_values, new_values, timestamp, ip_address
                ) VALUES (
                    COALESCE(current_setting('my.user_id', true)::INTEGER, 0),
                    COALESCE(new_tenant_id, old_tenant_id),
                    TG_OP,
                    TG_TABLE_NAME,
                    COALESCE(NEW.id::VARCHAR, OLD.id::VARCHAR),
                    CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
                    CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
                    NOW(),
                    inet_client_addr()
                );
                
                RETURN COALESCE(NEW, OLD);
            END;
            $$ LANGUAGE plpgsql;
            """
            
            try:
                conn.execute(text(audit_function))
                conn.commit()
                logger.info("✅ Created audit function")
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to create audit function: {e}")
                error_count += 1
                conn.rollback()
            
            # Create triggers for each table
            for table in audit_tables:
                try:
                    # Check if table exists
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name
                        )
                    """), {"table_name": table})
                    
                    table_exists = result.scalar()
                    
                    if not table_exists:
                        logger.warning(f"⚠️  Table '{table}' does not exist, skipping audit trigger...")
                        continue
                    
                    # Drop existing trigger if it exists
                    conn.execute(text(f"""
                        DROP TRIGGER IF EXISTS audit_tenant_changes_{table} ON {table}
                    """))
                    
                    # Create new trigger
                    conn.execute(text(f"""
                        CREATE TRIGGER audit_tenant_changes_{table}
                        AFTER INSERT OR UPDATE OR DELETE ON {table}
                        FOR EACH ROW EXECUTE FUNCTION audit_tenant_changes()
                    """))
                    
                    conn.commit()
                    logger.info(f"✅ Created audit trigger for table '{table}'")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create audit trigger for table '{table}': {e}")
                    error_count += 1
                    conn.rollback()
        
        logger.info(f"\n📊 AUDIT TRIGGERS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} triggers")
        logger.info(f"   ❌ Errors: {error_count} triggers")
        
        return success_count, error_count
    
    def create_performance_indexes(self):
        """Create performance indexes for tenant isolation"""
        logger.info("\n⚡ CREATING PERFORMANCE INDEXES FOR TENANT ISOLATION")
        logger.info("=" * 60)
        
        # Indexes for tenant isolation performance
        indexes = [
            # Composite indexes for common query patterns
            "CREATE INDEX IF NOT EXISTS idx_users_tenant_active ON users (tenant_id, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_accounts_tenant_type ON accounts (tenant_id, account_type)",
            "CREATE INDEX IF NOT EXISTS idx_products_tenant_category ON products (tenant_id, category_id)",
            "CREATE INDEX IF NOT EXISTS idx_customers_tenant_status ON customers (tenant_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_invoices_tenant_date ON invoices (tenant_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_payments_tenant_method ON payments (tenant_id, payment_method)",
            "CREATE INDEX IF NOT EXISTS idx_stock_movements_tenant_date ON stock_movements (tenant_id, created_at)",
            
            # Partial indexes for active records
            "CREATE INDEX IF NOT EXISTS idx_users_active_tenant ON users (tenant_id) WHERE is_active = TRUE",
            "CREATE INDEX IF NOT EXISTS idx_products_active_tenant ON products (tenant_id) WHERE is_active = TRUE",
            "CREATE INDEX IF NOT EXISTS idx_customers_active_tenant ON customers (tenant_id) WHERE is_active = TRUE",
            
            # Indexes for audit logs
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_date ON audit_logs (tenant_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_tenant ON audit_logs (user_id, tenant_id)",
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for i, index_sql in enumerate(indexes, 1):
                try:
                    conn.execute(text(index_sql))
                    conn.commit()
                    logger.info(f"✅ Created performance index {i}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create performance index {i}: {e}")
                    error_count += 1
                    conn.rollback()
        
        logger.info(f"\n📊 PERFORMANCE INDEXES SUMMARY:")
        logger.info(f"   ✅ Successfully created: {success_count} indexes")
        logger.info(f"   ❌ Errors: {error_count} indexes")
        
        return success_count, error_count
    
    def run_implementation(self):
        """Run the complete tenant isolation implementation"""
        logger.info("🚀 EDONUOPS ERP - TENANT ISOLATION IMPLEMENTATION")
        logger.info("=" * 60)
        logger.info("🏢 Strategy: Hybrid RLS + Query-Level Isolation")
        logger.info("🔒 RLS: Strict tenant boundaries for core business data")
        logger.info("🔧 Query-Level: Complex permissions, role-based access")
        logger.info("📝 Audit: Comprehensive logging for compliance")
        logger.info("=" * 60)
        
        if not self.connect_to_database():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Step 1: Add tenant_id columns
            logger.info("\n📋 STEP 1: Adding tenant_id columns to business tables")
            tenant_success, tenant_errors = self.add_tenant_id_columns()
            
            # Step 2: Create RLS policies
            logger.info("\n📋 STEP 2: Creating Row Level Security policies")
            rls_success, rls_errors = self.create_rls_policies()
            
            # Step 3: Create tenant context functions
            logger.info("\n📋 STEP 3: Creating tenant context functions")
            func_success, func_errors = self.create_tenant_context_functions()
            
            # Step 4: Create audit triggers
            logger.info("\n📋 STEP 4: Creating audit triggers")
            audit_success, audit_errors = self.create_audit_triggers()
            
            # Step 5: Create performance indexes
            logger.info("\n📋 STEP 5: Creating performance indexes")
            index_success, index_errors = self.create_performance_indexes()
            
            # Summary
            total_success = tenant_success + rls_success + func_success + audit_success + index_success
            total_errors = tenant_errors + rls_errors + func_errors + audit_errors + index_errors
            
            logger.info("\n🎉 TENANT ISOLATION IMPLEMENTATION COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"✅ Total operations successful: {total_success}")
            logger.info(f"❌ Total errors: {total_errors}")
            
            if total_errors == 0:
                logger.info("\n🔒 YOUR ERP NOW HAS ENTERPRISE-GRADE TENANT ISOLATION!")
                logger.info("📊 Features implemented:")
                logger.info("   • RLS policies for core business data")
                logger.info("   • Tenant context management functions")
                logger.info("   • Comprehensive audit logging")
                logger.info("   • Performance-optimized indexes")
                logger.info("   • Hybrid isolation strategy")
                
                logger.info("\n🎯 NEXT STEPS:")
                logger.info("   1. Update application code to use tenant context")
                logger.info("   2. Test tenant isolation with sample data")
                logger.info("   3. Implement tenant context middleware")
                logger.info("   4. Add tenant validation to all API endpoints")
                
                return True
            else:
                logger.warning(f"\n⚠️  Implementation completed with {total_errors} errors")
                logger.warning("   Please review the errors above and fix them")
                return False
                
        except Exception as e:
            logger.error(f"❌ Implementation failed: {e}")
            return False

def main():
    """Main function to run tenant isolation implementation"""
    implementer = TenantIsolationImplementer()
    success = implementer.run_implementation()
    
    if success:
        print("\n🎉 Tenant isolation implementation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Tenant isolation implementation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
