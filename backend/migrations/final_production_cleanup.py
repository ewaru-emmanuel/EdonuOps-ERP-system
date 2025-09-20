#!/usr/bin/env python3
"""
Migration: Final Production Cleanup
Date: September 18, 2025
Purpose: Clean the actual production database and set up posting rules
"""

import sqlite3
import os
import json
from datetime import datetime, date

def run_migration():
    """Final cleanup and setup for production database"""
    
    # Use the correct database file that the app uses
    db_path = os.path.join(os.path.dirname(__file__), '..', 'edonuops.db')
    
    print(f"🔄 Running migration: Final Production Cleanup")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        print("🗑️  Step 1: Cleaning transactional data...")
        
        # Clean transactional data but preserve structure and configuration
        tables_to_clean = [
            'advanced_general_ledger_entries',
            'advanced_journal_headers', 
            'journal_entries',
            'journal_lines',
            'invoices',
            'invoice_line_items',
            'payments',
            'customers',
            'vendors',
            'purchase_orders',
            'daily_balances',
            'daily_transaction_summaries',
            'inventory_transactions',
            'audit_logs'
        ]
        
        total_removed = 0
        for table in tables_to_clean:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    cursor.execute(f"DELETE FROM {table}")
                    print(f"   🗑️  {table}: removed {count} records")
                    total_removed += count
                else:
                    print(f"   ⚪ {table}: already empty")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  {table}: {e}")
        
        print(f"\n📊 Total records removed: {total_removed}")
        
        print("\n🔧 Step 2: Setting up posting rules...")
        
        # Clear and insert posting rules
        try:
            cursor.execute("DELETE FROM posting_rules")
            print("   🗑️  Cleared existing posting rules")
        except sqlite3.OperationalError:
            # Table might not exist, create it
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posting_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type VARCHAR(50) NOT NULL,
                    event_description VARCHAR(200),
                    debit_account_name VARCHAR(100) NOT NULL,
                    credit_account_name VARCHAR(100) NOT NULL,
                    conditions TEXT,
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
            print("   ✅ Created posting_rules table")
        
        # Insert default posting rules
        default_rules = [
            ('inventory_receipt', 'Goods received from vendor (GR/IR Process)', 'Inventory', 'GR/IR Clearing', '{"item_type": "stock"}', 1),
            ('inventory_sale', 'Inventory sold to customer (COGS)', 'Cost of Goods Sold', 'Inventory', '{"transaction_type": "sale"}', 1),
            ('vendor_bill_received', 'Vendor invoice received (clears GR/IR)', 'GR/IR Clearing', 'Accounts Payable', '{"has_goods_receipt": true}', 1),
            ('vendor_bill_received', 'Direct vendor bill (services)', 'Operating Expenses', 'Accounts Payable', '{"has_goods_receipt": false}', 2),
            ('payment_made', 'Payment made to vendor', 'Accounts Payable', 'Bank Account', '{"payment_method": "bank_transfer"}', 1),
            ('customer_invoice_created', 'Customer invoice created', 'Accounts Receivable', 'Sales Revenue', '{"document_type": "invoice"}', 1),
            ('customer_payment_received', 'Customer payment received', 'Bank Account', 'Accounts Receivable', '{"payment_method": "bank_transfer"}', 1),
        ]
        
        for rule in default_rules:
            cursor.execute("""
                INSERT INTO posting_rules 
                (event_type, event_description, debit_account_name, credit_account_name, conditions, priority, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'SYSTEM', ?)
            """, rule + (datetime.now(),))
        
        cursor.execute("SELECT COUNT(*) FROM posting_rules")
        rule_count = cursor.fetchone()[0]
        print(f"   ✅ Inserted {rule_count} posting rules")
        
        print("\n🔧 Step 3: Ensuring Chart of Accounts...")
        
        # Ensure basic chart of accounts exists
        basic_accounts = [
            ('1000', 'Cash', 'Asset', 'Current Assets'),
            ('1100', 'Bank Account', 'Asset', 'Current Assets'),
            ('1200', 'Accounts Receivable', 'Asset', 'Current Assets'),
            ('1300', 'Inventory', 'Asset', 'Current Assets'),
            ('1900', 'GR/IR Clearing', 'Asset', 'Current Assets'),
            ('2000', 'Accounts Payable', 'Liability', 'Current Liabilities'),
            ('3000', 'Equity', 'Equity', 'Owner Equity'),
            ('4000', 'Sales Revenue', 'Revenue', 'Operating Revenue'),
            ('5000', 'Cost of Goods Sold', 'Expense', 'Cost of Sales'),
            ('6000', 'Operating Expenses', 'Expense', 'Operating Expenses'),
        ]
        
        # Check if Chart of Accounts table exists
        try:
            cursor.execute("SELECT COUNT(*) FROM advanced_chart_of_accounts")
            coa_exists = True
        except sqlite3.OperationalError:
            # Create the table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS advanced_chart_of_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_code VARCHAR(20) UNIQUE NOT NULL,
                    account_name VARCHAR(100) NOT NULL,
                    account_type VARCHAR(50) NOT NULL,
                    account_category VARCHAR(50),
                    parent_account_id INTEGER,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            coa_exists = False
            print("   ✅ Created Chart of Accounts table")
        
        # Insert basic accounts if they don't exist
        accounts_added = 0
        for code, name, type_, category in basic_accounts:
            cursor.execute("SELECT COUNT(*) FROM advanced_chart_of_accounts WHERE account_code = ?", (code,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO advanced_chart_of_accounts 
                    (account_code, account_name, account_type, account_category, is_active, created_at)
                    VALUES (?, ?, ?, ?, 1, ?)
                """, (code, name, type_, category, datetime.now()))
                accounts_added += 1
        
        if accounts_added > 0:
            print(f"   ✅ Added {accounts_added} basic accounts to Chart of Accounts")
        else:
            print("   ⚪ Chart of Accounts already has basic accounts")
        
        print("\n🔧 Step 4: Reset auto-increment counters...")
        
        # Reset auto-increment counters
        for table in tables_to_clean:
            try:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            except sqlite3.OperationalError:
                pass
        
        connection.commit()
        
        print("\n✅ Migration completed successfully!")
        print("🚀 System Status: PRODUCTION READY")
        print("\n📋 Summary:")
        print(f"   • Database cleaned: {total_removed} records removed")
        print(f"   • Posting rules: {rule_count} configured")
        print(f"   • Chart of accounts: {accounts_added} basic accounts added")
        print("   • Auto-increment counters reset")
        print("   • Ready for your data! 🎯")
        
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

