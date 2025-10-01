#!/usr/bin/env python3
"""
Migration: Add provider fields to bank_accounts table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def run_migration():
    """Add missing provider fields to bank_accounts table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Adding provider fields to bank_accounts table...")
            
            # Check if provider column exists
            result = db.session.execute(text("PRAGMA table_info(bank_accounts)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'provider' not in columns:
                print("  ➕ Adding provider column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN provider VARCHAR(20)"))
            
            if 'external_account_id' not in columns:
                print("  ➕ Adding external_account_id column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN external_account_id VARCHAR(100)"))
            
            if 'access_token' not in columns:
                print("  ➕ Adding access_token column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN access_token TEXT"))
            
            if 'connected_at' not in columns:
                print("  ➕ Adding connected_at column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN connected_at DATETIME"))
            
            if 'connected_by' not in columns:
                print("  ➕ Adding connected_by column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN connected_by VARCHAR(100)"))
            
            if 'last_sync_at' not in columns:
                print("  ➕ Adding last_sync_at column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN last_sync_at DATETIME"))
            
            if 'sync_frequency' not in columns:
                print("  ➕ Adding sync_frequency column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN sync_frequency VARCHAR(20) DEFAULT 'daily'"))
            
            db.session.commit()
            print("✅ Successfully added provider fields to bank_accounts table")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)












