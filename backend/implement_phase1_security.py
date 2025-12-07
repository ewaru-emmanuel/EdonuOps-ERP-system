#!/usr/bin/env python3
"""
🔒 EDONUOPS ERP - PHASE 1 SECURITY TABLES IMPLEMENTATION
============================================================

Implements Phase 1 security tables for enterprise-grade authentication:
- login_attempts: Rate limiting and security monitoring
- email_verification_tokens: Secure email verification
- password_reset_tokens: Secure password recovery
- updated_at triggers: Automatic timestamp updates

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

class Phase1SecurityImplementer:
    def __init__(self):
        """Initialize the Phase 1 security implementer"""
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
    
    def create_login_attempts_table(self):
        """Create login_attempts table for rate limiting and security monitoring"""
        logger.info("\n🔐 CREATING LOGIN_ATTEMPTS TABLE")
        logger.info("=" * 60)
        
        table_sql = """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            email VARCHAR(255), -- Track by email for non-existent users
            ip_address INET NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN NOT NULL,
            user_agent TEXT,
            tenant_id VARCHAR(50) REFERENCES tenants(id),
            failure_reason VARCHAR(100), -- e.g., 'invalid_password', 'user_not_found'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_time ON login_attempts (ip_address, attempt_time);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_user_time ON login_attempts (user_id, attempt_time);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_email_time ON login_attempts (email, attempt_time);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_tenant ON login_attempts (tenant_id);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_success ON login_attempts (success, attempt_time);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create table
                conn.execute(text(table_sql))
                logger.info("✅ Created login_attempts table")
                success_count += 1
                
                # Create indexes
                for i, index_sql in enumerate(indexes_sql, 1):
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created index {i} for login_attempts")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create index {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create login_attempts table: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 LOGIN_ATTEMPTS TABLE SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_email_verification_table(self):
        """Create email_verification_tokens table for secure email verification"""
        logger.info("\n📧 CREATING EMAIL_VERIFICATION_TOKENS TABLE")
        logger.info("=" * 60)
        
        table_sql = """
        CREATE TABLE IF NOT EXISTS email_verification_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL, -- Email being verified
            expires_at TIMESTAMP NOT NULL DEFAULT NOW() + INTERVAL '24 hours',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used BOOLEAN DEFAULT FALSE,
            used_at TIMESTAMP NULL,
            tenant_id VARCHAR(50) REFERENCES tenants(id),
            verification_type VARCHAR(50) DEFAULT 'registration' -- 'registration', 'email_change'
        );
        """
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_email_verification_token ON email_verification_tokens (token);",
            "CREATE INDEX IF NOT EXISTS idx_email_verification_user ON email_verification_tokens (user_id);",
            "CREATE INDEX IF NOT EXISTS idx_email_verification_email ON email_verification_tokens (email);",
            "CREATE INDEX IF NOT EXISTS idx_email_verification_expires ON email_verification_tokens (expires_at);",
            "CREATE INDEX IF NOT EXISTS idx_email_verification_tenant ON email_verification_tokens (tenant_id);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create table
                conn.execute(text(table_sql))
                logger.info("✅ Created email_verification_tokens table")
                success_count += 1
                
                # Create indexes
                for i, index_sql in enumerate(indexes_sql, 1):
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created index {i} for email_verification_tokens")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create index {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create email_verification_tokens table: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 EMAIL_VERIFICATION_TOKENS TABLE SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_password_reset_table(self):
        """Create password_reset_tokens table for secure password recovery"""
        logger.info("\n🔑 CREATING PASSWORD_RESET_TOKENS TABLE")
        logger.info("=" * 60)
        
        table_sql = """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
            expires_at TIMESTAMP NOT NULL DEFAULT NOW() + INTERVAL '1 hour',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used BOOLEAN DEFAULT FALSE,
            used_at TIMESTAMP NULL,
            ip_address INET, -- Track where reset was requested
            user_agent TEXT,
            tenant_id VARCHAR(50) REFERENCES tenants(id)
        );
        """
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens (token);",
            "CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens (user_id);",
            "CREATE INDEX IF NOT EXISTS idx_password_reset_expires ON password_reset_tokens (expires_at);",
            "CREATE INDEX IF NOT EXISTS idx_password_reset_tenant ON password_reset_tokens (tenant_id);",
            "CREATE INDEX IF NOT EXISTS idx_password_reset_ip ON password_reset_tokens (ip_address);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create table
                conn.execute(text(table_sql))
                logger.info("✅ Created password_reset_tokens table")
                success_count += 1
                
                # Create indexes
                for i, index_sql in enumerate(indexes_sql, 1):
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created index {i} for password_reset_tokens")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create index {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create password_reset_tokens table: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 PASSWORD_RESET_TOKENS TABLE SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_updated_at_triggers(self):
        """Create updated_at triggers for automatic timestamp updates"""
        logger.info("\n⏰ CREATING UPDATED_AT TRIGGERS")
        logger.info("=" * 60)
        
        # Function for automatic timestamp updates
        function_sql = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Apply trigger to users table
        trigger_sql = """
        DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
        CREATE TRIGGER trg_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create function
                conn.execute(text(function_sql))
                logger.info("✅ Created update_updated_at_column function")
                success_count += 1
                
                # Create trigger
                conn.execute(text(trigger_sql))
                logger.info("✅ Created updated_at trigger for users table")
                success_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create updated_at triggers: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 UPDATED_AT TRIGGERS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_rls_policies(self):
        """Create Row Level Security policies for Phase 1 tables"""
        logger.info("\n🔒 CREATING RLS POLICIES FOR PHASE 1 TABLES")
        logger.info("=" * 60)
        
        tables = [
            'login_attempts',
            'email_verification_tokens', 
            'password_reset_tokens'
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for table in tables:
                try:
                    # Enable RLS
                    conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
                    
                    # Create tenant isolation policy
                    policy_name = f"tenant_isolation_{table}"
                    
                    # Drop existing policy if it exists
                    conn.execute(text(f"DROP POLICY IF EXISTS {policy_name} ON {table}"))
                    
                    # Create new policy
                    conn.execute(text(f"""
                        CREATE POLICY {policy_name} ON {table}
                        USING (tenant_id = current_setting('my.tenant_id', true))
                    """))
                    
                    logger.info(f"✅ Created RLS policy for table '{table}'")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create RLS policy for table '{table}': {e}")
                    error_count += 1
                    conn.rollback()
            
            conn.commit()
        
        logger.info(f"\n📊 RLS POLICIES SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} policies")
        logger.info(f"   ❌ Errors: {error_count} policies")
        
        return success_count, error_count
    
    def create_audit_triggers(self):
        """Create audit triggers for Phase 1 tables"""
        logger.info("\n📝 CREATING AUDIT TRIGGERS FOR PHASE 1 TABLES")
        logger.info("=" * 60)
        
        tables = [
            'login_attempts',
            'email_verification_tokens',
            'password_reset_tokens'
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for table in tables:
                try:
                    # Drop existing trigger if it exists
                    conn.execute(text(f"DROP TRIGGER IF EXISTS audit_tenant_changes_{table} ON {table}"))
                    
                    # Create new trigger
                    conn.execute(text(f"""
                        CREATE TRIGGER audit_tenant_changes_{table}
                        AFTER INSERT OR UPDATE OR DELETE ON {table}
                        FOR EACH ROW EXECUTE FUNCTION audit_tenant_changes()
                    """))
                    
                    logger.info(f"✅ Created audit trigger for table '{table}'")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create audit trigger for table '{table}': {e}")
                    error_count += 1
                    conn.rollback()
            
            conn.commit()
        
        logger.info(f"\n📊 AUDIT TRIGGERS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} triggers")
        logger.info(f"   ❌ Errors: {error_count} triggers")
        
        return success_count, error_count
    
    def run_phase1_implementation(self):
        """Run the complete Phase 1 security implementation"""
        logger.info("🚀 EDONUOPS ERP - PHASE 1 SECURITY IMPLEMENTATION")
        logger.info("=" * 60)
        logger.info("🔐 Implementing enterprise-grade security tables")
        logger.info("📊 Tables: login_attempts, email_verification_tokens, password_reset_tokens")
        logger.info("🔒 Features: RLS policies, audit triggers, performance indexes")
        logger.info("=" * 60)
        
        if not self.connect_to_database():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Step 1: Create login_attempts table
            logger.info("\n📋 STEP 1: Creating login_attempts table")
            login_success, login_errors = self.create_login_attempts_table()
            
            # Step 2: Create email_verification_tokens table
            logger.info("\n📋 STEP 2: Creating email_verification_tokens table")
            email_success, email_errors = self.create_email_verification_table()
            
            # Step 3: Create password_reset_tokens table
            logger.info("\n📋 STEP 3: Creating password_reset_tokens table")
            password_success, password_errors = self.create_password_reset_table()
            
            # Step 4: Create updated_at triggers
            logger.info("\n📋 STEP 4: Creating updated_at triggers")
            trigger_success, trigger_errors = self.create_updated_at_triggers()
            
            # Step 5: Create RLS policies
            logger.info("\n📋 STEP 5: Creating RLS policies")
            rls_success, rls_errors = self.create_rls_policies()
            
            # Step 6: Create audit triggers
            logger.info("\n📋 STEP 6: Creating audit triggers")
            audit_success, audit_errors = self.create_audit_triggers()
            
            # Summary
            total_success = login_success + email_success + password_success + trigger_success + rls_success + audit_success
            total_errors = login_errors + email_errors + password_errors + trigger_errors + rls_errors + audit_errors
            
            logger.info("\n🎉 PHASE 1 SECURITY IMPLEMENTATION COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"✅ Total operations successful: {total_success}")
            logger.info(f"❌ Total errors: {total_errors}")
            
            if total_errors == 0:
                logger.info("\n🔒 YOUR ERP NOW HAS ENTERPRISE-GRADE SECURITY!")
                logger.info("📊 Phase 1 features implemented:")
                logger.info("   • login_attempts: Rate limiting and security monitoring")
                logger.info("   • email_verification_tokens: Secure email verification")
                logger.info("   • password_reset_tokens: Secure password recovery")
                logger.info("   • updated_at triggers: Automatic timestamp updates")
                logger.info("   • RLS policies: Tenant isolation for all security tables")
                logger.info("   • Audit triggers: Comprehensive security logging")
                
                logger.info("\n🎯 NEXT STEPS:")
                logger.info("   1. Implement backend API endpoints for security features")
                logger.info("   2. Add rate limiting logic to login endpoint")
                logger.info("   3. Implement email verification workflow")
                logger.info("   4. Add password reset functionality")
                logger.info("   5. Test all security features")
                
                return True
            else:
                logger.warning(f"\n⚠️  Implementation completed with {total_errors} errors")
                logger.warning("   Please review the errors above and fix them")
                return False
                
        except Exception as e:
            logger.error(f"❌ Implementation failed: {e}")
            return False

def main():
    """Main function to run Phase 1 security implementation"""
    implementer = Phase1SecurityImplementer()
    success = implementer.run_phase1_implementation()
    
    if success:
        print("\n🎉 Phase 1 security implementation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Phase 1 security implementation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
