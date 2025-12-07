#!/usr/bin/env python3
"""
🔧 EDONUOPS ERP - PHASE 2 DATABASE FIXES
============================================================

Fixes Phase 2 implementation errors:
- Corrects token cleanup function syntax
- Fixes PostgreSQL extension syntax
- Completes remaining enhancements

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

class Phase2DatabaseFixer:
    def __init__(self):
        """Initialize the Phase 2 database fixer"""
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
    
    def fix_token_cleanup_function(self):
        """Fix the token cleanup function with correct PostgreSQL syntax"""
        logger.info("\n🔧 FIXING TOKEN CLEANUP FUNCTION")
        logger.info("=" * 60)
        
        # Fixed token cleanup function
        cleanup_function = """
        CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER := 0;
            temp_count INTEGER;
        BEGIN
            -- Clean up expired email verification tokens
            DELETE FROM email_verification_tokens 
            WHERE expires_at < NOW() AND used = FALSE;
            GET DIAGNOSTICS temp_count = ROW_COUNT;
            deleted_count := deleted_count + temp_count;
            
            -- Clean up expired password reset tokens
            DELETE FROM password_reset_tokens 
            WHERE expires_at < NOW() AND used = FALSE;
            GET DIAGNOSTICS temp_count = ROW_COUNT;
            deleted_count := deleted_count + temp_count;
            
            -- Clean up old login attempts (older than 30 days)
            DELETE FROM login_attempts 
            WHERE attempt_time < NOW() - INTERVAL '30 days';
            GET DIAGNOSTICS temp_count = ROW_COUNT;
            deleted_count := deleted_count + temp_count;
            
            -- Clean up old audit logs (older than 90 days)
            DELETE FROM audit_logs 
            WHERE timestamp < NOW() - INTERVAL '90 days';
            GET DIAGNOSTICS temp_count = ROW_COUNT;
            deleted_count := deleted_count + temp_count;
            
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create fixed cleanup function
                conn.execute(text(cleanup_function))
                logger.info("✅ Created fixed token cleanup function")
                success_count += 1
                
                # Test the cleanup function
                result = conn.execute(text("SELECT cleanup_expired_tokens()"))
                deleted_count = result.scalar()
                logger.info(f"✅ Tested cleanup function - deleted {deleted_count} expired records")
                success_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to fix token cleanup function: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 TOKEN CLEANUP FIX SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def fix_postgres_extensions(self):
        """Fix PostgreSQL extensions with correct syntax"""
        logger.info("\n🔧 FIXING POSTGRESQL EXTENSIONS")
        logger.info("=" * 60)
        
        # Fixed extensions with proper syntax
        extensions = [
            "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;",  # Query performance insights
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;",  # Fuzzy matching for suspicious patterns
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',  # UUID generation (quoted)
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
        
        logger.info(f"\n📊 POSTGRESQL EXTENSIONS FIX SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} extensions")
        logger.info(f"   ❌ Errors: {error_count} extensions")
        
        return success_count, error_count
    
    def create_refresh_views_function(self):
        """Create function to refresh materialized views"""
        logger.info("\n🔄 CREATING MATERIALIZED VIEW REFRESH FUNCTION")
        logger.info("=" * 60)
        
        refresh_function = """
        CREATE OR REPLACE FUNCTION refresh_tenant_activity_views()
        RETURNS VOID AS $$
        BEGIN
            -- Refresh all tenant activity materialized views
            REFRESH MATERIALIZED VIEW CONCURRENTLY tenant_login_summary;
            REFRESH MATERIALIZED VIEW CONCURRENTLY tenant_token_usage;
            REFRESH MATERIALIZED VIEW CONCURRENTLY tenant_security_alerts;
            
            -- Log the refresh
            INSERT INTO cleanup_jobs (job_name, last_run, status)
            VALUES ('refresh_tenant_views', NOW(), 'SUCCESS')
            ON CONFLICT (job_name) DO UPDATE SET 
                last_run = NOW(),
                status = 'SUCCESS';
        END;
        $$ LANGUAGE plpgsql;
        """
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create refresh function
                conn.execute(text(refresh_function))
                logger.info("✅ Created materialized view refresh function")
                success_count += 1
                
                # Test the refresh function
                conn.execute(text("SELECT refresh_tenant_activity_views()"))
                logger.info("✅ Tested materialized view refresh function")
                success_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create refresh function: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 MATERIALIZED VIEW REFRESH FUNCTION SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_sample_queries(self):
        """Create sample queries for developers"""
        logger.info("\n📝 CREATING SAMPLE QUERIES FOR DEVELOPERS")
        logger.info("=" * 60)
        
        # Create a table to store sample queries
        sample_queries_table = """
        CREATE TABLE IF NOT EXISTS sample_queries (
            id SERIAL PRIMARY KEY,
            query_name VARCHAR(100) NOT NULL,
            description TEXT,
            query_sql TEXT NOT NULL,
            category VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Sample queries for tenant-safe operations
        sample_queries_data = [
            {
                'name': 'get_tenant_users',
                'description': 'Get all users for current tenant',
                'query': "SELECT id, username, email, is_active, last_login FROM users WHERE tenant_id = current_setting('my.tenant_id', true);",
                'category': 'users'
            },
            {
                'name': 'get_login_attempts_summary',
                'description': 'Get login attempt summary for current tenant',
                'query': "SELECT DATE(attempt_time) as date, COUNT(*) as attempts, COUNT(CASE WHEN success = TRUE THEN 1 END) as successful FROM login_attempts WHERE tenant_id = current_setting('my.tenant_id', true) GROUP BY DATE(attempt_time) ORDER BY date DESC LIMIT 7;",
                'category': 'security'
            },
            {
                'name': 'get_active_tokens',
                'description': 'Get active tokens for current tenant',
                'query': "SELECT 'email_verification' as type, COUNT(*) as active FROM email_verification_tokens WHERE tenant_id = current_setting('my.tenant_id', true) AND expires_at > NOW() AND used = FALSE UNION ALL SELECT 'password_reset' as type, COUNT(*) as active FROM password_reset_tokens WHERE tenant_id = current_setting('my.tenant_id', true) AND expires_at > NOW() AND used = FALSE;",
                'category': 'security'
            },
            {
                'name': 'get_tenant_audit_logs',
                'description': 'Get recent audit logs for current tenant',
                'query': "SELECT table_name, action_type, timestamp, user_id FROM audit_logs WHERE tenant_id = current_setting('my.tenant_id', true) ORDER BY timestamp DESC LIMIT 50;",
                'category': 'audit'
            }
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create sample queries table
                conn.execute(text(sample_queries_table))
                logger.info("✅ Created sample queries table")
                success_count += 1
                
                # Insert sample queries
                for query_data in sample_queries_data:
                    conn.execute(text("""
                        INSERT INTO sample_queries (query_name, description, query_sql, category)
                        VALUES (:name, :description, :query, :category)
                        ON CONFLICT (query_name) DO NOTHING
                    """), query_data)
                
                logger.info(f"✅ Inserted {len(sample_queries_data)} sample queries")
                success_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create sample queries: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 SAMPLE QUERIES SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def run_phase2_fixes(self):
        """Run Phase 2 database fixes"""
        logger.info("🔧 EDONUOPS ERP - PHASE 2 DATABASE FIXES")
        logger.info("=" * 60)
        logger.info("🔧 Fixing Phase 2 implementation errors")
        logger.info("📊 Completing enterprise-grade database features")
        logger.info("=" * 60)
        
        if not self.connect_to_database():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Step 1: Fix token cleanup function
            logger.info("\n📋 STEP 1: Fixing token cleanup function")
            cleanup_success, cleanup_errors = self.fix_token_cleanup_function()
            
            # Step 2: Fix PostgreSQL extensions
            logger.info("\n📋 STEP 2: Fixing PostgreSQL extensions")
            extensions_success, extensions_errors = self.fix_postgres_extensions()
            
            # Step 3: Create refresh views function
            logger.info("\n📋 STEP 3: Creating materialized view refresh function")
            refresh_success, refresh_errors = self.create_refresh_views_function()
            
            # Step 4: Create sample queries
            logger.info("\n📋 STEP 4: Creating sample queries for developers")
            queries_success, queries_errors = self.create_sample_queries()
            
            # Summary
            total_success = cleanup_success + extensions_success + refresh_success + queries_success
            total_errors = cleanup_errors + extensions_errors + refresh_errors + queries_errors
            
            logger.info("\n🎉 PHASE 2 DATABASE FIXES COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"✅ Total operations successful: {total_success}")
            logger.info(f"❌ Total errors: {total_errors}")
            
            if total_errors == 0:
                logger.info("\n🏗️ YOUR ERP DATABASE IS NOW ENTERPRISE-READY!")
                logger.info("📊 Phase 2 fixes completed:")
                logger.info("   • Fixed token cleanup function with correct PostgreSQL syntax")
                logger.info("   • Enabled PostgreSQL extensions for performance and monitoring")
                logger.info("   • Created materialized view refresh function")
                logger.info("   • Added sample queries for safe tenant operations")
                
                logger.info("\n🎯 DATABASE FOUNDATION COMPLETE!")
                logger.info("   ✅ Phase 1: Security tables and RLS policies")
                logger.info("   ✅ Phase 2: Enterprise enhancements and monitoring")
                logger.info("   ✅ Soft deletes: Data recovery capabilities")
                logger.info("   ✅ Audit logging: Comprehensive change tracking")
                logger.info("   ✅ Performance: Optimized indexes and materialized views")
                logger.info("   ✅ Monitoring: Tenant activity reports and alerts")
                
                return True
            else:
                logger.warning(f"\n⚠️  Fixes completed with {total_errors} errors")
                logger.warning("   Please review the errors above and fix them")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fixes failed: {e}")
            return False

def main():
    """Main function to run Phase 2 database fixes"""
    fixer = Phase2DatabaseFixer()
    success = fixer.run_phase2_fixes()
    
    if success:
        print("\n🎉 Phase 2 database fixes completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Phase 2 database fixes failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
