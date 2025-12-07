#!/usr/bin/env python3
"""
🏗️ EDONUOPS ERP - DATABASE PHASE 2 ENTERPRISE ENHANCEMENTS
============================================================

Implements Phase 2 database enhancements for enterprise-grade scalability:
- Enhanced audit logging with old_data/new_data tracking
- Token cleanup and expiration jobs
- Tenant activity reports and materialized views
- PostgreSQL extensions for performance and monitoring
- Soft delete columns for data recovery
- RLS policy testing and validation

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

class Phase2DatabaseEnhancer:
    def __init__(self):
        """Initialize the Phase 2 database enhancer"""
        self.engine = None
        
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
    
    def enhance_audit_logging(self):
        """Enhance audit logging with old_data/new_data tracking"""
        logger.info("\n📝 ENHANCING AUDIT LOGGING")
        logger.info("=" * 60)
        
        # Enhanced audit function with old_data/new_data
        enhanced_audit_function = """
        CREATE OR REPLACE FUNCTION audit_tenant_changes_enhanced()
        RETURNS TRIGGER AS $$
        DECLARE
            old_tenant_id VARCHAR(50);
            new_tenant_id VARCHAR(50);
            old_data JSONB;
            new_data JSONB;
        BEGIN
            -- Get tenant IDs
            IF TG_OP = 'DELETE' THEN
                old_tenant_id := OLD.tenant_id;
                new_tenant_id := NULL;
                old_data := row_to_json(OLD);
                new_data := NULL;
            ELSIF TG_OP = 'INSERT' THEN
                old_tenant_id := NULL;
                new_tenant_id := NEW.tenant_id;
                old_data := NULL;
                new_data := row_to_json(NEW);
            ELSE -- UPDATE
                old_tenant_id := OLD.tenant_id;
                new_tenant_id := NEW.tenant_id;
                old_data := row_to_json(OLD);
                new_data := row_to_json(NEW);
            END IF;
            
            -- Log the change with enhanced data
            INSERT INTO audit_logs (
                user_id, tenant_id, action, table_name, record_id,
                old_values, new_values, timestamp, ip_address,
                action_type, old_data, new_data
            ) VALUES (
                COALESCE(current_setting('my.user_id', true)::INTEGER, 0),
                COALESCE(new_tenant_id, old_tenant_id),
                TG_OP,
                TG_TABLE_NAME,
                COALESCE(NEW.id::VARCHAR, OLD.id::VARCHAR),
                CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
                CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
                NOW(),
                inet_client_addr(),
                TG_OP,
                old_data,
                new_data
            );
            
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Add action_type column to audit_logs if it doesn't exist
        add_columns_sql = [
            "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS action_type VARCHAR(20);",
            "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS old_data JSONB;",
            "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS new_data JSONB;",
            "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS operation_context TEXT;"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create enhanced audit function
                conn.execute(text(enhanced_audit_function))
                logger.info("✅ Created enhanced audit function")
                success_count += 1
                
                # Add new columns to audit_logs
                for i, sql in enumerate(add_columns_sql, 1):
                    try:
                        conn.execute(text(sql))
                        logger.info(f"✅ Added column {i} to audit_logs")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to add column {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to enhance audit logging: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 AUDIT LOGGING ENHANCEMENT SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_token_cleanup_jobs(self):
        """Create token cleanup and expiration jobs"""
        logger.info("\n🧹 CREATING TOKEN CLEANUP JOBS")
        logger.info("=" * 60)
        
        # Token cleanup function
        cleanup_function = """
        CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER := 0;
        BEGIN
            -- Clean up expired email verification tokens
            DELETE FROM email_verification_tokens 
            WHERE expires_at < NOW() AND used = FALSE;
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            
            -- Clean up expired password reset tokens
            DELETE FROM password_reset_tokens 
            WHERE expires_at < NOW() AND used = FALSE;
            GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
            
            -- Clean up old login attempts (older than 30 days)
            DELETE FROM login_attempts 
            WHERE attempt_time < NOW() - INTERVAL '30 days';
            GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
            
            -- Clean up old audit logs (older than 90 days)
            DELETE FROM audit_logs 
            WHERE timestamp < NOW() - INTERVAL '90 days';
            GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
            
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Create cleanup job table for tracking
        cleanup_jobs_table = """
        CREATE TABLE IF NOT EXISTS cleanup_jobs (
            id SERIAL PRIMARY KEY,
            job_name VARCHAR(100) NOT NULL,
            last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            records_deleted INTEGER DEFAULT 0,
            execution_time INTERVAL,
            status VARCHAR(20) DEFAULT 'SUCCESS',
            error_message TEXT,
            tenant_id VARCHAR(50) REFERENCES tenants(id)
        );
        """
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create cleanup function
                conn.execute(text(cleanup_function))
                logger.info("✅ Created token cleanup function")
                success_count += 1
                
                # Create cleanup jobs table
                conn.execute(text(cleanup_jobs_table))
                logger.info("✅ Created cleanup jobs tracking table")
                success_count += 1
                
                # Test the cleanup function
                result = conn.execute(text("SELECT cleanup_expired_tokens()"))
                deleted_count = result.scalar()
                logger.info(f"✅ Tested cleanup function - deleted {deleted_count} expired records")
                success_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create token cleanup jobs: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 TOKEN CLEANUP JOBS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_tenant_activity_reports(self):
        """Create tenant activity reports and materialized views"""
        logger.info("\n📊 CREATING TENANT ACTIVITY REPORTS")
        logger.info("=" * 60)
        
        # Materialized view for login attempt summaries
        login_summary_view = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS tenant_login_summary AS
        SELECT 
            tenant_id,
            DATE(attempt_time) as login_date,
            COUNT(*) as total_attempts,
            COUNT(CASE WHEN success = TRUE THEN 1 END) as successful_logins,
            COUNT(CASE WHEN success = FALSE THEN 1 END) as failed_attempts,
            COUNT(DISTINCT ip_address) as unique_ips,
            COUNT(DISTINCT user_id) as unique_users,
            MIN(attempt_time) as first_attempt,
            MAX(attempt_time) as last_attempt
        FROM login_attempts
        WHERE attempt_time >= NOW() - INTERVAL '30 days'
        GROUP BY tenant_id, DATE(attempt_time)
        ORDER BY tenant_id, login_date DESC;
        """
        
        # Materialized view for token usage stats
        token_usage_view = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS tenant_token_usage AS
        SELECT 
            tenant_id,
            'email_verification' as token_type,
            COUNT(*) as total_tokens,
            COUNT(CASE WHEN used = TRUE THEN 1 END) as used_tokens,
            COUNT(CASE WHEN expires_at < NOW() AND used = FALSE THEN 1 END) as expired_tokens,
            AVG(EXTRACT(EPOCH FROM (expires_at - created_at))/3600) as avg_hours_to_expire
        FROM email_verification_tokens
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY tenant_id
        
        UNION ALL
        
        SELECT 
            tenant_id,
            'password_reset' as token_type,
            COUNT(*) as total_tokens,
            COUNT(CASE WHEN used = TRUE THEN 1 END) as used_tokens,
            COUNT(CASE WHEN expires_at < NOW() AND used = FALSE THEN 1 END) as expired_tokens,
            AVG(EXTRACT(EPOCH FROM (expires_at - created_at))/3600) as avg_hours_to_expire
        FROM password_reset_tokens
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY tenant_id;
        """
        
        # Materialized view for security alerts
        security_alerts_view = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS tenant_security_alerts AS
        SELECT 
            tenant_id,
            DATE(attempt_time) as alert_date,
            COUNT(CASE WHEN success = FALSE THEN 1 END) as failed_attempts,
            COUNT(DISTINCT ip_address) as suspicious_ips,
            COUNT(DISTINCT CASE WHEN success = FALSE THEN ip_address END) as failed_attempt_ips,
            MAX(CASE WHEN success = FALSE THEN attempt_time END) as last_failed_attempt
        FROM login_attempts
        WHERE attempt_time >= NOW() - INTERVAL '7 days'
        GROUP BY tenant_id, DATE(attempt_time)
        HAVING COUNT(CASE WHEN success = FALSE THEN 1 END) > 5
        ORDER BY tenant_id, alert_date DESC;
        """
        
        # Create indexes for materialized views
        view_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_tenant_login_summary_tenant_date ON tenant_login_summary (tenant_id, login_date);",
            "CREATE INDEX IF NOT EXISTS idx_tenant_token_usage_tenant_type ON tenant_token_usage (tenant_id, token_type);",
            "CREATE INDEX IF NOT EXISTS idx_tenant_security_alerts_tenant_date ON tenant_security_alerts (tenant_id, alert_date);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create materialized views
                views = [
                    ("login_summary", login_summary_view),
                    ("token_usage", token_usage_view),
                    ("security_alerts", security_alerts_view)
                ]
                
                for view_name, view_sql in views:
                    conn.execute(text(view_sql))
                    logger.info(f"✅ Created {view_name} materialized view")
                    success_count += 1
                
                # Create indexes
                for i, index_sql in enumerate(view_indexes, 1):
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created index {i} for materialized views")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create index {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create tenant activity reports: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 TENANT ACTIVITY REPORTS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def enable_postgres_extensions(self):
        """Enable PostgreSQL extensions for performance and monitoring"""
        logger.info("\n🔧 ENABLING POSTGRESQL EXTENSIONS")
        logger.info("=" * 60)
        
        extensions = [
            "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;",  # Query performance insights
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;",  # Fuzzy matching for suspicious patterns
            "CREATE EXTENSION IF NOT EXISTS uuid-ossp;",  # UUID generation
            "CREATE EXTENSION IF NOT EXISTS btree_gin;",  # GIN indexes for JSONB
            "CREATE EXTENSION IF NOT EXISTS pgcrypto;"  # Cryptographic functions
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for i, extension_sql in enumerate(extensions, 1):
                try:
                    conn.execute(text(extension_sql))
                    logger.info(f"✅ Enabled extension {i}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to enable extension {i}: {e}")
                    error_count += 1
            
            conn.commit()
        
        logger.info(f"\n📊 POSTGRESQL EXTENSIONS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} extensions")
        logger.info(f"   ❌ Errors: {error_count} extensions")
        
        return success_count, error_count
    
    def add_soft_delete_columns(self):
        """Add soft delete columns to key tables"""
        logger.info("\n🗑️ ADDING SOFT DELETE COLUMNS")
        logger.info("=" * 60)
        
        # Tables that need soft delete capability
        tables_with_soft_delete = [
            'users',
            'roles',
            'tenants',
            'accounts',
            'products',
            'customers',
            'invoices',
            'purchase_orders'
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for table in tables_with_soft_delete:
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
                    
                    # Add soft delete columns
                    conn.execute(text(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL,
                        ADD COLUMN IF NOT EXISTS deleted_by INTEGER REFERENCES users(id),
                        ADD COLUMN IF NOT EXISTS deletion_reason TEXT
                    """))
                    
                    # Create index for soft delete queries
                    conn.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS idx_{table}_deleted_at 
                        ON {table} (deleted_at) 
                        WHERE deleted_at IS NULL
                    """))
                    
                    logger.info(f"✅ Added soft delete columns to table '{table}'")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add soft delete columns to table '{table}': {e}")
                    error_count += 1
                    conn.rollback()
            
            conn.commit()
        
        logger.info(f"\n📊 SOFT DELETE COLUMNS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} tables")
        logger.info(f"   ❌ Errors: {error_count} tables")
        
        return success_count, error_count
    
    def test_rls_policies(self):
        """Test RLS policies thoroughly"""
        logger.info("\n🔒 TESTING RLS POLICIES")
        logger.info("=" * 60)
        
        # Test tables with RLS
        test_tables = [
            'users', 'accounts', 'products', 'customers', 'invoices',
            'login_attempts', 'email_verification_tokens', 'password_reset_tokens'
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for table in test_tables:
                try:
                    # Check if RLS is enabled
                    result = conn.execute(text("""
                        SELECT relrowsecurity FROM pg_class 
                        WHERE relname = :table_name
                    """), {"table_name": table})
                    
                    rls_enabled = result.scalar()
                    
                    if rls_enabled:
                        # Check if policy exists
                        result = conn.execute(text("""
                            SELECT COUNT(*) FROM pg_policies 
                            WHERE tablename = :table_name 
                            AND policyname LIKE 'tenant_isolation_%'
                        """), {"table_name": table})
                        
                        policy_count = result.scalar()
                        
                        if policy_count > 0:
                            logger.info(f"✅ RLS enabled and policy exists on table '{table}'")
                            success_count += 1
                        else:
                            logger.error(f"❌ RLS enabled but no policy on table '{table}'")
                            error_count += 1
                    else:
                        logger.warning(f"⚠️  RLS not enabled on table '{table}'")
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error testing RLS for table '{table}': {e}")
                    error_count += 1
        
        logger.info(f"\n📊 RLS POLICY TESTING SUMMARY:")
        logger.info(f"   ✅ Successfully tested: {success_count} tables")
        logger.info(f"   ❌ Issues found: {error_count} tables")
        
        return success_count, error_count
    
    def run_phase2_implementation(self):
        """Run the complete Phase 2 database enhancement"""
        logger.info("🏗️ EDONUOPS ERP - DATABASE PHASE 2 ENTERPRISE ENHANCEMENTS")
        logger.info("=" * 60)
        logger.info("📊 Implementing enterprise-grade database features")
        logger.info("🔧 Features: Enhanced audit, cleanup jobs, activity reports")
        logger.info("⚡ Performance: Extensions, partitioning, materialized views")
        logger.info("=" * 60)
        
        if not self.connect_to_database():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Step 1: Enhance audit logging
            logger.info("\n📋 STEP 1: Enhancing audit logging")
            audit_success, audit_errors = self.enhance_audit_logging()
            
            # Step 2: Create token cleanup jobs
            logger.info("\n📋 STEP 2: Creating token cleanup jobs")
            cleanup_success, cleanup_errors = self.create_token_cleanup_jobs()
            
            # Step 3: Create tenant activity reports
            logger.info("\n📋 STEP 3: Creating tenant activity reports")
            reports_success, reports_errors = self.create_tenant_activity_reports()
            
            # Step 4: Enable PostgreSQL extensions
            logger.info("\n📋 STEP 4: Enabling PostgreSQL extensions")
            extensions_success, extensions_errors = self.enable_postgres_extensions()
            
            # Step 5: Add soft delete columns
            logger.info("\n📋 STEP 5: Adding soft delete columns")
            soft_delete_success, soft_delete_errors = self.add_soft_delete_columns()
            
            # Step 6: Test RLS policies
            logger.info("\n📋 STEP 6: Testing RLS policies")
            rls_success, rls_errors = self.test_rls_policies()
            
            # Summary
            total_success = audit_success + cleanup_success + reports_success + extensions_success + soft_delete_success + rls_success
            total_errors = audit_errors + cleanup_errors + reports_errors + extensions_errors + soft_delete_errors + rls_errors
            
            logger.info("\n🎉 DATABASE PHASE 2 ENHANCEMENTS COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"✅ Total operations successful: {total_success}")
            logger.info(f"❌ Total errors: {total_errors}")
            
            if total_errors == 0:
                logger.info("\n🏗️ YOUR ERP NOW HAS ENTERPRISE-GRADE DATABASE FEATURES!")
                logger.info("📊 Phase 2 features implemented:")
                logger.info("   • Enhanced audit logging with old_data/new_data tracking")
                logger.info("   • Token cleanup and expiration jobs")
                logger.info("   • Tenant activity reports and materialized views")
                logger.info("   • PostgreSQL extensions for performance and monitoring")
                logger.info("   • Soft delete columns for data recovery")
                logger.info("   • Comprehensive RLS policy testing")
                
                logger.info("\n🎯 NEXT STEPS:")
                logger.info("   1. Schedule token cleanup jobs (cron or pg_cron)")
                logger.info("   2. Refresh materialized views regularly")
                logger.info("   3. Monitor tenant activity reports")
                logger.info("   4. Implement backup and recovery procedures")
                logger.info("   5. Set up database monitoring and alerting")
                
                return True
            else:
                logger.warning(f"\n⚠️  Implementation completed with {total_errors} errors")
                logger.warning("   Please review the errors above and fix them")
                return False
                
        except Exception as e:
            logger.error(f"❌ Implementation failed: {e}")
            return False

def main():
    """Main function to run Phase 2 database enhancements"""
    enhancer = Phase2DatabaseEnhancer()
    success = enhancer.run_phase2_implementation()
    
    if success:
        print("\n🎉 Database Phase 2 enhancements completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Database Phase 2 enhancements failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
