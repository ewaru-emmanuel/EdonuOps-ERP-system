#!/usr/bin/env python3
"""
Fresh Database Setup for EdonuOps
Creates a completely new database with sample data
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_fresh_database():
    """Set up a completely fresh database"""
    print("🚀 Setting up fresh database for EdonuOps")
    print("=" * 50)
    
    try:
        # Import Flask app and database
        from app import app, db
        from modules.inventory.advanced_models import (
            AdvancedProduct, ProductCategory, UnitOfMeasure
        )
        from modules.core.models import User, Organization
        
        with app.app_context():
            print("🗑️ Dropping all existing tables...")
            db.drop_all()
            
            print("🏗️ Creating fresh tables...")
            db.create_all()
            
            print("📝 Adding sample data...")
            
            # Create sample organizations
            org1 = Organization(
                name="EdonuOps Demo Company"
            )
            db.session.add(org1)
            
            # Create sample users
            admin_user = User(
                username="admin",
                email="admin@edonuops.com",
                password_hash="hashed_password_here"
            )
            db.session.add(admin_user)
            
            # Create sample UoM
            uom_data = [
                {"code": "PCS", "name": "Pieces", "description": "Individual pieces", "is_base_unit": True},
                {"code": "BOX", "name": "Boxes", "description": "Boxes of items", "is_base_unit": False},
                {"code": "KG", "name": "Kilograms", "description": "Weight in kilograms", "is_base_unit": True},
                {"code": "M", "name": "Meters", "description": "Length in meters", "is_base_unit": True},
                {"code": "L", "name": "Liters", "description": "Volume in liters", "is_base_unit": True}
            ]
            
            uoms = {}
            for uom_info in uom_data:
                uom = UnitOfMeasure(**uom_info)
                db.session.add(uom)
                uoms[uom_info["code"]] = uom
            
            # Create sample categories
            categories_data = [
                {"name": "Electronics", "description": "Electronic devices and components", "abc_class": "A"},
                {"name": "Office Supplies", "description": "Office equipment and supplies", "abc_class": "B"},
                {"name": "Furniture", "description": "Office furniture and fixtures", "abc_class": "C"},
                {"name": "Software", "description": "Software licenses and applications", "abc_class": "A"},
                {"name": "Raw Materials", "description": "Raw materials for production", "abc_class": "B"}
            ]
            
            categories = {}
            for cat_info in categories_data:
                category = ProductCategory(**cat_info)
                db.session.add(category)
                categories[cat_info["name"]] = category
            
            # Commit to get IDs
            db.session.commit()
            
            # Create sample products
            products_data = [
                {
                    "sku": "LAPTOP001",
                    "product_id": "PROD001",
                    "name": "Dell Latitude Laptop",
                    "description": "High-performance business laptop",
                    "category_id": categories["Electronics"].id,
                    "product_type": "serialized",
                    "track_serial_numbers": True,
                    "track_lots": False,
                    "track_expiry": False,
                    "base_uom_id": uoms["PCS"].id,
                    "purchase_uom_id": uoms["PCS"].id,
                    "sales_uom_id": uoms["PCS"].id,
                    "cost_method": "FIFO",
                    "standard_cost": 1200.00,
                    "current_cost": 1200.00,
                    "min_stock": 5.0,
                    "max_stock": 50.0,
                    "reorder_point": 10.0,
                    "reorder_quantity": 20.0,
                    "lead_time_days": 7,
                    "is_active": True,
                    "status": "active"
                },
                {
                    "sku": "MOUSE002",
                    "product_id": "PROD002",
                    "name": "Wireless Mouse",
                    "description": "Ergonomic wireless mouse",
                    "category_id": categories["Electronics"].id,
                    "product_type": "standard",
                    "track_serial_numbers": False,
                    "track_lots": False,
                    "track_expiry": False,
                    "base_uom_id": uoms["PCS"].id,
                    "purchase_uom_id": uoms["BOX"].id,
                    "sales_uom_id": uoms["PCS"].id,
                    "cost_method": "FIFO",
                    "standard_cost": 25.00,
                    "current_cost": 25.00,
                    "min_stock": 20.0,
                    "max_stock": 200.0,
                    "reorder_point": 30.0,
                    "reorder_quantity": 50.0,
                    "lead_time_days": 3,
                    "is_active": True,
                    "status": "active"
                },
                {
                    "sku": "PAPER003",
                    "product_id": "PROD003",
                    "name": "A4 Printer Paper",
                    "description": "High-quality A4 printer paper",
                    "category_id": categories["Office Supplies"].id,
                    "product_type": "standard",
                    "track_serial_numbers": False,
                    "track_lots": True,
                    "track_expiry": False,
                    "base_uom_id": uoms["PCS"].id,
                    "purchase_uom_id": uoms["BOX"].id,
                    "sales_uom_id": uoms["PCS"].id,
                    "cost_method": "FIFO",
                    "standard_cost": 0.05,
                    "current_cost": 0.05,
                    "min_stock": 1000.0,
                    "max_stock": 10000.0,
                    "reorder_point": 2000.0,
                    "reorder_quantity": 5000.0,
                    "lead_time_days": 5,
                    "is_active": True,
                    "status": "active"
                },
                {
                    "sku": "CHAIR004",
                    "product_id": "PROD004",
                    "name": "Ergonomic Office Chair",
                    "description": "Comfortable ergonomic office chair",
                    "category_id": categories["Furniture"].id,
                    "product_type": "standard",
                    "track_serial_numbers": False,
                    "track_lots": False,
                    "track_expiry": False,
                    "base_uom_id": uoms["PCS"].id,
                    "purchase_uom_id": uoms["PCS"].id,
                    "sales_uom_id": uoms["PCS"].id,
                    "cost_method": "FIFO",
                    "standard_cost": 350.00,
                    "current_cost": 350.00,
                    "min_stock": 2.0,
                    "max_stock": 20.0,
                    "reorder_point": 5.0,
                    "reorder_quantity": 10.0,
                    "lead_time_days": 14,
                    "is_active": True,
                    "status": "active"
                },
                {
                    "sku": "SW001",
                    "product_id": "PROD005",
                    "name": "Microsoft Office License",
                    "description": "Annual Microsoft Office 365 license",
                    "category_id": categories["Software"].id,
                    "product_type": "standard",
                    "track_serial_numbers": True,
                    "track_lots": False,
                    "track_expiry": True,
                    "base_uom_id": uoms["PCS"].id,
                    "purchase_uom_id": uoms["PCS"].id,
                    "sales_uom_id": uoms["PCS"].id,
                    "cost_method": "FIFO",
                    "standard_cost": 150.00,
                    "current_cost": 150.00,
                    "min_stock": 10.0,
                    "max_stock": 100.0,
                    "reorder_point": 20.0,
                    "reorder_quantity": 50.0,
                    "lead_time_days": 1,
                    "is_active": True,
                    "status": "active"
                }
            ]
            
            for product_info in products_data:
                product = AdvancedProduct(**product_info)
                db.session.add(product)
            
            # Commit all changes
            db.session.commit()
            
            print("✅ Fresh database setup completed successfully!")
            print(f"📊 Created:")
            print(f"   - {len(uom_data)} Units of Measure")
            print(f"   - {len(categories_data)} Product Categories")
            print(f"   - {len(products_data)} Products")
            print(f"   - 1 Organization")
            print(f"   - 1 Admin User")
            
            return True
            
    except Exception as e:
        print(f"❌ Error setting up fresh database: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_setup():
    """Verify the database setup"""
    print("\n🔍 Verifying database setup...")
    
    try:
        from app import app, db
        from modules.inventory.advanced_models import (
            AdvancedProduct, ProductCategory, UnitOfMeasure
        )
        from modules.core.models import User, Organization
        
        with app.app_context():
            # Check counts
            uom_count = UnitOfMeasure.query.count()
            category_count = ProductCategory.query.count()
            product_count = AdvancedProduct.query.count()
            user_count = User.query.count()
            org_count = Organization.query.count()
            
            print(f"✅ Verification Results:")
            print(f"   - UoM: {uom_count}")
            print(f"   - Categories: {category_count}")
            print(f"   - Products: {product_count}")
            print(f"   - Users: {user_count}")
            print(f"   - Organizations: {org_count}")
            
            # Test a sample query
            products = AdvancedProduct.query.filter_by(is_active=True).limit(3).all()
            print(f"   - Sample products: {len(products)} found")
            
            for product in products:
                print(f"     * {product.name} (SKU: {product.sku})")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 EdonuOps Fresh Database Setup")
    print("=" * 50)
    
    # Check if we're using SQLite or PostgreSQL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///edonuops.db')
    
    if 'postgresql' in database_url.lower():
        print("📊 Using PostgreSQL database")
        print("⚠️ Make sure PostgreSQL is running and accessible")
    else:
        print("📊 Using SQLite database")
    
    print()
    
    # Set up fresh database
    if not setup_fresh_database():
        print("\n❌ Database setup failed!")
        sys.exit(1)
    
    # Verify setup
    if not verify_setup():
        print("\n❌ Database verification failed!")
        sys.exit(1)
    
    print("\n🎉 FRESH DATABASE SETUP COMPLETED!")
    print("✅ Your application is ready to use with fresh sample data")
    print("✅ Start your Flask application: python run.py")
    print("✅ Login with: admin@edonuops.com")

if __name__ == "__main__":
    main()
