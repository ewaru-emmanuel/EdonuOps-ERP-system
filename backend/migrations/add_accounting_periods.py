#!/usr/bin/env python3
"""
Migration: Add Accounting Periods Support
========================================

This migration adds accounting period support to the double-entry system:
1. Creates FiscalYear and AccountingPeriod tables
2. Adds accounting_period_id to JournalEntry
3. Adds period validation fields
4. Initializes default periods for existing users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime, date
from modules.finance.accounting_periods import FiscalYear, AccountingPeriod, period_manager

def add_accounting_periods():
    """Add accounting periods support to the system"""
    with app.app_context():
        print("🔄 Adding Accounting Periods Support...")
        
        try:
            # Create the new tables
            print("   📋 Creating FiscalYear and AccountingPeriod tables...")
            db.create_all()
            
            # Get all unique user IDs from existing journal entries
            from modules.finance.models import JournalEntry
            user_ids = db.session.query(JournalEntry.user_id).distinct().all()
            user_ids = [uid[0] for uid in user_ids if uid[0] is not None]
            
            print(f"   👥 Found {len(user_ids)} users with journal entries")
            
            # Initialize default periods for each user
            for user_id in user_ids:
                print(f"   🔧 Initializing periods for user {user_id}...")
                
                # Check if user already has fiscal years
                existing_fy = FiscalYear.query.filter_by(user_id=user_id).first()
                if existing_fy:
                    print(f"      ✅ User {user_id} already has fiscal years")
                    continue
                
                # Create default fiscal year for current year
                current_year = datetime.now().year
                fiscal_year = period_manager.initialize_default_periods(user_id)
                print(f"      ✅ Created FY {current_year} with 12 periods")
            
            # Add accounting_period_id column to journal_entries if it doesn't exist
            print("   🔧 Adding accounting_period_id to journal_entries...")
            
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('journal_entries')]
            
            if 'accounting_period_id' not in columns:
                # Add the column
                db.engine.execute("""
                    ALTER TABLE journal_entries 
                    ADD COLUMN accounting_period_id INTEGER 
                    REFERENCES accounting_periods(id)
                """)
                print("      ✅ Added accounting_period_id column")
            else:
                print("      ✅ accounting_period_id column already exists")
            
            # Add period validation fields
            period_fields = [
                'is_backdated',
                'period_locked',
                'backdate_reason'
            ]
            
            for field in period_fields:
                if field not in columns:
                    if field == 'is_backdated':
                        db.engine.execute(f"ALTER TABLE journal_entries ADD COLUMN {field} BOOLEAN DEFAULT FALSE")
                    elif field == 'period_locked':
                        db.engine.execute(f"ALTER TABLE journal_entries ADD COLUMN {field} BOOLEAN DEFAULT FALSE")
                    elif field == 'backdate_reason':
                        db.engine.execute(f"ALTER TABLE journal_entries ADD COLUMN {field} VARCHAR(200)")
                    print(f"      ✅ Added {field} column")
                else:
                    print(f"      ✅ {field} column already exists")
            
            # Update existing journal entries with period information
            print("   🔄 Updating existing journal entries with period information...")
            
            journal_entries = JournalEntry.query.all()
            updated_count = 0
            
            for entry in journal_entries:
                if not entry.accounting_period_id:
                    # Find the appropriate period for this entry
                    period = period_manager.get_period_for_date(entry.doc_date, entry.user_id)
                    if period:
                        entry.accounting_period_id = period.id
                        
                        # Check if it's backdated
                        if entry.doc_date < date.today():
                            entry.is_backdated = True
                            entry.backdate_reason = "Migrated from existing data"
                        
                        updated_count += 1
            
            db.session.commit()
            print(f"      ✅ Updated {updated_count} journal entries with period information")
            
            # Create indexes for performance
            print("   🚀 Creating indexes for performance...")
            try:
                db.engine.execute("CREATE INDEX IF NOT EXISTS idx_journal_entries_period ON journal_entries(accounting_period_id)")
                db.engine.execute("CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries(doc_date)")
                db.engine.execute("CREATE INDEX IF NOT EXISTS idx_accounting_periods_dates ON accounting_periods(start_date, end_date)")
                print("      ✅ Created performance indexes")
            except Exception as e:
                print(f"      ⚠️  Index creation warning: {e}")
            
            print("✅ Accounting Periods migration completed successfully!")
            
            # Print summary
            fiscal_years = FiscalYear.query.count()
            periods = AccountingPeriod.query.count()
            print(f"📊 Summary:")
            print(f"   Fiscal Years: {fiscal_years}")
            print(f"   Accounting Periods: {periods}")
            print(f"   Updated Journal Entries: {updated_count}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

def rollback_accounting_periods():
    """Rollback accounting periods migration"""
    with app.app_context():
        print("🔄 Rolling back Accounting Periods migration...")
        
        try:
            # Remove the added columns
            db.engine.execute("ALTER TABLE journal_entries DROP COLUMN IF EXISTS accounting_period_id")
            db.engine.execute("ALTER TABLE journal_entries DROP COLUMN IF EXISTS is_backdated")
            db.engine.execute("ALTER TABLE journal_entries DROP COLUMN IF EXISTS period_locked")
            db.engine.execute("ALTER TABLE journal_entries DROP COLUMN IF EXISTS backdate_reason")
            
            # CRITICAL SAFETY: Create backup before destructive operation
            print("🔄 Creating backup before rollback...")
            backup_file = f"database_backup_before_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                import shutil
                shutil.copy2('edonuops.db', backup_file)
                print(f"✅ Backup created: {backup_file}")
            except Exception as e:
                print(f"❌ Backup failed: {e}")
                print("🚨 ABORTING: Cannot proceed without backup!")
                return False
            
            # Drop the tables
            db.drop_all()
            
            print("✅ Rollback completed successfully!")
            print(f"💾 Backup available at: {backup_file}")
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_accounting_periods()
    else:
        add_accounting_periods()
