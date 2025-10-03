#!/usr/bin/env python3
"""
Multi-Currency System Audit
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.finance.currency_models import Currency, ExchangeRate
from modules.finance.models import JournalEntry

def audit_multi_currency():
    with app.app_context():
        print('🔍 MULTI-CURRENCY SYSTEM AUDIT')
        print('=' * 50)
        
        # Check currencies
        currencies = Currency.query.all()
        print(f'✅ Currencies: {len(currencies)}')
        for currency in currencies:
            print(f'   {currency.code}: {currency.name} (Base: {currency.is_base_currency})')
        
        # Check exchange rates
        rates = ExchangeRate.query.all()
        print(f'✅ Exchange Rates: {len(rates)}')
        for rate in rates[:5]:  # Show first 5
            print(f'   {rate.from_currency.code} -> {rate.to_currency.code}: {rate.rate}')
        
        # Check journal entries with currency
        entries = JournalEntry.query.all()
        print(f'✅ Journal Entries: {len(entries)}')
        
        # Check currency distribution
        currency_counts = {}
        for entry in entries:
            curr = entry.currency or 'USD'
            currency_counts[curr] = currency_counts.get(curr, 0) + 1
        
        print('   Currency Distribution:')
        for curr, count in currency_counts.items():
            print(f'     {curr}: {count} entries')
        
        print()
        print('🎯 MULTI-CURRENCY STATUS:')
        print(f'   Currencies Available: {len(currencies)}')
        print(f'   Exchange Rates: {len(rates)}')
        print(f'   Journal Entries: {len(entries)}')
        print(f'   Multi-Currency Ready: {"YES" if len(currencies) > 1 else "NO"}')
        
        # Check if JournalEntry has currency field
        print()
        print('🔧 JOURNAL ENTRY CURRENCY INTEGRATION:')
        print(f'   Currency Field: {"✅ EXISTS" if hasattr(JournalEntry, "currency") else "❌ MISSING"}')
        
        # Check if we need to add multi-currency fields to JournalLine
        from modules.finance.models import JournalLine
        print(f'   JournalLine Currency Fields: {"✅ EXISTS" if hasattr(JournalLine, "currency") else "❌ MISSING"}')
        print(f'   JournalLine Exchange Rate: {"✅ EXISTS" if hasattr(JournalLine, "exchange_rate") else "❌ MISSING"}')

if __name__ == "__main__":
    audit_multi_currency()

