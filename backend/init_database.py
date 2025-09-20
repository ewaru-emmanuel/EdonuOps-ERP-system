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
            
            # Finance accounts will be created automatically by the auto-journal engine as needed
            print("✅ Finance accounts will be auto-created when transactions occur")
            
            # Inventory categories, warehouses, and products will be created by users as needed
            print("✅ Inventory system ready - users will add their own data")
            
            
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
