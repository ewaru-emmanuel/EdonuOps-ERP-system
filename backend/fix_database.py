#!/usr/bin/env python3
"""
Fix database by creating all necessary tables
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database():
    """Fix database by creating all necessary tables"""
    
    try:
        print("🔍 Fixing EdonuOps database...")
        
        # Import the existing Flask app
        from app import create_app, db
        
        # Create app
        app = create_app()
        
        with app.app_context():
            print("✅ App context created")
            
            # Drop all tables first
            print("🗑️ Dropping existing tables...")
            db.drop_all()
            print("✅ All tables dropped")
            
            # Create all tables
            print("🔨 Creating all tables...")
            db.create_all()
            print("✅ All tables created")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📊 Tables created: {existing_tables}")
            
            if existing_tables:
                print(f"\n🎉 Database fixed successfully!")
                print(f"📁 Database file: {os.path.abspath('edonuops.db')}")
                print(f"📋 Total tables: {len(existing_tables)}")
                return True
            else:
                print("❌ No tables were created!")
                return False
            
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("\n✅ Database fix completed successfully!")
    else:
        print("\n❌ Database fix failed!")
        sys.exit(1)
