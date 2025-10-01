#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('instance/edonuops.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
bank_tables = [t for t in tables if 'bank' in t or 'reconciliation' in t]
print('Bank-related tables:', bank_tables)
conn.close()


