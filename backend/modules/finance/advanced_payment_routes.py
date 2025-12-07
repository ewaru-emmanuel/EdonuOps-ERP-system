from flask import Blueprint, request, jsonify
from app import db
from .payment_models import PaymentMethod, BankAccount, PaymentTransaction, PartialPayment
from .currency_models import ExchangeRate
from .advanced_models import ChartOfAccounts
from datetime import datetime, date
import json

advanced_payment_bp = Blueprint('advanced_payment', __name__, url_prefix='/api/finance')

# ============= EXCHANGE RATES =============

@advanced_payment_bp.route('/exchange-rates', methods=['GET'])
def get_exchange_rates():
    """Get exchange rates for a date range"""
    try:
        from_currency = request.args.get('from_currency', 'USD')
        to_currency = request.args.get('to_currency')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = ExchangeRate.query.filter_by(from_currency=from_currency)
        
        if to_currency:
            query = query.filter_by(to_currency=to_currency)
        
        if start_date:
            query = query.filter(ExchangeRate.rate_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(ExchangeRate.rate_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        rates = query.order_by(ExchangeRate.rate_date.desc()).all()
        
        return jsonify([{
            'id': rate.id,
            'from_currency': rate.from_currency,
            'to_currency': rate.to_currency,
            'rate': rate.rate,
            'rate_date': rate.rate_date.isoformat(),
            'source': rate.source,
            'source_reference': rate.source_reference,
            'created_at': rate.created_at.isoformat(),
            'created_by': rate.created_by
        } for rate in rates]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/exchange-rates', methods=['POST'])
def create_exchange_rate():
    """Create or update exchange rate"""
    try:
        data = request.get_json()
        
        required_fields = ['from_currency', 'to_currency', 'rate']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        rate_date = datetime.strptime(data.get('rate_date', date.today().isoformat()), '%Y-%m-%d').date()
        
        rate = ExchangeRate.set_rate(
            from_currency=data['from_currency'],
            to_currency=data['to_currency'],
            rate=float(data['rate']),
            rate_date=rate_date,
            source=data.get('source', 'manual'),
            created_by=data.get('created_by')
        )
        
        return jsonify({
            'message': 'Exchange rate saved successfully',
            'id': rate.id,
            'from_currency': rate.from_currency,
            'to_currency': rate.to_currency,
            'rate': rate.rate,
            'rate_date': rate.rate_date.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/exchange-rates/current', methods=['GET'])
def get_current_exchange_rate():
    """Get current exchange rate for currency pair"""
    try:
        from_currency = request.args.get('from_currency', 'USD')
        to_currency = request.args.get('to_currency', 'USD')
        rate_date = request.args.get('rate_date')
        
        if rate_date:
            rate_date = datetime.strptime(rate_date, '%Y-%m-%d').date()
        
        rate = ExchangeRate.get_rate(from_currency, to_currency, rate_date)
        
        if rate is None:
            return jsonify({'error': f'No exchange rate found for {from_currency}/{to_currency}'}), 404
        
        return jsonify({
            'from_currency': from_currency,
            'to_currency': to_currency,
            'rate': rate,
            'rate_date': rate_date.isoformat() if rate_date else date.today().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= PARTIAL PAYMENTS =============

@advanced_payment_bp.route('/partial-payments', methods=['GET'])
def get_partial_payments():
    """Get partial payments for an invoice or all payments"""
    try:
        invoice_id = request.args.get('invoice_id')
        invoice_type = request.args.get('invoice_type')
        
        if invoice_id and invoice_type:
            payments = PartialPayment.get_invoice_payments(int(invoice_id), invoice_type)
        else:
            payments = PartialPayment.query.order_by(PartialPayment.payment_date.desc()).all()
        
        return jsonify([{
            'id': payment.id,
            'payment_reference': payment.payment_reference,
            'invoice_id': payment.invoice_id,
            'invoice_type': payment.invoice_type,
            'payment_date': payment.payment_date.isoformat(),
            'amount': payment.amount,
            'currency': payment.currency,
            'exchange_rate': payment.exchange_rate,
            'base_amount': payment.base_amount,
            'payment_method_id': payment.payment_method_id,
            'bank_account_id': payment.bank_account_id,
            'processing_fee': payment.processing_fee,
            'net_amount': payment.net_amount,
            'reference_number': payment.reference_number,
            'notes': payment.notes,
            'status': payment.status,
            'created_at': payment.created_at.isoformat(),
            'created_by': payment.created_by,
            'payment_method': payment.payment_method.name if payment.payment_method else None,
            'bank_account': payment.bank_account.account_name if payment.bank_account else None
        } for payment in payments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/partial-payments', methods=['POST'])
def create_partial_payment():
    """Create a new partial payment"""
    try:
        data = request.get_json()
        
        required_fields = ['payment_reference', 'invoice_id', 'invoice_type', 'payment_date', 'amount', 'payment_method_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Calculate exchange rate if different currency
        currency = data.get('currency', 'USD')
        exchange_rate = data.get('exchange_rate', 1.0)
        base_amount = float(data['amount']) * exchange_rate
        
        # Calculate processing fee if payment method has default rate
        payment_method = PaymentMethod.query.get(data['payment_method_id'])
        processing_fee = 0.0
        if payment_method and payment_method.default_processing_fee_rate > 0:
            processing_fee = float(data['amount']) * (payment_method.default_processing_fee_rate / 100)
        
        net_amount = float(data['amount']) - processing_fee
        
        payment = PartialPayment(
            payment_reference=data['payment_reference'],
            invoice_id=int(data['invoice_id']),
            invoice_type=data['invoice_type'],
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date(),
            amount=float(data['amount']),
            currency=currency,
            exchange_rate=exchange_rate,
            base_amount=base_amount,
            payment_method_id=int(data['payment_method_id']),
            bank_account_id=int(data['bank_account_id']) if data.get('bank_account_id') else None,
            processing_fee=processing_fee,
            net_amount=net_amount,
            reference_number=data.get('reference_number'),
            notes=data.get('notes'),
            status=data.get('status', 'pending'),
            created_by=data.get('created_by')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Partial payment created successfully',
            'id': payment.id,
            'payment_reference': payment.payment_reference,
            'net_amount': payment.net_amount
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/partial-payments/<int:payment_id>', methods=['PUT'])
def update_partial_payment(payment_id):
    """Update partial payment status"""
    try:
        data = request.get_json()
        payment = PartialPayment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Partial payment not found'}), 404
        
        if 'status' in data:
            payment.status = data['status']
        
        if 'notes' in data:
            payment.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Partial payment updated successfully',
            'id': payment.id,
            'status': payment.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/partial-payments/invoice/<int:invoice_id>/<invoice_type>', methods=['GET'])
def get_invoice_payment_summary(invoice_id, invoice_type):
    """Get payment summary for an invoice"""
    try:
        payments = PartialPayment.get_invoice_payments(invoice_id, invoice_type)
        total_paid = PartialPayment.get_total_paid(invoice_id, invoice_type)
        
        return jsonify({
            'invoice_id': invoice_id,
            'invoice_type': invoice_type,
            'total_payments': len(payments),
            'total_paid': total_paid,
            'payments': [{
                'id': payment.id,
                'payment_reference': payment.payment_reference,
                'payment_date': payment.payment_date.isoformat(),
                'amount': payment.amount,
                'net_amount': payment.net_amount,
                'status': payment.status,
                'payment_method': payment.payment_method.name if payment.payment_method else None
            } for payment in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= PROCESSING FEE AUTOMATION =============

@advanced_payment_bp.route('/processing-fees/calculate', methods=['POST'])
def calculate_processing_fee():
    """Calculate processing fee for a payment"""
    try:
        data = request.get_json()
        
        amount = float(data.get('amount', 0))
        payment_method_id = data.get('payment_method_id')
        
        if not payment_method_id:
            return jsonify({'error': 'payment_method_id is required'}), 400
        
        payment_method = PaymentMethod.query.get(payment_method_id)
        if not payment_method:
            return jsonify({'error': 'Payment method not found'}), 404
        
        processing_fee = 0.0
        if payment_method.default_processing_fee_rate > 0:
            processing_fee = amount * (payment_method.default_processing_fee_rate / 100)
        
        net_amount = amount - processing_fee
        
        return jsonify({
            'amount': amount,
            'payment_method': payment_method.name,
            'processing_fee_rate': payment_method.default_processing_fee_rate,
            'processing_fee': processing_fee,
            'net_amount': net_amount
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= MULTI-CURRENCY SUPPORT =============

@advanced_payment_bp.route('/currencies', methods=['GET'])
def get_supported_currencies():
    """Get list of supported currencies"""
    try:
        currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$'},
            {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$'},
            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},
            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥'},
            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'},
            {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$'},
            {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$'},
            {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩'},
            {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$'},
            {'code': 'HKD', 'name': 'Hong Kong Dollar', 'symbol': 'HK$'},
            {'code': 'NOK', 'name': 'Norwegian Krone', 'symbol': 'kr'},
            {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr'},
            {'code': 'DKK', 'name': 'Danish Krone', 'symbol': 'kr'},
            {'code': 'PLN', 'name': 'Polish Zloty', 'symbol': 'zł'},
            {'code': 'CZK', 'name': 'Czech Koruna', 'symbol': 'Kč'},
            {'code': 'HUF', 'name': 'Hungarian Forint', 'symbol': 'Ft'}
        ]
        
        return jsonify(currencies), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= AUTO-MATCHING & RECONCILIATION =============

@advanced_payment_bp.route('/auto-matching/unmatched-transactions', methods=['GET'])
def get_unmatched_transactions():
    """Get unmatched bank transactions"""
    try:
        from .auto_matching_service import AutoMatchingService
        
        days_back = int(request.args.get('days_back', 30))
        transactions = AutoMatchingService.get_unmatched_transactions(days_back)
        
        return jsonify({
            'transactions': transactions,
            'count': len(transactions),
            'days_back': days_back
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/auto-matching/find-matches', methods=['POST'])
def find_potential_matches():
    """Find potential matches for a bank transaction"""
    try:
        from .auto_matching_service import AutoMatchingService
        
        data = request.get_json()
        bank_transaction = data.get('transaction')
        tolerance_days = data.get('tolerance_days', 3)
        amount_tolerance = data.get('amount_tolerance', 0.01)
        
        if not bank_transaction:
            return jsonify({'error': 'Transaction data is required'}), 400
        
        matches = AutoMatchingService.find_potential_matches(
            bank_transaction, tolerance_days, amount_tolerance
        )
        
        # Convert matches to JSON-serializable format
        json_matches = []
        for match in matches:
            json_match = {
                'type': match['type'],
                'confidence': match['confidence'],
                'match_reasons': match['match_reasons'],
                'invoice': {
                    'id': match['invoice'].id,
                    'invoice_number': match['invoice'].invoice_number,
                    'total_amount': match['invoice'].total_amount,
                    'due_date': match['invoice'].due_date.isoformat(),
                    'status': match['invoice'].status,
                    'customer_name': getattr(match['invoice'], 'customer_name', None),
                    'vendor_name': getattr(match['invoice'], 'vendor_name', None)
                }
            }
            json_matches.append(json_match)
        
        return jsonify({
            'matches': json_matches,
            'count': len(json_matches),
            'transaction': bank_transaction
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/auto-matching/match-transaction', methods=['POST'])
def match_transaction():
    """Match a bank transaction with an invoice"""
    try:
        from .auto_matching_service import AutoMatchingService
        
        data = request.get_json()
        bank_transaction_id = data.get('bank_transaction_id')
        invoice_id = data.get('invoice_id')
        invoice_type = data.get('invoice_type')
        confidence = data.get('confidence', 0.0)
        
        required_fields = ['bank_transaction_id', 'invoice_id', 'invoice_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        result = AutoMatchingService.auto_match_transaction(
            bank_transaction_id, invoice_id, invoice_type, confidence
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/auto-matching/run-auto-matching', methods=['POST'])
def run_auto_matching():
    """Run auto-matching for all unmatched transactions"""
    try:
        from .auto_matching_service import AutoMatchingService
        
        data = request.get_json() or {}
        confidence_threshold = data.get('confidence_threshold', 0.8)
        
        results = AutoMatchingService.run_auto_matching(confidence_threshold)
        
        return jsonify({
            'message': 'Auto-matching completed',
            'results': results,
            'summary': {
                'total_processed': len(results['details']),
                'matched': results['matched'],
                'potential_matches': results['potential_matches'],
                'no_matches': results['no_matches']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= DISCREPANCY RESOLUTION =============

@advanced_payment_bp.route('/reconciliation/discrepancies', methods=['GET'])
def get_reconciliation_discrepancies():
    """Get reconciliation discrepancies that need resolution"""
    try:
        # Simulate discrepancy data - in real implementation, this would come from reconciliation engine
        discrepancies = [
            {
                'id': 1,
                'type': 'amount_mismatch',
                'description': 'Bank transaction amount differs from invoice amount',
                'bank_transaction': {
                    'id': 'TXN001',
                    'amount': 1485.00,
                    'date': '2024-09-18',
                    'reference': 'INV-2024-001'
                },
                'invoice': {
                    'id': 15,
                    'type': 'AR',
                    'invoice_number': 'INV-2024-001',
                    'amount': 1500.00,
                    'customer_name': 'ABC Corp'
                },
                'difference': -15.00,
                'suggested_resolution': 'Bank fees or discount applied',
                'status': 'pending',
                'created_date': '2024-09-18'
            },
            {
                'id': 2,
                'type': 'date_mismatch',
                'description': 'Payment received outside expected date range',
                'bank_transaction': {
                    'id': 'TXN002',
                    'amount': 2200.00,
                    'date': '2024-09-15',
                    'reference': 'WIRE-789'
                },
                'invoice': {
                    'id': 23,
                    'type': 'AR',
                    'invoice_number': 'INV-2024-023',
                    'amount': 2200.00,
                    'customer_name': 'DEF Ltd'
                },
                'difference': 0.00,
                'suggested_resolution': 'Early payment - confirm with customer',
                'status': 'pending',
                'created_date': '2024-09-15'
            }
        ]
        
        return jsonify({
            'discrepancies': discrepancies,
            'count': len(discrepancies),
            'summary': {
                'amount_mismatches': 1,
                'date_mismatches': 1,
                'pending_resolution': 2
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@advanced_payment_bp.route('/reconciliation/discrepancies/<int:discrepancy_id>/resolve', methods=['POST'])
def resolve_discrepancy(discrepancy_id):
    """Resolve a reconciliation discrepancy"""
    try:
        data = request.get_json()
        resolution_type = data.get('resolution_type')
        notes = data.get('notes', '')
        
        if not resolution_type:
            return jsonify({'error': 'resolution_type is required'}), 400
        
        # In real implementation, this would update the discrepancy record
        # and potentially create adjusting entries
        
        return jsonify({
            'message': 'Discrepancy resolved successfully',
            'discrepancy_id': discrepancy_id,
            'resolution_type': resolution_type,
            'resolved_date': datetime.now().isoformat(),
            'notes': notes
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

        if not payment_method_id:

            return jsonify({'error': 'payment_method_id is required'}), 400

        

        payment_method = PaymentMethod.query.get(payment_method_id)

        if not payment_method:

            return jsonify({'error': 'Payment method not found'}), 404

        

        processing_fee = 0.0

        if payment_method.default_processing_fee_rate > 0:

            processing_fee = amount * (payment_method.default_processing_fee_rate / 100)

        

        net_amount = amount - processing_fee

        

        return jsonify({

            'amount': amount,

            'payment_method': payment_method.name,

            'processing_fee_rate': payment_method.default_processing_fee_rate,

            'processing_fee': processing_fee,

            'net_amount': net_amount

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





# ============= MULTI-CURRENCY SUPPORT =============



@advanced_payment_bp.route('/currencies', methods=['GET'])

def get_supported_currencies():

    """Get list of supported currencies"""

    try:

        currencies = [

            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},

            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},

            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},

            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},

            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$'},

            {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$'},

            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},

            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥'},

            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'},

            {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$'},

            {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$'},

            {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩'},

            {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$'},

            {'code': 'HKD', 'name': 'Hong Kong Dollar', 'symbol': 'HK$'},

            {'code': 'NOK', 'name': 'Norwegian Krone', 'symbol': 'kr'},

            {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr'},

            {'code': 'DKK', 'name': 'Danish Krone', 'symbol': 'kr'},

            {'code': 'PLN', 'name': 'Polish Zloty', 'symbol': 'zł'},

            {'code': 'CZK', 'name': 'Czech Koruna', 'symbol': 'Kč'},

            {'code': 'HUF', 'name': 'Hungarian Forint', 'symbol': 'Ft'}

        ]

        

        return jsonify(currencies), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





# ============= AUTO-MATCHING & RECONCILIATION =============



@advanced_payment_bp.route('/auto-matching/unmatched-transactions', methods=['GET'])

def get_unmatched_transactions():

    """Get unmatched bank transactions"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        days_back = int(request.args.get('days_back', 30))

        transactions = AutoMatchingService.get_unmatched_transactions(days_back)

        

        return jsonify({

            'transactions': transactions,

            'count': len(transactions),

            'days_back': days_back

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/auto-matching/find-matches', methods=['POST'])

def find_potential_matches():

    """Find potential matches for a bank transaction"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        data = request.get_json()

        bank_transaction = data.get('transaction')

        tolerance_days = data.get('tolerance_days', 3)

        amount_tolerance = data.get('amount_tolerance', 0.01)

        

        if not bank_transaction:

            return jsonify({'error': 'Transaction data is required'}), 400

        

        matches = AutoMatchingService.find_potential_matches(

            bank_transaction, tolerance_days, amount_tolerance

        )

        

        # Convert matches to JSON-serializable format

        json_matches = []

        for match in matches:

            json_match = {

                'type': match['type'],

                'confidence': match['confidence'],

                'match_reasons': match['match_reasons'],

                'invoice': {

                    'id': match['invoice'].id,

                    'invoice_number': match['invoice'].invoice_number,

                    'total_amount': match['invoice'].total_amount,

                    'due_date': match['invoice'].due_date.isoformat(),

                    'status': match['invoice'].status,

                    'customer_name': getattr(match['invoice'], 'customer_name', None),

                    'vendor_name': getattr(match['invoice'], 'vendor_name', None)

                }

            }

            json_matches.append(json_match)

        

        return jsonify({

            'matches': json_matches,

            'count': len(json_matches),

            'transaction': bank_transaction

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/auto-matching/match-transaction', methods=['POST'])

def match_transaction():

    """Match a bank transaction with an invoice"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        data = request.get_json()

        bank_transaction_id = data.get('bank_transaction_id')

        invoice_id = data.get('invoice_id')

        invoice_type = data.get('invoice_type')

        confidence = data.get('confidence', 0.0)

        

        required_fields = ['bank_transaction_id', 'invoice_id', 'invoice_type']

        for field in required_fields:

            if field not in data:

                return jsonify({'error': f'{field} is required'}), 400

        

        result = AutoMatchingService.auto_match_transaction(

            bank_transaction_id, invoice_id, invoice_type, confidence

        )

        

        if result['success']:

            return jsonify(result), 200

        else:

            return jsonify(result), 400

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/auto-matching/run-auto-matching', methods=['POST'])

def run_auto_matching():

    """Run auto-matching for all unmatched transactions"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        data = request.get_json() or {}

        confidence_threshold = data.get('confidence_threshold', 0.8)

        

        results = AutoMatchingService.run_auto_matching(confidence_threshold)

        

        return jsonify({

            'message': 'Auto-matching completed',

            'results': results,

            'summary': {

                'total_processed': len(results['details']),

                'matched': results['matched'],

                'potential_matches': results['potential_matches'],

                'no_matches': results['no_matches']

            }

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





# ============= DISCREPANCY RESOLUTION =============



@advanced_payment_bp.route('/reconciliation/discrepancies', methods=['GET'])

def get_reconciliation_discrepancies():

    """Get reconciliation discrepancies that need resolution"""

    try:

        # Simulate discrepancy data - in real implementation, this would come from reconciliation engine

        discrepancies = [

            {

                'id': 1,

                'type': 'amount_mismatch',

                'description': 'Bank transaction amount differs from invoice amount',

                'bank_transaction': {

                    'id': 'TXN001',

                    'amount': 1485.00,

                    'date': '2024-09-18',

                    'reference': 'INV-2024-001'

                },

                'invoice': {

                    'id': 15,

                    'type': 'AR',

                    'invoice_number': 'INV-2024-001',

                    'amount': 1500.00,

                    'customer_name': 'ABC Corp'

                },

                'difference': -15.00,

                'suggested_resolution': 'Bank fees or discount applied',

                'status': 'pending',

                'created_date': '2024-09-18'

            },

            {

                'id': 2,

                'type': 'date_mismatch',

                'description': 'Payment received outside expected date range',

                'bank_transaction': {

                    'id': 'TXN002',

                    'amount': 2200.00,

                    'date': '2024-09-15',

                    'reference': 'WIRE-789'

                },

                'invoice': {

                    'id': 23,

                    'type': 'AR',

                    'invoice_number': 'INV-2024-023',

                    'amount': 2200.00,

                    'customer_name': 'DEF Ltd'

                },

                'difference': 0.00,

                'suggested_resolution': 'Early payment - confirm with customer',

                'status': 'pending',

                'created_date': '2024-09-15'

            }

        ]

        

        return jsonify({

            'discrepancies': discrepancies,

            'count': len(discrepancies),

            'summary': {

                'amount_mismatches': 1,

                'date_mismatches': 1,

                'pending_resolution': 2

            }

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/reconciliation/discrepancies/<int:discrepancy_id>/resolve', methods=['POST'])

def resolve_discrepancy(discrepancy_id):

    """Resolve a reconciliation discrepancy"""

    try:

        data = request.get_json()

        resolution_type = data.get('resolution_type')

        notes = data.get('notes', '')

        

        if not resolution_type:

            return jsonify({'error': 'resolution_type is required'}), 400

        

        # In real implementation, this would update the discrepancy record

        # and potentially create adjusting entries

        

        return jsonify({

            'message': 'Discrepancy resolved successfully',

            'discrepancy_id': discrepancy_id,

            'resolution_type': resolution_type,

            'resolved_date': datetime.now().isoformat(),

            'notes': notes

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500



        if not payment_method_id:

            return jsonify({'error': 'payment_method_id is required'}), 400

        

        payment_method = PaymentMethod.query.get(payment_method_id)

        if not payment_method:

            return jsonify({'error': 'Payment method not found'}), 404

        

        processing_fee = 0.0

        if payment_method.default_processing_fee_rate > 0:

            processing_fee = amount * (payment_method.default_processing_fee_rate / 100)

        

        net_amount = amount - processing_fee

        

        return jsonify({

            'amount': amount,

            'payment_method': payment_method.name,

            'processing_fee_rate': payment_method.default_processing_fee_rate,

            'processing_fee': processing_fee,

            'net_amount': net_amount

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





# ============= MULTI-CURRENCY SUPPORT =============



@advanced_payment_bp.route('/currencies', methods=['GET'])

def get_supported_currencies():

    """Get list of supported currencies"""

    try:

        currencies = [

            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},

            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},

            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},

            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},

            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$'},

            {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$'},

            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},

            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥'},

            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'},

            {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$'},

            {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$'},

            {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩'},

            {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$'},

            {'code': 'HKD', 'name': 'Hong Kong Dollar', 'symbol': 'HK$'},

            {'code': 'NOK', 'name': 'Norwegian Krone', 'symbol': 'kr'},

            {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr'},

            {'code': 'DKK', 'name': 'Danish Krone', 'symbol': 'kr'},

            {'code': 'PLN', 'name': 'Polish Zloty', 'symbol': 'zł'},

            {'code': 'CZK', 'name': 'Czech Koruna', 'symbol': 'Kč'},

            {'code': 'HUF', 'name': 'Hungarian Forint', 'symbol': 'Ft'}

        ]

        

        return jsonify(currencies), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





# ============= AUTO-MATCHING & RECONCILIATION =============



@advanced_payment_bp.route('/auto-matching/unmatched-transactions', methods=['GET'])

def get_unmatched_transactions():

    """Get unmatched bank transactions"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        days_back = int(request.args.get('days_back', 30))

        transactions = AutoMatchingService.get_unmatched_transactions(days_back)

        

        return jsonify({

            'transactions': transactions,

            'count': len(transactions),

            'days_back': days_back

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/auto-matching/find-matches', methods=['POST'])

def find_potential_matches():

    """Find potential matches for a bank transaction"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        data = request.get_json()

        bank_transaction = data.get('transaction')

        tolerance_days = data.get('tolerance_days', 3)

        amount_tolerance = data.get('amount_tolerance', 0.01)

        

        if not bank_transaction:

            return jsonify({'error': 'Transaction data is required'}), 400

        

        matches = AutoMatchingService.find_potential_matches(

            bank_transaction, tolerance_days, amount_tolerance

        )

        

        # Convert matches to JSON-serializable format

        json_matches = []

        for match in matches:

            json_match = {

                'type': match['type'],

                'confidence': match['confidence'],

                'match_reasons': match['match_reasons'],

                'invoice': {

                    'id': match['invoice'].id,

                    'invoice_number': match['invoice'].invoice_number,

                    'total_amount': match['invoice'].total_amount,

                    'due_date': match['invoice'].due_date.isoformat(),

                    'status': match['invoice'].status,

                    'customer_name': getattr(match['invoice'], 'customer_name', None),

                    'vendor_name': getattr(match['invoice'], 'vendor_name', None)

                }

            }

            json_matches.append(json_match)

        

        return jsonify({

            'matches': json_matches,

            'count': len(json_matches),

            'transaction': bank_transaction

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/auto-matching/match-transaction', methods=['POST'])

def match_transaction():

    """Match a bank transaction with an invoice"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        data = request.get_json()

        bank_transaction_id = data.get('bank_transaction_id')

        invoice_id = data.get('invoice_id')

        invoice_type = data.get('invoice_type')

        confidence = data.get('confidence', 0.0)

        

        required_fields = ['bank_transaction_id', 'invoice_id', 'invoice_type']

        for field in required_fields:

            if field not in data:

                return jsonify({'error': f'{field} is required'}), 400

        

        result = AutoMatchingService.auto_match_transaction(

            bank_transaction_id, invoice_id, invoice_type, confidence

        )

        

        if result['success']:

            return jsonify(result), 200

        else:

            return jsonify(result), 400

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/auto-matching/run-auto-matching', methods=['POST'])

def run_auto_matching():

    """Run auto-matching for all unmatched transactions"""

    try:

        from .auto_matching_service import AutoMatchingService

        

        data = request.get_json() or {}

        confidence_threshold = data.get('confidence_threshold', 0.8)

        

        results = AutoMatchingService.run_auto_matching(confidence_threshold)

        

        return jsonify({

            'message': 'Auto-matching completed',

            'results': results,

            'summary': {

                'total_processed': len(results['details']),

                'matched': results['matched'],

                'potential_matches': results['potential_matches'],

                'no_matches': results['no_matches']

            }

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





# ============= DISCREPANCY RESOLUTION =============



@advanced_payment_bp.route('/reconciliation/discrepancies', methods=['GET'])

def get_reconciliation_discrepancies():

    """Get reconciliation discrepancies that need resolution"""

    try:

        # Simulate discrepancy data - in real implementation, this would come from reconciliation engine

        discrepancies = [

            {

                'id': 1,

                'type': 'amount_mismatch',

                'description': 'Bank transaction amount differs from invoice amount',

                'bank_transaction': {

                    'id': 'TXN001',

                    'amount': 1485.00,

                    'date': '2024-09-18',

                    'reference': 'INV-2024-001'

                },

                'invoice': {

                    'id': 15,

                    'type': 'AR',

                    'invoice_number': 'INV-2024-001',

                    'amount': 1500.00,

                    'customer_name': 'ABC Corp'

                },

                'difference': -15.00,

                'suggested_resolution': 'Bank fees or discount applied',

                'status': 'pending',

                'created_date': '2024-09-18'

            },

            {

                'id': 2,

                'type': 'date_mismatch',

                'description': 'Payment received outside expected date range',

                'bank_transaction': {

                    'id': 'TXN002',

                    'amount': 2200.00,

                    'date': '2024-09-15',

                    'reference': 'WIRE-789'

                },

                'invoice': {

                    'id': 23,

                    'type': 'AR',

                    'invoice_number': 'INV-2024-023',

                    'amount': 2200.00,

                    'customer_name': 'DEF Ltd'

                },

                'difference': 0.00,

                'suggested_resolution': 'Early payment - confirm with customer',

                'status': 'pending',

                'created_date': '2024-09-15'

            }

        ]

        

        return jsonify({

            'discrepancies': discrepancies,

            'count': len(discrepancies),

            'summary': {

                'amount_mismatches': 1,

                'date_mismatches': 1,

                'pending_resolution': 2

            }

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@advanced_payment_bp.route('/reconciliation/discrepancies/<int:discrepancy_id>/resolve', methods=['POST'])

def resolve_discrepancy(discrepancy_id):

    """Resolve a reconciliation discrepancy"""

    try:

        data = request.get_json()

        resolution_type = data.get('resolution_type')

        notes = data.get('notes', '')

        

        if not resolution_type:

            return jsonify({'error': 'resolution_type is required'}), 400

        

        # In real implementation, this would update the discrepancy record

        # and potentially create adjusting entries

        

        return jsonify({

            'message': 'Discrepancy resolved successfully',

            'discrepancy_id': discrepancy_id,

            'resolution_type': resolution_type,

            'resolved_date': datetime.now().isoformat(),

            'notes': notes

        }), 200

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500


