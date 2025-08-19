#!/usr/bin/env python3
"""
Check and fix database issues
"""

import os
import sys
from datetime import datetime, date

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_and_fix_database():
    """Check database and fix any issues"""
    
    try:
        print("🔍 Checking database...")
        
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
            # Import models
            from modules.crm.models import Contact, Lead, Opportunity
            from modules.finance.models import Account, JournalEntry, JournalLine
            from modules.inventory.models import Category, Product, Warehouse
            from modules.hr.models import Employee, Payroll, Recruitment
            
            print("📦 Models imported successfully")
            
            # Check if tables exist
            print("🔍 Checking if tables exist...")
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"Existing tables: {existing_tables}")
            
            if not existing_tables:
                print("❌ No tables found. Creating tables...")
                db.create_all()
                print("✅ Tables created successfully")
            else:
                print("✅ Tables already exist")
            
            # Check if we have data
            print("🔍 Checking for existing data...")
            contact_count = Contact.query.count()
            account_count = Account.query.count()
            product_count = Product.query.count()
            employee_count = Employee.query.count()
            
            print(f"   👥 Contacts: {contact_count}")
            print(f"   💰 Accounts: {account_count}")
            print(f"   📦 Products: {product_count}")
            print(f"   👨‍💼 Employees: {employee_count}")
            
            # If no data, seed sample data
            if contact_count == 0 and account_count == 0:
                print("🌱 No data found. Seeding sample data...")
                
                # Create sample contacts
                contacts = [
                    Contact(
                        first_name="John",
                        last_name="Doe",
                        email="john.doe@acme.com",
                        phone="+1234567890",
                        company="Acme Corporation",
                        type="customer",
                        status="active"
                    ),
                    Contact(
                        first_name="Jane",
                        last_name="Smith",
                        email="jane.smith@techcorp.com",
                        phone="+0987654321",
                        company="TechCorp Inc",
                        type="customer",
                        status="active"
                    )
                ]
                
                for contact in contacts:
                    db.session.add(contact)
                
                # Create sample accounts
                accounts = [
                    Account(
                        code="1000",
                        name="Cash",
                        type="asset",
                        balance=50000.00,
                        currency="USD"
                    ),
                    Account(
                        code="1200",
                        name="Accounts Receivable",
                        type="asset",
                        balance=25000.00,
                        currency="USD"
                    ),
                    Account(
                        code="2000",
                        name="Accounts Payable",
                        type="liability",
                        balance=15000.00,
                        currency="USD"
                    )
                ]
                
                for account in accounts:
                    db.session.add(account)
                
                # Create sample categories
                categories = [
                    Category(name="Electronics", description="Electronic devices"),
                    Category(name="Office Supplies", description="Office items")
                ]
                
                for category in categories:
                    db.session.add(category)
                
                # Commit categories first to get IDs
                db.session.commit()
                
                # Create sample products
                products = [
                    Product(
                        name="Laptop Computer",
                        sku="LAP001",
                        description="High-performance laptop",
                        category_id=1,
                        price=1200.00,
                        cost=800.00,
                        status="active"
                    ),
                    Product(
                        name="Office Chair",
                        sku="CHAIR001",
                        description="Ergonomic chair",
                        category_id=2,
                        price=300.00,
                        cost=200.00,
                        status="active"
                    )
                ]
                
                for product in products:
                    db.session.add(product)
                
                # Create sample employees
                employees = [
                    Employee(
                        first_name="Michael",
                        last_name="Davis",
                        email="michael.davis@company.com",
                        phone="+1999888777",
                        position="Manager",
                        department="Sales",
                        hire_date=date(2023, 1, 15),
                        salary=75000.00,
                        status="active"
                    )
                ]
                
                for employee in employees:
                    db.session.add(employee)
                
                # Commit all changes
                db.session.commit()
                print("✅ Sample data created successfully!")
            else:
                print("✅ Data already exists")
            
            print(f"\n🎉 Database check completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_and_fix_database()
    if success:
        print("\n✅ Database check completed successfully!")
    else:
        print("\n❌ Database check failed!")
        sys.exit(1)
