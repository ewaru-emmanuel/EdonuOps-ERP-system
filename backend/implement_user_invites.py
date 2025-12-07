#!/usr/bin/env python3
"""
🏢 EDONUOPS ERP - USER INVITES TABLE IMPLEMENTATION
============================================================

Creates user_invites table for secure tenant invitation system:
- Secure token-based invitations
- Role assignment per invitation
- Expiration and usage tracking
- Tenant isolation with RLS

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

class UserInvitesImplementer:
    def __init__(self):
        """Initialize the user invites implementer"""
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
    
    def create_user_invites_table(self):
        """Create user_invites table for secure tenant invitation system"""
        logger.info("\n🏢 CREATING USER_INVITES TABLE")
        logger.info("=" * 60)
        
        table_sql = """
        CREATE TABLE IF NOT EXISTS user_invites (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
            invited_by INTEGER NOT NULL REFERENCES users(id),
            email VARCHAR(255) NOT NULL,
            role_id INTEGER REFERENCES roles(id),
            token VARCHAR(255) NOT NULL UNIQUE DEFAULT gen_random_uuid()::text,
            expires_at TIMESTAMP NOT NULL DEFAULT NOW() + INTERVAL '7 days',
            used BOOLEAN DEFAULT FALSE,
            used_at TIMESTAMP NULL,
            used_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT,
            invitation_type VARCHAR(50) DEFAULT 'user' -- 'user', 'admin', 'superadmin'
        );
        """
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_user_invites_token ON user_invites (token);",
            "CREATE INDEX IF NOT EXISTS idx_user_invites_email ON user_invites (email);",
            "CREATE INDEX IF NOT EXISTS idx_user_invites_tenant ON user_invites (tenant_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_invites_expires ON user_invites (expires_at);",
            "CREATE INDEX IF NOT EXISTS idx_user_invites_used ON user_invites (used);",
            "CREATE INDEX IF NOT EXISTS idx_user_invites_invited_by ON user_invites (invited_by);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create table
                conn.execute(text(table_sql))
                logger.info("✅ Created user_invites table")
                success_count += 1
                
                # Create indexes
                for i, index_sql in enumerate(indexes_sql, 1):
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created index {i} for user_invites")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create index {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create user_invites table: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 USER_INVITES TABLE SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_rls_policies(self):
        """Create RLS policies for user_invites table"""
        logger.info("\n🔒 CREATING RLS POLICIES FOR USER_INVITES")
        logger.info("=" * 60)
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Enable RLS
                conn.execute(text("ALTER TABLE user_invites ENABLE ROW LEVEL SECURITY"))
                
                # Create tenant isolation policy
                policy_name = "tenant_isolation_user_invites"
                
                # Drop existing policy if it exists
                conn.execute(text(f"DROP POLICY IF EXISTS {policy_name} ON user_invites"))
                
                # Create new policy
                conn.execute(text(f"""
                    CREATE POLICY {policy_name} ON user_invites
                    USING (tenant_id = current_setting('my.tenant_id', true))
                """))
                
                logger.info("✅ Created RLS policy for user_invites table")
                success_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create RLS policy for user_invites: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 RLS POLICIES SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} policies")
        logger.info(f"   ❌ Errors: {error_count} policies")
        
        return success_count, error_count
    
    def create_audit_triggers(self):
        """Create audit triggers for user_invites table"""
        logger.info("\n📝 CREATING AUDIT TRIGGERS FOR USER_INVITES")
        logger.info("=" * 60)
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Drop existing trigger if it exists
                conn.execute(text("DROP TRIGGER IF EXISTS audit_tenant_changes_user_invites ON user_invites"))
                
                # Create new trigger
                conn.execute(text("""
                    CREATE TRIGGER audit_tenant_changes_user_invites
                    AFTER INSERT OR UPDATE OR DELETE ON user_invites
                    FOR EACH ROW EXECUTE FUNCTION audit_tenant_changes()
                """))
                
                logger.info("✅ Created audit trigger for user_invites table")
                success_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create audit trigger for user_invites: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 AUDIT TRIGGERS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} triggers")
        logger.info(f"   ❌ Errors: {error_count} triggers")
        
        return success_count, error_count
    
    def create_invite_management_functions(self):
        """Create functions for invite management"""
        logger.info("\n🔧 CREATING INVITE MANAGEMENT FUNCTIONS")
        logger.info("=" * 60)
        
        # Function to create invite
        create_invite_function = """
        CREATE OR REPLACE FUNCTION create_user_invite(
            p_tenant_id VARCHAR(50),
            p_invited_by INTEGER,
            p_email VARCHAR(255),
            p_role_id INTEGER DEFAULT NULL,
            p_message TEXT DEFAULT NULL,
            p_expires_days INTEGER DEFAULT 7
        )
        RETURNS VARCHAR(255) AS $$
        DECLARE
            invite_token VARCHAR(255);
        BEGIN
            -- Generate secure token
            invite_token := encode(gen_random_bytes(32), 'base64');
            
            -- Create invite
            INSERT INTO user_invites (
                tenant_id, invited_by, email, role_id, token, 
                expires_at, message, invitation_type
            ) VALUES (
                p_tenant_id, p_invited_by, p_email, p_role_id, invite_token,
                NOW() + (p_expires_days || ' days')::INTERVAL, p_message, 'user'
            );
            
            RETURN invite_token;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Function to validate invite
        validate_invite_function = """
        CREATE OR REPLACE FUNCTION validate_user_invite(p_token VARCHAR(255))
        RETURNS TABLE(
            tenant_id VARCHAR(50),
            email VARCHAR(255),
            role_id INTEGER,
            expires_at TIMESTAMP,
            valid BOOLEAN
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                ui.tenant_id,
                ui.email,
                ui.role_id,
                ui.expires_at,
                (ui.expires_at > NOW() AND ui.used = FALSE) as valid
            FROM user_invites ui
            WHERE ui.token = p_token;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Function to cleanup expired invites
        cleanup_invites_function = """
        CREATE OR REPLACE FUNCTION cleanup_expired_invites()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM user_invites 
            WHERE expires_at < NOW() AND used = FALSE;
            
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            functions = [
                ("create_user_invite", create_invite_function),
                ("validate_user_invite", validate_invite_function),
                ("cleanup_expired_invites", cleanup_invites_function)
            ]
            
            for func_name, func_sql in functions:
                try:
                    conn.execute(text(func_sql))
                    logger.info(f"✅ Created {func_name} function")
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to create {func_name} function: {e}")
                    error_count += 1
            
            conn.commit()
        
        logger.info(f"\n📊 INVITE MANAGEMENT FUNCTIONS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} functions")
        logger.info(f"   ❌ Errors: {error_count} functions")
        
        return success_count, error_count
    
    def run_implementation(self):
        """Run the complete user invites implementation"""
        logger.info("🏢 EDONUOPS ERP - USER INVITES IMPLEMENTATION")
        logger.info("=" * 60)
        logger.info("🔐 Implementing secure tenant invitation system")
        logger.info("📊 Features: Token-based invites, role assignment, expiration tracking")
        logger.info("🔒 Security: RLS policies, audit triggers, tenant isolation")
        logger.info("=" * 60)
        
        if not self.connect_to_database():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Step 1: Create user_invites table
            logger.info("\n📋 STEP 1: Creating user_invites table")
            table_success, table_errors = self.create_user_invites_table()
            
            # Step 2: Create RLS policies
            logger.info("\n📋 STEP 2: Creating RLS policies")
            rls_success, rls_errors = self.create_rls_policies()
            
            # Step 3: Create audit triggers
            logger.info("\n📋 STEP 3: Creating audit triggers")
            audit_success, audit_errors = self.create_audit_triggers()
            
            # Step 4: Create invite management functions
            logger.info("\n📋 STEP 4: Creating invite management functions")
            func_success, func_errors = self.create_invite_management_functions()
            
            # Summary
            total_success = table_success + rls_success + audit_success + func_success
            total_errors = table_errors + rls_errors + audit_errors + func_errors
            
            logger.info("\n🎉 USER INVITES IMPLEMENTATION COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"✅ Total operations successful: {total_success}")
            logger.info(f"❌ Total errors: {total_errors}")
            
            if total_errors == 0:
                logger.info("\n🏢 YOUR ERP NOW HAS SECURE TENANT INVITATION SYSTEM!")
                logger.info("📊 User invites features implemented:")
                logger.info("   • user_invites table with secure token-based invitations")
                logger.info("   • Role assignment per invitation")
                logger.info("   • Expiration and usage tracking")
                logger.info("   • RLS policies for tenant isolation")
                logger.info("   • Audit triggers for compliance")
                logger.info("   • Management functions for invite operations")
                
                logger.info("\n🎯 NEXT STEPS:")
                logger.info("   1. Integrate user_invites with enhanced authentication API")
                logger.info("   2. Create invite management endpoints")
                logger.info("   3. Implement invite UI in frontend")
                logger.info("   4. Test invitation flow end-to-end")
                
                return True
            else:
                logger.warning(f"\n⚠️  Implementation completed with {total_errors} errors")
                logger.warning("   Please review the errors above and fix them")
                return False
                
        except Exception as e:
            logger.error(f"❌ Implementation failed: {e}")
            return False

def main():
    """Main function to run user invites implementation"""
    implementer = UserInvitesImplementer()
    success = implementer.run_implementation()
    
    if success:
        print("\n🎉 User invites implementation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ User invites implementation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
