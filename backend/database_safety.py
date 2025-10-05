#!/usr/bin/env python3
"""
Database Safety and Backup System
Prevents data loss in production environments
"""

import os
import shutil
import sqlite3
from datetime import datetime
import sys

class DatabaseSafety:
    """Database safety and backup management"""
    
    def __init__(self, db_path='edonuops.db'):
        self.db_path = db_path
        self.backup_dir = 'database_backups'
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"✅ Created backup directory: {self.backup_dir}")
    
    def create_backup(self, reason="manual"):
        """Create a timestamped backup of the database"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"edonuops_backup_{timestamp}_{reason}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup created: {backup_path}")
            
            # Also create a latest backup for quick access
            latest_backup = os.path.join(self.backup_dir, "latest_backup.db")
            shutil.copy2(self.db_path, latest_backup)
            print(f"✅ Latest backup updated: {latest_backup}")
            
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        if not os.path.exists(backup_path):
            print(f"❌ Backup not found: {backup_path}")
            return False
        
        try:
            # Create backup of current database before restore
            current_backup = self.create_backup("before_restore")
            if not current_backup:
                print("❌ Failed to create backup before restore")
                return False
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            print(f"✅ Database restored from: {backup_path}")
            print(f"💾 Previous state backed up to: {current_backup}")
            return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        if not os.path.exists(self.backup_dir):
            print("❌ No backup directory found")
            return []
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': size,
                    'modified': mtime
                })
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        return backups
    
    def show_backups(self):
        """Show all available backups"""
        backups = self.list_backups()
        if not backups:
            print("❌ No backups found")
            return
        
        print(f"📊 Available Backups ({len(backups)}):")
        print("=" * 80)
        for i, backup in enumerate(backups, 1):
            size_mb = backup['size'] / (1024 * 1024)
            print(f"{i:2d}. {backup['filename']}")
            print(f"    Size: {size_mb:.2f} MB")
            print(f"    Date: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    def cleanup_old_backups(self, keep_count=10):
        """Clean up old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        if len(backups) <= keep_count:
            print(f"✅ No cleanup needed ({len(backups)} backups, keeping {keep_count})")
            return
        
        to_delete = backups[keep_count:]
        deleted_count = 0
        
        for backup in to_delete:
            try:
                os.remove(backup['path'])
                print(f"🗑️ Deleted old backup: {backup['filename']}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {backup['filename']}: {e}")
        
        print(f"✅ Cleanup complete: {deleted_count} old backups removed")
    
    def check_database_integrity(self):
        """Check database integrity"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result[0] == 'ok':
                print("✅ Database integrity check passed")
                
                # Get basic stats
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                print(f"📊 Database contains {table_count} tables")
                
                # Check critical tables
                critical_tables = ['users', 'user_modules', 'journal_entries', 'accounts']
                for table in critical_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"  📋 {table}: {count} records")
                    except:
                        print(f"  ❌ {table}: table not found")
                
                conn.close()
                return True
            else:
                print(f"❌ Database integrity check failed: {result[0]}")
                conn.close()
                return False
                
        except Exception as e:
            print(f"❌ Database integrity check failed: {e}")
            return False

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Database Safety System")
        print("Usage:")
        print("  python database_safety.py backup [reason]")
        print("  python database_safety.py restore <backup_file>")
        print("  python database_safety.py list")
        print("  python database_safety.py cleanup [keep_count]")
        print("  python database_safety.py check")
        return
    
    safety = DatabaseSafety()
    command = sys.argv[1]
    
    if command == 'backup':
        reason = sys.argv[2] if len(sys.argv) > 2 else 'manual'
        safety.create_backup(reason)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Please specify backup file to restore from")
            return
        backup_file = sys.argv[2]
        safety.restore_backup(backup_file)
    
    elif command == 'list':
        safety.show_backups()
    
    elif command == 'cleanup':
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        safety.cleanup_old_backups(keep_count)
    
    elif command == 'check':
        safety.check_database_integrity()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()