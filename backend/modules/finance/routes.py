# Finance routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.finance.models import Account, JournalEntry, JournalLine
from modules.core.permissions import require_permission
from datetime import datetime

finance_bp = Blueprint('finance', __name__)
@finance_bp.route('/fx/revaluation/preview', methods=['GET', 'OPTIONS'])
@require_permission('finance.reports.read')
def fx_revaluation_preview():
    if request.method == 'OPTIONS':
        return ('', 200)
    """Preview FX revaluation for AR/AP open items and cash as of a date.
    Query: as_of=YYYY-MM-DD, base=USD
    Returns: summary only (no postings) for audit-safe planning.
    """
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
        
        # Get base currency from database settings
        from sqlalchemy import text
        import json
        base_currency = None
        try:
            result = db.session.execute(
                text("SELECT data FROM system_settings WHERE section = 'currency'")
            ).fetchone()
            if result and result[0]:
                data = result[0]
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except:
                        data = {}
                if isinstance(data, dict) and 'base_currency' in data:
                    base_currency = data['base_currency']
        except:
            pass
        
        # If still no user_id, return empty summary (for development)
        if not user_id:
            print("Warning: No user context found for FX revaluation, returning empty results")
            return jsonify({
                'as_of': datetime.utcnow().date().isoformat(),
                'base_currency': base_currency or None,
                'ar_unrealized_gl': 0.0,
                'ap_unrealized_gl': 0.0,
                'cash_unrealized_gl': 0.0,
                'by_currency': []
            }), 200
        
        as_of = request.args.get('as_of') or datetime.utcnow().date().isoformat()
        base = request.args.get('base') or base_currency
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
@require_permission('finance.accounts.read')
def get_accounts():
    """Get accounts for the current user only"""
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
        
        # SECURITY: Convert user_id to int and validate (prevent injection)
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        accounts = Account.query.filter_by(user_id=user_id).all()
        
        return jsonify([{
            "id": acc.id,
            "code": acc.code,
            "name": acc.name,
            "type": acc.type,
            "balance": float(acc.balance) if acc.balance else 0.0,
            "parent_id": acc.parent_id,
            "is_active": acc.is_active,
            "user_id": acc.user_id,
            "created_at": acc.created_at.isoformat() if acc.created_at else None
        } for acc in accounts]), 200
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts"}), 500

@finance_bp.route('/journal-entries', methods=['GET'])
@require_permission('finance.journal.read')
def get_journal_entries():
    """Get journal entries for the current user only"""
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
        
        # SECURITY: Convert user_id to int and validate (prevent injection)
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        entries = JournalEntry.query.filter_by(user_id=user_id).all()
        
        return jsonify([{
            "id": entry.id,
            "entry_date": entry.doc_date.isoformat() if entry.doc_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "status": entry.status,
            "payment_method": entry.payment_method,
            "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
            "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "user_id": entry.user_id
        } for entry in entries]), 200
    except Exception as e:
        print(f"Error fetching journal entries: {e}")
        return jsonify({"error": "Failed to fetch journal entries"}), 500

@finance_bp.route('/accounts', methods=['POST'])
@require_permission('finance.accounts.create')
def create_account():
    """Create a new account in database"""
    try:
        data = request.get_json()
        
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return error
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        new_account = Account(
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            balance=data.get('balance', 0),
            parent_id=data.get('parent_id'),
            is_active=data.get('is_active', True),
            user_id=user_id  # Associate with current user
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
@require_permission('finance.accounts.update')
def update_account(account_id):
    """Update an account in database"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return error
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        # Get account and check ownership
        account = Account.query.get_or_404(account_id)
        
        # Ensure user can only update their own accounts (or accounts with no user_id for backward compatibility)
        if account.user_id is not None and account.user_id != int(user_id):
            return jsonify({"error": "Access denied: You can only update your own accounts"}), 403
        
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
@require_permission('finance.accounts.delete')
def delete_account(account_id):
    """Delete an account from database"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return error
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        # Get account and check ownership
        account = Account.query.get_or_404(account_id)
        
        # Ensure user can only delete their own accounts (or accounts with no user_id for backward compatibility)
        if account.user_id is not None and account.user_id != int(user_id):
            return jsonify({"error": "Access denied: You can only delete your own accounts"}), 403
        
        db.session.delete(account)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {e}")
        return jsonify({"error": "Failed to delete account"}), 500

@finance_bp.route('/journal-entries', methods=['POST'])
@require_permission('finance.journal.create')
def create_journal_entry():
    """Create a new journal entry in database with double-entry validation"""
    try:
        data = request.get_json()
        
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return error
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        # CRITICAL: Validate double-entry balance
        total_debit = float(data.get('total_debit', 0))
        total_credit = float(data.get('total_credit', 0))
        
        # Check if debits equal credits (fundamental double-entry rule)
        if abs(total_debit - total_credit) > 0.01:  # Allow for small rounding differences
            return jsonify({
                "error": "Double-entry validation failed",
                "details": f"Debits (${total_debit:.2f}) must equal credits (${total_credit:.2f}). Difference: ${abs(total_debit - total_credit):.2f}",
                "total_debit": total_debit,
                "total_credit": total_credit,
                "difference": abs(total_debit - total_credit)
            }), 400
        
        # Check that at least one amount is greater than zero
        if total_debit == 0 and total_credit == 0:
            return jsonify({
                "error": "Invalid journal entry",
                "details": "Journal entry must have at least one non-zero debit or credit amount"
            }), 400
        
        # Validate payment method
        valid_payment_methods = ['cash', 'bank', 'wire', 'credit_card', 'check', 'digital']
        payment_method = data.get('payment_method', 'bank')
        if payment_method not in valid_payment_methods:
            return jsonify({
                "error": "Invalid payment method",
                "details": f"Payment method must be one of: {', '.join(valid_payment_methods)}",
                "valid_methods": valid_payment_methods
            }), 400
        
        # Generate unique reference if empty or not provided
        reference = data.get('reference', '').strip()
        if not reference:
            reference = f"JE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{datetime.utcnow().microsecond}"
        
        new_entry = JournalEntry(
            period=datetime.fromisoformat(data.get('entry_date')).strftime('%Y-%m') if data.get('entry_date') else datetime.utcnow().strftime('%Y-%m'),
            doc_date=datetime.fromisoformat(data.get('entry_date')) if data.get('entry_date') else datetime.utcnow(),
            reference=reference,
            description=data.get('description'),
            status=data.get('status', 'draft'),
            payment_method=payment_method,
            total_debit=total_debit,
            total_credit=total_credit,
            user_id=user_id  # Associate with current user
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({
            "message": "Journal entry created successfully", 
            "entry": {
                "id": new_entry.id,
                "entry_date": new_entry.doc_date.isoformat() if new_entry.doc_date else None,
                "reference": new_entry.reference,
                "description": new_entry.description,
                "status": new_entry.status,
                "payment_method": new_entry.payment_method,
                "total_debit": float(new_entry.total_debit) if new_entry.total_debit else 0.0,
                "total_credit": float(new_entry.total_credit) if new_entry.total_credit else 0.0,
                "created_at": new_entry.created_at.isoformat() if new_entry.created_at else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating journal entry: {e}")
        return jsonify({"error": "Failed to create journal entry"}), 500

@finance_bp.route('/journal-entries/<int:entry_id>', methods=['PUT'])
@require_permission('finance.journal.update')
def update_journal_entry(entry_id):
    """Update a journal entry in database"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return error
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        # Get entry and check ownership
        entry = JournalEntry.query.get_or_404(entry_id)
        
        # Ensure user can only update their own entries (or entries with no user_id for backward compatibility)
        if entry.user_id is not None and entry.user_id != int(user_id):
            return jsonify({"error": "Access denied: You can only update your own entries"}), 403
        
        data = request.get_json()
        
        # CRITICAL: Validate double-entry balance if amounts are being updated
        if 'total_debit' in data or 'total_credit' in data:
            total_debit = float(data.get('total_debit', entry.total_debit))
            total_credit = float(data.get('total_credit', entry.total_credit))
            
            # Check if debits equal credits (fundamental double-entry rule)
            if abs(total_debit - total_credit) > 0.01:  # Allow for small rounding differences
                return jsonify({
                    "error": "Double-entry validation failed",
                    "details": f"Debits (${total_debit:.2f}) must equal credits (${total_credit:.2f}). Difference: ${abs(total_debit - total_credit):.2f}",
                    "total_debit": total_debit,
                    "total_credit": total_credit,
                    "difference": abs(total_debit - total_credit)
                }), 400
            
            # Check that at least one amount is greater than zero
            if total_debit == 0 and total_credit == 0:
                return jsonify({
                    "error": "Invalid journal entry",
                    "details": "Journal entry must have at least one non-zero debit or credit amount"
                }), 400
        
        # Validate payment method if being updated
        if 'payment_method' in data:
            valid_payment_methods = ['cash', 'bank', 'wire', 'credit_card', 'check', 'digital']
            payment_method = data.get('payment_method')
            if payment_method not in valid_payment_methods:
                return jsonify({
                    "error": "Invalid payment method",
                    "details": f"Payment method must be one of: {', '.join(valid_payment_methods)}",
                    "valid_methods": valid_payment_methods
                }), 400
        
        if data.get('entry_date'):
            entry.doc_date = datetime.fromisoformat(data.get('entry_date'))
            entry.period = datetime.fromisoformat(data.get('entry_date')).strftime('%Y-%m')
        
        # Handle reference update - generate unique if empty
        if 'reference' in data:
            reference = data.get('reference', '').strip()
            if not reference:
                reference = f"JE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{datetime.utcnow().microsecond}"
            entry.reference = reference
        
        entry.description = data.get('description', entry.description)
        entry.status = data.get('status', entry.status)
        entry.payment_method = data.get('payment_method', entry.payment_method)
        entry.total_debit = data.get('total_debit', entry.total_debit)
        entry.total_credit = data.get('total_credit', entry.total_credit)
        
        db.session.commit()
        return jsonify({
            "message": "Journal entry updated successfully",
            "entry": {
                "id": entry.id,
                "entry_date": entry.doc_date.isoformat() if entry.doc_date else None,
                "reference": entry.reference,
                "description": entry.description,
                "status": entry.status,
                "payment_method": entry.payment_method,
                "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
                "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating journal entry: {e}")
        return jsonify({"error": "Failed to update journal entry"}), 500

@finance_bp.route('/journal-entries/<int:entry_id>', methods=['DELETE'])
@require_permission('finance.journal.delete')
def delete_journal_entry(entry_id):
    """Delete a journal entry from database"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return error
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        # Get entry and check ownership
        entry = JournalEntry.query.get_or_404(entry_id)
        
        # Ensure user can only delete their own entries (or entries with no user_id for backward compatibility)
        if entry.user_id is not None and entry.user_id != int(user_id):
            return jsonify({"error": "Access denied: You can only delete your own entries"}), 403
        
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message": "Journal entry deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting journal entry: {e}")
        return jsonify({"error": "Failed to delete journal entry"}), 500

