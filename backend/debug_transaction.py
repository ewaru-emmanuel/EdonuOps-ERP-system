#!/usr/bin/env python3
"""
Debug script for transaction creation
"""

from app import app, db
from modules.finance.transaction_templates import transaction_manager

def debug_transaction_creation():
    """Debug transaction creation"""
    with app.app_context():
        try:
            print('🧪 Testing transaction creation directly...')
            
            # Test creating a cash sales transaction
            result = transaction_manager.create_transaction(
                template_id='cash_sales',
                user_id=3,
                amount=100.0,
                description='Direct test transaction'
            )
            
            print('✅ Transaction created successfully!')
            print(f'   Entry ID: {result["entry_id"]}')
            print(f'   Reference: {result["reference"]}')
            print(f'   Template: {result["template_used"]}')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_transaction_creation()

