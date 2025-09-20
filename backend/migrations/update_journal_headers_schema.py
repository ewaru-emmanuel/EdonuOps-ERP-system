#!/usr/bin/env python3
"""
Migration: Update Journal Headers Schema
Date: September 18, 2025
Purpose: Add missing columns to advanced_journal_headers table
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Update advanced_journal_headers table with missing columns"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'erp_system.db')
    
    print(f"🔄 Running migration: Update Journal Headers Schema")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Check which columns exist
        cursor.execute("PRAGMA table_info(advanced_journal_headers)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Existing columns: {existing_columns}")
        
        # Define new columns to add
        new_columns = [
            ("source_module", "VARCHAR(50)", "Finance"),
            ("source_document_type", "VARCHAR(50)", ""),
            ("reference_id", "VARCHAR(50)", ""),
            ("posting_date", "DATE", "CURRENT_DATE"),
            ("document_date", "DATE", "CURRENT_DATE"),
            ("fiscal_period", "VARCHAR(10)", "2025-09"),
            ("currency", "VARCHAR(3)", "USD"),
            ("exchange_rate", "REAL", "1.0"),
            ("posting_status", "VARCHAR(20)", "posted"),
            ("approval_status", "VARCHAR(20)", "pending"),
            ("posted_by", "VARCHAR(100)", ""),
            ("approved_by", "VARCHAR(100)", ""),
            ("reversed_by", "VARCHAR(100)", ""),
            ("posted_at", "DATETIME", ""),
            ("approved_at", "DATETIME", ""),
            ("reversed_at", "DATETIME", ""),
            ("audit_trail", "TEXT", ""),
            ("reversal_reason", "TEXT", ""),
            ("reversal_journal_id", "INTEGER", "")
        ]
        
        # Add missing columns
        columns_added = 0
        for column_name, column_type, default_value in new_columns:
            if column_name not in existing_columns:
                try:
                    if default_value and default_value not in ["", "CURRENT_DATE"]:
                        cursor.execute(f"""
                            ALTER TABLE advanced_journal_headers 
                            ADD COLUMN {column_name} {column_type} DEFAULT '{default_value}'
                        """)
                    else:
                        cursor.execute(f"""
                            ALTER TABLE advanced_journal_headers 
                            ADD COLUMN {column_name} {column_type}
                        """)
                    print(f"✅ Added column: {column_name}")
                    columns_added += 1
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️  Error adding column {column_name}: {e}")
        
        # Update existing records with default values
        if columns_added > 0:
            print("📋 Updating existing records with default values...")
            
            # Update records that have NULL values in new columns
            update_queries = [
                "UPDATE advanced_journal_headers SET source_module = 'Finance' WHERE source_module IS NULL",
                "UPDATE advanced_journal_headers SET posting_date = date('now') WHERE posting_date IS NULL",
                "UPDATE advanced_journal_headers SET document_date = date('now') WHERE document_date IS NULL",
                "UPDATE advanced_journal_headers SET fiscal_period = strftime('%Y-%m', 'now') WHERE fiscal_period IS NULL",
                "UPDATE advanced_journal_headers SET currency = 'USD' WHERE currency IS NULL",
                "UPDATE advanced_journal_headers SET exchange_rate = 1.0 WHERE exchange_rate IS NULL",
                "UPDATE advanced_journal_headers SET posting_status = 'posted' WHERE posting_status IS NULL",
                "UPDATE advanced_journal_headers SET approval_status = 'pending' WHERE approval_status IS NULL"
            ]
            
            for query in update_queries:
                try:
                    cursor.execute(query)
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Update query failed: {e}")
        
        connection.commit()
        print(f"✅ Migration completed successfully! Added {columns_added} columns")
        
        # Show final table structure
        cursor.execute("PRAGMA table_info(advanced_journal_headers)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"📊 Final columns: {len(final_columns)} total")
        
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

