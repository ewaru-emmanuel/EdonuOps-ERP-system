#!/usr/bin/env python3
"""
Quick Database Fix
Add missing product_id column to advanced_products table
"""

import sqlite3
import os

def fix_database():
    """Add missing product_id column to advanced_products table"""
    try:
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        # Check if product_id column exists
        cursor.execute("PRAGMA table_info(advanced_products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        if 'product_id' not in columns:
            print("Adding product_id column...")
            cursor.execute("ALTER TABLE advanced_products ADD COLUMN product_id VARCHAR(50) UNIQUE")
            print("✅ product_id column added successfully")
        else:
            print("✅ product_id column already exists")
        
        # Check if we have any data
        cursor.execute("SELECT COUNT(*) FROM advanced_products")
        count = cursor.fetchone()[0]
        print(f"📊 Found {count} products in database")
        
        # If no data, add some sample data
        if count == 0:
            print("Adding sample data...")
            
            # First add categories if they don't exist
            cursor.execute("SELECT COUNT(*) FROM advanced_product_categories")
            cat_count = cursor.fetchone()[0]
            
            if cat_count == 0:
                cursor.execute('''
                    INSERT INTO advanced_product_categories (name, description, abc_class) VALUES
                    ('Electronics', 'Electronic devices and components', 'A'),
                    ('Clothing', 'Apparel and fashion items', 'B'),
                    ('Home & Garden', 'Home improvement and garden supplies', 'B')
                ''')
                print("✅ Added sample categories")
            
            # Add UoM if they don't exist
            cursor.execute("SELECT COUNT(*) FROM advanced_uom")
            uom_count = cursor.fetchone()[0]
            
            if uom_count == 0:
                cursor.execute('''
                    INSERT INTO advanced_uom (code, name, description, is_base_unit) VALUES
                    ('PCS', 'Pieces', 'Individual units', 1),
                    ('KG', 'Kilograms', 'Weight in kilograms', 0),
                    ('BOX', 'Boxes', 'Packaged in boxes', 0)
                ''')
                print("✅ Added sample UoM")
            
            # Add sample products
            cursor.execute('''
                INSERT INTO advanced_products (sku, product_id, name, description, category_id, base_uom_id, min_stock, max_stock, current_cost) VALUES
                ('LAPTOP001', 'PID001', 'Gaming Laptop', 'High-performance gaming laptop', 1, 1, 5, 50, 1200.00),
                ('MOUSE002', 'PID002', 'Wireless Mouse', 'Ergonomic wireless mouse', 1, 1, 10, 100, 25.50),
                ('TSHIRT003', 'PID003', 'Cotton T-Shirt', 'Comfortable cotton t-shirt', 2, 1, 20, 200, 15.00)
            ''')
            print("✅ Added sample products")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Database fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Quick Database Fix")
    print("=" * 30)
    fix_database()

