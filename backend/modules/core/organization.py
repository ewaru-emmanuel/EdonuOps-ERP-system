# backend/modules/core/organization.py

from flask import Blueprint, request, jsonify
from app import db
from .auth import User
from .models import Organization, Role
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..core.rbac import requires_roles

org_bp = Blueprint("org", __name__)

@org_bp.route("/organization", methods=["POST"])
@jwt_required()
@requires_roles("admin")
def create_organization():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"message": "Organization name is required"}), 400

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    new_org = Organization(name=name, created_by_user_id=current_user_id)
    db.session.add(new_org)
    db.session.commit()

    return jsonify({"message": "Organization created successfully", "id": new_org.id}), 201

@org_bp.route("/organization/<int:org_id>/users", methods=["GET"])
@jwt_required()
@requires_roles("admin", "manager")
def get_organization_users(org_id):
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"message": "Organization not found"}), 404

    users = User.query.filter_by(organization_id=org_id).all()
    user_list = [{"id": u.id, "username": u.username, "email": u.email, "role": u.role.role_name} for u in users]
    return jsonify({"users": user_list}), 200