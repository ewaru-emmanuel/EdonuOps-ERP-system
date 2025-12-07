from flask import Blueprint, request, jsonify
from datetime import datetime, date
import logging
from app import db
from modules.sales.models import Customer, Invoice, Payment, CustomerCommunication
from app.audit_logger import AuditLogger, AuditAction
from sqlalchemy import or_ as sa_or_
from modules.core.permissions import require_permission, require_module_access

# Import auto-journal engine for AR integration
try:
    from modules.integration.auto_journal import auto_journal_engine as _auto_journal_engine
except Exception:
    _auto_journal_engine = None

bp = Blueprint('sales', __name__, url_prefix='/api/sales')
logger = logging.getLogger(__name__)

# Helper function to serialize customer data
def _serialize_customer(customer):
    """Serialize customer object to dictionary"""
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "company_name": customer.company_name,
        "tax_id": customer.tax_id,
        "credit_limit": customer.credit_limit,
        "payment_terms": customer.payment_terms,
        "is_active": customer.is_active,
        "customer_type": customer.customer_type,
        "category": customer.category,
        "region": customer.region,
        "total_sales": customer.total_sales,
        "outstanding_balance": customer.outstanding_balance,
        "overdue_amount": customer.overdue_amount,
        "current_amount": customer.current_amount,
        "last_payment_date": customer.last_payment_date.isoformat() if customer.last_payment_date else None,
        "average_payment_days": customer.average_payment_days,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
        "created_by": customer.created_by
    }

def _serialize_invoice(invoice):
    """Serialize invoice object to dictionary"""
    return {
        "id": invoice.id,
        "customer_id": invoice.customer_id,
        "customer_name": invoice.customer.name if invoice.customer else None,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "discount_amount": invoice.discount_amount,
        "total_amount": invoice.total_amount,
        "paid_amount": invoice.paid_amount,
        "outstanding_amount": invoice.outstanding_amount,
        "status": invoice.status,
        "payment_method": invoice.payment_method,
        "description": invoice.description,
        "notes": invoice.notes,
        "po_reference": invoice.po_reference,
        "project_id": invoice.project_id,
        "is_overdue": invoice.is_overdue,
        "days_overdue": invoice.days_overdue,
        "aging_bucket": invoice.aging_bucket,
        "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
        "updated_at": invoice.updated_at.isoformat() if invoice.updated_at else None,
        "created_by": invoice.created_by
    }

# Customer endpoints
@bp.route('/customers', methods=['GET'])
@require_permission('sales.customers.read')
def get_customers():
    """Get customers with optional filters and search"""
    try:
        # Get query parameters
        search = request.args.get('search', '').strip()
        customer_type = request.args.get('type')
        region = request.args.get('region')
        is_active = request.args.get('active')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Build query
        query = Customer.query
        
        # Apply filters
        if search:
            search_filter = sa_or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.company_name.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)
        
        if region:
            query = query.filter(Customer.region == region)
            
        if is_active is not None:
            active_bool = is_active.lower() in ['true', '1', 'yes']
            query = query.filter(Customer.is_active == active_bool)
        
        # Get paginated results
        customers = query.order_by(Customer.name.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "customers": [_serialize_customer(c) for c in customers.items],
            "pagination": {
                "page": customers.page,
                "pages": customers.pages,
                "per_page": customers.per_page,
                "total": customers.total,
                "has_next": customers.has_next,
                "has_prev": customers.has_prev
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        return jsonify({"error": f"Failed to fetch customers: {str(e)}"}), 500

@bp.route('/customers', methods=['POST'])
@require_permission('sales.customers.create')
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json() or {}
        customer = Customer(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            company_name=data.get('company_name'),
            tax_id=data.get('tax_id'),
            credit_limit=float(data.get('credit_limit') or 0.0),
            payment_terms=data.get('payment_terms') or 'Net 30',
            is_active=bool(data.get('is_active') if data.get('is_active') is not None else True),
            customer_type=data.get('customer_type') or 'regular',
            category=data.get('category'),
            region=data.get('region'),
            created_by=data.get('created_by')
        )
        db.session.add(customer)
        db.session.commit()
        
        try:
            AuditLogger.log(
                user_id=(data.get('created_by') or 'system'),
                action=AuditAction.CREATE,
                entity_type='customer',
                entity_id=str(customer.id),
                new_values=_serialize_customer(customer)
            )
        except Exception:
            pass
            
        return jsonify(_serialize_customer(customer)), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating customer: {str(e)}")
        return jsonify({"error": f"Failed to create customer: {str(e)}"}), 500

@bp.route('/customers/<int:customer_id>', methods=['GET'])
@require_permission('sales.customers.read')
def get_customer(customer_id: int):
    """Get a specific customer"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(_serialize_customer(customer)), 200

@bp.route('/customers/<int:customer_id>', methods=['PUT'])
@require_permission('sales.customers.update')
def update_customer(customer_id: int):
    """Update a customer"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        data = request.get_json() or {}
        old_values = _serialize_customer(customer)
        
        # Update fields
        if 'name' in data:
            customer.name = data['name']
        if 'email' in data:
            customer.email = data['email']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'address' in data:
            customer.address = data['address']
        if 'company_name' in data:
            customer.company_name = data['company_name']
        if 'tax_id' in data:
            customer.tax_id = data['tax_id']
        if 'credit_limit' in data:
            customer.credit_limit = float(data['credit_limit'])
        if 'payment_terms' in data:
            customer.payment_terms = data['payment_terms']
        if 'is_active' in data:
            customer.is_active = bool(data['is_active'])
        if 'customer_type' in data:
            customer.customer_type = data['customer_type']
        if 'category' in data:
            customer.category = data['category']
        if 'region' in data:
            customer.region = data['region']
        
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        
        try:
            AuditLogger.log(
                user_id=(data.get('updated_by') or 'system'),
                action=AuditAction.UPDATE,
                entity_type='customer',
                entity_id=str(customer.id),
                old_values=old_values,
                new_values=_serialize_customer(customer)
            )
        except Exception:
            pass
            
        return jsonify(_serialize_customer(customer)), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating customer: {str(e)}")
        return jsonify({"error": f"Failed to update customer: {str(e)}"}), 500

# Invoice endpoints
@bp.route('/invoices', methods=['GET'])
@require_permission('sales.invoices.read')
def get_invoices():
    """Get invoices with optional filters"""
    try:
        # Get query parameters
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        overdue_only = request.args.get('overdue', 'false').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Build query
        query = Invoice.query
        
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        if status:
            query = query.filter(Invoice.status == status)
        if overdue_only:
            query = query.filter(Invoice.due_date < date.today(), Invoice.status != 'paid')
        
        # Get paginated results
        invoices = query.order_by(Invoice.invoice_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "invoices": [_serialize_invoice(inv) for inv in invoices.items],
            "pagination": {
                "page": invoices.page,
                "pages": invoices.pages,
                "per_page": invoices.per_page,
                "total": invoices.total,
                "has_next": invoices.has_next,
                "has_prev": invoices.has_prev
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching invoices: {str(e)}")
        return jsonify({"error": f"Failed to fetch invoices: {str(e)}"}), 500

@bp.route('/invoices', methods=['POST'])
@require_permission('sales.invoices.create')
def create_invoice():
    """Create a new invoice"""
    try:
        data = request.get_json() or {}
        
        # Calculate outstanding amount
        total_amount = float(data.get('total_amount', 0))
        paid_amount = float(data.get('paid_amount', 0))
        outstanding_amount = total_amount - paid_amount
        
        invoice = Invoice(
            customer_id=int(data.get('customer_id')),
            invoice_number=data.get('invoice_number'),
            invoice_date=datetime.strptime(data.get('invoice_date'), '%Y-%m-%d').date(),
            due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date(),
            subtotal=float(data.get('subtotal', 0)),
            tax_amount=float(data.get('tax_amount', 0)),
            discount_amount=float(data.get('discount_amount', 0)),
            total_amount=total_amount,
            paid_amount=paid_amount,
            outstanding_amount=outstanding_amount,
            status=data.get('status', 'pending'),
            payment_method=data.get('payment_method'),
            description=data.get('description'),
            notes=data.get('notes'),
            po_reference=data.get('po_reference'),
            project_id=data.get('project_id'),
            created_by=data.get('created_by')
        )
        db.session.add(invoice)
        db.session.flush()  # Get the ID
        
        # Update customer outstanding balance
        customer = Customer.query.get(invoice.customer_id)
        if customer:
            customer.outstanding_balance += outstanding_amount
            customer.total_sales += total_amount
        
        db.session.commit()
        
        # Auto-create journal entry for the invoice
        try:
            if _auto_journal_engine is not None:
                customer_name = customer.name if customer else f"Customer {invoice.customer_id}"
                
                invoice_result = _auto_journal_engine.on_customer_invoice_created({
                    'invoice_amount': total_amount,
                    'invoice_date': invoice.invoice_date,
                    'invoice_reference': invoice.invoice_number,
                    'customer_id': invoice.customer_id,
                    'customer_name': customer_name,
                    'description': invoice.description or f"Invoice {invoice.invoice_number}",
                    'invoice_id': invoice.id
                })
                
                if invoice_result.get('success'):
                    logger.info(f"Auto-journal entry created for Invoice {invoice.invoice_number}: {invoice_result.get('journal_entry_id')}")
        except Exception as e:
            logger.warning(f"Failed to create auto-journal entry for Invoice {invoice.invoice_number}: {str(e)}")
        
        try:
            AuditLogger.log(
                user_id=(data.get('created_by') or 'system'),
                action=AuditAction.CREATE,
                entity_type='invoice',
                entity_id=str(invoice.id),
                new_values=_serialize_invoice(invoice)
            )
        except Exception:
            pass
            
        return jsonify(_serialize_invoice(invoice)), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating invoice: {str(e)}")
        return jsonify({"error": f"Failed to create invoice: {str(e)}"}), 500

# Accounts Receivable summary endpoint
@bp.route('/accounts-receivable', methods=['GET'])
@require_permission('sales.invoices.read')
def get_accounts_receivable():
    """Get accounts receivable summary"""
    try:
        # Get all unpaid invoices
        unpaid_invoices = Invoice.query.filter(
            Invoice.status != 'paid',
            Invoice.outstanding_amount > 0
        ).all()
        
        # Calculate aging buckets
        aging_summary = {
            'current': 0,
            '1-30 days': 0,
            '31-60 days': 0,
            '61-90 days': 0,
            '90+ days': 0
        }
        
        total_outstanding = 0
        overdue_amount = 0
        
        ar_data = []
        for invoice in unpaid_invoices:
            total_outstanding += invoice.outstanding_amount
            aging_summary[invoice.aging_bucket] += invoice.outstanding_amount
            
            if invoice.is_overdue:
                overdue_amount += invoice.outstanding_amount
            
            ar_data.append({
                'invoice_id': invoice.id,
                'customer_id': invoice.customer_id,
                'customer_name': invoice.customer.name if invoice.customer else None,
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.invoice_date.isoformat(),
                'due_date': invoice.due_date.isoformat(),
                'outstanding_amount': invoice.outstanding_amount,
                'status': invoice.status,
                'is_overdue': invoice.is_overdue,
                'days_overdue': invoice.days_overdue,
                'aging_bucket': invoice.aging_bucket
            })
        
        return jsonify({
            'summary': {
                'total_outstanding': total_outstanding,
                'overdue_amount': overdue_amount,
                'current_amount': total_outstanding - overdue_amount,
                'total_invoices': len(unpaid_invoices)
            },
            'aging_summary': aging_summary,
            'invoices': ar_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching accounts receivable: {str(e)}")
        return jsonify({"error": f"Failed to fetch accounts receivable: {str(e)}"}), 500

