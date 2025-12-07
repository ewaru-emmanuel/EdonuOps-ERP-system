"""
Tenant Management API Routes
APIs for managing tenants, user-tenant relationships, and tenant settings
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
    require_role
)
from modules.core.tenant_models import (
    Tenant, 
    UserTenant, 
    TenantModule, 
    TenantSettings
)
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
tenant_management_bp = Blueprint('tenant_management', __name__, url_prefix='/api/tenant')

# ============================================================================
# TENANT MANAGEMENT (Admin Only)
# ============================================================================

@tenant_management_bp.route('/tenants', methods=['GET'])
@require_tenant
@require_role('admin')
def get_all_tenants():
    """Get all tenants (admin only)"""
    try:
        tenants = Tenant.query.all()
        
        return jsonify([{
            'id': tenant.id,
            'name': tenant.name,
            'domain': tenant.domain,
            'subscription_plan': tenant.subscription_plan,
            'status': tenant.status,
            'settings': tenant.settings or {},
            'metadata': tenant.tenant_metadata or {},
            'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
            'created_by': tenant.created_by,
            'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None
        } for tenant in tenants]), 200
        
    except Exception as e:
        logger.error(f"Error fetching all tenants: {e}")
        return jsonify({'error': 'Failed to fetch tenants'}), 500

@tenant_management_bp.route('/tenants', methods=['POST'])
@require_tenant
@require_role('admin')
def create_tenant():
    """Create a new tenant (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if tenant ID already exists
        existing_tenant = Tenant.query.filter_by(id=data['id']).first()
        if existing_tenant:
            return jsonify({'error': 'Tenant ID already exists'}), 400
        
        # Create new tenant
        tenant = Tenant(
            id=data['id'],
            name=data['name'],
            domain=data.get('domain'),
            subscription_plan=data.get('subscription_plan', 'free'),
            status=data.get('status', 'active'),
            settings=data.get('settings', {}),
            tenant_metadata=data.get('metadata', {}),
            created_by=get_tenant_context().user_id
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'domain': tenant.domain,
            'subscription_plan': tenant.subscription_plan,
            'status': tenant.status,
            'message': 'Tenant created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating tenant: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create tenant'}), 500

@tenant_management_bp.route('/tenants/<tenant_id>', methods=['GET'])
@require_tenant
@require_role('admin')
def get_tenant(tenant_id):
    """Get a specific tenant (admin only)"""
    try:
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'domain': tenant.domain,
            'subscription_plan': tenant.subscription_plan,
            'status': tenant.status,
            'settings': tenant.settings or {},
            'metadata': tenant.tenant_metadata or {},
            'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
            'created_by': tenant.created_by,
            'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching tenant: {e}")
        return jsonify({'error': 'Failed to fetch tenant'}), 500

@tenant_management_bp.route('/tenants/<tenant_id>', methods=['PUT'])
@require_tenant
@require_role('admin')
def update_tenant(tenant_id):
    """Update a tenant (admin only)"""
    try:
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        data = request.get_json()
        
        # Update tenant fields
        for field in ['name', 'domain', 'subscription_plan', 'status', 'settings', 'metadata']:
            if field in data:
                if field == 'metadata':
                    setattr(tenant, 'tenant_metadata', data[field])
                else:
                    setattr(tenant, field, data[field])
        
        tenant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'domain': tenant.domain,
            'subscription_plan': tenant.subscription_plan,
            'status': tenant.status,
            'message': 'Tenant updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating tenant: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update tenant'}), 500

# ============================================================================
# USER-TENANT RELATIONSHIPS
# ============================================================================

@tenant_management_bp.route('/user-tenants', methods=['GET'])
@require_tenant
@require_role('admin')
def get_user_tenants():
    """Get all user-tenant relationships (admin only)"""
    try:
        user_tenants = UserTenant.query.all()
        
        return jsonify([{
            'id': ut.id,
            'user_id': ut.user_id,
            'tenant_id': ut.tenant_id,
            'tenant_name': ut.tenant.name if ut.tenant else None,
            'role': ut.role,
            'is_default': ut.is_default,
            'permissions': ut.permissions or {},
            'joined_at': ut.joined_at.isoformat() if ut.joined_at else None,
            'last_accessed': ut.last_accessed.isoformat() if ut.last_accessed else None
        } for ut in user_tenants]), 200
        
    except Exception as e:
        logger.error(f"Error fetching user-tenants: {e}")
        return jsonify({'error': 'Failed to fetch user-tenants'}), 500

@tenant_management_bp.route('/user-tenants', methods=['POST'])
@require_tenant
@require_role('admin')
def create_user_tenant():
    """Create a user-tenant relationship (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'tenant_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if relationship already exists
        existing = UserTenant.query.filter_by(
            user_id=data['user_id'],
            tenant_id=data['tenant_id']
        ).first()
        
        if existing:
            return jsonify({'error': 'User-tenant relationship already exists'}), 400
        
        # Create new user-tenant relationship
        user_tenant = UserTenant(
            user_id=data['user_id'],
            tenant_id=data['tenant_id'],
            role=data.get('role', 'user'),
            is_default=data.get('is_default', False),
            permissions=data.get('permissions', {})
        )
        
        db.session.add(user_tenant)
        db.session.commit()
        
        return jsonify({
            'id': user_tenant.id,
            'user_id': user_tenant.user_id,
            'tenant_id': user_tenant.tenant_id,
            'role': user_tenant.role,
            'is_default': user_tenant.is_default,
            'message': 'User-tenant relationship created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating user-tenant relationship: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create user-tenant relationship'}), 500

@tenant_management_bp.route('/user-tenants/<int:user_tenant_id>', methods=['PUT'])
@require_tenant
@require_role('admin')
def update_user_tenant(user_tenant_id):
    """Update a user-tenant relationship (admin only)"""
    try:
        user_tenant = UserTenant.query.get(user_tenant_id)
        
        if not user_tenant:
            return jsonify({'error': 'User-tenant relationship not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        for field in ['role', 'is_default', 'permissions']:
            if field in data:
                setattr(user_tenant, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'id': user_tenant.id,
            'user_id': user_tenant.user_id,
            'tenant_id': user_tenant.tenant_id,
            'role': user_tenant.role,
            'is_default': user_tenant.is_default,
            'message': 'User-tenant relationship updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating user-tenant relationship: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user-tenant relationship'}), 500

# ============================================================================
# TENANT MODULES
# ============================================================================

@tenant_management_bp.route('/tenants/<tenant_id>/modules', methods=['GET'])
@require_tenant
@require_role('admin')
def get_tenant_modules(tenant_id):
    """Get modules for a specific tenant (admin only)"""
    try:
        from modules.core.tenant_query_helper import tenant_query
        # Note: TenantModule queries by specific tenant_id are OK for admin routes
        modules = TenantModule.query.filter_by(tenant_id=tenant_id).all()
        
        return jsonify([{
            'id': module.id,
            'tenant_id': module.tenant_id,
            'module_name': module.module_name,
            'enabled': module.enabled,
            'activated_at': module.activated_at.isoformat() if module.activated_at else None,
            'expires_at': module.expires_at.isoformat() if module.expires_at else None,
            'configuration': module.configuration or {}
        } for module in modules]), 200
        
    except Exception as e:
        logger.error(f"Error fetching tenant modules: {e}")
        return jsonify({'error': 'Failed to fetch tenant modules'}), 500

@tenant_management_bp.route('/tenants/<tenant_id>/modules', methods=['POST'])
@require_tenant
@require_role('admin')
def activate_tenant_module(tenant_id):
    """Activate a module for a tenant (admin only)"""
    try:
        data = request.get_json()
        
        if 'module_name' not in data:
            return jsonify({'error': 'Missing required field: module_name'}), 400
        
        # Check if module already exists
        existing = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_name=data['module_name']
        ).first()
        
        if existing:
            # Update existing module
            existing.enabled = data.get('enabled', True)
            existing.activated_at = datetime.utcnow()
            existing.configuration = data.get('configuration', {})
        else:
            # Create new module
            module = TenantModule(
                tenant_id=tenant_id,
                module_name=data['module_name'],
                enabled=data.get('enabled', True),
                activated_at=datetime.utcnow(),
                expires_at=data.get('expires_at'),
                configuration=data.get('configuration', {})
            )
            db.session.add(module)
        
        db.session.commit()
        
        return jsonify({
            'tenant_id': tenant_id,
            'module_name': data['module_name'],
            'enabled': data.get('enabled', True),
            'message': 'Module activated successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error activating tenant module: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to activate tenant module'}), 500

# ============================================================================
# TENANT SETTINGS
# ============================================================================

@tenant_management_bp.route('/tenants/<tenant_id>/settings', methods=['GET'])
@require_tenant
def get_tenant_settings(tenant_id):
    """Get settings for a specific tenant"""
    try:
        # Check if user has access to this tenant
        tenant_context = get_tenant_context()
        if tenant_context.tenant_id != tenant_id and not tenant_context.has_role('admin'):
            return jsonify({'error': 'Access denied to this tenant'}), 403
        
        settings = TenantSettings.query.filter_by(tenant_id=tenant_id).all()
        
        return jsonify([{
            'id': setting.id,
            'tenant_id': setting.tenant_id,
            'setting_key': setting.setting_key,
            'setting_value': setting.setting_value,
            'setting_type': setting.setting_type,
            'created_at': setting.created_at.isoformat() if setting.created_at else None,
            'updated_at': setting.updated_at.isoformat() if setting.updated_at else None,
            'updated_by': setting.updated_by
        } for setting in settings]), 200
        
    except Exception as e:
        logger.error(f"Error fetching tenant settings: {e}")
        return jsonify({'error': 'Failed to fetch tenant settings'}), 500

@tenant_management_bp.route('/tenants/<tenant_id>/settings', methods=['POST'])
@require_tenant
def create_tenant_setting(tenant_id):
    """Create a setting for a specific tenant"""
    try:
        # Check if user has access to this tenant
        tenant_context = get_tenant_context()
        if tenant_context.tenant_id != tenant_id and not tenant_context.has_role('admin'):
            return jsonify({'error': 'Access denied to this tenant'}), 403
        
        data = request.get_json()
        
        if 'setting_key' not in data:
            return jsonify({'error': 'Missing required field: setting_key'}), 400
        
        # Check if setting already exists
        existing = TenantSettings.query.filter_by(
            tenant_id=tenant_id,
            setting_key=data['setting_key']
        ).first()
        
        if existing:
            return jsonify({'error': 'Setting already exists'}), 400
        
        # Create new setting
        setting = TenantSettings(
            tenant_id=tenant_id,
            setting_key=data['setting_key'],
            setting_value=data.get('setting_value'),
            setting_type=data.get('setting_type', 'string'),
            updated_by=tenant_context.user_id
        )
        
        db.session.add(setting)
        db.session.commit()
        
        return jsonify({
            'id': setting.id,
            'tenant_id': setting.tenant_id,
            'setting_key': setting.setting_key,
            'setting_value': setting.setting_value,
            'setting_type': setting.setting_type,
            'message': 'Setting created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating tenant setting: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create tenant setting'}), 500

@tenant_management_bp.route('/tenants/<tenant_id>/settings/<setting_key>', methods=['PUT'])
@require_tenant
def update_tenant_setting(tenant_id, setting_key):
    """Update a setting for a specific tenant"""
    try:
        # Check if user has access to this tenant
        tenant_context = get_tenant_context()
        if tenant_context.tenant_id != tenant_id and not tenant_context.has_role('admin'):
            return jsonify({'error': 'Access denied to this tenant'}), 403
        
        setting = TenantSettings.query.filter_by(
            tenant_id=tenant_id,
            setting_key=setting_key
        ).first()
        
        if not setting:
            return jsonify({'error': 'Setting not found'}), 404
        
        data = request.get_json()
        
        # Update setting
        if 'setting_value' in data:
            setting.setting_value = data['setting_value']
        if 'setting_type' in data:
            setting.setting_type = data['setting_type']
        
        setting.updated_at = datetime.utcnow()
        setting.updated_by = tenant_context.user_id
        
        db.session.commit()
        
        return jsonify({
            'id': setting.id,
            'tenant_id': setting.tenant_id,
            'setting_key': setting.setting_key,
            'setting_value': setting.setting_value,
            'setting_type': setting.setting_type,
            'message': 'Setting updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating tenant setting: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update tenant setting'}), 500

# ============================================================================
# CURRENT USER TENANTS
# ============================================================================

@tenant_management_bp.route('/my-tenants', methods=['GET'])
@require_tenant
def get_my_tenants():
    """Get all tenants for the current user"""
    try:
        tenant_context = get_tenant_context()
        
        user_tenants = UserTenant.query.filter_by(user_id=tenant_context.user_id).all()
        
        return jsonify([{
            'id': ut.id,
            'user_id': ut.user_id,
            'tenant_id': ut.tenant_id,
            'tenant_name': ut.tenant.name if ut.tenant else None,
            'tenant_domain': ut.tenant.domain if ut.tenant else None,
            'tenant_plan': ut.tenant.subscription_plan if ut.tenant else None,
            'role': ut.role,
            'is_default': ut.is_default,
            'permissions': ut.permissions or {},
            'joined_at': ut.joined_at.isoformat() if ut.joined_at else None,
            'last_accessed': ut.last_accessed.isoformat() if ut.last_accessed else None
        } for ut in user_tenants]), 200
        
    except Exception as e:
        logger.error(f"Error fetching user tenants: {e}")
        return jsonify({'error': 'Failed to fetch user tenants'}), 500

@tenant_management_bp.route('/switch-tenant/<tenant_id>', methods=['POST'])
@require_tenant
def switch_tenant(tenant_id):
    """Switch to a different tenant (if user has access)"""
    try:
        tenant_context = get_tenant_context()
        
        # Check if user has access to the requested tenant
        user_tenant = UserTenant.query.filter_by(
            user_id=tenant_context.user_id,
            tenant_id=tenant_id
        ).first()
        
        if not user_tenant:
            return jsonify({'error': 'Access denied to this tenant'}), 403
        
        # Update last accessed time
        user_tenant.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'tenant_id': tenant_id,
            'tenant_name': user_tenant.tenant.name if user_tenant.tenant else None,
            'role': user_tenant.role,
            'message': 'Successfully switched to tenant'
        }), 200
        
    except Exception as e:
        logger.error(f"Error switching tenant: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to switch tenant'}), 500












