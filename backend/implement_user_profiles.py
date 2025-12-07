#!/usr/bin/env python3
"""
👤 EDONUOPS ERP - COMPREHENSIVE USER PROFILE ENHANCEMENT
============================================================

Enhances users table with comprehensive profile fields for rich user data:
- Personal information (first_name, last_name, phone, etc.)
- Professional information (job_title, department, etc.)
- Company information (company_name, industry, etc.)
- Preferences and settings
- Onboarding progress tracking

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

class UserProfileEnhancer:
    def __init__(self):
        """Initialize the user profile enhancer"""
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
    
    def add_profile_fields_to_users(self):
        """Add comprehensive profile fields to users table"""
        logger.info("\n👤 ADDING PROFILE FIELDS TO USERS TABLE")
        logger.info("=" * 60)
        
        # Personal Information Fields
        personal_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS middle_name VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS mobile_number VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS date_of_birth DATE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture_url TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en';"
        ]
        
        # Professional Information Fields
        professional_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS job_title VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS manager_id INTEGER REFERENCES users(id);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS hire_date DATE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS employment_type VARCHAR(50);",  # full-time, part-time, contractor
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS work_location VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS skills TEXT[];",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS certifications TEXT[];",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_years INTEGER;"
        ]
        
        # Company Information Fields
        company_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_name VARCHAR(200);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_size VARCHAR(50);",  # small, medium, large, enterprise
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS industry VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_website VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_address TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_phone VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_email VARCHAR(255);"
        ]
        
        # Contact Information Fields
        contact_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS address_line1 VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS address_line2 VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS state VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS emergency_contact_relationship VARCHAR(50);"
        ]
        
        # Onboarding Progress Fields
        onboarding_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_step INTEGER DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_started_at TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed_at TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_completion_percentage INTEGER DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_profile_update TIMESTAMP;"
        ]
        
        # Preferences and Settings Fields
        preferences_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{}';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS dashboard_preferences JSONB DEFAULT '{}';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS privacy_settings JSONB DEFAULT '{}';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS theme_preference VARCHAR(20) DEFAULT 'light';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_frequency VARCHAR(20) DEFAULT 'daily';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS sms_notifications BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS marketing_emails BOOLEAN DEFAULT FALSE;"
        ]
        
        # Social and Professional Links
        social_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS linkedin_url VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS twitter_url VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS github_url VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS website_url VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS portfolio_url VARCHAR(255);"
        ]
        
        # Additional Metadata
        metadata_fields = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS source VARCHAR(50);",  # invite, self-registration, admin-created
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code VARCHAR(50);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by INTEGER REFERENCES users(id);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS session_duration_total INTEGER DEFAULT 0;"  # in minutes
        ]
        
        all_fields = (
            personal_fields + professional_fields + company_fields + 
            contact_fields + onboarding_fields + preferences_fields + 
            social_fields + metadata_fields
        )
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for i, field_sql in enumerate(all_fields, 1):
                try:
                    conn.execute(text(field_sql))
                    logger.info(f"✅ Added profile field {i}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to add profile field {i}: {e}")
                    error_count += 1
            
            conn.commit()
        
        logger.info(f"\n📊 PROFILE FIELDS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} fields")
        logger.info(f"   ❌ Errors: {error_count} fields")
        
        return success_count, error_count
    
    def create_profile_indexes(self):
        """Create indexes for profile fields for better performance"""
        logger.info("\n📊 CREATING PROFILE FIELD INDEXES")
        logger.info("=" * 60)
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_first_name ON users (first_name);",
            "CREATE INDEX IF NOT EXISTS idx_users_last_name ON users (last_name);",
            "CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users (phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_users_job_title ON users (job_title);",
            "CREATE INDEX IF NOT EXISTS idx_users_department ON users (department);",
            "CREATE INDEX IF NOT EXISTS idx_users_company_name ON users (company_name);",
            "CREATE INDEX IF NOT EXISTS idx_users_industry ON users (industry);",
            "CREATE INDEX IF NOT EXISTS idx_users_onboarding_completed ON users (onboarding_completed);",
            "CREATE INDEX IF NOT EXISTS idx_users_onboarding_step ON users (onboarding_step);",
            "CREATE INDEX IF NOT EXISTS idx_users_manager_id ON users (manager_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users (employee_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users (last_activity);",
            "CREATE INDEX IF NOT EXISTS idx_users_source ON users (source);",
            "CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users (referred_by);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            for i, index_sql in enumerate(indexes, 1):
                try:
                    conn.execute(text(index_sql))
                    logger.info(f"✅ Created profile index {i}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to create profile index {i}: {e}")
                    error_count += 1
            
            conn.commit()
        
        logger.info(f"\n📊 PROFILE INDEXES SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} indexes")
        logger.info(f"   ❌ Errors: {error_count} indexes")
        
        return success_count, error_count
    
    def create_onboarding_progress_table(self):
        """Create onboarding_progress table for tracking user onboarding steps"""
        logger.info("\n📋 CREATING ONBOARDING_PROGRESS TABLE")
        logger.info("=" * 60)
        
        table_sql = """
        CREATE TABLE IF NOT EXISTS onboarding_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            step_name VARCHAR(100) NOT NULL,
            step_order INTEGER NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP NULL,
            data JSONB DEFAULT '{}',
            skipped BOOLEAN DEFAULT FALSE,
            tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_onboarding_progress_user_id ON onboarding_progress (user_id);",
            "CREATE INDEX IF NOT EXISTS idx_onboarding_progress_step_name ON onboarding_progress (step_name);",
            "CREATE INDEX IF NOT EXISTS idx_onboarding_progress_completed ON onboarding_progress (completed);",
            "CREATE INDEX IF NOT EXISTS idx_onboarding_progress_tenant_id ON onboarding_progress (tenant_id);",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_onboarding_progress_user_step ON onboarding_progress (user_id, step_name);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create table
                conn.execute(text(table_sql))
                logger.info("✅ Created onboarding_progress table")
                success_count += 1
                
                # Create indexes
                for i, index_sql in enumerate(indexes_sql, 1):
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created onboarding index {i}")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create onboarding index {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create onboarding_progress table: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 ONBOARDING_PROGRESS TABLE SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_onboarding_steps_table(self):
        """Create onboarding_steps table for defining onboarding workflow"""
        logger.info("\n📋 CREATING ONBOARDING_STEPS TABLE")
        logger.info("=" * 60)
        
        table_sql = """
        CREATE TABLE IF NOT EXISTS onboarding_steps (
            id SERIAL PRIMARY KEY,
            step_name VARCHAR(100) NOT NULL UNIQUE,
            step_title VARCHAR(200) NOT NULL,
            step_description TEXT,
            step_order INTEGER NOT NULL,
            is_required BOOLEAN DEFAULT TRUE,
            is_skippable BOOLEAN DEFAULT FALSE,
            component_name VARCHAR(100),
            validation_rules JSONB DEFAULT '{}',
            tenant_specific BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Insert default onboarding steps
        default_steps_sql = """
        INSERT INTO onboarding_steps (step_name, step_title, step_description, step_order, is_required, is_skippable, component_name, validation_rules) VALUES
        ('professional_info', 'Professional Information', 'Your work details', 1, TRUE, FALSE, 'ProfessionalInfoStep', '{"job_title": "required", "department": "required"}'),
        ('company_info', 'Company Information', 'About your organization', 2, TRUE, FALSE, 'CompanyInfoStep', '{"company_name": "required", "industry": "required"}'),
        ('contact_info', 'Contact Information', 'How to reach you', 3, FALSE, TRUE, 'ContactInfoStep', '{"address_line1": "optional", "city": "optional"}'),
        ('preferences', 'Preferences & Settings', 'Customize your experience', 4, FALSE, TRUE, 'PreferencesStep', '{"theme_preference": "optional", "notification_preferences": "optional"}'),
        ('social_links', 'Social & Professional Links', 'Connect your profiles', 5, FALSE, TRUE, 'SocialLinksStep', '{"linkedin_url": "optional", "github_url": "optional"}'),
        ('emergency_contact', 'Emergency Contact', 'Emergency contact information', 6, FALSE, TRUE, 'EmergencyContactStep', '{"emergency_contact_name": "optional", "emergency_contact_phone": "optional"}'),
        ('review_profile', 'Review & Complete', 'Review your information', 7, TRUE, FALSE, 'ReviewProfileStep', '{}')
        ON CONFLICT (step_name) DO NOTHING;
        """
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_onboarding_steps_step_order ON onboarding_steps (step_order);",
            "CREATE INDEX IF NOT EXISTS idx_onboarding_steps_is_required ON onboarding_steps (is_required);",
            "CREATE INDEX IF NOT EXISTS idx_onboarding_steps_tenant_specific ON onboarding_steps (tenant_specific);"
        ]
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            try:
                # Create table
                conn.execute(text(table_sql))
                logger.info("✅ Created onboarding_steps table")
                success_count += 1
                
                # Insert default steps
                conn.execute(text(default_steps_sql))
                logger.info("✅ Inserted default onboarding steps")
                success_count += 1
                
                # Create indexes
                for i, index_sql in enumerate(indexes_sql, 1):
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created onboarding steps index {i}")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create onboarding steps index {i}: {e}")
                        error_count += 1
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Failed to create onboarding_steps table: {e}")
                error_count += 1
                conn.rollback()
        
        logger.info(f"\n📊 ONBOARDING_STEPS TABLE SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} operations")
        logger.info(f"   ❌ Errors: {error_count} operations")
        
        return success_count, error_count
    
    def create_onboarding_functions(self):
        """Create functions for onboarding management"""
        logger.info("\n🔧 CREATING ONBOARDING MANAGEMENT FUNCTIONS")
        logger.info("=" * 60)
        
        # Function to calculate profile completion percentage
        profile_completion_function = """
        CREATE OR REPLACE FUNCTION calculate_profile_completion(p_user_id INTEGER)
        RETURNS INTEGER AS $$
        DECLARE
            total_fields INTEGER := 0;
            completed_fields INTEGER := 0;
            completion_percentage INTEGER;
        BEGIN
            -- Count total profile fields
            SELECT COUNT(*) INTO total_fields
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN (
                'first_name', 'last_name', 'phone_number', 'job_title', 
                'department', 'company_name', 'industry', 'address_line1', 
                'city', 'state', 'country', 'linkedin_url', 'bio'
            );
            
            -- Count completed fields (non-null and non-empty)
            SELECT COUNT(*) INTO completed_fields
            FROM users 
            WHERE id = p_user_id
            AND (
                (first_name IS NOT NULL AND first_name != '') OR
                (last_name IS NOT NULL AND last_name != '') OR
                (phone_number IS NOT NULL AND phone_number != '') OR
                (job_title IS NOT NULL AND job_title != '') OR
                (department IS NOT NULL AND department != '') OR
                (company_name IS NOT NULL AND company_name != '') OR
                (industry IS NOT NULL AND industry != '') OR
                (address_line1 IS NOT NULL AND address_line1 != '') OR
                (city IS NOT NULL AND city != '') OR
                (state IS NOT NULL AND state != '') OR
                (country IS NOT NULL AND country != '') OR
                (linkedin_url IS NOT NULL AND linkedin_url != '') OR
                (bio IS NOT NULL AND bio != '')
            );
            
            -- Calculate percentage
            IF total_fields > 0 THEN
                completion_percentage := (completed_fields * 100) / total_fields;
            ELSE
                completion_percentage := 0;
            END IF;
            
            -- Update user's profile completion percentage
            UPDATE users 
            SET profile_completion_percentage = completion_percentage,
                last_profile_update = NOW()
            WHERE id = p_user_id;
            
            RETURN completion_percentage;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Function to get onboarding progress
        onboarding_progress_function = """
        CREATE OR REPLACE FUNCTION get_onboarding_progress(p_user_id INTEGER)
        RETURNS TABLE(
            step_name VARCHAR(100),
            step_title VARCHAR(200),
            step_description TEXT,
            step_order INTEGER,
            is_required BOOLEAN,
            is_skippable BOOLEAN,
            completed BOOLEAN,
            completed_at TIMESTAMP,
            skipped BOOLEAN,
            data JSONB
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                os.step_name,
                os.step_title,
                os.step_description,
                os.step_order,
                os.is_required,
                os.is_skippable,
                COALESCE(op.completed, FALSE) as completed,
                op.completed_at,
                COALESCE(op.skipped, FALSE) as skipped,
                COALESCE(op.data, '{}') as data
            FROM onboarding_steps os
            LEFT JOIN onboarding_progress op ON os.step_name = op.step_name AND op.user_id = p_user_id
            ORDER BY os.step_order;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Function to complete onboarding step
        complete_step_function = """
        CREATE OR REPLACE FUNCTION complete_onboarding_step(
            p_user_id INTEGER,
            p_step_name VARCHAR(100),
            p_data JSONB DEFAULT '{}',
            p_skipped BOOLEAN DEFAULT FALSE
        )
        RETURNS BOOLEAN AS $$
        DECLARE
            step_exists BOOLEAN;
            tenant_id VARCHAR(50);
        BEGIN
            -- Get user's tenant_id
            SELECT u.tenant_id INTO tenant_id
            FROM users u
            WHERE u.id = p_user_id;
            
            IF tenant_id IS NULL THEN
                RETURN FALSE;
            END IF;
            
            -- Check if step exists
            SELECT EXISTS(
                SELECT 1 FROM onboarding_steps 
                WHERE step_name = p_step_name
            ) INTO step_exists;
            
            IF NOT step_exists THEN
                RETURN FALSE;
            END IF;
            
            -- Insert or update onboarding progress
            INSERT INTO onboarding_progress (
                user_id, step_name, completed, completed_at, 
                data, skipped, tenant_id
            ) VALUES (
                p_user_id, p_step_name, NOT p_skipped, 
                CASE WHEN NOT p_skipped THEN NOW() ELSE NULL END,
                p_data, p_skipped, tenant_id
            )
            ON CONFLICT (user_id, step_name) 
            DO UPDATE SET
                completed = NOT p_skipped,
                completed_at = CASE WHEN NOT p_skipped THEN NOW() ELSE NULL END,
                data = p_data,
                skipped = p_skipped,
                updated_at = NOW();
            
            -- Update user's onboarding step
            UPDATE users 
            SET onboarding_step = (
                SELECT step_order FROM onboarding_steps 
                WHERE step_name = p_step_name
            ),
            onboarding_started_at = COALESCE(onboarding_started_at, NOW())
            WHERE id = p_user_id;
            
            RETURN TRUE;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        success_count = 0
        error_count = 0
        
        with self.engine.connect() as conn:
            functions = [
                ("calculate_profile_completion", profile_completion_function),
                ("get_onboarding_progress", onboarding_progress_function),
                ("complete_onboarding_step", complete_step_function)
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
        
        logger.info(f"\n📊 ONBOARDING FUNCTIONS SUMMARY:")
        logger.info(f"   ✅ Successfully processed: {success_count} functions")
        logger.info(f"   ❌ Errors: {error_count} functions")
        
        return success_count, error_count
    
    def run_implementation(self):
        """Run the complete user profile enhancement"""
        logger.info("👤 EDONUOPS ERP - COMPREHENSIVE USER PROFILE ENHANCEMENT")
        logger.info("=" * 60)
        logger.info("📊 Implementing rich user data collection")
        logger.info("🔧 Features: Profile fields, progressive onboarding, tenant-specific flows")
        logger.info("⚡ Performance: Optimized indexes, completion tracking")
        logger.info("=" * 60)
        
        if not self.connect_to_database():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Step 1: Add profile fields to users table
            logger.info("\n📋 STEP 1: Adding profile fields to users table")
            fields_success, fields_errors = self.add_profile_fields_to_users()
            
            # Step 2: Create profile indexes
            logger.info("\n📋 STEP 2: Creating profile field indexes")
            indexes_success, indexes_errors = self.create_profile_indexes()
            
            # Step 3: Create onboarding progress table
            logger.info("\n📋 STEP 3: Creating onboarding progress table")
            progress_success, progress_errors = self.create_onboarding_progress_table()
            
            # Step 4: Create onboarding steps table
            logger.info("\n📋 STEP 4: Creating onboarding steps table")
            steps_success, steps_errors = self.create_onboarding_steps_table()
            
            # Step 5: Create onboarding functions
            logger.info("\n📋 STEP 5: Creating onboarding management functions")
            func_success, func_errors = self.create_onboarding_functions()
            
            # Summary
            total_success = fields_success + indexes_success + progress_success + steps_success + func_success
            total_errors = fields_errors + indexes_errors + progress_errors + steps_errors + func_errors
            
            logger.info("\n🎉 USER PROFILE ENHANCEMENT COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"✅ Total operations successful: {total_success}")
            logger.info(f"❌ Total errors: {total_errors}")
            
            if total_errors == 0:
                logger.info("\n👤 YOUR ERP NOW HAS COMPREHENSIVE USER PROFILES!")
                logger.info("📊 User profile features implemented:")
                logger.info("   • 50+ profile fields for rich user data")
                logger.info("   • Progressive onboarding system with 8 steps")
                logger.info("   • Profile completion percentage tracking")
                logger.info("   • Tenant-specific onboarding flows")
                logger.info("   • Onboarding progress management")
                logger.info("   • Performance-optimized indexes")
                
                logger.info("\n🎯 NEXT STEPS:")
                logger.info("   1. Create onboarding API endpoints")
                logger.info("   2. Implement frontend onboarding components")
                logger.info("   3. Add validation for profile fields")
                logger.info("   4. Test progressive onboarding flow")
                
                return True
            else:
                logger.warning(f"\n⚠️  Implementation completed with {total_errors} errors")
                logger.warning("   Please review the errors above and fix them")
                return False
                
        except Exception as e:
            logger.error(f"❌ Implementation failed: {e}")
            return False

def main():
    """Main function to run user profile enhancement"""
    enhancer = UserProfileEnhancer()
    success = enhancer.run_implementation()
    
    if success:
        print("\n🎉 User profile enhancement completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ User profile enhancement failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

