#!/usr/bin/env python3
"""
Migration: Create Cost Layer Tables
Date: September 18, 2025
Purpose: Create tables for FIFO/LIFO cost layer management
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Create cost layer and variance reporting tables"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'edonuops.db')
    
    print(f"🔄 Running migration: Create Cost Layer Tables")
    print(f"📂 Database: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # 1. Create inventory_cost_layers table
        print("📋 Creating inventory_cost_layers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_cost_layers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                variant_id INTEGER,
                simple_warehouse_id INTEGER,
                lot_batch_id INTEGER,
                layer_sequence INTEGER NOT NULL,
                receipt_date DATE NOT NULL,
                receipt_reference VARCHAR(100),
                unit_cost REAL NOT NULL,
                original_quantity REAL NOT NULL,
                remaining_quantity REAL NOT NULL,
                total_cost REAL NOT NULL,
                remaining_cost REAL NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                exchange_rate REAL DEFAULT 1.0,
                base_currency_unit_cost REAL NOT NULL,
                base_currency_total_cost REAL NOT NULL,
                is_depleted BOOLEAN DEFAULT 0,
                depleted_date DATE,
                source_transaction_id INTEGER,
                source_document_type VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100),
                FOREIGN KEY (product_id) REFERENCES inventory_products (id)
            )
        """)
        
        # 2. Create cost_layer_transactions table
        print("📋 Creating cost_layer_transactions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_layer_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cost_layer_id INTEGER NOT NULL,
                transaction_date DATE NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                transaction_reference VARCHAR(100),
                quantity_depleted REAL NOT NULL,
                cost_depleted REAL NOT NULL,
                unit_cost_used REAL NOT NULL,
                journal_entry_id VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100),
                FOREIGN KEY (cost_layer_id) REFERENCES inventory_cost_layers (id)
            )
        """)
        
        # 3. Create inventory_valuation_snapshots table
        print("📋 Creating inventory_valuation_snapshots table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_valuation_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL,
                product_id INTEGER NOT NULL,
                variant_id INTEGER,
                simple_warehouse_id INTEGER,
                fifo_quantity REAL DEFAULT 0.0,
                fifo_unit_cost REAL DEFAULT 0.0,
                fifo_total_value REAL DEFAULT 0.0,
                lifo_quantity REAL DEFAULT 0.0,
                lifo_unit_cost REAL DEFAULT 0.0,
                lifo_total_value REAL DEFAULT 0.0,
                average_quantity REAL DEFAULT 0.0,
                average_unit_cost REAL DEFAULT 0.0,
                average_total_value REAL DEFAULT 0.0,
                standard_quantity REAL DEFAULT 0.0,
                standard_unit_cost REAL DEFAULT 0.0,
                standard_total_value REAL DEFAULT 0.0,
                active_cost_method VARCHAR(20) NOT NULL,
                active_quantity REAL DEFAULT 0.0,
                active_unit_cost REAL DEFAULT 0.0,
                active_total_value REAL DEFAULT 0.0,
                method_variance_fifo_vs_avg REAL DEFAULT 0.0,
                method_variance_lifo_vs_avg REAL DEFAULT 0.0,
                method_variance_std_vs_actual REAL DEFAULT 0.0,
                days_on_hand INTEGER DEFAULT 0,
                aging_category VARCHAR(20),
                last_movement_date DATE,
                currency VARCHAR(3) DEFAULT 'USD',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES inventory_products (id)
            )
        """)
        
        # 4. Create indexes for performance
        print("📋 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_cost_layers_product_date ON inventory_cost_layers(product_id, receipt_date)",
            "CREATE INDEX IF NOT EXISTS idx_cost_layers_fifo ON inventory_cost_layers(product_id, simple_warehouse_id, layer_sequence)",
            "CREATE INDEX IF NOT EXISTS idx_cost_layers_lifo ON inventory_cost_layers(product_id, simple_warehouse_id, receipt_date, layer_sequence)",
            "CREATE INDEX IF NOT EXISTS idx_cost_layer_txn_date ON cost_layer_transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_cost_layer_txn_layer ON cost_layer_transactions(cost_layer_id)",
            "CREATE INDEX IF NOT EXISTS idx_valuation_snapshot_date_product ON inventory_valuation_snapshots(snapshot_date, product_id)",
            "CREATE INDEX IF NOT EXISTS idx_valuation_snapshot_aging ON inventory_valuation_snapshots(aging_category, days_on_hand)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        connection.commit()
        print("✅ Migration completed successfully!")
        
        # Show summary
        tables_created = [
            'inventory_cost_layers',
            'cost_layer_transactions',
            'inventory_valuation_snapshots'
        ]
        
        print(f"📊 Created {len(tables_created)} tables for cost layer management:")
        for table in tables_created:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} records")
        
        print("🚀 FIFO/LIFO Cost Layer System Ready!")
        print("📊 Variance Reporting Tables Ready!")
        
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

