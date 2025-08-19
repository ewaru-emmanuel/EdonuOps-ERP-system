#!/usr/bin/env python3
"""
Seed sample data for EdonuOps
"""

import os
import sys
from datetime import datetime, date

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def seed_sample_data():
    """Seed the database with sample data"""
    
    try:
        print("🌱 Seeding sample data...")
        
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
            
            # Create sample contacts
            print("👥 Creating sample contacts...")
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
                ),
                Contact(
                    first_name="Bob",
                    last_name="Johnson",
                    email="bob.johnson@innovate.com",
                    phone="+1122334455",
                    company="Innovate Solutions",
                    type="prospect",
                    status="active"
                )
            ]
            
            for contact in contacts:
                db.session.add(contact)
            
            # Create sample leads
            print("🎯 Creating sample leads...")
            leads = [
                Lead(
                    first_name="Alice",
                    last_name="Brown",
                    email="alice.brown@startup.com",
                    phone="+1555666777",
                    company="StartupXYZ",
                    source="website",
                    status="new"
                ),
                Lead(
                    first_name="Charlie",
                    last_name="Wilson",
                    email="charlie.wilson@enterprise.com",
                    phone="+1888999000",
                    company="Enterprise Corp",
                    source="referral",
                    status="qualified"
                )
            ]
            
            for lead in leads:
                db.session.add(lead)
            
            # Create sample accounts
            print("💰 Creating sample accounts...")
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
                ),
                Account(
                    code="3000",
                    name="Retained Earnings",
                    type="equity",
                    balance=60000.00,
                    currency="USD"
                )
            ]
            
            for account in accounts:
                db.session.add(account)
            
            # Create sample categories
            print("📂 Creating sample categories...")
            categories = [
                Category(name="Electronics", description="Electronic devices and components"),
                Category(name="Office Supplies", description="Office and stationery items"),
                Category(name="Furniture", description="Office furniture and fixtures")
            ]
            
            for category in categories:
                db.session.add(category)
            
            # Commit categories first to get IDs
            db.session.commit()
            
            # Create sample products
            print("📦 Creating sample products...")
            products = [
                Product(
                    name="Laptop Computer",
                    sku="LAP001",
                    description="High-performance laptop for business use",
                    category_id=1,
                    price=1200.00,
                    cost=800.00,
                    status="active"
                ),
                Product(
                    name="Office Chair",
                    sku="CHAIR001",
                    description="Ergonomic office chair",
                    category_id=3,
                    price=300.00,
                    cost=200.00,
                    status="active"
                ),
                Product(
                    name="Printer Paper",
                    sku="PAPER001",
                    description="A4 printer paper, 500 sheets",
                    category_id=2,
                    price=15.00,
                    cost=10.00,
                    status="active"
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            # Create sample warehouses
            print("🏢 Creating sample warehouses...")
            warehouses = [
                Warehouse(
                    name="Main Warehouse",
                    location="123 Main St, City, State",
                    capacity=10000
                ),
                Warehouse(
                    name="Secondary Warehouse",
                    location="456 Oak Ave, City, State",
                    capacity=5000
                )
            ]
            
            for warehouse in warehouses:
                db.session.add(warehouse)
            
            # Create sample employees
            print("👨‍💼 Creating sample employees...")
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
                ),
                Employee(
                    first_name="Sarah",
                    last_name="Miller",
                    email="sarah.miller@company.com",
                    phone="+1777666555",
                    position="Accountant",
                    department="Finance",
                    hire_date=date(2023, 3, 20),
                    salary=65000.00,
                    status="active"
                )
            ]
            
            for employee in employees:
                db.session.add(employee)
            
            # Commit all changes
            db.session.commit()
            print("✅ Sample data created successfully!")
            
            # Print summary
            print(f"\n📊 Sample data summary:")
            print(f"   👥 Contacts: {len(contacts)}")
            print(f"   🎯 Leads: {len(leads)}")
            print(f"   💰 Accounts: {len(accounts)}")
            print(f"   📂 Categories: {len(categories)}")
            print(f"   📦 Products: {len(products)}")
            print(f"   🏢 Warehouses: {len(warehouses)}")
            print(f"   👨‍💼 Employees: {len(employees)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_sample_data()
    if success:
        print("\n✅ Data seeding completed successfully!")
    else:
        print("\n❌ Data seeding failed!")
        sys.exit(1)
