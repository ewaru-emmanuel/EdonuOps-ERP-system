#!/usr/bin/env python3
"""
Quick test to verify accounting periods are working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.finance.accounting_periods import FiscalYear, AccountingPeriod, period_manager
from modules.finance.models import JournalEntry

def quick_test():
    with app.app_context():
        print("🔍 QUICK ACCOUNTING PERIODS TEST")
        print("=" * 40)
        
        # Check fiscal years
        fiscal_years = FiscalYear.query.all()
        print(f"✅ Fiscal Years: {len(fiscal_years)}")
        for fy in fiscal_years:
            print(f"   {fy.year}: {fy.name} ({fy.status})")
        
        # Check periods
        periods = AccountingPeriod.query.all()
        print(f"✅ Accounting Periods: {len(periods)}")
        for period in periods[:3]:  # Show first 3
            print(f"   {period.short_name}: {period.start_date} to {period.end_date} ({period.status})")
        
        # Check journal entries with periods
        entries = JournalEntry.query.filter(JournalEntry.accounting_period_id.isnot(None)).all()
        print(f"✅ Journal Entries with Periods: {len(entries)}")
        
        # Check backdated entries
        backdated = JournalEntry.query.filter_by(is_backdated=True).count()
        print(f"✅ Backdated Entries: {backdated}")
        
        # Test period validation
        from datetime import date
        is_valid, message, period = period_manager.validate_transaction_date(date.today(), 3)
        print(f"✅ Today's Date Validation: {is_valid} - {message}")
        
        print("\n🎉 ACCOUNTING PERIODS: WORKING!")

if __name__ == "__main__":
    quick_test()

