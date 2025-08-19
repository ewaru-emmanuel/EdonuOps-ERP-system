"""
Currency API Routes for Multi-Currency Support
Provides endpoints for currency management and exchange rates
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from .currency_service import CurrencyService
from .currency_models import Currency, ExchangeRate, CurrencyConversion
from app import db

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
currency_bp = Blueprint('currency', __name__, url_prefix='/currency')

@currency_bp.route('/health', methods=['GET'])
def health_check():
    """Currency service health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'currency',
        'message': 'Currency service is running'
    }), 200

@currency_bp.route('/currencies', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_currencies():
    """
    Get list of all currencies
    Query params:
    - active_only: bool (default: true)
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        currencies = CurrencyService.get_currency_list(active_only=active_only)
        
        logger.info(f"💰 Returning {len(currencies)} currencies (active_only={active_only})")
        return jsonify(currencies), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching currencies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/currencies/base', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_base_currency():
    """Get the company's base currency"""
    try:
        base_currency = Currency.get_base_currency()
        if not base_currency:
            return jsonify({'error': 'No base currency set'}), 404
        
        return jsonify(base_currency.to_dict()), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching base currency: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/currencies/base', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def set_base_currency():
    """
    Set the company's base currency
    Body: {"currency_code": "USD"}
    """
    try:
        data = request.get_json()
        currency_code = data.get('currency_code')
        
        if not currency_code:
            return jsonify({'error': 'currency_code is required'}), 400
        
        success = CurrencyService.set_base_currency(currency_code)
        if success:
            return jsonify({'message': f'Base currency set to {currency_code}'}), 200
        else:
            return jsonify({'error': 'Failed to set base currency'}), 400
            
    except Exception as e:
        logger.error(f"❌ Error setting base currency: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/exchange-rates/update', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def update_exchange_rates():
    """
    Update exchange rates from ExchangeRate-API
    Body: {"base_currency": "USD"} (optional, defaults to USD)
    """
    try:
        data = request.get_json() or {}
        base_currency = data.get('base_currency', 'USD')
        
        logger.info(f"🔄 Starting exchange rate update with base currency: {base_currency}")
        success = CurrencyService.update_exchange_rates(base_currency)
        
        if success:
            return jsonify({
                'message': 'Exchange rates updated successfully',
                'base_currency': base_currency,
                'timestamp': db.session.execute(db.text('SELECT CURRENT_TIMESTAMP')).scalar().isoformat()
            }), 200
        else:
            return jsonify({'error': 'Failed to update exchange rates'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error updating exchange rates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/exchange-rates', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_exchange_rates():
    """
    Get current exchange rates
    Query params:
    - from_currency: string (optional)
    - to_currency: string (optional)
    """
    try:
        from_currency = request.args.get('from_currency')
        to_currency = request.args.get('to_currency')
        
        query = ExchangeRate.query.filter_by(is_current=True)
        
        if from_currency:
            query = query.join(Currency, ExchangeRate.from_currency_id == Currency.id).filter(Currency.code == from_currency)
        
        if to_currency:
            query = query.join(Currency, ExchangeRate.to_currency_id == Currency.id).filter(Currency.code == to_currency)
        
        rates = query.all()
        
        return jsonify([rate.to_dict() for rate in rates]), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching exchange rates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/exchange-rates/history', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_exchange_rate_history():
    """
    Get historical exchange rates
    Query params:
    - from_currency: string (required)
    - to_currency: string (required)
    - days: int (optional, default: 30)
    """
    try:
        from_currency = request.args.get('from_currency')
        to_currency = request.args.get('to_currency')
        days = int(request.args.get('days', 30))
        
        if not from_currency or not to_currency:
            return jsonify({'error': 'from_currency and to_currency are required'}), 400
        
        history = CurrencyService.get_exchange_rate_history(from_currency, to_currency, days)
        
        return jsonify({
            'from_currency': from_currency,
            'to_currency': to_currency,
            'days': days,
            'history': history
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching exchange rate history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/convert', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def convert_currency():
    """
    Convert amount between currencies
    Body: {
        "amount": 100.0,
        "from_currency": "USD",
        "to_currency": "EUR",
        "record_conversion": true
    }
    """
    try:
        data = request.get_json()
        
        amount = data.get('amount')
        from_currency = data.get('from_currency')
        to_currency = data.get('to_currency')
        record_conversion = data.get('record_conversion', True)
        
        if not all([amount, from_currency, to_currency]):
            return jsonify({'error': 'amount, from_currency, and to_currency are required'}), 400
        
        converted_amount, exchange_rate = CurrencyService.convert_currency(
            float(amount), from_currency, to_currency, record_conversion
        )
        
        if converted_amount is None:
            return jsonify({'error': 'Currency conversion failed'}), 400
        
        return jsonify({
            'original_amount': float(amount),
            'from_currency': from_currency,
            'to_currency': to_currency,
            'converted_amount': converted_amount,
            'exchange_rate': exchange_rate,
            'conversion_recorded': record_conversion
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error converting currency: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/conversions', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_conversion_history():
    """
    Get currency conversion history
    Query params:
    - limit: int (optional, default: 50)
    - reference_type: string (optional)
    """
    try:
        limit = int(request.args.get('limit', 50))
        reference_type = request.args.get('reference_type')
        
        query = CurrencyConversion.query
        
        if reference_type:
            query = query.filter_by(reference_type=reference_type)
        
        conversions = query.order_by(CurrencyConversion.conversion_date.desc()).limit(limit).all()
        
        return jsonify([conversion.to_dict() for conversion in conversions]), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching conversion history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/initialize', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def initialize_currencies():
    """
    Initialize currency database with popular currencies
    """
    try:
        logger.info("🚀 Starting currency initialization...")
        success = CurrencyService.initialize_currencies()
        
        if success:
            # Also update exchange rates after initialization
            logger.info("🔄 Updating exchange rates after initialization...")
            CurrencyService.update_exchange_rates()
            
            return jsonify({
                'message': 'Currencies initialized successfully',
                'currencies_added': len(CurrencyService.POPULAR_CURRENCIES)
            }), 200
        else:
            return jsonify({'error': 'Currency initialization failed'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error initializing currencies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@currency_bp.route('/status', methods=['GET'])
def get_currency_status():
    """
    Get currency system status and statistics
    """
    try:
        total_currencies = Currency.query.count()
        active_currencies = Currency.query.filter_by(is_active=True).count()
        base_currency = Currency.get_base_currency()
        total_rates = ExchangeRate.query.filter_by(is_current=True).count()
        total_conversions = CurrencyConversion.query.count()
        
        # Get latest rate update
        latest_rate = ExchangeRate.query.filter_by(is_current=True).order_by(ExchangeRate.created_at.desc()).first()
        
        return jsonify({
            'status': 'operational',
            'statistics': {
                'total_currencies': total_currencies,
                'active_currencies': active_currencies,
                'base_currency': base_currency.code if base_currency else None,
                'current_exchange_rates': total_rates,
                'total_conversions': total_conversions,
                'last_rate_update': latest_rate.created_at.isoformat() if latest_rate else None
            },
            'api_source': 'ExchangeRate-API (free)',
            'endpoints': {
                'currencies': '/currency/currencies',
                'exchange_rates': '/currency/exchange-rates',
                'convert': '/currency/convert',
                'update_rates': '/currency/exchange-rates/update'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching currency status: {str(e)}")
        return jsonify({'error': str(e)}), 500

