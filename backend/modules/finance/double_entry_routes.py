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
from modules.core.tenant_helpers import get_current_user_tenant_id, get_current_user_id
from modules.core.tenant_query_helper import tenant_query
from modules.core.permissions import require_permission
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

# Create blueprint
double_entry_bp = Blueprint('double_entry', __name__, url_prefix='/api/finance/double-entry')

# Test route to verify blueprint is working
@double_entry_bp.route('/test', methods=['GET', 'OPTIONS'])
def test_route():
    """Test route to verify blueprint registration"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID,X-Tenant-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        return response, 200
    return jsonify({"message": "Double-entry blueprint is working", "route": "/api/finance/double-entry/test"}), 200

# Handle CORS preflight for all routes in this blueprint
@double_entry_bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID,X-Tenant-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        return response, 200

@double_entry_bp.route('/journal-entries', methods=['GET'])
@require_permission('finance.journal.read')
def get_journal_entries():
    """Get all journal entries with their lines - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id from current user
        from modules.core.tenant_helpers import get_current_user_tenant_id
        tenant_id = get_current_user_tenant_id()
        
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        # Get journal entries for this tenant (company-wide) - USING TENANT_QUERY for consistency
        entries = tenant_query(JournalEntry).order_by(JournalEntry.doc_date.desc()).all()
        
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
            
            # Add journal lines - SECURITY: Use tenant_query to ensure account belongs to tenant
            for line in lines:
                # SECURITY FIX: Use tenant_query instead of Account.query.get() to prevent cross-tenant data access
                account = tenant_query(Account).filter_by(id=line.account_id).first()
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
@require_permission('finance.journal.create')
def create_journal_entry():
    """Create a new journal entry with proper double-entry validation - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('description'):
            return jsonify({"error": "Description is required"}), 400
        
        if not data.get('lines') or len(data['lines']) < 2:
            return jsonify({"error": "At least 2 journal lines are required"}), 400
        
        # Validate journal lines
        lines_data = []
        inactive_accounts = []
        
        for line_data in data['lines']:
            if not line_data.get('account_id'):
                return jsonify({"error": "Account ID is required for all lines"}), 400
            
            # Validate that account exists and is active - TENANT-CENTRIC
            account_id = line_data['account_id']
            account = tenant_query(Account).filter_by(id=account_id).first()
            
            if not account:
                return jsonify({
                    "error": f"Account with ID {account_id} not found or does not belong to your company"
                }), 400
            
            if account.is_active == False:
                inactive_accounts.append({
                    "account_id": account_id,
                    "account_code": account.code,
                    "account_name": account.name
                })
            
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
        
        # Block journal entry if any inactive accounts are used
        if inactive_accounts:
            account_list = ", ".join([f"{acc['account_code']} ({acc['account_name']})" for acc in inactive_accounts])
            return jsonify({
                "error": "Cannot use inactive accounts in journal entries",
                "details": f"The following accounts are inactive and cannot be used: {account_list}",
                "inactive_accounts": inactive_accounts
            }), 400
        
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
        
        # Validate accounting period - TENANT-CENTRIC (pass tenant_id instead of user_id)
        is_valid, message, period = period_manager.validate_transaction_date(entry_date, tenant_id)
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
            tenant_id=tenant_id,  # TENANT-CENTRIC: Store tenant_id
            created_by=user_id_int  # Audit trail: who created it
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

@double_entry_bp.route('/accounts', methods=['GET', 'OPTIONS'])
@require_permission('finance.accounts.read')
def get_accounts():
    """Get chart of accounts"""
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID,X-Tenant-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS")
        return response, 200
    
    try:
        # TENANT-CENTRIC: Get tenant_id from current user
        tenant_id = get_current_user_tenant_id()
        
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        # TENANT-CENTRIC: Automatic tenant filtering
        accounts = tenant_query(Account).order_by(Account.code).all()
        
        # Default account codes (for marking)
        # Core accounts (12) - these get the "Default" badge
        core_codes = {'1000', '1100', '1200', '1300', '2000', '2100', '3000', '3100', '4000', '4100', '5000', '6000'}
        # All default account codes (25 total)
        default_codes = {
            # Assets (6)
            '1000', '1100', '1200', '1300', '1400', '1500',
            # Liabilities (4)
            '2000', '2100', '2200', '2300',
            # Equity (3)
            '3000', '3100', '3200',
            # Revenue (2)
            '4000', '4100',
            # Expenses (10)
            '5000', '6000', '6100', '6200', '6300', '6400', '6500', '6600', '6700', '6800'
        }
        
        result = []
        for account in accounts:
            # Calculate balance from journal lines for this tenant (company-wide)
            from sqlalchemy import func
            balance_result = db.session.query(
                func.coalesce(func.sum(JournalLine.debit_amount), 0) - 
                func.coalesce(func.sum(JournalLine.credit_amount), 0)
            ).join(JournalEntry).filter(
                JournalLine.account_id == account.id,
                JournalEntry.tenant_id == tenant_id  # TENANT-CENTRIC: Company-wide balance
            ).scalar() or 0.0
            
            account_data = {
                "id": account.id,
                "code": account.code,
                "name": account.name,
                "type": account.type,
                "balance": float(balance_result),
                "is_active": account.is_active,
                "is_default": account.code in default_codes,  # Mark all 25 default accounts
                "is_core": account.code in core_codes  # Mark 12 core accounts for special highlighting
            }
            result.append(account_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error getting accounts: {e}")
        return jsonify({"error": "Failed to get accounts"}), 500

@double_entry_bp.route('/accounts/default/preview', methods=['GET'])
@require_permission('finance.accounts.read')

def get_default_accounts_preview():
    """Get preview of default accounts (for onboarding)"""
    try:
        from .default_accounts_service import get_default_accounts_preview
        preview = get_default_accounts_preview()
        return jsonify(preview), 200
    except Exception as e:
        print(f"Error getting default accounts preview: {e}")
        return jsonify({"error": "Failed to get default accounts preview"}), 500

@double_entry_bp.route('/accounts/default/create', methods=['POST'])
@jwt_required()
def create_default_accounts():
    """Create default accounts for the authenticated tenant (company) - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id from JWT
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({"error": "User authentication required"}), 401
        
        try:
            user_id_int = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid user ID in token"}), 400
        
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            # Fallback for development
            tenant_id = 'default'
        
        # Handle empty request body gracefully
        try:
            request_data = request.get_json(silent=True) or {}
            force = request_data.get('force', False)
        except Exception:
            force = False
        
        from .default_accounts_service import create_default_accounts, check_tenant_has_accounts
        
        # Check if tenant already has accounts - TENANT-CENTRIC
        if check_tenant_has_accounts(tenant_id) and not force:
            return jsonify({
                "message": "Company already has accounts",
                "has_accounts": True,
                "created": [],
                "skipped": [],
                "total": 0,
                "new_count": 0
            }), 200
        
        result = create_default_accounts(tenant_id, user_id_int, force=force)
        
        return jsonify({
            "message": f"Successfully created {result['new_count']} default accounts (12 core + 13 standard)",
            "has_accounts": True,
            **result
        }), 201
        
    except Exception as e:
        import traceback
        error_str = str(e).lower()
        
        # Handle duplicate key errors gracefully
        if 'duplicate key' in error_str or 'unique constraint' in error_str or 'uniqueviolation' in error_str:
            logger.warning(f"⚠️ Duplicate key error creating default accounts for tenant {tenant_id}: {e}")
            
            # Check what accounts already exist for this tenant
            from .models import Account
            existing_accounts = tenant_query(Account).all()
            
            return jsonify({
                "message": f"Some accounts already exist. Found {len(existing_accounts)} existing accounts.",
                "has_accounts": len(existing_accounts) > 0,
                "created": [],
                "skipped": [{'id': acc.id, 'code': acc.code, 'name': acc.name} for acc in existing_accounts],
                "total": len(existing_accounts),
                "new_count": 0
            }), 200  # Return 200 (OK) instead of error since accounts exist
        error_trace = traceback.format_exc()
        logger.error(f"Error creating default accounts: {e}\n{error_trace}")
        print(f"Error creating default accounts: {e}")
        print(error_trace)
        return jsonify({
            "error": f"Failed to create default accounts: {str(e)}",
            "details": str(e)
        }), 500

@double_entry_bp.route('/accounts/default/check', methods=['GET'])
@require_permission('finance.accounts.read')
def check_default_accounts():
    """Check if user has accounts"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        user_id_int = int(user_id)
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        from .default_accounts_service import check_tenant_has_accounts
        
        has_accounts = check_tenant_has_accounts(tenant_id)
        
        return jsonify({
            "has_accounts": has_accounts
        }), 200
        
    except Exception as e:
        print(f"Error checking accounts: {e}")
        return jsonify({"error": "Failed to check accounts"}), 500

@double_entry_bp.route('/accounts', methods=['POST'])
@require_permission('finance.accounts.create')
def create_account():
    """Create a new account - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Account name is required"}), 400
        if not data.get('type'):
            return jsonify({"error": "Account type is required"}), 400
        
        # Auto-generate code if not provided
        account_code = data.get('code')
        if not account_code:
            # Auto-suggest code based on account type - TENANT-CENTRIC
            account_code = suggest_account_code(data['type'], tenant_id)
        
        # Check if code already exists for this tenant - TENANT-CENTRIC
        existing = tenant_query(Account).filter_by(code=account_code).first()
        if existing:
            return jsonify({"error": f"Account code {account_code} already exists in your company"}), 400
        
        account = Account(
            code=account_code,
            name=data['name'],
            type=data['type'],
            balance=data.get('balance', 0.0),
            currency=data.get('currency', 'USD'),
            is_active=data.get('is_active', True),
            notes=data.get('notes'),
            tenant_id=tenant_id,  # TENANT-CENTRIC: Company-wide account
            created_by=user_id_int,  # Audit trail: who created it
            parent_id=data.get('parent_id')
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            "id": account.id,
            "code": account.code,
            "name": account.name,
            "type": account.type,
            "balance": account.balance,
            "is_active": account.is_active,
            "notes": account.notes,
            "is_default": False
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating account: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to create account: {str(e)}"}), 500

def suggest_account_code(account_type: str, user_id: int) -> str:
    """Auto-suggest account code based on account type"""
    # Type prefixes
    type_prefixes = {
        'asset': '1',
        'liability': '2',
        'equity': '3',
        'revenue': '4',
        'expense': '5'
    }
    
    prefix = type_prefixes.get(account_type.lower(), '9')
    
    # Get the highest code for this type and user
    existing_accounts = Account.query.filter(
        Account.user_id == user_id,
        Account.code.like(f'{prefix}%')
    ).order_by(Account.code.desc()).all()
    
    if existing_accounts:
        # Find next available code
        max_code = max([int(acc.code) for acc in existing_accounts if acc.code.isdigit()], default=int(f'{prefix}000'))
        next_code = max_code + 10  # Increment by 10 to leave room
    else:
        # Start with type prefix + 000
        next_code = int(f'{prefix}000')
    
    # Ensure code doesn't exceed 9999
    if next_code > 9999:
        next_code = int(f'{prefix}000') + 100
    
    return str(next_code)

@double_entry_bp.route('/trial-balance', methods=['GET'])
@require_permission('finance.reports.read')
def get_trial_balance():
    """Get trial balance report - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id
        tenant_id = get_current_user_tenant_id()
        
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        # Get all accounts for this tenant - TENANT-CENTRIC
        accounts = Account.query.filter(
            Account.tenant_id == tenant_id  # TENANT-CENTRIC
        ).all()
        
        trial_balance = []
        total_debits = 0
        total_credits = 0
        
        for account in accounts:
            # Calculate account balance from journal lines - TENANT-CENTRIC
            debit_total = db.session.query(func.sum(JournalLine.debit_amount)).join(JournalEntry).filter(
                JournalLine.account_id == account.id,
                JournalEntry.tenant_id == tenant_id  # TENANT-CENTRIC
            ).scalar() or 0
            
            credit_total = db.session.query(func.sum(JournalLine.credit_amount)).join(JournalEntry).filter(
                JournalLine.account_id == account.id,
                JournalEntry.tenant_id == tenant_id  # TENANT-CENTRIC
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
@require_permission('finance.journal.read')
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
@require_permission('finance.journal.create')

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
@require_permission('finance.journal.create')
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

@double_entry_bp.route('/accounts/<int:account_id>', methods=['PUT'])
@require_permission('finance.accounts.update')
def update_account(account_id):
    """Update an account - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id
        tenant_id = get_current_user_tenant_id()
        
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        data = request.get_json()
        
        # Get account and verify it belongs to tenant - TENANT-CENTRIC
        account = tenant_query(Account).filter_by(id=account_id).first()
        if not account:
            return jsonify({"error": "Account not found or access denied"}), 404
        
        # Update account fields
        if 'name' in data:
            account.name = data['name']
        if 'code' in data:
            # Check if new code already exists for this tenant - TENANT-CENTRIC
            existing = tenant_query(Account).filter_by(code=data['code']).first()
            if existing and existing.id != account_id:
                return jsonify({"error": f"Account code {data['code']} already exists in your company"}), 400
            account.code = data['code']
        if 'type' in data:
            account.type = data['type']
        if 'balance' in data:
            account.balance = data['balance']
        if 'currency' in data:
            account.currency = data['currency']
        if 'parent_id' in data:
                # Verify parent belongs to same tenant - TENANT-CENTRIC
            if data['parent_id']:
                parent = tenant_query(Account).filter_by(id=data['parent_id']).first()
                if not parent:
                    return jsonify({"error": "Parent account not found or access denied"}), 400
            account.parent_id = data['parent_id']
        if 'is_active' in data:
            account.is_active = data['is_active']
        if 'notes' in data:
            account.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            "id": account.id,
            "code": account.code,
            "name": account.name,
            "type": account.type,
            "balance": float(account.balance) if account.balance else 0.0,
            "is_active": account.is_active,
            "notes": account.notes,
            "message": "Account updated successfully"
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error updating account: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to update account: {str(e)}"}), 500

@double_entry_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@require_permission('finance.accounts.delete')
def delete_account(account_id):
    """Delete an account - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id
        tenant_id = get_current_user_tenant_id()
        
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        # Get account and verify it belongs to tenant - TENANT-CENTRIC
        account = tenant_query(Account).filter_by(id=account_id).first()
        if not account:
            return jsonify({"error": "Account not found or access denied"}), 404
        
        # Check if account has journal entries (prevent deletion of accounts with transactions) - TENANT-CENTRIC
        from sqlalchemy import func
        entry_count = db.session.query(func.count(JournalLine.id)).join(JournalEntry).filter(
            JournalLine.account_id == account_id,
            JournalEntry.tenant_id == tenant_id  # TENANT-CENTRIC
        ).scalar() or 0
        
        if entry_count > 0:
            return jsonify({
                "error": f"Cannot delete account with {entry_count} transaction(s). Deactivate it instead to preserve transaction history.",
                "entry_count": entry_count,
                "suggestion": "deactivate"
            }), 400
        
        # Check if account has non-zero balance (prevent deletion of accounts with balance)
        account_balance = float(account.balance) if account.balance else 0.0
        if abs(account_balance) > 0.01:  # Allow for floating point precision
            return jsonify({
                "error": f"Cannot delete account with balance of {account_balance:,.2f}. Transfer the balance to another account or deactivate it instead.",
                "balance": account_balance,
                "suggestion": "deactivate_or_transfer"
            }), 400
        
        # Check if account has children (sub-accounts) - TENANT-CENTRIC
        child_count = tenant_query(Account).filter_by(parent_id=account_id).count()
        if child_count > 0:
            return jsonify({
                "error": f"Cannot delete account with {child_count} sub-account(s). Remove or reassign sub-accounts first.",
                "child_count": child_count
            }), 400
        
        db.session.delete(account)
        db.session.commit()
        
        return jsonify({
            "message": "Account deleted successfully",
            "deleted_account_id": account_id
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete account: {str(e)}"}), 500

@double_entry_bp.route('/accounts/export', methods=['GET'])
@require_permission('finance.accounts.read')
def export_accounts():
    """Export accounts to CSV format"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        user_id_int = int(user_id)
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        # Get all accounts for tenant - automatic tenant filtering
        accounts = tenant_query(Account).order_by(Account.code).all()
        
        # Prepare CSV data
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Code', 'Name', 'Type', 'Balance', 'Currency', 'Parent Code', 'Active', 'Notes'])
        
        # Write account data
        for account in accounts:
            parent_code = None
            if account.parent_id:
                parent = tenant_query(Account).filter_by(id=account.parent_id).first()
                if parent:
                    parent_code = parent.code
            
            writer.writerow([
                account.code,
                account.name,
                account.type,
                account.balance or 0.0,
                account.currency or 'USD',
                parent_code or '',
                'Yes' if account.is_active else 'No',
                account.notes or ''
            ])
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=chart_of_accounts_{tenant_id}.csv'
            }
        )
        
    except Exception as e:
        print(f"Error exporting accounts: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to export accounts: {str(e)}"}), 500

@double_entry_bp.route('/accounts/import', methods=['POST'])
@require_permission('finance.accounts.create')
def import_accounts():
    """Import accounts from CSV format - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        import csv
        from io import StringIO
        
        # Read CSV file
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        created = []
        updated = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            try:
                code = row.get('Code', '').strip()
                name = row.get('Name', '').strip()
                account_type = row.get('Type', '').strip().lower()
                
                if not code or not name or not account_type:
                    errors.append({
                        "row": row_num,
                        "error": "Missing required fields: Code, Name, or Type"
                    })
                    continue
                
                # Validate account type
                valid_types = ['asset', 'liability', 'equity', 'revenue', 'expense']
                if account_type not in valid_types:
                    errors.append({
                        "row": row_num,
                        "error": f"Invalid account type: {account_type}. Must be one of: {', '.join(valid_types)}"
                    })
                    continue
                
                # Check if account exists - TENANT-CENTRIC
                existing = tenant_query(Account).filter_by(code=code).first()
                
                # Parse optional fields
                balance = float(row.get('Balance', 0) or 0)
                currency = row.get('Currency', 'USD').strip() or 'USD'
                is_active = row.get('Active', 'Yes').strip().lower() in ['yes', 'true', '1', 'active']
                notes = row.get('Notes', '').strip() or None
                
                # Handle parent code - TENANT-CENTRIC
                parent_id = None
                parent_code = row.get('Parent Code', '').strip()
                if parent_code:
                    parent = tenant_query(Account).filter_by(code=parent_code).first()
                    if parent:
                        parent_id = parent.id
                    else:
                        errors.append({
                            "row": row_num,
                            "error": f"Parent account with code '{parent_code}' not found"
                        })
                        continue
                
                if existing:
                    # Update existing account
                    existing.name = name
                    existing.type = account_type
                    existing.balance = balance
                    existing.currency = currency
                    existing.is_active = is_active
                    existing.parent_id = parent_id
                    if notes is not None:
                        existing.notes = notes
                    updated.append({"code": code, "name": name})
                else:
                    # Create new account - TENANT-CENTRIC
                    new_account = Account(
                        code=code,
                        name=name,
                        type=account_type,
                        balance=balance,
                        currency=currency,
                        is_active=is_active,
                        parent_id=parent_id,
                        notes=notes,
                        tenant_id=tenant_id,  # TENANT-CENTRIC
                        created_by=user_id_int  # Audit trail
                    )
                    db.session.add(new_account)
                    created.append({"code": code, "name": name})
                    
            except ValueError as e:
                errors.append({
                    "row": row_num,
                    "error": f"Invalid data format: {str(e)}"
                })
            except Exception as e:
                errors.append({
                    "row": row_num,
                    "error": f"Error processing row: {str(e)}"
                })
        
        db.session.commit()
        
        return jsonify({
            "message": f"Import completed: {len(created)} created, {len(updated)} updated, {len(errors)} errors",
            "created": created,
            "updated": updated,
            "errors": errors,
            "total_processed": len(created) + len(updated)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error importing accounts: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to import accounts: {str(e)}"}), 500

@double_entry_bp.route('/accounts/merge', methods=['POST'])
@require_permission('finance.accounts.update')
def merge_accounts():
    """Merge two accounts - transfer balance and transactions from source to target - TENANT-CENTRIC"""
    try:
        # TENANT-CENTRIC: Get tenant_id
        tenant_id = get_current_user_tenant_id()
        
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        data = request.get_json()
        
        source_account_id = data.get('source_account_id')
        target_account_id = data.get('target_account_id')
        
        if not source_account_id or not target_account_id:
            return jsonify({"error": "Both source_account_id and target_account_id are required"}), 400
        
        if source_account_id == target_account_id:
            return jsonify({"error": "Source and target accounts cannot be the same"}), 400
        
        # Verify both accounts belong to tenant - TENANT-CENTRIC
        source_account = tenant_query(Account).filter_by(id=source_account_id).first()
        target_account = tenant_query(Account).filter_by(id=target_account_id).first()
        
        if not source_account:
            return jsonify({"error": "Source account not found or access denied"}), 404
        if not target_account:
            return jsonify({"error": "Target account not found or access denied"}), 404
        
        # Define default account codes (25 total)
        default_codes = {
            '1000', '1100', '1200', '1300', '1400', '1500',  # Assets (6)
            '2000', '2100', '2200', '2300',  # Liabilities (4)
            '3000', '3100', '3200',  # Equity (3)
            '4000', '4100',  # Revenue (2)
            '5000', '6000', '6100', '6200', '6300', '6400', '6500', '6600', '6700', '6800'  # Expenses (10)
        }
        
        # VALIDATION CHECKS - Blockers
        
        # 1. Check if accounts are default/system accounts
        if source_account.code in default_codes:
            return jsonify({
                "error": f"Cannot merge default account '{source_account.code} - {source_account.name}'. Default accounts are protected."
            }), 400
        if target_account.code in default_codes:
            return jsonify({
                "error": f"Cannot merge into default account '{target_account.code} - {target_account.name}'. Default accounts are protected."
            }), 400
        
        # 2. Check if accounts are active
        if not source_account.is_active:
            return jsonify({
                "error": f"Source account '{source_account.name}' is inactive. Activate the account before merging."
            }), 400
        if not target_account.is_active:
            return jsonify({
                "error": f"Target account '{target_account.name}' is inactive. Activate the account before merging."
            }), 400
        
        # 3. Check if accounts have same type (STRICT - required)
        if source_account.type != target_account.type:
            return jsonify({
                "error": f"Cannot merge accounts of different types. Source is '{source_account.type}', target is '{target_account.type}'",
                "detail": "Merging different account types violates accounting principles and will corrupt your balance sheet."
            }), 400
        
        # 4. Check if accounts have same currency
        source_currency = source_account.currency or 'USD'
        target_currency = target_account.currency or 'USD'
        if source_currency != target_currency:
            return jsonify({
                "error": f"Cannot merge accounts with different currencies. Source uses '{source_currency}', target uses '{target_currency}'",
                "detail": "Convert currencies first or use accounts with the same currency."
            }), 400
        
        # 5. Check if source account has children - TENANT-CENTRIC
        child_count = tenant_query(Account).filter_by(parent_id=source_account_id).count()
        if child_count > 0:
            return jsonify({
                "error": f"Cannot merge account with {child_count} sub-account(s). Reassign or remove sub-accounts first.",
                "detail": f"Account '{source_account.name}' has {child_count} child account(s) that must be reassigned before merging."
            }), 400
        
        # 6. Check if target account has source as parent (circular reference)
        if target_account.parent_id == source_account_id:
            return jsonify({
                "error": "Cannot merge: Target account is a child of the source account. This would create a circular reference."
            }), 400
        
        # 7. Check if source account is parent of target (circular reference)
        if source_account.parent_id == target_account_id:
            return jsonify({
                "error": "Cannot merge: Source account is a child of the target account. This would create a circular reference."
            }), 400
        
        # Get transaction counts for audit trail - TENANT-CENTRIC
        from sqlalchemy import func
        source_transaction_count = db.session.query(func.count(JournalLine.id)).join(JournalEntry).filter(
            JournalLine.account_id == source_account_id,
            JournalEntry.tenant_id == tenant_id  # TENANT-CENTRIC
        ).scalar() or 0
        
        target_transaction_count = db.session.query(func.count(JournalLine.id)).join(JournalEntry).filter(
            JournalLine.account_id == target_account_id,
            JournalEntry.tenant_id == tenant_id  # TENANT-CENTRIC
        ).scalar() or 0
        
        # Transfer balance to target account
        source_balance = source_account.balance or 0.0
        target_balance = target_account.balance or 0.0
        target_account.balance = target_balance + source_balance
        
        # Transfer all journal lines from source to target - TENANT-CENTRIC
        updated_lines = JournalLine.query.join(JournalEntry).filter(
            JournalLine.account_id == source_account_id,
            JournalEntry.tenant_id == tenant_id  # TENANT-CENTRIC
        ).update({JournalLine.account_id: target_account_id}, synchronize_session=False)
        
        # Update any accounts that have source as parent (reassign to target) - TENANT-CENTRIC
        tenant_query(Account).filter_by(parent_id=source_account_id).update(
            {Account.parent_id: target_account_id}, synchronize_session=False
        )
        
        # Merge notes if both have notes
        merge_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        if source_account.notes and target_account.notes:
            target_account.notes = f"{target_account.notes}\n\n--- Merged from {source_account.name} ({source_account.code}) on {merge_timestamp} ---\n{source_account.notes}"
        elif source_account.notes:
            target_account.notes = f"--- Merged from {source_account.name} ({source_account.code}) on {merge_timestamp} ---\n{source_account.notes}"
        else:
            # Add merge record even if no notes
            if target_account.notes:
                target_account.notes = f"{target_account.notes}\n\n--- Merged from {source_account.name} ({source_account.code}) on {merge_timestamp} ---"
            else:
                target_account.notes = f"--- Merged from {source_account.name} ({source_account.code}) on {merge_timestamp} ---"
        
        # Store source account details for audit before deletion
        source_account_details = {
            "id": source_account.id,
            "code": source_account.code,
            "name": source_account.name,
            "type": source_account.type,
            "balance": source_balance
        }
        
        # Delete source account
        db.session.delete(source_account)
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully merged '{source_account_details['name']}' into '{target_account.name}'",
            "source_account": source_account_details,
            "target_account": {
                "id": target_account.id,
                "code": target_account.code,
                "name": target_account.name,
                "type": target_account.type
            },
            "balance_transferred": source_balance,
            "transactions_moved": updated_lines,
            "source_transaction_count": source_transaction_count,
            "target_transaction_count": target_transaction_count,
            "merged_at": merge_timestamp
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error merging accounts: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to merge accounts: {str(e)}"}), 500