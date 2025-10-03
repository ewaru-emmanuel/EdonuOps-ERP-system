#!/usr/bin/env python3
"""
Test script for SimpleTransactionTemplate
"""

from modules.finance.models import Account
from modules.finance.transaction_templates import transaction_manager

def test_simple_transaction():
    """Test the simple transaction template"""
    
    # Check if there are any accounts
    accounts = Account.query.limit(5).all()
    print('Available accounts:')
    for acc in accounts:
        print(f'  ID: {acc.id}, Name: {acc.name}, Type: {acc.account_type}')
    
    if not accounts:
        print('No accounts found in database')
        return
    
    # Test with the first account
    template = transaction_manager.get_template('simple_transaction')
    print(f'\nTesting template: {template.name}')
    
    try:
        result = template.create_journal_entry(
            amount=100.0,
            description='Test transaction',
            account_id=accounts[0].id,
            is_debit=True
        )
        print('✅ Journal entry created successfully!')
        print(f'Lines: {len(result["lines"])}')
        for line in result['lines']:
            print(f'  {line["account_name"]}: Debit {line["debit_amount"]}, Credit {line["credit_amount"]}')
    except Exception as e:
        print(f'❌ Error creating journal entry: {e}')

if __name__ == '__main__':
    test_simple_transaction()

