# Finance routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.finance.models import Account, JournalEntry, JournalLine
from datetime import datetime

finance_bp = Blueprint('finance', __name__)
@finance_bp.route('/fx/revaluation/preview', methods=['GET', 'OPTIONS'])
def fx_revaluation_preview():
    if request.method == 'OPTIONS':
        return ('', 200)
    """Preview FX revaluation for AR/AP open items and cash as of a date.
    Query: as_of=YYYY-MM-DD, base=USD
    Returns: summary only (no postings) for audit-safe planning.
    """
    try:
        as_of = request.args.get('as_of') or datetime.utcnow().date().isoformat()
        base = request.args.get('base') or 'USD'
        # Placeholder summary; real impl would query AR/AP/cash balances by currency
        summary = {
            'as_of': as_of,
            'base_currency': base,
            'ar_unrealized_gl': 0.0,
            'ap_unrealized_gl': 0.0,
            'cash_unrealized_gl': 0.0,
            'by_currency': []
        }
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@finance_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts from database"""
    try:
        accounts = Account.query.all()
        return jsonify([{
            "id": acc.id,
            "code": acc.code,
            "name": acc.name,
            "type": acc.type,
            "balance": float(acc.balance) if acc.balance else 0.0,
            "parent_id": acc.parent_id,
            "is_active": acc.is_active,
            "created_at": acc.created_at.isoformat() if acc.created_at else None
        } for acc in accounts]), 200
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts"}), 500

@finance_bp.route('/journal-entries', methods=['GET'])
def get_journal_entries():
    """Get all journal entries from database"""
    try:
        entries = JournalEntry.query.all()
        return jsonify([{
            "id": entry.id,
            "entry_date": entry.doc_date.isoformat() if entry.doc_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "status": entry.status,
            "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
            "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
            "created_at": entry.created_at.isoformat() if entry.created_at else None
        } for entry in entries]), 200
    except Exception as e:
        print(f"Error fetching journal entries: {e}")
        return jsonify({"error": "Failed to fetch journal entries"}), 500

@finance_bp.route('/accounts', methods=['POST'])
def create_account():
    """Create a new account in database"""
    try:
        data = request.get_json()
        new_account = Account(
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            balance=data.get('balance', 0),
            parent_id=data.get('parent_id'),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_account)
        db.session.commit()
        return jsonify({
            "message": "Account created successfully", 
            "id": new_account.id,
            "account": {
                "id": new_account.id,
                "code": new_account.code,
                "name": new_account.name,
                "type": new_account.type,
                "balance": float(new_account.balance) if new_account.balance else 0.0,
                "is_active": new_account.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating account: {e}")
        return jsonify({"error": "Failed to create account"}), 500

@finance_bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """Update an account in database"""
    try:
        account = Account.query.get_or_404(account_id)
        data = request.get_json()
        
        account.code = data.get('code', account.code)
        account.name = data.get('name', account.name)
        account.type = data.get('type', account.type)
        account.balance = data.get('balance', account.balance)
        account.parent_id = data.get('parent_id', account.parent_id)
        account.is_active = data.get('is_active', account.is_active)
        
        db.session.commit()
        return jsonify({
            "message": "Account updated successfully",
            "account": {
                "id": account.id,
                "code": account.code,
                "name": account.name,
                "type": account.type,
                "balance": float(account.balance) if account.balance else 0.0,
                "is_active": account.is_active
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating account: {e}")
        return jsonify({"error": "Failed to update account"}), 500

@finance_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account from database"""
    try:
        account = Account.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {e}")
        return jsonify({"error": "Failed to delete account"}), 500

@finance_bp.route('/journal-entries', methods=['POST'])
def create_journal_entry():
    """Create a new journal entry in database"""
    try:
        data = request.get_json()
        new_entry = JournalEntry(
            entry_date=datetime.fromisoformat(data.get('entry_date')) if data.get('entry_date') else datetime.utcnow(),
            reference=data.get('reference'),
            description=data.get('description'),
            status=data.get('status', 'draft'),
            total_debit=data.get('total_debit', 0),
            total_credit=data.get('total_credit', 0)
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({
            "message": "Journal entry created successfully", 
            "id": new_entry.id,
            "entry": {
                "id": new_entry.id,
                "reference": new_entry.reference,
                "description": new_entry.description,
                "status": new_entry.status,
                "total_debit": float(new_entry.total_debit) if new_entry.total_debit else 0.0,
                "total_credit": float(new_entry.total_credit) if new_entry.total_credit else 0.0
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating journal entry: {e}")
        return jsonify({"error": "Failed to create journal entry"}), 500

@finance_bp.route('/journal-entries/<int:entry_id>', methods=['PUT'])
def update_journal_entry(entry_id):
    """Update a journal entry in database"""
    try:
        entry = JournalEntry.query.get_or_404(entry_id)
        data = request.get_json()
        
        entry.entry_date = datetime.fromisoformat(data.get('entry_date')) if data.get('entry_date') else entry.entry_date
        entry.reference = data.get('reference', entry.reference)
        entry.description = data.get('description', entry.description)
        entry.status = data.get('status', entry.status)
        entry.total_debit = data.get('total_debit', entry.total_debit)
        entry.total_credit = data.get('total_credit', entry.total_credit)
        
        db.session.commit()
        return jsonify({
            "message": "Journal entry updated successfully",
            "entry": {
                "id": entry.id,
                "reference": entry.reference,
                "description": entry.description,
                "status": entry.status,
                "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
                "total_credit": float(entry.total_credit) if entry.total_credit else 0.0
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating journal entry: {e}")
        return jsonify({"error": "Failed to update journal entry"}), 500

@finance_bp.route('/journal-entries/<int:entry_id>', methods=['DELETE'])
def delete_journal_entry(entry_id):
    """Delete a journal entry from database"""
    try:
        entry = JournalEntry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message": "Journal entry deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting journal entry: {e}")
        return jsonify({"error": "Failed to delete journal entry"}), 500

