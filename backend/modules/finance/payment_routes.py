from flask import Blueprint, request, jsonify
from app import db
from .payment_models import PaymentMethod, BankAccount, PaymentTransaction, PartialPayment
from .currency_models import ExchangeRate
from .advanced_models import ChartOfAccounts
from datetime import datetime, date
import json

payment_bp = Blueprint('payment', __name__, url_prefix='/api/finance')

# ============= PAYMENT METHODS =============

@payment_bp.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    """Get all active payment methods"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # SECURITY: Require authentication - no anonymous access
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        methods = PaymentMethod.query.filter_by(user_id=user_id, is_active=True).all()
        return jsonify([{
            'id': method.id,
            'code': method.code,
            'name': method.name,
            'description': method.description,
            'requires_reference': method.requires_reference,
            'requires_bank_account': method.requires_bank_account,
            'default_processing_fee_rate': method.default_processing_fee_rate,
            'icon_name': method.icon_name,
            'color_code': method.color_code,
            'display_order': method.display_order
        } for method in methods]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payment-methods', methods=['POST'])
def create_payment_method():
    """Create a new payment method"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['code', 'name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if code already exists
        existing = PaymentMethod.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({'error': 'Payment method code already exists'}), 400
        
        method = PaymentMethod(
            code=data['code'].upper(),
            name=data['name'],
            description=data.get('description'),
            requires_reference=data.get('requires_reference', False),
            requires_bank_account=data.get('requires_bank_account', True),
            default_processing_fee_rate=float(data.get('default_processing_fee_rate', 0)),
            display_order=int(data.get('display_order', 0)),
            icon_name=data.get('icon_name'),
            color_code=data.get('color_code'),
            created_by=data.get('created_by', 'system')
        )
        
        db.session.add(method)
        db.session.commit()
        
        return jsonify({
            'id': method.id,
            'code': method.code,
            'name': method.name,
            'message': 'Payment method created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payment-methods/<int:method_id>', methods=['PUT'])
def update_payment_method(method_id):
    """Update a payment method"""
    try:
        method = PaymentMethod.query.get(method_id)
        if not method:
            return jsonify({'error': 'Payment method not found'}), 404
        
        if method.is_system:
            return jsonify({'error': 'Cannot modify system payment methods'}), 400
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            method.name = data['name']
        if 'description' in data:
            method.description = data['description']
        if 'requires_reference' in data:
            method.requires_reference = data['requires_reference']
        if 'requires_bank_account' in data:
            method.requires_bank_account = data['requires_bank_account']
        if 'default_processing_fee_rate' in data:
            method.default_processing_fee_rate = float(data['default_processing_fee_rate'])
        if 'display_order' in data:
            method.display_order = int(data['display_order'])
        if 'icon_name' in data:
            method.icon_name = data['icon_name']
        if 'color_code' in data:
            method.color_code = data['color_code']
        if 'is_active' in data:
            method.is_active = data['is_active']
        
        method.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Payment method updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= BANK ACCOUNTS =============

@payment_bp.route('/bank-accounts', methods=['GET'])
def get_bank_accounts():
    """Get all active bank accounts"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # SECURITY: Require authentication - no anonymous access
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        accounts = BankAccount.query.filter_by(user_id=user_id, is_active=True).all()
        return jsonify([{
            'id': account.id,
            'account_name': account.account_name,
            'account_number': account.account_number,
            'bank_name': account.bank_name,
            'bank_code': account.bank_code,
            'account_type': account.account_type,
            'currency': account.currency,
            'gl_account_id': account.gl_account_id,
            'gl_account_name': account.gl_account.account_name if account.gl_account else None,
            'is_default': account.is_default,
            'allow_deposits': account.allow_deposits,
            'allow_withdrawals': account.allow_withdrawals,
            'daily_limit': account.daily_limit,
            'monthly_limit': account.monthly_limit,
            'requires_approval': account.requires_approval
        } for account in accounts]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/bank-accounts/deposits', methods=['GET'])
def get_deposit_accounts():
    """Get bank accounts that can receive deposits"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # SECURITY: Require authentication - no anonymous access
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        accounts = BankAccount.query.filter_by(user_id=user_id, can_receive_deposits=True).all()
        return jsonify([{
            'id': account.id,
            'account_name': account.account_name,
            'account_type': account.account_type,
            'currency': account.currency,
            'is_default': account.is_default
        } for account in accounts]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/bank-accounts/withdrawals', methods=['GET'])
def get_withdrawal_accounts():
    """Get bank accounts that can make payments"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # SECURITY: Require authentication - no anonymous access
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        accounts = BankAccount.query.filter_by(user_id=user_id, can_make_payments=True).all()
        return jsonify([{
            'id': account.id,
            'account_name': account.account_name,
            'account_type': account.account_type,
            'currency': account.currency,
            'is_default': account.is_default
        } for account in accounts]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/bank-accounts', methods=['POST'])
def create_bank_account():
    """Create a new bank account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['account_name', 'account_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # If this is set as default, unset other defaults
        if data.get('is_default'):
            BankAccount.query.filter_by(is_default=True).update({'is_default': False})
        
        account = BankAccount(
            account_name=data['account_name'],
            account_number=data.get('account_number'),
            bank_name=data.get('bank_name'),
            bank_code=data.get('bank_code'),
            account_type=data['account_type'],
            currency=data.get('currency', 'USD'),
            gl_account_id=data.get('gl_account_id'),
            is_default=data.get('is_default', False),
            allow_deposits=data.get('allow_deposits', True),
            allow_withdrawals=data.get('allow_withdrawals', True),
            daily_limit=float(data['daily_limit']) if data.get('daily_limit') else None,
            monthly_limit=float(data['monthly_limit']) if data.get('monthly_limit') else None,
            requires_approval=data.get('requires_approval', False),
            created_by=data.get('created_by', 'system')
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'id': account.id,
            'account_name': account.account_name,
            'message': 'Bank account created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/bank-accounts/<int:account_id>', methods=['PUT'])
def update_bank_account(account_id):
    """Update a bank account"""
    try:
        account = BankAccount.query.get(account_id)
        if not account:
            return jsonify({'error': 'Bank account not found'}), 404
        
        data = request.get_json()
        
        # If this is set as default, unset other defaults
        if data.get('is_default') and not account.is_default:
            BankAccount.query.filter_by(is_default=True).update({'is_default': False})
        
        # Update fields
        if 'account_name' in data:
            account.account_name = data['account_name']
        if 'account_number' in data:
            account.account_number = data['account_number']
        if 'bank_name' in data:
            account.bank_name = data['bank_name']
        if 'bank_code' in data:
            account.bank_code = data['bank_code']
        if 'account_type' in data:
            account.account_type = data['account_type']
        if 'currency' in data:
            account.currency = data['currency']
        if 'gl_account_id' in data:
            account.gl_account_id = data['gl_account_id']
        if 'is_default' in data:
            account.is_default = data['is_default']
        if 'allow_deposits' in data:
            account.allow_deposits = data['allow_deposits']
        if 'allow_withdrawals' in data:
            account.allow_withdrawals = data['allow_withdrawals']
        if 'daily_limit' in data:
            account.daily_limit = float(data['daily_limit']) if data['daily_limit'] else None
        if 'monthly_limit' in data:
            account.monthly_limit = float(data['monthly_limit']) if data['monthly_limit'] else None
        if 'requires_approval' in data:
            account.requires_approval = data['requires_approval']
        if 'is_active' in data:
            account.is_active = data['is_active']
        
        account.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Bank account updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= PAYMENT TRANSACTIONS =============

@payment_bp.route('/payment-transactions', methods=['POST'])
def create_payment_transaction():
    """Create a payment transaction record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['payment_date', 'amount', 'payment_method_id', 'transaction_type']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate transaction number
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        transaction_number = f"PMT-{timestamp}-{data.get('source_id', '000')}"
        
        # Calculate net amount
        amount = float(data['amount'])
        processing_fee = float(data.get('processing_fee', 0))
        net_amount = amount - processing_fee
        
        transaction = PaymentTransaction(
            transaction_number=transaction_number,
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date(),
            amount=amount,
            currency=data.get('currency', 'USD'),
            exchange_rate=float(data.get('exchange_rate', 1.0)),
            payment_method_id=int(data['payment_method_id']),
            bank_account_id=int(data['bank_account_id']) if data.get('bank_account_id') else None,
            payment_reference=data.get('payment_reference'),
            external_reference=data.get('external_reference'),
            processing_fee=processing_fee,
            fee_account_id=int(data['fee_account_id']) if data.get('fee_account_id') else None,
            net_amount=net_amount,
            transaction_type=data['transaction_type'],
            source_table=data.get('source_table'),
            source_id=int(data['source_id']) if data.get('source_id') else None,
            status=data.get('status', 'completed'),
            description=data.get('description'),
            notes=data.get('notes'),
            created_by=data.get('created_by', 'system')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'id': transaction.id,
            'transaction_number': transaction.transaction_number,
            'net_amount': transaction.net_amount,
            'message': 'Payment transaction created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= UTILITY ENDPOINTS =============

@payment_bp.route('/payment-methods/seed', methods=['POST'])
def seed_payment_methods():
    """Seed default payment methods"""
    try:
        default_methods = [
            {
                'code': 'CASH',
                'name': 'Cash',
                'description': 'Physical cash payments',
                'requires_reference': False,
                'requires_bank_account': False,
                'default_processing_fee_rate': 0.0,
                'display_order': 1,
                'icon_name': 'Money',
                'color_code': '#4CAF50',
                'is_system': True
            },
            {
                'code': 'CARD',
                'name': 'Credit/Debit Card',
                'description': 'Credit and debit card payments',
                'requires_reference': True,
                'requires_bank_account': True,
                'default_processing_fee_rate': 2.9,
                'display_order': 2,
                'icon_name': 'CreditCard',
                'color_code': '#2196F3',
                'is_system': True
            },
            {
                'code': 'BANK_TRANSFER',
                'name': 'Bank Transfer',
                'description': 'Direct bank to bank transfers',
                'requires_reference': True,
                'requires_bank_account': True,
                'default_processing_fee_rate': 0.0,
                'display_order': 3,
                'icon_name': 'AccountBalance',
                'color_code': '#FF9800',
                'is_system': True
            },
            {
                'code': 'CHECK',
                'name': 'Check',
                'description': 'Paper check payments',
                'requires_reference': True,
                'requires_bank_account': True,
                'default_processing_fee_rate': 0.0,
                'display_order': 4,
                'icon_name': 'Receipt',
                'color_code': '#9C27B0',
                'is_system': True
            },
            {
                'code': 'WIRE',
                'name': 'Wire Transfer',
                'description': 'Wire transfer payments',
                'requires_reference': True,
                'requires_bank_account': True,
                'default_processing_fee_rate': 0.0,
                'display_order': 5,
                'icon_name': 'Send',
                'color_code': '#F44336',
                'is_system': True
            }
        ]
        
        created_count = 0
        for method_data in default_methods:
            existing = PaymentMethod.query.filter_by(code=method_data['code']).first()
            if not existing:
                method = PaymentMethod(**method_data, created_by='system')
                db.session.add(method)
                created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Seeded {created_count} payment methods successfully',
            'created_count': created_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
