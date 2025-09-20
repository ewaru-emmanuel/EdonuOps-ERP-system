#!/usr/bin/env python3
"""
Migration: Add Inventory Posting Rules
Date: September 18, 2025
Purpose: Add posting rules for all inventory-finance integration events
"""

import sqlite3
import os
import json
from datetime import datetime, date

def run_migration():
    """Add inventory posting rules to the database"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'edonuops.db')
    
    print(f"🔄 Running migration: Add Inventory Posting Rules")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Define inventory-specific posting rules
        inventory_rules = [
            # Inventory Issues (COGS)
            {
                'event_type': 'inventory_issue',
                'event_description': 'Inventory issued for sales (COGS)',
                'debit_account_name': 'Cost of Goods Sold',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"transaction_type": "issue"}),
                'priority': 1
            },
            
            # Inventory Adjustments
            {
                'event_type': 'inventory_adjustment',
                'event_description': 'Positive inventory adjustment (found more)',
                'debit_account_name': 'Inventory',
                'credit_account_name': 'Inventory Adjustment Income',
                'conditions': json.dumps({"adjustment_type": "positive"}),
                'priority': 1
            },
            {
                'event_type': 'inventory_adjustment',
                'event_description': 'Negative inventory adjustment (shortage/loss)',
                'debit_account_name': 'Inventory Adjustment Expense',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"adjustment_type": "negative"}),
                'priority': 2
            },
            
            # Inventory Write-offs
            {
                'event_type': 'inventory_writeoff',
                'event_description': 'Inventory write-off for damaged items',
                'debit_account_name': 'Inventory Damage Expense',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"reason": "damaged"}),
                'priority': 1
            },
            {
                'event_type': 'inventory_writeoff',
                'event_description': 'Inventory write-off for obsolete items',
                'debit_account_name': 'Inventory Obsolescence Expense',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"reason": "obsolete"}),
                'priority': 2
            },
            {
                'event_type': 'inventory_writeoff',
                'event_description': 'Inventory write-off for expired items',
                'debit_account_name': 'Inventory Expiry Expense',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"reason": "expired"}),
                'priority': 3
            },
            {
                'event_type': 'inventory_writeoff',
                'event_description': 'General inventory loss',
                'debit_account_name': 'Inventory Loss Expense',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"reason": "other"}),
                'priority': 4
            },
            
            # Inventory Revaluations
            {
                'event_type': 'inventory_revaluation',
                'event_description': 'Positive inventory revaluation (cost increase)',
                'debit_account_name': 'Inventory',
                'credit_account_name': 'Inventory Revaluation Gain',
                'conditions': json.dumps({"revaluation_type": "gain"}),
                'priority': 1
            },
            {
                'event_type': 'inventory_revaluation',
                'event_description': 'Negative inventory revaluation (cost decrease)',
                'debit_account_name': 'Inventory Revaluation Loss',
                'credit_account_name': 'Inventory',
                'conditions': json.dumps({"revaluation_type": "loss"}),
                'priority': 2
            },
            
            # Inventory Transfers (with cost changes)
            {
                'event_type': 'inventory_transfer',
                'event_description': 'Inventory transfer with cost adjustment',
                'debit_account_name': 'Inventory',
                'credit_account_name': 'Inventory Revaluation',
                'conditions': json.dumps({"cost_change": True}),
                'priority': 1
            }
        ]
        
        # Insert inventory posting rules
        rules_added = 0
        for rule in inventory_rules:
            try:
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
                    'SYSTEM',
                    datetime.now()
                ))
                rules_added += 1
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"   ⚠️  Rule already exists: {rule['event_type']} (priority {rule['priority']})")
                else:
                    print(f"   ❌ Error adding rule: {e}")
        
        # Also ensure we have the necessary Chart of Accounts entries
        print("\n🔧 Ensuring inventory-related accounts exist...")
        
        inventory_accounts = [
            ('1300', 'Inventory', 'Asset', 'Current Assets'),
            ('1350', 'GR/IR Clearing', 'Asset', 'Current Assets'),
            ('5100', 'Cost of Goods Sold', 'Expense', 'Cost of Sales'),
            ('6100', 'Inventory Adjustment Expense', 'Expense', 'Operating Expenses'),
            ('6110', 'Inventory Damage Expense', 'Expense', 'Operating Expenses'),
            ('6120', 'Inventory Obsolescence Expense', 'Expense', 'Operating Expenses'),
            ('6130', 'Inventory Expiry Expense', 'Expense', 'Operating Expenses'),
            ('6140', 'Inventory Loss Expense', 'Expense', 'Operating Expenses'),
            ('6150', 'Inventory Revaluation Loss', 'Expense', 'Operating Expenses'),
            ('4200', 'Inventory Adjustment Income', 'Revenue', 'Other Income'),
            ('4210', 'Inventory Revaluation Gain', 'Revenue', 'Other Income'),
        ]
        
        accounts_added = 0
        for code, name, type_, category in inventory_accounts:
            try:
                cursor.execute("SELECT COUNT(*) FROM advanced_chart_of_accounts WHERE account_code = ?", (code,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO advanced_chart_of_accounts 
                        (account_code, account_name, account_type, account_category, is_active, created_at)
                        VALUES (?, ?, ?, ?, 1, ?)
                    """, (code, name, type_, category, datetime.now()))
                    accounts_added += 1
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  Could not add account {name}: {e}")
        
        connection.commit()
        
        # Get final counts
        cursor.execute("SELECT COUNT(*) FROM posting_rules WHERE event_type LIKE '%inventory%'")
        total_inventory_rules = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM advanced_chart_of_accounts WHERE account_name LIKE '%inventory%' OR account_name LIKE '%cogs%'")
        total_inventory_accounts = cursor.fetchone()[0]
        
        print(f"\n✅ Migration completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Inventory posting rules added: {rules_added}")
        print(f"   • Total inventory rules: {total_inventory_rules}")
        print(f"   • Inventory accounts added: {accounts_added}")
        print(f"   • Total inventory accounts: {total_inventory_accounts}")
        print("🚀 Inventory-Finance Integration Ready!")
        
        # Show rule summary
        print(f"\n📋 Inventory Posting Rules:")
        cursor.execute("""
            SELECT event_type, COUNT(*) as rule_count 
            FROM posting_rules 
            WHERE event_type LIKE '%inventory%' 
            GROUP BY event_type 
            ORDER BY event_type
        """)
        
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

