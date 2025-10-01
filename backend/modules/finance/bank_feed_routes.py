"""
Bank Feed Integration API Routes
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging
from .bank_feed_service import bank_feed_service
from .payment_models import BankAccount, BankTransaction
from ..database import db

logger = logging.getLogger(__name__)

# Create blueprint
bank_feed_bp = Blueprint('bank_feed', __name__, url_prefix='/api/finance/bank-feed')

@bank_feed_bp.route('/providers', methods=['GET'])
@jwt_required()
def get_providers():
    """Get available bank feed providers"""
    try:
        providers = [
            {
                'id': 'plaid',
                'name': 'Plaid',
                'description': 'Connect to 11,000+ financial institutions',
                'supported_countries': ['US', 'CA', 'GB', 'ES', 'FR', 'IE', 'NL', 'DE', 'IT', 'PT'],
                'features': ['transactions', 'accounts', 'identity', 'investments', 'liabilities']
            },
            {
                'id': 'yodlee',
                'name': 'Yodlee',
                'description': 'Global financial data aggregation',
                'supported_countries': ['US', 'CA', 'GB', 'AU', 'IN', 'SG', 'MY', 'TH', 'PH', 'ID'],
                'features': ['transactions', 'accounts', 'identity', 'investments', 'liabilities']
            },
            {
                'id': 'manual',
                'name': 'Manual Import',
                'description': 'Import bank statements via CSV or manual entry',
                'supported_countries': ['ALL'],
                'features': ['csv_import', 'manual_entry']
            }
        ]
        
        return jsonify({
            'success': True,
            'providers': providers
        })
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bank_feed_bp.route('/plaid/link-token', methods=['POST'])
@jwt_required()
def create_plaid_link_token():
    """Create Plaid link token for bank connection"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # This would typically call Plaid's /link/token/create endpoint
        # For now, we'll return a mock token
        link_token = f"link-sandbox-{user_id}-{datetime.now().timestamp()}"
        
        return jsonify({
            'success': True,
            'link_token': link_token,
            'expiration': (datetime.now() + timedelta(hours=1)).isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating Plaid link token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bank_feed_bp.route('/plaid/exchange-token', methods=['POST'])
@jwt_required()
def exchange_plaid_token():
    """Exchange Plaid public token for access token"""
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        
        if not public_token:
            return jsonify({'error': 'Public token is required'}), 400
        
        # Exchange token
        access_token = bank_feed_service.get_plaid_access_token(public_token)
        
        if not access_token:
            return jsonify({'error': 'Failed to exchange token'}), 400
        
        return jsonify({
            'success': True,
            'access_token': access_token
        })
    except Exception as e:
        logger.error(f"Error exchanging Plaid token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bank_feed_bp.route('/plaid/accounts', methods=['POST'])
@jwt_required()
def get_plaid_accounts():
    """Get Plaid accounts"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'Access token is required'}), 400
        
        accounts = bank_feed_service.get_plaid_accounts(access_token)
        
        return jsonify({
            'success': True,
            'accounts': accounts
        })
    except Exception as e:
        logger.error(f"Error getting Plaid accounts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bank_feed_bp.route('/connect-account', methods=['POST'])
@jwt_required()
def connect_bank_account():
    """Connect external bank account to internal bank account"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        bank_account_id = data.get('bank_account_id')
        provider = data.get('provider')
        access_token = data.get('access_token')
        external_account_id = data.get('external_account_id')
        
        if not all([bank_account_id, provider, access_token, external_account_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get bank account
        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account:
            return jsonify({'error': 'Bank account not found'}), 404
        
        # Store connection details
        bank_account.provider = provider
        bank_account.external_account_id = external_account_id
        bank_account.access_token = access_token  # In production, encrypt this
        bank_account.connected_at = datetime.utcnow()
        bank_account.connected_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bank account connected successfully'
        })
    except Exception as e:
        logger.error(f"Error connecting bank account: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bank_feed_bp.route('/sync-transactions', methods=['POST'])
@jwt_required()
def sync_transactions():
    """Sync transactions from connected bank account"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        bank_account_id = data.get('bank_account_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not bank_account_id:
            return jsonify({'error': 'Bank account ID is required'}), 400
        
        # Get bank account
        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account:
            return jsonify({'error': 'Bank account not found'}), 404
        
        if not bank_account.provider or not bank_account.access_token:
            return jsonify({'error': 'Bank account not connected to external provider'}), 400
        
        # Set date range
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Sync transactions
        result = bank_feed_service.sync_bank_data(
            bank_account_id=bank_account_id,
            provider=bank_account.provider,
            access_token=bank_account.access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        if result.get('error'):
            return jsonify({'error': result['error']}), 500
        
        # Store transactions in database
        transactions_created = 0
        for tx_data in result.get('transactions', []):
            # Check if transaction already exists
            existing_tx = BankTransaction.query.filter_by(
                bank_account_id=bank_account_id,
                external_transaction_id=tx_data.get('transaction_id')
            ).first()
            
            if not existing_tx:
                bank_transaction = BankTransaction(
                    bank_account_id=bank_account_id,
                    transaction_date=datetime.strptime(tx_data.get('date'), '%Y-%m-%d').date(),
                    amount=tx_data.get('amount', 0),
                    description=tx_data.get('name', ''),
                    reference=tx_data.get('transaction_id', ''),
                    external_transaction_id=tx_data.get('transaction_id'),
                    external_data=tx_data,
                    created_by=user_id
                )
                db.session.add(bank_transaction)
                transactions_created += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transactions_created': transactions_created,
            'total_transactions': len(result.get('transactions', [])),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as e:
        logger.error(f"Error syncing transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bank_feed_bp.route('/get-balance', methods=['POST'])
@jwt_required()
def get_account_balance():
    """Get current account balance from external provider"""
    try:
        data = request.get_json()
        bank_account_id = data.get('bank_account_id')
        
        if not bank_account_id:
            return jsonify({'error': 'Bank account ID is required'}), 400
        
        # Get bank account
        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account:
            return jsonify({'error': 'Bank account not found'}), 404
        
        if not bank_account.provider or not bank_account.access_token:
            return jsonify({'error': 'Bank account not connected to external provider'}), 400
        
        # Get balance
        balance = bank_feed_service.get_account_balance(
            access_token=bank_account.access_token,
            account_id=bank_account.external_account_id,
            provider=bank_account.provider
        )
        
        if balance is None:
            return jsonify({'error': 'Failed to get account balance'}), 500
        
        return jsonify({
            'success': True,
            'balance': balance,
            'currency': 'USD',  # This should come from the provider
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting account balance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bank_feed_bp.route('/disconnect-account', methods=['POST'])
@jwt_required()
def disconnect_bank_account():
    """Disconnect external bank account"""
    try:
        data = request.get_json()
        bank_account_id = data.get('bank_account_id')
        
        if not bank_account_id:
            return jsonify({'error': 'Bank account ID is required'}), 400
        
        # Get bank account
        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account:
            return jsonify({'error': 'Bank account not found'}), 404
        
        # Clear connection details
        bank_account.provider = None
        bank_account.external_account_id = None
        bank_account.access_token = None
        bank_account.connected_at = None
        bank_account.connected_by = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bank account disconnected successfully'
        })
    except Exception as e:
        logger.error(f"Error disconnecting bank account: {str(e)}")
        return jsonify({'error': str(e)}), 500










