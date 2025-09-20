#!/usr/bin/env python3
"""
Migration: Clean All Dummy Data
Date: September 18, 2025
Purpose: Remove all sample/dummy data from the system for production
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Remove all dummy/sample data from the database"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'erp_system.db')
    
    print(f"🔄 Running migration: Clean All Dummy Data")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # List of tables to clean (preserve structure, remove data)
        tables_to_clean = [
            # Finance
            'advanced_general_ledger_entries',
            'journal_entries',
            'journal_lines',
            'accounts',
            'invoices',
            'invoice_line_items',
            'payments',
            'advanced_accounts_payable',
            'advanced_accounts_receivable',
            'advanced_ap_payments',
            'advanced_ar_payments',
            
            # Sales
            'customers',
            'invoices',
            'payments',
            'customer_communications',
            
            # Procurement
            'vendors',
            'purchase_orders',
            'purchase_order_lines',
            'receipts',
            
            # Inventory
            'inventory_items',
            'inventory_transactions',
            'inventory_categories',
            'warehouses',
            'stock_levels',
            
            # CRM
            'contacts',
            'leads',
            'opportunities',
            'activities',
            'tickets',
            
            # Daily Cycle
            'daily_balances',
            'daily_transaction_summaries',
            'daily_cycle_status',
            
            # Other transactional data
            'audit_logs',
            'notifications',
            'user_sessions',
        ]
        
        # Tables to preserve (configuration/master data)
        preserve_tables = [
            'posting_rules',  # Keep our posting rules
            'advanced_chart_of_accounts',  # Keep chart of accounts structure
            'users',  # Keep user accounts
            'roles',
            'permissions',
            'company_settings',
            'currencies',
            'exchange_rates',
            'tax_rates'
        ]
        
        cleaned_count = 0
        total_records_removed = 0
        
        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found {len(all_tables)} tables in database")
        
        for table in all_tables:
            # Skip system tables
            if table.startswith('sqlite_'):
                continue
                
            # Check if table exists and has data
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                record_count = cursor.fetchone()[0]
                
                if record_count > 0:
                    if table in preserve_tables:
                        print(f"🔒 Preserving {table}: {record_count} records")
                    else:
                        # Clean the table
                        cursor.execute(f"DELETE FROM {table}")
                        print(f"🗑️  Cleaned {table}: removed {record_count} records")
                        cleaned_count += 1
                        total_records_removed += record_count
                else:
                    print(f"⚪ {table}: already empty")
                    
            except sqlite3.OperationalError as e:
                print(f"⚠️  Could not clean {table}: {e}")
        
        # Reset auto-increment counters for cleaned tables
        print("\n🔄 Resetting auto-increment counters...")
        for table in all_tables:
            if table not in preserve_tables and not table.startswith('sqlite_'):
                try:
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
                except sqlite3.OperationalError:
                    pass  # Table might not have auto-increment
        
        # Create a clean system status record
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO company_settings 
                (setting_key, setting_value, setting_type, description, created_at)
                VALUES 
                ('system_status', 'production_ready', 'string', 'System cleaned and ready for production', ?)
            """, (datetime.now(),))
        except sqlite3.OperationalError:
            pass  # Table might not exist
        
        connection.commit()
        
        print(f"\n✅ Migration completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Tables cleaned: {cleaned_count}")
        print(f"   • Total records removed: {total_records_removed}")
        print(f"   • Configuration preserved: {len(preserve_tables)} tables")
        print(f"   • System status: PRODUCTION READY 🚀")
        
        # Verify key tables are empty
        print(f"\n🔍 Verification - Key tables status:")
        key_tables = ['advanced_general_ledger_entries', 'customers', 'vendors', 'inventory_items']
        for table in key_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                status = "✅ CLEAN" if count == 0 else f"⚠️  {count} records"
                print(f"   • {table}: {status}")
            except sqlite3.OperationalError:
                print(f"   • {table}: ❓ Table not found")
        
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

