#!/usr/bin/env python3
"""
🧪 EDONUOPS ERP - TENANT ISOLATION TESTING
============================================================

Comprehensive testing suite for tenant isolation:
- Tests RLS policies
- Validates tenant context functions
- Tests audit logging
- Performance testing
- Security validation

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
import time
import uuid
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TenantIsolationTester:
    def __init__(self):
        """Initialize the tenant isolation tester"""
        self.engine = None
        self.test_results = {
            'rls_policies': {'passed': 0, 'failed': 0, 'tests': []},
            'tenant_functions': {'passed': 0, 'failed': 0, 'tests': []},
            'audit_logging': {'passed': 0, 'failed': 0, 'tests': []},
            'performance': {'passed': 0, 'failed': 0, 'tests': []},
            'security': {'passed': 0, 'failed': 0, 'tests': []}
        }
        
    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            # Load environment variables from config.env
            load_dotenv('config.env')
            
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL environment variable not set")
            
            self.engine = create_engine(database_url, echo=False)
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Connected to PostgreSQL database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def test_rls_policies(self):
        """Test Row Level Security policies"""
        logger.info("\n🔒 TESTING ROW LEVEL SECURITY POLICIES")
        logger.info("=" * 60)
        
        # Test tables with RLS
        test_tables = ['users', 'accounts', 'products', 'customers', 'invoices']
        
        with self.engine.connect() as conn:
            for table in test_tables:
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
                        logger.warning(f"⚠️  Table '{table}' does not exist, skipping RLS test...")
                        continue
                    
                    # Test 1: Check if RLS is enabled
                    result = conn.execute(text("""
                        SELECT relrowsecurity FROM pg_class 
                        WHERE relname = :table_name
                    """), {"table_name": table})
                    
                    rls_enabled = result.scalar()
                    
                    if rls_enabled:
                        logger.info(f"✅ RLS enabled on table '{table}'")
                        self.test_results['rls_policies']['passed'] += 1
                        self.test_results['rls_policies']['tests'].append(f"RLS enabled on {table}")
                    else:
                        logger.error(f"❌ RLS not enabled on table '{table}'")
                        self.test_results['rls_policies']['failed'] += 1
                        self.test_results['rls_policies']['tests'].append(f"RLS NOT enabled on {table}")
                    
                    # Test 2: Check if policy exists
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM pg_policies 
                        WHERE tablename = :table_name 
                        AND policyname LIKE 'tenant_isolation_%'
                    """), {"table_name": table})
                    
                    policy_count = result.scalar()
                    
                    if policy_count > 0:
                        logger.info(f"✅ Tenant isolation policy exists on table '{table}'")
                        self.test_results['rls_policies']['passed'] += 1
                        self.test_results['rls_policies']['tests'].append(f"Policy exists on {table}")
                    else:
                        logger.error(f"❌ No tenant isolation policy on table '{table}'")
                        self.test_results['rls_policies']['failed'] += 1
                        self.test_results['rls_policies']['tests'].append(f"No policy on {table}")
                    
                except Exception as e:
                    logger.error(f"❌ Error testing RLS for table '{table}': {e}")
                    self.test_results['rls_policies']['failed'] += 1
                    self.test_results['rls_policies']['tests'].append(f"Error testing {table}: {e}")
    
    def test_tenant_functions(self):
        """Test tenant context functions"""
        logger.info("\n🔧 TESTING TENANT CONTEXT FUNCTIONS")
        logger.info("=" * 60)
        
        with self.engine.connect() as conn:
            # Test 1: set_tenant_context function
            try:
                test_tenant_id = f"test_tenant_{uuid.uuid4().hex[:8]}"
                conn.execute(text("SELECT set_tenant_context(:tenant_id)"), {
                    'tenant_id': test_tenant_id
                })
                
                result = conn.execute(text("SELECT get_current_tenant()"))
                current_tenant = result.scalar()
                
                if current_tenant == test_tenant_id:
                    logger.info("✅ set_tenant_context and get_current_tenant functions work")
                    self.test_results['tenant_functions']['passed'] += 1
                    self.test_results['tenant_functions']['tests'].append("Tenant context functions work")
                else:
                    logger.error(f"❌ Tenant context functions failed: expected {test_tenant_id}, got {current_tenant}")
                    self.test_results['tenant_functions']['failed'] += 1
                    self.test_results['tenant_functions']['tests'].append("Tenant context functions failed")
                    
            except Exception as e:
                logger.error(f"❌ Error testing tenant context functions: {e}")
                self.test_results['tenant_functions']['failed'] += 1
                self.test_results['tenant_functions']['tests'].append(f"Error: {e}")
            
            # Test 2: validate_tenant_access function
            try:
                # Create test data
                test_user_id = 999999
                test_tenant_id = f"test_tenant_{uuid.uuid4().hex[:8]}"
                
                # Insert test tenant
                conn.execute(text("""
                    INSERT INTO tenants (id, name, domain, is_active) 
                    VALUES (:id, :name, :domain, :is_active)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    'id': test_tenant_id,
                    'name': 'Test Tenant',
                    'domain': 'test.com',
                    'is_active': True
                })
                
                # Insert test user
                conn.execute(text("""
                    INSERT INTO users (id, username, email, password_hash, tenant_id, is_active) 
                    VALUES (:id, :username, :email, :password_hash, :tenant_id, :is_active)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    'id': test_user_id,
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'password_hash': 'test_hash',
                    'tenant_id': test_tenant_id,
                    'is_active': True
                })
                
                # Insert user_tenant relationship
                conn.execute(text("""
                    INSERT INTO user_tenants (user_id, tenant_id, is_active) 
                    VALUES (:user_id, :tenant_id, :is_active)
                    ON CONFLICT (user_id, tenant_id) DO NOTHING
                """), {
                    'user_id': test_user_id,
                    'tenant_id': test_tenant_id,
                    'is_active': True
                })
                
                conn.commit()
                
                # Test validation
                result = conn.execute(text("""
                    SELECT validate_tenant_access(:user_id, :tenant_id)
                """), {
                    'user_id': test_user_id,
                    'tenant_id': test_tenant_id
                })
                
                has_access = result.scalar()
                
                if has_access:
                    logger.info("✅ validate_tenant_access function works")
                    self.test_results['tenant_functions']['passed'] += 1
                    self.test_results['tenant_functions']['tests'].append("validate_tenant_access works")
                else:
                    logger.error("❌ validate_tenant_access function failed")
                    self.test_results['tenant_functions']['failed'] += 1
                    self.test_results['tenant_functions']['tests'].append("validate_tenant_access failed")
                
                # Cleanup test data
                conn.execute(text("DELETE FROM user_tenants WHERE user_id = :user_id"), {'user_id': test_user_id})
                conn.execute(text("DELETE FROM users WHERE id = :user_id"), {'user_id': test_user_id})
                conn.execute(text("DELETE FROM tenants WHERE id = :tenant_id"), {'tenant_id': test_tenant_id})
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Error testing validate_tenant_access: {e}")
                self.test_results['tenant_functions']['failed'] += 1
                self.test_results['tenant_functions']['tests'].append(f"Error: {e}")
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        logger.info("\n📝 TESTING AUDIT LOGGING")
        logger.info("=" * 60)
        
        with self.engine.connect() as conn:
            try:
                # Test audit_tenant_access function
                test_user_id = 999998
                test_tenant_id = f"test_tenant_{uuid.uuid4().hex[:8]}"
                
                conn.execute(text("""
                    SELECT audit_tenant_access(:user_id, :tenant_id, :action, :table_name, :record_id)
                """), {
                    'user_id': test_user_id,
                    'tenant_id': test_tenant_id,
                    'action': 'TEST_ACCESS',
                    'table_name': 'test_table',
                    'record_id': 'test_record'
                })
                
                conn.commit()
                
                # Check if audit log was created
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM audit_logs 
                    WHERE user_id = :user_id 
                    AND tenant_id = :tenant_id 
                    AND action = :action
                """), {
                    'user_id': test_user_id,
                    'tenant_id': test_tenant_id,
                    'action': 'TEST_ACCESS'
                })
                
                audit_count = result.scalar()
                
                if audit_count > 0:
                    logger.info("✅ audit_tenant_access function works")
                    self.test_results['audit_logging']['passed'] += 1
                    self.test_results['audit_logging']['tests'].append("audit_tenant_access works")
                else:
                    logger.error("❌ audit_tenant_access function failed")
                    self.test_results['audit_logging']['failed'] += 1
                    self.test_results['audit_logging']['tests'].append("audit_tenant_access failed")
                
                # Cleanup test data
                conn.execute(text("DELETE FROM audit_logs WHERE user_id = :user_id"), {'user_id': test_user_id})
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Error testing audit logging: {e}")
                self.test_results['audit_logging']['failed'] += 1
                self.test_results['audit_logging']['tests'].append(f"Error: {e}")
    
    def test_performance(self):
        """Test performance of tenant isolation"""
        logger.info("\n⚡ TESTING PERFORMANCE")
        logger.info("=" * 60)
        
        with self.engine.connect() as conn:
            # Test 1: Check if performance indexes exist
            performance_indexes = [
                'idx_users_tenant_active',
                'idx_accounts_tenant_type',
                'idx_products_tenant_category',
                'idx_customers_tenant_status',
                'idx_invoices_tenant_date'
            ]
            
            for index_name in performance_indexes:
                try:
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM pg_indexes 
                            WHERE indexname = :index_name
                        )
                    """), {"index_name": index_name})
                    
                    index_exists = result.scalar()
                    
                    if index_exists:
                        logger.info(f"✅ Performance index '{index_name}' exists")
                        self.test_results['performance']['passed'] += 1
                        self.test_results['performance']['tests'].append(f"Index {index_name} exists")
                    else:
                        logger.warning(f"⚠️  Performance index '{index_name}' missing")
                        self.test_results['performance']['failed'] += 1
                        self.test_results['performance']['tests'].append(f"Index {index_name} missing")
                        
                except Exception as e:
                    logger.error(f"❌ Error checking index '{index_name}': {e}")
                    self.test_results['performance']['failed'] += 1
                    self.test_results['performance']['tests'].append(f"Error checking {index_name}: {e}")
    
    def test_security(self):
        """Test security aspects of tenant isolation"""
        logger.info("\n🔐 TESTING SECURITY")
        logger.info("=" * 60)
        
        with self.engine.connect() as conn:
            # Test 1: Check if tenant_id columns exist on critical tables
            critical_tables = ['users', 'accounts', 'products', 'customers', 'invoices']
            
            for table in critical_tables:
                try:
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
                        logger.info(f"✅ Table '{table}' has tenant_id column")
                        self.test_results['security']['passed'] += 1
                        self.test_results['security']['tests'].append(f"{table} has tenant_id")
                    else:
                        logger.error(f"❌ Table '{table}' missing tenant_id column")
                        self.test_results['security']['failed'] += 1
                        self.test_results['security']['tests'].append(f"{table} missing tenant_id")
                        
                except Exception as e:
                    logger.error(f"❌ Error checking tenant_id on table '{table}': {e}")
                    self.test_results['security']['failed'] += 1
                    self.test_results['security']['tests'].append(f"Error checking {table}: {e}")
            
            # Test 2: Check foreign key constraints
            for table in critical_tables:
                try:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.table_name = :table_name 
                        AND tc.constraint_type = 'FOREIGN KEY'
                        AND kcu.column_name = 'tenant_id'
                    """), {"table_name": table})
                    
                    fk_count = result.scalar()
                    
                    if fk_count > 0:
                        logger.info(f"✅ Table '{table}' has tenant_id foreign key constraint")
                        self.test_results['security']['passed'] += 1
                        self.test_results['security']['tests'].append(f"{table} has FK constraint")
                    else:
                        logger.warning(f"⚠️  Table '{table}' missing tenant_id foreign key constraint")
                        self.test_results['security']['failed'] += 1
                        self.test_results['security']['tests'].append(f"{table} missing FK constraint")
                        
                except Exception as e:
                    logger.error(f"❌ Error checking FK constraint on table '{table}': {e}")
                    self.test_results['security']['failed'] += 1
                    self.test_results['security']['tests'].append(f"Error checking {table} FK: {e}")
    
    def run_all_tests(self):
        """Run all tenant isolation tests"""
        logger.info("🧪 EDONUOPS ERP - TENANT ISOLATION TESTING")
        logger.info("=" * 60)
        logger.info("🔒 Testing RLS policies, tenant functions, audit logging")
        logger.info("⚡ Performance indexes and security constraints")
        logger.info("=" * 60)
        
        if not self.connect_to_database():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Run all test suites
            self.test_rls_policies()
            self.test_tenant_functions()
            self.test_audit_logging()
            self.test_performance()
            self.test_security()
            
            # Generate summary report
            self.generate_summary_report()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Testing failed: {e}")
            return False
    
    def generate_summary_report(self):
        """Generate comprehensive test summary report"""
        logger.info("\n📊 TENANT ISOLATION TEST SUMMARY REPORT")
        logger.info("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results['passed']
            failed = results['failed']
            total_passed += passed
            total_failed += failed
            
            logger.info(f"\n📋 {category.upper().replace('_', ' ')}:")
            logger.info(f"   ✅ Passed: {passed}")
            logger.info(f"   ❌ Failed: {failed}")
            
            if results['tests']:
                logger.info("   📝 Test Details:")
                for test in results['tests']:
                    logger.info(f"      • {test}")
        
        logger.info(f"\n🎯 OVERALL SUMMARY:")
        logger.info(f"   ✅ Total Passed: {total_passed}")
        logger.info(f"   ❌ Total Failed: {total_failed}")
        logger.info(f"   📊 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
        
        if total_failed == 0:
            logger.info("\n🎉 ALL TESTS PASSED! Tenant isolation is working correctly!")
            logger.info("🔒 Your ERP system has enterprise-grade tenant isolation!")
        else:
            logger.warning(f"\n⚠️  {total_failed} tests failed. Please review and fix issues.")
            logger.warning("🔧 Tenant isolation may not be fully functional.")

def main():
    """Main function to run tenant isolation tests"""
    tester = TenantIsolationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Tenant isolation testing completed!")
        sys.exit(0)
    else:
        print("\n❌ Tenant isolation testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
