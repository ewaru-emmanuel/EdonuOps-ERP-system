import requests
import time

def test_accounts_api():
    """Test the accounts API with balance calculation"""
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Test the accounts API
    url = 'http://localhost:5000/api/finance/double-entry/accounts'
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': '1'
    }
    
    print('Testing accounts API with balance calculation...')
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            accounts = response.json()
            print(f'✅ Retrieved {len(accounts)} accounts')
            
            # Show accounts with non-zero balances
            non_zero_accounts = [acc for acc in accounts if acc['balance'] != 0]
            print(f'Accounts with non-zero balances: {len(non_zero_accounts)}')
            
            for acc in non_zero_accounts:
                print(f'  Account {acc["code"]} ({acc["name"]}): ${acc["balance"]:.2f}')
            
            # Calculate totals by type
            assets = sum(acc['balance'] for acc in accounts if acc['type'] == 'asset')
            liabilities = sum(acc['balance'] for acc in accounts if acc['type'] == 'liability')
            equity = sum(acc['balance'] for acc in accounts if acc['type'] == 'equity')
            revenue = sum(acc['balance'] for acc in accounts if acc['type'] == 'revenue')
            expenses = sum(acc['balance'] for acc in accounts if acc['type'] == 'expense')
            
            print()
            print('TOTALS BY TYPE:')
            print(f'  Assets: ${assets:.2f}')
            print(f'  Liabilities: ${liabilities:.2f}')
            print(f'  Equity: ${equity:.2f}')
            print(f'  Revenue: ${revenue:.2f}')
            print(f'  Expenses: ${expenses:.2f}')
            print(f'  Net Income: ${revenue - expenses:.2f}')
            
            print()
            print('🎯 DASHBOARD SHOULD NOW SHOW:')
            print(f'  Total Assets: ${assets:.2f}')
            print(f'  Net Income: ${revenue - expenses:.2f}')
            print(f'  Accounts Receivable: ${sum(acc["balance"] for acc in accounts if acc["code"] == "1200"):.2f}')
            print(f'  Accounts Payable: ${sum(acc["balance"] for acc in accounts if acc["code"] == "2000"):.2f}')
            
        else:
            print(f'❌ API call failed: {response.text}')
            
    except Exception as e:
        print(f'❌ Request failed: {e}')

if __name__ == '__main__':
    test_accounts_api()
