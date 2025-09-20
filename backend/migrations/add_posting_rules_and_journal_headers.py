#!/usr/bin/env python3
"""
Migration: Add Posting Rules and Journal Headers Tables
Date: September 18, 2025
Purpose: Close enterprise ERP gaps - configurable posting rules and proper journal headers
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add posting rules and journal headers tables"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'erp_system.db')
    
    print(f"🔄 Running migration: Add Posting Rules and Journal Headers")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # 1. Create posting_rules table
        print("📋 Creating posting_rules table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posting_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type VARCHAR(50) NOT NULL,
                event_description VARCHAR(200),
                debit_account_name VARCHAR(100) NOT NULL,
                credit_account_name VARCHAR(100) NOT NULL,
                conditions TEXT,  -- JSON field for flexible conditions
                priority INTEGER DEFAULT 1,
                valid_from DATE DEFAULT CURRENT_DATE,
                valid_to DATE,
                company_id INTEGER,
                business_unit VARCHAR(50),
                is_active BOOLEAN DEFAULT 1,
                created_by VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                change_reason TEXT,
                version INTEGER DEFAULT 1
            )
        """)
        
        # 2. Create advanced_journal_headers table
        print("📋 Creating advanced_journal_headers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advanced_journal_headers (
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
                audit_trail TEXT,  -- JSON field for audit events
                reversal_reason TEXT,
                reversal_journal_id INTEGER,
                FOREIGN KEY (reversal_journal_id) REFERENCES advanced_journal_headers (id)
            )
        """)
        
        # 3. Insert default posting rules
        print("📋 Inserting default posting rules...")
        
        default_rules = [
            # Inventory Management
            ('inventory_receipt', 'Goods received from vendor', 'Inventory', 'GR/IR Clearing', '{"item_type": "stock"}', 1),
            ('inventory_sale', 'Inventory sold to customer', 'Cost of Goods Sold', 'Inventory', '{"transaction_type": "sale"}', 1),
            ('inventory_adjustment', 'Inventory count adjustment', 'Inventory Adjustment', 'Inventory', '{"adjustment_type": "count"}', 1),
            
            # Procurement
            ('vendor_bill_received', 'Vendor invoice received', 'GR/IR Clearing', 'Accounts Payable', '{"document_type": "invoice"}', 1),
            ('payment_made', 'Payment made to vendor', 'Accounts Payable', 'Cash', '{"payment_method": "bank"}', 1),
            
            # Sales
            ('customer_invoice_created', 'Customer invoice created', 'Accounts Receivable', 'Sales Revenue', '{"document_type": "invoice"}', 1),
            ('customer_payment_received', 'Customer payment received', 'Cash', 'Accounts Receivable', '{"payment_method": "bank"}', 1),
            
            # Alternative payment methods
            ('payment_made', 'Payment made via bank transfer', 'Accounts Payable', 'Bank Account', '{"payment_method": "transfer"}', 2),
            ('customer_payment_received', 'Customer payment via transfer', 'Bank Account', 'Accounts Receivable', '{"payment_method": "transfer"}', 2),
        ]
        
        for rule in default_rules:
            cursor.execute("""
                INSERT OR IGNORE INTO posting_rules 
                (event_type, event_description, debit_account_name, credit_account_name, conditions, priority, created_by)
                VALUES (?, ?, ?, ?, ?, ?, 'SYSTEM')
            """, rule)
        
        # 4. Update GeneralLedgerEntry to reference journal headers
        print("📋 Adding journal_header_id to GeneralLedgerEntry...")
        try:
            cursor.execute("""
                ALTER TABLE advanced_general_ledger_entries 
                ADD COLUMN journal_header_id INTEGER 
                REFERENCES advanced_journal_headers(id)
            """)
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"⚠️  Column might already exist: {e}")
        
        # 5. Create indexes for performance
        print("📋 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_posting_rules_event ON posting_rules(event_type, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_posting_rules_validity ON posting_rules(valid_from, valid_to)",
            "CREATE INDEX IF NOT EXISTS idx_journal_headers_source ON advanced_journal_headers(source_module, reference_id)",
            "CREATE INDEX IF NOT EXISTS idx_journal_headers_status ON advanced_journal_headers(status, posting_status)",
            "CREATE INDEX IF NOT EXISTS idx_journal_headers_period ON advanced_journal_headers(fiscal_period, posting_date)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        connection.commit()
        print("✅ Migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM posting_rules")
        rules_count = cursor.fetchone()[0]
        print(f"📊 Created {rules_count} posting rules")
        
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

