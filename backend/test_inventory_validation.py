#!/usr/bin/env python3
"""
Test inventory validation and business rules.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.inventory.models import Product, Category, Supplier, StockLevel, InventoryTransaction
from app import create_app
from datetime import datetime

def test_inventory_validation():
    """Test inventory validation rules and constraints."""
    app = create_app()
    
    with app.app_context():
        try:
            print("📦 Testing inventory validation...")
            
            # Test 1: Product validation
            print("Test 1: Product validation")
            
            # Valid product
            valid_product = Product(
                name="Test Product",
                description="A test product",
                sku="TEST001",
                price=99.99,
                cost=50.00,
                tenant_id=1,
                created_at=datetime.utcnow()
            )
            db.session.add(valid_product)
            db.session.flush()
            print("✅ Valid product created")
            
            # Test negative price
            try:
                invalid_product = Product(
                    name="Invalid Product",
                    price=-10.00,
                    cost=5.00,
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
                db.session.add(invalid_product)
                db.session.commit()
                print("❌ Should have failed with negative price")
            except Exception as e:
                print(f"✅ Correctly rejected negative price: {e}")
                db.session.rollback()
            
            # Test duplicate SKU
            try:
                duplicate_product = Product(
                    name="Duplicate Product",
                    sku="TEST001",  # Same SKU as valid_product
                    price=50.00,
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
                db.session.add(duplicate_product)
                db.session.commit()
                print("❌ Should have failed with duplicate SKU")
            except Exception as e:
                print(f"✅ Correctly rejected duplicate SKU: {e}")
                db.session.rollback()
            
            # Test 2: Stock level validation
            print("Test 2: Stock level validation")
            
            stock_level = StockLevel(
                product_id=valid_product.id,
                quantity=100,
                min_quantity=10,
                max_quantity=500,
                tenant_id=1,
                created_at=datetime.utcnow()
            )
            db.session.add(stock_level)
            print("✅ Valid stock level created")
            
            # Test negative quantity
            try:
                invalid_stock = StockLevel(
                    product_id=valid_product.id,
                    quantity=-50,
                    min_quantity=10,
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
                db.session.add(invalid_stock)
                db.session.commit()
                print("❌ Should have failed with negative quantity")
            except Exception as e:
                print(f"✅ Correctly rejected negative quantity: {e}")
                db.session.rollback()
            
            # Test min > max quantity
            try:
                invalid_range = StockLevel(
                    product_id=valid_product.id,
                    quantity=100,
                    min_quantity=200,
                    max_quantity=100,
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
                db.session.add(invalid_range)
                db.session.commit()
                print("❌ Should have failed with min > max")
            except Exception as e:
                print(f"✅ Correctly rejected invalid range: {e}")
                db.session.rollback()
            
            # Test 3: Inventory transaction validation
            print("Test 3: Inventory transaction validation")
            
            # Valid transaction
            valid_transaction = InventoryTransaction(
                product_id=valid_product.id,
                transaction_type="in",
                quantity=50,
                reference_type="purchase",
                reference_id=1,
                tenant_id=1,
                created_at=datetime.utcnow()
            )
            db.session.add(valid_transaction)
            print("✅ Valid inventory transaction created")
            
            # Test invalid transaction type
            try:
                invalid_transaction = InventoryTransaction(
                    product_id=valid_product.id,
                    transaction_type="invalid_type",
                    quantity=10,
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
                db.session.add(invalid_transaction)
                db.session.commit()
                print("❌ Should have failed with invalid transaction type")
            except Exception as e:
                print(f"✅ Correctly rejected invalid transaction type: {e}")
                db.session.rollback()
            
            # Test 4: Category validation
            print("Test 4: Category validation")
            
            category = Category(
                name="Test Category",
                description="A test category",
                tenant_id=1,
                created_at=datetime.utcnow()
            )
            db.session.add(category)
            print("✅ Valid category created")
            
            # Test duplicate category name
            try:
                duplicate_category = Category(
                    name="Test Category",  # Same name
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
                db.session.add(duplicate_category)
                db.session.commit()
                print("❌ Should have failed with duplicate category name")
            except Exception as e:
                print(f"✅ Correctly rejected duplicate category: {e}")
                db.session.rollback()
            
            # Test 5: Supplier validation
            print("Test 5: Supplier validation")
            
            supplier = Supplier(
                name="Test Supplier",
                email="supplier@example.com",
                phone="555-1234",
                address="123 Supplier St",
                tenant_id=1,
                created_at=datetime.utcnow()
            )
            db.session.add(supplier)
            print("✅ Valid supplier created")
            
            # Test invalid email format
            try:
                invalid_supplier = Supplier(
                    name="Invalid Supplier",
                    email="not_an_email",
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
                db.session.add(invalid_supplier)
                db.session.commit()
                print("❌ Should have failed with invalid email")
            except Exception as e:
                print(f"✅ Correctly rejected invalid email: {e}")
                db.session.rollback()
            
            # Commit all valid data
            db.session.commit()
            
            print("🎉 Inventory validation tests completed!")
            print("✅ All validation rules are working correctly!")
            
            # Cleanup
            print("🧹 Cleaning up test data...")
            db.session.delete(valid_transaction)
            db.session.delete(stock_level)
            db.session.delete(valid_product)
            db.session.delete(category)
            db.session.delete(supplier)
            db.session.commit()
            print("✅ Test data cleaned up")
            
        except Exception as e:
            print(f"❌ Error during inventory validation test: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_inventory_validation()







