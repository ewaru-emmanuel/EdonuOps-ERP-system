# backend/modules/database.py

from app import db

# Simple database utilities
def get_db():
    """Get database instance"""
    return db

def init_db():
    """Initialize database tables"""
    db.create_all()

def drop_db():
    """Drop all database tables - DANGER: This will delete ALL data!"""
    import os
    import sys
    from datetime import datetime
    
    # CRITICAL SAFETY: Never allow in production
    if os.getenv('FLASK_ENV') == 'production':
        raise RuntimeError("🚨 CRITICAL: Cannot drop database in production environment!")
    
    # CRITICAL SAFETY: Create backup before any destructive operation
    print("🔄 Creating backup before destructive operation...")
    backup_file = f"database_backup_before_drop_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    try:
        import shutil
        shutil.copy2('edonuops.db', backup_file)
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        print("🚨 ABORTING: Cannot proceed without backup!")
        return False
    
    # Multiple safety checks
    print("🚨 CRITICAL WARNING: This will delete ALL data!")
    print("🚨 This includes user_modules, journal_entries, and ALL user data!")
    
    response1 = input("⚠️  Type 'I_UNDERSTAND_DESTRUCTIVE' to continue: ")
    if response1 != 'I_UNDERSTAND_DESTRUCTIVE':
        print("Operation cancelled.")
        return False
    
    response2 = input("⚠️  Type 'DELETE_ALL_DATA' to confirm: ")
    if response2 != 'DELETE_ALL_DATA':
        print("Operation cancelled.")
        return False
    
    response3 = input("⚠️  Type 'YES_DELETE_EVERYTHING' for final confirmation: ")
    if response3 != 'YES_DELETE_EVERYTHING':
        print("Operation cancelled.")
        return False
    
    print("🗑️  Dropping all database tables...")
    db.drop_all()
    print("✅ All tables dropped.")
    print(f"💾 Backup available at: {backup_file}")
    return True


