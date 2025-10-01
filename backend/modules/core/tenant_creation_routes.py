# backend/modules/core/tenant_creation_routes.py

from flask import Blueprint, request, jsonify, g
from app import db
from modules.core.tenant_models import Tenant, UserTenant, TenantModule
from modules.core.tenant_context import require_tenant
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

tenant_creation_bp = Blueprint('tenant_creation', __name__)

@tenant_creation_bp.route('/api/tenant/tenants', methods=['POST'])
@jwt_required()
def create_tenant():
    """Create a new tenant for a user"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['name', 'subscription_plan']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Check if user already has a tenant
        existing_tenant = UserTenant.query.filter_by(user_id=user_id, is_default=True).first()
        if existing_tenant:
            return jsonify({
                "message": "User already has a default tenant"
            }), 409
        
        # Create tenant
        tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
        tenant = Tenant(
            id=tenant_id,
            name=data['name'],
            domain=data.get('domain', f"{data['name'].lower().replace(' ', '')}.company.com"),
            subscription_plan=data['subscription_plan'],
            status='active',
            tenant_metadata=data.get('settings', {})
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        # Associate user with tenant as admin
        user_tenant = UserTenant(
            user_id=user_id,
            tenant_id=tenant_id,
            role='admin',
            is_default=True,
            permissions=['*']  # Full permissions for tenant creator
        )
        
        db.session.add(user_tenant)
        db.session.commit()
        
        return jsonify({
            "message": "Tenant created successfully",
            "id": tenant_id,
            "name": tenant.name,
            "subscription_plan": tenant.subscription_plan
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Tenant creation error: {str(e)}")
        return jsonify({
            "message": "Failed to create tenant",
            "error": str(e)
        }), 500

@tenant_creation_bp.route('/api/tenant/user-tenants', methods=['POST'])
@jwt_required()
def associate_user_tenant():
    """Associate a user with a tenant"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or get_jwt_identity()
        tenant_id = data.get('tenant_id')
        role = data.get('role', 'member')
        is_default = data.get('is_default', False)
        
        if not tenant_id:
            return jsonify({
                "message": "tenant_id is required"
            }), 400
        
        # Check if tenant exists
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        if not tenant:
            return jsonify({
                "message": "Tenant not found"
            }), 404
        
        # Check if association already exists
        existing = UserTenant.query.filter_by(user_id=user_id, tenant_id=tenant_id).first()
        if existing:
            return jsonify({
                "message": "User already associated with this tenant"
            }), 409
        
        # Create association
        user_tenant = UserTenant(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            is_default=is_default,
            permissions=data.get('permissions', [])
        )
        
        db.session.add(user_tenant)
        db.session.commit()
        
        return jsonify({
            "message": "User associated with tenant successfully"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ User-tenant association error: {str(e)}")
        return jsonify({
            "message": "Failed to associate user with tenant",
            "error": str(e)
        }), 500

@tenant_creation_bp.route('/api/tenant/tenants/<tenant_id>/modules/<module_name>', methods=['POST'])
@jwt_required()
def activate_tenant_module(tenant_id, module_name):
    """Activate a module for a tenant"""
    try:
        data = request.get_json()
        
        # Check if tenant exists
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        if not tenant:
            return jsonify({
                "message": "Tenant not found"
            }), 404
        
        # Check if module already activated
        existing = TenantModule.query.filter_by(tenant_id=tenant_id, module_name=module_name).first()
        if existing:
            return jsonify({
                "message": "Module already activated for this tenant"
            }), 409
        
        # Activate module
        tenant_module = TenantModule(
            tenant_id=tenant_id,
            module_name=module_name,
            enabled=data.get('enabled', True),
            configuration=data.get('configuration', {}),
            activated_by=get_jwt_identity()
        )
        
        db.session.add(tenant_module)
        db.session.commit()
        
        return jsonify({
            "message": f"Module {module_name} activated successfully"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Module activation error: {str(e)}")
        return jsonify({
            "message": "Failed to activate module",
            "error": str(e)
        }), 500

@tenant_creation_bp.route('/api/tenant/my-tenants', methods=['GET'])
@jwt_required()
def get_user_tenants():
    """Get all tenants for the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's tenants
        user_tenants = UserTenant.query.filter_by(user_id=user_id).all()
        
        tenants = []
        for ut in user_tenants:
            tenant = Tenant.query.filter_by(id=ut.tenant_id).first()
            if tenant:
                tenants.append({
                    "id": tenant.id,
                    "name": tenant.name,
                    "domain": tenant.domain,
                    "subscription_plan": tenant.subscription_plan,
                    "status": tenant.status,
                    "role": ut.role,
                    "is_default": ut.is_default,
                    "permissions": ut.permissions
                })
        
        return jsonify({
            "tenants": tenants,
            "default_tenant": next((t for t in tenants if t.get('is_default')), tenants[0] if tenants else None)
        }), 200
        
    except Exception as e:
        print(f"❌ Get user tenants error: {str(e)}")
        return jsonify({
            "message": "Failed to get user tenants",
            "error": str(e)
        }), 500












