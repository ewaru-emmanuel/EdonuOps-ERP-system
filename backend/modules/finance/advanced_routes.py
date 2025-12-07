from flask import Blueprint, request, jsonify
from app import db
from datetime import datetime, date
from sqlalchemy import func, and_, or_
import json
from modules.core.permissions import require_permission, require_module_access
from modules.core.tenant_helpers import get_current_user_tenant_id, get_current_user_id
from .advanced_models import (
    ChartOfAccounts, GeneralLedgerEntry, AccountsPayable, AccountsReceivable,
    FixedAsset, Budget, TaxRecord, BankReconciliation, APPayment, ARPayment,
    FinanceVendor, FinanceCustomer, AuditTrail, FinancialReport,
    DepreciationSchedule, InvoiceLineItem, FinancialPeriod, JournalHeader, MaintenanceRecord,
    TaxFilingHistory, ComplianceReport, UserActivity, BankStatement, KPI, CompanySettings
)
# Currency and ExchangeRate moved to currency_models.py - import separately if needed
from .currency_models import Currency, ExchangeRate
from .ai_analytics_service import AIAnalyticsService
from .workflow_service import WorkflowService
from .payment_journal_service import create_ar_payment_journal, create_ap_payment_journal, create_fx_journal

# Create Blueprint
advanced_finance_bp = Blueprint('advanced_finance', __name__)

# Handle CORS preflight for all routes in this blueprint
@advanced_finance_bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID,X-Tenant-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        return response, 200

# Test route to verify blueprint is registered
@advanced_finance_bp.route('/test', methods=['GET', 'OPTIONS'])
def test_route():
    """Test route to verify blueprint registration"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID,X-Tenant-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        return response, 200
    return jsonify({"message": "Advanced finance blueprint is working", "route": "/api/finance/advanced/test"}), 200

# Helper function to create audit trail
def create_audit_trail(table_name, record_id, action, old_values=None, new_values=None, user_id=None):
    try:
        audit = AuditTrail(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            user_id=user_id,
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        print(f"Audit trail creation failed: {e}")

# Chart of Accounts Routes - REMOVED (using tenant-aware routes instead)
# The tenant-aware routes in tenant_aware_routes.py provide better functionality
# with real-time balance calculation and multi-tenancy support

# Chart of Accounts POST route - REMOVED (using tenant-aware routes instead)

# General Ledger Routes
@advanced_finance_bp.route('/general-ledger', methods=['GET'])
@require_permission('finance.journal.read')
def get_general_ledger():
    try:
        print("🔍 GET /general-ledger called")
        print(f"📋 Request headers: {dict(request.headers)}")
        
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        print(f"👤 User ID from headers: {user_id}")
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
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        account_id = request.args.get('account_id')
        status = request.args.get('status')
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        query = GeneralLedgerEntry.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(GeneralLedgerEntry.entry_date >= start_date)
        if end_date:
            query = query.filter(GeneralLedgerEntry.entry_date <= end_date)
        if account_id:
            query = query.filter(GeneralLedgerEntry.account_id == account_id)
        if status:
            query = query.filter(GeneralLedgerEntry.status == status)
        
        entries = query.order_by(GeneralLedgerEntry.entry_date.desc()).all()
        
        # Build response with safe account name lookup
        result = []
        for entry in entries:
            account_name = f'Account {entry.account_id}'  # Default fallback
            try:
                # Try to get account name from relationship
                if hasattr(entry, 'account') and entry.account:
                    account_name = entry.account.account_name
                else:
                    # Fallback: query account directly
                    from modules.finance.advanced_models import ChartOfAccounts
                    account = ChartOfAccounts.query.get(entry.account_id)
                    if account:
                        account_name = account.account_name
            except Exception as e:
                print(f"Warning: Could not get account name for entry {entry.id}: {e}")
            
            # Safe datetime serialization
            def safe_isoformat(dt):
                if dt is None:
                    return None
                try:
                    return dt.isoformat()
                except Exception:
                    return str(dt) if dt else None
            
            result.append({
                'id': entry.id,
                'entry_date': safe_isoformat(entry.entry_date),
                'reference': entry.reference,
                'description': entry.description,
                'account_id': entry.account_id,
                'account_name': account_name,
                'debit_amount': entry.debit_amount,
                'credit_amount': entry.credit_amount,
                'balance': entry.balance,
                'status': entry.status,
                'journal_type': entry.journal_type,
                'fiscal_period': entry.fiscal_period,
                'created_by': entry.created_by,
                'approved_by': entry.approved_by,
                'created_at': safe_isoformat(entry.created_at)
            })
        
        print(f"✅ Returning {len(result)} general ledger entries for user {user_id}")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in get_general_ledger: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/general-ledger', methods=['POST', 'OPTIONS'])
@require_permission('finance.journal.create')
def create_general_ledger_entry():
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID,X-Tenant-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        return response, 200
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id using the same pattern as working routes
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['entry_date', 'account_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Auto-generate reference if empty
        if not data.get('reference'):
            data['reference'] = f"GL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Validate double-entry bookkeeping
        debit_amount = float(data.get('debit_amount', 0) or 0)
        credit_amount = float(data.get('credit_amount', 0) or 0)
        
        if debit_amount > 0 and credit_amount > 0:
            return jsonify({'error': 'Cannot have both debit and credit amounts'}), 400
        
        if debit_amount == 0 and credit_amount == 0:
            return jsonify({'error': 'Must have either debit or credit amount'}), 400
        
        # Validate account exists and belongs to tenant
        # GeneralLedgerEntry uses ChartOfAccounts model (advanced_chart_of_accounts table)
        account = tenant_query(ChartOfAccounts).filter_by(id=data['account_id']).first()
        if not account:
            # Also check if account exists in regular Account model (in case frontend sends wrong ID)
            from .models import Account
            regular_account = tenant_query(Account).filter_by(id=data['account_id']).first()
            if regular_account:
                return jsonify({'error': 'Account found but General Ledger requires Chart of Accounts entry. Please use an account from the Chart of Accounts.'}), 400
            return jsonify({'error': f'Account {data["account_id"]} not found or access denied for tenant {tenant_id}'}), 404
        
        entry = GeneralLedgerEntry(
            entry_date=datetime.strptime(data['entry_date'], '%Y-%m-%d').date(),
            reference=data['reference'],
            description=data.get('description'),
            account_id=data['account_id'],
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            balance=debit_amount - credit_amount,
            status=data.get('status', 'posted'),
            journal_type=data.get('journal_type', 'manual'),
            fiscal_period=data.get('fiscal_period'),
            tenant_id=tenant_id,  # TENANT-CENTRIC: Required field
            created_by=user_id_int,  # Audit trail: who created it
            approved_by=data.get('approved_by'),
            # Payment method integration fields
            payment_method_id=data.get('payment_method_id'),
            bank_account_id=data.get('bank_account_id'),
            payment_reference=data.get('payment_reference'),
            source_module=data.get('source_module', 'manual_entry'),
            source_transaction_id=data.get('source_transaction_id')
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('general_ledger_entries', entry.id, 'create', new_values=data)
        
        response = jsonify({
            'id': entry.id,
            'reference': entry.reference,
            'message': 'General ledger entry created successfully'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-User-ID,X-Tenant-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        return response, 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error creating general ledger entry: {e}")
        print(error_trace)
        return jsonify({'error': f'Failed to create general ledger entry: {str(e)}'}), 500

# Update General Ledger Entry
@advanced_finance_bp.route('/general-ledger/<int:entry_id>', methods=['PUT'])
@require_permission('finance.journal.update')
def update_general_ledger_entry(entry_id):
    try:
        # Get user context for multi-tenancy
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Find entry with user context - STRICT USER ISOLATION
        entry = GeneralLedgerEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return jsonify({'error': 'Entry not found or access denied'}), 404
            
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['entry_date', 'reference', 'account_id']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate double-entry bookkeeping
        debit_amount = float(data.get('debit_amount', 0) or 0)
        credit_amount = float(data.get('credit_amount', 0) or 0)
        
        if debit_amount > 0 and credit_amount > 0:
            return jsonify({'error': 'Cannot have both debit and credit amounts'}), 400
        
        if debit_amount == 0 and credit_amount == 0:
            return jsonify({'error': 'Must have either debit or credit amount'}), 400
        
        # Update entry
        entry.entry_date = datetime.strptime(data['entry_date'], '%Y-%m-%d').date()
        entry.reference = data['reference']
        entry.description = data.get('description')
        entry.account_id = data['account_id']
        entry.debit_amount = debit_amount
        entry.credit_amount = credit_amount
        entry.balance = debit_amount - credit_amount
        entry.status = data.get('status', 'posted')
        entry.journal_type = data.get('journal_type', 'manual')
        entry.fiscal_period = data.get('fiscal_period')
        entry.approved_by = data.get('approved_by')
        entry.updated_at = datetime.utcnow()
        
        # Don't update created_by - it should remain the original creator
        # entry.created_by = data.get('created_by')  # Removed this line
        
        db.session.commit()
        
        print(f"✅ Updated general ledger entry {entry.id} for user {user_id}")
        
        # Create audit trail
        try:
            create_audit_trail('general_ledger_entries', entry.id, 'update', new_values=data)
        except Exception as audit_error:
            print(f"Warning: Audit trail creation failed: {audit_error}")
        
        return jsonify({
            'id': entry.id,
            'reference': entry.reference,
            'message': 'General ledger entry updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete General Ledger Entry
@advanced_finance_bp.route('/general-ledger/<int:entry_id>', methods=['DELETE'])
@require_permission('finance.journal.delete')
def delete_general_ledger_entry(entry_id):
    try:
        # Get user context for multi-tenancy
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Find entry with user context - STRICT USER ISOLATION
        entry = GeneralLedgerEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return jsonify({'error': 'Entry not found or access denied'}), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        print(f"✅ Deleted general ledger entry {entry_id} for user {user_id}")
        
        # Create audit trail
        try:
            create_audit_trail('general_ledger_entries', entry_id, 'delete')
        except Exception as audit_error:
            print(f"Warning: Audit trail creation failed: {audit_error}")
        
        return jsonify({
            'message': 'General ledger entry deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Accounts Payable Routes
@advanced_finance_bp.route('/accounts-payable', methods=['GET'])
@require_permission('finance.ap.read')
def get_accounts_payable():
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for accounts payable, returning empty results")
            return jsonify([]), 200
        
        # Get query parameters
        status = request.args.get('status')
        vendor_id = request.args.get('vendor_id')
        due_date_from = request.args.get('due_date_from')
        due_date_to = request.args.get('due_date_to')
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        query = AccountsPayable.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter(AccountsPayable.status == status)
        if vendor_id:
            query = query.filter(AccountsPayable.vendor_id == vendor_id)
        if due_date_from:
            query = query.filter(AccountsPayable.due_date >= due_date_from)
        if due_date_to:
            query = query.filter(AccountsPayable.due_date <= due_date_to)
        
        invoices = query.order_by(AccountsPayable.due_date.asc()).all()
        
        return jsonify([{
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'vendor_id': invoice.vendor_id,
            'vendor_name': invoice.vendor_name,
            'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'total_amount': invoice.total_amount,
            'tax_amount': invoice.tax_amount,
            'discount_amount': invoice.discount_amount,
            'outstanding_amount': invoice.outstanding_amount,
            'currency': invoice.currency,
            'exchange_rate': invoice.exchange_rate,
            'status': invoice.status,
            'payment_terms': invoice.payment_terms,
            'approval_status': invoice.approval_status,
            'approved_by': invoice.approved_by,
            'created_at': invoice.created_at.isoformat() if invoice.created_at else None
        } for invoice in invoices]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/accounts-payable', methods=['POST'])
@require_permission('finance.ap.create')
def create_accounts_payable():
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
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for accounts payable creation, using default user ID")
        
        # Validate required fields
        required_fields = ['invoice_number', 'vendor_id', 'invoice_date', 'due_date', 'total_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if invoice number already exists
        existing_invoice = AccountsPayable.query.filter_by(invoice_number=data['invoice_number']).first()
        if existing_invoice:
            return jsonify({'error': 'Invoice number already exists'}), 400
        
        invoice = AccountsPayable(
            invoice_number=data['invoice_number'],
            vendor_id=data['vendor_id'],
            vendor_name=data.get('vendor_name'),
            invoice_date=datetime.strptime(data['invoice_date'], '%Y-%m-%d').date(),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            total_amount=data['total_amount'],
            tax_amount=float(data.get('tax_amount', 0) or 0),
            discount_amount=float(data.get('discount_amount', 0) or 0),
            outstanding_amount=data['total_amount'],
            currency=data.get('currency', 'USD'),
            exchange_rate=data.get('exchange_rate', 1.0),
            status=data.get('status', 'pending'),
            payment_terms=data.get('payment_terms'),
            approval_status=data.get('approval_status', 'pending'),
            created_by=user_id  # Associate with current user
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('accounts_payable', invoice.id, 'create', new_values=data)
        
        return jsonify({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'message': 'Accounts payable invoice created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Accounts Payable
@advanced_finance_bp.route('/accounts-payable/<int:invoice_id>', methods=['PUT'])
@require_permission('finance.ap.update')
def update_accounts_payable(invoice_id):
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for accounts payable update, using default user ID")
        
        # Get invoice and check ownership
        invoice = AccountsPayable.query.get_or_404(invoice_id)
        
        # STRICT USER ISOLATION: Ensure user can only update their own invoices
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        if invoice.user_id != user_id:
            return jsonify({"error": "Access denied: You can only update your own invoices"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['invoice_number', 'vendor_id', 'invoice_date', 'due_date', 'total_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Update invoice
        invoice.invoice_number = data['invoice_number']
        invoice.vendor_id = data['vendor_id']
        invoice.vendor_name = data.get('vendor_name')
        invoice.invoice_date = datetime.strptime(data['invoice_date'], '%Y-%m-%d').date()
        invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        invoice.total_amount = float(data['total_amount'])
        invoice.tax_amount = float(data.get('tax_amount', 0) or 0)
        invoice.discount_amount = float(data.get('discount_amount', 0) or 0)
        invoice.outstanding_amount = float(data['total_amount'])
        invoice.currency = data.get('currency', 'USD')
        invoice.exchange_rate = data.get('exchange_rate', 1.0)
        invoice.status = data.get('status', 'pending')
        invoice.payment_terms = data.get('payment_terms')
        invoice.approval_status = data.get('approval_status', 'pending')
        
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('accounts_payable', invoice.id, 'update', new_values=data)
        
        return jsonify({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'message': 'Accounts payable invoice updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Accounts Payable
@advanced_finance_bp.route('/accounts-payable/<int:invoice_id>', methods=['DELETE'])
@require_permission('finance.ap.delete')
def delete_accounts_payable(invoice_id):
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for accounts payable deletion, using default user ID")
        
        # Get invoice and check ownership
        invoice = AccountsPayable.query.get_or_404(invoice_id)
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Ensure user can only delete their own invoices
        if invoice.user_id != user_id:
            return jsonify({"error": "Access denied: You can only delete your own invoices"}), 403
        
        db.session.delete(invoice)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('accounts_payable', invoice_id, 'delete')
        
        return jsonify({
            'message': 'Accounts payable invoice deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Accounts Receivable Routes
@advanced_finance_bp.route('/accounts-receivable', methods=['GET'])
@require_permission('finance.ar.read')
def get_accounts_receivable():
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for accounts receivable, returning empty results")
            return jsonify([]), 200
        
        # Get query parameters
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        due_date_from = request.args.get('due_date_from')
        due_date_to = request.args.get('due_date_to')
        
        # Filter by user - include records with no user_id for backward compatibility
        query = AccountsReceivable.query.filter(
            AccountsReceivable.user_id == int(user_id)
        )
        
        if status:
            query = query.filter(AccountsReceivable.status == status)
        if customer_id:
            query = query.filter(AccountsReceivable.customer_id == customer_id)
        if due_date_from:
            query = query.filter(AccountsReceivable.due_date >= due_date_from)
        if due_date_to:
            query = query.filter(AccountsReceivable.due_date <= due_date_to)
        
        invoices = query.order_by(AccountsReceivable.due_date.asc()).all()
        
        return jsonify([{
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'customer_id': invoice.customer_id,
            'customer_name': invoice.customer_name,
            'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'total_amount': invoice.total_amount,
            'tax_amount': invoice.tax_amount,
            'discount_amount': invoice.discount_amount,
            'outstanding_amount': invoice.outstanding_amount,
            'currency': invoice.currency,
            'exchange_rate': invoice.exchange_rate,
            'status': invoice.status,
            'payment_terms': invoice.payment_terms,
            'credit_limit': invoice.credit_limit,
            'dunning_level': invoice.dunning_level,
            'last_reminder_date': invoice.last_reminder_date.isoformat() if invoice.last_reminder_date else None,
            'created_at': invoice.created_at.isoformat() if invoice.created_at else None
        } for invoice in invoices]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/accounts-receivable', methods=['POST'])
@require_permission('finance.ar.create')
def create_accounts_receivable():
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
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for accounts receivable creation, using default user ID")
        
        # Validate required fields
        required_fields = ['invoice_number', 'customer_id', 'invoice_date', 'due_date', 'total_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if invoice number already exists
        existing_invoice = AccountsReceivable.query.filter_by(invoice_number=data['invoice_number']).first()
        if existing_invoice:
            return jsonify({'error': 'Invoice number already exists'}), 400
        
        invoice = AccountsReceivable(
            invoice_number=data['invoice_number'],
            customer_id=data['customer_id'],
            customer_name=data.get('customer_name'),
            invoice_date=datetime.strptime(data['invoice_date'], '%Y-%m-%d').date(),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            total_amount=float(data['total_amount']),
            tax_amount=float(data.get('tax_amount', 0) or 0),
            discount_amount=float(data.get('discount_amount', 0) or 0),
            outstanding_amount=float(data['total_amount']),
            currency=data.get('currency', 'USD'),
            exchange_rate=data.get('exchange_rate', 1.0),
            status=data.get('status', 'pending'),
            payment_terms=data.get('payment_terms'),
            credit_limit=data.get('credit_limit'),
            dunning_level=data.get('dunning_level', 0),
            created_by=user_id  # Associate with current user
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('accounts_receivable', invoice.id, 'create', new_values=data)
        
        return jsonify({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'message': 'Accounts receivable invoice created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Accounts Receivable
@advanced_finance_bp.route('/accounts-receivable/<int:invoice_id>', methods=['PUT'])
@require_permission('finance.ar.update')
def update_accounts_receivable(invoice_id):
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for accounts receivable update, using default user ID")
        
        # Get invoice and check ownership
        invoice = AccountsReceivable.query.get_or_404(invoice_id)
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Ensure user can only update their own invoices
        if invoice.user_id != user_id:
            return jsonify({"error": "Access denied: You can only update your own invoices"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['invoice_number', 'customer_id', 'invoice_date', 'due_date', 'total_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Update invoice
        invoice.invoice_number = data['invoice_number']
        invoice.customer_id = data['customer_id']
        invoice.customer_name = data.get('customer_name')
        invoice.invoice_date = datetime.strptime(data['invoice_date'], '%Y-%m-%d').date()
        invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        invoice.total_amount = float(data['total_amount'])
        invoice.tax_amount = float(data.get('tax_amount', 0) or 0)
        invoice.discount_amount = float(data.get('discount_amount', 0) or 0)
        invoice.outstanding_amount = float(data['total_amount'])
        invoice.currency = data.get('currency', 'USD')
        invoice.exchange_rate = data.get('exchange_rate', 1.0)
        invoice.status = data.get('status', 'pending')
        invoice.payment_terms = data.get('payment_terms')
        invoice.credit_limit = data.get('credit_limit')
        invoice.dunning_level = data.get('dunning_level', 0)
        
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('accounts_receivable', invoice.id, 'update', new_values=data)
        
        return jsonify({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'message': 'Accounts receivable invoice updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Accounts Receivable
@advanced_finance_bp.route('/accounts-receivable/<int:invoice_id>', methods=['DELETE'])
@require_permission('finance.ar.delete')
def delete_accounts_receivable(invoice_id):
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for accounts receivable deletion, using default user ID")
        
        # Get invoice and check ownership
        invoice = AccountsReceivable.query.get_or_404(invoice_id)
        
        # STRICT USER ISOLATION: Convert and validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # STRICT USER ISOLATION: Ensure user can only delete their own invoices
        if invoice.user_id != user_id:
            return jsonify({"error": "Access denied: You can only delete your own invoices"}), 403
        
        db.session.delete(invoice)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('accounts_receivable', invoice_id, 'delete')
        
        return jsonify({
            'message': 'Accounts receivable invoice deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Fixed Assets Routes
@advanced_finance_bp.route('/fixed-assets', methods=['GET'])
@require_permission('finance.assets.read')
def get_fixed_assets():
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for fixed assets, returning empty results")
            return jsonify([]), 200
        
        # Get query parameters
        status = request.args.get('status')
        category = request.args.get('category')
        department = request.args.get('department')
        
        # Filter by user - include records with no user_id for backward compatibility
        query = FixedAsset.query.filter(
            FixedAsset.user_id == int(user_id)
        )
        
        if status:
            query = query.filter(FixedAsset.status == status)
        if category:
            query = query.filter(FixedAsset.category == category)
        if department:
            query = query.filter(FixedAsset.department == department)
        
        assets = query.order_by(FixedAsset.purchase_date.desc()).all()
        
        return jsonify([{
            'id': asset.id,
            'asset_id': asset.asset_id,
            'asset_name': asset.asset_name,
            'description': asset.description,
            'category': asset.category,
            'subcategory': asset.subcategory,
            'purchase_date': asset.purchase_date.isoformat() if asset.purchase_date else None,
            'purchase_value': asset.purchase_value,
            'current_value': asset.current_value,
            'salvage_value': asset.salvage_value,
            'useful_life': asset.useful_life,
            'depreciation_method': asset.depreciation_method,
            'depreciation_rate': asset.depreciation_rate,
            'accumulated_depreciation': asset.accumulated_depreciation,
            'location': asset.location,
            'department': asset.department,
            'assigned_to': asset.assigned_to,
            'status': asset.status,
            'disposal_date': asset.disposal_date.isoformat() if asset.disposal_date else None,
            'disposal_value': asset.disposal_value,
            'created_at': asset.created_at.isoformat() if asset.created_at else None
        } for asset in assets]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/fixed-assets', methods=['POST'])
@require_permission('finance.assets.create')
def create_fixed_asset():
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
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for fixed asset creation, using default user ID")
        
        # Validate required fields
        required_fields = ['asset_id', 'asset_name', 'category', 'purchase_date', 'purchase_value']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if asset ID already exists
        existing_asset = FixedAsset.query.filter_by(asset_id=data['asset_id']).first()
        if existing_asset:
            return jsonify({'error': 'Asset ID already exists'}), 400
        
        asset = FixedAsset(
            asset_id=data['asset_id'],
            asset_name=data['asset_name'],
            description=data.get('description'),
            category=data['category'],
            subcategory=data.get('subcategory'),
            purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date(),
            purchase_value=data['purchase_value'],
            current_value=data.get('current_value', data['purchase_value']),
            salvage_value=data.get('salvage_value', 0),
            useful_life=data.get('useful_life'),
            depreciation_method=data.get('depreciation_method'),
            depreciation_rate=data.get('depreciation_rate'),
            location=data.get('location'),
            department=data.get('department'),
            assigned_to=data.get('assigned_to'),
            status=data.get('status', 'active'),
            created_by=user_id  # Associate with current user
        )
        
        db.session.add(asset)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('fixed_assets', asset.id, 'create', new_values=data)
        
        return jsonify({
            'id': asset.id,
            'asset_id': asset.asset_id,
            'message': 'Fixed asset created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/fixed-assets/<int:asset_id>', methods=['PUT'])
@require_permission('finance.assets.update')
def update_fixed_asset(asset_id):
    try:
        asset = FixedAsset.query.get_or_404(asset_id)
        data = request.get_json()
        
        # Update fields
        if 'asset_name' in data:
            asset.asset_name = data['asset_name']
        if 'description' in data:
            asset.description = data['description']
        if 'category' in data:
            asset.category = data['category']
        if 'purchase_date' in data:
            asset.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        if 'purchase_value' in data:
            asset.purchase_value = data['purchase_value']
        if 'current_value' in data:
            asset.current_value = data['current_value']
        if 'salvage_value' in data:
            asset.salvage_value = data['salvage_value']
        if 'useful_life' in data:
            asset.useful_life = data['useful_life']
        if 'location' in data:
            asset.location = data['location']
        if 'status' in data:
            asset.status = data['status']
        
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('fixed_assets', asset.id, 'update', new_values=data)
        
        return jsonify({
            'id': asset.id,
            'asset_id': asset.asset_id,
            'message': 'Fixed asset updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/fixed-assets/<int:asset_id>', methods=['DELETE'])
@require_permission('finance.assets.delete')
def delete_fixed_asset(asset_id):
    try:
        asset = FixedAsset.query.get_or_404(asset_id)
        
        # Create audit trail before deletion
        create_audit_trail('fixed_assets', asset.id, 'delete', old_values={
            'asset_id': asset.asset_id,
            'asset_name': asset.asset_name,
            'category': asset.category
        })
        
        db.session.delete(asset)
        db.session.commit()
        
        return jsonify({
            'message': 'Fixed asset deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Maintenance Records Routes
@advanced_finance_bp.route('/maintenance-records', methods=['GET'])
@require_permission('finance.assets.read')
def get_maintenance_records():
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for maintenance records, returning empty results")
            return jsonify([]), 200
        
        # Get query parameters
        asset_id = request.args.get('asset_id')
        maintenance_type = request.args.get('maintenance_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        query = MaintenanceRecord.query.filter(
            MaintenanceRecord.user_id == int(user_id)
        )
        
        if asset_id:
            query = query.filter(MaintenanceRecord.asset_id == asset_id)
        if maintenance_type:
            query = query.filter(MaintenanceRecord.maintenance_type == maintenance_type)
        if status:
            query = query.filter(MaintenanceRecord.status == status)
        if start_date:
            query = query.filter(MaintenanceRecord.maintenance_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(MaintenanceRecord.maintenance_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        records = query.order_by(MaintenanceRecord.maintenance_date.desc()).all()
        
        return jsonify([{
            'id': record.id,
            'asset_id': record.asset_id,
            'asset_name': record.asset.asset_name if record.asset else None,
            'maintenance_type': record.maintenance_type,
            'maintenance_date': record.maintenance_date.isoformat() if record.maintenance_date else None,
            'description': record.description,
            'cost': record.cost,
            'performed_by': record.performed_by,
            'vendor': record.vendor,
            'next_maintenance_date': record.next_maintenance_date.isoformat() if record.next_maintenance_date else None,
            'status': record.status,
            'priority': record.priority,
            'parts_used': record.parts_used,
            'labor_hours': record.labor_hours,
            'notes': record.notes,
            'created_at': record.created_at.isoformat() if record.created_at else None
        } for record in records]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/maintenance-records', methods=['POST'])
@require_permission('finance.assets.update')
def create_maintenance_record():
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
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['asset_id', 'maintenance_type', 'maintenance_date', 'description']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if asset exists and belongs to user
        asset = FixedAsset.query.filter(
            and_(
                FixedAsset.id == data['asset_id'],
                FixedAsset.user_id == int(user_id)
            )
        ).first()
        if not asset:
            return jsonify({'error': 'Asset not found or access denied'}), 404
        
        record = MaintenanceRecord(
            asset_id=data['asset_id'],
            maintenance_type=data['maintenance_type'],
            maintenance_date=datetime.strptime(data['maintenance_date'], '%Y-%m-%d').date(),
            description=data['description'],
            cost=data.get('cost', 0.0),
            performed_by=data.get('performed_by'),
            vendor=data.get('vendor'),
            next_maintenance_date=datetime.strptime(data['next_maintenance_date'], '%Y-%m-%d').date() if data.get('next_maintenance_date') else None,
            status=data.get('status', 'completed'),
            priority=data.get('priority', 'normal'),
            parts_used=data.get('parts_used'),
            labor_hours=data.get('labor_hours', 0.0),
            notes=data.get('notes'),
            created_by=user_id  # Associate with current user
        )
        
        db.session.add(record)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('maintenance_records', record.id, 'create', new_values=data)
        
        return jsonify({
            'id': record.id,
            'asset_id': record.asset_id,
            'maintenance_type': record.maintenance_type,
            'message': 'Maintenance record created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/maintenance-records/<int:record_id>', methods=['PUT'])
@require_permission('finance.assets.update')
def update_maintenance_record(record_id):
    try:
        record = MaintenanceRecord.query.get_or_404(record_id)
        data = request.get_json()
        
        if 'maintenance_type' in data: record.maintenance_type = data['maintenance_type']
        if 'maintenance_date' in data: record.maintenance_date = datetime.strptime(data['maintenance_date'], '%Y-%m-%d').date()
        if 'description' in data: record.description = data['description']
        if 'cost' in data: record.cost = data['cost']
        if 'performed_by' in data: record.performed_by = data['performed_by']
        if 'vendor' in data: record.vendor = data['vendor']
        if 'next_maintenance_date' in data: 
            record.next_maintenance_date = datetime.strptime(data['next_maintenance_date'], '%Y-%m-%d').date() if data['next_maintenance_date'] else None
        if 'status' in data: record.status = data['status']
        if 'priority' in data: record.priority = data['priority']
        if 'parts_used' in data: record.parts_used = data['parts_used']
        if 'labor_hours' in data: record.labor_hours = data['labor_hours']
        if 'notes' in data: record.notes = data['notes']
        
        db.session.commit()
        create_audit_trail('maintenance_records', record.id, 'update', new_values=data)
        
        return jsonify({
            'id': record.id,
            'message': 'Maintenance record updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/maintenance-records/<int:record_id>', methods=['DELETE'])
@require_permission('finance.assets.delete')
def delete_maintenance_record(record_id):
    try:
        record = MaintenanceRecord.query.get_or_404(record_id)
        
        # Create audit trail before deletion
        create_audit_trail('maintenance_records', record.id, 'delete', old_values={
            'asset_id': record.asset_id,
            'maintenance_type': record.maintenance_type,
            'description': record.description
        })
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            'message': 'Maintenance record deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Budget Routes
@advanced_finance_bp.route('/budgets', methods=['GET'])
@require_permission('finance.budgets.read')
def get_budgets():
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for budgets, returning empty results")
            return jsonify([]), 200
        
        # Get query parameters
        fiscal_year = request.args.get('fiscal_year')
        department = request.args.get('department')
        status = request.args.get('status')
        
        # Filter by user - include records with no user_id for backward compatibility
        query = Budget.query.filter(
            Budget.user_id == int(user_id)
        )
        
        if fiscal_year:
            query = query.filter(Budget.fiscal_year == fiscal_year)
        if department:
            query = query.filter(Budget.department == department)
        if status:
            query = query.filter(Budget.status == status)
        
        budgets = query.order_by(Budget.fiscal_year.desc(), Budget.period.desc()).all()
        
        return jsonify([{
            'id': budget.id,
            'name': budget.name,
            'description': budget.description,
            'fiscal_year': budget.fiscal_year,
            'period': budget.period,
            'department': budget.department,
            'account_id': budget.account_id,
            'budgeted_amount': budget.budgeted_amount,
            'actual_amount': budget.actual_amount,
            'variance_amount': budget.variance_amount,
            'variance_percentage': budget.variance_percentage,
            'budget_type': budget.budget_type,
            'status': budget.status,
            'approved_by': budget.approved_by,
            'created_at': budget.created_at.isoformat() if budget.created_at else None
        } for budget in budgets]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/budgets', methods=['POST'])
@require_permission('finance.budgets.create')
def create_budget():
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'fiscal_year', 'budgeted_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        budget = Budget(
            name=data['name'],
            description=data.get('description'),
            fiscal_year=data['fiscal_year'],
            period=data.get('period'),
            department=data.get('department'),
            account_id=data.get('account_id'),
            budgeted_amount=data['budgeted_amount'],
            actual_amount=data.get('actual_amount', 0),
            variance_amount=data.get('variance_amount', 0),
            variance_percentage=data.get('variance_percentage', 0),
            budget_type=data.get('budget_type'),
            status=data.get('status', 'active'),
            user_id=int(user_id)
        )
        
        db.session.add(budget)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('budgets', budget.id, 'create', new_values=data)
        
        return jsonify({
            'id': budget.id,
            'name': budget.name,
            'message': 'Budget created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Budget
@advanced_finance_bp.route('/budgets/<int:budget_id>', methods=['PUT'])
@require_permission('finance.budgets.update')
def update_budget(budget_id):
    try:
        budget = Budget.query.get_or_404(budget_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'fiscal_year', 'budgeted_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Update budget
        budget.name = data['name']
        budget.description = data.get('description')
        budget.fiscal_year = data['fiscal_year']
        budget.period = data.get('period')
        budget.department = data.get('department')
        budget.account_id = data.get('account_id')
        budget.budgeted_amount = float(data['budgeted_amount'])
        budget.actual_amount = float(data.get('actual_amount', 0) or 0)
        budget.variance_amount = float(data.get('variance_amount', 0) or 0)
        budget.variance_percentage = float(data.get('variance_percentage', 0) or 0)
        budget.budget_type = data.get('budget_type')
        budget.status = data.get('status', 'active')
        
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('budgets', budget.id, 'update', new_values=data)
        
        return jsonify({
            'id': budget.id,
            'name': budget.name,
            'message': 'Budget updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Budget
@advanced_finance_bp.route('/budgets/<int:budget_id>', methods=['DELETE'])
@require_permission('finance.budgets.delete')
def delete_budget(budget_id):
    try:
        budget = Budget.query.get_or_404(budget_id)
        db.session.delete(budget)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('budgets', budget_id, 'delete')
        
        return jsonify({
            'message': 'Budget deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get Budgets by Account and Period
@advanced_finance_bp.route('/budgets/account/<int:account_id>', methods=['GET'])
@require_permission('finance.budgets.read')
def get_budgets_by_account(account_id):
    try:
        period = request.args.get('period')  # YYYY-MM format
        scenario = request.args.get('scenario', 'base')
        
        query = Budget.query.filter_by(account_id=account_id)
        
        if period:
            query = query.filter(Budget.period == period)
        if scenario:
            query = query.filter(Budget.budget_type == scenario)
        
        budgets = query.order_by(Budget.period.desc()).all()
        
        return jsonify([{
            'id': budget.id,
            'period': budget.period,
            'budgeted_amount': budget.budgeted_amount,
            'actual_amount': budget.actual_amount,
            'variance_amount': budget.variance_amount,
            'variance_percentage': budget.variance_percentage,
            'scenario': budget.budget_type,
            'status': budget.status
        } for budget in budgets]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Budget Summary for Dashboard
@advanced_finance_bp.route('/budgets/summary', methods=['GET'])
@require_permission('finance.budgets.read')
def get_budget_summary():
    try:
        period = request.args.get('period')  # YYYY-MM format
        scenario = request.args.get('scenario', 'base')
        
        query = Budget.query
        
        if period:
            query = query.filter(Budget.period == period)
        if scenario:
            query = query.filter(Budget.budget_type == scenario)
        
        budgets = query.all()
        
        # Calculate summary metrics
        total_budget = sum(b.budgeted_amount for b in budgets)
        total_actual = sum(b.actual_amount for b in budgets)
        total_variance = total_actual - total_budget
        total_variance_percentage = (total_variance / total_budget * 100) if total_budget > 0 else 0
        
        # Group by account type
        revenue_budget = sum(b.budgeted_amount for b in budgets if b.account and b.account.account_type == 'Revenue')
        expense_budget = sum(b.budgeted_amount for b in budgets if b.account and b.account.account_type == 'Expense')
        
        return jsonify({
            'total_budget': total_budget,
            'total_actual': total_actual,
            'total_variance': total_variance,
            'total_variance_percentage': total_variance_percentage,
            'revenue_budget': revenue_budget,
            'expense_budget': expense_budget,
            'net_budget': revenue_budget - expense_budget,
            'period': period,
            'scenario': scenario,
            'budget_count': len(budgets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create Budget from Template (Multiple accounts)
@advanced_finance_bp.route('/budgets/template', methods=['POST'])
@require_permission('finance.budgets.create')
def create_budget_from_template():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['period', 'scenario', 'accounts']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        period = data['period']
        scenario = data['scenario']
        accounts = data['accounts']  # Array of {account_id, budget_amount}
        
        created_budgets = []
        
        for account_data in accounts:
            budget = Budget(
                name=f"Budget {period} - {scenario}",
                description=f"Auto-generated budget for {period} with {scenario} scenario",
                fiscal_year=period[:4],
                period=period,
                account_id=account_data['account_id'],
                budgeted_amount=float(account_data['budget_amount']),
                budget_type=scenario,
                status='active'
            )
            db.session.add(budget)
            created_budgets.append(budget)
        
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('budgets', 'bulk', 'create', new_values=data)
        
        return jsonify({
            'message': f'{len(created_budgets)} budgets created successfully',
            'created_count': len(created_budgets),
            'period': period,
            'scenario': scenario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Tax Management Routes
@advanced_finance_bp.route('/tax-records', methods=['GET'])
@require_permission('finance.tax.read')
def get_tax_records():
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for tax records, returning empty results")
            return jsonify([]), 200
        
        # Get query parameters
        tax_type = request.args.get('tax_type')
        period = request.args.get('period')
        status = request.args.get('status')
        
        # STRICT USER ISOLATION: Filter by user_id only (no backward compatibility)
        query = TaxRecord.query.filter(
            TaxRecord.user_id == int(user_id)
        )
        
        if tax_type:
            query = query.filter(TaxRecord.tax_type == tax_type)
        if period:
            query = query.filter(TaxRecord.period == period)
        if status:
            query = query.filter(TaxRecord.status == status)
        
        tax_records = query.order_by(TaxRecord.due_date.asc()).all()
        
        return jsonify([{
            'id': tax.id,
            'tax_type': tax.tax_type,
            'tax_code': tax.tax_code,
            'jurisdiction': tax.jurisdiction,
            'period': tax.period,
            'taxable_amount': tax.taxable_amount,
            'tax_amount': tax.tax_amount,
            'tax_rate': tax.tax_rate,
            'due_date': tax.due_date.isoformat() if tax.due_date else None,
            'filing_date': tax.filing_date.isoformat() if tax.filing_date else None,
            'payment_date': tax.payment_date.isoformat() if tax.payment_date else None,
            'status': tax.status,
            'filing_reference': tax.filing_reference,
            'payment_reference': tax.payment_reference,
            'notes': tax.notes,
            'created_at': tax.created_at.isoformat() if tax.created_at else None
        } for tax in tax_records]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/tax-records', methods=['POST'])
@require_permission('finance.tax.create')
def create_tax_record():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['tax_type', 'taxable_amount', 'tax_amount', 'due_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        tax_record = TaxRecord(
            tax_type=data['tax_type'],
            tax_code=data.get('tax_code'),
            jurisdiction=data.get('jurisdiction'),
            period=data.get('period'),
            taxable_amount=data['taxable_amount'],
            tax_amount=data['tax_amount'],
            tax_rate=data.get('tax_rate'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            filing_date=datetime.strptime(data['filing_date'], '%Y-%m-%d').date() if data.get('filing_date') else None,
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date() if data.get('payment_date') else None,
            status=data.get('status', 'pending'),
            filing_reference=data.get('filing_reference'),
            payment_reference=data.get('payment_reference'),
            notes=data.get('notes')
        )
        
        db.session.add(tax_record)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('tax_records', tax_record.id, 'create', new_values=data)
        
        return jsonify({
            'id': tax_record.id,
            'tax_type': tax_record.tax_type,
            'message': 'Tax record created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Tax Record
@advanced_finance_bp.route('/tax-records/<int:tax_id>', methods=['PUT'])
@require_permission('finance.tax.update')
def update_tax_record(tax_id):
    try:
        tax_record = TaxRecord.query.get_or_404(tax_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['tax_type', 'taxable_amount', 'tax_amount', 'due_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Update tax record
        tax_record.tax_type = data['tax_type']
        tax_record.tax_code = data.get('tax_code')
        tax_record.jurisdiction = data.get('jurisdiction')
        tax_record.period = data.get('period')
        tax_record.taxable_amount = float(data['taxable_amount'])
        tax_record.tax_amount = float(data['tax_amount'])
        tax_record.tax_rate = float(data.get('tax_rate', 0) or 0)
        tax_record.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        tax_record.filing_date = datetime.strptime(data['filing_date'], '%Y-%m-%d').date() if data.get('filing_date') else None
        tax_record.payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date() if data.get('payment_date') else None
        tax_record.status = data.get('status', 'pending')
        tax_record.filing_reference = data.get('filing_reference')
        tax_record.payment_reference = data.get('payment_reference')
        tax_record.notes = data.get('notes')
        
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('tax_records', tax_record.id, 'update', new_values=data)
        
        return jsonify({
            'id': tax_record.id,
            'tax_type': tax_record.tax_type,
            'message': 'Tax record updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Tax Record
@advanced_finance_bp.route('/tax-records/<int:tax_id>', methods=['DELETE'])
@require_permission('finance.tax.delete')
def delete_tax_record(tax_id):
    try:
        tax_record = TaxRecord.query.get_or_404(tax_id)
        db.session.delete(tax_record)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('tax_records', tax_id, 'delete')
        
        return jsonify({
            'message': 'Tax record deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bank Reconciliation Routes
@advanced_finance_bp.route('/bank-reconciliations', methods=['GET'])
@require_permission('finance.reconciliation.read')
def get_bank_reconciliations():
    try:
        # Get query parameters
        bank_account = request.args.get('bank_account')
        status = request.args.get('status')
        
        query = BankReconciliation.query
        
        if bank_account:
            query = query.filter(BankReconciliation.bank_account == bank_account)
        if status:
            query = query.filter(BankReconciliation.status == status)
        
        reconciliations = query.order_by(BankReconciliation.statement_date.desc()).all()
        
        return jsonify([{
            'id': rec.id,
            'bank_account': rec.bank_account,
            'statement_date': rec.statement_date.isoformat() if rec.statement_date else None,
            'book_balance': rec.book_balance,
            'bank_balance': rec.bank_balance,
            'difference': rec.difference,
            'outstanding_deposits': rec.outstanding_deposits,
            'outstanding_checks': rec.outstanding_checks,
            'bank_charges': rec.bank_charges,
            'bank_interest': rec.bank_interest,
            'status': rec.status,
            'reconciled_by': rec.reconciled_by,
            'notes': rec.notes,
            'created_at': rec.created_at.isoformat() if rec.created_at else None
        } for rec in reconciliations]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/bank-reconciliations', methods=['POST'])
@require_permission('finance.reconciliation.create')
def create_bank_reconciliation():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['bank_account', 'statement_date', 'book_balance', 'bank_balance']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Convert string amounts to float
        book_balance = float(data['book_balance'])
        bank_balance = float(data['bank_balance'])
        
        reconciliation = BankReconciliation(
            bank_account=data['bank_account'],
            statement_date=datetime.strptime(data['statement_date'], '%Y-%m-%d').date(),
            book_balance=book_balance,
            bank_balance=bank_balance,
            difference=book_balance - bank_balance,
            outstanding_deposits=float(data.get('outstanding_deposits', 0) or 0),
            outstanding_checks=float(data.get('outstanding_checks', 0) or 0),
            bank_charges=float(data.get('bank_charges', 0) or 0),
            bank_interest=float(data.get('bank_interest', 0) or 0),
            status=data.get('status', 'pending'),
            notes=data.get('notes')
        )
        
        db.session.add(reconciliation)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('bank_reconciliations', reconciliation.id, 'create', new_values=data)
        
        return jsonify({
            'id': reconciliation.id,
            'bank_account': reconciliation.bank_account,
            'message': 'Bank reconciliation created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Bank Reconciliation
@advanced_finance_bp.route('/bank-reconciliations/<int:reconciliation_id>', methods=['PUT'])
@require_permission('finance.reconciliation.update')
def update_bank_reconciliation(reconciliation_id):
    try:
        reconciliation = BankReconciliation.query.get_or_404(reconciliation_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['bank_account', 'statement_date', 'book_balance', 'bank_balance']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Convert string amounts to float
        book_balance = float(data['book_balance'])
        bank_balance = float(data['bank_balance'])
        
        # Update reconciliation
        reconciliation.bank_account = data['bank_account']
        reconciliation.statement_date = datetime.strptime(data['statement_date'], '%Y-%m-%d').date()
        reconciliation.book_balance = book_balance
        reconciliation.bank_balance = bank_balance
        reconciliation.difference = book_balance - bank_balance
        reconciliation.outstanding_deposits = float(data.get('outstanding_deposits', 0) or 0)
        reconciliation.outstanding_checks = float(data.get('outstanding_checks', 0) or 0)
        reconciliation.bank_charges = float(data.get('bank_charges', 0) or 0)
        reconciliation.bank_interest = float(data.get('bank_interest', 0) or 0)
        reconciliation.status = data.get('status', 'pending')
        reconciliation.notes = data.get('notes')
        
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('bank_reconciliations', reconciliation.id, 'update', new_values=data)
        
        return jsonify({
            'id': reconciliation.id,
            'bank_account': reconciliation.bank_account,
            'message': 'Bank reconciliation updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Bank Reconciliation
@advanced_finance_bp.route('/bank-reconciliations/<int:reconciliation_id>', methods=['DELETE'])
@require_permission('finance.reconciliation.delete')
def delete_bank_reconciliation(reconciliation_id):
    try:
        reconciliation = BankReconciliation.query.get_or_404(reconciliation_id)
        db.session.delete(reconciliation)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('bank_reconciliations', reconciliation_id, 'delete')
        
        return jsonify({
            'message': 'Bank reconciliation deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Financial Reports Routes
@advanced_finance_bp.route('/reports/profit-loss', methods=['GET'])
@require_permission('finance.reports.read')
def get_profit_loss_report():
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
        
        # If still no user_id, return empty report (for development)
        if not user_id:
            print("Warning: No user context found for profit-loss report, returning empty results")
            return jsonify({
                'revenue': 0,
                'expenses': 0,
                'net_profit': 0
            }), 200
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400
        
        # Calculate revenue (credit entries in revenue accounts) - FILTER BY USER
        revenue = db.session.query(func.sum(GeneralLedgerEntry.credit_amount)).filter(
            and_(
                GeneralLedgerEntry.entry_date >= start_date,
                GeneralLedgerEntry.entry_date <= end_date,
                GeneralLedgerEntry.account.has(account_type='Revenue'),
                GeneralLedgerEntry.user_id == int(user_id)
            )
        ).scalar() or 0
        
        # Calculate expenses (debit entries in expense accounts) - FILTER BY USER
        expenses = db.session.query(func.sum(GeneralLedgerEntry.debit_amount)).filter(
            and_(
                GeneralLedgerEntry.entry_date >= start_date,
                GeneralLedgerEntry.entry_date <= end_date,
                GeneralLedgerEntry.account.has(account_type='Expense'),
                GeneralLedgerEntry.user_id == int(user_id)
            )
        ).scalar() or 0
        
        net_profit = revenue - expenses
        
        report_data = {
            'period': f"{start_date} to {end_date}",
            'revenue': revenue,
            'expenses': expenses,
            'net_profit': net_profit,
            'gross_margin': (revenue - expenses) / revenue * 100 if revenue > 0 else 0
        }
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/reports/balance-sheet', methods=['GET'])
@require_permission('finance.reports.read')
def get_balance_sheet_report():
    try:
        # Get query parameters
        as_of_date = request.args.get('as_of_date')
        
        if not as_of_date:
            return jsonify({'error': 'as_of_date is required'}), 400
        
        # Calculate assets (debit balance in asset accounts)
        assets = db.session.query(func.sum(GeneralLedgerEntry.balance)).filter(
            and_(
                GeneralLedgerEntry.entry_date <= as_of_date,
                GeneralLedgerEntry.account.has(account_type='Asset')
            )
        ).scalar() or 0
        
        # Calculate liabilities (credit balance in liability accounts)
        liabilities = db.session.query(func.sum(GeneralLedgerEntry.balance)).filter(
            and_(
                GeneralLedgerEntry.entry_date <= as_of_date,
                GeneralLedgerEntry.account.has(account_type='Liability')
            )
        ).scalar() or 0
        
        # Calculate equity (credit balance in equity accounts)
        equity = db.session.query(func.sum(GeneralLedgerEntry.balance)).filter(
            and_(
                GeneralLedgerEntry.entry_date <= as_of_date,
                GeneralLedgerEntry.account.has(account_type='Equity')
            )
        ).scalar() or 0
        
        report_data = {
            'as_of_date': as_of_date,
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'total_liabilities_equity': liabilities + equity
        }
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard Metrics
@advanced_finance_bp.route('/dashboard-metrics', methods=['GET'])
@require_permission('finance.reports.read')
def get_dashboard_metrics():
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
        
        # If still no user_id, return empty metrics (for development)
        if not user_id:
            print("Warning: No user context found for dashboard metrics, returning empty results")
            return jsonify({
                'total_assets': 0,
                'total_accounts_payable': 0,
                'total_accounts_receivable': 0,
                'pending_reconciliations': 0,
                'overdue_invoices': 0
            }), 200
        
        # Calculate key metrics - FILTER BY USER
        total_assets = db.session.query(func.sum(FixedAsset.current_value)).filter(
            FixedAsset.user_id == int(user_id)
        ).scalar() or 0
        
        total_ap = db.session.query(func.sum(AccountsPayable.outstanding_amount)).filter(
            and_(
                AccountsPayable.status.in_(['pending', 'approved']),
                AccountsPayable.user_id == int(user_id)
            )
        ).scalar() or 0
        
        total_ar = db.session.query(func.sum(AccountsReceivable.outstanding_amount)).filter(
            and_(
                AccountsReceivable.status.in_(['pending', 'overdue']),
                AccountsReceivable.user_id == int(user_id)
            )
        ).scalar() or 0
        
        pending_reconciliations = db.session.query(func.count(BankReconciliation.id)).filter(
            and_(
                BankReconciliation.status == 'pending',
                BankReconciliation.user_id == int(user_id)
            )
        ).scalar() or 0
        
        overdue_invoices = db.session.query(func.count(AccountsReceivable.id)).filter(
            and_(
                AccountsReceivable.status == 'overdue',
                AccountsReceivable.due_date < date.today(),
                AccountsReceivable.user_id == int(user_id)
            )
        ).scalar() or 0
        
        metrics = {
            'total_assets': total_assets,
            'total_accounts_payable': total_ap,
            'total_accounts_receivable': total_ar,
            'pending_reconciliations': pending_reconciliations,
            'overdue_invoices': overdue_invoices,
            'cash_flow': total_ar - total_ap,
            'compliance_score': 95  # Mock score
        }
        
        return jsonify(metrics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Legacy routes for backward compatibility
@advanced_finance_bp.route('/accounts', methods=['GET'])
@require_permission('finance.accounts.read')
def get_accounts():
    """Get all accounts from database - Legacy route"""
    try:
        accounts = ChartOfAccounts.query.filter_by(is_active=True).all()
        result = []
        for acc in accounts:
            # Calculate balance from journal lines
            from sqlalchemy import func
            from modules.finance.models import JournalLine, JournalEntry
            
            balance_result = db.session.query(
                func.coalesce(func.sum(JournalLine.debit_amount), 0) - 
                func.coalesce(func.sum(JournalLine.credit_amount), 0)
            ).join(JournalEntry).filter(
                JournalLine.account_id == acc.id
            ).scalar() or 0.0
            
            result.append({
                "id": acc.id,
                "code": acc.account_code,
                "name": acc.account_name,
                "type": acc.account_type,
                "balance": float(balance_result),
                "parent_id": acc.parent_account_id,
                "is_active": acc.is_active,
                "created_at": acc.created_at.isoformat() if acc.created_at else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts"}), 500

@advanced_finance_bp.route('/accounts', methods=['POST'])
@require_permission('finance.accounts.create')
def create_account():
    """Create a new account - Legacy route"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['code', 'name', 'type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if account code already exists
        existing_account = ChartOfAccounts.query.filter_by(account_code=data['code']).first()
        if existing_account:
            return jsonify({'error': 'Account code already exists'}), 400
        
        account = ChartOfAccounts(
            account_code=data['code'],
            account_name=data['name'],
            account_type=data['type'],
            parent_account_id=data.get('parent_id'),
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            "id": account.id,
            "code": account.account_code,
            "name": account.account_name,
            "type": account.account_type,
            "balance": 0.0,
            "parent_id": account.parent_account_id,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat() if account.created_at else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating account: {e}")
        return jsonify({"error": f"Failed to create account: {str(e)}"}), 500

@advanced_finance_bp.route('/journal-entries', methods=['GET'])
@require_permission('finance.journal.read')
def get_journal_entries():
    """Get all journal entries from database - Legacy route"""
    try:
        entries = GeneralLedgerEntry.query.all()
        return jsonify([{
            "id": entry.id,
            "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "status": entry.status,
            "total_debit": float(entry.debit_amount) if entry.debit_amount else 0.0,
            "total_credit": float(entry.credit_amount) if entry.credit_amount else 0.0,
            "created_at": entry.created_at.isoformat() if entry.created_at else None
        } for entry in entries]), 200
    except Exception as e:
        print(f"Error fetching journal entries: {e}")
        return jsonify({"error": "Failed to fetch journal entries"}), 500

# Vendor Management Routes
@advanced_finance_bp.route('/vendors', methods=['GET'])
@require_permission('finance.vendors.read')
def get_vendors():
    try:
        vendors = FinanceVendor.query.all()
        return jsonify([{
            'id': vendor.id,
            'vendor_code': vendor.vendor_code,
            'vendor_name': vendor.vendor_name,
            'contact_person': vendor.contact_person,
            'email': vendor.email,
            'phone': vendor.phone,
            'address': vendor.address,
            'tax_id': vendor.tax_id,
            'payment_terms': vendor.payment_terms,
            'credit_limit': vendor.credit_limit,
            'status': vendor.status,
            'created_at': vendor.created_at.isoformat() if vendor.created_at else None
        } for vendor in vendors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/vendors', methods=['POST'])
@require_permission('finance.vendors.create')
def create_vendor():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vendor_code', 'vendor_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if vendor code already exists
        existing_vendor = FinanceVendor.query.filter_by(vendor_code=data['vendor_code']).first()
        if existing_vendor:
            return jsonify({'error': 'Vendor code already exists'}), 400
        
        vendor = FinanceVendor(
            vendor_code=data['vendor_code'],
            vendor_name=data['vendor_name'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            tax_id=data.get('tax_id'),
            payment_terms=data.get('payment_terms'),
            credit_limit=data.get('credit_limit'),
            status=data.get('status', 'active')
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('finance_vendors', vendor.id, 'create', new_values=data)
        
        return jsonify({
            'id': vendor.id,
            'vendor_code': vendor.vendor_code,
            'message': 'Vendor created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Customer Management Routes
@advanced_finance_bp.route('/customers', methods=['GET'])
@require_permission('finance.customers.read')
def get_customers():
    try:
        customers = FinanceCustomer.query.all()
        return jsonify([{
            'id': customer.id,
            'customer_code': customer.customer_code,
            'customer_name': customer.customer_name,
            'contact_person': customer.contact_person,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'tax_id': customer.tax_id,
            'payment_terms': customer.payment_terms,
            'credit_limit': customer.credit_limit,
            'status': customer.status,
            'created_at': customer.created_at.isoformat() if customer.created_at else None
        } for customer in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/customers', methods=['POST'])
@require_permission('finance.customers.create')
def create_customer():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_code', 'customer_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if customer code already exists
        existing_customer = FinanceCustomer.query.filter_by(customer_code=data['customer_code']).first()
        if existing_customer:
            return jsonify({'error': 'Customer code already exists'}), 400
        
        customer = FinanceCustomer(
            customer_code=data['customer_code'],
            customer_name=data['customer_name'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            tax_id=data.get('tax_id'),
            payment_terms=data.get('payment_terms'),
            credit_limit=data.get('credit_limit'),
            status=data.get('status', 'active')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('finance_customers', customer.id, 'create', new_values=data)
        
        return jsonify({
            'id': customer.id,
            'customer_code': customer.customer_code,
            'message': 'Customer created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Payment Management Routes
@advanced_finance_bp.route('/ap-payments', methods=['GET'])
@require_permission('finance.payments.read')
def get_ap_payments():
    try:
        payments = APPayment.query.all()
        return jsonify([{
            'id': payment.id,
            'payment_reference': payment.payment_reference,
            'invoice_id': payment.invoice_id,
            'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
            'payment_amount': payment.payment_amount,
            'payment_method': payment.payment_method,
            'bank_account': payment.bank_account,
            'status': payment.status,
            'created_at': payment.created_at.isoformat() if payment.created_at else None
        } for payment in payments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/ap-payments', methods=['POST'])
@require_permission('finance.payments.create')
def create_ap_payment():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['payment_reference', 'invoice_id', 'payment_date', 'payment_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if payment reference already exists
        existing_payment = APPayment.query.filter_by(payment_reference=data['payment_reference']).first()
        if existing_payment:
            return jsonify({'error': 'Payment reference already exists'}), 400
        
        payment = APPayment(
            payment_reference=data['payment_reference'],
            invoice_id=data['invoice_id'],
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date(),
            payment_amount=data['payment_amount'],
            payment_method=data.get('payment_method'),
            bank_account=data.get('bank_account'),
            status=data.get('status', 'pending')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Create automatic journal entry for payment
        if data.get('status') == 'cleared' or data.get('auto_create_journal', True):
            journal_result = create_ap_payment_journal({
                'invoice_id': payment.invoice_id,
                'payment_amount': payment.payment_amount,
                'payment_method_id': data.get('payment_method_id'),
                'bank_account_id': data.get('bank_account_id'),
                'processing_fee': data.get('processing_fee', 0),
                'payment_reference': payment.payment_reference,
                'payment_date': payment.payment_date
            })
            
            if not journal_result.get('success'):
                # Log warning but don't fail the payment creation
                print(f"Warning: Could not create journal entry for AP payment {payment.id}: {journal_result.get('error')}")
        
        # Create audit trail
        create_audit_trail('ap_payments', payment.id, 'create', new_values=data)
        
        return jsonify({
            'id': payment.id,
            'payment_reference': payment.payment_reference,
            'message': 'AP payment created successfully',
            'journal_entry_created': journal_result.get('success', False) if 'journal_result' in locals() else False
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/ar-payments', methods=['GET'])
@require_permission('finance.payments.read')
def get_ar_payments():
    try:
        payments = ARPayment.query.all()
        return jsonify([{
            'id': payment.id,
            'payment_reference': payment.payment_reference,
            'invoice_id': payment.invoice_id,
            'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
            'payment_amount': payment.payment_amount,
            'payment_method': payment.payment_method,
            'bank_account': payment.bank_account,
            'status': payment.status,
            'created_at': payment.created_at.isoformat() if payment.created_at else None
        } for payment in payments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/ar-payments', methods=['POST'])
@require_permission('finance.payments.create')
def create_ar_payment():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['payment_reference', 'invoice_id', 'payment_date', 'payment_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if payment reference already exists
        existing_payment = ARPayment.query.filter_by(payment_reference=data['payment_reference']).first()
        if existing_payment:
            return jsonify({'error': 'Payment reference already exists'}), 400
        
        payment = ARPayment(
            payment_reference=data['payment_reference'],
            invoice_id=data['invoice_id'],
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date(),
            payment_amount=data['payment_amount'],
            payment_method=data.get('payment_method'),
            bank_account=data.get('bank_account'),
            status=data.get('status', 'pending')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Create automatic journal entry for payment
        if data.get('status') == 'cleared' or data.get('auto_create_journal', True):
            journal_result = create_ar_payment_journal({
                'invoice_id': payment.invoice_id,
                'payment_amount': payment.payment_amount,
                'payment_method_id': data.get('payment_method_id'),
                'bank_account_id': data.get('bank_account_id'),
                'processing_fee': data.get('processing_fee', 0),
                'payment_reference': payment.payment_reference,
                'payment_date': payment.payment_date
            })
            
            if not journal_result.get('success'):
                # Log warning but don't fail the payment creation
                print(f"Warning: Could not create journal entry for AR payment {payment.id}: {journal_result.get('error')}")
        
        # Create audit trail
        create_audit_trail('ar_payments', payment.id, 'create', new_values=data)
        
        return jsonify({
            'id': payment.id,
            'payment_reference': payment.payment_reference,
            'message': 'AR payment created successfully',
            'journal_entry_created': journal_result.get('success', False) if 'journal_result' in locals() else False
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Audit Trail Routes
@advanced_finance_bp.route('/audit-trail', methods=['GET'])
@require_permission('finance.audit.read')
def get_audit_trail():
    try:
        # Get query parameters
        table_name = request.args.get('table_name')
        record_id = request.args.get('record_id')
        action = request.args.get('action')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = AuditTrail.query
        
        if table_name:
            query = query.filter(AuditTrail.table_name == table_name)
        if record_id:
            query = query.filter(AuditTrail.record_id == record_id)
        if action:
            query = query.filter(AuditTrail.action == action)
        if start_date:
            query = query.filter(AuditTrail.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditTrail.timestamp <= end_date)
        
        audit_records = query.order_by(AuditTrail.timestamp.desc()).limit(100).all()
        
        return jsonify([{
            'id': audit.id,
            'table_name': audit.table_name,
            'record_id': audit.record_id,
            'action': audit.action,
            'old_values': json.loads(audit.old_values) if audit.old_values else None,
            'new_values': json.loads(audit.new_values) if audit.new_values else None,
            'user_id': audit.user_id,
            'ip_address': audit.ip_address,
            'timestamp': audit.timestamp.isoformat() if audit.timestamp else None
        } for audit in audit_records]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Currency Management Routes
@advanced_finance_bp.route('/currencies', methods=['GET'])
@require_permission('finance.currency.read')
def get_currencies():
    try:
        currencies = Currency.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': currency.id,
            'currency_code': currency.currency_code,
            'currency_name': currency.currency_name,
            'symbol': currency.symbol,
            'is_base_currency': currency.is_base_currency,
            'is_active': currency.is_active,
            'created_at': currency.created_at.isoformat() if currency.created_at else None
        } for currency in currencies]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/currencies', methods=['POST'])
@require_permission('finance.currency.create')
def create_currency():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['currency_code', 'currency_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if currency code already exists
        existing_currency = Currency.query.filter_by(currency_code=data['currency_code']).first()
        if existing_currency:
            return jsonify({'error': 'Currency code already exists'}), 400
        
        currency = Currency(
            currency_code=data['currency_code'],
            currency_name=data['currency_name'],
            symbol=data.get('symbol'),
            is_base_currency=data.get('is_base_currency', False),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(currency)
        db.session.commit()
        
        return jsonify({
            'id': currency.id,
            'currency_code': currency.currency_code,
            'message': 'Currency created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Exchange Rate Routes
@advanced_finance_bp.route('/exchange-rates', methods=['GET'])
@require_permission('finance.currency.read')
def get_exchange_rates():
    try:
        # Return empty array if ExchangeRate model doesn't exist
        try:
            from .currency_models import ExchangeRate
        except ImportError:
            return jsonify([]), 200
        
        # Get query parameters
        from_currency = request.args.get('from_currency')
        to_currency = request.args.get('to_currency')
        effective_date = request.args.get('effective_date')
        
        query = ExchangeRate.query
        
        if from_currency:
            query = query.filter(ExchangeRate.from_currency == from_currency)
        if to_currency:
            query = query.filter(ExchangeRate.to_currency == to_currency)
        if effective_date:
            query = query.filter(ExchangeRate.effective_date == effective_date)
        
        rates = query.order_by(ExchangeRate.effective_date.desc()).all()
        
        return jsonify([{
            'id': rate.id,
            'from_currency': rate.from_currency,
            'to_currency': rate.to_currency,
            'rate': rate.rate,
            'effective_date': rate.effective_date.isoformat() if rate.effective_date else None,
            'created_at': rate.created_at.isoformat() if rate.created_at else None
        } for rate in rates]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/exchange-rates', methods=['POST'])
@require_permission('finance.currency.create')
def create_exchange_rate():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['from_currency', 'to_currency', 'rate', 'effective_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        rate = ExchangeRate(
            from_currency=data['from_currency'],
            to_currency=data['to_currency'],
            rate=data['rate'],
            effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d').date()
        )
        
        db.session.add(rate)
        db.session.commit()
        
        return jsonify({
            'id': rate.id,
            'from_currency': rate.from_currency,
            'to_currency': rate.to_currency,
            'message': 'Exchange rate created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Financial Reports Cache Routes
@advanced_finance_bp.route('/reports/cache', methods=['GET'])
@require_permission('finance.reports.read')
def get_cached_reports():
    try:
        # Get query parameters
        report_type = request.args.get('report_type')
        period = request.args.get('period')
        
        query = FinancialReport.query
        
        if report_type:
            query = query.filter(FinancialReport.report_type == report_type)
        if period:
            query = query.filter(FinancialReport.report_period == period)
        
        reports = query.filter_by(is_latest=True).order_by(FinancialReport.generated_at.desc()).all()
        
        return jsonify([{
            'id': report.id,
            'report_type': report.report_type,
            'report_period': report.report_period,
            'report_data': json.loads(report.report_data) if report.report_data else None,
            'generated_at': report.generated_at.isoformat() if report.generated_at else None,
            'generated_by': report.generated_by,
            'is_latest': report.is_latest
        } for report in reports]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/reports/cache', methods=['POST'])
@require_permission('reports.cache.create')
def cache_financial_report():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['report_type', 'report_period', 'report_data']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Mark existing reports as not latest
        FinancialReport.query.filter_by(
            report_type=data['report_type'],
            report_period=data['report_period'],
            is_latest=True
        ).update({'is_latest': False})
        
        report = FinancialReport(
            report_type=data['report_type'],
            report_period=data['report_period'],
            report_data=json.dumps(data['report_data']),
            generated_by=data.get('generated_by'),
            is_latest=True
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'id': report.id,
            'report_type': report.report_type,
            'message': 'Financial report cached successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Journal Header Routes
@advanced_finance_bp.route('/journal-headers', methods=['GET'])
@require_permission('journal-headers.journal-headers.read')
def get_journal_headers():
    try:
        # Get query parameters
        status = request.args.get('status')
        journal_type = request.args.get('journal_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = JournalHeader.query
        
        if status:
            query = query.filter(JournalHeader.status == status)
        if journal_type:
            query = query.filter(JournalHeader.journal_type == journal_type)
        if start_date:
            query = query.filter(JournalHeader.journal_date >= start_date)
        if end_date:
            query = query.filter(JournalHeader.journal_date <= end_date)
        
        headers = query.order_by(JournalHeader.journal_date.desc()).all()
        
        return jsonify([{
            'id': header.id,
            'journal_number': header.journal_number,
            'journal_date': header.journal_date.isoformat() if header.journal_date else None,
            'reference': header.reference,
            'description': header.description,
            'journal_type': header.journal_type,
            'status': header.status,
            'total_debit': header.total_debit,
            'total_credit': header.total_credit,
            'fiscal_period': header.fiscal_period,
            'created_by': header.created_by,
            'posted_by': header.posted_by,
            'posted_at': header.posted_at.isoformat() if header.posted_at else None,
            'created_at': header.created_at.isoformat() if header.created_at else None
        } for header in headers]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/journal-headers', methods=['POST'])
@require_permission('journal-headers.journal-headers.create')
def create_journal_header():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['journal_number', 'journal_date', 'journal_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if journal number already exists
        existing_journal = JournalHeader.query.filter_by(journal_number=data['journal_number']).first()
        if existing_journal:
            return jsonify({'error': 'Journal number already exists'}), 400
        
        header = JournalHeader(
            journal_number=data['journal_number'],
            journal_date=datetime.strptime(data['journal_date'], '%Y-%m-%d').date(),
            reference=data.get('reference'),
            description=data.get('description'),
            journal_type=data['journal_type'],
            status=data.get('status', 'draft'),
            fiscal_period=data.get('fiscal_period'),
            created_by=data.get('created_by')
        )
        
        db.session.add(header)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('journal_headers', header.id, 'create', new_values=data)
        
        return jsonify({
            'id': header.id,
            'journal_number': header.journal_number,
            'message': 'Journal header created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Depreciation Schedule Routes
@advanced_finance_bp.route('/depreciation-schedules', methods=['GET'])
@require_permission('finance.assets.read')
def get_depreciation_schedules():
    try:
        # Get query parameters
        asset_id = request.args.get('asset_id')
        period = request.args.get('period')
        is_posted = request.args.get('is_posted')
        
        query = DepreciationSchedule.query
        
        if asset_id:
            query = query.filter(DepreciationSchedule.asset_id == asset_id)
        if period:
            query = query.filter(DepreciationSchedule.period == period)
        if is_posted is not None:
            query = query.filter(DepreciationSchedule.is_posted == (is_posted.lower() == 'true'))
        
        schedules = query.order_by(DepreciationSchedule.period.desc()).all()
        
        return jsonify([{
            'id': schedule.id,
            'asset_id': schedule.asset_id,
            'period': schedule.period,
            'depreciation_amount': schedule.depreciation_amount,
            'accumulated_depreciation': schedule.accumulated_depreciation,
            'book_value': schedule.book_value,
            'is_posted': schedule.is_posted,
            'posted_date': schedule.posted_date.isoformat() if schedule.posted_date else None,
            'created_at': schedule.created_at.isoformat() if schedule.created_at else None
        } for schedule in schedules]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/depreciation-schedules', methods=['POST'])
@require_permission('finance.assets.create')
def create_depreciation_schedule():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['asset_id', 'period', 'depreciation_amount', 'accumulated_depreciation', 'book_value']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        schedule = DepreciationSchedule(
            asset_id=data['asset_id'],
            period=data['period'],
            depreciation_amount=data['depreciation_amount'],
            accumulated_depreciation=data['accumulated_depreciation'],
            book_value=data['book_value'],
            is_posted=data.get('is_posted', False),
            posted_date=datetime.strptime(data['posted_date'], '%Y-%m-%d').date() if data.get('posted_date') else None
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('depreciation_schedules', schedule.id, 'create', new_values=data)
        
        return jsonify({
            'id': schedule.id,
            'asset_id': schedule.asset_id,
            'period': schedule.period,
            'message': 'Depreciation schedule created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Invoice Line Items Routes
@advanced_finance_bp.route('/invoice-line-items', methods=['GET'])
@require_permission('finance.invoices.read')
def get_invoice_line_items():
    try:
        # Get query parameters
        invoice_id = request.args.get('invoice_id')
        invoice_type = request.args.get('invoice_type')
        
        query = InvoiceLineItem.query
        
        if invoice_id:
            query = query.filter(InvoiceLineItem.invoice_id == invoice_id)
        if invoice_type:
            query = query.filter(InvoiceLineItem.invoice_type == invoice_type)
        
        line_items = query.order_by(InvoiceLineItem.line_number.asc()).all()
        
        return jsonify([{
            'id': item.id,
            'invoice_id': item.invoice_id,
            'invoice_type': item.invoice_type,
            'line_number': item.line_number,
            'description': item.description,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'tax_rate': item.tax_rate,
            'tax_amount': item.tax_amount,
            'discount_rate': item.discount_rate,
            'discount_amount': item.discount_amount,
            'total_amount': item.total_amount,
            'account_id': item.account_id,
            'created_at': item.created_at.isoformat() if item.created_at else None
        } for item in line_items]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/invoice-line-items', methods=['POST'])
@require_permission('finance.invoices.create')
def create_invoice_line_item():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['invoice_id', 'invoice_type', 'line_number', 'description', 'unit_price', 'total_amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        line_item = InvoiceLineItem(
            invoice_id=data['invoice_id'],
            invoice_type=data['invoice_type'],
            line_number=data['line_number'],
            description=data['description'],
            quantity=data.get('quantity', 1.0),
            unit_price=data['unit_price'],
            tax_rate=data.get('tax_rate', 0.0),
            tax_amount=data.get('tax_amount', 0.0),
            discount_rate=data.get('discount_rate', 0.0),
            discount_amount=data.get('discount_amount', 0.0),
            total_amount=data['total_amount'],
            account_id=data.get('account_id')
        )
        
        db.session.add(line_item)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('invoice_line_items', line_item.id, 'create', new_values=data)
        
        return jsonify({
            'id': line_item.id,
            'invoice_id': line_item.invoice_id,
            'line_number': line_item.line_number,
            'message': 'Invoice line item created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Financial Periods Routes
@advanced_finance_bp.route('/financial-periods', methods=['GET'])
@require_permission('finance.settings.read')
def get_financial_periods():
    try:
        # Get query parameters
        is_open = request.args.get('is_open')
        is_closed = request.args.get('is_closed')
        
        query = FinancialPeriod.query
        
        if is_open is not None:
            query = query.filter(FinancialPeriod.is_open == (is_open.lower() == 'true'))
        if is_closed is not None:
            query = query.filter(FinancialPeriod.is_closed == (is_closed.lower() == 'true'))
        
        periods = query.order_by(FinancialPeriod.start_date.desc()).all()
        
        return jsonify([{
            'id': period.id,
            'period_code': period.period_code,
            'period_name': period.period_name,
            'start_date': period.start_date.isoformat() if period.start_date else None,
            'end_date': period.end_date.isoformat() if period.end_date else None,
            'is_open': period.is_open,
            'is_closed': period.is_closed,
            'closed_by': period.closed_by,
            'closed_at': period.closed_at.isoformat() if period.closed_at else None,
            'created_at': period.created_at.isoformat() if period.created_at else None
        } for period in periods]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/financial-periods', methods=['POST'])
@require_permission('finance.settings.create')
def create_financial_period():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['period_code', 'period_name', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if period code already exists
        existing_period = FinancialPeriod.query.filter_by(period_code=data['period_code']).first()
        if existing_period:
            return jsonify({'error': 'Period code already exists'}), 400
        
        period = FinancialPeriod(
            period_code=data['period_code'],
            period_name=data['period_name'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            is_open=data.get('is_open', True),
            is_closed=data.get('is_closed', False)
        )
        
        db.session.add(period)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('financial_periods', period.id, 'create', new_values=data)
        
        return jsonify({
            'id': period.id,
            'period_code': period.period_code,
            'message': 'Financial period created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Tax Filing History Routes
@advanced_finance_bp.route('/tax-filing-history', methods=['GET'])
@require_permission('finance.tax.read')
def get_tax_filing_history():
    try:
        # Get query parameters
        tax_type = request.args.get('tax_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = TaxFilingHistory.query
        
        if tax_type:
            query = query.filter(TaxFilingHistory.tax_type == tax_type)
        if status:
            query = query.filter(TaxFilingHistory.status == status)
        if start_date:
            query = query.filter(TaxFilingHistory.filing_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(TaxFilingHistory.filing_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        filings = query.order_by(TaxFilingHistory.filing_date.desc()).all()
        
        return jsonify([{
            'id': filing.id,
            'tax_type': filing.tax_type,
            'filing_period': filing.filing_period,
            'filing_date': filing.filing_date.isoformat() if filing.filing_date else None,
            'due_date': filing.due_date.isoformat() if filing.due_date else None,
            'amount': filing.amount,
            'reference_number': filing.reference_number,
            'status': filing.status,
            'jurisdiction': filing.jurisdiction,
            'filing_method': filing.filing_method,
            'confirmation_number': filing.confirmation_number,
            'notes': filing.notes,
            'created_at': filing.created_at.isoformat() if filing.created_at else None
        } for filing in filings]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/tax-filing-history', methods=['POST'])
@require_permission('finance.tax.create')
def create_tax_filing():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['tax_type', 'filing_period', 'filing_date', 'due_date', 'amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        filing = TaxFilingHistory(
            tax_type=data['tax_type'],
            filing_period=data['filing_period'],
            filing_date=datetime.strptime(data['filing_date'], '%Y-%m-%d').date(),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            amount=data['amount'],
            reference_number=data.get('reference_number'),
            status=data.get('status', 'pending'),
            jurisdiction=data.get('jurisdiction'),
            filing_method=data.get('filing_method'),
            confirmation_number=data.get('confirmation_number'),
            notes=data.get('notes')
        )
        
        db.session.add(filing)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('tax_filing_history', filing.id, 'create', new_values=data)
        
        return jsonify({
            'id': filing.id,
            'tax_type': filing.tax_type,
            'filing_period': filing.filing_period,
            'message': 'Tax filing created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Compliance Reports Routes
@advanced_finance_bp.route('/compliance-reports', methods=['GET'])
@require_permission('finance.reports.read')
def get_compliance_reports():
    try:
        # Get query parameters
        report_type = request.args.get('report_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = ComplianceReport.query
        
        if report_type:
            query = query.filter(ComplianceReport.report_type == report_type)
        if status:
            query = query.filter(ComplianceReport.status == status)
        if start_date:
            query = query.filter(ComplianceReport.report_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(ComplianceReport.report_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        reports = query.order_by(ComplianceReport.report_date.desc()).all()
        
        return jsonify([{
            'id': report.id,
            'report_type': report.report_type,
            'report_period': report.report_period,
            'report_date': report.report_date.isoformat() if report.report_date else None,
            'status': report.status,
            'compliance_score': report.compliance_score,
            'total_checks': report.total_checks,
            'passed_checks': report.passed_checks,
            'failed_checks': report.failed_checks,
            'description': report.description,
            'findings': report.findings,
            'recommendations': report.recommendations,
            'auditor': report.auditor,
            'next_review_date': report.next_review_date.isoformat() if report.next_review_date else None,
            'created_at': report.created_at.isoformat() if report.created_at else None
        } for report in reports]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/compliance-reports', methods=['POST'])
@require_permission('finance.reports.create')
def create_compliance_report():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['report_type', 'report_period', 'report_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        report = ComplianceReport(
            report_type=data['report_type'],
            report_period=data['report_period'],
            report_date=datetime.strptime(data['report_date'], '%Y-%m-%d').date(),
            status=data.get('status', 'pending'),
            compliance_score=data.get('compliance_score', 0.0),
            total_checks=data.get('total_checks', 0),
            passed_checks=data.get('passed_checks', 0),
            failed_checks=data.get('failed_checks', 0),
            description=data.get('description'),
            findings=data.get('findings'),
            recommendations=data.get('recommendations'),
            auditor=data.get('auditor'),
            next_review_date=datetime.strptime(data['next_review_date'], '%Y-%m-%d').date() if data.get('next_review_date') else None
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('compliance_reports', report.id, 'create', new_values=data)
        
        return jsonify({
            'id': report.id,
            'report_type': report.report_type,
            'report_period': report.report_period,
            'message': 'Compliance report created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Activity Routes
@advanced_finance_bp.route('/user-activity', methods=['GET'])
@require_permission('finance.audit.read')
def get_user_activity():
    try:
        # Get query parameters
        user_name = request.args.get('user_name')
        action_type = request.args.get('action_type')
        module = request.args.get('module')
        status = request.args.get('status')
        
        query = UserActivity.query
        
        if user_name:
            query = query.filter(UserActivity.user_name == user_name)
        if action_type:
            query = query.filter(UserActivity.action_type == action_type)
        if module:
            query = query.filter(UserActivity.module == module)
        if status:
            query = query.filter(UserActivity.status == status)
        
        activities = query.order_by(UserActivity.last_activity.desc()).all()
        
        return jsonify([{
            'id': activity.id,
            'user_name': activity.user_name,
            'user_id': activity.user_id,
            'action_type': activity.action_type,
            'module': activity.module,
            'record_id': activity.record_id,
            'record_type': activity.record_type,
            'description': activity.description,
            'ip_address': activity.ip_address,
            'user_agent': activity.user_agent,
            'session_id': activity.session_id,
            'last_activity': activity.last_activity.isoformat() if activity.last_activity else None,
            'action_count': activity.action_count,
            'status': activity.status,
            'created_at': activity.created_at.isoformat() if activity.created_at else None
        } for activity in activities]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/user-activity', methods=['POST'])
@require_permission('finance.audit.create')
def create_user_activity():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_name', 'action_type', 'module']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        activity = UserActivity(
            user_name=data['user_name'],
            user_id=data.get('user_id'),
            action_type=data['action_type'],
            module=data['module'],
            record_id=data.get('record_id'),
            record_type=data.get('record_type'),
            description=data.get('description'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            session_id=data.get('session_id'),
            action_count=data.get('action_count', 1),
            status=data.get('status', 'active')
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'id': activity.id,
            'user_name': activity.user_name,
            'action_type': activity.action_type,
            'message': 'User activity recorded successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Compliance Audit Routes (alias for compliance-reports)
@advanced_finance_bp.route('/compliance-audit', methods=['GET'])
@require_permission('finance.reconciliation.read')
def get_compliance_audit():
    return get_compliance_reports()

# Bank Statements Routes
@advanced_finance_bp.route('/bank-statements', methods=['GET'])
@require_permission('finance.reconciliation.read')
def get_bank_statements():
    try:
        # Get query parameters
        bank_account = request.args.get('bank_account')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        is_reconciled = request.args.get('is_reconciled')
        
        query = BankStatement.query
        
        if bank_account:
            query = query.filter(BankStatement.bank_account == bank_account)
        if start_date:
            query = query.filter(BankStatement.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(BankStatement.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        if is_reconciled is not None:
            query = query.filter(BankStatement.is_reconciled == (is_reconciled.lower() == 'true'))
        
        statements = query.order_by(BankStatement.transaction_date.desc()).all()
        
        return jsonify([{
            'id': statement.id,
            'bank_account': statement.bank_account,
            'statement_date': statement.statement_date.isoformat() if statement.statement_date else None,
            'transaction_date': statement.transaction_date.isoformat() if statement.transaction_date else None,
            'description': statement.description,
            'reference': statement.reference,
            'debit_amount': statement.debit_amount,
            'credit_amount': statement.credit_amount,
            'balance': statement.balance,
            'transaction_type': statement.transaction_type,
            'category': statement.category,
            'is_reconciled': statement.is_reconciled,
            'reconciled_date': statement.reconciled_date.isoformat() if statement.reconciled_date else None,
            'reconciled_by': statement.reconciled_by,
            'notes': statement.notes,
            'created_at': statement.created_at.isoformat() if statement.created_at else None
        } for statement in statements]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/bank-statements', methods=['POST'])
@require_permission('finance.reconciliation.create')
def create_bank_statement():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['bank_account', 'statement_date', 'transaction_date', 'description', 'balance']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        statement = BankStatement(
            bank_account=data['bank_account'],
            statement_date=datetime.strptime(data['statement_date'], '%Y-%m-%d').date(),
            transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d').date(),
            description=data['description'],
            reference=data.get('reference'),
            debit_amount=data.get('debit_amount', 0.0),
            credit_amount=data.get('credit_amount', 0.0),
            balance=data['balance'],
            transaction_type=data.get('transaction_type'),
            category=data.get('category'),
            is_reconciled=data.get('is_reconciled', False),
            notes=data.get('notes')
        )
        
        db.session.add(statement)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('bank_statements', statement.id, 'create', new_values=data)
        
        return jsonify({
            'id': statement.id,
            'bank_account': statement.bank_account,
            'transaction_date': statement.transaction_date.isoformat(),
            'message': 'Bank statement created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ledger Entries Routes (alias for general-ledger)
@advanced_finance_bp.route('/ledger-entries', methods=['GET'])
@require_permission('finance.reports.read')
def get_ledger_entries():
    return get_general_ledger()

# Financial Reports Routes
@advanced_finance_bp.route('/profit-loss', methods=['GET'])
@require_permission('finance.reports.read')
def get_profit_loss():
    try:
        # Get query parameters
        period = request.args.get('period', datetime.now().strftime('%Y-%m'))
        
        # Calculate profit and loss from general ledger
        revenue_accounts = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Revenue',
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        expense_accounts = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Expense',
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        total_revenue = sum(entry.credit_amount for entry in revenue_accounts)
        total_expenses = sum(entry.debit_amount for entry in expense_accounts)
        net_income = total_revenue - total_expenses
        
        return jsonify({
            'period': period,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'gross_margin': (net_income / total_revenue * 100) if total_revenue > 0 else 0,
            'revenue_breakdown': [
                {
                    'account_name': entry.account.account_name,
                    'amount': entry.credit_amount
                } for entry in revenue_accounts
            ],
            'expense_breakdown': [
                {
                    'account_name': entry.account.account_name,
                    'amount': entry.debit_amount
                } for entry in expense_accounts
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/balance-sheet', methods=['GET'])
@require_permission('finance.reports.read')
def get_balance_sheet():
    try:
        # Get query parameters
        period = request.args.get('period', datetime.now().strftime('%Y-%m'))
        
        # Calculate balance sheet from general ledger
        assets = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Asset',
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        liabilities = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Liability',
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        equity = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Equity',
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        total_assets = sum(entry.debit_amount - entry.credit_amount for entry in assets)
        total_liabilities = sum(entry.credit_amount - entry.debit_amount for entry in liabilities)
        total_equity = sum(entry.credit_amount - entry.debit_amount for entry in equity)
        
        return jsonify({
            'period': period,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'assets': [
                {
                    'account_name': entry.account.account_name,
                    'balance': entry.debit_amount - entry.credit_amount
                } for entry in assets
            ],
            'liabilities': [
                {
                    'account_name': entry.account.account_name,
                    'balance': entry.credit_amount - entry.debit_amount
                } for entry in liabilities
            ],
            'equity': [
                {
                    'account_name': entry.account.account_name,
                    'balance': entry.credit_amount - entry.debit_amount
                } for entry in equity
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/cash-flow', methods=['GET'])
@require_permission('finance.reports.read')
def get_cash_flow():
    try:
        # Get query parameters
        period = request.args.get('period', datetime.now().strftime('%Y-%m'))
        
        # Calculate cash flow from general ledger
        operating_activities = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_category.in_(['Current Assets', 'Current Liabilities']),
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        investing_activities = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_category == 'Fixed Assets',
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        financing_activities = GeneralLedgerEntry.query.join(ChartOfAccounts).filter(
            ChartOfAccounts.account_category == 'Shareholders Equity',
            GeneralLedgerEntry.fiscal_period == period
        ).all()
        
        operating_cash_flow = sum(entry.credit_amount - entry.debit_amount for entry in operating_activities)
        investing_cash_flow = sum(entry.credit_amount - entry.debit_amount for entry in investing_activities)
        financing_cash_flow = sum(entry.credit_amount - entry.debit_amount for entry in financing_activities)
        net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        return jsonify({
            'period': period,
            'operating_cash_flow': operating_cash_flow,
            'investing_cash_flow': investing_cash_flow,
            'financing_cash_flow': financing_cash_flow,
            'net_cash_flow': net_cash_flow,
            'operating_activities': [
                {
                    'account_name': entry.account.account_name,
                    'amount': entry.credit_amount - entry.debit_amount
                } for entry in operating_activities
            ],
            'investing_activities': [
                {
                    'account_name': entry.account.account_name,
                    'amount': entry.credit_amount - entry.debit_amount
                } for entry in investing_activities
            ],
            'financing_activities': [
                {
                    'account_name': entry.account.account_name,
                    'amount': entry.credit_amount - entry.debit_amount
                } for entry in financing_activities
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# KPIs Routes
@advanced_finance_bp.route('/kpis', methods=['GET'])
@require_permission('inventory.reports.read')
def get_kpis():
    try:
        # Get query parameters
        category = request.args.get('category')
        status = request.args.get('status')
        
        query = KPI.query
        
        if category:
            query = query.filter(KPI.kpi_category == category)
        if status:
            query = query.filter(KPI.status == status)
        
        kpis = query.order_by(KPI.kpi_name).all()
        
        return jsonify([{
            'id': kpi.id,
            'kpi_code': kpi.kpi_code,
            'kpi_name': kpi.kpi_name,
            'kpi_category': kpi.kpi_category,
            'description': kpi.description,
            'calculation_formula': kpi.calculation_formula,
            'target_value': kpi.target_value,
            'current_value': kpi.current_value,
            'previous_value': kpi.previous_value,
            'unit': kpi.unit,
            'frequency': kpi.frequency,
            'trend': kpi.trend,
            'status': kpi.status,
            'last_updated': kpi.last_updated.isoformat() if kpi.last_updated else None,
            'created_at': kpi.created_at.isoformat() if kpi.created_at else None
        } for kpi in kpis]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/kpis', methods=['POST'])
@require_permission('finance.reports.create')
def create_kpi():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['kpi_code', 'kpi_name', 'kpi_category']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if KPI code already exists
        existing_kpi = KPI.query.filter_by(kpi_code=data['kpi_code']).first()
        if existing_kpi:
            return jsonify({'error': 'KPI code already exists'}), 400
        
        kpi = KPI(
            kpi_code=data['kpi_code'],
            kpi_name=data['kpi_name'],
            kpi_category=data['kpi_category'],
            description=data.get('description'),
            calculation_formula=data.get('calculation_formula'),
            target_value=data.get('target_value'),
            current_value=data.get('current_value', 0.0),
            previous_value=data.get('previous_value', 0.0),
            unit=data.get('unit'),
            frequency=data.get('frequency', 'monthly'),
            trend=data.get('trend'),
            status=data.get('status', 'active')
        )
        
        db.session.add(kpi)
        db.session.commit()
        
        # Create audit trail
        create_audit_trail('kpis', kpi.id, 'create', new_values=data)
        
        return jsonify({
            'id': kpi.id,
            'kpi_code': kpi.kpi_code,
            'kpi_name': kpi.kpi_name,
            'message': 'KPI created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# AI Analytics Routes
@advanced_finance_bp.route('/ai/insights', methods=['GET'])
@require_permission('finance.reports.read')
def get_ai_insights():
    """Get AI-powered financial insights"""
    try:
        analysis_type = request.args.get('type', 'general')
        insights = AIAnalyticsService.get_financial_insights(analysis_type)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/ai/inventory-insights', methods=['GET'])
@require_permission('finance.reports.read')
def get_inventory_insights():
    """Get AI-powered inventory insights"""
    try:
        insights = AIAnalyticsService.get_inventory_insights()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/ai/market-trends', methods=['GET'])
@require_permission('finance.reports.read')
def get_market_trends():
    """Get AI-powered market trend analysis"""
    try:
        currency = request.args.get('currency', 'USD')
        trends = AIAnalyticsService.get_market_trends(currency)
        return jsonify(trends), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CURRENCY SETTINGS ROUTES
# ============================================================================

@advanced_finance_bp.route('/settings/base-currency', methods=['GET'])
@require_permission('finance.settings.read')
def get_base_currency():
    """Get current base currency setting"""
    try:
        # Force a fresh session to avoid any caching issues
        db.session.close()
        
        # Get base currency from CompanySettings with fresh query
        settings = CompanySettings.query.filter_by(setting_key='base_currency').first()
        print(f"GET endpoint - Found settings: {settings.setting_value if settings else 'None'}")
        
        if settings:
            return jsonify({
                'status': 'success',
                'base_currency': settings.setting_value,
                'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
            }), 200
        else:
            # No settings exist - return empty (no defaults)
            return jsonify({
                'status': 'success',
                'base_currency': None,
                'updated_at': None
            }), 200
    except Exception as e:
        print(f"Error in get_base_currency: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/settings/debug', methods=['GET'])
@require_permission('finance.settings.read')
def debug_settings():
    """Debug endpoint to check all settings in database"""
    try:
        all_settings = CompanySettings.query.all()
        settings_list = []
        for setting in all_settings:
            if setting:  # Check if setting is not None
                settings_list.append({
                    'id': setting.id,
                    'key': setting.setting_key,
                    'value': setting.setting_value,
                    'type': setting.setting_type,
                    'created_at': setting.created_at.isoformat() if setting.created_at else None,
                    'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
                })
            else:
                settings_list.append({
                    'id': 'None',
                    'key': 'None',
                    'value': 'None',
                    'type': 'None',
                    'created_at': None,
                    'updated_at': None
                })
        
        return jsonify({
            'status': 'success',
            'total_settings': len(settings_list),
            'settings': settings_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/settings/cleanup', methods=['POST'])
@require_permission('finance.settings.update')
def cleanup_settings():
    """Clean up corrupted settings and create fresh base currency"""
    try:
        # Delete all existing settings
        CompanySettings.query.delete()
        db.session.commit()
        
        # Create fresh base currency setting
        settings = CompanySettings(
            setting_key='base_currency',
            setting_value='USD',
            setting_type='string',
            description='Base currency for the company'
        )
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Settings cleaned up and fresh base currency created',
            'base_currency': 'USD'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/settings/base-currency', methods=['POST'])
@require_permission('finance.settings.update')
def set_base_currency():
    """Set base currency setting"""
    try:
        data = request.get_json()
        new_currency = data.get('base_currency')
        
        if not new_currency:
            return jsonify({'error': 'base_currency is required'}), 400
        
        # Force a fresh session to avoid any caching issues
        db.session.close()
        
        # Use explicit transaction with proper isolation
        try:
            # First, delete any existing base_currency setting
            CompanySettings.query.filter_by(setting_key='base_currency').delete()
            db.session.commit()
            
            # Now create a new setting
            settings = CompanySettings(
                setting_key='base_currency',
                setting_value=new_currency,
                setting_type='string',
                description='Base currency for the company'
            )
            
            db.session.add(settings)
            db.session.commit()
            
            # Force a flush to ensure data is written
            db.session.flush()
            
            print(f"Successfully set base currency to: {new_currency}")
            
            return jsonify({
                'status': 'success',
                'message': f'Base currency updated to {new_currency}',
                'base_currency': new_currency
            }), 200
            
        except Exception as e:
            db.session.rollback()
            raise e
            
    except Exception as e:
        print(f"Error in set_base_currency: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/currency/convert-all', methods=['POST'])
@require_permission('currency.convert-all.create')
def convert_all_currencies():
    """Convert all existing data to new base currency"""
    try:
        data = request.get_json()
        new_base_currency = data.get('new_base_currency')
        
        if not new_base_currency:
            return jsonify({'error': 'new_base_currency is required'}), 400
        
        # Initialize valuation engine
        valuation_engine = MultiCurrencyValuationEngine()
        
        # Convert all existing data
        result = valuation_engine.convert_all_to_new_currency(new_base_currency)
        
        return jsonify({
            'status': 'success',
            'message': f'All data converted to {new_base_currency}',
            'converted_records': result.get('converted_records', 0),
            'new_base_currency': new_base_currency
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# WORKFLOW ROUTES
# ============================================================================

@advanced_finance_bp.route('/workflows/alerts/low-stock', methods=['GET'])
@require_permission('finance.workflows.read')
def get_low_stock_alerts():
    """Get low stock alerts"""
    try:
        alerts = WorkflowService.check_low_stock_alerts()
        return jsonify({
            'status': 'success',
            'alerts': alerts,
            'count': len(alerts)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/alerts/overstock', methods=['GET'])
@require_permission('finance.workflows.read')
def get_overstock_alerts():
    """Get overstock alerts"""
    try:
        alerts = WorkflowService.check_overstock_alerts()
        return jsonify({
            'status': 'success',
            'alerts': alerts,
            'count': len(alerts)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/alerts/budget', methods=['POST'])
@require_permission('finance.workflows.create')
def check_budget_alerts():
    """Check budget exceeded alerts"""
    try:
        data = request.get_json()
        budget_limits = data.get('budget_limits', {})
        alerts = WorkflowService.check_budget_alerts(budget_limits)
        return jsonify({
            'status': 'success',
            'alerts': alerts,
            'count': len(alerts)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/alerts/payment-due', methods=['GET'])
@require_permission('finance.workflows.read')
def get_payment_due_alerts():
    """Get payment due alerts"""
    try:
        days_threshold = int(request.args.get('days', 30))
        alerts = WorkflowService.check_payment_due_alerts(days_threshold)
        return jsonify({
            'status': 'success',
            'alerts': alerts,
            'count': len(alerts)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/reports/daily', methods=['GET'])
@require_permission('finance.workflows.read')
def get_daily_report():
    """Get daily automated report"""
    try:
        report = WorkflowService.generate_daily_reports()
        return jsonify({
            'status': 'success',
            'report': report
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/approval', methods=['POST'])
@require_permission('finance.workflows.create')
def create_approval_workflow():
    """Create an approval workflow"""
    try:
        data = request.get_json()
        workflow_type = data.get('type')
        workflow_data = data.get('data', {})
        
        workflow = WorkflowService.create_approval_workflow(workflow_type, workflow_data)
        return jsonify({
            'status': 'success',
            'workflow': workflow
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/approval/<workflow_id>', methods=['POST'])
@require_permission('finance.workflows.create')
def process_approval(workflow_id):
    """Process an approval decision"""
    try:
        data = request.get_json()
        approver = data.get('approver')
        approved = data.get('approved', False)
        comments = data.get('comments', '')
        
        result = WorkflowService.process_approval(workflow_id, approver, approved, comments)
        return jsonify({
            'status': 'success',
            'result': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/approval/<workflow_id>/status', methods=['GET'])
@require_permission('finance.workflows.read')
def get_workflow_status(workflow_id):
    """Get workflow status"""
    try:
        status = WorkflowService.get_workflow_status(workflow_id)
        return jsonify({
            'status': 'success',
            'workflow_status': status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/schedule', methods=['POST'])
@require_permission('finance.workflows.create')
def schedule_task():
    """Schedule a recurring task"""
    try:
        data = request.get_json()
        task_type = data.get('type')
        schedule = data.get('schedule', {})
        task_data = data.get('data', {})
        
        task = WorkflowService.schedule_task(task_type, schedule, task_data)
        return jsonify({
            'status': 'success',
            'task': task
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_finance_bp.route('/workflows/run-scheduled', methods=['POST'])
@require_permission('finance.workflows.create')
def run_scheduled_tasks():
    """Run all scheduled tasks that are due"""
    try:
        results = WorkflowService.run_scheduled_tasks()
        return jsonify({
            'status': 'success',
            'results': results,
            'executed_count': len(results)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# General Finance Summary Endpoint
@advanced_finance_bp.route('/summary', methods=['GET'])
@require_permission('finance.reports.read')
def get_finance_summary():
    """Get overall finance summary for dashboard"""
    try:
        # Get summary data from various sources
        from .models import Account, JournalEntry, Invoice, Payment
        
        # Count accounts
        total_accounts = Account.query.count()
        active_accounts = Account.query.filter_by(is_active=True).count()
        
        # Count journal entries
        total_entries = JournalEntry.query.count()
        posted_entries = JournalEntry.query.filter_by(status='posted').count()
        
        # Count invoices
        total_invoices = Invoice.query.count()
        paid_invoices = Invoice.query.filter_by(status='paid').count()
        
        # Calculate total balances
        total_balance = db.session.query(func.sum(Account.balance)).scalar() or 0.0
        
        # Get recent activity
        recent_entries = JournalEntry.query.order_by(JournalEntry.created_at.desc()).limit(5).all()
        recent_activity = [{
            'id': entry.id,
            'reference': entry.reference,
            'description': entry.description,
            'status': entry.status,
            'created_at': entry.created_at.isoformat() if entry.created_at else None
        } for entry in recent_entries]
        
        return jsonify({
            'status': 'success',
            'summary': {
                'accounts': {
                    'total': total_accounts,
                    'active': active_accounts
                },
                'journal_entries': {
                    'total': total_entries,
                    'posted': posted_entries
                },
                'invoices': {
                    'total': total_invoices,
                    'paid': paid_invoices
                },
                'total_balance': float(total_balance),
                'recent_activity': recent_activity
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Financial Reports Endpoint
@advanced_finance_bp.route('/financial-reports', methods=['GET'])
@require_permission('finance.reports.read')
def get_financial_reports():
    """Get available financial reports"""
    try:
        # Return list of available reports
        available_reports = [
            {
                'id': 'profit_loss',
                'name': 'Profit & Loss Statement',
                'description': 'Shows revenue, expenses, and net income',
                'endpoint': '/api/finance/reports/profit-loss',
                'available': True
            },
            {
                'id': 'balance_sheet',
                'name': 'Balance Sheet',
                'description': 'Shows assets, liabilities, and equity',
                'endpoint': '/api/finance/reports/balance-sheet',
                'available': True
            },
            {
                'id': 'cash_flow',
                'name': 'Cash Flow Statement',
                'description': 'Shows cash inflows and outflows',
                'endpoint': '/api/finance/reports/cash-flow',
                'available': True
            },
            {
                'id': 'trial_balance',
                'name': 'Trial Balance',
                'description': 'Shows all account balances',
                'endpoint': '/api/finance/reports/trial-balance',
                'available': False
            },
            {
                'id': 'aged_receivables',
                'name': 'Aged Receivables Report',
                'description': 'Shows outstanding receivables by age',
                'endpoint': '/api/finance/reports/aged-receivables',
                'available': False
            }
        ]
        
        return jsonify({
            'status': 'success',
            'reports': available_reports,
            'total_available': len([r for r in available_reports if r['available']])
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
