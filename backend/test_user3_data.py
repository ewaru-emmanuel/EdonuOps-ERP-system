import requests
import time

def test_user3_data():
    """Test the accounts API for User 3 (admin@edonuerp.com)"""
    
    print('Testing User 3 (admin@edonuerp.com) data...')
    
    # Test the accounts API for User 3
    url = 'http://localhost:5000/api/finance/double-entry/accounts'
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': '3'  # User 3
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            accounts = response.json()
            print(f'✅ Retrieved {len(accounts)} accounts for User 3')
            
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
            print('USER 3 TOTALS BY TYPE:')
            print(f'  Assets: ${assets:.2f}')
            print(f'  Liabilities: ${liabilities:.2f}')
            print(f'  Equity: ${equity:.2f}')
            print(f'  Revenue: ${revenue:.2f}')
            print(f'  Expenses: ${expenses:.2f}')
            print(f'  Net Income: ${revenue - expenses:.2f}')
            
            print()
            print('🎯 DASHBOARD SHOULD SHOW FOR USER 3:')
            print(f'  Total Assets: ${assets:.2f}')
            print(f'  Net Income: ${revenue - expenses:.2f}')
            print(f'  Accounts Receivable: ${sum(acc["balance"] for acc in accounts if acc["code"] == "1200"):.2f}')
            print(f'  Accounts Payable: ${sum(acc["balance"] for acc in accounts if acc["code"] == "2000"):.2f}')
            
        else:
            print(f'❌ API call failed: {response.text}')
            
    except Exception as e:
        print(f'❌ Request failed: {e}')
    
    print()
    print('Testing journal entries for User 3...')
    
    # Test journal entries for User 3
    url = 'http://localhost:5000/api/finance/double-entry/journal-entries'
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': '3'  # User 3
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            entries = response.json()
            print(f'✅ Retrieved {len(entries)} journal entries for User 3')
            
            if entries:
                print('Recent entries:')
                for entry in entries[:3]:
                    print(f'  Entry {entry["id"]}: {entry["reference"]} - {entry["description"]}')
                    print(f'    Total Debits: ${entry["total_debits"]:.2f}, Total Credits: ${entry["total_credits"]:.2f}')
                    print(f'    Lines: {len(entry["lines"])}')
        else:
            print(f'❌ Journal entries API call failed: {response.text}')
            
    except Exception as e:
        print(f'❌ Journal entries request failed: {e}')

if __name__ == '__main__':
    test_user3_data()
