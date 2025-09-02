#!/usr/bin/env python3
import sqlite3

def check_database():
    conn = sqlite3.connect('edonuops.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Tables in database: {tables}")
    
    # Check each table structure
    for table in tables:
        print(f"\nTable: {table}")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_database()

