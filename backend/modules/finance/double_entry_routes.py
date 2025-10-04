"""
Double-Entry Accounting API Routes
=================================

This module provides proper double-entry accounting API endpoints that work with
JournalLines instead of the old total_debit/total_credit approach.

Phase 1: Foundation - Basic double-entry operations
"""

from flask import Blueprint, request, jsonify
from app import db
from modules.finance.models import JournalEntry, JournalLine, Account
from modules.finance.accounting_periods import period_manager
from modules.finance.multi_currency_journal_service import multi_currency_service
from datetime import datetime, date
from sqlalchemy import func

# Create blueprint
double_entry_bp = Blueprint('double_entry', __name__, url_prefix='/api/finance/double-entry')

@double_entry_bp.route('/journal-entries', methods=['GET'])
def get_journal_entries():
    """Get all journal entries with their lines"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        user_id_int = int(user_id)
        
        # Get journal entries for this user
        entries = JournalEntry.query.filter(
            (JournalEntry.user_id == user_id_int) | (JournalEntry.user_id.is_(None))
        ).order_by(JournalEntry.doc_date.desc()).all()
        
        result = []
        for entry in entries:
            # Get journal lines for this entry
            lines = JournalLine.query.filter_by(journal_entry_id=entry.id).all()
            
            # Calculate totals from lines
            total_debits = sum(line.debit_amount for line in lines)
            total_credits = sum(line.credit_amount for line in lines)
            
            entry_data = {
                "id": entry.id,
                "date": entry.doc_date.isoformat() if entry.doc_date else None,
                "reference": entry.reference,
                "description": entry.description,
                "status": entry.status,
                "payment_method": entry.payment_method,
                "total_debits": float(total_debits),
                "total_credits": float(total_credits),
                "is_balanced": abs(total_debits - total_credits) < 0.01,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "lines": []
            }
            
            # Add journal lines
            for line in lines:
                account = Account.query.get(line.account_id)
                line_data = {
                    "id": line.id,
                    "account_id": line.account_id,
                    "account_name": account.name if account else "Unknown Account",
                    "account_code": account.code if account else "N/A",
                    "description": line.description,
                    "debit_amount": float(line.debit_amount),
                    "credit_amount": float(line.credit_amount)
                }
                entry_data["lines"].append(line_data)
            
            result.append(entry_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error getting journal entries: {e}")
        return jsonify({"error": "Failed to get journal entries"}), 500

@double_entry_bp.route('/journal-entries', methods=['POST'])
def create_journal_entry():
    """Create a new journal entry with proper double-entry validation"""
    try:
        data = request.get_json()
        user_id = request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        user_id_int = int(user_id)
        
        # Validate required fields
        if not data.get('description'):
            return jsonify({"error": "Description is required"}), 400
        
        if not data.get('lines') or len(data['lines']) < 2:
            return jsonify({"error": "At least 2 journal lines are required"}), 400
        
        # Validate journal lines
        lines_data = []
        
        for line_data in data['lines']:
            if not line_data.get('account_id'):
                return jsonify({"error": "Account ID is required for all lines"}), 400
            
            debit = float(line_data.get('debit_amount', 0))
            credit = float(line_data.get('credit_amount', 0))
            
            if debit < 0 or credit < 0:
                return jsonify({"error": "Debit and credit amounts must be non-negative"}), 400
            
            if debit > 0 and credit > 0:
                return jsonify({"error": "A line cannot have both debit and credit amounts"}), 400
            
            if debit == 0 and credit == 0:
                return jsonify({"error": "Each line must have either a debit or credit amount"}), 400
            
            lines_data.append({
                'account_id': line_data['account_id'],
                'description': line_data.get('description', ''),
                'debit_amount': debit,
                'credit_amount': credit,
                'currency': line_data.get('currency'),  # Include currency if provided
                'cost_center_id': line_data.get('cost_center_id'),  # Include cost center if provided
                'department_id': line_data.get('department_id'),  # Include department if provided
                'project_id': line_data.get('project_id')  # Include project if provided
            })
        
        # Create a temporary journal entry for multi-currency processing
        entry_currency = data.get('currency', 'USD')
        temp_entry = JournalEntry(
            currency=entry_currency,
            doc_date=datetime.fromisoformat(data.get('date', datetime.now().isoformat())).date()
        )
        
        # Process multi-currency and validate balance in functional currency
        currency_result = multi_currency_service.process_journal_entry_currency(temp_entry, lines_data)
        
        if not currency_result['success']:
            return jsonify({
                "error": "Multi-currency processing failed",
                "details": currency_result['error']
            }), 400
        
        # Validate double-entry balance in functional currency
        if not currency_result['is_balanced']:
            return jsonify({
                "error": "Double-entry validation failed",
                "details": f"Total debits (${currency_result['total_functional_debits']:.2f}) must equal total credits (${currency_result['total_functional_credits']:.2f}) in base currency ({currency_result['base_currency']})",
                "total_debits": currency_result['total_functional_debits'],
                "total_credits": currency_result['total_functional_credits'],
                "difference": abs(currency_result['total_functional_debits'] - currency_result['total_functional_credits']),
                "base_currency": currency_result['base_currency']
            }), 400
        
        # Create journal entry
        entry_date = datetime.fromisoformat(data.get('date', datetime.now().isoformat())).date()
        reference = data.get('reference', f"JE-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Validate accounting period
        is_valid, message, period = period_manager.validate_transaction_date(entry_date, user_id_int)
        if not is_valid:
            return jsonify({
                "error": "Accounting period validation failed",
                "details": message,
                "transaction_date": entry_date.isoformat()
            }), 400
        
        # Check if entry is backdated
        is_backdated = entry_date < date.today()
        backdate_reason = data.get('backdate_reason') if is_backdated else None
        
        # Calculate totals from processed lines
        total_debits = sum(line['functional_debit_amount'] for line in currency_result['processed_lines'])
        total_credits = sum(line['functional_credit_amount'] for line in currency_result['processed_lines'])
        
        journal_entry = JournalEntry(
            period=entry_date.strftime('%Y-%m'),
            doc_date=entry_date,
            reference=reference,
            description=data['description'],
            status=data.get('status', 'draft'),
            payment_method=data.get('payment_method', 'bank'),
            currency=data.get('currency', 'USD'),  # Add currency to journal entry
            total_debit=total_debits,
            total_credit=total_credits,
            accounting_period_id=period.id,
            is_backdated=is_backdated,
            backdate_reason=backdate_reason,
            user_id=user_id_int,
            created_by=user_id_int
        )
        
        db.session.add(journal_entry)
        db.session.flush()  # Get the ID
        
        # Create journal lines with multi-currency data (already processed above)
        for line_data in currency_result['processed_lines']:
            journal_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=line_data['account_id'],
                description=line_data['description'],
                debit_amount=line_data['debit_amount'],
                credit_amount=line_data['credit_amount'],
                currency=line_data['currency'],
                exchange_rate=line_data['exchange_rate'],
                functional_debit_amount=line_data['functional_debit_amount'],
                functional_credit_amount=line_data['functional_credit_amount'],
                cost_center_id=line_data.get('cost_center_id'),
                department_id=line_data.get('department_id'),
                project_id=line_data.get('project_id')
            )
            db.session.add(journal_line)
        
        db.session.commit()
        
        return jsonify({
            "message": "Journal entry created successfully",
            "entry_id": journal_entry.id,
            "reference": journal_entry.reference,
            "total_debits": total_debits,
            "total_credits": total_credits,
            "currency": journal_entry.currency,
            "base_currency": currency_result['base_currency'],
            "total_functional_debits": currency_result['total_functional_debits'],
            "total_functional_credits": currency_result['total_functional_credits'],
            "is_balanced": currency_result['is_balanced']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating journal entry: {e}")
        return jsonify({"error": "Failed to create journal entry"}), 500

@double_entry_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get chart of accounts"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        user_id_int = int(user_id)
        
        accounts = Account.query.filter(
            (Account.user_id == user_id_int) | (Account.user_id.is_(None))
        ).order_by(Account.code).all()
        
        result = []
        for account in accounts:
            # Calculate balance from journal lines for this user
            from sqlalchemy import func
            balance_result = db.session.query(
                func.coalesce(func.sum(JournalLine.debit_amount), 0) - 
                func.coalesce(func.sum(JournalLine.credit_amount), 0)
            ).join(JournalEntry).filter(
                JournalLine.account_id == account.id,
                (JournalEntry.user_id == user_id_int) | (JournalEntry.user_id.is_(None))
            ).scalar() or 0.0
            
            account_data = {
                "id": account.id,
                "code": account.code,
                "name": account.name,
                "type": account.type,
                "balance": float(balance_result),
                "is_active": account.is_active
            }
            result.append(account_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error getting accounts: {e}")
        return jsonify({"error": "Failed to get accounts"}), 500

@double_entry_bp.route('/trial-balance', methods=['GET'])
def get_trial_balance():
    """Get trial balance report"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        user_id_int = int(user_id)
        
        # Get all accounts for this user
        accounts = Account.query.filter(
            (Account.user_id == user_id_int) | (Account.user_id.is_(None))
        ).all()
        
        trial_balance = []
        total_debits = 0
        total_credits = 0
        
        for account in accounts:
            # Calculate account balance from journal lines
            debit_total = db.session.query(func.sum(JournalLine.debit_amount)).join(JournalEntry).filter(
                JournalLine.account_id == account.id,
                (JournalEntry.user_id == user_id_int) | (JournalEntry.user_id.is_(None))
            ).scalar() or 0
            
            credit_total = db.session.query(func.sum(JournalLine.credit_amount)).join(JournalEntry).filter(
                JournalLine.account_id == account.id,
                (JournalEntry.user_id == user_id_int) | (JournalEntry.user_id.is_(None))
            ).scalar() or 0
            
            # Determine normal balance
            if account.type in ['asset', 'expense']:
                # Normal debit balance
                balance = debit_total - credit_total
                normal_side = 'debit'
            else:
                # Normal credit balance (liability, equity, revenue)
                balance = credit_total - debit_total
                normal_side = 'credit'
            
            if abs(balance) > 0.01:  # Only include accounts with balances
                # For trial balance, we show the actual debit/credit amounts, not the balance
                debit_balance = float(debit_total) if debit_total > 0 else 0.0
                credit_balance = float(credit_total) if credit_total > 0 else 0.0
                
                trial_balance.append({
                    "account_code": account.code,
                    "account_name": account.name,
                    "account_type": account.type,
                    "debit_balance": debit_balance,
                    "credit_balance": credit_balance,
                    "normal_side": normal_side
                })
                
                # Add to totals
                total_debits += debit_total
                total_credits += credit_total
        
        return jsonify({
            "trial_balance": trial_balance,
            "total_debits": float(total_debits),
            "total_credits": float(total_credits),
            "is_balanced": abs(total_debits - total_credits) < 0.01,
            "difference": float(abs(total_debits - total_credits))
        }), 200
        
    except Exception as e:
        print(f"Error getting trial balance: {e}")
        return jsonify({"error": "Failed to get trial balance"}), 500

@double_entry_bp.route('/journal-entries/<int:entry_id>/currency-summary', methods=['GET'])
def get_journal_entry_currency_summary(entry_id):
    """Get currency summary for a journal entry"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        user_id_int = int(user_id)
        
        # Verify entry belongs to user
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id_int).first()
        if not entry:
            return jsonify({"error": "Journal entry not found"}), 404
        
        # Get currency summary
        summary = multi_currency_service.get_currency_summary(entry_id)
        
        if 'error' in summary:
            return jsonify({"error": summary['error']}), 500
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get currency summary: {str(e)}"}), 500

@double_entry_bp.route('/validate-multi-currency', methods=['POST'])
def validate_multi_currency_entry():
    """Validate multi-currency journal entry"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        lines_data = data.get('lines', [])
        entry_currency = data.get('currency', 'USD')
        
        if not lines_data:
            return jsonify({"error": "Journal lines are required"}), 400
        
        # Validate multi-currency entry
        validation_result = multi_currency_service.validate_multi_currency_entry(lines_data, entry_currency)
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to validate multi-currency entry: {str(e)}"}), 500

@double_entry_bp.route('/convert-currency', methods=['POST'])
def convert_currency():
    """Convert amount between currencies"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        amount = float(data.get('amount', 0))
        from_currency = data.get('from_currency', 'USD')
        to_currency = data.get('to_currency', 'USD')
        rate_date = data.get('rate_date')
        
        if rate_date:
            from datetime import datetime
            rate_date = datetime.fromisoformat(rate_date).date()
        
        # Convert currency
        conversion_result = multi_currency_service.convert_amount(amount, from_currency, to_currency, rate_date)
        
        return jsonify(conversion_result), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to convert currency: {str(e)}"}), 500