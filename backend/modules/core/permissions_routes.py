# backend/modules/core/permissions_routes.py

from flask import Blueprint, request, jsonify, g, current_app
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
        
        # Handle superadmin/admin case - check if user has superadmin or admin role
        user = User.query.get(current_user_id)
        if user and user.role and user.role.role_name in ['superadmin', 'admin']:
            # Return all permissions for admin role
            all_permissions = Permission.query.all()
            return jsonify({
                'user_id': user.id,
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
        
        # Handle superadmin/admin case - check if user has superadmin or admin role
        user = User.query.get(current_user_id)
        if user and user.role and user.role.role_name in ['superadmin', 'admin']:
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
        
        # Handle superadmin/admin case - check if user has superadmin or admin role
        user = User.query.get(current_user_id)
        if user and user.role and user.role.role_name in ['superadmin', 'admin']:
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
@permissions_bp.route('', methods=['GET'])  # Also support root path
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
            # Superadmin and Admin roles get ALL permissions (no restrictions - top notch, no limit)
            if role.role_name in ['superadmin', 'admin']:
                # Return all permissions for superadmin/admin
                all_permissions = Permission.query.all()
                result.append({
                    'id': role.id,
                    'role_name': role.role_name,
                    'permission_count': len(all_permissions),
                    'permissions': [perm.to_dict() for perm in all_permissions],
                    'is_superadmin': role.role_name == 'superadmin'  # Flag to show all checked in UI
                })
            else:
                # Get permissions for other roles
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
        
        current_user_id_str = get_jwt_identity()
        current_user_id = None
        if current_user_id_str:
            try:
                current_user_id = int(current_user_id_str)
            except (ValueError, TypeError):
                current_user_id = None
        
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
                    granted_by=current_user_id
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

@permissions_bp.route('/roles', methods=['POST'])
@jwt_required()
def create_role():
    """Create a new role - Simple pattern like chart of accounts"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Get role name
        role_name = data.get('name') or data.get('role_name')
        if not role_name:
            return jsonify({'error': 'Role name is required'}), 400
        
        # Validate role name length
        if len(role_name) > 50:
            return jsonify({'error': 'Role name must be 50 characters or less'}), 400
        
        # Check if role already exists
        existing_role = Role.query.filter_by(role_name=role_name).first()
        if existing_role:
            return jsonify({'error': 'Role with this name already exists'}), 400
        
        # Create new role - simple pattern like chart of accounts
        new_role = Role(
            role_name=role_name,
            description=data.get('description', f'Role: {role_name}'),
            is_active=True
        )
        
        db.session.add(new_role)
        db.session.commit()
        
        # Return created role
        return jsonify({
            'message': 'Role created successfully',
            'role': {
                'id': new_role.id,
                'role_name': new_role.role_name,
                'description': new_role.description,
                'permissions': []
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating role: {e}", exc_info=True)
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Full traceback:\n{error_trace}")
        
        # Check for specific database errors
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower() or 'duplicate key' in error_msg.lower():
            return jsonify({
                'error': 'Role with this name already exists',
                'message': 'A role with this name already exists in the database'
            }), 400
        elif 'not null' in error_msg.lower():
            return jsonify({
                'error': 'Validation error',
                'message': 'Required fields are missing'
            }), 400
        
        return jsonify({
            'error': 'Failed to create role',
            'message': error_msg,
            'details': error_trace if current_app.config.get('DEBUG') else None
        }), 500

@permissions_bp.route('/roles/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """Update role name, description, and permissions - Simple pattern like chart of accounts"""
    try:
        # Force print to console - this will definitely show up
        print(f"\n{'='*60}")
        print(f"PUT /api/core/permissions/roles/{role_id}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Content-Type: {request.content_type}")
        
        data = request.get_json()
        print(f"Received data: {data}")
        print(f"Data type: {type(data)}")
        
        logger.info(f"PUT /roles/{role_id} - Received data: {data}")
        
        if not data:
            error_msg = 'Request body is required'
            print(f"ERROR: {error_msg}")
            logger.warning(f"PUT /roles/{role_id} - No request body provided")
            return jsonify({'error': error_msg}), 400
        
        role = Role.query.get(role_id)
        if not role:
            error_msg = f'Role not found: {role_id}'
            print(f"ERROR: {error_msg}")
            logger.warning(f"PUT /roles/{role_id} - Role not found")
            return jsonify({'error': error_msg}), 404
        
        # Only prevent renaming superadmin role (critical system role)
        # Allow renaming admin and other default roles as companies may want different names
        if role.role_name == 'superadmin' and ('name' in data or 'role_name' in data):
            error_msg = 'Cannot rename superadmin role'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Update role name if provided
        if 'name' in data or 'role_name' in data:
            new_role_name = data.get('name') or data.get('role_name')
            print(f"Attempting to update role name to: '{new_role_name}'")
            
            if not new_role_name:
                error_msg = f'Role name is required, got: {new_role_name}'
                print(f"ERROR: {error_msg}")
                logger.warning(f"PUT /roles/{role_id} - Invalid role name provided: {new_role_name}")
                return jsonify({'error': error_msg}), 400
            
            if not isinstance(new_role_name, str):
                error_msg = f'Role name must be a string, got {type(new_role_name)}: {new_role_name}'
                print(f"ERROR: {error_msg}")
                return jsonify({'error': error_msg}), 400
            
            new_role_name = new_role_name.strip()
            if len(new_role_name) == 0:
                error_msg = 'Role name cannot be empty'
                print(f"ERROR: {error_msg}")
                return jsonify({'error': error_msg}), 400
            
            if new_role_name != role.role_name:
                # Check if new name already exists
                existing_role = Role.query.filter_by(role_name=new_role_name).first()
                if existing_role and existing_role.id != role_id:
                    error_msg = f'Role with name "{new_role_name}" already exists'
                    print(f"ERROR: {error_msg}")
                    logger.warning(f"PUT /roles/{role_id} - Role name '{new_role_name}' already exists")
                    return jsonify({'error': error_msg}), 400
                role.role_name = new_role_name
                print(f"✓ Updated role name to '{new_role_name}'")
                logger.info(f"PUT /roles/{role_id} - Updated role name to '{new_role_name}'")
        
        # Update description if provided
        if 'description' in data:
            role.description = data.get('description')
        
        # Update permissions if provided
        if 'permissions' in data:
            permission_ids = data.get('permissions', [])
            
            # Validate permission_ids is a list
            if not isinstance(permission_ids, list):
                logger.warning(f"PUT /roles/{role_id} - permissions must be a list, got {type(permission_ids)}")
                return jsonify({'error': 'permissions must be an array of permission IDs'}), 400
            
            # Validate all permission IDs are integers
            try:
                permission_ids = [int(pid) for pid in permission_ids if pid is not None]
            except (ValueError, TypeError) as e:
                logger.warning(f"PUT /roles/{role_id} - Invalid permission IDs: {e}")
                return jsonify({'error': 'All permission IDs must be valid integers'}), 400
            
            # Get user ID from JWT (already verified by @jwt_required())
            current_user_id_str = get_jwt_identity()
            current_user_id = None
            if current_user_id_str:
                try:
                    current_user_id = int(current_user_id_str)
                except (ValueError, TypeError):
                    current_user_id = None
            
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
                        granted_by=current_user_id
                    )
                    db.session.add(role_permission)
                else:
                    logger.warning(f"PUT /roles/{role_id} - Permission ID {permission_id} not found, skipping")
        
        db.session.commit()
        print(f"✓ Database committed successfully")
        
        # Get updated permissions
        permissions = db.session.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.role_id == role_id,
            RolePermission.granted == True
        ).all()
        
        result = {
            'message': f'Role updated successfully',
            'role': {
                'id': role.id,
                'role_name': role.role_name,
                'description': role.description,
                'permissions': [perm.to_dict() for perm in permissions]
            }
        }
        
        print(f"✓ SUCCESS: Role {role_id} updated successfully")
        print(f"Response: {result}")
        print(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        print(f"\n{'='*60}")
        print(f"❌ EXCEPTION in PUT /api/core/permissions/roles/{role_id}")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e).__name__}")
        print(f"Traceback:\n{error_trace}")
        print(f"{'='*60}\n")
        
        logger.error(f"Error updating role {role_id}: {e}", exc_info=True)
        logger.error(f"Full traceback: {error_trace}")
        db.session.rollback()
        
        error_response = {
            'error': f'Failed to update role: {str(e)}',
            'error_type': type(e).__name__,
            'message': str(e)
        }
        
        # Include traceback in debug mode
        if current_app.config.get('DEBUG'):
            error_response['details'] = error_trace
        
        return jsonify(error_response), 500

@permissions_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """Delete a role (admin only)"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        # Only prevent deletion of superadmin role (critical system role)
        # Allow deletion of admin and other default roles as companies may want different names
        if role.role_name == 'superadmin':
            return jsonify({'error': 'Cannot delete superadmin role'}), 400
        
        # Check if role is assigned to any users
        users_with_role = User.query.filter_by(role_id=role_id).count()
        if users_with_role > 0:
            return jsonify({
                'error': f'Cannot delete role. {users_with_role} user(s) are assigned to this role.'
            }), 400
        
        # Delete role permissions first
        RolePermission.query.filter_by(role_id=role_id).delete()
        
        # Delete role
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({
            'message': f'Role {role.role_name} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete role'}), 500

