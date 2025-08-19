#!/usr/bin/env python3
"""
Currency Manager CLI Tool
Standalone tool for managing currencies and exchange rates
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.finance.currency_service import CurrencyService
from modules.finance.currency_models import Currency, ExchangeRate

def init_database():
    """Initialize database tables"""
    print("🗄️  Creating database tables...")
    db.create_all()
    print("✅ Database tables created!")

def initialize_currencies():
    """Initialize currencies in database"""
    print("🌍 Initializing currencies...")
    success = CurrencyService.initialize_currencies()
    if success:
        print("✅ Currencies initialized successfully!")
        return True
    else:
        print("❌ Currency initialization failed!")
        return False

def update_rates(base_currency='USD'):
    """Update exchange rates from API"""
    print(f"🔄 Updating exchange rates with base currency: {base_currency}")
    success = CurrencyService.update_exchange_rates(base_currency)
    if success:
        print("✅ Exchange rates updated successfully!")
        return True
    else:
        print("❌ Exchange rate update failed!")
        return False

def show_status():
    """Show currency system status"""
    print("\n📊 Currency System Status")
    print("=" * 40)
    
    total_currencies = Currency.query.count()
    active_currencies = Currency.query.filter_by(is_active=True).count()
    base_currency = Currency.get_base_currency()
    current_rates = ExchangeRate.query.filter_by(is_current=True).count()
    
    print(f"Total Currencies: {total_currencies}")
    print(f"Active Currencies: {active_currencies}")
    print(f"Base Currency: {base_currency.code if base_currency else 'Not Set'}")
    print(f"Current Exchange Rates: {current_rates}")
    
    # Show latest rate update
    latest_rate = ExchangeRate.query.filter_by(is_current=True).order_by(ExchangeRate.created_at.desc()).first()
    if latest_rate:
        print(f"Last Rate Update: {latest_rate.created_at}")
    else:
        print("Last Rate Update: Never")
    
    print()

def list_currencies():
    """List all currencies"""
    currencies = Currency.query.order_by(Currency.code).all()
    
    print("\n💰 Available Currencies")
    print("=" * 50)
    print(f"{'Code':<5} {'Name':<25} {'Symbol':<8} {'Status':<8} {'Base'}")
    print("-" * 50)
    
    for currency in currencies:
        status = "Active" if currency.is_active else "Inactive"
        base_flag = "Yes" if currency.is_base_currency else "No"
        print(f"{currency.code:<5} {currency.name:<25} {currency.symbol:<8} {status:<8} {base_flag}")
    
    print()

def set_base_currency(currency_code):
    """Set base currency"""
    print(f"🎯 Setting base currency to: {currency_code}")
    success = CurrencyService.set_base_currency(currency_code)
    if success:
        print("✅ Base currency updated successfully!")
        return True
    else:
        print("❌ Failed to set base currency!")
        return False

def test_conversion(amount, from_curr, to_curr):
    """Test currency conversion"""
    print(f"🔄 Converting {amount} {from_curr} to {to_curr}")
    converted, rate = CurrencyService.convert_currency(float(amount), from_curr, to_curr, record_conversion=False)
    
    if converted is not None:
        print(f"✅ Result: {amount} {from_curr} = {converted:.2f} {to_curr} (Rate: {rate:.4f})")
        return True
    else:
        print("❌ Conversion failed!")
        return False

def full_setup():
    """Complete currency system setup"""
    print("🚀 Starting full currency system setup...")
    print()
    
    # Step 1: Initialize database
    init_database()
    print()
    
    # Step 2: Initialize currencies
    if not initialize_currencies():
        return False
    print()
    
    # Step 3: Update exchange rates
    if not update_rates():
        return False
    print()
    
    # Step 4: Show status
    show_status()
    
    print("🎉 Currency system setup completed successfully!")
    return True

def main():
    """Main CLI function"""
    app = create_app()
    
    with app.app_context():
        if len(sys.argv) < 2:
            print("🌍 EdonuOps Currency Manager")
            print("=" * 30)
            print("Available commands:")
            print("  setup           - Complete currency system setup")
            print("  init-db         - Initialize database tables")
            print("  init-currencies - Initialize currency data")
            print("  update-rates    - Update exchange rates")
            print("  status          - Show system status")
            print("  list            - List all currencies")
            print("  set-base <CODE> - Set base currency")
            print("  convert <AMT> <FROM> <TO> - Test conversion")
            print()
            print("Examples:")
            print("  python currency_manager.py setup")
            print("  python currency_manager.py update-rates")
            print("  python currency_manager.py set-base EUR")
            print("  python currency_manager.py convert 100 USD EUR")
            return
        
        command = sys.argv[1].lower()
        
        try:
            if command == 'setup':
                full_setup()
            elif command == 'init-db':
                init_database()
            elif command == 'init-currencies':
                initialize_currencies()
            elif command == 'update-rates':
                base = sys.argv[2] if len(sys.argv) > 2 else 'USD'
                update_rates(base)
            elif command == 'status':
                show_status()
            elif command == 'list':
                list_currencies()
            elif command == 'set-base':
                if len(sys.argv) < 3:
                    print("❌ Please specify currency code: set-base <CODE>")
                else:
                    set_base_currency(sys.argv[2].upper())
            elif command == 'convert':
                if len(sys.argv) < 5:
                    print("❌ Usage: convert <AMOUNT> <FROM> <TO>")
                else:
                    test_conversion(sys.argv[2], sys.argv[3].upper(), sys.argv[4].upper())
            else:
                print(f"❌ Unknown command: {command}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Currency manager interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    main()

