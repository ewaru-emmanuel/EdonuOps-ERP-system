#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script
Tests different connection parameters to diagnose the issue
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def test_postgresql_connection():
    """Test PostgreSQL connection with different parameters"""
    
    print("🔍 PostgreSQL Connection Diagnostic Test")
    print("=" * 50)
    
    # Get connection parameters
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT', '5432')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    print(f"📊 Connection Parameters:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   User: {user}")
    print(f"   Password: {'*' * len(password) if password else 'None'}")
    print()
    
    # Test 1: Basic connection without SSL
    print("🔌 Test 1: Basic connection (no SSL)")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        print("✅ Basic connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
    
    # Test 2: Connection with SSL disabled
    print("\n🔌 Test 2: Connection with SSL disabled")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            sslmode='disable',
            connect_timeout=10
        )
        print("✅ SSL disabled connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ SSL disabled connection failed: {e}")
    
    # Test 3: Connection with SSL required
    print("\n🔌 Test 3: Connection with SSL required")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            sslmode='require',
            connect_timeout=10
        )
        print("✅ SSL required connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ SSL required connection failed: {e}")
    
    # Test 4: Connection with SSL preferred
    print("\n🔌 Test 4: Connection with SSL preferred")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            sslmode='prefer',
            connect_timeout=10
        )
        print("✅ SSL preferred connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ SSL preferred connection failed: {e}")
    
    # Test 5: Test with DATABASE_URL
    print("\n🔌 Test 5: Connection using DATABASE_URL")
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            conn = psycopg2.connect(database_url, connect_timeout=10)
            print("✅ DATABASE_URL connection successful!")
            conn.close()
        except Exception as e:
            print(f"❌ DATABASE_URL connection failed: {e}")
    else:
        print("❌ DATABASE_URL not found in environment")

def main():
    """Main function"""
    test_postgresql_connection()
    
    print("\n🎯 Recommendations:")
    print("   1. If SSL disabled works: Update config to use sslmode='disable'")
    print("   2. If SSL required works: Keep current SSL settings")
    print("   3. If all fail: Check AWS RDS authentication settings")
    print("   4. If DATABASE_URL fails: Check URL encoding")

if __name__ == "__main__":
    main()


