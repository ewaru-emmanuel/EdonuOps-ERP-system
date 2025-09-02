#!/usr/bin/env python3
"""
Test script to verify database connectivity and data storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.inventory.advanced_models import AdvancedProduct, ProductCategory, UnitOfMeasure

def test_database_status():
    """Test database connectivity and data storage"""
    
    print("🔍 Testing Database Status...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Database Connection
            print("\n1. Testing Database Connection...")
            db.engine.execute("SELECT 1")
            print("✅ Database connection: SUCCESS")
            
            # Test 2: Check if tables exist
            print("\n2. Checking if tables exist...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'advanced_products',
                'advanced_product_categories', 
                'advanced_uom',
                'advanced_stock_levels'
            ]
            
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                print("   Tables found: ", tables)
                return False
            else:
                print("✅ All required tables exist")
            
            # Test 3: Check if data exists
            print("\n3. Checking existing data...")
            
            product_count = AdvancedProduct.query.count()
            category_count = ProductCategory.query.count()
            uom_count = UnitOfMeasure.query.count()
            
            print(f"   Products: {product_count}")
            print(f"   Categories: {category_count}")
            print(f"   Units of Measure: {uom_count}")
            
            if product_count == 0:
                print("⚠️  No products found - database may be empty")
                print("   Run: python init_advanced_inventory_db.py to seed data")
            
            # Test 4: Try to create a test product
            print("\n4. Testing data creation...")
            
            # Check if we have categories and UoMs
            if category_count == 0:
                print("   Creating test category...")
                test_category = ProductCategory(name="Test Category", description="Test")
                db.session.add(test_category)
                db.session.commit()
                category_id = test_category.id
            else:
                category_id = ProductCategory.query.first().id
            
            if uom_count == 0:
                print("   Creating test UoM...")
                test_uom = UnitOfMeasure(name="Each", code="EA", description="Test")
                db.session.add(test_uom)
                db.session.commit()
                uom_id = test_uom.id
            else:
                uom_id = UnitOfMeasure.query.first().id
            
            # Create test product
            test_product = AdvancedProduct(
                sku="TEST-DB-001",
                name="Database Test Product",
                description="Testing database storage",
                category_id=category_id,
                base_uom_id=uom_id,
                status="active"
            )
            
            db.session.add(test_product)
            db.session.commit()
            
            print("✅ Test product created successfully")
            print(f"   Product ID: {test_product.id}")
            
            # Clean up test product
            db.session.delete(test_product)
            db.session.commit()
            print("✅ Test product cleaned up")
            
            print("\n🎉 Database is working correctly!")
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

if __name__ == "__main__":
    test_database_status()
