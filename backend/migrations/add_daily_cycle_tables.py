#!/usr/bin/env python3
"""
Migration script to add daily cycle tables for finance module
Run this script to create the necessary tables for daily opening/closing balance management
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from modules.finance.daily_cycle_models import DailyBalance, DailyCycleStatus, DailyTransactionSummary

def run_migration():
    """Run the migration to create daily cycle tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting daily cycle tables migration...")
            
            # Create all daily cycle tables
            db.create_all()
            
            print("✅ Daily cycle tables created successfully!")
            print("📋 Created tables:")
            print("   - daily_balances")
            print("   - daily_cycle_status") 
            print("   - daily_transaction_summaries")
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            daily_cycle_tables = [t for t in tables if 'daily' in t.lower()]
            print(f"📊 Daily cycle tables in database: {daily_cycle_tables}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("💡 You can now use the daily cycle functionality in your finance module.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        sys.exit(1)
