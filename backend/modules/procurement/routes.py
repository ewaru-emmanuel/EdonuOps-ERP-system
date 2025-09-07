# backend/modules/procurement/routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.procurement.models import (
    Vendor,
    PurchaseOrder,
    PurchaseOrderItem,
    POAttachment,
    VendorDocument,
    VendorCommunication,
    RFQ,
    RFQItem,
    RFQInvitation,
    RFQResponseHeader,
    RFQResponseItem,
    Contract,
    ContractDocument,
)
from modules.finance.models import Account
from app.audit_logger import AuditLogger, AuditAction
import os
from werkzeug.utils import secure_filename
try:
    # Optional finance auto-journaling
    from modules.integration.auto_journal import auto_journal_engine as _auto_journal_engine
except Exception:
    _auto_journal_engine = None

bp = Blueprint('procurement', __name__, url_prefix='/api/procurement')

# In-memory placeholder for POs until migrated fully to DB
purchase_orders = []

# Vendor endpoints
@bp.route('/vendors', methods=['GET'])
def get_vendors():
    """Get vendors with optional filters and search"""
    query = Vendor.query
    # Filters
    if request.args.get('category'):
        query = query.filter(Vendor.category == request.args.get('category'))
    if request.args.get('risk_level'):
        query = query.filter(Vendor.risk_level == request.args.get('risk_level'))
    if request.args.get('region'):
        query = query.filter(Vendor.region == request.args.get('region'))
    if request.args.get('is_preferred') is not None:
        val = request.args.get('is_preferred').lower() in ['1', 'true', 'yes']
        query = query.filter(Vendor.is_preferred == val)
    if request.args.get('is_active') is not None:
        val = request.args.get('is_active').lower() in ['1', 'true', 'yes']
        query = query.filter(Vendor.is_active == val)
    # Search
    q = request.args.get('q')
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Vendor.name.ilike(like), Vendor.email.ilike(like)))

    vendors = query.order_by(Vendor.name.asc()).all()
    return jsonify([_serialize_vendor(v) for v in vendors])

@bp.route('/vendors', methods=['POST'])
def create_vendor():
    """Create a new vendor"""
    data = request.get_json() or {}
    vendor = Vendor(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        tax_id=data.get('tax_id'),
        payment_terms=data.get('payment_terms') or 'Net 30',
        credit_limit=float(data.get('credit_limit') or 0.0),
        is_active=bool(data.get('is_active') if data.get('is_active') is not None else True),
        category=data.get('category'),
        risk_level=data.get('risk_level'),
        region=data.get('region'),
        is_preferred=bool(data.get('is_preferred') or False),
    )
    db.session.add(vendor)
    db.session.commit()
    try:
        AuditLogger.log(
            user_id=(data.get('created_by') or 'system'),
            action=AuditAction.CREATE,
            entity_type='vendor',
            entity_id=str(vendor.id),
            new_values=_serialize_vendor(vendor)
        )
    except Exception:
        pass
    return jsonify(_serialize_vendor(vendor)), 201

@bp.route('/vendors/<int:vendor_id>', methods=['GET'])
def get_vendor(vendor_id: int):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    return jsonify(_serialize_vendor(vendor))

@bp.route('/vendors/<int:vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    """Update a vendor"""
    data = request.get_json() or {}
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    before = _serialize_vendor(vendor)
    for field in [
        'name','email','phone','address','tax_id','payment_terms','category','risk_level','region'
    ]:
        if field in data:
            setattr(vendor, field, data.get(field))
    if 'credit_limit' in data:
        vendor.credit_limit = float(data.get('credit_limit') or 0.0)
    if 'is_active' in data:
        vendor.is_active = bool(data.get('is_active'))
    if 'is_preferred' in data:
        vendor.is_preferred = bool(data.get('is_preferred'))
    # Performance fields (optional in general update)
    for field in [
        'on_time_delivery_rate','price_variance_pct','quality_score','performance_notes','last_reviewed_at'
    ]:
        if field in data:
            setattr(vendor, field, data.get(field))
    db.session.commit()
    try:
        AuditLogger.log(
            user_id=(data.get('updated_by') or 'system'),
            action=AuditAction.UPDATE,
            entity_type='vendor',
            entity_id=str(vendor.id),
            old_values=before,
            new_values=_serialize_vendor(vendor)
        )
    except Exception:
        pass
    return jsonify(_serialize_vendor(vendor))

@bp.route('/vendors/<int:vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id: int):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    db.session.delete(vendor)
    db.session.commit()
    try:
        AuditLogger.log(
            user_id='system',
            action=AuditAction.DELETE,
            entity_type='vendor',
            entity_id=str(vendor_id)
        )
    except Exception:
        pass
    return jsonify({"message": "Vendor deleted"})

@bp.route('/vendors/<int:vendor_id>/performance', methods=['PUT'])
def update_vendor_performance(vendor_id: int):
    data = request.get_json() or {}
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    before = _serialize_vendor(vendor)
    for field in ['on_time_delivery_rate','price_variance_pct','quality_score','performance_notes']:
        if field in data:
            setattr(vendor, field, float(data.get(field)) if field != 'performance_notes' else data.get(field))
    vendor.last_reviewed_at = datetime.utcnow()
    db.session.commit()
    try:
        AuditLogger.log(
            user_id=(data.get('updated_by') or 'system'),
            action=AuditAction.UPDATE,
            entity_type='vendor_performance',
            entity_id=str(vendor.id),
            old_values=before,
            new_values=_serialize_vendor(vendor)
        )
    except Exception:
        pass
    return jsonify(_serialize_vendor(vendor))

@bp.route('/vendors/<int:vendor_id>/documents', methods=['GET'])
def list_vendor_documents(vendor_id: int):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    docs = VendorDocument.query.filter_by(vendor_id=vendor_id).order_by(VendorDocument.uploaded_at.desc()).all()
    return jsonify([_serialize_vendor_document(d) for d in docs])

@bp.route('/vendors/<int:vendor_id>/documents', methods=['POST'])
def upload_vendor_document(vendor_id: int):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_extension not in allowed_extensions:
        return jsonify({"error": "Invalid file type"}), 400
    filename = secure_filename(file.filename)
    file_path = f"uploads/vendor_docs/{vendor_id}_{int(datetime.utcnow().timestamp())}_{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    doc = VendorDocument(
        vendor_id=vendor_id,
        doc_type=request.form.get('doc_type'),
        filename=filename,
        file_path=file_path,
        file_type=file_extension,
        file_size=os.path.getsize(file_path),
        uploaded_by=(request.form.get('uploaded_by')),
        effective_date=_parse_date(request.form.get('effective_date')),
        expiry_date=_parse_date(request.form.get('expiry_date'))
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify(_serialize_vendor_document(doc)), 201

@bp.route('/vendors/<int:vendor_id>/documents/<int:doc_id>', methods=['DELETE'])
def delete_vendor_document(vendor_id: int, doc_id: int):
    doc = VendorDocument.query.filter_by(id=doc_id, vendor_id=vendor_id).first()
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception:
        pass
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"message": "Document deleted"})

@bp.route('/vendors/<int:vendor_id>/communications', methods=['GET'])
def list_vendor_communications(vendor_id: int):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    comms = VendorCommunication.query.filter_by(vendor_id=vendor_id).order_by(VendorCommunication.created_at.desc()).all()
    return jsonify([_serialize_vendor_communication(c) for c in comms])

@bp.route('/vendors/<int:vendor_id>/communications', methods=['POST'])
def create_vendor_communication(vendor_id: int):
    data = request.get_json() or {}
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404
    comm = VendorCommunication(
        vendor_id=vendor_id,
        channel=data.get('channel'),
        direction=data.get('direction'),
        subject=data.get('subject'),
        message=data.get('message'),
        related_rfx_id=data.get('related_rfx_id'),
        created_by=data.get('created_by')
    )
    db.session.add(comm)
    db.session.commit()
    try:
        AuditLogger.log(
            user_id=(data.get('created_by') or 'system'),
            action=AuditAction.CREATE,
            entity_type='vendor_communication',
            entity_id=str(comm.id),
            new_values=_serialize_vendor_communication(comm)
        )
    except Exception:
        pass
    return jsonify(_serialize_vendor_communication(comm)), 201

# Purchase Order endpoints
@bp.route('/purchase-orders', methods=['GET', 'OPTIONS'])
def get_purchase_orders():
    if request.method == 'OPTIONS':
        return ('', 200)
    """Get all purchase orders with filters"""
    vendor_id = request.args.get('vendor_id', type=int)
    status = request.args.get('status')
    
    filtered_pos = purchase_orders
    if vendor_id:
        filtered_pos = [po for po in filtered_pos if po.get('vendor_id') == vendor_id]
    if status:
        filtered_pos = [po for po in filtered_pos if po.get('status') == status]
    
    return jsonify(filtered_pos)

@bp.route('/purchase-orders', methods=['POST', 'OPTIONS'])
def create_purchase_order():
    if request.method == 'OPTIONS':
        return ('', 200)
    """Create a new purchase order"""
    data = request.get_json()
    
    # Generate PO number
    po_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{len(purchase_orders) + 1:03d}"
    
    # Currency and FX locking at PO header (can be overridden per line)
    po_currency = data.get('currency', 'USD')
    fx_rate = float(data.get('fx_rate') or 1.0)  # to base currency

    # Build items with currency context
    items_in = data.get('items', []) or []
    items = []
    total_foreign = 0.0
    total_base = 0.0
    for it in items_in:
        qty = float(it.get('quantity') or 0)
        unit_price_foreign = float(it.get('unit_price') or it.get('unit_price_foreign') or 0)
        line_currency = it.get('currency', po_currency)
        line_fx = float(it.get('fx_rate') or fx_rate)
        line_total_foreign = qty * unit_price_foreign
        line_total_base = line_total_foreign * line_fx
        item_rec = {
            'id': len(items) + 1,
            'product_id': it.get('product_id'),
            'description': it.get('description'),
            'quantity': qty,
            'unit_price_foreign': unit_price_foreign,
            'currency': line_currency,
            'fx_rate': line_fx,
            'total_amount_foreign': line_total_foreign,
            'total_amount_base': line_total_base,
            'tax_rate': float(it.get('tax_rate') or 0.0),
            'received_quantity': 0.0,
        }
        items.append(item_rec)
        total_foreign += line_total_foreign
        total_base += line_total_base

    new_po = {
        "id": len(purchase_orders) + 1,
        "po_number": po_number,
        "vendor_id": data.get('vendor_id'),
        "order_date": data.get('order_date', datetime.utcnow().date().isoformat()),
        "expected_delivery": data.get('expected_delivery'),
        "status": 'pending',
        "currency": po_currency,
        "fx_rate": fx_rate,
        "total_amount_foreign": round(total_foreign, 2),
        "total_amount_base": round(total_base, 2),
        "total_amount": round(total_base, 2),
        "tax_amount": data.get('tax_amount', 0.0),
        "notes": data.get('notes'),
        "items": items,
        "created_by": data.get('created_by'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    purchase_orders.append(new_po)
    
    # TODO: Auto-create budget/reserved amount in GL
    # create_budget_reservation(new_po['id'], new_po['total_amount'])
    try:
        AuditLogger.log(
            user_id=(data.get('created_by') or 'system'),
            action=AuditAction.CREATE,
            entity_type='purchase_order',
            entity_id=str(new_po['id']),
            new_values=new_po
        )
    except Exception:
        pass
    return jsonify(new_po), 201

@bp.route('/purchase-orders/<int:po_id>', methods=['PUT', 'OPTIONS'])
def update_purchase_order(po_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    """Update a purchase order"""
    data = request.get_json()
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if po:
        before = dict(po)
        po.update(data)
        # keep total_amount in sync if total_amount_base present
        if 'total_amount_base' in po and ('total_amount' not in po or data.get('total_amount') is None):
            po['total_amount'] = po.get('total_amount_base')
        po['updated_at'] = datetime.utcnow().isoformat()
        try:
            AuditLogger.log(
                user_id=(data.get('updated_by') or 'system'),
                action=AuditAction.UPDATE,
                entity_type='purchase_order',
                entity_id=str(po_id),
                old_values=before,
                new_values=po
            )
        except Exception:
            pass
        return jsonify(po)
    return jsonify({"error": "Purchase Order not found"}), 404

@bp.route('/purchase-orders/<int:po_id>', methods=['DELETE', 'OPTIONS'])
def delete_purchase_order(po_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    """Delete a purchase order"""
    global purchase_orders
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if po:
        purchase_orders = [p for p in purchase_orders if p['id'] != po_id]
        try:
            AuditLogger.log(
                user_id='system',
                action=AuditAction.DELETE,
                entity_type='purchase_order',
                entity_id=str(po_id),
                old_values=po
            )
        except Exception:
            pass
        return jsonify({"message": "Purchase Order deleted successfully"}), 200
    return jsonify({"error": "Purchase Order not found"}), 404

@bp.route('/purchase-orders/<int:po_id>/approve', methods=['POST', 'OPTIONS'])
def approve_purchase_order(po_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    """Approve a purchase order"""
    data = request.get_json()
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if po:
        before = dict(po)
        po['status'] = 'approved'
        po['approved_by'] = data.get('approved_by')
        po['approved_at'] = datetime.utcnow().isoformat()
        po['updated_at'] = datetime.utcnow().isoformat()
        try:
            AuditLogger.log(
                user_id=(data.get('approved_by') or 'system'),
                action=AuditAction.APPROVE,
                entity_type='purchase_order',
                entity_id=str(po_id),
                old_values=before,
                new_values=po
            )
        except Exception:
            pass
        return jsonify(po)
    return jsonify({"error": "Purchase Order not found"}), 404

@bp.route('/purchase-orders/<int:po_id>/reject', methods=['POST', 'OPTIONS'])
def reject_purchase_order(po_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    """Reject a purchase order"""
    data = request.get_json()
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if po:
        before = dict(po)
        po['status'] = 'rejected'
        po['rejection_reason'] = data.get('reason')
        po['updated_at'] = datetime.utcnow().isoformat()
        try:
            AuditLogger.log(
                user_id=(data.get('rejected_by') or 'system'),
                action=AuditAction.UPDATE,
                entity_type='purchase_order_reject',
                entity_id=str(po_id),
                old_values=before,
                new_values=po
            )
        except Exception:
            pass
        return jsonify(po)
    return jsonify({"error": "Purchase Order not found"}), 404

# File upload endpoint for PO attachments
@bp.route('/purchase-orders/<int:po_id>/attachments', methods=['POST'])
def upload_po_attachment(po_id):
    """Upload attachment for a purchase order"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file type
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    
    if file_extension not in allowed_extensions:
        return jsonify({"error": "Invalid file type"}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    file_path = f"uploads/po_attachments/{po_id}_{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    
    # Create attachment record
    attachment = {
        "id": len(purchase_orders) + 1,  # This should be from a proper sequence
        "po_id": po_id,
        "filename": filename,
        "file_path": file_path,
        "file_type": file_extension,
        "file_size": os.path.getsize(file_path),
        "uploaded_by": request.form.get('uploaded_by'),
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    return jsonify(attachment), 201


# Receiving endpoint: locks FX, allocates landed costs, posts inventory
@bp.route('/purchase-orders/<int:po_id>/receive', methods=['POST', 'OPTIONS'])
def receive_purchase_order(po_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    from modules.inventory.models import BasicInventoryTransaction
    data = request.get_json() or {}
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if not po:
        return jsonify({'error': 'Purchase Order not found'}), 404
    if po.get('status') == 'rejected':
        return jsonify({'error': 'Cannot receive a rejected PO'}), 400

    lines = data.get('items') or []
    warehouse_id = int(data.get('warehouse_id') or 1)
    landed_total = float(data.get('landed_costs_total') or 0.0)
    # Compute proportional allocation base
    base_sum = 0.0
    for l in lines:
        item = next((it for it in po['items'] if it['id'] == l.get('item_id')), None)
        if not item:
            continue
        qty = float(l.get('quantity') or 0)
        base_sum += qty * float(item.get('unit_price_foreign') or 0)

    receipts = []
    gaps = []
    for l in lines:
        item = next((it for it in po['items'] if it['id'] == l.get('item_id')), None)
        if not item:
            gaps.append({'type': 'line_not_found', 'item_id': l.get('item_id')})
            continue
        qty = float(l.get('quantity') or 0)
        if qty <= 0:
            continue
        if not item.get('product_id'):
            gaps.append({'type': 'missing_product', 'item_id': item['id']})
            continue
        # FX locked from item/PO
        line_fx = float(item.get('fx_rate') or po.get('fx_rate') or 1.0)
        unit_foreign = float(item.get('unit_price_foreign') or 0)
        # Landed allocation per unit
        allocated = 0.0
        if landed_total > 0 and base_sum > 0:
            share = (qty * unit_foreign) / base_sum
            allocated = landed_total * share
        unit_base = unit_foreign * line_fx
        total_base = qty * unit_base + allocated

        # Persist inventory transaction (SQLite via SQLAlchemy model)
        try:
            txn = BasicInventoryTransaction(
                product_id=int(item.get('product_id') or 0),
                transaction_type='IN',
                quantity=qty,
                unit_cost=unit_base,
                total_cost=total_base,
                reference_type='PO',
                reference_id=po_id,
                warehouse_id=warehouse_id
            )
            db.session.add(txn)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Fallback: continue without failing entire receipt
        item['received_quantity'] = float(item.get('received_quantity') or 0) + qty
        receipts.append({
            'item_id': item['id'],
            'received_qty': qty,
            'unit_cost_base': round(unit_base, 4),
            'fx_rate': line_fx,
            'allocated_landed_costs': round(allocated, 2),
            'total_cost_base': round(total_base, 2)
        })

    # Auto-close if fully received
    if all((it.get('received_quantity') or 0) >= (it.get('quantity') or 0) for it in po['items']):
        po['status'] = 'received'
        po['updated_at'] = datetime.utcnow().isoformat()

    # Attempt auto-journal in finance (optional)
    try:
        if _auto_journal_engine is not None:
            _auto_journal_engine.on_inventory_receipt({
                'po_id': po_id,
                'currency': po.get('currency'),
                'fx_rate': po.get('fx_rate'),
                'receipts': receipts
            })
    except Exception:
        # Ignore finance errors but report sync intent
        gaps.append({'type': 'finance_sync_pending'})

    try:
        AuditLogger.log(
            user_id=(data.get('received_by') or 'system'),
            action=AuditAction.UPDATE,
            entity_type='purchase_order_receive',
            entity_id=str(po_id),
            new_values={'receipts': receipts, 'po_status': po['status']}
        )
    except Exception:
        pass
    return jsonify({'message': 'Received', 'receipts': receipts, 'po_status': po['status'], 'gaps': gaps}), 200


# Reporting summary endpoint
@bp.route('/reporting/summary', methods=['GET', 'OPTIONS'])
def procurement_reporting_summary():
    if request.method == 'OPTIONS':
        return ('', 200)
    status_counts = {}
    vendor_stats = {}
    monthly = {}
    total_spend = 0.0
    for po in purchase_orders:
        status = po.get('status') or 'unknown'
        status_counts[status] = status_counts.get(status, 0) + 1
        amount = float(po.get('total_amount') or po.get('total_amount_base') or 0)
        total_spend += amount
        vendor_id = po.get('vendor_id')
        if vendor_id is not None:
            if vendor_id not in vendor_stats:
                vendor_stats[vendor_id] = {'po_count': 0, 'total_spent': 0.0}
            vendor_stats[vendor_id]['po_count'] += 1
            vendor_stats[vendor_id]['total_spent'] += amount
        try:
            od = po.get('order_date')
            if od:
                # Expect YYYY-MM-DD
                month = str(od)[:7]
                if month not in monthly:
                    monthly[month] = {'value': 0.0, 'count': 0}
                monthly[month]['value'] += amount
                monthly[month]['count'] += 1
        except Exception:
            pass
    # ERP sync counts
    erp_counts = {}
    for po in purchase_orders:
        sync = po.get('erp_sync_status') or 'not_exported'
        erp_counts[sync] = erp_counts.get(sync, 0) + 1
    return jsonify({
        'summary': {
            'total_spend': round(total_spend, 2),
            'total_pos': len(purchase_orders)
        },
        'status_counts': status_counts,
        'vendor_stats': vendor_stats,
        'monthly': monthly,
        'erp_sync_counts': erp_counts
    }), 200


# ERP integration endpoints
@bp.route('/erp/export-po', methods=['POST', 'OPTIONS'])
def erp_export_po():
    if request.method == 'OPTIONS':
        return ('', 200)
    data = request.get_json() or {}
    po_id = int(data.get('po_id') or 0)
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if not po:
        return jsonify({'error': 'PO not found'}), 404
    po['erp_sync_status'] = 'exported'
    po['erp_external_id'] = po.get('erp_external_id') or f"ERP-{po.get('po_number')}"
    po['erp_last_status_at'] = datetime.utcnow().isoformat()
    try:
        AuditLogger.log(user_id=(data.get('user_id') or 'system'), action=AuditAction.POST, entity_type='purchase_order_export', entity_id=str(po_id), new_values={'erp_external_id': po['erp_external_id']})
    except Exception:
        pass
    return jsonify({'message': 'Exported', 'po': po}), 200


@bp.route('/erp/update-po-status', methods=['POST', 'OPTIONS'])
def erp_update_po_status():
    if request.method == 'OPTIONS':
        return ('', 200)
    data = request.get_json() or {}
    po_id = data.get('po_id')
    po_number = data.get('po_number')
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'status is required'}), 400
    po = None
    if po_id is not None:
        po = next((p for p in purchase_orders if str(p['id']) == str(po_id)), None)
    if po is None and po_number is not None:
        po = next((p for p in purchase_orders if p.get('po_number') == po_number), None)
    if not po:
        return jsonify({'error': 'PO not found'}), 404
    before = dict(po)
    po['status'] = new_status
    po['erp_last_status_at'] = datetime.utcnow().isoformat()
    try:
        AuditLogger.log(user_id=(data.get('user_id') or 'erp'), action=AuditAction.UPDATE, entity_type='purchase_order_status', entity_id=str(po.get('id')), old_values=before, new_values=po)
    except Exception:
        pass
    return jsonify({'message': 'Updated', 'po': po}), 200


@bp.route('/erp/pending-pos', methods=['GET', 'OPTIONS'])
def erp_pending_pos():
    if request.method == 'OPTIONS':
        return ('', 200)
    pending = [p for p in purchase_orders if (p.get('erp_sync_status') or 'not_exported') != 'exported']
    return jsonify({'pending': pending, 'count': len(pending)}), 200


@bp.route('/integration/gaps', methods=['GET', 'OPTIONS'])
def integration_gaps():
    """Report simple integration gaps after purchases: missing product mapping, pending finance sync."""
    if request.method == 'OPTIONS':
        return ('', 200)
    gaps = []
    for po in purchase_orders:
        for it in (po.get('items') or []):
            if (it.get('received_quantity') or 0) > 0 and not it.get('product_id'):
                gaps.append({'po_number': po.get('po_number'), 'item_id': it.get('id'), 'type': 'missing_product'})
    return jsonify({'gaps': gaps}), 200


@bp.route('/purchase-orders/map-item-product', methods=['POST', 'OPTIONS'])
def map_po_item_product():
    """Map a product_id to a purchase order line item using po_number and item_id."""
    if request.method == 'OPTIONS':
        return ('', 200)
    data = request.get_json() or {}
    po_number = data.get('po_number')
    item_id = data.get('item_id')
    product_id = data.get('product_id')
    if not (po_number and item_id and product_id):
        return jsonify({'error': 'po_number, item_id, product_id are required'}), 400
    po = next((p for p in purchase_orders if p.get('po_number') == po_number), None)
    if not po:
        return jsonify({'error': 'PO not found'}), 404
    item = next((it for it in (po.get('items') or []) if str(it.get('id')) == str(item_id)), None)
    if not item:
        return jsonify({'error': 'Line item not found'}), 404
    try:
        item['product_id'] = int(product_id)
        return jsonify({'message': 'Mapped', 'po_number': po_number, 'item_id': item_id, 'product_id': int(product_id)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Analytics endpoints
@bp.route('/analytics', methods=['GET'])
def get_procurement_analytics():
    """Get procurement analytics"""
    total_pos = len(purchase_orders)
    pending_pos = len([po for po in purchase_orders if po.get('status') == 'pending'])
    approved_pos = len([po for po in purchase_orders if po.get('status') == 'approved'])
    total_value = sum(po.get('total_amount', 0) for po in purchase_orders)
    
    return jsonify({
        "total_purchase_orders": total_pos,
        "pending_purchase_orders": pending_pos,
        "approved_purchase_orders": approved_pos,
        "total_value": total_value,
        "average_po_value": total_value / total_pos if total_pos > 0 else 0
    })


# ---------------- RFx (RFQ) Endpoints ----------------
@bp.route('/rfqs', methods=['GET'])
def list_rfqs():
    rfqs = RFQ.query.order_by(RFQ.created_at.desc()).all()
    return jsonify([_serialize_rfq(r) for r in rfqs])


@bp.route('/rfqs', methods=['POST'])
def create_rfq():
    data = request.get_json() or {}
    rfq = RFQ(
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status') or 'draft',
        due_date=_parse_date(data.get('due_date')),
        criteria_json=data.get('criteria_json'),
        created_by=data.get('created_by')
    )
    db.session.add(rfq)
    db.session.flush()
    # Items
    for it in (data.get('items') or []):
        db.session.add(RFQItem(
            rfq_id=rfq.id,
            description=it.get('description'),
            quantity=float(it.get('quantity') or 1),
            uom=it.get('uom')
        ))
    db.session.commit()
    return jsonify(_serialize_rfq(rfq)), 201


@bp.route('/rfqs/<int:rfq_id>', methods=['GET'])
def get_rfq(rfq_id: int):
    rfq = RFQ.query.get(rfq_id)
    if not rfq:
        return jsonify({'error': 'RFQ not found'}), 404
    return jsonify(_serialize_rfq(rfq, include_children=True))


@bp.route('/rfqs/<int:rfq_id>', methods=['PUT'])
def update_rfq(rfq_id: int):
    data = request.get_json() or {}
    rfq = RFQ.query.get(rfq_id)
    if not rfq:
        return jsonify({'error': 'RFQ not found'}), 404
    before = _serialize_rfq(rfq, include_children=False)
    for field in ['title', 'description', 'status', 'criteria_json']:
        if field in data:
            setattr(rfq, field, data.get(field))
    if 'due_date' in data:
        rfq.due_date = _parse_date(data.get('due_date'))
    db.session.commit()
    try:
        AuditLogger.log(user_id=(data.get('updated_by') or 'system'), action=AuditAction.UPDATE, entity_type='rfq', entity_id=str(rfq.id), old_values=before, new_values=_serialize_rfq(rfq))
    except Exception:
        pass
    return jsonify(_serialize_rfq(rfq))


@bp.route('/rfqs/<int:rfq_id>/invite', methods=['POST'])
def invite_vendors_to_rfq(rfq_id: int):
    data = request.get_json() or {}
    vendor_ids = data.get('vendor_ids') or []
    rfq = RFQ.query.get(rfq_id)
    if not rfq:
        return jsonify({'error': 'RFQ not found'}), 404
    created = []
    for vid in vendor_ids:
        inv = RFQInvitation(
            rfq_id=rfq_id,
            vendor_id=int(vid),
            invite_token=f"INV-{rfq_id}-{vid}-{int(datetime.utcnow().timestamp())}"
        )
        db.session.add(inv)
        created.append(inv)
    db.session.commit()
    return jsonify({'invitations': [_serialize_invitation(i) for i in created]}), 201


@bp.route('/rfqs/<int:rfq_id>/responses', methods=['POST'])
def submit_rfq_response(rfq_id: int):
    data = request.get_json() or {}
    rfq = RFQ.query.get(rfq_id)
    if not rfq:
        return jsonify({'error': 'RFQ not found'}), 404
    response = RFQResponseHeader(
        rfq_id=rfq_id,
        vendor_id=int(data.get('vendor_id')),
        currency=data.get('currency') or 'USD',
        validity_days=data.get('validity_days'),
        notes=data.get('notes'),
        delivery_days=data.get('delivery_days')
    )
    db.session.add(response)
    db.session.flush()
    total_price = 0.0
    for it in (data.get('items') or []):
        price = float(it.get('price') or 0)
        total_price += price * float(it.get('quantity') or 1)
        db.session.add(RFQResponseItem(
            response_id=response.id,
            rfq_item_id=int(it.get('rfq_item_id')),
            price=price,
            currency=it.get('currency') or response.currency,
            delivery_days=it.get('delivery_days'),
            notes=it.get('notes')
        ))
    response.total_price = total_price
    db.session.commit()
    return jsonify(_serialize_response(response, include_items=True)), 201


@bp.route('/rfqs/<int:rfq_id>/score', methods=['POST'])
def score_rfq_responses(rfq_id: int):
    data = request.get_json() or {}
    rfq = RFQ.query.get(rfq_id)
    if not rfq:
        return jsonify({'error': 'RFQ not found'}), 404
    # criteria_json expected: [{name, weight}] weights sum to 1 or 100
    import json
    try:
        criteria = json.loads(rfq.criteria_json or '[]')
    except Exception:
        criteria = []
    responses = RFQResponseHeader.query.filter_by(rfq_id=rfq_id).all()
    for resp in responses:
        scores = {}
        # Example scoring: inverse of total price, lower delivery days better
        weight_price = next((c['weight'] for c in criteria if c.get('name') == 'price'), 0.5)
        weight_delivery = next((c['weight'] for c in criteria if c.get('name') == 'delivery'), 0.5)
        # Normalize across responses
    
    totals = [r.total_price or 0 for r in responses] or [1]
    min_total, max_total = min(totals), max(totals)
    deliveries = [r.delivery_days or 0 for r in responses] or [0]
    min_deliv, max_deliv = min(deliveries), max(deliveries)
    def normalize_inverse(value, min_v, max_v):
        if max_v == min_v:
            return 1.0
        return 1 - ((value - min_v) / (max_v - min_v))
    import json as _json
    for resp in responses:
        price_score = normalize_inverse(resp.total_price or 0, min_total, max_total)
        delivery_score = normalize_inverse(resp.delivery_days or 0, min_deliv, max_deliv)
        total_score = (weight_price * price_score) + (weight_delivery * delivery_score)
        resp.total_score = round(total_score * 100, 2)
        resp.score_json = _json.dumps({'price': round(price_score, 4), 'delivery': round(delivery_score, 4)})
    db.session.commit()
    return jsonify({'responses': [_serialize_response(r) for r in responses]})


@bp.route('/rfqs/<int:rfq_id>/award', methods=['POST'])
def award_rfq(rfq_id: int):
    data = request.get_json() or {}
    rfq = RFQ.query.get(rfq_id)
    if not rfq:
        return jsonify({'error': 'RFQ not found'}), 404
    winning_response_id = int(data.get('response_id'))
    response = RFQResponseHeader.query.get(winning_response_id)
    if not response or response.rfq_id != rfq_id:
        return jsonify({'error': 'Response not found'}), 404
    # Create PO in-memory (existing PO persistence is in-memory in this module)
    po_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{len(purchase_orders) + 1:03d}"
    items = []
    total_base = 0.0
    for ri in response.items:
        line_total = (ri.price or 0) * (ri.rfq_item.quantity or 1)
        items.append({
            'id': len(items) + 1,
            'description': ri.rfq_item.description,
            'quantity': ri.rfq_item.quantity,
            'unit_price_foreign': ri.price,
            'currency': response.currency,
            'fx_rate': 1.0,
            'total_amount_foreign': line_total,
            'total_amount_base': line_total,
            'tax_rate': 0.0,
            'received_quantity': 0.0,
        })
        total_base += line_total
    new_po = {
        'id': len(purchase_orders) + 1,
        'po_number': po_number,
        'vendor_id': response.vendor_id,
        'order_date': datetime.utcnow().date().isoformat(),
        'expected_delivery': None,
        'status': 'pending',
        'currency': response.currency,
        'fx_rate': 1.0,
        'total_amount_foreign': round(total_base, 2),
        'total_amount_base': round(total_base, 2),
        'tax_amount': 0.0,
        'notes': f"Awarded from RFQ {rfq.id}",
        'items': items,
        'created_by': data.get('awarded_by')
    }
    purchase_orders.append(new_po)
    rfq.status = 'awarded'
    db.session.commit()
    try:
        AuditLogger.log(user_id=(data.get('awarded_by') or 'system'), action=AuditAction.APPROVE, entity_type='rfq_award', entity_id=str(rfq.id), new_values={'response_id': response.id, 'po_number': po_number})
    except Exception:
        pass
    return jsonify({'message': 'Awarded', 'po': new_po})


# ---------------- Contracts (CLM v1) ----------------
@bp.route('/contracts', methods=['GET'])
def list_contracts():
    vendor_id = request.args.get('vendor_id', type=int)
    status = request.args.get('status')
    expiring_in_days = request.args.get('expiring_in_days', type=int)
    query = Contract.query
    if vendor_id:
        query = query.filter(Contract.vendor_id == vendor_id)
    if status:
        query = query.filter(Contract.status == status)
    contracts = query.order_by(Contract.created_at.desc()).all()
    results = [_serialize_contract(c) for c in contracts]
    if expiring_in_days is not None:
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow().date() + timedelta(days=expiring_in_days)
        results = [c for c in results if c.get('end_date') and c['end_date'] <= cutoff.isoformat()]
    return jsonify(results)


@bp.route('/contracts', methods=['POST'])
def create_contract():
    data = request.get_json() or {}
    contract = Contract(
        title=data.get('title'),
        vendor_id=int(data.get('vendor_id')),
        rfq_id=data.get('rfq_id'),
        status=data.get('status') or 'active',
        start_date=_parse_date(data.get('start_date')),
        end_date=_parse_date(data.get('end_date')),
        renewal_notice_days=int(data.get('renewal_notice_days') or 60),
        auto_renew=bool(data.get('auto_renew') or False),
        contract_value=float(data.get('contract_value') or 0.0),
        terms_summary=data.get('terms_summary'),
        created_by=data.get('created_by')
    )
    db.session.add(contract)
    db.session.commit()
    return jsonify(_serialize_contract(contract)), 201


@bp.route('/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id: int):
    contract = Contract.query.get(contract_id)
    if not contract:
        return jsonify({'error': 'Contract not found'}), 404
    return jsonify(_serialize_contract(contract, include_documents=True))


@bp.route('/contracts/<int:contract_id>', methods=['PUT'])
def update_contract(contract_id: int):
    data = request.get_json() or {}
    contract = Contract.query.get(contract_id)
    if not contract:
        return jsonify({'error': 'Contract not found'}), 404
    before = _serialize_contract(contract)
    for field in ['title','status','terms_summary','rfq_id','auto_renew','renewal_notice_days','contract_value']:
        if field in data:
            setattr(contract, field, data.get(field))
    if 'start_date' in data:
        contract.start_date = _parse_date(data.get('start_date'))
    if 'end_date' in data:
        contract.end_date = _parse_date(data.get('end_date'))
    db.session.commit()
    try:
        AuditLogger.log(user_id=(data.get('updated_by') or 'system'), action=AuditAction.UPDATE, entity_type='contract', entity_id=str(contract.id), old_values=before, new_values=_serialize_contract(contract))
    except Exception:
        pass
    return jsonify(_serialize_contract(contract))


@bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
def delete_contract(contract_id: int):
    contract = Contract.query.get(contract_id)
    if not contract:
        return jsonify({'error': 'Contract not found'}), 404
    db.session.delete(contract)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@bp.route('/contracts/<int:contract_id>/documents', methods=['POST'])
def upload_contract_document(contract_id: int):
    contract = Contract.query.get(contract_id)
    if not contract:
        return jsonify({'error': 'Contract not found'}), 404
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type'}), 400
    filename = secure_filename(file.filename)
    file_path = f"uploads/contracts/{contract_id}_{int(datetime.utcnow().timestamp())}_{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    doc = ContractDocument(
        contract_id=contract_id,
        doc_type=request.form.get('doc_type'),
        filename=filename,
        file_path=file_path,
        file_type=ext,
        file_size=os.path.getsize(file_path),
        uploaded_by=request.form.get('uploaded_by')
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify(_serialize_contract_document(doc)), 201


# ---------- Helpers ----------
def _serialize_vendor(v: Vendor) -> dict:
    return {
        'id': v.id,
        'name': v.name,
        'email': v.email,
        'phone': v.phone,
        'address': v.address,
        'tax_id': v.tax_id,
        'payment_terms': v.payment_terms,
        'credit_limit': v.credit_limit,
        'is_active': v.is_active,
        'category': v.category,
        'risk_level': v.risk_level,
        'region': v.region,
        'is_preferred': v.is_preferred,
        'on_time_delivery_rate': v.on_time_delivery_rate,
        'price_variance_pct': v.price_variance_pct,
        'quality_score': v.quality_score,
        'performance_notes': v.performance_notes,
        'last_reviewed_at': v.last_reviewed_at.isoformat() if v.last_reviewed_at else None,
        'created_at': v.created_at.isoformat() if v.created_at else None,
        'updated_at': v.updated_at.isoformat() if v.updated_at else None,
    }


def _serialize_vendor_document(d: VendorDocument) -> dict:
    return {
        'id': d.id,
        'vendor_id': d.vendor_id,
        'doc_type': d.doc_type,
        'filename': d.filename,
        'file_path': d.file_path,
        'file_type': d.file_type,
        'file_size': d.file_size,
        'uploaded_by': d.uploaded_by,
        'uploaded_at': d.uploaded_at.isoformat() if d.uploaded_at else None,
        'effective_date': d.effective_date.isoformat() if d.effective_date else None,
        'expiry_date': d.expiry_date.isoformat() if d.expiry_date else None,
    }


def _serialize_vendor_communication(c: VendorCommunication) -> dict:
    return {
        'id': c.id,
        'vendor_id': c.vendor_id,
        'channel': c.channel,
        'direction': c.direction,
        'subject': c.subject,
        'message': c.message,
        'related_rfx_id': c.related_rfx_id,
        'created_by': c.created_by,
        'created_at': c.created_at.isoformat() if c.created_at else None,
    }


def _parse_date(val: str):
    if not val:
        return None
    try:
        return datetime.fromisoformat(val).date()
    except Exception:
        try:
            # Fallback YYYY-MM-DD
            return datetime.strptime(val, '%Y-%m-%d').date()
        except Exception:
            return None


def _serialize_rfq(r: RFQ, include_children: bool = False) -> dict:
    data = {
        'id': r.id,
        'title': r.title,
        'description': r.description,
        'status': r.status,
        'due_date': r.due_date.isoformat() if r.due_date else None,
        'criteria_json': r.criteria_json,
        'created_at': r.created_at.isoformat() if r.created_at else None,
        'updated_at': r.updated_at.isoformat() if r.updated_at else None,
    }
    if include_children:
        data['items'] = [{'id': it.id, 'description': it.description, 'quantity': it.quantity, 'uom': it.uom} for it in r.items]
        data['responses'] = [_serialize_response(resp) for resp in r.responses]
    else:
        data['items_count'] = len(r.items or [])
    return data


def _serialize_invitation(i: RFQInvitation) -> dict:
    return {
        'id': i.id,
        'rfq_id': i.rfq_id,
        'vendor_id': i.vendor_id,
        'invite_token': i.invite_token,
        'invited_at': i.invited_at.isoformat() if i.invited_at else None,
        'responded_at': i.responded_at.isoformat() if i.responded_at else None,
    }


def _serialize_response(resp: RFQResponseHeader, include_items: bool = False) -> dict:
    data = {
        'id': resp.id,
        'rfq_id': resp.rfq_id,
        'vendor_id': resp.vendor_id,
        'vendor': _serialize_vendor(resp.vendor) if resp.vendor else None,
        'submitted_at': resp.submitted_at.isoformat() if resp.submitted_at else None,
        'currency': resp.currency,
        'validity_days': resp.validity_days,
        'notes': resp.notes,
        'total_price': resp.total_price,
        'delivery_days': resp.delivery_days,
        'score_json': resp.score_json,
        'total_score': resp.total_score,
    }
    if include_items:
        data['items'] = [
            {
                'id': it.id,
                'rfq_item_id': it.rfq_item_id,
                'description': it.rfq_item.description if it.rfq_item else None,
                'quantity': it.rfq_item.quantity if it.rfq_item else None,
                'price': it.price,
                'currency': it.currency,
                'delivery_days': it.delivery_days,
                'notes': it.notes,
            }
            for it in resp.items
        ]
    return data


def _serialize_contract(c: Contract, include_documents: bool = False) -> dict:
    data = {
        'id': c.id,
        'title': c.title,
        'vendor_id': c.vendor_id,
        'rfq_id': c.rfq_id,
        'status': c.status,
        'start_date': c.start_date.isoformat() if c.start_date else None,
        'end_date': c.end_date.isoformat() if c.end_date else None,
        'renewal_notice_days': c.renewal_notice_days,
        'auto_renew': c.auto_renew,
        'contract_value': c.contract_value,
        'terms_summary': c.terms_summary,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'updated_at': c.updated_at.isoformat() if c.updated_at else None,
        'vendor': _serialize_vendor(c.vendor) if c.vendor else None,
    }
    if include_documents:
        data['documents'] = [_serialize_contract_document(d) for d in c.documents]
    return data


def _serialize_contract_document(d: ContractDocument) -> dict:
    return {
        'id': d.id,
        'contract_id': d.contract_id,
        'doc_type': d.doc_type,
        'filename': d.filename,
        'file_path': d.file_path,
        'file_type': d.file_type,
        'file_size': d.file_size,
        'uploaded_by': d.uploaded_by,
        'uploaded_at': d.uploaded_at.isoformat() if d.uploaded_at else None,
    }