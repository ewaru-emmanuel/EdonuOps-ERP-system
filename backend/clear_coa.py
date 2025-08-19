#!/usr/bin/env python3
"""
Clear Chart of Accounts - Reset to blank state
This script removes all existing CoA accounts to start fresh
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from modules.finance.models import ChartOfAccount

def clear_chart_of_accounts():
    """Clear all Chart of Accounts entries"""
    app = create_app()
    
    with app.app_context():
        try:
            # Count existing accounts
            existing_count = ChartOfAccount.query.count()
            
            if existing_count == 0:
                print("✅ Chart of Accounts is already empty.")
                return
            
            print(f"🔍 Found {existing_count} existing accounts.")
            
            # Confirm deletion
            confirm = input(f"⚠️  Are you sure you want to delete all {existing_count} accounts? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("❌ Operation cancelled.")
                return
            
            # Delete all accounts
            deleted_count = ChartOfAccount.query.delete()
            db.session.commit()
            
            print(f"✅ Successfully deleted {deleted_count} accounts.")
            print("🎯 Chart of Accounts is now empty and ready for fresh setup!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error clearing Chart of Accounts: {e}")
            raise

if __name__ == "__main__":
    print("🧹 EdonuOps - Clear Chart of Accounts")
    print("=" * 50)
    clear_chart_of_accounts()

