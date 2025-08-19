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
@bp.route('/purchase-orders', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders with filters"""
    vendor_id = request.args.get('vendor_id', type=int)
    status = request.args.get('status')
    
    filtered_pos = purchase_orders
    if vendor_id:
        filtered_pos = [po for po in filtered_pos if po.get('vendor_id') == vendor_id]
    if status:
        filtered_pos = [po for po in filtered_pos if po.get('status') == status]
    
    return jsonify(filtered_pos)

@bp.route('/purchase-orders', methods=['POST'])
def create_purchase_order():
    """Create a new purchase order"""
    data = request.get_json()
    
    # Generate PO number
    po_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{len(purchase_orders) + 1:03d}"
    
    new_po = {
        "id": len(purchase_orders) + 1,
        "po_number": po_number,
        "vendor_id": data.get('vendor_id'),
        "order_date": data.get('order_date', datetime.utcnow().date().isoformat()),
        "expected_delivery": data.get('expected_delivery'),
        "status": 'pending',
        "total_amount": data.get('total_amount', 0.0),
        "tax_amount": data.get('tax_amount', 0.0),
        "notes": data.get('notes'),
        "created_by": data.get('created_by'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    purchase_orders.append(new_po)
    
    # TODO: Auto-create budget/reserved amount in GL
    # create_budget_reservation(new_po['id'], new_po['total_amount'])
    
    return jsonify(new_po), 201

@bp.route('/purchase-orders/<int:po_id>', methods=['PUT'])
def update_purchase_order(po_id):
    """Update a purchase order"""
    data = request.get_json()
    po = next((p for p in purchase_orders if p['id'] == po_id), None)
    if po:
        po.update(data)
        po['updated_at'] = datetime.utcnow().isoformat()
        return jsonify(po)
    return jsonify({"error": "Purchase Order not found"}), 404

@bp.route('/purchase-orders/<int:po_id>/approve', methods=['POST'])
def approve_purchase_order(po_id):
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

@bp.route('/purchase-orders/<int:po_id>/reject', methods=['POST'])
def reject_purchase_order(po_id):
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