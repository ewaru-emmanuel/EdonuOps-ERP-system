#!/usr/bin/env python3
"""
Migration: Insert Default Posting Rules
Date: September 18, 2025
Purpose: Insert default posting rules for core business events
"""

import sqlite3
import os
import json
from datetime import datetime, date

def run_migration():
    """Insert default posting rules into the database"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'erp_system.db')
    
    print(f"🔄 Running migration: Insert Default Posting Rules")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Clear existing rules first
        cursor.execute("DELETE FROM posting_rules")
        print("🗑️  Cleared existing posting rules")
        
        # Define default posting rules
        default_rules = [
            # Inventory Management
            {
                'event_type': 'inventory_receipt',
                'event_description': 'Goods received from vendor (GR/IR Process)',
                'debit_account_name': 'Inventory',
                'credit_account_name': 'GR/IR Clearing',
                'conditions': json.dumps({"item_type": "stock", "process": "gr_ir"}),
                'priority': 1,
                'created_by': 'SYSTEM'
            },
            {
                'event_type': 'inventory_sale',
                'event_description': 'Inventory sold to customer (COGS)',
                'debit_account_name': 'Cost of Goods Sold',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"transaction_type": "sale"}),
                'priority': 1,
                'created_by': 'SYSTEM'
            },
            {
                'event_type': 'inventory_adjustment',
                'event_description': 'Inventory count adjustment',
                'debit_account_name': 'Inventory Adjustment',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"adjustment_type": "count"}),
                'priority': 1,
                'created_by': 'SYSTEM'
            },
            
            # Procurement (GR/IR Process)
            {
                'event_type': 'vendor_bill_received',
                'event_description': 'Vendor invoice received (clears GR/IR)',
                'debit_account_name': 'GR/IR Clearing',
                'credit_account_name': 'Accounts Payable',
                'conditions': json.dumps({"has_goods_receipt": True}),
                'priority': 1,
                'created_by': 'SYSTEM'
            },
            {
                'event_type': 'vendor_bill_received',
                'event_description': 'Direct vendor bill (no goods receipt)',
                'debit_account_name': 'Operating Expenses',
                'credit_account_name': 'Accounts Payable',
                'conditions': json.dumps({"has_goods_receipt": False, "bill_type": "service"}),
                'priority': 2,
                'created_by': 'SYSTEM'
            },
            {
                'event_type': 'payment_made',
                'event_description': 'Payment made to vendor via bank',
                'debit_account_name': 'Accounts Payable',
                'credit_account_name': 'Bank Account',
                'conditions': json.dumps({"payment_method": "bank_transfer"}),
                'priority': 1,
                'created_by': 'SYSTEM'
            },
            {
                'event_type': 'payment_made',
                'event_description': 'Payment made to vendor via cash',
                'debit_account_name': 'Accounts Payable',
                'credit_account_name': 'Cash',
                'conditions': json.dumps({"payment_method": "cash"}),
                'priority': 2,
                'created_by': 'SYSTEM'
            },
            
            # Sales
            {
                'event_type': 'customer_invoice_created',
                'event_description': 'Customer invoice created',
                'debit_account_name': 'Accounts Receivable',
                'credit_account_name': 'Sales Revenue',
                'conditions': json.dumps({"document_type": "invoice"}),
                'priority': 1,
                'created_by': 'SYSTEM'
            },
            {
                'event_type': 'customer_payment_received',
                'event_description': 'Customer payment received via bank',
                'debit_account_name': 'Bank Account',
                'credit_account_name': 'Accounts Receivable',
                'conditions': json.dumps({"payment_method": "bank_transfer"}),
                'priority': 1,
                'created_by': 'SYSTEM'
            },
            {
                'event_type': 'customer_payment_received',
                'event_description': 'Customer payment received via cash',
                'debit_account_name': 'Cash',
                'credit_account_name': 'Accounts Receivable',
                'conditions': json.dumps({"payment_method": "cash"}),
                'priority': 2,
                'created_by': 'SYSTEM'
            }
        ]
        
        # Insert rules
        for rule in default_rules:
            cursor.execute("""
                INSERT INTO posting_rules 
                (event_type, event_description, debit_account_name, credit_account_name, 
                 conditions, priority, valid_from, is_active, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule['event_type'],
                rule['event_description'],
                rule['debit_account_name'],
                rule['credit_account_name'],
                rule['conditions'],
                rule['priority'],
                date.today(),
                True,
                rule['created_by'],
                datetime.now()
            ))
        
        connection.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM posting_rules")
        rule_count = cursor.fetchone()[0]
        
        print(f"✅ Migration completed successfully!")
        print(f"📊 Inserted {rule_count} default posting rules")
        
        # Show summary by event type
        cursor.execute("""
            SELECT event_type, COUNT(*) as rule_count 
            FROM posting_rules 
            GROUP BY event_type 
            ORDER BY event_type
        """)
        
        print("\n📋 Posting Rules Summary:")
        for event_type, count in cursor.fetchall():
            print(f"   • {event_type}: {count} rule(s)")
        
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

