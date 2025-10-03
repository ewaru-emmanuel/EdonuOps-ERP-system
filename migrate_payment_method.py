import sqlite3
import os

# Find the database file
db_files = [f for f in os.listdir('.') if f.endswith('.db')]
if not db_files:
    print("No database files found in current directory")
    exit(1)

db_file = db_files[0]
print(f"Using database file: {db_file}")

# Connect to database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(journal_entries)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'payment_method' in columns:
        print("✅ payment_method column already exists!")
    else:
        print("🔄 Adding payment_method column...")
        cursor.execute("ALTER TABLE journal_entries ADD COLUMN payment_method VARCHAR(20) DEFAULT 'bank'")
        
        # Update existing entries
        cursor.execute("UPDATE journal_entries SET payment_method = 'bank' WHERE payment_method IS NULL")
        
        conn.commit()
        print("✅ Successfully added payment_method column!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

