#!/usr/bin/env python3
"""
Migration script to add payment method fields to GeneralLedgerEntry table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def add_payment_fields_to_gl():
    """Add payment method integration fields to GeneralLedgerEntry table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Adding payment method fields to GeneralLedgerEntry table...")
            
            # Check if columns already exist (SQLite compatible)
            try:
                result = db.session.execute(text("PRAGMA table_info(advanced_general_ledger_entries)"))
                existing_columns = [row[1] for row in result.fetchall()]
                print(f"📋 All columns: {existing_columns}")
            except Exception as e:
                print(f"⚠️ Could not check existing columns: {e}")
                existing_columns = []
            
            # Add payment_method_id column
            if 'payment_method_id' not in existing_columns:
                print("➕ Adding payment_method_id column...")
                db.session.execute(text("""
                    ALTER TABLE advanced_general_ledger_entries 
                    ADD COLUMN payment_method_id INTEGER REFERENCES payment_methods(id)
                """))
                print("✅ payment_method_id column added")
            else:
                print("✅ payment_method_id column already exists")
            
            # Add bank_account_id column
            if 'bank_account_id' not in existing_columns:
                print("➕ Adding bank_account_id column...")
                db.session.execute(text("""
                    ALTER TABLE advanced_general_ledger_entries 
                    ADD COLUMN bank_account_id INTEGER REFERENCES bank_accounts(id)
                """))
                print("✅ bank_account_id column added")
            else:
                print("✅ bank_account_id column already exists")
            
            # Add payment_reference column
            if 'payment_reference' not in existing_columns:
                print("➕ Adding payment_reference column...")
                db.session.execute(text("""
                    ALTER TABLE advanced_general_ledger_entries 
                    ADD COLUMN payment_reference VARCHAR(100)
                """))
                print("✅ payment_reference column added")
            else:
                print("✅ payment_reference column already exists")
            
            # Add source_module column
            if 'source_module' not in existing_columns:
                print("➕ Adding source_module column...")
                db.session.execute(text("""
                    ALTER TABLE advanced_general_ledger_entries 
                    ADD COLUMN source_module VARCHAR(50)
                """))
                print("✅ source_module column added")
            else:
                print("✅ source_module column already exists")
            
            # Add source_transaction_id column
            if 'source_transaction_id' not in existing_columns:
                print("➕ Adding source_transaction_id column...")
                db.session.execute(text("""
                    ALTER TABLE advanced_general_ledger_entries 
                    ADD COLUMN source_transaction_id INTEGER
                """))
                print("✅ source_transaction_id column added")
            else:
                print("✅ source_transaction_id column already exists")
            
            # Commit all changes
            db.session.commit()
            print("🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_payment_fields_to_gl()
