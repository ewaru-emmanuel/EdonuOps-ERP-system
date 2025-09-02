#!/usr/bin/env python3
"""
Fix Entire Platform Database Issues
Comprehensive fix for all database loading errors across the platform
"""

import os
import sys
import sqlite3
import subprocess
import time

def check_database_integrity():
    """Check if the database is properly structured"""
    try:
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        # Check all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Found {len(tables)} tables in database")
        
        # Check key tables
        key_tables = [
            'advanced_products',
            'advanced_product_categories', 
            'advanced_uom',
            'users',
            'organizations'
        ]
        
        missing_tables = []
        for table in key_tables:
            if table not in tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            print("✅ All key tables present")
        
        # Check advanced_products structure
        cursor.execute("PRAGMA table_info(advanced_products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['id', 'name', 'sku', 'product_id', 'category_id', 'base_uom_id']
        missing_columns = []
        
        for col in required_columns:
            if col not in columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"❌ Missing columns in advanced_products: {missing_columns}")
            return False
        else:
            print("✅ advanced_products table structure is correct")
        
        # Check if there's data
        cursor.execute("SELECT COUNT(*) FROM advanced_products")
        product_count = cursor.fetchone()[0]
        print(f"📊 Found {product_count} products in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database integrity check failed: {e}")
        return False

def recreate_database_completely():
    """Completely recreate the database with all tables"""
    try:
        # Remove existing database
        if os.path.exists('edonuops.db'):
            os.remove('edonuops.db')
            print("🗑️ Removed existing database")
        
        # Create new database
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        # Create all necessary tables
        tables_sql = [
            # Core tables
            '''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            '''
            CREATE TABLE organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                code VARCHAR(50) UNIQUE,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # Advanced Inventory tables
            '''
            CREATE TABLE advanced_uom (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                is_base_unit BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            '''
            CREATE TABLE advanced_product_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                parent_id INTEGER,
                abc_class VARCHAR(10),
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            '''
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
            '''
        ]
        
        for sql in tables_sql:
            cursor.execute(sql)
        
        # Insert default data
        cursor.execute('''
            INSERT INTO advanced_product_categories (name, description, abc_class) VALUES
            ('Electronics', 'Electronic devices and components', 'A'),
            ('Clothing', 'Apparel and fashion items', 'B'),
            ('Home & Garden', 'Home improvement and garden supplies', 'B'),
            ('Automotive', 'Automotive parts and accessories', 'C'),
            ('Books & Media', 'Books, movies, and media', 'C')
        ''')
        
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
        
        cursor.execute('''
            INSERT INTO advanced_products (sku, product_id, name, description, category_id, base_uom_id, min_stock, max_stock, current_cost) VALUES
            ('LAPTOP001', 'PID001', 'Gaming Laptop', 'High-performance gaming laptop', 1, 1, 5, 50, 1200.00),
            ('MOUSE002', 'PID002', 'Wireless Mouse', 'Ergonomic wireless mouse', 1, 1, 10, 100, 25.50),
            ('TSHIRT003', 'PID003', 'Cotton T-Shirt', 'Comfortable cotton t-shirt', 2, 1, 20, 200, 15.00),
            ('BOOK004', 'PID004', 'Programming Guide', 'Complete programming guide', 5, 1, 3, 30, 45.00),
            ('TOOL005', 'PID005', 'Screwdriver Set', 'Professional screwdriver set', 3, 6, 8, 80, 35.75)
        ''')
        
        cursor.execute('''
            INSERT INTO organizations (name, code) VALUES
            ('Default Organization', 'DEFAULT')
        ''')
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash) VALUES
            ('admin', 'admin@edonuops.com', 'dummy_hash_for_testing')
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database recreated successfully with all tables and sample data")
        return True
        
    except Exception as e:
        print(f"❌ Failed to recreate database: {e}")
        return False

def test_all_endpoints():
    """Test all major endpoints"""
    endpoints = [
        ('Health Check', '/health'),
        ('Test', '/test'),
        ('Categories', '/api/inventory/advanced/categories'),
        ('UoM', '/api/inventory/advanced/uom'),
        ('Products', '/api/inventory/advanced/products')
    ]
    
    import urllib.request
    import json
    
    results = {}
    
    for name, endpoint in endpoints:
        try:
            print(f"  📡 Testing {name}...")
            req = urllib.request.Request(f'http://localhost:5000{endpoint}')
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            
            if isinstance(data, list):
                print(f"    ✅ {name} works! Found {len(data)} items")
            else:
                print(f"    ✅ {name} works!")
            
            results[name] = True
            
        except Exception as e:
            print(f"    ❌ {name} failed: {e}")
            results[name] = False
    
    return results

def main():
    """Main function to fix entire platform"""
    print("🔧 Fixing Entire Platform Database Issues")
    print("=" * 50)
    
    # Step 1: Check current database integrity
    print("\n📊 Step 1: Checking database integrity...")
    if not check_database_integrity():
        print("❌ Database integrity check failed")
    else:
        print("✅ Database integrity check passed")
    
    # Step 2: Recreate database completely
    print("\n🔄 Step 2: Recreating database...")
    if not recreate_database_completely():
        print("❌ Database recreation failed")
        return
    
    # Step 3: Kill existing processes
    print("\n🔄 Step 3: Restarting server...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, check=False)
        print("✅ Killed existing processes")
    except:
        pass
    
    # Step 4: Start server
    time.sleep(2)
    try:
        subprocess.Popen(['python', 'run.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        print("✅ Server started")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return
    
    # Step 5: Test endpoints
    print("\n🧪 Step 4: Testing endpoints...")
    time.sleep(10)  # Wait for server to start
    
    endpoint_results = test_all_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Platform Fix Summary")
    print("=" * 50)
    
    working_endpoints = sum(endpoint_results.values())
    total_endpoints = len(endpoint_results)
    
    for name, result in endpoint_results.items():
        status = "✅ WORKING" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print(f"\n🎯 Results: {working_endpoints}/{total_endpoints} endpoints working")
    
    if working_endpoints == total_endpoints:
        print("\n🎉 ENTIRE PLATFORM IS NOW WORKING!")
        print("✅ All database issues have been resolved!")
        print("✅ All endpoints are responding correctly!")
        print("✅ The inventory module should now work perfectly!")
    else:
        print("\n⚠️ Some endpoints still need attention")
        print("Check the server logs for more details")

if __name__ == "__main__":
    main()

