#!/usr/bin/env python3
"""
Migration: Create Inventory Daily Cycle Tables
Date: September 18, 2025
Purpose: Create tables for daily inventory opening/closing cycles
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Create inventory daily cycle tables"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'edonuops.db')
    
    print(f"🔄 Running migration: Create Inventory Daily Cycle Tables")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # 1. Create daily_inventory_balances table
        print("📋 Creating daily_inventory_balances table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_inventory_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_date DATE NOT NULL,
                product_id INTEGER NOT NULL,
                variant_id INTEGER,
                simple_warehouse_id INTEGER,
                basic_location_id INTEGER,
                advanced_location_id INTEGER,
                lot_batch_id INTEGER,
                opening_quantity REAL DEFAULT 0.0,
                opening_unit_cost REAL DEFAULT 0.0,
                opening_total_value REAL DEFAULT 0.0,
                closing_quantity REAL DEFAULT 0.0,
                closing_unit_cost REAL DEFAULT 0.0,
                closing_total_value REAL DEFAULT 0.0,
                quantity_received REAL DEFAULT 0.0,
                quantity_issued REAL DEFAULT 0.0,
                quantity_transferred_in REAL DEFAULT 0.0,
                quantity_transferred_out REAL DEFAULT 0.0,
                quantity_adjusted REAL DEFAULT 0.0,
                value_received REAL DEFAULT 0.0,
                value_issued REAL DEFAULT 0.0,
                value_transferred_in REAL DEFAULT 0.0,
                value_transferred_out REAL DEFAULT 0.0,
                value_adjusted REAL DEFAULT 0.0,
                net_quantity_change REAL DEFAULT 0.0,
                net_value_change REAL DEFAULT 0.0,
                cost_method VARCHAR(20) DEFAULT 'FIFO',
                currency VARCHAR(3) DEFAULT 'USD',
                exchange_rate REAL DEFAULT 1.0,
                base_currency_opening_value REAL DEFAULT 0.0,
                base_currency_closing_value REAL DEFAULT 0.0,
                is_locked BOOLEAN DEFAULT 0,
                locked_at DATETIME,
                locked_by VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100),
                FOREIGN KEY (product_id) REFERENCES inventory_products (id),
                FOREIGN KEY (variant_id) REFERENCES inventory_product_variants (id),
                FOREIGN KEY (simple_warehouse_id) REFERENCES inventory_simple_warehouses (id)
            )
        """)
        
        # 2. Create daily_inventory_cycle_status table
        print("📋 Creating daily_inventory_cycle_status table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_inventory_cycle_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_date DATE NOT NULL UNIQUE,
                opening_status VARCHAR(20) DEFAULT 'pending',
                opening_started_at DATETIME,
                opening_completed_at DATETIME,
                opening_started_by VARCHAR(100),
                opening_records_count INTEGER DEFAULT 0,
                closing_status VARCHAR(20) DEFAULT 'pending',
                closing_started_at DATETIME,
                closing_completed_at DATETIME,
                closing_started_by VARCHAR(100),
                closing_records_count INTEGER DEFAULT 0,
                total_products_processed INTEGER DEFAULT 0,
                total_locations_processed INTEGER DEFAULT 0,
                total_inventory_value REAL DEFAULT 0.0,
                total_quantity_on_hand REAL DEFAULT 0.0,
                error_message TEXT,
                error_count INTEGER DEFAULT 0,
                grace_period_end DATETIME,
                is_locked BOOLEAN DEFAULT 0,
                locked_at DATETIME,
                locked_by VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Create daily_inventory_transaction_summaries table
        print("📋 Creating daily_inventory_transaction_summaries table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_inventory_transaction_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary_date DATE NOT NULL,
                product_id INTEGER NOT NULL,
                variant_id INTEGER,
                simple_warehouse_id INTEGER,
                basic_location_id INTEGER,
                advanced_location_id INTEGER,
                receipts_count INTEGER DEFAULT 0,
                issues_count INTEGER DEFAULT 0,
                transfers_in_count INTEGER DEFAULT 0,
                transfers_out_count INTEGER DEFAULT 0,
                adjustments_count INTEGER DEFAULT 0,
                cycle_counts_count INTEGER DEFAULT 0,
                receipts_quantity REAL DEFAULT 0.0,
                issues_quantity REAL DEFAULT 0.0,
                transfers_in_quantity REAL DEFAULT 0.0,
                transfers_out_quantity REAL DEFAULT 0.0,
                adjustments_quantity REAL DEFAULT 0.0,
                cycle_counts_quantity REAL DEFAULT 0.0,
                receipts_value REAL DEFAULT 0.0,
                issues_value REAL DEFAULT 0.0,
                transfers_in_value REAL DEFAULT 0.0,
                transfers_out_value REAL DEFAULT 0.0,
                adjustments_value REAL DEFAULT 0.0,
                cycle_counts_value REAL DEFAULT 0.0,
                total_transactions INTEGER DEFAULT 0,
                net_quantity_change REAL DEFAULT 0.0,
                net_value_change REAL DEFAULT 0.0,
                average_unit_cost REAL DEFAULT 0.0,
                cost_method VARCHAR(20) DEFAULT 'FIFO',
                currency VARCHAR(3) DEFAULT 'USD',
                exchange_rate REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES inventory_products (id),
                FOREIGN KEY (variant_id) REFERENCES inventory_product_variants (id),
                FOREIGN KEY (simple_warehouse_id) REFERENCES inventory_simple_warehouses (id)
            )
        """)
        
        # 4. Create inventory_adjustment_entries table
        print("📋 Creating inventory_adjustment_entries table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_adjustment_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_date DATE NOT NULL,
                product_id INTEGER NOT NULL,
                simple_warehouse_id INTEGER,
                lot_batch_id INTEGER,
                adjustment_type VARCHAR(50) NOT NULL,
                reason_code VARCHAR(20),
                system_quantity REAL NOT NULL,
                physical_quantity REAL NOT NULL,
                adjustment_quantity REAL NOT NULL,
                system_unit_cost REAL DEFAULT 0.0,
                adjusted_unit_cost REAL DEFAULT 0.0,
                adjustment_value REAL DEFAULT 0.0,
                status VARCHAR(20) DEFAULT 'pending',
                requires_approval BOOLEAN DEFAULT 1,
                approved_by VARCHAR(100),
                approved_at DATETIME,
                approval_threshold_exceeded BOOLEAN DEFAULT 0,
                notes TEXT,
                reference_document VARCHAR(100),
                supporting_documents TEXT,
                created_by VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                journal_entry_id VARCHAR(50),
                FOREIGN KEY (product_id) REFERENCES inventory_products (id),
                FOREIGN KEY (simple_warehouse_id) REFERENCES inventory_simple_warehouses (id)
            )
        """)
        
        # 5. Create daily_inventory_cycle_audit_logs table
        print("📋 Creating daily_inventory_cycle_audit_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_inventory_cycle_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_date DATE NOT NULL,
                operation VARCHAR(50) NOT NULL,
                operation_status VARCHAR(20) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                user_name VARCHAR(100),
                user_role VARCHAR(50),
                ip_address VARCHAR(45),
                user_agent TEXT,
                records_processed INTEGER DEFAULT 0,
                records_created INTEGER DEFAULT 0,
                records_updated INTEGER DEFAULT 0,
                errors_encountered INTEGER DEFAULT 0,
                processing_time_seconds REAL DEFAULT 0.0,
                memory_usage_mb REAL DEFAULT 0.0,
                operation_details TEXT,
                error_details TEXT,
                started_at DATETIME NOT NULL,
                completed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 6. Create indexes for performance
        print("📋 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_daily_inv_bal_date_product ON daily_inventory_balances(cycle_date, product_id)",
            "CREATE INDEX IF NOT EXISTS idx_daily_inv_bal_date_location ON daily_inventory_balances(cycle_date, simple_warehouse_id)",
            "CREATE INDEX IF NOT EXISTS idx_daily_inv_cycle_date ON daily_inventory_cycle_status(cycle_date)",
            "CREATE INDEX IF NOT EXISTS idx_daily_inv_summary_date_product ON daily_inventory_transaction_summaries(summary_date, product_id)",
            "CREATE INDEX IF NOT EXISTS idx_daily_inv_summary_date_location ON daily_inventory_transaction_summaries(summary_date, simple_warehouse_id)",
            "CREATE INDEX IF NOT EXISTS idx_inv_adjustments_date ON inventory_adjustment_entries(cycle_date)",
            "CREATE INDEX IF NOT EXISTS idx_inv_audit_date_operation ON daily_inventory_cycle_audit_logs(cycle_date, operation)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        connection.commit()
        print("✅ Migration completed successfully!")
        
        # Show summary
        tables_created = [
            'daily_inventory_balances',
            'daily_inventory_cycle_status', 
            'daily_inventory_transaction_summaries',
            'inventory_adjustment_entries',
            'daily_inventory_cycle_audit_logs'
        ]
        
        print(f"📊 Created {len(tables_created)} tables for inventory daily cycles:")
        for table in tables_created:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} records")
        
        print("🚀 Inventory Daily Cycle System Ready!")
        
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

