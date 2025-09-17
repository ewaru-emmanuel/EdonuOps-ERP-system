#!/usr/bin/env python3
"""
Migration script to update daily cycle tables with missing columns
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from modules.finance.daily_cycle_models import DailyBalance, DailyCycleStatus, DailyTransactionSummary

def run_migration():
    """Run the migration to update daily cycle tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting daily cycle tables update migration...")
            
            # Check current table structure
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # Get current columns for daily_balances table
            if 'daily_balances' in inspector.get_table_names():
                current_columns = [col['name'] for col in inspector.get_columns('daily_balances')]
                print(f"📋 Current daily_balances columns: {current_columns}")
                
                # Add missing columns
                missing_columns = []
                
                # Check for missing columns and add them
                if 'total_debits' not in current_columns:
                    missing_columns.append('total_debits')
                if 'total_credits' not in current_columns:
                    missing_columns.append('total_credits')
                if 'transaction_count' not in current_columns:
                    missing_columns.append('transaction_count')
                if 'opening_captured_at' not in current_columns:
                    missing_columns.append('opening_captured_at')
                if 'opening_captured_by' not in current_columns:
                    missing_columns.append('opening_captured_by')
                if 'closing_calculated_at' not in current_columns:
                    missing_columns.append('closing_calculated_at')
                if 'closing_calculated_by' not in current_columns:
                    missing_columns.append('closing_calculated_by')
                
                if missing_columns:
                    print(f"🔧 Adding missing columns: {missing_columns}")
                    
                    # Add missing columns using raw SQL
                    for column in missing_columns:
                        if column in ['total_debits', 'total_credits', 'transaction_count']:
                            db.engine.execute(f'ALTER TABLE daily_balances ADD COLUMN {column} FLOAT DEFAULT 0.0')
                        elif column in ['opening_captured_at', 'closing_calculated_at']:
                            db.engine.execute(f'ALTER TABLE daily_balances ADD COLUMN {column} DATETIME')
                        elif column in ['opening_captured_by', 'closing_calculated_by']:
                            db.engine.execute(f'ALTER TABLE daily_balances ADD COLUMN {column} VARCHAR(100)')
                    
                    print("✅ Missing columns added successfully!")
                else:
                    print("✅ All required columns already exist!")
            
            # Check daily_cycle_status table
            if 'daily_cycle_status' in inspector.get_table_names():
                current_columns = [col['name'] for col in inspector.get_columns('daily_cycle_status')]
                print(f"📋 Current daily_cycle_status columns: {current_columns}")
                
                # Add missing columns for daily_cycle_status
                missing_status_columns = []
                
                if 'opening_captured_at' not in current_columns:
                    missing_status_columns.append('opening_captured_at')
                if 'opening_captured_by' not in current_columns:
                    missing_status_columns.append('opening_captured_by')
                if 'closing_calculated_at' not in current_columns:
                    missing_status_columns.append('closing_calculated_at')
                if 'closing_calculated_by' not in current_columns:
                    missing_status_columns.append('closing_calculated_by')
                if 'total_closing_balance' not in current_columns:
                    missing_status_columns.append('total_closing_balance')
                
                if missing_status_columns:
                    print(f"🔧 Adding missing status columns: {missing_status_columns}")
                    
                    for column in missing_status_columns:
                        if column == 'total_closing_balance':
                            db.engine.execute(f'ALTER TABLE daily_cycle_status ADD COLUMN {column} FLOAT DEFAULT 0.0')
                        elif column in ['opening_captured_at', 'closing_calculated_at']:
                            db.engine.execute(f'ALTER TABLE daily_cycle_status ADD COLUMN {column} DATETIME')
                        elif column in ['opening_captured_by', 'closing_calculated_by']:
                            db.engine.execute(f'ALTER TABLE daily_cycle_status ADD COLUMN {column} VARCHAR(100)')
                    
                    print("✅ Missing status columns added successfully!")
                else:
                    print("✅ All required status columns already exist!")
            
            print("🎉 Daily cycle tables update migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("💡 Daily cycle tables are now ready for enhanced daily balance flow!")
    else:
        print("💥 Migration failed. Please check the error messages above.")
