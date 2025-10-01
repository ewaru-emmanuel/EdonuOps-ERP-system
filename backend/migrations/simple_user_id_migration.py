#!/usr/bin/env python3
"""
Simple Multi-Tenancy Migration Script
Adds user_id column to all business tables for data isolation
"""

import sqlite3
import os

def get_database_connection():
    """Get database connection"""
    db_path = 'backend/edonuops.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_business_tables(conn):
    """Get all business tables that need user_id filtering"""
    cursor = conn.cursor()
    
    # Tables that should NOT get user_id (system tables)
    system_tables = {
        'users', 'roles', 'organizations', 'permissions', 'role_permissions', 
        'user_roles', 'security_roles', 'system_settings', 'audit_logs', 
        'login_history', 'password_history', 'two_factor_auth', 'user_sessions', 
        'account_lockouts', 'security_events', 'security_policies', 
        'permission_changes', 'user_modules', 'user_preferences', 
        'user_tenants', 'tenant_modules', 'tenant_settings', 
        'tenant_usage_stats', 'tenants', 'sqlite_sequence', 'migration_logs'
    }
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    # Filter out system tables
    business_tables = [table for table in all_tables if table not in system_tables]
    
    return business_tables

def check_table_has_user_id(conn, table_name):
    """Check if table already has user_id column"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return 'user_id' in columns

def add_user_id_to_table(conn, table_name):
    """Add user_id column to a table"""
    cursor = conn.cursor()
    
    try:
        # Check if user_id already exists
        if check_table_has_user_id(conn, table_name):
            print(f"   {table_name} already has user_id column")
            return True
        
        # Add user_id column
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN user_id INTEGER")
        print(f"   Added user_id to {table_name}")
        return True
        
    except Exception as e:
        print(f"   Error adding user_id to {table_name}: {e}")
        return False

def assign_existing_data_to_admin(conn, table_name):
    """Assign existing data to admin user (user_id = 1)"""
    cursor = conn.cursor()
    
    try:
        # Check if table has data
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"   {table_name} is empty, skipping")
            return True
        
        # Update existing records to user_id = 1
        cursor.execute(f"UPDATE {table_name} SET user_id = 1 WHERE user_id IS NULL")
        updated_count = cursor.rowcount
        
        print(f"   Assigned {updated_count} records in {table_name} to admin user")
        return True
        
    except Exception as e:
        print(f"   Error assigning data in {table_name}: {e}")
        return False

def main():
    print("Multi-Tenancy Migration: Adding User ID Filtering")
    print("=" * 60)
    
    # Connect to database
    conn = get_database_connection()
    if not conn:
        return
    
    try:
        # Get all business tables
        business_tables = get_business_tables(conn)
        print(f"Found {len(business_tables)} business tables to process")
        print()
        
        success_count = 0
        error_count = 0
        tables_processed = 0
        
        # Process each table
        for table_name in business_tables:
            print(f"Processing {table_name}...")
            
            # Add user_id column
            if add_user_id_to_table(conn, table_name):
                # Assign existing data to admin user
                if assign_existing_data_to_admin(conn, table_name):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
            
            tables_processed += 1
            print()
        
        # Commit all changes
        conn.commit()
        
        print("=" * 60)
        print(f"Migration completed!")
        print(f"Tables processed: {tables_processed}")
        print(f"Successful: {success_count}")
        print(f"Errors: {error_count}")
        print()
        print("All business data is now isolated by user_id")
        print("Existing data assigned to admin user (user_id = 1)")
        print("Ready for multi-tenant operation!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()


