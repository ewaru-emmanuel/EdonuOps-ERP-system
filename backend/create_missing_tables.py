#!/usr/bin/env python3
"""
Create missing database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def create_missing_tables():
    """Create missing database tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Creating missing database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            print("📊 Tables created:")
            print("   - user_modules")
            print("   - exchange_rates") 
            print("   - currencies")
            print("   - currency_conversions")
            print("   - dashboards")
            print("   - dashboard_widgets")
            print("   - widget_templates")
            print("   - dashboard_templates")
            
            print("\n🎉 Database setup complete!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Creating missing database tables...")
    success = create_missing_tables()
    if success:
        print("✅ Setup completed successfully!")
    else:
        print("❌ Setup failed!")
        sys.exit(1)

