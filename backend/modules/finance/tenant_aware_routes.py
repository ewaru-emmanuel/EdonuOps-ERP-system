"""
Tenant-Aware Finance Routes
Updated finance routes with multi-tenancy support
"""

from flask import Blueprint, request, jsonify, g
from app import db
from datetime import datetime
from sqlalchemy import and_, or_, func
from modules.core.tenant_context import (
    require_tenant, 
    get_tenant_context, 
    TenantAwareQuery,
    require_permission,
    require_module
)
from modules.core.rate_limiting import api_endpoint_limit, sensitive_endpoint_limit
from modules.finance.advanced_models import (
    ChartOfAccounts, 
    GeneralLedgerEntry, 
    JournalHeader,
    AccountsReceivable,
    AccountsPayable
)
from modules.finance.payment_models import (
    BankAccount, 
    BankTransaction, 
    ReconciliationSession,
    PaymentMethod
)
from modules.finance.daily_cycle_models import (
    DailyBalance,
    DailyCycleStatus,
    DailyTransactionSummary
)
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
tenant_finance_bp = Blueprint('tenant_finance', __name__, url_prefix='/api/finance')

# ============================================================================
# CHART OF ACCOUNTS - TENANT AWARE
# ============================================================================

@tenant_finance_bp.route('/chart-of-accounts', methods=['GET'])
def get_chart_of_accounts():
    """Get all chart of accounts"""
    try:
        # Simple query without tenant filtering
        accounts = ChartOfAccounts.query.all()
        
        # Calculate real-time balances for each account
        accounts_with_balances = []
        for account in accounts:
            # Get all GL entries for this account
            gl_entries = GeneralLedgerEntry.query.filter_by(account_id=account.id).all()
            
            # Calculate totals
            total_debits = sum(entry.debit_amount for entry in gl_entries)
            total_credits = sum(entry.credit_amount for entry in gl_entries)
            
            # Calculate balance based on account type
            if account.account_type.lower() in ['asset', 'expense']:
                # Assets and Expenses: Debit increases, Credit decreases
                balance = total_debits - total_credits
            else:
                # Liabilities, Equity, Revenue: Credit increases, Debit decreases
                balance = total_credits - total_debits
            
            accounts_with_balances.append({
                'id': account.id,
                'account_code': account.account_code,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'account_category': account.account_category,
                'parent_account_id': account.parent_account_id,
                'description': account.description,
                'is_active': account.is_active,
                'created_at': account.created_at.isoformat() if account.created_at else None,
                'updated_at': account.updated_at.isoformat() if account.updated_at else None,
                # Real-time balance information
                'balance': balance,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'gl_entry_count': len(gl_entries)
            })
        
        return jsonify(accounts_with_balances), 200
        
    except Exception as e:
        logger.error(f"Error fetching chart of accounts: {e}")
        return jsonify({'error': 'Failed to fetch chart of accounts'}), 500

@tenant_finance_bp.route('/chart-of-accounts', methods=['POST'])
def create_chart_of_account():
    """Create a new chart of account"""
    try:
        data = request.get_json()
        
        # Add default tenant_id
        data['tenant_id'] = 'default_tenant'
        
        # Create account directly
        account = ChartOfAccounts(**data)
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'id': account.id,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'account_type': account.account_type,
            'message': 'Account created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating chart of account: {e}")
        return jsonify({'error': 'Failed to create chart of account'}), 500

@tenant_finance_bp.route('/chart-of-accounts/<int:account_id>', methods=['PUT'])
@require_tenant
@require_permission('finance.accounts.update')
def update_chart_of_account(account_id):
    """Update a chart of account for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        data = request.get_json()
        
        # Remove tenant_id from data if present (shouldn't be changed)
        data.pop('tenant_id', None)
        
        account = TenantAwareQuery.update_by_tenant_and_id(
            ChartOfAccounts,
            tenant_context.tenant_id,
            account_id,
            **data
        )
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        return jsonify({
            'id': account.id,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'message': 'Account updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating chart of account: {e}")
        return jsonify({'error': 'Failed to update chart of account'}), 500

@tenant_finance_bp.route('/chart-of-accounts/<int:account_id>', methods=['DELETE'])
@require_tenant
@require_permission('finance.accounts.delete')
def delete_chart_of_account(account_id):
    """Delete a chart of account for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        success = TenantAwareQuery.delete_by_tenant_and_id(
            ChartOfAccounts,
            tenant_context.tenant_id,
            account_id
        )
        
        if not success:
            return jsonify({'error': 'Account not found'}), 404
            
        return jsonify({'message': 'Account deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting chart of account: {e}")
        return jsonify({'error': 'Failed to delete chart of account'}), 500

# ============================================================================
# GENERAL LEDGER - TENANT AWARE
# ============================================================================

@tenant_finance_bp.route('/general-ledger', methods=['GET'])
def get_general_ledger_entries():
    """Get all general ledger entries - No authentication required after login"""
    try:
        # Get query parameters
        account_id = request.args.get('account_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        # Debug: Log the request
        logger.info(f"GL GET request - account_id: {account_id}, start_date: {start_date}, end_date: {end_date}, status: {status}")
        
        # Build query without tenant filter (tenant_id column doesn't exist yet)
        query = GeneralLedgerEntry.query
        
        if account_id:
            query = query.filter_by(account_id=account_id)
        if start_date:
            query = query.filter(GeneralLedgerEntry.entry_date >= start_date)
        if end_date:
            query = query.filter(GeneralLedgerEntry.entry_date <= end_date)
        if status:
            query = query.filter_by(status=status)
        
        entries = query.order_by(GeneralLedgerEntry.entry_date.desc()).all()
        
        # Debug: Log the results
        logger.info(f"GL query returned {len(entries)} entries")
        
        result = [{
            'id': entry.id,
            'journal_header_id': entry.journal_header_id,
            'entry_date': entry.entry_date.isoformat() if entry.entry_date else None,
            'reference': entry.reference,
            'description': entry.description,
            'account_id': entry.account_id,
            'account_name': entry.account.account_name if entry.account else None,
            'debit_amount': entry.debit_amount,
            'credit_amount': entry.credit_amount,
            'balance': entry.balance,
            'status': entry.status,
            'journal_type': entry.journal_type,
            'fiscal_period': entry.fiscal_period,
            'created_by': entry.created_by,
            'created_at': entry.created_at.isoformat() if entry.created_at else None
        } for entry in entries]
        
        # Debug: Log the final result
        logger.info(f"GL returning {len(result)} entries to frontend")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching general ledger entries: {e}")
        return jsonify({'error': 'Failed to fetch general ledger entries'}), 500

@tenant_finance_bp.route('/general-ledger/debug', methods=['GET'])
def debug_general_ledger():
    """Debug endpoint to check GL entries count"""
    try:
        total_count = GeneralLedgerEntry.query.count()
        logger.info(f"Total GL entries in database: {total_count}")
        
        # Get a sample entry
        sample_entry = GeneralLedgerEntry.query.first()
        sample_data = None
        if sample_entry:
            sample_data = {
                'id': sample_entry.id,
                'description': sample_entry.description,
                'account_id': sample_entry.account_id,
                'debit_amount': sample_entry.debit_amount,
                'credit_amount': sample_entry.credit_amount,
                'entry_date': sample_entry.entry_date.isoformat() if sample_entry.entry_date else None
            }
        
        return jsonify({
            'total_count': total_count,
            'sample_entry': sample_data,
            'message': 'Debug info retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Debug GL error: {e}")
        return jsonify({'error': f'Debug failed: {str(e)}'}), 500

@tenant_finance_bp.route('/general-ledger', methods=['POST'])
@require_tenant
@require_permission('finance.gl.create')
def create_general_ledger_entry():
    """Create a new general ledger entry for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        data = request.get_json()
        
        # Add tenant_id to the data
        data['tenant_id'] = tenant_context.tenant_id
        data['created_by'] = tenant_context.user_id
        
        entry = TenantAwareQuery.create_with_tenant(
            GeneralLedgerEntry,
            tenant_context.tenant_id,
            **data
        )
        
        return jsonify({
            'id': entry.id,
            'reference': entry.reference,
            'description': entry.description,
            'account_id': entry.account_id,
            'debit_amount': entry.debit_amount,
            'credit_amount': entry.credit_amount,
            'message': 'General ledger entry created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating general ledger entry: {e}")
        return jsonify({'error': 'Failed to create general ledger entry'}), 500

# ============================================================================
# BANK RECONCILIATION - TENANT AWARE
# ============================================================================

@tenant_finance_bp.route('/reconciliation-sessions', methods=['GET'])
@require_tenant
def get_reconciliation_sessions():
    """Get all reconciliation sessions for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        bank_account_id = request.args.get('bank_account_id')
        status = request.args.get('status')
        
        query = ReconciliationSession.query.filter_by(tenant_id=tenant_context.tenant_id)
        
        if bank_account_id:
            query = query.filter_by(bank_account_id=bank_account_id)
        if status:
            query = query.filter_by(status=status)
        
        sessions = query.order_by(ReconciliationSession.statement_date.desc()).all()
        
        return jsonify([{
            'id': session.id,
            'bank_account_id': session.bank_account_id,
            'bank_account_name': session.bank_account.account_name if session.bank_account else None,
            'statement_date': session.statement_date.isoformat() if session.statement_date else None,
            'statement_balance': session.statement_balance,
            'book_balance': session.book_balance,
            'difference': session.difference,
            'status': session.status,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'completed_by': session.completed_by,
            'outstanding_deposits': session.outstanding_deposits,
            'outstanding_checks': session.outstanding_checks,
            'bank_charges': session.bank_charges,
            'bank_interest': session.bank_interest,
            'notes': session.notes,
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'created_by': session.created_by
        } for session in sessions]), 200
        
    except Exception as e:
        logger.error(f"Error fetching reconciliation sessions: {e}")
        return jsonify({'error': 'Failed to fetch reconciliation sessions'}), 500

@tenant_finance_bp.route('/reconciliation-sessions', methods=['POST'])
@require_tenant
@require_permission('finance.reconciliation.create')
def create_reconciliation_session():
    """Create a new reconciliation session for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        data = request.get_json()
        
        # Add tenant_id to the data
        data['tenant_id'] = tenant_context.tenant_id
        data['created_by'] = tenant_context.user_id
        
        session = TenantAwareQuery.create_with_tenant(
            ReconciliationSession,
            tenant_context.tenant_id,
            **data
        )
        
        return jsonify({
            'id': session.id,
            'bank_account_id': session.bank_account_id,
            'statement_date': session.statement_date.isoformat() if session.statement_date else None,
            'statement_balance': session.statement_balance,
            'book_balance': session.book_balance,
            'difference': session.difference,
            'status': session.status,
            'message': 'Reconciliation session created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating reconciliation session: {e}")
        return jsonify({'error': 'Failed to create reconciliation session'}), 500

# ============================================================================
# BANK ACCOUNTS - TENANT AWARE
# ============================================================================

@tenant_finance_bp.route('/bank-accounts', methods=['GET'])
@require_tenant
def get_bank_accounts():
    """Get all bank accounts for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        accounts = TenantAwareQuery.get_all_by_tenant(
            BankAccount,
            tenant_context.tenant_id
        )
        
        return jsonify([{
            'id': account.id,
            'account_name': account.account_name,
            'account_number': account.account_number,
            'bank_name': account.bank_name,
            'account_type': account.account_type,
            'currency': account.currency,
            'current_balance': account.current_balance,
            'is_active': account.is_active,
            'created_at': account.created_at.isoformat() if account.created_at else None,
            'created_by': account.created_by
        } for account in accounts]), 200
        
    except Exception as e:
        logger.error(f"Error fetching bank accounts: {e}")
        return jsonify({'error': 'Failed to fetch bank accounts'}), 500

@tenant_finance_bp.route('/bank-accounts', methods=['POST'])
@require_tenant
@require_permission('finance.bank_accounts.create')
def create_bank_account():
    """Create a new bank account for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        data = request.get_json()
        
        # Add tenant_id to the data
        data['tenant_id'] = tenant_context.tenant_id
        data['created_by'] = tenant_context.user_id
        
        account = TenantAwareQuery.create_with_tenant(
            BankAccount,
            tenant_context.tenant_id,
            **data
        )
        
        return jsonify({
            'id': account.id,
            'account_name': account.account_name,
            'account_number': account.account_number,
            'bank_name': account.bank_name,
            'account_type': account.account_type,
            'currency': account.currency,
            'current_balance': account.current_balance,
            'message': 'Bank account created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating bank account: {e}")
        return jsonify({'error': 'Failed to create bank account'}), 500

# ============================================================================
# BANK TRANSACTIONS - TENANT AWARE
# ============================================================================

@tenant_finance_bp.route('/bank-transactions', methods=['GET'])
@require_tenant
def get_bank_transactions():
    """Get all bank transactions for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        bank_account_id = request.args.get('bank_account_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        matched = request.args.get('matched')
        
        query = BankTransaction.query.filter_by(tenant_id=tenant_context.tenant_id)
        
        if bank_account_id:
            query = query.filter_by(bank_account_id=bank_account_id)
        if start_date:
            query = query.filter(BankTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(BankTransaction.transaction_date <= end_date)
        if matched is not None:
            query = query.filter_by(matched=matched.lower() == 'true')
        
        transactions = query.order_by(BankTransaction.transaction_date.desc()).all()
        
        return jsonify([{
            'id': transaction.id,
            'bank_account_id': transaction.bank_account_id,
            'bank_account_name': transaction.bank_account.account_name if transaction.bank_account else None,
            'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
            'amount': transaction.amount,
            'reference': transaction.reference,
            'description': transaction.description,
            'statement_date': transaction.statement_date.isoformat() if transaction.statement_date else None,
            'bank_reference': transaction.bank_reference,
            'matched': transaction.matched,
            'matched_transaction_id': transaction.matched_transaction_id,
            'matched_transaction_type': transaction.matched_transaction_type,
            'reconciliation_session_id': transaction.reconciliation_session_id,
            'reconciled_by': transaction.reconciled_by,
            'reconciled_at': transaction.reconciled_at.isoformat() if transaction.reconciled_at else None,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
            'created_by': transaction.created_by
        } for transaction in transactions]), 200
        
    except Exception as e:
        logger.error(f"Error fetching bank transactions: {e}")
        return jsonify({'error': 'Failed to fetch bank transactions'}), 500

# ============================================================================
# UNRECONCILED GL ENTRIES - TENANT AWARE
# ============================================================================

@tenant_finance_bp.route('/test-simple', methods=['GET'])
def test_simple():
    """Simple test route"""
    return jsonify({'message': 'Test route working'}), 200

@tenant_finance_bp.route('/unreconciled-gl-entries', methods=['GET'])
@require_tenant
def get_unreconciled_gl_entries():
    """Get unreconciled GL entries for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        # Simple implementation for now
        return jsonify([{
            'id': 1,
            'account_id': 1,
            'account_name': 'Test Account',
            'entry_date': '2024-01-01',
            'reference': 'TEST-001',
            'description': 'Test entry',
            'debit_amount': 100.0,
            'credit_amount': 0.0,
            'balance': 100.0,
            'status': 'posted',
            'created_at': '2024-01-01T00:00:00',
            'created_by': 'system'
        }]), 200
        
    except Exception as e:
        logger.error(f"Error fetching unreconciled GL entries: {e}")
        return jsonify({'error': 'Failed to fetch unreconciled GL entries'}), 500

# ============================================================================
# DAILY CYCLE - TENANT AWARE
# ============================================================================

@tenant_finance_bp.route('/daily-cycle/balances/<balance_date>', methods=['GET'])
@require_tenant
def get_daily_balances(balance_date):
    """Get all daily balances for a specific date for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        # Parse date
        try:
            balance_date_obj = datetime.strptime(balance_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get daily balances for the tenant
        daily_balances = DailyBalance.query.filter_by(
            tenant_id=tenant_context.tenant_id
        ).filter_by(balance_date=balance_date_obj).all()
        
        balances_data = []
        for balance in daily_balances:
            balances_data.append({
                'id': balance.id,
                'account_id': balance.account_id,
                'account_name': balance.account.account_name if balance.account else None,
                'account_type': balance.account.account_type if balance.account else None,
                'opening_balance': balance.opening_balance,
                'daily_debit': balance.daily_debit,
                'daily_credit': balance.daily_credit,
                'daily_net_movement': balance.daily_net_movement,
                'closing_balance': balance.closing_balance,
                'cycle_status': balance.cycle_status,
                'is_opening_captured': balance.is_opening_captured,
                'is_closing_calculated': balance.is_closing_calculated
            })
        
        return jsonify({
            'success': True,
            'data': {
                'balance_date': balance_date,
                'balances': balances_data,
                'total_accounts': len(balances_data)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily balances: {e}")
        return jsonify({'error': 'Failed to get daily balances'}), 500

# ============================================================================
# TENANT INFO ENDPOINTS
# ============================================================================

@tenant_finance_bp.route('/tenant-info', methods=['GET'])
@require_tenant
def get_tenant_info():
    """Get current tenant information"""
    try:
        tenant_context = get_tenant_context()
        tenant = g.tenant
        
        return jsonify({
            'tenant_id': tenant.id,
            'name': tenant.name,
            'domain': tenant.domain,
            'subscription_plan': tenant.subscription_plan,
            'status': tenant.status,
            'settings': tenant.settings or {},
            'metadata': tenant.tenant_metadata or {},
            'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
            'created_by': tenant.created_by
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching tenant info: {e}")
        return jsonify({'error': 'Failed to fetch tenant info'}), 500

@tenant_finance_bp.route('/tenant-modules', methods=['GET'])
@require_tenant
def get_tenant_modules():
    """Get activated modules for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        from modules.core.tenant_models import TenantModule
        modules = TenantModule.query.filter_by(
            tenant_id=tenant_context.tenant_id,
            enabled=True
        ).all()
        
        return jsonify([{
            'module_name': module.module_name,
            'enabled': module.enabled,
            'activated_at': module.activated_at.isoformat() if module.activated_at else None,
            'expires_at': module.expires_at.isoformat() if module.expires_at else None,
            'configuration': module.configuration or {}
        } for module in modules]), 200
        
    except Exception as e:
        logger.error(f"Error fetching tenant modules: {e}")
        return jsonify({'error': 'Failed to fetch tenant modules'}), 500
