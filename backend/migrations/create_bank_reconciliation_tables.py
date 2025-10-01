#!/usr/bin/env python3
"""
Migration script to create bank reconciliation tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def create_bank_reconciliation_tables():
    """Create bank reconciliation tables"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Creating bank reconciliation tables...")
            
            # Create bank_transactions table
            print("➕ Creating bank_transactions table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS bank_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bank_account_id INTEGER NOT NULL,
                    transaction_date DATE NOT NULL,
                    amount REAL NOT NULL,
                    reference VARCHAR(100),
                    description VARCHAR(255),
                    statement_date DATE,
                    bank_reference VARCHAR(100),
                    matched BOOLEAN DEFAULT 0,
                    matched_transaction_id INTEGER,
                    matched_transaction_type VARCHAR(20),
                    reconciliation_session_id INTEGER,
                    reconciled_by VARCHAR(100),
                    reconciled_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id),
                    FOREIGN KEY (reconciliation_session_id) REFERENCES reconciliation_sessions(id)
                )
            """))
            print("✅ bank_transactions table created")
            
            # Create reconciliation_sessions table
            print("➕ Creating reconciliation_sessions table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS reconciliation_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bank_account_id INTEGER NOT NULL,
                    statement_date DATE NOT NULL,
                    statement_balance REAL NOT NULL,
                    book_balance REAL NOT NULL,
                    difference REAL DEFAULT 0.0,
                    status VARCHAR(20) DEFAULT 'pending',
                    completed_at DATETIME,
                    completed_by VARCHAR(100),
                    outstanding_deposits REAL DEFAULT 0.0,
                    outstanding_checks REAL DEFAULT 0.0,
                    bank_charges REAL DEFAULT 0.0,
                    bank_interest REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id)
                )
            """))
            print("✅ reconciliation_sessions table created")
            
            # Commit all changes
            db.session.commit()
            print("🎉 Bank reconciliation tables created successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_bank_reconciliation_tables()










