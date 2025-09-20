#!/usr/bin/env python3
"""
Database migration script to add multi-currency support
This script adds the necessary tables and fields for multi-currency inventory valuation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from modules.finance.advanced_models import ExchangeRate, CompanySettings
from modules.inventory.advanced_models import AdvancedProduct, AdvancedInventoryTransaction
from sqlalchemy import text

def add_multi_currency_support():
    """Add multi-currency support to the database"""
    
    with app.app_context():
        try:
            print("Starting multi-currency support migration...")
            
            # 1. Create exchange_rates table
            print("Creating exchange_rates table...")
            db.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS advanced_exchange_rates (
                    id SERIAL PRIMARY KEY,
                    from_currency VARCHAR(3) NOT NULL,
                    to_currency VARCHAR(3) NOT NULL,
                    rate_date DATE NOT NULL,
                    exchange_rate FLOAT NOT NULL,
                    rate_type VARCHAR(20) DEFAULT 'spot',
                    source VARCHAR(50) DEFAULT 'manual',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_exchange_rate UNIQUE (from_currency, to_currency, rate_date)
                );
            """))
            
            # 2. Create company_settings table
            print("Creating company_settings table...")
            db.engine.execute(text("""
                CREATE TABLE IF NOT EXISTS advanced_company_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type VARCHAR(20) DEFAULT 'string',
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 3. Add currency fields to products table
            print("Adding currency fields to products table...")
            try:
                db.engine.execute(text("""
                    ALTER TABLE advanced_products 
                    ADD COLUMN cost_currency VARCHAR(3) DEFAULT 'USD';
                """))
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"Warning: Could not add cost_currency column: {e}")
            
            try:
                db.engine.execute(text("""
                    ALTER TABLE advanced_products 
                    ADD COLUMN base_currency_cost FLOAT DEFAULT 0.0;
                """))
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"Warning: Could not add base_currency_cost column: {e}")
            
            # 4. Add currency fields to inventory transactions table
            print("Adding currency fields to inventory transactions table...")
            try:
                db.engine.execute(text("""
                    ALTER TABLE advanced_inventory_transactions 
                    ADD COLUMN transaction_currency VARCHAR(3) DEFAULT 'USD';
                """))
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"Warning: Could not add transaction_currency column: {e}")
            
            try:
                db.engine.execute(text("""
                    ALTER TABLE advanced_inventory_transactions 
                    ADD COLUMN exchange_rate FLOAT DEFAULT 1.0;
                """))
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"Warning: Could not add exchange_rate column: {e}")
            
            try:
                db.engine.execute(text("""
                    ALTER TABLE advanced_inventory_transactions 
                    ADD COLUMN base_currency_unit_cost FLOAT DEFAULT 0.0;
                """))
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"Warning: Could not add base_currency_unit_cost column: {e}")
            
            try:
                db.engine.execute(text("""
                    ALTER TABLE advanced_inventory_transactions 
                    ADD COLUMN base_currency_total_cost FLOAT DEFAULT 0.0;
                """))
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"Warning: Could not add base_currency_total_cost column: {e}")
            
            # 5. Insert default base currency setting
            print("Setting default base currency...")
            db.engine.execute(text("""
                INSERT INTO advanced_company_settings (setting_key, setting_value, setting_type, description)
                VALUES ('base_currency', 'USD', 'string', 'Company base currency for multi-currency operations')
                ON CONFLICT (setting_key) DO NOTHING;
            """))
            
            # 6. Exchange rates will be added by users as needed
            print("✅ Exchange rate system ready - users will add rates as needed")
            
            # 7. Update existing products to have USD as default currency
            print("Updating existing products with default currency...")
            db.engine.execute(text("""
                UPDATE advanced_products 
                SET cost_currency = 'USD', base_currency_cost = current_cost 
                WHERE cost_currency IS NULL;
            """))
            
            # 8. Update existing inventory transactions
            print("Updating existing inventory transactions...")
            db.engine.execute(text("""
                UPDATE advanced_inventory_transactions 
                SET transaction_currency = 'USD', 
                    exchange_rate = 1.0,
                    base_currency_unit_cost = unit_cost,
                    base_currency_total_cost = unit_cost * quantity
                WHERE transaction_currency IS NULL;
            """))
            
            print("Multi-currency support migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_multi_currency_support()
