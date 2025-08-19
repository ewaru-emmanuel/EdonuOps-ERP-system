#!/usr/bin/env python3
"""
Create clean database with only essential models
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_clean_database():
    """Create database with only essential models"""
    
    try:
        print("🔍 Creating clean EdonuOps database...")
        
        # Import Flask and create app
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv('config.env')
        
        # Create Flask app
        app = Flask(__name__)
        
        # Configure database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edonuops.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'dev-secret-key'
        
        # Initialize SQLAlchemy
        db = SQLAlchemy(app)
        
        with app.app_context():
            print("✅ Database context created")
            
            # Import only essential models without problematic relationships
            print("📦 Importing essential models...")
            
            # Core models - simplified
            from modules.core.models import User, Organization, Role
            print("✅ Core models imported")
            
            # CRM models - simplified (remove problematic relationships)
            from modules.crm.models import Contact, Lead, Opportunity
            print("✅ CRM models imported")
            
            # Finance models
            from modules.finance.models import Account, JournalEntry, JournalLine
            print("✅ Finance models imported")
            
            # Inventory models
            from modules.inventory.models import Category, Product, InventoryTransaction, Warehouse
            print("✅ Inventory models imported")
            
            # HR models
            from modules.hr.models import Employee, Payroll, Recruitment
            print("✅ HR models imported")
            
            # Create all tables
            print("🔨 Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📊 Tables created: {existing_tables}")
            
            print(f"\n🎉 Clean database created successfully!")
            print(f"📁 Database file: {os.path.abspath('edonuops.db')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_clean_database()
    if success:
        print("\n✅ Clean database setup completed successfully!")
    else:
        print("\n❌ Clean database setup failed!")
        sys.exit(1)
