#!/usr/bin/env python3
"""
🔄 EDONUOPS ERP - UPDATE ONBOARDING SYSTEM
============================================================

Updates the onboarding system to remove fields now collected during registration:
- Removes first_name, last_name, phone_number from onboarding steps
- Updates step order and validation rules
- Ensures no data overlap between registration and onboarding

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

class OnboardingUpdater:
    def __init__(self):
        """Initialize the onboarding updater"""
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
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def update_onboarding_steps(self):
        """Update onboarding steps to remove registration fields"""
        logger.info("\n🔄 UPDATING ONBOARDING STEPS")
        logger.info("=" * 60)
        
        try:
            with self.engine.connect() as conn:
                # Remove the personal_info step since those fields are now in registration
                conn.execute(text("""
                    DELETE FROM onboarding_steps 
                    WHERE step_name = 'personal_info'
                """))
                logger.info("✅ Removed personal_info step from onboarding")
                
                # Update step order for remaining steps
                update_steps_sql = """
                UPDATE onboarding_steps SET step_order = CASE
                    WHEN step_name = 'professional_info' THEN 1
                    WHEN step_name = 'company_info' THEN 2
                    WHEN step_name = 'contact_info' THEN 3
                    WHEN step_name = 'preferences' THEN 4
                    WHEN step_name = 'social_links' THEN 5
                    WHEN step_name = 'emergency_contact' THEN 6
                    WHEN step_name = 'review_profile' THEN 7
                END
                WHERE step_name IN ('professional_info', 'company_info', 'contact_info', 
                                  'preferences', 'social_links', 'emergency_contact', 'review_profile')
                """
                
                conn.execute(text(update_steps_sql))
                logger.info("✅ Updated step order for remaining onboarding steps")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to update onboarding steps: {e}")
            return False
    
    def verify_onboarding_steps(self):
        """Verify the updated onboarding steps"""
        logger.info("\n📊 VERIFYING ONBOARDING STEPS")
        logger.info("=" * 60)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT step_name, step_title, step_order, is_required
                    FROM onboarding_steps
                    ORDER BY step_order
                """))
                
                steps = result.fetchall()
                
                logger.info("Current onboarding steps:")
                for step in steps:
                    required = "Required" if step.is_required else "Optional"
                    logger.info(f"  {step.step_order}. {step.step_name} - {step.step_title} ({required})")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to verify onboarding steps: {e}")
            return False
    
    def update_onboarding_progress(self):
        """Update existing user onboarding progress"""
        logger.info("\n🔄 UPDATING USER ONBOARDING PROGRESS")
        logger.info("=" * 60)
        
        try:
            with self.engine.connect() as conn:
                # Reset onboarding progress for existing users since step order changed
                conn.execute(text("""
                    UPDATE users 
                    SET onboarding_step = 0, 
                        onboarding_completed = FALSE,
                        onboarding_started_at = NULL,
                        onboarding_completed_at = NULL
                    WHERE onboarding_step > 0
                """))
                
                logger.info(f"✅ Reset onboarding progress for existing users")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to update onboarding progress: {e}")
            return False
    
    def run_update(self):
        """Run the complete onboarding update"""
        logger.info("🔄 EDONUOPS ERP - ONBOARDING SYSTEM UPDATE")
        logger.info("=" * 80)
        
        # Connect to database
        if not self.connect_to_database():
            return False
        
        # Update onboarding steps
        if not self.update_onboarding_steps():
            return False
        
        # Verify the update
        if not self.verify_onboarding_steps():
            return False
        
        # Update user progress
        if not self.update_onboarding_progress():
            return False
        
        logger.info("\n🎉 ONBOARDING SYSTEM UPDATE COMPLETED!")
        logger.info("=" * 60)
        logger.info("✅ Removed personal_info step from onboarding")
        logger.info("✅ Updated step order for remaining steps")
        logger.info("✅ Reset onboarding progress for existing users")
        logger.info("✅ Registration now collects: first_name, last_name, phone_number")
        logger.info("✅ Onboarding now focuses on: professional, company, preferences")
        logger.info("\n🚀 System ready for enhanced registration + onboarding flow!")
        
        return True

def main():
    """Main function"""
    updater = OnboardingUpdater()
    success = updater.run_update()
    
    if success:
        print("\n🎉 Onboarding system update completed successfully!")
        print("Registration and onboarding are now properly separated.")
    else:
        print("\n❌ Onboarding system update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
