#!/usr/bin/env python3
"""
Migration: Add Multi-Currency Support to Journal Lines
====================================================

This migration adds multi-currency fields to journal_lines table:
1. currency - Transaction currency
2. exchange_rate - Exchange rate used
3. functional_debit_amount - Amount in base currency
4. functional_credit_amount - Amount in base currency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime

def add_multi_currency_journal_lines():
    """Add multi-currency support to journal lines"""
    with app.app_context():
        print("🔄 Adding Multi-Currency Support to Journal Lines...")
        
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('journal_lines')]
            
            # Add currency field
            if 'currency' not in columns:
                db.engine.execute("ALTER TABLE journal_lines ADD COLUMN currency VARCHAR(3) DEFAULT 'USD'")
                print("   ✅ Added currency column")
            else:
                print("   ✅ currency column already exists")
            
            # Add exchange_rate field
            if 'exchange_rate' not in columns:
                db.engine.execute("ALTER TABLE journal_lines ADD COLUMN exchange_rate FLOAT DEFAULT 1.0")
                print("   ✅ Added exchange_rate column")
            else:
                print("   ✅ exchange_rate column already exists")
            
            # Add functional_debit_amount field
            if 'functional_debit_amount' not in columns:
                db.engine.execute("ALTER TABLE journal_lines ADD COLUMN functional_debit_amount FLOAT DEFAULT 0.0")
                print("   ✅ Added functional_debit_amount column")
            else:
                print("   ✅ functional_debit_amount column already exists")
            
            # Add functional_credit_amount field
            if 'functional_credit_amount' not in columns:
                db.engine.execute("ALTER TABLE journal_lines ADD COLUMN functional_credit_amount FLOAT DEFAULT 0.0")
                print("   ✅ Added functional_credit_amount column")
            else:
                print("   ✅ functional_credit_amount column already exists")
            
            # Update existing journal lines with functional amounts
            print("   🔄 Updating existing journal lines with functional amounts...")
            
            # Get all journal lines
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
            
            # Create indexes for performance
            print("   🚀 Creating indexes for performance...")
            try:
                db.engine.execute("CREATE INDEX IF NOT EXISTS idx_journal_lines_currency ON journal_lines(currency)")
                db.engine.execute("CREATE INDEX IF NOT EXISTS idx_journal_lines_exchange_rate ON journal_lines(exchange_rate)")
                print("      ✅ Created performance indexes")
            except Exception as e:
                print(f"      ⚠️  Index creation warning: {e}")
            
            print("✅ Multi-Currency Journal Lines migration completed successfully!")
            
            # Print summary
            print(f"📊 Summary:")
            print(f"   Updated Journal Lines: {updated_count}")
            print(f"   Multi-Currency Fields: Added")
            print(f"   Performance Indexes: Created")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

def rollback_multi_currency_journal_lines():
    """Rollback multi-currency journal lines migration"""
    with app.app_context():
        print("🔄 Rolling back Multi-Currency Journal Lines migration...")
        
        try:
            # Remove the added columns
            db.engine.execute("ALTER TABLE journal_lines DROP COLUMN IF EXISTS currency")
            db.engine.execute("ALTER TABLE journal_lines DROP COLUMN IF EXISTS exchange_rate")
            db.engine.execute("ALTER TABLE journal_lines DROP COLUMN IF EXISTS functional_debit_amount")
            db.engine.execute("ALTER TABLE journal_lines DROP COLUMN IF EXISTS functional_credit_amount")
            
            print("✅ Rollback completed successfully!")
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_multi_currency_journal_lines()
    else:
        add_multi_currency_journal_lines()

