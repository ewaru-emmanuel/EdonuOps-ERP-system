#!/usr/bin/env python3
"""
Database initialization script for EdonuOps
This script creates the database tables and adds some initial data
"""

from app import create_app, db
from modules.core.models import User, Role, Organization
from modules.finance.models import Account
from modules.inventory.models import Category, Product, Warehouse
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Check if we already have data
            if User.query.first():
                print("✓ Database already contains data, skipping initialization")
                return
            
            # Create default organization
            print("Creating default organization...")
            default_org = Organization(
                name="EdonuOps Default Organization",
                created_at=datetime.utcnow()
            )
            db.session.add(default_org)
            db.session.flush()  # Get the ID
            
            # Create default roles
            print("Creating default roles...")
            admin_role = Role(
                role_name="Administrator",
                permissions=["*"]
            )
            user_role = Role(
                role_name="User",
                permissions=["read", "write"]
            )
            db.session.add_all([admin_role, user_role])
            db.session.flush()
            
            # Create default admin user
            print("Creating default admin user...")
            admin_user = User(
                username="admin",
                email="admin@edonuops.com",
                password_hash=generate_password_hash("admin123"),
                role_id=admin_role.id,
                organization_id=default_org.id
            )
            db.session.add(admin_user)
            
            # Create sample finance accounts
            print("Creating sample finance accounts...")
            sample_accounts = [
                Account(code="1000", name="Cash", type="asset", balance=10000.00),
                Account(code="1100", name="Accounts Receivable", type="asset", balance=5000.00),
                Account(code="2000", name="Accounts Payable", type="liability", balance=3000.00),
                Account(code="3000", name="Owner's Equity", type="equity", balance=12000.00),
                Account(code="4000", name="Sales Revenue", type="revenue", balance=0.00),
                Account(code="5000", name="Cost of Goods Sold", type="expense", balance=0.00),
            ]
            db.session.add_all(sample_accounts)
            
            # Create sample inventory categories
            print("Creating sample inventory categories...")
            sample_categories = [
                Category(name="Electronics", description="Electronic devices and accessories"),
                Category(name="Office Supplies", description="Office equipment and supplies"),
                Category(name="Furniture", description="Office furniture and fixtures"),
            ]
            db.session.add_all(sample_categories)
            db.session.flush()
            
            # Create sample warehouse
            print("Creating sample warehouse...")
            main_warehouse = Warehouse(
                name="Main Warehouse",
                location="123 Business St, City, State 12345",
                capacity=10000
            )
            db.session.add(main_warehouse)
            
            # Create sample products
            print("Creating sample products...")
            sample_products = [
                Product(
                    name="Laptop Computer",
                    sku="LAPTOP-001",
                    price=999.99,
                    current_stock=10,
                    category_id=sample_categories[0].id,
                    current_cost=800.00,
                    min_stock=2
                ),
                Product(
                    name="Office Chair",
                    sku="CHAIR-001",
                    price=299.99,
                    current_stock=5,
                    category_id=sample_categories[2].id,
                    current_cost=200.00,
                    min_stock=1
                ),
                Product(
                    name="Printer Paper",
                    sku="PAPER-001",
                    price=19.99,
                    current_stock=100,
                    category_id=sample_categories[1].id,
                    current_cost=15.00,
                    min_stock=20
                ),
            ]
            db.session.add_all(sample_products)
            
            # Create sample HCM departments
            print("Creating sample HCM departments...")
            from modules.hcm.models import Department
            sample_departments = [
                Department(name="Engineering", code="ENG", description="Software development team"),
                Department(name="Marketing", code="MKT", description="Marketing and sales team"),
                Department(name="Human Resources", code="HR", description="HR and recruitment team"),
                Department(name="Finance", code="FIN", description="Finance and accounting team"),
            ]
            db.session.add_all(sample_departments)
            db.session.flush()
            
            # Create sample HCM employees
            print("Creating sample HCM employees...")
            from modules.hcm.models import Employee
            sample_employees = [
                Employee(
                    first_name="John",
                    last_name="Doe",
                    email="john.doe@company.com",
                    phone="+1-555-0101",
                    position="Software Engineer",
                    department_id=sample_departments[0].id,
                    salary=75000.00,
                    status="active",
                    hire_date=datetime(2023, 1, 15)
                ),
                Employee(
                    first_name="Jane",
                    last_name="Smith",
                    email="jane.smith@company.com",
                    phone="+1-555-0102",
                    position="Marketing Manager",
                    department_id=sample_departments[1].id,
                    salary=65000.00,
                    status="active",
                    hire_date=datetime(2023, 3, 20)
                ),
                Employee(
                    first_name="Mike",
                    last_name="Johnson",
                    email="mike.johnson@company.com",
                    phone="+1-555-0103",
                    position="Sales Representative",
                    department_id=sample_departments[1].id,
                    salary=55000.00,
                    status="active",
                    hire_date=datetime(2023, 6, 10)
                ),
            ]
            db.session.add_all(sample_employees)
            db.session.flush()
            
            # Create sample HCM payroll records
            print("Creating sample HCM payroll records...")
            from modules.hcm.models import Payroll
            sample_payroll = [
                Payroll(
                    employee_id=sample_employees[0].id,
                    period="2024-01",
                    gross_pay=7500.00,
                    net_pay=5625.00,
                    status="paid"
                ),
                Payroll(
                    employee_id=sample_employees[1].id,
                    period="2024-01",
                    gross_pay=6500.00,
                    net_pay=4875.00,
                    status="paid"
                ),
                Payroll(
                    employee_id=sample_employees[2].id,
                    period="2024-01",
                    gross_pay=5500.00,
                    net_pay=4125.00,
                    status="pending"
                ),
            ]
            db.session.add_all(sample_payroll)
            
            # Create sample HCM recruitment records
            print("Creating sample HCM recruitment records...")
            from modules.hcm.models import Recruitment
            sample_recruitment = [
                Recruitment(
                    position="Senior Developer",
                    department="Engineering",
                    status="Open",
                    applications=15
                ),
                Recruitment(
                    position="Product Manager",
                    department="Product",
                    status="Closed",
                    applications=8
                ),
                Recruitment(
                    position="UX Designer",
                    department="Design",
                    status="Open",
                    applications=12
                ),
            ]
            db.session.add_all(sample_recruitment)
            
            # Commit all changes
            db.session.commit()
            print("✓ Database initialized successfully!")
            print("\nDefault login credentials:")
            print("Username: admin")
            print("Email: admin@edonuops.com")
            print("Password: admin123")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error initializing database: {e}")
            raise

if __name__ == '__main__':
    init_database()
