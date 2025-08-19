from flask import Blueprint, jsonify, request
from .models import Account, JournalEntry, JournalLine
from app import db
from datetime import datetime

bp = Blueprint('finance', __name__, url_prefix='/api/finance')

# Chart of Accounts endpoints
@bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all chart of accounts"""
    try:
        accounts = Account.query.all()
        return jsonify([{
            "id": acc.id,
            "code": acc.code,
            "name": acc.name,
            "type": acc.type,
            "parent_id": acc.parent_id,
            "is_active": acc.is_active,
            "created_at": acc.created_at.isoformat() if acc.created_at else None
        } for acc in accounts]), 200
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts"}), 500

@bp.route('/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    try:
        data = request.get_json()
        
        account = Account(
            code=data['code'],
            name=data['name'],
            type=data['type'],
            parent_id=data.get('parent_id'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            "id": account.id,
            "code": account.code,
            "name": account.name,
            "type": account.type,
            "parent_id": account.parent_id,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat() if account.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating account: {e}")
        return jsonify({"error": "Failed to create account"}), 500

@bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """Update an account"""
    try:
        account = Account.query.get_or_404(account_id)
        data = request.get_json()
        
        account.code = data.get('code', account.code)
        account.name = data.get('name', account.name)
        account.type = data.get('type', account.type)
        account.parent_id = data.get('parent_id', account.parent_id)
        account.is_active = data.get('is_active', account.is_active)
        
        db.session.commit()
        
        return jsonify({
            "id": account.id,
            "code": account.code,
            "name": account.name,
            "type": account.type,
            "parent_id": account.parent_id,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat() if account.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating account: {e}")
        return jsonify({"error": "Failed to update account"}), 500

@bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    try:
        account = Account.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()
        
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {e}")
        return jsonify({"error": "Failed to delete account"}), 500

# Journal Entry endpoints
@bp.route('/journal-entries', methods=['GET'])
def get_journal_entries():
    """Get all journal entries"""
    try:
        entries = JournalEntry.query.all()
        return jsonify([{
            "id": entry.id,
            "period": entry.period,
            "doc_date": entry.doc_date.isoformat() if entry.doc_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "status": entry.status,
            "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
            "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "lines": [{
                "id": line.id,
                "account_id": line.account_id,
                "debit_amount": float(line.debit_amount) if line.debit_amount else 0.0,
                "credit_amount": float(line.credit_amount) if line.credit_amount else 0.0,
                "description": line.description
            } for line in entry.lines]
        } for entry in entries]), 200
    except Exception as e:
        print(f"Error fetching journal entries: {e}")
        return jsonify({"error": "Failed to fetch journal entries"}), 500

@bp.route('/journal-entries', methods=['POST'])
def create_journal_entry():
    """Create a new journal entry"""
    try:
        data = request.get_json()
        
        entry = JournalEntry(
            period=data.get('period', datetime.utcnow().strftime('%Y-%m')),
            doc_date=datetime.fromisoformat(data['doc_date']) if data.get('doc_date') else datetime.utcnow().date(),
            reference=data.get('reference', f"JE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"),
            description=data.get('description', ''),
            status=data.get('status', 'draft'),
            total_debit=data.get('total_debit', 0.0),
            total_credit=data.get('total_credit', 0.0)
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # Add journal lines if provided
        if data.get('lines'):
            for line_data in data['lines']:
                line = JournalLine(
                    journal_entry_id=entry.id,
                    account_id=line_data['account_id'],
                    debit_amount=line_data.get('debit_amount', 0.0),
                    credit_amount=line_data.get('credit_amount', 0.0),
                    description=line_data.get('description')
                )
                db.session.add(line)
            
            db.session.commit()
        
        return jsonify({
            "id": entry.id,
            "period": entry.period,
            "doc_date": entry.doc_date.isoformat() if entry.doc_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "status": entry.status,
            "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
            "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
            "created_at": entry.created_at.isoformat() if entry.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating journal entry: {e}")
        return jsonify({"error": "Failed to create journal entry"}), 500

@bp.route('/journal-entries/<int:entry_id>', methods=['PUT'])
def update_journal_entry(entry_id):
    """Update a journal entry"""
    try:
        entry = JournalEntry.query.get_or_404(entry_id)
        data = request.get_json()
        
        if data.get('period'):
            entry.period = data['period']
        if data.get('doc_date'):
            entry.doc_date = datetime.fromisoformat(data['doc_date']).date()
        entry.reference = data.get('reference', entry.reference)
        entry.description = data.get('description', entry.description)
        entry.status = data.get('status', entry.status)
        entry.total_debit = data.get('total_debit', entry.total_debit)
        entry.total_credit = data.get('total_credit', entry.total_credit)
        
        db.session.commit()
        
        return jsonify({
            "id": entry.id,
            "period": entry.period,
            "doc_date": entry.doc_date.isoformat() if entry.doc_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "status": entry.status,
            "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
            "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
            "created_at": entry.created_at.isoformat() if entry.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating journal entry: {e}")
        return jsonify({"error": "Failed to update journal entry"}), 500

@bp.route('/journal-entries/<int:entry_id>', methods=['DELETE'])
def delete_journal_entry(entry_id):
    """Delete a journal entry"""
    try:
        entry = JournalEntry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({"message": "Journal entry deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting journal entry: {e}")
        return jsonify({"error": "Failed to delete journal entry"}), 500

# Journal Line endpoints
@bp.route('/journal-lines', methods=['GET'])
def get_journal_lines():
    """Get all journal lines"""
    try:
        lines = JournalLine.query.all()
        return jsonify([{
            "id": line.id,
            "journal_entry_id": line.journal_entry_id,
            "account_id": line.account_id,
            "debit_amount": line.debit_amount,
            "credit_amount": line.credit_amount,
            "description": line.description
        } for line in lines]), 200
    except Exception as e:
        print(f"Error fetching journal lines: {e}")
        return jsonify({"error": "Failed to fetch journal lines"}), 500

@bp.route('/journal-lines', methods=['POST'])
def create_journal_line():
    """Create a new journal line"""
    try:
        data = request.get_json()
        
        line = JournalLine(
            journal_entry_id=data['journal_entry_id'],
            account_id=data['account_id'],
            debit_amount=data.get('debit_amount', 0.0),
            credit_amount=data.get('credit_amount', 0.0),
            description=data.get('description')
        )
        
        db.session.add(line)
        db.session.commit()
        
        return jsonify({
            "id": line.id,
            "journal_entry_id": line.journal_entry_id,
            "account_id": line.account_id,
            "debit_amount": line.debit_amount,
            "credit_amount": line.credit_amount,
            "description": line.description
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating journal line: {e}")
        return jsonify({"error": "Failed to create journal line"}), 500

@bp.route('/journal-lines/<int:line_id>', methods=['PUT'])
def update_journal_line(line_id):
    """Update a journal line"""
    try:
        line = JournalLine.query.get_or_404(line_id)
        data = request.get_json()
        
        line.journal_entry_id = data.get('journal_entry_id', line.journal_entry_id)
        line.account_id = data.get('account_id', line.account_id)
        line.debit_amount = data.get('debit_amount', line.debit_amount)
        line.credit_amount = data.get('credit_amount', line.credit_amount)
        line.description = data.get('description', line.description)
        
        db.session.commit()
        
        return jsonify({
            "id": line.id,
            "journal_entry_id": line.journal_entry_id,
            "account_id": line.account_id,
            "debit_amount": line.debit_amount,
            "credit_amount": line.credit_amount,
            "description": line.description
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating journal line: {e}")
        return jsonify({"error": "Failed to update journal line"}), 500

@bp.route('/journal-lines/<int:line_id>', methods=['DELETE'])
def delete_journal_line(line_id):
    """Delete a journal line"""
    try:
        line = JournalLine.query.get_or_404(line_id)
        db.session.delete(line)
        db.session.commit()
        
        return jsonify({"message": "Journal line deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting journal line: {e}")
        return jsonify({"error": "Failed to delete journal line"}), 500