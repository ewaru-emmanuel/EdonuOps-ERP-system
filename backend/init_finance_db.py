#!/usr/bin/env python3
"""
Database initialization script for Advanced Finance Module
This script creates all the necessary tables and adds sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.finance.advanced_models import (
    ChartOfAccounts, GeneralLedgerEntry, AccountsPayable, AccountsReceivable,
    FixedAsset, Budget, TaxRecord, BankReconciliation, APPayment, ARPayment,
    FinanceVendor, FinanceCustomer, AuditTrail, FinancialReport, Currency, ExchangeRate,
    DepreciationSchedule, InvoiceLineItem, FinancialPeriod, JournalHeader, MaintenanceRecord
)
from datetime import datetime, date

def init_finance_database():
    """Initialize the finance database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        print("Dropping existing finance tables...")
        
        # Drop all tables first
        db.drop_all()
        print("✓ All existing tables dropped")
        
        print("Creating finance database tables...")
        
        # Create all tables
        db.create_all()
        print("✓ All tables created successfully")
        
        # Add sample data
        print("Adding sample data...")
        
        # Sample Chart of Accounts
        sample_accounts = [
            {'account_code': '1000', 'account_name': 'Cash', 'account_type': 'Asset', 'account_category': 'Current Assets'},
            {'account_code': '1100', 'account_name': 'Accounts Receivable', 'account_type': 'Asset', 'account_category': 'Current Assets'},
            {'account_code': '1200', 'account_name': 'Inventory', 'account_type': 'Asset', 'account_category': 'Current Assets'},
            {'account_code': '1500', 'account_name': 'Equipment', 'account_type': 'Asset', 'account_category': 'Fixed Assets'},
            {'account_code': '2000', 'account_name': 'Accounts Payable', 'account_type': 'Liability', 'account_category': 'Current Liabilities'},
            {'account_code': '3000', 'account_name': 'Common Stock', 'account_type': 'Equity', 'account_category': 'Shareholders Equity'},
            {'account_code': '4000', 'account_name': 'Sales Revenue', 'account_type': 'Revenue', 'account_category': 'Operating Revenue'},
            {'account_code': '5000', 'account_name': 'Cost of Goods Sold', 'account_type': 'Expense', 'account_category': 'Operating Expenses'},
            {'account_code': '6000', 'account_name': 'Operating Expenses', 'account_type': 'Expense', 'account_category': 'Operating Expenses'},
        ]
        
        for account_data in sample_accounts:
            existing = ChartOfAccounts.query.filter_by(account_code=account_data['account_code']).first()
            if not existing:
                account = ChartOfAccounts(**account_data)
                db.session.add(account)
        
        # Sample Vendors (commented out to avoid dummy data)
        # sample_vendors = [
        #     {'vendor_code': 'V001', 'vendor_name': 'ABC Supplies Inc.', 'contact_person': 'John Smith', 'email': 'john@abcsupplies.com', 'phone': '+1-555-0101'},
        #     {'vendor_code': 'V002', 'vendor_name': 'XYZ Corporation', 'contact_person': 'Jane Doe', 'email': 'jane@xyzcorp.com', 'phone': '+1-555-0102'},
        #     {'vendor_code': 'V003', 'vendor_name': 'Tech Solutions Ltd.', 'contact_person': 'Mike Johnson', 'email': 'mike@techsolutions.com', 'phone': '+1-555-0103'},
        # ]
        # 
        # for vendor_data in sample_vendors:
        #     existing = FinanceVendor.query.filter_by(vendor_code=vendor_data['vendor_code']).first()
        #     if not existing:
        #         vendor = FinanceVendor(**vendor_data)
        #         db.session.add(vendor)
        
        # Sample Customers (commented out to avoid dummy data)
        # sample_customers = [
        #     {'customer_code': 'C001', 'customer_name': 'Global Enterprises', 'contact_person': 'Sarah Wilson', 'email': 'sarah@globalent.com', 'phone': '+1-555-0201'},
        #     {'customer_code': 'C002', 'customer_name': 'Innovation Corp', 'contact_person': 'David Brown', 'email': 'david@innovationcorp.com', 'phone': '+1-555-0202'},
        #     {'customer_code': 'C003', 'customer_name': 'Future Systems', 'contact_person': 'Lisa Garcia', 'email': 'lisa@futuresystems.com', 'phone': '+1-555-0203'},
        # ]
        # 
        # for customer_data in sample_customers:
        #     existing = FinanceCustomer.query.filter_by(customer_code=customer_data['customer_code']).first()
        #     if not existing:
        #         customer = FinanceCustomer(**customer_data)
        #         db.session.add(customer)
        
        # Sample Currencies
        sample_currencies = [
            {'currency_code': 'USD', 'currency_name': 'US Dollar', 'symbol': '$', 'is_base_currency': True},
            {'currency_code': 'EUR', 'currency_name': 'Euro', 'symbol': '€', 'is_base_currency': False},
            {'currency_code': 'GBP', 'currency_name': 'British Pound', 'symbol': '£', 'is_base_currency': False},
        ]
        
        for currency_data in sample_currencies:
            existing = Currency.query.filter_by(currency_code=currency_data['currency_code']).first()
            if not existing:
                currency = Currency(**currency_data)
                db.session.add(currency)
        
        # Sample Financial Periods
        sample_periods = [
            {'period_code': '2024-01', 'period_name': 'January 2024', 'start_date': date(2024, 1, 1), 'end_date': date(2024, 1, 31)},
            {'period_code': '2024-02', 'period_name': 'February 2024', 'start_date': date(2024, 2, 1), 'end_date': date(2024, 2, 29)},
            {'period_code': '2024-03', 'period_name': 'March 2024', 'start_date': date(2024, 3, 1), 'end_date': date(2024, 3, 31)},
        ]
        
        for period_data in sample_periods:
            existing = FinancialPeriod.query.filter_by(period_code=period_data['period_code']).first()
            if not existing:
                period = FinancialPeriod(**period_data)
                db.session.add(period)
        
        # Sample Fixed Assets (commented out to avoid dummy data)
        # sample_assets = [
        #     {'asset_id': 'FA001', 'asset_name': 'Office Building', 'category': 'Buildings', 'purchase_date': date(2020, 1, 15), 'purchase_value': 500000, 'current_value': 500000, 'useful_life': 30},
        #     {'asset_id': 'FA002', 'asset_name': 'Delivery Truck', 'category': 'Vehicles', 'purchase_date': date(2021, 6, 10), 'purchase_value': 45000, 'current_value': 45000, 'useful_life': 5},
        #     {'asset_id': 'FA003', 'asset_name': 'Computer Equipment', 'category': 'Equipment', 'purchase_date': date(2022, 3, 20), 'purchase_value': 25000, 'current_value': 25000, 'useful_life': 3},
        # ]
        
        # for asset_data in sample_assets:
        #     existing = FixedAsset.query.filter_by(asset_id=asset_data['asset_id']).first()
        #     if not existing:
        #         asset = FixedAsset(**asset_data)
        #         db.session.add(asset)
        
        # Sample Maintenance Records (commented out to avoid dummy data)
        # sample_maintenance_records = [
        #     {
        #         'asset_id': 1,  # Office Building
        #         'maintenance_type': 'preventive',
        #         'maintenance_date': date(2024, 1, 15),
        #         'description': 'Annual HVAC system inspection and cleaning',
        #         'cost': 2500.0,
        #         'performed_by': 'HVAC Pro Services',
        #         'vendor': 'HVAC Pro Services',
        #         'next_maintenance_date': date(2025, 1, 15),
        #         'status': 'completed',
        #         'priority': 'normal',
        #         'parts_used': 'Air filters, cleaning supplies',
        #         'labor_hours': 8.0,
        #         'notes': 'System operating efficiently after maintenance'
        #     },
        #     {
        #         'asset_id': 2,  # Delivery Truck
        #         'maintenance_type': 'corrective',
        #         'maintenance_date': date(2024, 2, 10),
        #         'description': 'Brake system repair and replacement',
        #         'cost': 1200.0,
        #         'performed_by': 'AutoCare Center',
        #         'vendor': 'AutoCare Center',
        #         'next_maintenance_date': date(2024, 8, 10),
        #         'status': 'completed',
        #         'priority': 'high',
        #         'parts_used': 'Brake pads, brake fluid',
        #         'labor_hours': 4.0,
        #         'notes': 'Brake system fully functional after repair'
        #     },
        #     {
        #         'asset_id': 3,  # Computer Equipment
        #         'maintenance_type': 'preventive',
        #         'maintenance_date': date(2024, 3, 5),
        #         'description': 'Software updates and system optimization',
        #         'cost': 500.0,
        #         'performed_by': 'IT Support Team',
        #         'vendor': 'Internal IT',
        #         'next_maintenance_date': date(2024, 9, 5),
        #         'status': 'completed',
        #         'priority': 'normal',
        #         'parts_used': 'Software licenses',
        #         'labor_hours': 6.0,
        #         'notes': 'All systems updated and optimized'
        #     }
        # ]
        
        # for record_data in sample_maintenance_records:
        #     existing = MaintenanceRecord.query.filter_by(
        #         asset_id=record_data['asset_id'],
        #         maintenance_date=record_data['maintenance_date'],
        #         description=record_data['description']
        #     ).first()
        #     if not existing:
        #         record = MaintenanceRecord(**record_data)
        #         db.session.add(record)
        
        # Commit all changes
        db.session.commit()
        print("✓ Sample data added successfully")
        
        print("\nFinance database initialization completed!")
        print("Available endpoints:")
        print("- /api/finance/chart-of-accounts")
        print("- /api/finance/general-ledger")
        print("- /api/finance/accounts-payable")
        print("- /api/finance/accounts-receivable")
        print("- /api/finance/fixed-assets")
        print("- /api/finance/maintenance-records")
        print("- /api/finance/budgets")
        print("- /api/finance/tax-records")
        print("- /api/finance/bank-reconciliations")
        print("- /api/finance/vendors")
        print("- /api/finance/customers")
        print("- /api/finance/ap-payments")
        print("- /api/finance/ar-payments")
        print("- /api/finance/audit-trail")
        print("- /api/finance/currencies")
        print("- /api/finance/exchange-rates")
        print("- /api/finance/journal-headers")
        print("- /api/finance/depreciation-schedules")
        print("- /api/finance/invoice-line-items")
        print("- /api/finance/financial-periods")
        print("- /api/finance/reports/profit-loss")
        print("- /api/finance/reports/balance-sheet")
        print("- /api/finance/dashboard-metrics")

if __name__ == '__main__':
    init_finance_database()
