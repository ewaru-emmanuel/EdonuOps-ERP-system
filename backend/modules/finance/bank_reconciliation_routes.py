from flask import Blueprint, request, jsonify
from app import db
from datetime import datetime, date
from sqlalchemy import and_, or_, func
from modules.core.permissions import require_permission
from .payment_models import BankAccount, BankTransaction, ReconciliationSession
from .advanced_models import GeneralLedgerEntry, AccountsReceivable, AccountsPayable
import json

# Create Blueprint
bank_reconciliation_bp = Blueprint('bank_reconciliation', __name__, url_prefix='/api/finance/reconciliation')

# Helper function to get unreconciled GL entries for a bank account
def get_unreconciled_gl_entries(bank_account_id, start_date=None, end_date=None):
    """Get all GL entries that affect a specific bank account and haven't been reconciled"""
    query = GeneralLedgerEntry.query.filter(
        GeneralLedgerEntry.account_id == bank_account_id
    )
    
    if start_date:
        query = query.filter(GeneralLedgerEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(GeneralLedgerEntry.entry_date <= end_date)
    
    return query.order_by(GeneralLedgerEntry.entry_date.desc()).all()

# Bank Reconciliation Session Endpoints
@bank_reconciliation_bp.route('/reconciliation-sessions', methods=['GET'])
@require_permission('finance.reconciliation.read')
def get_reconciliation_sessions():
    """Get all reconciliation sessions"""
    try:
        bank_account_id = request.args.get('bank_account_id')
        status = request.args.get('status')
        
        query = ReconciliationSession.query
        
        if bank_account_id:
            query = query.filter(ReconciliationSession.bank_account_id == bank_account_id)
        if status:
            query = query.filter(ReconciliationSession.status == status)
        
        sessions = query.order_by(ReconciliationSession.statement_date.desc()).all()
        
        return jsonify([{
            'id': session.id,
            'bank_account_id': session.bank_account_id,
            'bank_account_name': session.bank_account.account_name,
            'statement_date': session.statement_date.isoformat() if session.statement_date else None,
            'statement_balance': session.statement_balance,
            'book_balance': session.book_balance,
            'difference': session.difference,
            'status': session.status,
            'outstanding_deposits': session.outstanding_deposits,
            'outstanding_checks': session.outstanding_checks,
            'bank_charges': session.bank_charges,
            'bank_interest': session.bank_interest,
            'notes': session.notes,
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        } for session in sessions])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bank_reconciliation_bp.route('/reconciliation-sessions', methods=['POST'])
@require_permission('finance.reconciliation.create')
def create_reconciliation_session():
    """Create a new reconciliation session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['bank_account_id', 'statement_date', 'statement_balance']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get current book balance for the bank account
        bank_account = BankAccount.query.get(data['bank_account_id'])
        if not bank_account:
            return jsonify({'error': 'Bank account not found'}), 404
        
        # Calculate book balance from GL entries
        gl_entries = get_unreconciled_gl_entries(data['bank_account_id'])
        book_balance = sum(entry.debit_amount - entry.credit_amount for entry in gl_entries)
        
        # Create reconciliation session
        session = ReconciliationSession(
            bank_account_id=data['bank_account_id'],
            statement_date=datetime.strptime(data['statement_date'], '%Y-%m-%d').date(),
            statement_balance=float(data['statement_balance']),
            book_balance=book_balance,
            difference=float(data['statement_balance']) - book_balance,
            notes=data.get('notes'),
            created_by=data.get('created_by', 'system')
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'id': session.id,
            'message': 'Reconciliation session created successfully',
            'book_balance': book_balance,
            'difference': session.difference
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bank Transaction Endpoints
@bank_reconciliation_bp.route('/bank-transactions', methods=['GET'])
@require_permission('finance.reconciliation.read')
def get_bank_transactions():
    """Get bank transactions for reconciliation"""
    try:
        bank_account_id = request.args.get('bank_account_id')
        session_id = request.args.get('session_id')
        matched = request.args.get('matched')  # 'true', 'false', or None for all
        
        query = BankTransaction.query
        
        if bank_account_id:
            query = query.filter(BankTransaction.bank_account_id == bank_account_id)
        if session_id:
            query = query.filter(BankTransaction.reconciliation_session_id == session_id)
        if matched is not None:
            query = query.filter(BankTransaction.matched == (matched.lower() == 'true'))
        
        transactions = query.order_by(BankTransaction.transaction_date.desc()).all()
        
        return jsonify([{
            'id': tx.id,
            'bank_account_id': tx.bank_account_id,
            'bank_account_name': tx.bank_account.account_name,
            'transaction_date': tx.transaction_date.isoformat() if tx.transaction_date else None,
            'amount': tx.amount,
            'reference': tx.reference,
            'description': tx.description,
            'statement_date': tx.statement_date.isoformat() if tx.statement_date else None,
            'bank_reference': tx.bank_reference,
            'matched': tx.matched,
            'matched_transaction_id': tx.matched_transaction_id,
            'matched_transaction_type': tx.matched_transaction_type,
            'reconciled_by': tx.reconciled_by,
            'reconciled_at': tx.reconciled_at.isoformat() if tx.reconciled_at else None
        } for tx in transactions])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bank_reconciliation_bp.route('/bank-transactions', methods=['POST'])
@require_permission('finance.reconciliation.create')
def create_bank_transaction():
    """Create a bank transaction (import from statement)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['bank_account_id', 'transaction_date', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        transaction = BankTransaction(
            bank_account_id=data['bank_account_id'],
            transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d').date(),
            amount=float(data['amount']),
            reference=data.get('reference'),
            description=data.get('description'),
            statement_date=datetime.strptime(data['statement_date'], '%Y-%m-%d').date() if data.get('statement_date') else None,
            bank_reference=data.get('bank_reference'),
            reconciliation_session_id=data.get('reconciliation_session_id'),
            created_by=data.get('created_by', 'system')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'id': transaction.id,
            'message': 'Bank transaction created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Auto-Matching Logic
@bank_reconciliation_bp.route('/auto-match', methods=['POST'])
@require_permission('finance.reconciliation.update')
def auto_match_transactions():
    """Auto-match bank transactions with GL entries"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        bank_account_id = data.get('bank_account_id')
        
        if not session_id and not bank_account_id:
            return jsonify({'error': 'session_id or bank_account_id is required'}), 400
        
        # Get unmatched bank transactions
        query = BankTransaction.query.filter(BankTransaction.matched == False)
        if session_id:
            query = query.filter(BankTransaction.reconciliation_session_id == session_id)
        if bank_account_id:
            query = query.filter(BankTransaction.bank_account_id == bank_account_id)
        
        unmatched_transactions = query.all()
        
        # Get unreconciled GL entries
        gl_entries = get_unreconciled_gl_entries(bank_account_id)
        
        matches_found = 0
        
        for bank_tx in unmatched_transactions:
            # Try to find matching GL entry
            for gl_entry in gl_entries:
                # Match by amount and date proximity (within 3 days)
                amount_match = abs(bank_tx.amount - (gl_entry.debit_amount - gl_entry.credit_amount)) < 0.01
                date_diff = abs((bank_tx.transaction_date - gl_entry.entry_date).days)
                date_match = date_diff <= 3
                
                # Match by reference if available
                reference_match = False
                if bank_tx.reference and gl_entry.reference:
                    reference_match = bank_tx.reference.lower() in gl_entry.reference.lower() or \
                                    gl_entry.reference.lower() in bank_tx.reference.lower()
                
                # If amount and date match, or amount and reference match
                if amount_match and (date_match or reference_match):
                    # Mark as matched
                    bank_tx.matched = True
                    bank_tx.matched_transaction_id = gl_entry.id
                    bank_tx.matched_transaction_type = 'GL'
                    bank_tx.reconciled_by = data.get('reconciled_by', 'auto_match')
                    bank_tx.reconciled_at = datetime.utcnow()
                    
                    matches_found += 1
                    break
        
        db.session.commit()
        
        return jsonify({
            'message': f'Auto-matching completed. {matches_found} matches found.',
            'matches_found': matches_found
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Manual Matching
@bank_reconciliation_bp.route('/match-transaction', methods=['POST'])
@require_permission('finance.reconciliation.update')
def match_transaction():
    """Manually match a bank transaction with a GL entry"""
    try:
        data = request.get_json()
        
        bank_transaction_id = data.get('bank_transaction_id')
        gl_entry_id = data.get('gl_entry_id')
        transaction_type = data.get('transaction_type', 'GL')  # 'GL', 'AR', 'AP'
        
        if not bank_transaction_id or not gl_entry_id:
            return jsonify({'error': 'bank_transaction_id and gl_entry_id are required'}), 400
        
        # Get the bank transaction
        bank_tx = BankTransaction.query.get(bank_transaction_id)
        if not bank_tx:
            return jsonify({'error': 'Bank transaction not found'}), 404
        
        # Mark as matched
        bank_tx.matched = True
        bank_tx.matched_transaction_id = gl_entry_id
        bank_tx.matched_transaction_type = transaction_type
        bank_tx.reconciled_by = data.get('reconciled_by', 'manual')
        bank_tx.reconciled_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction matched successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get unreconciled GL entries for matching
@bank_reconciliation_bp.route('/unreconciled-gl-entries', methods=['GET'])
@require_permission('finance.reconciliation.read')
def get_unreconciled_gl_entries_api():
    """Get unreconciled GL entries for a bank account"""
    try:
        bank_account_id = request.args.get('bank_account_id')
        if not bank_account_id:
            return jsonify({'error': 'bank_account_id is required'}), 400
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert date strings to date objects
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        gl_entries = get_unreconciled_gl_entries(bank_account_id, start_date_obj, end_date_obj)
        
        return jsonify([{
            'id': entry.id,
            'entry_date': entry.entry_date.isoformat() if entry.entry_date else None,
            'reference': entry.reference,
            'description': entry.description,
            'debit_amount': entry.debit_amount,
            'credit_amount': entry.credit_amount,
            'balance': entry.balance,
            'status': entry.status,
            'account_id': entry.account_id,
            'account_name': entry.account.account_name if entry.account else None
        } for entry in gl_entries])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Complete reconciliation session
@bank_reconciliation_bp.route('/reconciliation-sessions/<int:session_id>/complete', methods=['POST'])
@require_permission('finance.reconciliation.update')
def complete_reconciliation_session(session_id):
    """Complete a reconciliation session"""
    try:
        session = ReconciliationSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Reconciliation session not found'}), 404
        
        if session.status == 'completed':
            return jsonify({'error': 'Session already completed'}), 400
        
        # Update session status
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        session.completed_by = request.json.get('completed_by', 'system')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reconciliation session completed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

