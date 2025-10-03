#!/usr/bin/env python3
"""
Add payment_method column to journal_entries table using Flask app context
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.app import create_app, db
    from sqlalchemy import text
    
    def add_payment_method_column():
        """Add payment_method column to journal_entries table"""
        
        app = create_app()
        with app.app_context():
            try:
                print("🔄 Adding payment_method column to journal_entries table...")
                
                # Check if column already exists by trying to query it
                try:
                    result = db.session.execute(text("SELECT payment_method FROM journal_entries LIMIT 1"))
                    print("✅ payment_method column already exists!")
                    return
                except Exception as e:
                    if "no such column" in str(e).lower() or "column" in str(e).lower():
                        print("📝 Column doesn't exist, adding it...")
                    else:
                        print(f"❌ Error checking column: {e}")
                        return
                
                # Add the column
                db.session.execute(text("ALTER TABLE journal_entries ADD COLUMN payment_method VARCHAR(20) DEFAULT 'bank'"))
                db.session.commit()
                
                print("✅ Successfully added payment_method column!")
                
                # Update existing entries to have default value
                db.session.execute(text("UPDATE journal_entries SET payment_method = 'bank' WHERE payment_method IS NULL"))
                db.session.commit()
                
                print("✅ Updated existing entries with default payment_method = 'bank'")
                
                # Verify the column was added
                result = db.session.execute(text("SELECT payment_method FROM journal_entries LIMIT 1"))
                print("✅ Column verification successful!")
                
            except Exception as e:
                print(f"❌ Error adding payment_method column: {str(e)}")
                db.session.rollback()
                raise
    
    if __name__ == "__main__":
        add_payment_method_column()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running this from the project root directory")
    sys.exit(1)

