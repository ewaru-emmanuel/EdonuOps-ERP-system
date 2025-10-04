import requests
import time
import subprocess
import sys

def test_transaction_fix():
    """Test the transaction creation fix"""
    
    print('Testing the fix by creating a new transaction...')
    
    # First, let's check if the server is running
    try:
        response = requests.get('http://localhost:5000/api/finance/transactions/test', timeout=5)
        print('✅ Server is running')
    except:
        print('❌ Server is not running, starting it...')
        subprocess.Popen([sys.executable, 'run.py'])
        time.sleep(5)
    
    # Now test the transaction creation
    url = 'http://localhost:5000/api/finance/transactions/create'
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': '1'
    }
    data = {
        'template_id': 'simple_transaction',
        'amount': 200.00,
        'description': 'Test transaction after code fix',
        'account_id': 1,
        'is_debit': True,
        'date': '2025-10-04',
        'reference': f'TEST-FIX-{int(time.time())}',
        'status': 'posted',
        'payment_method': 'cash'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f'Status: {response.status_code}')
        if response.status_code == 201:
            print('✅ Transaction created successfully!')
            result = response.json()
            transaction = result['transaction']
            print(f'Entry ID: {transaction["entry_id"]}')
            print(f'Reference: {transaction["reference"]}')
            print(f'Total Debits: ${transaction["total_debits"]}')
            print(f'Total Credits: ${transaction["total_credits"]}')
            
            # Now verify in database
            import sqlite3
            conn = sqlite3.connect('edonuops.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT je.total_debit, je.total_credit,
                       COALESCE(SUM(jl.debit_amount), 0) as line_debits,
                       COALESCE(SUM(jl.credit_amount), 0) as line_credits
                FROM journal_entries je
                LEFT JOIN journal_lines jl ON je.id = jl.journal_entry_id
                WHERE je.id = ?
                GROUP BY je.id, je.total_debit, je.total_credit
            ''', (transaction["entry_id"],))
            
            result = cursor.fetchone()
            if result:
                entry_debit, entry_credit, line_debit, line_credit = result
                print(f'Database Verification:')
                print(f'  Entry Totals: Debit ${entry_debit:.2f}, Credit ${entry_credit:.2f}')
                print(f'  Line Totals: Debit ${line_debit:.2f}, Credit ${line_credit:.2f}')
                
                if abs(entry_debit - line_debit) < 0.01 and abs(entry_credit - line_credit) < 0.01:
                    print('✅ FIX VERIFIED: Entry totals match line totals!')
                else:
                    print('❌ FIX FAILED: Entry totals do not match line totals')
            
            conn.close()
        else:
            print(f'❌ Transaction creation failed: {response.text}')
    except Exception as e:
        print(f'❌ Request failed: {e}')

if __name__ == '__main__':
    test_transaction_fix()
