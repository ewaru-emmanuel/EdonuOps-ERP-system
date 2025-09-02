#!/usr/bin/env python3
"""
Initialize All Database Tables
Creates all necessary tables for the entire platform
"""

import sqlite3
import os

def create_all_tables():
    """Create all necessary tables for the platform"""
    try:
        # Remove existing database if it exists
        if os.path.exists('edonuops.db'):
            os.remove('edonuops.db')
            print("🗑️ Removed existing database")
        
        # Create new database
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        print("🔧 Creating all database tables...")
        
        # Core tables
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Created users table")
        
        cursor.execute('''
            CREATE TABLE organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                code VARCHAR(50) UNIQUE,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Created organizations table")
        
        # Advanced Inventory tables
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
        print("✅ Created advanced_uom table")
        
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
        print("✅ Created advanced_product_categories table")
        
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
        print("✅ Created advanced_products table")
        
        # Finance tables
        cursor.execute('''
            CREATE TABLE accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                account_type VARCHAR(50) NOT NULL,
                parent_account_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Created accounts table")
        
        cursor.execute('''
            CREATE TABLE journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_number VARCHAR(20) UNIQUE NOT NULL,
                entry_date DATE NOT NULL,
                description TEXT,
                reference VARCHAR(100),
                is_posted BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Created journal_entries table")
        
        # Insert sample data
        print("\n📊 Inserting sample data...")
        
        # Categories
        cursor.execute('''
            INSERT INTO advanced_product_categories (name, description, abc_class) VALUES
            ('Electronics', 'Electronic devices and components', 'A'),
            ('Clothing', 'Apparel and fashion items', 'B'),
            ('Home & Garden', 'Home improvement and garden supplies', 'B'),
            ('Automotive', 'Automotive parts and accessories', 'C'),
            ('Books & Media', 'Books, movies, and media', 'C')
        ''')
        print("✅ Added sample categories")
        
        # UoM
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
        print("✅ Added sample UoM")
        
        # Products
        cursor.execute('''
            INSERT INTO advanced_products (sku, product_id, name, description, category_id, base_uom_id, min_stock, max_stock, current_cost) VALUES
            ('LAPTOP001', 'PID001', 'Gaming Laptop', 'High-performance gaming laptop', 1, 1, 5, 50, 1200.00),
            ('MOUSE002', 'PID002', 'Wireless Mouse', 'Ergonomic wireless mouse', 1, 1, 10, 100, 25.50),
            ('TSHIRT003', 'PID003', 'Cotton T-Shirt', 'Comfortable cotton t-shirt', 2, 1, 20, 200, 15.00),
            ('BOOK004', 'PID004', 'Programming Guide', 'Complete programming guide', 5, 1, 3, 30, 45.00),
            ('TOOL005', 'PID005', 'Screwdriver Set', 'Professional screwdriver set', 3, 6, 8, 80, 35.75)
        ''')
        print("✅ Added sample products")
        
        # Organizations
        cursor.execute('''
            INSERT INTO organizations (name, code) VALUES
            ('Default Organization', 'DEFAULT')
        ''')
        print("✅ Added default organization")
        
        # Users
        cursor.execute('''
            INSERT INTO users (username, email, password_hash) VALUES
            ('admin', 'admin@edonuops.com', 'dummy_hash_for_testing')
        ''')
        print("✅ Added admin user")
        
        # Finance accounts
        cursor.execute('''
            INSERT INTO accounts (account_number, name, account_type) VALUES
            ('1000', 'Cash', 'Asset'),
            ('1100', 'Accounts Receivable', 'Asset'),
            ('1200', 'Inventory', 'Asset'),
            ('2000', 'Accounts Payable', 'Liability'),
            ('3000', 'Equity', 'Equity'),
            ('4000', 'Revenue', 'Revenue'),
            ('5000', 'Cost of Goods Sold', 'Expense')
        ''')
        print("✅ Added sample accounts")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 All tables created successfully!")
        print("✅ Database is ready for use!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Initializing All Database Tables")
    print("=" * 40)
    create_all_tables()
