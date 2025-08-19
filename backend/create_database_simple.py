#!/usr/bin/env python3
"""
Simple database creation script for EdonuOps
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_database():
    """Create the database and all tables"""
    
    try:
        print("🔍 Creating EdonuOps database...")
        
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
            
            # Import all models to ensure they're registered
            print("📦 Importing models...")
            
            # Core models
            from modules.core import models as core_models
            print("✅ Core models imported")
            
            # CRM models
            from modules.crm.models import Contact, Lead, Opportunity, Communication, FollowUp, CRMUser, LeadIntake
            print("✅ CRM models imported")
            
            # Finance models
            from modules.finance.models import Account, JournalEntry, JournalLine, Currency, ExchangeRate
            print("✅ Finance models imported")
            
            # Inventory models
            from modules.inventory.models import Category, Product, InventoryTransaction, Warehouse, InventoryReceipt, ReceiptItem
            print("✅ Inventory models imported")
            
            # HR models
            from modules.hr.models import Employee, Payroll, Recruitment
            print("✅ HR models imported")
            
            # Create all tables
            print("🔨 Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully")
            
            # Create some sample data
            print("🌱 Creating sample data...")
            
            # Create a sample contact
            sample_contact = Contact(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="+1234567890",
                company="Acme Corp",
                type="customer",
                status="active"
            )
            db.session.add(sample_contact)
            
            # Create a sample lead
            sample_lead = Lead(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="+0987654321",
                company="Tech Solutions",
                source="website",
                status="new"
            )
            db.session.add(sample_lead)
            
            # Create a sample account
            sample_account = Account(
                code="1000",
                name="Cash",
                type="asset",
                category="current_assets",
                status="active"
            )
            db.session.add(sample_account)
            
            # Create a sample product
            sample_product = Product(
                name="Sample Product",
                sku="SP001",
                description="A sample product for testing",
                price=99.99,
                cost=50.00,
                category_id=1,
                status="active"
            )
            db.session.add(sample_product)
            
            # Commit all changes
            db.session.commit()
            print("✅ Sample data created successfully")
            
            print(f"\n🎉 Database created successfully!")
            print(f"📁 Database file: {os.path.abspath('edonuops.db')}")
            print(f"📊 Tables created: {len(db.metadata.tables)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_database()
    if success:
        print("\n✅ Database setup completed successfully!")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)

