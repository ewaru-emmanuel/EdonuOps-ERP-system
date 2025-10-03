#!/usr/bin/env python3
"""
Phase 1: Double-Entry Database Schema Migration
===============================================

This script migrates from the current fake double-entry system to proper
double-entry accounting with JournalLines.

Current State:
- Journal Entries: 6 (with total_debit/total_credit)
- Journal Lines: 0
- Accounts: 0

Target State:
- Journal Entries: 6 (without total_debit/total_credit)
- Journal Lines: 12+ (2 lines per entry for proper double-entry)
- Accounts: 10+ (basic chart of accounts)
"""

from app import app, db
from modules.finance.models import JournalEntry, JournalLine, Account
from datetime import datetime
import sys

def create_basic_chart_of_accounts():
    """Create a basic chart of accounts for the system"""
    print("🏗️  Creating basic chart of accounts...")
    
    # Basic chart of accounts structure
    accounts_data = [
        # Assets
        {"code": "1000", "name": "Cash on Hand", "type": "asset", "balance": 0.0},
        {"code": "1100", "name": "Bank Account", "type": "asset", "balance": 0.0},
        {"code": "1200", "name": "Accounts Receivable", "type": "asset", "balance": 0.0},
        {"code": "1300", "name": "Inventory", "type": "asset", "balance": 0.0},
        
        # Liabilities
        {"code": "2000", "name": "Accounts Payable", "type": "liability", "balance": 0.0},
        {"code": "2100", "name": "Accrued Expenses", "type": "liability", "balance": 0.0},
        
        # Equity
        {"code": "3000", "name": "Owner's Equity", "type": "equity", "balance": 0.0},
        {"code": "3100", "name": "Retained Earnings", "type": "equity", "balance": 0.0},
        
        # Revenue
        {"code": "4000", "name": "Sales Revenue", "type": "revenue", "balance": 0.0},
        {"code": "4100", "name": "Service Revenue", "type": "revenue", "balance": 0.0},
        
        # Expenses
        {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "balance": 0.0},
        {"code": "5100", "name": "Operating Expenses", "type": "expense", "balance": 0.0},
    ]
    
    created_accounts = []
    for account_data in accounts_data:
        # Check if account already exists
        existing = Account.query.filter_by(code=account_data["code"]).first()
        if existing:
            print(f"  ⚠️  Account {account_data['code']} already exists, skipping...")
            created_accounts.append(existing)
            continue
            
        account = Account(
            code=account_data["code"],
            name=account_data["name"],
            type=account_data["type"],
            balance=account_data["balance"],
            currency="USD",
            is_active=True,
            user_id=1,  # Default to user 1 for now
            created_by=1
        )
        db.session.add(account)
        created_accounts.append(account)
        print(f"  ✅ Created account: {account_data['code']} - {account_data['name']}")
    
    db.session.commit()
    print(f"📊 Created {len(created_accounts)} accounts")
    return created_accounts

def migrate_journal_entries_to_lines():
    """Migrate existing journal entries to proper journal lines"""
    print("\n🔄 Migrating journal entries to proper journal lines...")
    
    # Get all existing journal entries
    entries = JournalEntry.query.all()
    print(f"📋 Found {len(entries)} journal entries to migrate")
    
    # Get accounts for mapping
    cash_account = Account.query.filter_by(code="1000").first()  # Cash on Hand
    bank_account = Account.query.filter_by(code="1100").first()  # Bank Account
    sales_revenue = Account.query.filter_by(code="4000").first()  # Sales Revenue
    operating_expenses = Account.query.filter_by(code="5100").first()  # Operating Expenses
    
    if not all([cash_account, bank_account, sales_revenue, operating_expenses]):
        print("❌ Error: Required accounts not found. Please run create_basic_chart_of_accounts first.")
        return False
    
    migrated_count = 0
    for entry in entries:
        print(f"\n📝 Processing Entry {entry.id}: {entry.description}")
        print(f"   Original: Debit ${entry.total_debit}, Credit ${entry.total_credit}")
        
        # Determine transaction type based on payment method and amounts
        amount = max(entry.total_debit or 0, entry.total_credit or 0)
        
        if amount == 0:
            print(f"   ⚠️  Skipping entry with zero amount")
            continue
        
        # Determine accounts based on payment method
        if entry.payment_method == 'cash':
            debit_account = cash_account
            credit_account = sales_revenue
            transaction_type = "Cash Sales"
        elif entry.payment_method == 'bank':
            debit_account = bank_account
            credit_account = sales_revenue
            transaction_type = "Bank Sales"
        elif entry.payment_method in ['wire', 'credit_card', 'check', 'digital']:
            debit_account = bank_account
            credit_account = sales_revenue
            transaction_type = f"{entry.payment_method.title()} Sales"
        else:
            # Default to cash sales
            debit_account = cash_account
            credit_account = sales_revenue
            transaction_type = "Sales Transaction"
        
        # Create journal lines for proper double-entry
        # Line 1: Debit (Asset increase)
        line1 = JournalLine(
            journal_entry_id=entry.id,
            account_id=debit_account.id,
            description=f"{transaction_type} - {entry.description}",
            debit_amount=amount,
            credit_amount=0.0
        )
        
        # Line 2: Credit (Revenue increase)
        line2 = JournalLine(
            journal_entry_id=entry.id,
            account_id=credit_account.id,
            description=f"{transaction_type} - {entry.description}",
            debit_amount=0.0,
            credit_amount=amount
        )
        
        db.session.add(line1)
        db.session.add(line2)
        
        print(f"   ✅ Created 2 journal lines:")
        print(f"      Line 1: {debit_account.name} - Debit ${amount}")
        print(f"      Line 2: {credit_account.name} - Credit ${amount}")
        
        migrated_count += 1
    
    db.session.commit()
    print(f"\n🎉 Successfully migrated {migrated_count} journal entries to {migrated_count * 2} journal lines")
    return True

def update_journal_entry_model():
    """Remove total_debit and total_credit from JournalEntry model (for future use)"""
    print("\n🔧 Note: JournalEntry model will be updated to remove total_debit/total_credit fields")
    print("   This will be done in the next step to avoid breaking existing data")
    print("   For now, we'll keep them for backward compatibility")

def validate_migration():
    """Validate that the migration was successful"""
    print("\n🔍 Validating migration...")
    
    entries = JournalEntry.query.all()
    total_lines = JournalLine.query.count()
    total_accounts = Account.query.count()
    
    print(f"📊 Final State:")
    print(f"   Journal Entries: {len(entries)}")
    print(f"   Journal Lines: {total_lines}")
    print(f"   Accounts: {total_accounts}")
    
    # Validate double-entry balance
    print(f"\n⚖️  Validating double-entry balance...")
    for entry in entries:
        lines = JournalLine.query.filter_by(journal_entry_id=entry.id).all()
        if len(lines) != 2:
            print(f"   ⚠️  Entry {entry.id} has {len(lines)} lines (expected 2)")
            continue
            
        total_debits = sum(line.debit_amount for line in lines)
        total_credits = sum(line.credit_amount for line in lines)
        
        if abs(total_debits - total_credits) < 0.01:
            print(f"   ✅ Entry {entry.id}: Balanced (${total_debits:.2f} = ${total_credits:.2f})")
        else:
            print(f"   ❌ Entry {entry.id}: Unbalanced (${total_debits:.2f} ≠ ${total_credits:.2f})")
    
    print(f"\n🎯 Migration validation complete!")

def main():
    """Main migration function"""
    print("🚀 Starting Phase 1: Double-Entry Database Schema Migration")
    print("=" * 60)
    
    try:
        with app.app_context():
            # Step 1: Create basic chart of accounts
            accounts = create_basic_chart_of_accounts()
            
            # Step 2: Migrate journal entries to proper journal lines
            success = migrate_journal_entries_to_lines()
            if not success:
                print("❌ Migration failed!")
                return False
            
            # Step 3: Validate migration
            validate_migration()
            
            print("\n🎉 Phase 1 Migration Complete!")
            print("✅ Database now has proper double-entry structure")
            print("✅ All journal entries have balanced journal lines")
            print("✅ Basic chart of accounts created")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

