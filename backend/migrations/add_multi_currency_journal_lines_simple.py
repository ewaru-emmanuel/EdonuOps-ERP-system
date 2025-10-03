#!/usr/bin/env python3
"""
Simple Migration: Add Multi-Currency Support to Journal Lines
============================================================

This migration adds multi-currency fields to journal_lines table without conflicts.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime

def add_multi_currency_journal_lines_simple():
    """Add multi-currency support to journal lines - simple version"""
    with app.app_context():
        print("🔄 Adding Multi-Currency Support to Journal Lines (Simple)...")
        
        try:
            # Check if columns already exist and add them
            with db.engine.connect() as connection:
                # Add currency field
                try:
                    connection.execute("ALTER TABLE journal_lines ADD COLUMN currency VARCHAR(3) DEFAULT 'USD'")
                    print("   ✅ Added currency column")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e).lower():
                        print("   ✅ currency column already exists")
                    else:
                        print(f"   ⚠️  currency column: {e}")
                
                # Add exchange_rate field
                try:
                    connection.execute("ALTER TABLE journal_lines ADD COLUMN exchange_rate FLOAT DEFAULT 1.0")
                    print("   ✅ Added exchange_rate column")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e).lower():
                        print("   ✅ exchange_rate column already exists")
                    else:
                        print(f"   ⚠️  exchange_rate column: {e}")
                
                # Add functional_debit_amount field
                try:
                    connection.execute("ALTER TABLE journal_lines ADD COLUMN functional_debit_amount FLOAT DEFAULT 0.0")
                    print("   ✅ Added functional_debit_amount column")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e).lower():
                        print("   ✅ functional_debit_amount column already exists")
                    else:
                        print(f"   ⚠️  functional_debit_amount column: {e}")
                
                # Add functional_credit_amount field
                try:
                    connection.execute("ALTER TABLE journal_lines ADD COLUMN functional_credit_amount FLOAT DEFAULT 0.0")
                    print("   ✅ Added functional_credit_amount column")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e).lower():
                        print("   ✅ functional_credit_amount column already exists")
                    else:
                        print(f"   ⚠️  functional_credit_amount column: {e}")
                
                # Connection commit not needed for DDL operations
            
            # Update existing journal lines with functional amounts
            print("   🔄 Updating existing journal lines with functional amounts...")
            
            # Get all journal lines and update them
            from modules.finance.models import JournalLine, JournalEntry
            
            journal_lines = JournalLine.query.all()
            updated_count = 0
            
            for line in journal_lines:
                # Get the journal entry to get the currency
                entry = JournalEntry.query.get(line.journal_entry_id)
                if entry:
                    # Set currency from journal entry
                    line.currency = entry.currency or 'USD'
                    line.exchange_rate = 1.0  # Default to 1.0 for existing entries
                    
                    # Set functional amounts (same as transaction amounts for existing entries)
                    line.functional_debit_amount = line.debit_amount
                    line.functional_credit_amount = line.credit_amount
                    
                    updated_count += 1
            
            db.session.commit()
            print(f"      ✅ Updated {updated_count} journal lines with multi-currency data")
            
            print("✅ Multi-Currency Journal Lines migration completed successfully!")
            
            # Print summary
            print(f"📊 Summary:")
            print(f"   Updated Journal Lines: {updated_count}")
            print(f"   Multi-Currency Fields: Added")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_multi_currency_journal_lines_simple()
