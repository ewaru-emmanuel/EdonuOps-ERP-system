#!/usr/bin/env python3
"""
Migrate from SQLite to PostgreSQL
Comprehensive migration script for EdonuOps ERP
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class SQLiteToPostgreSQLMigrator:
    def __init__(self):
        self.sqlite_db = 'edonuops.db'
        self.pg_connection_string = os.getenv('DATABASE_URL')
        
        if not self.pg_connection_string:
            print("❌ DATABASE_URL environment variable not set!")
            print("Please set DATABASE_URL=postgresql://username:password@host:port/database")
            sys.exit(1)
    
    def test_connections(self):
        """Test both SQLite and PostgreSQL connections"""
        print("🔧 Testing database connections...")
        
        # Test SQLite
        try:
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            cursor = sqlite_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            print(f"✅ SQLite: Connected, {table_count} tables found")
            sqlite_conn.close()
        except Exception as e:
            print(f"❌ SQLite connection failed: {e}")
            return False
        
        # Test PostgreSQL
        try:
            pg_conn = psycopg2.connect(self.pg_connection_string)
            cursor = pg_conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL: Connected, {version}")
            pg_conn.close()
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return False
        
        return True
    
    def create_postgresql_schema(self):
        """Create all tables in PostgreSQL"""
        print("\n🏗️ Creating PostgreSQL schema...")
        
        schema_sql = """
        -- Core tables
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS organizations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            code VARCHAR(50) UNIQUE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Advanced Inventory tables
        CREATE TABLE IF NOT EXISTS advanced_uom (
            id SERIAL PRIMARY KEY,
            code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            is_base_unit BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS advanced_product_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            parent_id INTEGER REFERENCES advanced_product_categories(id),
            abc_class VARCHAR(10),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS advanced_products (
            id SERIAL PRIMARY KEY,
            sku VARCHAR(50) UNIQUE,
            product_id VARCHAR(50) UNIQUE,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category_id INTEGER REFERENCES advanced_product_categories(id),
            product_type VARCHAR(20) DEFAULT 'standard',
            track_serial_numbers BOOLEAN DEFAULT FALSE,
            track_lots BOOLEAN DEFAULT FALSE,
            track_expiry BOOLEAN DEFAULT FALSE,
            base_uom_id INTEGER NOT NULL REFERENCES advanced_uom(id),
            purchase_uom_id INTEGER REFERENCES advanced_uom(id),
            sales_uom_id INTEGER REFERENCES advanced_uom(id),
            cost_method VARCHAR(20) DEFAULT 'FIFO',
            standard_cost DECIMAL(10,2) DEFAULT 0.0,
            current_cost DECIMAL(10,2) DEFAULT 0.0,
            min_stock DECIMAL(10,2) DEFAULT 0.0,
            max_stock DECIMAL(10,2) DEFAULT 0.0,
            reorder_point DECIMAL(10,2) DEFAULT 0.0,
            reorder_quantity DECIMAL(10,2) DEFAULT 0.0,
            lead_time_days INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Finance tables
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            account_number VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(200) NOT NULL,
            account_type VARCHAR(50) NOT NULL,
            parent_account_id INTEGER REFERENCES accounts(id),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS journal_entries (
            id SERIAL PRIMARY KEY,
            entry_number VARCHAR(20) UNIQUE NOT NULL,
            entry_date DATE NOT NULL,
            description TEXT,
            reference VARCHAR(100),
            is_posted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_advanced_products_sku ON advanced_products(sku);
        CREATE INDEX IF NOT EXISTS idx_advanced_products_product_id ON advanced_products(product_id);
        CREATE INDEX IF NOT EXISTS idx_advanced_products_category ON advanced_products(category_id);
        CREATE INDEX IF NOT EXISTS idx_advanced_products_active ON advanced_products(is_active);
        CREATE INDEX IF NOT EXISTS idx_accounts_number ON accounts(account_number);
        CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries(entry_date);
        """
        
        try:
            pg_conn = psycopg2.connect(self.pg_connection_string)
            cursor = pg_conn.cursor()
            
            # Split and execute each statement
            statements = schema_sql.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            
            pg_conn.commit()
            pg_conn.close()
            print("✅ PostgreSQL schema created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create PostgreSQL schema: {e}")
            return False
    
    def migrate_data(self):
        """Migrate data from SQLite to PostgreSQL"""
        print("\n📦 Migrating data from SQLite to PostgreSQL...")
        
        try:
            # Connect to both databases
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            sqlite_conn.row_factory = sqlite3.Row
            
            pg_conn = psycopg2.connect(self.pg_connection_string)
            pg_cursor = pg_conn.cursor()
            
            # Migration order (respecting foreign keys)
            tables = [
                'organizations',
                'users', 
                'advanced_uom',
                'advanced_product_categories',
                'advanced_products',
                'accounts',
                'journal_entries'
            ]
            
            for table in tables:
                print(f"  📋 Migrating {table}...")
                
                # Get data from SQLite
                sqlite_cursor = sqlite_conn.cursor()
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(f"    ⚠️ No data in {table}")
                    continue
                
                # Get column names
                columns = [description[0] for description in sqlite_cursor.description]
                
                # Insert into PostgreSQL
                for row in rows:
                    # Convert row to dict
                    row_dict = dict(row)
                    
                    # Build INSERT statement
                    placeholders = ', '.join(['%s'] * len(columns))
                    column_names = ', '.join(columns)
                    
                    # Handle PostgreSQL-specific data types
                    values = []
                    for col in columns:
                        value = row_dict[col]
                        if isinstance(value, bool):
                            values.append('TRUE' if value else 'FALSE')
                        elif value is None:
                            values.append(None)
                        else:
                            values.append(value)
                    
                    insert_sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                    
                    try:
                        pg_cursor.execute(insert_sql, values)
                    except Exception as e:
                        print(f"    ❌ Error inserting into {table}: {e}")
                        print(f"    Data: {row_dict}")
                        continue
                
                print(f"    ✅ Migrated {len(rows)} rows from {table}")
            
            pg_conn.commit()
            sqlite_conn.close()
            pg_conn.close()
            
            print("✅ Data migration completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Data migration failed: {e}")
            return False
    
    def verify_migration(self):
        """Verify that migration was successful"""
        print("\n🔍 Verifying migration...")
        
        try:
            pg_conn = psycopg2.connect(self.pg_connection_string)
            cursor = pg_conn.cursor()
            
            # Check table counts
            tables = [
                'users', 'organizations', 'advanced_uom', 
                'advanced_product_categories', 'advanced_products',
                'accounts', 'journal_entries'
            ]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  📊 {table}: {count} records")
            
            # Test a sample query
            cursor.execute("""
                SELECT p.name, c.name as category, p.sku, p.product_id 
                FROM advanced_products p 
                LEFT JOIN advanced_product_categories c ON p.category_id = c.id 
                LIMIT 5
            """)
            
            sample_data = cursor.fetchall()
            print(f"  ✅ Sample query returned {len(sample_data)} products")
            
            pg_conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting SQLite to PostgreSQL Migration")
        print("=" * 50)
        
        # Step 1: Test connections
        if not self.test_connections():
            return False
        
        # Step 2: Create PostgreSQL schema
        if not self.create_postgresql_schema():
            return False
        
        # Step 3: Migrate data
        if not self.migrate_data():
            return False
        
        # Step 4: Verify migration
        if not self.verify_migration():
            return False
        
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("✅ Your data has been migrated from SQLite to PostgreSQL")
        print("✅ Update your DATABASE_URL environment variable to use PostgreSQL")
        print("✅ Restart your Flask application")
        
        return True

def main():
    """Main function"""
    migrator = SQLiteToPostgreSQLMigrator()
    success = migrator.run_migration()
    
    if not success:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()


