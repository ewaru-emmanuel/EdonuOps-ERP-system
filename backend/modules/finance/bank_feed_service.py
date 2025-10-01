"""
Bank Feed Integration Service
Supports Plaid, Yodlee, and other bank feed providers
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class BankFeedService:
    """Service for integrating with bank feed providers"""
    
    def __init__(self):
        self.plaid_client_id = os.getenv('PLAID_CLIENT_ID')
        self.plaid_secret = os.getenv('PLAID_SECRET')
        self.plaid_env = os.getenv('PLAID_ENV', 'sandbox')
        self.yodlee_client_id = os.getenv('YODLEE_CLIENT_ID')
        self.yodlee_secret = os.getenv('YODLEE_SECRET')
        
    def get_plaid_access_token(self, public_token: str) -> Optional[str]:
        """Exchange public token for access token"""
        try:
            url = f"https://{self.plaid_env}.plaid.com/link/token/exchange"
            headers = {
                'Content-Type': 'application/json',
                'PLAID-CLIENT-ID': self.plaid_client_id,
                'PLAID-SECRET': self.plaid_secret
            }
            data = {
                'public_token': public_token
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                logger.error(f"Plaid token exchange failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error exchanging Plaid token: {str(e)}")
            return None
    
    def get_plaid_accounts(self, access_token: str) -> List[Dict]:
        """Get accounts from Plaid"""
        try:
            url = f"https://{self.plaid_env}.plaid.com/accounts/get"
            headers = {
                'Content-Type': 'application/json',
                'PLAID-CLIENT-ID': self.plaid_client_id,
                'PLAID-SECRET': self.plaid_secret
            }
            data = {
                'access_token': access_token
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json().get('accounts', [])
            else:
                logger.error(f"Plaid accounts fetch failed: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching Plaid accounts: {str(e)}")
            return []
    
    def get_plaid_transactions(self, access_token: str, start_date: str, end_date: str) -> List[Dict]:
        """Get transactions from Plaid"""
        try:
            url = f"https://{self.plaid_env}.plaid.com/transactions/get"
            headers = {
                'Content-Type': 'application/json',
                'PLAID-CLIENT-ID': self.plaid_client_id,
                'PLAID-SECRET': self.plaid_secret
            }
            data = {
                'access_token': access_token,
                'start_date': start_date,
                'end_date': end_date
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json().get('transactions', [])
            else:
                logger.error(f"Plaid transactions fetch failed: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching Plaid transactions: {str(e)}")
            return []
    
    def get_yodlee_accounts(self, user_session_token: str) -> List[Dict]:
        """Get accounts from Yodlee"""
        try:
            url = "https://sandbox.api.yodlee.com/ysl/accounts"
            headers = {
                'Authorization': f'Bearer {user_session_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('account', [])
            else:
                logger.error(f"Yodlee accounts fetch failed: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching Yodlee accounts: {str(e)}")
            return []
    
    def get_yodlee_transactions(self, user_session_token: str, account_id: str, 
                              start_date: str, end_date: str) -> List[Dict]:
        """Get transactions from Yodlee"""
        try:
            url = "https://sandbox.api.yodlee.com/ysl/transactions"
            headers = {
                'Authorization': f'Bearer {user_session_token}',
                'Content-Type': 'application/json'
            }
            params = {
                'accountId': account_id,
                'fromDate': start_date,
                'toDate': end_date
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get('transaction', [])
            else:
                logger.error(f"Yodlee transactions fetch failed: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching Yodlee transactions: {str(e)}")
            return []
    
    def normalize_transaction(self, transaction: Dict, provider: str) -> Dict:
        """Normalize transaction data from different providers"""
        if provider == 'plaid':
            return {
                'transaction_id': transaction.get('transaction_id'),
                'account_id': transaction.get('account_id'),
                'amount': transaction.get('amount'),
                'date': transaction.get('date'),
                'name': transaction.get('name'),
                'merchant_name': transaction.get('merchant_name'),
                'category': transaction.get('category'),
                'subcategory': transaction.get('subcategory'),
                'account_owner': transaction.get('account_owner'),
                'pending': transaction.get('pending', False),
                'transaction_type': transaction.get('transaction_type'),
                'iso_currency_code': transaction.get('iso_currency_code'),
                'unofficial_currency_code': transaction.get('unofficial_currency_code')
            }
        elif provider == 'yodlee':
            return {
                'transaction_id': transaction.get('id'),
                'account_id': transaction.get('accountId'),
                'amount': transaction.get('amount', {}).get('amount'),
                'date': transaction.get('date'),
                'name': transaction.get('description', {}).get('original'),
                'merchant_name': transaction.get('merchant', {}).get('name'),
                'category': transaction.get('category'),
                'subcategory': transaction.get('subcategory'),
                'account_owner': transaction.get('accountOwner'),
                'pending': transaction.get('status') == 'PENDING',
                'transaction_type': transaction.get('type'),
                'iso_currency_code': transaction.get('amount', {}).get('currency'),
                'unofficial_currency_code': None
            }
        else:
            return transaction
    
    def sync_bank_data(self, bank_account_id: int, provider: str, access_token: str, 
                      start_date: str, end_date: str) -> Dict:
        """Sync bank data from external provider"""
        try:
            if provider == 'plaid':
                transactions = self.get_plaid_transactions(access_token, start_date, end_date)
            elif provider == 'yodlee':
                transactions = self.get_yodlee_transactions(access_token, bank_account_id, start_date, end_date)
            else:
                return {'error': 'Unsupported provider'}
            
            # Normalize transactions
            normalized_transactions = []
            for tx in transactions:
                normalized_tx = self.normalize_transaction(tx, provider)
                normalized_transactions.append(normalized_tx)
            
            return {
                'success': True,
                'transactions': normalized_transactions,
                'count': len(normalized_transactions)
            }
        except Exception as e:
            logger.error(f"Error syncing bank data: {str(e)}")
            return {'error': str(e)}
    
    def get_account_balance(self, access_token: str, account_id: str, provider: str) -> Optional[float]:
        """Get current account balance"""
        try:
            if provider == 'plaid':
                url = f"https://{self.plaid_env}.plaid.com/accounts/balance/get"
                headers = {
                    'Content-Type': 'application/json',
                    'PLAID-CLIENT-ID': self.plaid_client_id,
                    'PLAID-SECRET': self.plaid_secret
                }
                data = {
                    'access_token': access_token,
                    'account_ids': [account_id]
                }
                
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    accounts = response.json().get('accounts', [])
                    if accounts:
                        return accounts[0].get('balances', {}).get('current')
            elif provider == 'yodlee':
                url = f"https://sandbox.api.yodlee.com/ysl/accounts/{account_id}"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    account = response.json().get('account', {})
                    return account.get('balance', {}).get('amount')
            
            return None
        except Exception as e:
            logger.error(f"Error getting account balance: {str(e)}")
            return None

# Global instance
bank_feed_service = BankFeedService()










