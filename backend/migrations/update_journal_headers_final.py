#!/usr/bin/env python3
"""
Migration: Update Journal Headers Final
Date: September 18, 2025
Purpose: Update journal headers table to match our enhanced model
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Update journal headers table structure"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'edonuops.db')
    
    print(f"🔄 Running migration: Update Journal Headers Final")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Drop and recreate the table with the correct structure
        print("🗑️  Dropping old advanced_journal_headers table...")
        cursor.execute("DROP TABLE IF EXISTS advanced_journal_headers")
        
        print("✅ Creating new advanced_journal_headers table...")
        cursor.execute("""
            CREATE TABLE advanced_journal_headers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_number VARCHAR(50) UNIQUE NOT NULL,
                source_module VARCHAR(50) NOT NULL,
                source_document_type VARCHAR(50),
                reference_id VARCHAR(50),
                posting_date DATE NOT NULL,
                document_date DATE NOT NULL,
                fiscal_period VARCHAR(10) NOT NULL,
                description TEXT,
                total_debit REAL DEFAULT 0.0,
                total_credit REAL DEFAULT 0.0,
                currency VARCHAR(3) DEFAULT 'USD',
                exchange_rate REAL DEFAULT 1.0,
                status VARCHAR(20) DEFAULT 'draft',
                posting_status VARCHAR(20) DEFAULT 'unposted',
                approval_status VARCHAR(20) DEFAULT 'pending',
                created_by VARCHAR(100),
                posted_by VARCHAR(100),
                approved_by VARCHAR(100),
                reversed_by VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                posted_at DATETIME,
                approved_at DATETIME,
                reversed_at DATETIME,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                audit_trail TEXT,
                reversal_reason TEXT,
                reversal_journal_id INTEGER,
                FOREIGN KEY (reversal_journal_id) REFERENCES advanced_journal_headers (id)
            )
        """)
        
        # Create indexes for performance
        print("📋 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_journal_headers_source ON advanced_journal_headers(source_module, reference_id)",
            "CREATE INDEX IF NOT EXISTS idx_journal_headers_status ON advanced_journal_headers(status, posting_status)",
            "CREATE INDEX IF NOT EXISTS idx_journal_headers_period ON advanced_journal_headers(fiscal_period, posting_date)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Also ensure GeneralLedgerEntry table has the journal_header_id column
        print("🔧 Updating GeneralLedgerEntry table...")
        try:
            cursor.execute("""
                ALTER TABLE advanced_general_ledger_entries 
                ADD COLUMN journal_header_id INTEGER 
                REFERENCES advanced_journal_headers(id)
            """)
            print("   ✅ Added journal_header_id column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"   ⚠️  Column might already exist: {e}")
            else:
                print("   ⚪ journal_header_id column already exists")
        
        connection.commit()
        
        print("✅ Migration completed successfully!")
        print("📊 Journal headers table updated with enterprise features")
        
        # Show the new structure
        cursor.execute("PRAGMA table_info(advanced_journal_headers)")
        columns = cursor.fetchall()
        print(f"📋 Table now has {len(columns)} columns with full enterprise features")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    run_migration()

