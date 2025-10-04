#!/usr/bin/env python3
"""
Database Safety Utilities
Prevents accidental data loss and provides safe database operations
"""

import os
import sys
from datetime import datetime

def check_database_safety():
    """Check if it's safe to perform database operations"""
    
    # Check environment
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        print("❌ PRODUCTION ENVIRONMENT DETECTED!")
        print("🚫 Database operations are restricted in production.")
        return False
    
    # Check if database file exists and has data
    db_path = os.path.join(os.path.dirname(__file__), 'edonuops.db')
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        if file_size > 1024:  # More than 1KB suggests it has data
            print(f"⚠️  Database file exists ({file_size} bytes) - may contain data!")
            return False
    
    return True

def safe_database_operation(operation_name, operation_func):
    """Safely execute a database operation with multiple safety checks"""
    
    print(f"\n🔒 SAFETY CHECK: {operation_name}")
    print("=" * 50)
    
    # Check 1: Environment
    if not check_database_safety():
        print("❌ Safety check failed. Operation cancelled.")
        return False
    
    # Check 2: User confirmation
    print(f"⚠️  You are about to perform: {operation_name}")
    print("This operation may affect your database.")
    
    response = input("Type 'YES' to continue, or anything else to cancel: ")
    if response != 'YES':
        print("❌ Operation cancelled by user.")
        return False
    
    # Check 3: Final warning
    print("\n🚨 FINAL WARNING:")
    print("This operation will modify your database.")
    print("Make sure you have a backup if needed.")
    
    final_response = input("Type 'PROCEED' to execute the operation: ")
    if final_response != 'PROCEED':
        print("❌ Operation cancelled at final confirmation.")
        return False
    
    # Execute the operation
    try:
        print(f"\n🔄 Executing: {operation_name}")
        result = operation_func()
        print(f"✅ Operation completed successfully!")
        return result
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        return False

def create_backup():
    """Create a backup of the current database"""
    import shutil
    from datetime import datetime
    
    db_path = os.path.join(os.path.dirname(__file__), 'edonuops.db')
    if not os.path.exists(db_path):
        print("❌ No database file found to backup.")
        return False
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(os.path.dirname(__file__), f'edonuops_backup_{timestamp}.db')
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def list_database_files():
    """List all database files in the backend directory"""
    backend_dir = os.path.dirname(__file__)
    db_files = []
    
    for file in os.listdir(backend_dir):
        if file.endswith('.db'):
            file_path = os.path.join(backend_dir, file)
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            db_files.append({
                'name': file,
                'size': size,
                'modified': modified
            })
    
    if db_files:
        print("\n📁 Database files found:")
        print("-" * 60)
        for db_file in sorted(db_files, key=lambda x: x['modified'], reverse=True):
            print(f"  {db_file['name']:<30} {db_file['size']:>8} bytes  {db_file['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ No database files found.")
    
    return db_files

if __name__ == '__main__':
    print("🔒 Database Safety Utilities")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'backup':
            create_backup()
        elif command == 'list':
            list_database_files()
        elif command == 'check':
            safe = check_database_safety()
            print(f"Database safety check: {'✅ PASSED' if safe else '❌ FAILED'}")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: backup, list, check")
    else:
        print("Available commands:")
        print("  python database_safety.py backup  - Create database backup")
        print("  python database_safety.py list    - List database files")
        print("  python database_safety.py check   - Check database safety")
