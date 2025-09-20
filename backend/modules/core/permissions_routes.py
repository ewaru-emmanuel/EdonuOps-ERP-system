# backend/modules/core/permissions_routes.py

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from modules.core.models import User, Role
from modules.core.permissions import Permission, RolePermission, PermissionManager, require_permission
import logging

logger = logging.getLogger(__name__)

permissions_bp = Blueprint('permissions', __name__)

@permissions_bp.route('/user/permissions', methods=['GET'])
@jwt_required()
def get_current_user_permissions():
    """Get current user's permissions"""
    try:
        current_user_id = get_jwt_identity()
        
        # Handle hardcoded admin case
        if isinstance(current_user_id, str) and current_user_id == 'admin@edonuops.com':
            # Return all permissions for hardcoded admin
            all_permissions = Permission.query.all()
            return jsonify({
                'user_id': 'admin',
                'role': 'admin',
                'permissions': [perm.to_dict() for perm in all_permissions],
                'modules': list(set([perm.module for perm in all_permissions]))
            })
        
        # Get user and permissions
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        permissions = PermissionManager.get_user_permissions(current_user_id)
        modules = PermissionManager.get_user_modules(current_user_id)
        
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.role_name if user.role else None,
            'permissions': [perm.to_dict() for perm in permissions],
            'modules': modules
        })
        
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        return jsonify({'error': 'Failed to get user permissions'}), 500

@permissions_bp.route('/user/<int:user_id>/permissions', methods=['GET'])
@require_permission('system.users.read')
def get_user_permissions(user_id):
    """Get specific user's permissions (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        permissions = PermissionManager.get_user_permissions(user_id)
        modules = PermissionManager.get_user_modules(user_id)
        
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.role_name if user.role else None,
            'permissions': [perm.to_dict() for perm in permissions],
            'modules': modules
        })
        
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        return jsonify({'error': 'Failed to get user permissions'}), 500

@permissions_bp.route('/check', methods=['POST'])
@jwt_required()
def check_permission():
    """Check if current user has specific permission"""
    try:
        data = request.get_json()
        permission_name = data.get('permission')
        
        if not permission_name:
            return jsonify({'error': 'Permission name required'}), 400
        
        current_user_id = get_jwt_identity()
        
        # Handle hardcoded admin case
        if isinstance(current_user_id, str) and current_user_id == 'admin@edonuops.com':
            return jsonify({
                'has_permission': True,
                'permission': permission_name,
                'reason': 'admin_access'
            })
        
        has_permission = PermissionManager.user_has_permission(current_user_id, permission_name)
        
        return jsonify({
            'has_permission': has_permission,
            'permission': permission_name,
            'user_id': current_user_id
        })
        
    except Exception as e:
        logger.error(f"Error checking permission: {e}")
        return jsonify({'error': 'Failed to check permission'}), 500

@permissions_bp.route('/check/module', methods=['POST'])
@jwt_required()
def check_module_access():
    """Check if current user has access to specific module"""
    try:
        data = request.get_json()
        module_name = data.get('module')
        
        if not module_name:
            return jsonify({'error': 'Module name required'}), 400
        
        current_user_id = get_jwt_identity()
        
        # Handle hardcoded admin case
        if isinstance(current_user_id, str) and current_user_id == 'admin@edonuops.com':
            return jsonify({
                'has_access': True,
                'module': module_name,
                'reason': 'admin_access'
            })
        
        has_access = PermissionManager.user_has_module_access(current_user_id, module_name)
        
        return jsonify({
            'has_access': has_access,
            'module': module_name,
            'user_id': current_user_id
        })
        
    except Exception as e:
        logger.error(f"Error checking module access: {e}")
        return jsonify({'error': 'Failed to check module access'}), 500

@permissions_bp.route('/all', methods=['GET'])
@require_permission('system.roles.manage')
def get_all_permissions():
    """Get all available permissions (admin only)"""
    try:
        permissions = Permission.query.order_by(Permission.module, Permission.name).all()
        
        # Group by module
        modules = {}
        for perm in permissions:
            if perm.module not in modules:
                modules[perm.module] = []
            modules[perm.module].append(perm.to_dict())
        
        return jsonify({
            'permissions': [perm.to_dict() for perm in permissions],
            'modules': modules,
            'total_count': len(permissions)
        })
        
    except Exception as e:
        logger.error(f"Error getting all permissions: {e}")
        return jsonify({'error': 'Failed to get permissions'}), 500

@permissions_bp.route('/roles', methods=['GET'])
@require_permission('system.roles.manage')
def get_roles_with_permissions():
    """Get all roles with their permissions (admin only)"""
    try:
        roles = Role.query.all()
        result = []
        
        for role in roles:
            # Get permissions for this role
            permissions = db.session.query(Permission).join(
                RolePermission, Permission.id == RolePermission.permission_id
            ).filter(
                RolePermission.role_id == role.id,
                RolePermission.granted == True
            ).all()
            
            result.append({
                'id': role.id,
                'role_name': role.role_name,
                'permission_count': len(permissions),
                'permissions': [perm.to_dict() for perm in permissions]
            })
        
        return jsonify({
            'roles': result,
            'total_roles': len(roles)
        })
        
    except Exception as e:
        logger.error(f"Error getting roles with permissions: {e}")
        return jsonify({'error': 'Failed to get roles with permissions'}), 500

@permissions_bp.route('/role/<int:role_id>/permissions', methods=['POST'])
@require_permission('system.roles.manage')
def update_role_permissions(role_id):
    """Update permissions for a role (admin only)"""
    try:
        data = request.get_json()
        permission_ids = data.get('permission_ids', [])
        
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        current_user_id = get_jwt_identity()
        
        # Remove existing permissions
        RolePermission.query.filter_by(role_id=role_id).delete()
        
        # Add new permissions
        for permission_id in permission_ids:
            permission = Permission.query.get(permission_id)
            if permission:
                role_permission = RolePermission(
                    role_id=role_id,
                    permission_id=permission_id,
                    granted=True,
                    granted_by=current_user_id if isinstance(current_user_id, int) else None
                )
                db.session.add(role_permission)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Updated permissions for role {role.role_name}',
            'role_id': role_id,
            'permission_count': len(permission_ids)
        })
        
    except Exception as e:
        logger.error(f"Error updating role permissions: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update role permissions'}), 500

