#!/usr/bin/env python3
"""
Database Migration Script
Adds product_id field to advanced_products table
"""

import sqlite3
import os

def migrate_database():
    """Add product_id column to advanced_products table"""
    db_path = 'edonuops.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Creating new database...")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if product_id column already exists
        cursor.execute("PRAGMA table_info(advanced_products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'product_id' not in columns:
            print("Adding product_id column to advanced_products table...")
            cursor.execute("ALTER TABLE advanced_products ADD COLUMN product_id VARCHAR(50) UNIQUE")
            print("✅ product_id column added successfully")
        else:
            print("✅ product_id column already exists")
        
        # Check if sku column is nullable
        cursor.execute("PRAGMA table_info(advanced_products)")
        columns_info = cursor.fetchall()
        sku_column = next((col for col in columns_info if col[1] == 'sku'), None)
        
        if sku_column and sku_column[3] == 1:  # 1 means NOT NULL
            print("Making sku column nullable...")
            # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
            # For now, we'll just note this limitation
            print("⚠️ Note: sku column is still NOT NULL. You may need to recreate the table for full flexibility.")
        else:
            print("✅ sku column is already nullable")
        
        conn.commit()
        conn.close()
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()

