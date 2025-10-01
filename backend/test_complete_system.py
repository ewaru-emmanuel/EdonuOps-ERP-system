#!/usr/bin/env python3
"""
Complete system integration test for the ERP system.
Tests all modules working together.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.user_preferences_models import UserPreferences
from modules.core.tenant_models import Tenant
from modules.finance.models import Transaction, Account, Budget
from modules.sales.models import Customer, SalesOrder, SalesOrderItem
from modules.inventory.models import Product, Category, Supplier, StockLevel
from modules.hr.models import Employee, Department
from app import create_app
from datetime import datetime, date

def test_complete_system():
    """Test the complete ERP system integration."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Starting complete system integration test...")
            
            # Step 1: Create tenant
            print("Step 1: Creating tenant...")
            tenant = Tenant(
                name="Test Company",
                subdomain="testcompany",
                created_at=datetime.utcnow()
            )
            db.session.add(tenant)
            db.session.flush()
            tenant_id = tenant.id
            print(f"✅ Tenant created with ID: {tenant_id}")
            
            # Step 2: Create user preferences
            print("Step 2: Creating user preferences...")
            user_pref = UserPreferences(
                user_id=1,
                tenant_id=tenant_id,
                preferences={
                    "modules": ["finance", "sales", "inventory", "hr"],
                    "dashboard_layout": "grid",
                    "theme": "light"
                },
                created_at=datetime.utcnow()
            )
            db.session.add(user_pref)
            print("✅ User preferences created")
            
            # Step 3: Create financial accounts
            print("Step 3: Creating financial accounts...")
            cash_account = Account(
                name="Cash Account",
                account_type="asset",
                balance=10000.00,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            revenue_account = Account(
                name="Sales Revenue",
                account_type="revenue",
                balance=0.00,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add_all([cash_account, revenue_account])
            db.session.flush()
            print("✅ Financial accounts created")
            
            # Step 4: Create inventory
            print("Step 4: Creating inventory...")
            category = Category(
                name="Electronics",
                description="Electronic products",
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(category)
            db.session.flush()
            
            product = Product(
                name="Laptop Computer",
                description="High-performance laptop",
                sku="LAPTOP001",
                price=999.99,
                cost=600.00,
                category_id=category.id,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(product)
            db.session.flush()
            
            stock_level = StockLevel(
                product_id=product.id,
                quantity=50,
                min_quantity=10,
                max_quantity=100,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(stock_level)
            print("✅ Inventory created")
            
            # Step 5: Create customer
            print("Step 5: Creating customer...")
            customer = Customer(
                name="John Doe",
                email="john@example.com",
                phone="555-1234",
                address="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001",
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(customer)
            db.session.flush()
            print("✅ Customer created")
            
            # Step 6: Create sales order
            print("Step 6: Creating sales order...")
            sales_order = SalesOrder(
                customer_id=customer.id,
                order_date=date.today(),
                status="pending",
                total_amount=999.99,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(sales_order)
            db.session.flush()
            
            order_item = SalesOrderItem(
                order_id=sales_order.id,
                product_id=product.id,
                quantity=1,
                unit_price=999.99,
                total_price=999.99,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(order_item)
            print("✅ Sales order created")
            
            # Step 7: Create financial transaction
            print("Step 7: Creating financial transaction...")
            transaction = Transaction(
                account_id=cash_account.id,
                amount=999.99,
                transaction_type="credit",
                description="Sale of laptop computer",
                reference_id=sales_order.id,
                reference_type="sales_order",
                transaction_date=date.today(),
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(transaction)
            print("✅ Financial transaction created")
            
            # Step 8: Create HR data
            print("Step 8: Creating HR data...")
            department = Department(
                name="Sales",
                description="Sales department",
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(department)
            db.session.flush()
            
            employee = Employee(
                first_name="Jane",
                last_name="Smith",
                email="jane@testcompany.com",
                phone="555-5678",
                department_id=department.id,
                position="Sales Manager",
                hire_date=date.today(),
                salary=50000.00,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(employee)
            print("✅ HR data created")
            
            # Step 9: Update balances
            print("Step 9: Updating account balances...")
            cash_account.balance += 999.99
            revenue_account.balance += 999.99
            print("✅ Account balances updated")
            
            # Step 10: Update inventory
            print("Step 10: Updating inventory...")
            stock_level.quantity -= 1
            print("✅ Inventory updated")
            
            # Commit all changes
            db.session.commit()
            
            # Verify data integrity
            print("Step 11: Verifying data integrity...")
            
            # Check account balances
            cash_balance = Account.query.filter_by(id=cash_account.id).first().balance
            revenue_balance = Account.query.filter_by(id=revenue_account.id).first().balance
            print(f"✅ Cash balance: ${cash_balance}")
            print(f"✅ Revenue balance: ${revenue_balance}")
            
            # Check inventory
            stock_qty = StockLevel.query.filter_by(product_id=product.id).first().quantity
            print(f"✅ Stock quantity: {stock_qty}")
            
            # Check sales order status
            order_status = SalesOrder.query.filter_by(id=sales_order.id).first().status
            print(f"✅ Order status: {order_status}")
            
            print("🎉 Complete system integration test PASSED!")
            print("✨ All modules are working together correctly!")
            
            # Cleanup (optional)
            cleanup = input("Do you want to clean up test data? (y/n): ").lower() == 'y'
            if cleanup:
                print("🧹 Cleaning up test data...")
                db.session.delete(transaction)
                db.session.delete(order_item)
                db.session.delete(sales_order)
                db.session.delete(customer)
                db.session.delete(stock_level)
                db.session.delete(product)
                db.session.delete(category)
                db.session.delete(employee)
                db.session.delete(department)
                db.session.delete(revenue_account)
                db.session.delete(cash_account)
                db.session.delete(user_pref)
                db.session.delete(tenant)
                db.session.commit()
                print("✅ Test data cleaned up")
            
        except Exception as e:
            print(f"❌ Error during system integration test: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_complete_system()







