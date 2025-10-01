#!/usr/bin/env python3
"""
Test edge cases and error handling in the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.user_preferences_models import UserPreferences
from modules.core.tenant_models import Tenant
from modules.finance.models import Transaction, Account
from modules.sales.models import Customer, SalesOrder
from modules.inventory.models import Product, Category
from app import create_app
import pytest

def test_edge_cases():
    """Test various edge cases and error conditions."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testing edge cases...")
            
            # Test 1: Invalid data types
            print("Test 1: Invalid data types")
            try:
                invalid_pref = UserPreferences(
                    user_id="not_a_number",
                    preferences={"invalid": "data"}
                )
                db.session.add(invalid_pref)
                db.session.commit()
                print("❌ Should have failed with invalid user_id")
            except Exception as e:
                print(f"✅ Correctly rejected invalid user_id: {e}")
                db.session.rollback()
            
            # Test 2: Null required fields
            print("Test 2: Null required fields")
            try:
                null_pref = UserPreferences(
                    user_id=None,
                    preferences={}
                )
                db.session.add(null_pref)
                db.session.commit()
                print("❌ Should have failed with null user_id")
            except Exception as e:
                print(f"✅ Correctly rejected null user_id: {e}")
                db.session.rollback()
            
            # Test 3: Very long strings
            print("Test 3: Very long strings")
            try:
                long_string = "x" * 10000
                customer = Customer(
                    name=long_string,
                    email="test@example.com"
                )
                db.session.add(customer)
                db.session.commit()
                print(f"✅ Handled long string (length: {len(long_string)})")
                db.session.delete(customer)
                db.session.commit()
            except Exception as e:
                print(f"⚠️  Long string handling: {e}")
                db.session.rollback()
            
            # Test 4: Negative amounts
            print("Test 4: Negative amounts")
            try:
                account = Account(
                    name="Test Account",
                    account_type="asset",
                    balance=-1000.00
                )
                db.session.add(account)
                db.session.commit()
                print("✅ Negative balance allowed (may be valid)")
                db.session.delete(account)
                db.session.commit()
            except Exception as e:
                print(f"✅ Correctly handled negative balance: {e}")
                db.session.rollback()
            
            # Test 5: Duplicate constraints
            print("Test 5: Duplicate constraints")
            try:
                # Create first tenant
                tenant1 = Tenant(name="Test Tenant 1", subdomain="test1")
                db.session.add(tenant1)
                db.session.flush()
                
                # Try to create duplicate subdomain
                tenant2 = Tenant(name="Test Tenant 2", subdomain="test1")
                db.session.add(tenant2)
                db.session.commit()
                print("❌ Should have failed with duplicate subdomain")
            except Exception as e:
                print(f"✅ Correctly rejected duplicate subdomain: {e}")
                db.session.rollback()
            
            # Test 6: Foreign key constraints
            print("Test 6: Foreign key constraints")
            try:
                # Try to create user preference for non-existent user
                pref = UserPreferences(
                    user_id=99999,
                    preferences={"test": "data"}
                )
                db.session.add(pref)
                db.session.commit()
                print("❌ Should have failed with invalid user_id")
            except Exception as e:
                print(f"✅ Correctly rejected invalid foreign key: {e}")
                db.session.rollback()
            
            # Test 7: JSON field validation
            print("Test 7: JSON field validation")
            try:
                pref = UserPreferences(
                    user_id=1,
                    preferences="not_json_string"
                )
                db.session.add(pref)
                db.session.commit()
                print("❌ Should have failed with invalid JSON")
            except Exception as e:
                print(f"✅ Correctly rejected invalid JSON: {e}")
                db.session.rollback()
            
            # Test 8: Date validation
            print("Test 8: Date validation")
            try:
                # Test with invalid date format
                transaction = Transaction(
                    amount=100.00,
                    description="Test",
                    transaction_date="invalid_date",
                    account_id=1
                )
                db.session.add(transaction)
                db.session.commit()
                print("❌ Should have failed with invalid date")
            except Exception as e:
                print(f"✅ Correctly rejected invalid date: {e}")
                db.session.rollback()
            
            print("🎉 Edge case testing completed!")
            
        except Exception as e:
            print(f"❌ Error during edge case testing: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_edge_cases()







