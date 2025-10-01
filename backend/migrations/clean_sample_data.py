#!/usr/bin/env python3
"""
Clean sample data from the database for production deployment.
This script removes all test data while preserving the database structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.database import db
from modules.core.user_preferences_models import UserPreferences
from modules.core.tenant_models import Tenant
from modules.core.permission_models import Permission, Role, UserRole
from modules.core.audit_models import AuditLog
from modules.finance.models import *
from modules.hr.models import *
from modules.sales.models import *
from modules.inventory.models import *
from app import create_app

def clean_sample_data():
    """Remove all sample/test data from the database."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧹 Starting database cleanup...")
            
            # Delete sample data from all modules
            tables_to_clean = [
                # Audit logs
                AuditLog,
                
                # Finance module
                Transaction, Account, Budget, Invoice, Payment,
                
                # HR module  
                Employee, Department, Position, Payroll, LeaveRequest,
                
                # Sales module
                Customer, SalesOrder, SalesOrderItem, Quote, QuoteItem,
                
                # Inventory module
                Product, Category, Supplier, PurchaseOrder, PurchaseOrderItem,
                InventoryTransaction, StockLevel,
                
                # User preferences and roles (keep admin user)
                UserPreferences,
                UserRole,
                
                # Keep core tables: User, Tenant, Role, Permission
            ]
            
            total_deleted = 0
            for model in tables_to_clean:
                try:
                    count = model.query.count()
                    if count > 0:
                        model.query.delete()
                        total_deleted += count
                        print(f"✅ Cleaned {count} records from {model.__tablename__}")
                except Exception as e:
                    print(f"⚠️  Could not clean {model.__tablename__}: {e}")
            
            # Reset auto-increment counters
            db.engine.execute("ALTER TABLE transactions AUTO_INCREMENT = 1")
            db.engine.execute("ALTER TABLE accounts AUTO_INCREMENT = 1") 
            db.engine.execute("ALTER TABLE invoices AUTO_INCREMENT = 1")
            db.engine.execute("ALTER TABLE employees AUTO_INCREMENT = 1")
            db.engine.execute("ALTER TABLE customers AUTO_INCREMENT = 1")
            db.engine.execute("ALTER TABLE sales_orders AUTO_INCREMENT = 1")
            db.engine.execute("ALTER TABLE products AUTO_INCREMENT = 1")
            db.engine.execute("ALTER TABLE suppliers AUTO_INCREMENT = 1")
            db.engine.execute("ALTER TABLE purchase_orders AUTO_INCREMENT = 1")
            
            db.session.commit()
            
            print(f"🎉 Database cleanup completed!")
            print(f"📊 Total records deleted: {total_deleted}")
            print("✨ Database is now clean and ready for production!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during cleanup: {e}")
            raise

if __name__ == "__main__":
    clean_sample_data()







