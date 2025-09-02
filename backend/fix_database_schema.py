#!/usr/bin/env python3
"""
Fix Database Schema
Recreates the database tables with the correct structure including product_id field
"""

import os
import sqlite3
from datetime import datetime

def backup_existing_data():
    """Backup existing data before recreating tables"""
    if os.path.exists('edonuops.db'):
        backup_name = f'edonuops_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            import shutil
            shutil.copy2('edonuops.db', backup_name)
            print(f"✅ Database backed up to {backup_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to backup database: {e}")
            return False
    return True

def recreate_database():
    """Recreate the database with correct schema"""
    try:
        # Remove existing database
        if os.path.exists('edonuops.db'):
            os.remove('edonuops.db')
            print("🗑️ Removed existing database")
        
        # Create new database
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        # Create advanced_products table with product_id field
        cursor.execute('''
            CREATE TABLE advanced_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku VARCHAR(50) UNIQUE,
                product_id VARCHAR(50) UNIQUE,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category_id INTEGER,
                product_type VARCHAR(20) DEFAULT 'standard',
                track_serial_numbers BOOLEAN DEFAULT 0,
                track_lots BOOLEAN DEFAULT 0,
                track_expiry BOOLEAN DEFAULT 0,
                base_uom_id INTEGER NOT NULL,
                purchase_uom_id INTEGER,
                sales_uom_id INTEGER,
                cost_method VARCHAR(20) DEFAULT 'FIFO',
                standard_cost FLOAT DEFAULT 0.0,
                current_cost FLOAT DEFAULT 0.0,
                min_stock FLOAT DEFAULT 0.0,
                max_stock FLOAT DEFAULT 0.0,
                reorder_point FLOAT DEFAULT 0.0,
                reorder_quantity FLOAT DEFAULT 0.0,
                lead_time_days INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create advanced_product_categories table
        cursor.execute('''
            CREATE TABLE advanced_product_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                parent_id INTEGER,
                abc_class VARCHAR(10),
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create advanced_uom table
        cursor.execute('''
            CREATE TABLE advanced_uom (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                is_base_unit BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default categories
        cursor.execute('''
            INSERT INTO advanced_product_categories (name, description, abc_class) VALUES
            ('Electronics', 'Electronic devices and components', 'A'),
            ('Clothing', 'Apparel and fashion items', 'B'),
            ('Home & Garden', 'Home improvement and garden supplies', 'B'),
            ('Automotive', 'Automotive parts and accessories', 'C'),
            ('Books & Media', 'Books, movies, and media', 'C')
        ''')
        
        # Insert default UoM
        cursor.execute('''
            INSERT INTO advanced_uom (code, name, description, is_base_unit) VALUES
            ('PCS', 'Pieces', 'Individual units', 1),
            ('KG', 'Kilograms', 'Weight in kilograms', 0),
            ('M', 'Meters', 'Length in meters', 0),
            ('L', 'Liters', 'Volume in liters', 0),
            ('BOX', 'Boxes', 'Packaged in boxes', 0),
            ('PACK', 'Packs', 'Items in packs', 0),
            ('SET', 'Sets', 'Items sold as sets', 0)
        ''')
        
        # Insert some sample products
        cursor.execute('''
            INSERT INTO advanced_products (sku, product_id, name, description, category_id, base_uom_id, min_stock, max_stock, current_cost) VALUES
            ('LAPTOP001', 'PID001', 'Gaming Laptop', 'High-performance gaming laptop', 1, 1, 5, 50, 1200.00),
            ('MOUSE002', 'PID002', 'Wireless Mouse', 'Ergonomic wireless mouse', 1, 1, 10, 100, 25.50),
            ('TSHIRT003', 'PID003', 'Cotton T-Shirt', 'Comfortable cotton t-shirt', 2, 1, 20, 200, 15.00),
            ('BOOK004', 'PID004', 'Programming Guide', 'Complete programming guide', 5, 1, 3, 30, 45.00),
            ('TOOL005', 'PID005', 'Screwdriver Set', 'Professional screwdriver set', 3, 6, 8, 80, 35.75)
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database recreated successfully with correct schema")
        print("✅ Default categories, UoM, and sample products added")
        return True
        
    except Exception as e:
        print(f"❌ Failed to recreate database: {e}")
        return False

def main():
    """Main function to fix database schema"""
    print("🔧 Fixing Database Schema")
    print("=" * 40)
    
    # Backup existing data
    if not backup_existing_data():
        print("⚠️ Proceeding without backup...")
    
    # Recreate database
    if recreate_database():
        print("\n🎉 Database schema fixed successfully!")
        print("✅ All tables created with correct structure")
        print("✅ product_id field added to advanced_products table")
        print("✅ Sample data inserted for testing")
    else:
        print("\n❌ Failed to fix database schema")

if __name__ == "__main__":
    main()

