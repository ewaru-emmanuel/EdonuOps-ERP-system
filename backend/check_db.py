import sqlite3
import os

print('Database file exists:', os.path.exists('edonuops.db'))

if os.path.exists('edonuops.db'):
    conn = sqlite3.connect('edonuops.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tables in database:')
    for table in tables:
        print(f'  - {table[0]}')
    
    # Check users
    try:
        cursor.execute('SELECT id, email, username FROM users')
        users = cursor.fetchall()
        print('\nUsers in database:')
        for user in users:
            print(f'  ID: {user[0]}, Email: {user[1]}, Username: {user[2]}')
    except Exception as e:
        print(f'Error checking users: {e}')
    
    # Check journal entries
    try:
        cursor.execute('SELECT COUNT(*) FROM journal_entries')
        entry_count = cursor.fetchone()[0]
        print(f'\nJournal entries count: {entry_count}')
        
        if entry_count > 0:
            cursor.execute('SELECT id, reference, total_debit, total_credit FROM journal_entries LIMIT 5')
            entries = cursor.fetchall()
            print('Sample journal entries:')
            for entry in entries:
                print(f'  Entry {entry[0]}: {entry[1]} - Debit: ${entry[2]}, Credit: ${entry[3]}')
    except Exception as e:
        print(f'Error checking journal entries: {e}')
    
    conn.close()
else:
    print('Database file not found')
