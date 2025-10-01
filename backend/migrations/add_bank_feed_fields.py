"""
Migration: Add bank feed integration fields to bank_accounts table
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def add_bank_feed_fields():
    """Add bank feed integration fields to bank_accounts table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("PRAGMA table_info(bank_accounts)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            # Add provider field
            if 'provider' not in existing_columns:
                print("➕ Adding provider column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN provider VARCHAR(20)"))
                db.session.commit()
            
            # Add external_account_id field
            if 'external_account_id' not in existing_columns:
                print("➕ Adding external_account_id column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN external_account_id VARCHAR(100)"))
                db.session.commit()
            
            # Add access_token field
            if 'access_token' not in existing_columns:
                print("➕ Adding access_token column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN access_token TEXT"))
                db.session.commit()
            
            # Add connected_at field
            if 'connected_at' not in existing_columns:
                print("➕ Adding connected_at column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN connected_at DATETIME"))
                db.session.commit()
            
            # Add connected_by field
            if 'connected_by' not in existing_columns:
                print("➕ Adding connected_by column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN connected_by VARCHAR(100)"))
                db.session.commit()
            
            # Add last_sync_at field
            if 'last_sync_at' not in existing_columns:
                print("➕ Adding last_sync_at column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN last_sync_at DATETIME"))
                db.session.commit()
            
            # Add sync_frequency field
            if 'sync_frequency' not in existing_columns:
                print("➕ Adding sync_frequency column...")
                db.session.execute(text("ALTER TABLE bank_accounts ADD COLUMN sync_frequency VARCHAR(20) DEFAULT 'daily'"))
                db.session.commit()
            
            print("✅ Bank feed fields added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding bank feed fields: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_bank_feed_fields()










