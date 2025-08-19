# backend/modules/procurement/vendor_portal.py

from flask import Blueprint, request, jsonify
from app import db
from .models import PurchaseOrder, Vendor
from ..core.rbac import requires_roles
from flask_jwt_extended import jwt_required

vendor_portal_bp = Blueprint("vendor_portal", __name__)

@vendor_portal_bp.route("/po/<int:po_id>", methods=["GET"])
@jwt_required()
@requires_roles("vendor")
def view_po_for_vendor(po_id):
    po = PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({"message": "Purchase order not found"}), 404
    # Logic to check if the current user is the vendor for this PO
    return jsonify({"id": po.id, "vendor_id": po.vendor_id, "status": po.status, "total_amount": po.total_amount}), 200