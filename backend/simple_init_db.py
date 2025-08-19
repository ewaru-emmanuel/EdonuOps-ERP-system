#!/usr/bin/env python3
"""
Comprehensive database initialization script for EdonuOps
Creates all tables and ensures proper backend integration
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Initialize the database with all tables"""
    try:
        print("🚀 Initializing EdonuOps Database...")
        
        # Import Flask app and database
        from app import create_app, db
        
        # Create the Flask app
        app = create_app()
        
        with app.app_context():
            print("📊 Creating database tables...")
            
            # Import all models to ensure they're registered
            from modules.core.models import User, Role, Organization
            from modules.hr.models import Employee, Payroll, Recruitment
            from modules.inventory.models import Category, Product, Warehouse, InventoryTransaction
            from modules.crm.models import Contact, Lead, Opportunity
            from modules.finance.models import Account, JournalEntry, JournalLine
            
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully")
            
            # Insert default data
            print("📝 Inserting default data...")
            
            # Create default roles
            admin_role = Role.query.filter_by(role_name='admin').first()
            if not admin_role:
                admin_role = Role(role_name='admin', permissions='["all"]')
                db.session.add(admin_role)
            
            user_role = Role.query.filter_by(role_name='user').first()
            if not user_role:
                user_role = Role(role_name='user', permissions='["read"]')
                db.session.add(user_role)
            
            # Create default organization
            org = Organization.query.filter_by(name='EdonuOps').first()
            if not org:
                org = Organization(name='EdonuOps')
                db.session.add(org)
            
            db.session.commit()
            
            # Create default admin user
            admin_user = User.query.filter_by(email='admin@edonuops.com').first()
            if not admin_user:
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    username='admin',
                    email='admin@edonuops.com',
                    password_hash=generate_password_hash('password'),
                    role_id=admin_role.id,
                    organization_id=org.id
                )
                db.session.add(admin_user)
            
            # Create sample data for testing
            print("📋 Creating sample data...")
            
            # Sample employees
            if Employee.query.count() == 0:
                sample_employees = [
                    Employee(
                        first_name='John',
                        last_name='Smith',
                        email='john.smith@company.com',
                        phone='+1-555-0123',
                        position='Software Engineer',
                        department='Engineering',
                        salary=85000.00,
                        hire_date=datetime(2023, 1, 15).date(),
                        status='active'
                    ),
                    Employee(
                        first_name='Sarah',
                        last_name='Johnson',
                        email='sarah.johnson@company.com',
                        phone='+1-555-0124',
                        position='Marketing Manager',
                        department='Marketing',
                        salary=75000.00,
                        hire_date=datetime(2023, 3, 20).date(),
                        status='active'
                    )
                ]
                for emp in sample_employees:
                    db.session.add(emp)
            
            # Sample products
            if Product.query.count() == 0:
                # Create a default category first
                default_category = Category.query.filter_by(name='General').first()
                if not default_category:
                    default_category = Category(name='General', description='General products')
                    db.session.add(default_category)
                    db.session.commit()
                
                sample_products = [
                    Product(
                        sku='PROD-001',
                        name='Laptop Computer',
                        description='High-performance laptop for business use',
                        category_id=default_category.id,
                        unit='pcs',
                        standard_cost=800.00,
                        current_cost=800.00,
                        current_stock=50,
                        min_stock=10,
                        max_stock=100,
                        is_active=True
                    ),
                    Product(
                        sku='PROD-002',
                        name='Office Chair',
                        description='Ergonomic office chair',
                        category_id=default_category.id,
                        unit='pcs',
                        standard_cost=200.00,
                        current_cost=200.00,
                        current_stock=25,
                        min_stock=5,
                        max_stock=50,
                        is_active=True
                    )
                ]
                for prod in sample_products:
                    db.session.add(prod)
            
            # Sample contacts
            if Contact.query.count() == 0:
                sample_contacts = [
                    Contact(
                        first_name='Alice',
                        last_name='Brown',
                        email='alice.brown@customer.com',
                        phone='+1-555-0101',
                        company='ABC Corp',
                        type='customer',
                        status='active'
                    ),
                    Contact(
                        first_name='Bob',
                        last_name='Wilson',
                        email='bob.wilson@vendor.com',
                        phone='+1-555-0102',
                        company='XYZ Supplies',
                        type='vendor',
                        status='active'
                    )
                ]
                for contact in sample_contacts:
                    db.session.add(contact)
            
            # Sample accounts
            if Account.query.count() == 0:
                sample_accounts = [
                    Account(code='1000', name='Cash', type='asset', is_active=True),
                    Account(code='1100', name='Accounts Receivable', type='asset', is_active=True),
                    Account(code='2000', name='Accounts Payable', type='liability', is_active=True),
                    Account(code='3000', name='Common Stock', type='equity', is_active=True),
                    Account(code='4000', name='Sales Revenue', type='revenue', is_active=True),
                    Account(code='5000', name='Cost of Goods Sold', type='expense', is_active=True)
                ]
                for account in sample_accounts:
                    db.session.add(account)
            
            # Sample warehouse
            if Warehouse.query.count() == 0:
                default_warehouse = Warehouse(
                    name='Main Warehouse',
                    location='123 Business St, City, State 12345',
                    capacity=10000,
                    is_active=True
                )
                db.session.add(default_warehouse)
            
            db.session.commit()
            print("✅ Sample data created successfully")
            
            print("\n🎉 Database initialization completed successfully!")
            print("📁 Database file: edonuops.db")
            print("🔑 Admin user: admin@edonuops.com / password")
            print("📊 Sample data has been created for testing")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n✅ Database is ready for use!")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
