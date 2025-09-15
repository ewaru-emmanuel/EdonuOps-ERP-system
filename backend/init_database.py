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
                # ASSETS
                Account(code="1000", name="Cash and Cash Equivalents", type="asset", balance=10000.00),
                Account(code="1020", name="Business Checking", type="asset", balance=8000.00),
                Account(code="1030", name="Petty Cash", type="asset", balance=200.00),
                Account(code="1100", name="Accounts Receivable", type="asset", balance=5000.00),
                Account(code="1110", name="Allowance for Bad Debts", type="asset", balance=-500.00),
                Account(code="1200", name="Inventory", type="asset", balance=15000.00),
                Account(code="1210", name="Finished Goods", type="asset", balance=12000.00),
                Account(code="1220", name="Raw Materials", type="asset", balance=3000.00),
                Account(code="1300", name="Prepaid Expenses", type="asset", balance=2000.00),
                Account(code="1310", name="Prepaid Rent", type="asset", balance=1200.00),
                Account(code="1320", name="Prepaid Insurance", type="asset", balance=800.00),
                Account(code="1400", name="Fixed Assets", type="asset", balance=25000.00),
                Account(code="1410", name="Store Equipment", type="asset", balance=15000.00),
                Account(code="1420", name="Computer Equipment", type="asset", balance=8000.00),
                Account(code="1430", name="Accumulated Depreciation", type="asset", balance=-2000.00),
                
                # LIABILITIES
                Account(code="2000", name="Accounts Payable", type="liability", balance=3000.00),
                Account(code="2100", name="Accrued Expenses", type="liability", balance=1500.00),
                Account(code="2110", name="Accrued Wages", type="liability", balance=800.00),
                Account(code="2200", name="Short-term Loans", type="liability", balance=5000.00),
                Account(code="2300", name="Long-term Loans", type="liability", balance=10000.00),
                
                # EQUITY
                Account(code="3000", name="Owner's Equity", type="equity", balance=20000.00),
                Account(code="3100", name="Retained Earnings", type="equity", balance=15000.00),
                Account(code="3200", name="Current Year Earnings", type="equity", balance=5000.00),
                
                # REVENUE
                Account(code="4000", name="Sales Revenue", type="revenue", balance=0.00),
                Account(code="4100", name="Service Revenue", type="revenue", balance=0.00),
                
                # EXPENSES
                Account(code="5000", name="Cost of Goods Sold", type="expense", balance=0.00),
                Account(code="6000", name="Operating Expenses", type="expense", balance=0.00),
                Account(code="6100", name="Rent Expense", type="expense", balance=0.00),
                Account(code="6200", name="Utilities", type="expense", balance=0.00),
                Account(code="6300", name="Salaries and Wages", type="expense", balance=0.00),
                Account(code="6400", name="Marketing and Advertising", type="expense", balance=0.00),
                Account(code="6500", name="Insurance", type="expense", balance=0.00),
                Account(code="6600", name="Professional Services", type="expense", balance=0.00),
                Account(code="6700", name="Office Supplies", type="expense", balance=0.00),
                Account(code="6800", name="Depreciation", type="expense", balance=0.00),
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
