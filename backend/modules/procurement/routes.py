# backend/modules/procurement/routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.procurement.models import Vendor, PurchaseOrder, PurchaseOrderItem, POAttachment
from modules.finance.models import Account
import os
from werkzeug.utils import secure_filename

bp = Blueprint('procurement', __name__, url_prefix='/api/procurement')

# Sample data (replace with database queries)
vendors = []
purchase_orders = []

# Vendor endpoints
@bp.route('/vendors', methods=['GET'])
def get_vendors():
    """Get all vendors"""
    return jsonify(vendors)

@bp.route('/vendors', methods=['POST'])
def create_vendor():
    """Create a new vendor"""
    data = request.get_json()
    new_vendor = {
        "id": len(vendors) + 1,
        "name": data.get('name'),
        "email": data.get('email'),
        "phone": data.get('phone'),
        "address": data.get('address'),
        "tax_id": data.get('tax_id'),
        "payment_terms": data.get('payment_terms', 'Net 30'),
        "credit_limit": data.get('credit_limit', 0.0),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    vendors.append(new_vendor)
    return jsonify(new_vendor), 201

@bp.route('/vendors/<int:vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    """Update a vendor"""
    data = request.get_json()
    vendor = next((v for v in vendors if v['id'] == vendor_id), None)
    if vendor:
        vendor.update(data)
        vendor['updated_at'] = datetime.utcnow().isoformat()
        return jsonify(vendor)
    return jsonify({"error": "Vendor not found"}), 404

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
        "tax_amount": data.get('tax_amount', 0.0),
        "notes": data.get('notes'),
        "items": items,
        "created_by": data.get('created_by'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    purchase_orders.append(new_po)
    
    # TODO: Auto-create budget/reserved amount in GL
    # create_budget_reservation(new_po['id'], new_po['total_amount'])
    
    return jsonify(new_po), 201

@bp.route('/purchase-orders/<int:po_id>', methods=['PUT', 'OPTIONS'])
def update_purchase_order(po_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    """Update a purchase order"""
    data = request.get_json()
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if po:
        po.update(data)
        po['updated_at'] = datetime.utcnow().isoformat()
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
        po['status'] = 'approved'
        po['approved_by'] = data.get('approved_by')
        po['approved_at'] = datetime.utcnow().isoformat()
        po['updated_at'] = datetime.utcnow().isoformat()
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
        po['status'] = 'rejected'
        po['rejection_reason'] = data.get('reason')
        po['updated_at'] = datetime.utcnow().isoformat()
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
    for l in lines:
        item = next((it for it in po['items'] if it['id'] == l.get('item_id')), None)
        if not item:
            continue
        qty = float(l.get('quantity') or 0)
        if qty <= 0:
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

    return jsonify({'message': 'Received', 'receipts': receipts, 'po_status': po['status']}), 200

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