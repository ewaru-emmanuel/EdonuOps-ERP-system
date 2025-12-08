"""
Database Migration: Accounting Periods to Tenant-Centric
=========================================================

This migration converts accounting_periods and fiscal_years tables from
user-centric to tenant-centric architecture.

Steps:
1. Add tenant_id columns (nullable initially)
2. Migrate existing data (map user_id to tenant_id via users table)
3. Make tenant_id NOT NULL
4. Drop old user_id columns
5. Add unique constraint on fiscal_years (tenant_id, year)
6. Create indexes

Run with: python migrations/migrate_accounting_periods_to_tenant.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_accounting_periods_to_tenant():
    """Migrate accounting periods from user-centric to tenant-centric"""
    
    with app.app_context():
        try:
            logger.info("🔄 Starting migration: Accounting Periods to Tenant-Centric")
            
            # Step 1: Add tenant_id columns (nullable initially)
            logger.info("Step 1: Adding tenant_id columns...")
            
            # Check if columns already exist
            with db.engine.connect() as conn:
                # Check fiscal_years
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'fiscal_years' AND column_name = 'tenant_id'
                """))
                fiscal_years_has_tenant = result.fetchone() is not None
                
                # Check accounting_periods
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'accounting_periods' AND column_name = 'tenant_id'
                """))
                accounting_periods_has_tenant = result.fetchone() is not None
                
                # Add tenant_id to fiscal_years if not exists
                if not fiscal_years_has_tenant:
                    conn.execute(text("""
                        ALTER TABLE fiscal_years 
                        ADD COLUMN tenant_id VARCHAR(50)
                    """))
                    conn.commit()
                    logger.info("✅ Added tenant_id column to fiscal_years")
                else:
                    logger.info("ℹ️  tenant_id column already exists in fiscal_years")
                
                # Add tenant_id to accounting_periods if not exists
                if not accounting_periods_has_tenant:
                    conn.execute(text("""
                        ALTER TABLE accounting_periods 
                        ADD COLUMN tenant_id VARCHAR(50)
                    """))
                    conn.commit()
                    logger.info("✅ Added tenant_id column to accounting_periods")
                else:
                    logger.info("ℹ️  tenant_id column already exists in accounting_periods")
            
            # Step 2: Migrate existing data (map user_id to tenant_id)
            logger.info("Step 2: Migrating existing data...")
            
            with db.engine.connect() as conn:
                # Migrate fiscal_years: Get tenant_id from users table
                result = conn.execute(text("""
                    UPDATE fiscal_years fy
                    SET tenant_id = u.tenant_id
                    FROM users u
                    WHERE fy.user_id = u.id 
                    AND fy.tenant_id IS NULL
                    AND u.tenant_id IS NOT NULL
                """))
                fiscal_years_updated = result.rowcount
                conn.commit()
                logger.info(f"✅ Migrated {fiscal_years_updated} fiscal_years records")
                
                # Migrate accounting_periods: Get tenant_id from fiscal_years
                result = conn.execute(text("""
                    UPDATE accounting_periods ap
                    SET tenant_id = fy.tenant_id
                    FROM fiscal_years fy
                    WHERE ap.fiscal_year_id = fy.id
                    AND ap.tenant_id IS NULL
                    AND fy.tenant_id IS NOT NULL
                """))
                accounting_periods_updated = result.rowcount
                conn.commit()
                logger.info(f"✅ Migrated {accounting_periods_updated} accounting_periods records")
                
                # Check for any unmigrated records
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM fiscal_years WHERE tenant_id IS NULL
                """))
                unmigrated_fy = result.scalar()
                
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM accounting_periods WHERE tenant_id IS NULL
                """))
                unmigrated_ap = result.scalar()
                
                if unmigrated_fy > 0 or unmigrated_ap > 0:
                    logger.warning(f"⚠️  Warning: {unmigrated_fy} fiscal_years and {unmigrated_ap} accounting_periods could not be migrated (no tenant_id found)")
                    logger.warning("   These records may need manual intervention")
            
            # Step 3: Create indexes
            logger.info("Step 3: Creating indexes...")
            
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fiscal_years_tenant_id ON fiscal_years(tenant_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_accounting_periods_tenant_id ON accounting_periods(tenant_id)"))
                    conn.commit()
                    logger.info("✅ Created indexes on tenant_id columns")
                except Exception as e:
                    logger.warning(f"⚠️  Index creation warning (may already exist): {e}")
            
            # Step 4: Make tenant_id NOT NULL (only if all records have been migrated)
            logger.info("Step 4: Making tenant_id NOT NULL...")
            
            with db.engine.connect() as conn:
                # Check for NULL values
                result = conn.execute(text("SELECT COUNT(*) FROM fiscal_years WHERE tenant_id IS NULL"))
                null_fy = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM accounting_periods WHERE tenant_id IS NULL"))
                null_ap = result.scalar()
                
                if null_fy == 0 and null_ap == 0:
                    conn.execute(text("ALTER TABLE fiscal_years ALTER COLUMN tenant_id SET NOT NULL"))
                    conn.execute(text("ALTER TABLE accounting_periods ALTER COLUMN tenant_id SET NOT NULL"))
                    conn.commit()
                    logger.info("✅ Made tenant_id NOT NULL")
                else:
                    logger.warning(f"⚠️  Skipping NOT NULL constraint: {null_fy} fiscal_years and {null_ap} accounting_periods still have NULL tenant_id")
            
            # Step 5: Drop unique constraint on fiscal_years.year if it exists, then add composite unique constraint
            logger.info("Step 5: Updating unique constraints...")
            
            with db.engine.connect() as conn:
                try:
                    # Drop old unique constraint on year (if exists)
                    conn.execute(text("ALTER TABLE fiscal_years DROP CONSTRAINT IF EXISTS fiscal_years_year_key"))
                    conn.commit()
                    logger.info("✅ Dropped old unique constraint on year")
                except Exception as e:
                    logger.warning(f"⚠️  Could not drop old constraint (may not exist): {e}")
                
                try:
                    # Add composite unique constraint
                    conn.execute(text("""
                        ALTER TABLE fiscal_years 
                        ADD CONSTRAINT uq_fiscal_year_tenant_year 
                        UNIQUE (tenant_id, year)
                    """))
                    conn.commit()
                    logger.info("✅ Added composite unique constraint (tenant_id, year)")
                except Exception as e:
                    logger.warning(f"⚠️  Could not add constraint (may already exist): {e}")
            
            # Step 6: Drop old user_id columns (optional - comment out if you want to keep them for reference)
            logger.info("Step 6: Dropping old user_id columns...")
            
            drop_user_id = os.environ.get('DROP_OLD_USER_ID', 'false').lower() == 'true'
            if drop_user_id:
                with db.engine.connect() as conn:
                    try:
                        conn.execute(text("ALTER TABLE fiscal_years DROP COLUMN IF EXISTS user_id"))
                        conn.execute(text("ALTER TABLE accounting_periods DROP COLUMN IF EXISTS user_id"))
                        conn.commit()
                        logger.info("✅ Dropped old user_id columns")
                    except Exception as e:
                        logger.warning(f"⚠️  Could not drop user_id columns: {e}")
            else:
                logger.info("ℹ️  Skipping user_id column deletion (set DROP_OLD_USER_ID=true to enable)")
            
            logger.info("✅ Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_accounting_periods_to_tenant()

