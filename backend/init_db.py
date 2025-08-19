#!/usr/bin/env python3
"""
Database initialization script for EdonuOps
Creates all tables and populates with sample data
"""

from app import create_app, db
from modules.core.models import User, Role, Organization
from modules.inventory.models import Category, Product, Warehouse, InventoryTransaction
from modules.finance.models import Account, JournalEntry, JournalLine
from modules.crm.models import Customer, Lead
from modules.hr.models import Employee
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

def init_database():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Creating database tables...")
        db.create_all()
        
        print("👥 Creating default roles...")
        # Create default roles
        admin_role = Role.query.filter_by(role_name="admin").first()
        if not admin_role:
            admin_role = Role(role_name="admin", permissions={"all": True})
            db.session.add(admin_role)
        
        user_role = Role.query.filter_by(role_name="user").first()
        if not user_role:
            user_role = Role(role_name="user", permissions={"read": True})
            db.session.add(user_role)
        
        print("🏢 Creating default organization...")
        # Create default organization
        org = Organization.query.filter_by(name="EdonuOps Corp").first()
        if not org:
            org = Organization(name="EdonuOps Corp")
            db.session.add(org)
        
        print("👤 Creating admin user...")
        # Create admin user
        admin_user = User.query.filter_by(email="admin@edonuops.com").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@edonuops.com",
                password_hash=generate_password_hash("password"),
                role_id=admin_role.id,
                organization_id=org.id
            )
            db.session.add(admin_user)
        
        print("📦 Creating sample inventory data...")
        # Create sample inventory categories
        categories = [
            Category(name="Electronics", description="Electronic components and devices"),
            Category(name="Office Supplies", description="Office equipment and supplies"),
            Category(name="Raw Materials", description="Raw materials for manufacturing"),
            Category(name="Furniture", description="Office and home furniture"),
            Category(name="Software", description="Software licenses and applications")
        ]
        
        for category in categories:
            existing = Category.query.filter_by(name=category.name).first()
            if not existing:
                db.session.add(category)
        
        print("🏭 Creating sample warehouses...")
        # Create sample warehouses
        warehouses = [
            Warehouse(name="Main Warehouse", location="123 Industrial Blvd, City Center", capacity=10000),
            Warehouse(name="Secondary Storage", location="456 Warehouse Ave, Suburb", capacity=5000),
            Warehouse(name="Distribution Center", location="789 Logistics Way, Port City", capacity=15000)
        ]
        
        for warehouse in warehouses:
            existing = Warehouse.query.filter_by(name=warehouse.name).first()
            if not existing:
                db.session.add(warehouse)
        
        print("💰 Creating sample financial accounts...")
        # Create sample financial accounts
        accounts = [
            Account(code="1000", name="Cash and Cash Equivalents", type="asset", balance=10000.0),
            Account(code="1100", name="Accounts Receivable", type="asset", balance=5000.0),
            Account(code="1200", name="Inventory", type="asset", balance=15000.0),
            Account(code="2000", name="Accounts Payable", type="liability", balance=8000.0),
            Account(code="3000", name="Owner's Equity", type="equity", balance=22000.0),
            Account(code="4000", name="Sales Revenue", type="revenue", balance=50000.0),
            Account(code="5000", name="Cost of Goods Sold", type="expense", balance=30000.0)
        ]
        
        for account in accounts:
            existing = Account.query.filter_by(code=account.code).first()
            if not existing:
                db.session.add(account)
        
        print("👥 Creating sample employees...")
        # Create sample employees
        employees = [
            Employee(
                first_name="John",
                last_name="Doe",
                email="john.doe@edonuops.com",
                position="Software Engineer",
                department="Engineering",
                salary=75000.0,
                hire_date=datetime(2023, 1, 15)
            ),
            Employee(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@edonuops.com",
                position="Product Manager",
                department="Product",
                salary=85000.0,
                hire_date=datetime(2023, 3, 20)
            ),
            Employee(
                first_name="Mike",
                last_name="Johnson",
                email="mike.johnson@edonuops.com",
                position="Sales Representative",
                department="Sales",
                salary=65000.0,
                hire_date=datetime(2023, 6, 10)
            )
        ]
        
        for employee in employees:
            existing = Employee.query.filter_by(email=employee.email).first()
            if not existing:
                db.session.add(employee)
        
        print("👥 Creating sample customers...")
        # Create sample customers
        customers = [
            Customer(
                name="ABC Company",
                email="contact@abc.com",
                phone="+1-555-0101",
                address="123 Business St, City",
                status="active"
            ),
            Customer(
                name="XYZ Corporation",
                email="info@xyz.com",
                phone="+1-555-0102",
                address="456 Corporate Ave, Town",
                status="active"
            ),
            Customer(
                name="Tech Solutions Inc",
                email="sales@techsolutions.com",
                phone="+1-555-0103",
                address="789 Innovation Blvd, Tech City",
                status="active"
            )
        ]
        
        for customer in customers:
            existing = Customer.query.filter_by(email=customer.email).first()
            if not existing:
                db.session.add(customer)
        
        print("🎯 Creating sample leads...")
        # Create sample leads
        leads = [
            Lead(
                name="New Startup",
                email="founder@newstartup.com",
                phone="+1-555-0201",
                company="New Startup Inc",
                status="new",
                source="website"
            ),
            Lead(
                name="Enterprise Corp",
                email="procurement@enterprise.com",
                phone="+1-555-0202",
                company="Enterprise Corporation",
                status="qualified",
                source="referral"
            )
        ]
        
        for lead in leads:
            existing = Lead.query.filter_by(email=lead.email).first()
            if not existing:
                db.session.add(lead)
        
        print("💾 Committing all changes to database...")
        db.session.commit()
        
        print("✅ Database initialization completed successfully!")
        print(f"📊 Created:")
        print(f"   - {len(categories)} inventory categories")
        print(f"   - {len(warehouses)} warehouses")
        print(f"   - {len(accounts)} financial accounts")
        print(f"   - {len(employees)} employees")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(leads)} leads")
        print(f"   - Admin user: admin@edonuops.com / password")

if __name__ == "__main__":
    init_database()







