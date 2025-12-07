# backend/modules/core/user_management_routes.py

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from modules.core.models import User, Role, Organization
from modules.core.permissions import require_permission, PermissionManager
from modules.core.tenant_helpers import get_current_user_tenant_id, get_current_user_id
from modules.core.tenant_query_helper import tenant_query
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

user_management_bp = Blueprint('user_management', __name__)

# Test endpoint to verify JWT is working
@user_management_bp.route('/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt():
    """Test endpoint to verify JWT authentication is working"""
    try:
        current_user_id = get_jwt_identity()
        return jsonify({
            'success': True,
            'user_id': current_user_id,
            'message': 'JWT authentication is working'
        }), 200
    except Exception as e:
        logger.error(f"JWT test error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'JWT authentication failed'
        }), 401

@user_management_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users with their roles and permissions - STRICT TENANT ISOLATION"""
    try:
        # Get current user ID from JWT (already verified by @jwt_required())
        try:
            current_user_id = get_jwt_identity()
        except Exception as jwt_error:
            logger.error(f"JWT error in get_all_users: {jwt_error}")
            return jsonify({'error': 'JWT token error', 'message': str(jwt_error)}), 401
        
        if not current_user_id:
            return jsonify({'error': 'Authentication required', 'message': 'User ID not found in JWT token'}), 401
        
        # Get user and check if admin
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Superadmin/Admin bypass - can view users without explicit permission
        is_admin = user.role and user.role.role_name in ['superadmin', 'admin']
        
        # Non-admin users need system.users.read permission
        if not is_admin:
            if not PermissionManager.user_has_permission(current_user_id, 'system.users.read'):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': 'This action requires the "system.users.read" permission'
                }), 403
        
        # STRICT TENANT ISOLATION: Automatic tenant filtering
        users = tenant_query(User).all()
        tenant_id = get_current_user_tenant_id() or 'default'
        logger.debug(f"Found {len(users)} users for tenant {tenant_id}")
        result = []
        
        for user in users:
            # Safely get organization info if it exists
            organization_name = None
            organization_id = None
            try:
                # Check if user has organization_id attribute (column exists)
                if hasattr(user, 'organization_id') and user.organization_id:
                    organization_id = user.organization_id
                    # Try to get organization name if Organization model exists
                    try:
                        from modules.core.models import Organization
                        org = Organization.query.get(user.organization_id)
                        if org:
                            organization_name = org.name
                    except Exception as org_err:
                        logger.debug(f"Could not fetch organization for user {user.id}: {org_err}")
                        pass
                # Note: User model does not have 'organization' relationship defined
                # So we don't check for user.organization
            except Exception as org_err:
                logger.debug(f"Error getting organization info for user {user.id}: {org_err}")
                pass
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.role_name if (hasattr(user, 'role') and user.role) else None,
                'role_id': user.role_id,
                'organization': organization_name,
                'organization_id': organization_id,
                'is_active': getattr(user, 'is_active', True),
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
                'last_login': user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None
            }
            
            # Get user's permission count - PermissionManager is imported at top of file
            try:
                permissions = PermissionManager.get_user_permissions(user.id)
                user_data['permission_count'] = len(permissions) if permissions else 0
                user_data['modules'] = PermissionManager.get_user_modules(user.id) if permissions else []
            except Exception as perm_err:
                import traceback
                error_trace = traceback.format_exc()
                logger.warning(f"Error getting permissions for user {user.id}: {perm_err}")
                logger.debug(f"Permission error traceback: {error_trace}")
                user_data['permission_count'] = 0
                user_data['modules'] = []
            
            result.append(user_data)
        
        return jsonify({
            'users': result,
            'total_count': len(result)
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error getting users: {e}")
        logger.error(f"Traceback: {error_trace}")
        return jsonify({
            'error': 'Failed to get users',
            'message': str(e),
            'traceback': error_trace
        }), 500

@user_management_bp.route('/users', methods=['POST'])
@require_permission('system.users.create')
def create_user():
    """Create a new user - STRICT TENANT ISOLATION"""
    try:
        # STRICT TENANT ISOLATION: Get tenant_id for assignment
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            logger.warning("User has no tenant_id - cannot create users without tenant context")
            return jsonify({
                'error': 'Tenant context required',
                'message': 'User must belong to a tenant to create users'
            }), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # STRICT TENANT ISOLATION: Check if username or email already exists within same tenant
        existing_user = tenant_query(User).filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username or email already exists in your organization'}), 409
        
        # Validate role exists
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Hash password
        password_hash = generate_password_hash(data['password'])
        
        # Create user with tenant_id
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password_hash': password_hash,
            'role_id': data['role_id'],
            'tenant_id': tenant_id  # STRICT TENANT ISOLATION: Assign to current user's tenant
        }
        
        # Only add organization_id if User model supports it
        if hasattr(User, 'organization_id'):
            user_data['organization_id'] = data.get('organization_id', 1)  # Default organization
        
        new_user = User(**user_data)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log user creation to audit trail
        try:
            from services.audit_logger_service import audit_logger
            from flask import request
            current_user_id = request.headers.get('X-User-ID')
            if not current_user_id:
                from flask_jwt_extended import get_jwt_identity
                try:
                    current_user_id = get_jwt_identity()
                except:
                    current_user_id = None
            
            if audit_logger and current_user_id:
                audit_logger.log_action(
                    action='CREATE',
                    entity_type='user',
                    entity_id=str(new_user.id),
                    new_values={'username': new_user.username, 'email': new_user.email, 'role_id': new_user.role_id},
                    module='admin',
                    user_id=int(current_user_id)
                )
        except Exception as audit_err:
            logger.warning(f"Failed to log user creation to audit trail: {audit_err}")
        
        # Create default accounts automatically for new user
        try:
            from modules.finance.default_accounts_service import create_default_accounts
            logger.info(f"Creating default accounts for new user {new_user.id}...")
            result = create_default_accounts(new_user.id, force=False)
            logger.info(f"Created {result['new_count']} default accounts for user {new_user.id}")
        except Exception as e:
            logger.warning(f"Failed to create default accounts for user {new_user.id}: {e}")
            # Don't fail user creation if account creation fails - can be created later
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': role.role_name
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create user'}), 500

@user_management_bp.route('/users/<int:user_id>', methods=['GET'])
@require_permission('system.users.read')
def get_user(user_id):
    """Get specific user details - STRICT TENANT ISOLATION"""
    try:
        # STRICT TENANT ISOLATION: Automatic tenant filtering
        user = tenant_query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's permissions
        permissions = PermissionManager.get_user_permissions(user_id)
        modules = PermissionManager.get_user_modules(user_id)
        
        # Safely get organization info if it exists
        organization_name = None
        organization_id = None
        try:
            # Check if user has organization_id attribute (column exists)
            if hasattr(user, 'organization_id') and user.organization_id:
                organization_id = user.organization_id
                # Try to get organization name if Organization model exists
                try:
                    from modules.core.models import Organization
                    org = Organization.query.get(user.organization_id)
                    if org:
                        organization_name = org.name
                except Exception as org_err:
                    logger.debug(f"Could not fetch organization for user {user.id}: {org_err}")
                    pass
            # Note: User model does not have 'organization' relationship defined
            # So we don't check for user.organization
        except Exception as org_err:
            logger.debug(f"Error getting organization info for user {user.id}: {org_err}")
            pass
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.role_name if user.role else None,
            'role_id': user.role_id,
            'organization': organization_name,
            'organization_id': organization_id,
            'is_active': getattr(user, 'is_active', True),
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
            'last_login': user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
            'permissions': [perm.to_dict() for perm in permissions],
            'modules': modules,
            'permission_count': len(permissions)
        })
        
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return jsonify({'error': 'Failed to get user'}), 500

@user_management_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_permission('system.users.update')
def update_user(user_id):
    """Update user information - STRICT TENANT ISOLATION"""
    try:
        # STRICT TENANT ISOLATION: Get tenant_id for validation
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            logger.warning("User has no tenant_id - cannot update user without tenant context")
            return jsonify({
                'error': 'Tenant context required',
                'message': 'User must belong to a tenant to update users'
            }), 403
        
        # STRICT TENANT ISOLATION: Automatic tenant filtering
        user = tenant_query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'username' in data:
            # STRICT TENANT ISOLATION: Check if username already exists within same tenant (excluding current user)
            existing = tenant_query(User).filter(
                User.username == data['username'],
                User.id != user_id
            ).first()
            if existing:
                return jsonify({'error': 'Username already exists in your organization'}), 409
            user.username = data['username']
        
        if 'email' in data:
            # STRICT TENANT ISOLATION: Check if email already exists within same tenant (excluding current user)
            existing = tenant_query(User).filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists in your organization'}), 409
            user.email = data['email']
        
        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({'error': 'Invalid role'}), 400
            user.role_id = data['role_id']
        
        if 'organization_id' in data and hasattr(user, 'organization_id'):
            user.organization_id = data['organization_id']
        
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        if 'is_active' in data:
            if hasattr(user, 'is_active'):
                user.is_active = data['is_active']
        
        # Track old values for audit log
        old_values = {
            'username': user.username,
            'email': user.email,
            'role_id': user.role_id,
            'is_active': getattr(user, 'is_active', True)
        }
        
        db.session.commit()
        
        # Log user update to audit trail
        try:
            from services.audit_logger_service import audit_logger
            from flask import request
            current_user_id = request.headers.get('X-User-ID')
            if not current_user_id:
                from flask_jwt_extended import get_jwt_identity
                try:
                    current_user_id = get_jwt_identity()
                except:
                    current_user_id = None
            
            if audit_logger and current_user_id:
                new_values = {
                    'username': user.username,
                    'email': user.email,
                    'role_id': user.role_id,
                    'is_active': getattr(user, 'is_active', True)
                }
                # Only log if there were actual changes
                if old_values != new_values:
                    audit_logger.log_action(
                        action='UPDATE',
                        entity_type='user',
                        entity_id=str(user_id),
                        old_values=old_values,
                        new_values=new_values,
                        module='admin',
                        user_id=int(current_user_id)
                    )
        except Exception as audit_err:
            logger.warning(f"Failed to log user update to audit trail: {audit_err}")
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.role_name if user.role else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user'}), 500

@user_management_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_permission('system.users.delete')
def delete_user(user_id):
    """Delete a user - STRICT TENANT ISOLATION"""
    try:
        # STRICT TENANT ISOLATION: Get tenant_id for validation
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            logger.warning("User has no tenant_id - cannot delete user without tenant context")
            return jsonify({
                'error': 'Tenant context required',
                'message': 'User must belong to a tenant to delete users'
            }), 403
        
        # STRICT TENANT ISOLATION: Automatic tenant filtering
        user = tenant_query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Track user data for audit log before deletion
        user_data = {
            'username': user.username,
            'email': user.email,
            'role_id': user.role_id,
            'is_active': getattr(user, 'is_active', True)
        }
        
        db.session.delete(user)
        db.session.commit()
        
        # Log user deletion to audit trail
        try:
            from services.audit_logger_service import audit_logger
            current_user_id = request.headers.get('X-User-ID')
            if not current_user_id:
                try:
                    current_user_id = get_jwt_identity()
                except:
                    current_user_id = None
            
            if audit_logger and current_user_id:
                audit_logger.log_action(
                    action='DELETE',
                    entity_type='user',
                    entity_id=str(user_id),
                    old_values=user_data,
                    module='admin',
                    user_id=int(current_user_id)
                )
        except Exception as audit_err:
            logger.warning(f"Failed to log user deletion to audit trail: {audit_err}")
        
        # Prevent deleting the last superadmin/admin within the same tenant
        if user.role and user.role.role_name in ['superadmin', 'admin']:
            admin_count = tenant_query(User).join(Role).filter(
                Role.role_name.in_(['superadmin', 'admin'])
            ).count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last admin user in your organization'}), 400
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500

@user_management_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@require_permission('system.users.update')
def activate_user(user_id):
    """Activate a user - STRICT TENANT ISOLATION"""
    try:
        # STRICT TENANT ISOLATION: Automatic tenant filtering
        user = tenant_query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if hasattr(user, 'is_active'):
            user.is_active = True
            db.session.commit()
        
        return jsonify({
            'message': 'User activated successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Error activating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to activate user'}), 500

@user_management_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@require_permission('system.users.update')
def deactivate_user(user_id):
    """Deactivate a user - STRICT TENANT ISOLATION"""
    try:
        # STRICT TENANT ISOLATION: Get tenant_id for validation
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'User must belong to a tenant to deactivate users'
            }), 403
        
        # STRICT TENANT ISOLATION: Automatic tenant filtering
        user = tenant_query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deactivating the last admin within the same tenant
        if user.role and user.role.role_name == 'admin':
            active_admin_count = tenant_query(User).join(Role).filter(
                Role.role_name == 'admin',
                User.id != user_id
            ).count()
            if active_admin_count == 0:
                return jsonify({'error': 'Cannot deactivate the last admin user in your organization'}), 400
        
        if hasattr(user, 'is_active'):
            user.is_active = False
            db.session.commit()
        
        return jsonify({
            'message': 'User deactivated successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Error deactivating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to deactivate user'}), 500

@user_management_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_all_roles():
    """Get all roles with permission counts - STRICT TENANT ISOLATION"""
    try:
        # Get current user ID from JWT (already verified by @jwt_required())
        try:
            current_user_id = get_jwt_identity()
        except Exception as jwt_error:
            logger.error(f"JWT error in get_all_roles: {jwt_error}")
            return jsonify({'error': 'JWT token error', 'message': str(jwt_error)}), 401
        
        if not current_user_id:
            return jsonify({'error': 'Authentication required', 'message': 'User ID not found in JWT token'}), 401
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admin bypass - admin can view roles without explicit permission
        is_admin = user.role and user.role.role_name == 'admin'
        
        # Non-admin users need system.roles.manage permission
        if not is_admin:
            # PermissionManager is imported at top of file
            if not PermissionManager.user_has_permission(current_user_id, 'system.roles.manage'):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': 'This action requires the "system.roles.manage" permission'
                }), 403
        
        roles = Role.query.all()
        result = []
        
        for role in roles:
            # STRICT TENANT ISOLATION: Count users with this role within same tenant
            user_count = tenant_query(User).filter_by(role_id=role.id).count()
            
            # Get permissions count (simplified)
            try:
                from modules.core.permissions import Permission, RolePermission
                permission_count = db.session.query(RolePermission).filter_by(role_id=role.id).count()
            except Exception:
                permission_count = 0
            
            result.append({
                'id': role.id,
                'role_name': role.role_name,
                'permission_count': permission_count,
                'user_count': user_count,
                'permissions': getattr(role, 'permissions', None)
            })
        
        return jsonify({
            'roles': result,
            'total_count': len(result)
        })
        
    except Exception as e:
        logger.error(f"Error getting roles: {e}")
        return jsonify({'error': 'Failed to get roles'}), 500

@user_management_bp.route('/organizations', methods=['GET'])
@require_permission('system.users.read')
def get_organizations():
    """Get all organizations"""
    try:
        from modules.core.models import Organization
        organizations = Organization.query.all()
        result = []
        
        for org in organizations:
            # Check if User model has organization_id field
            if hasattr(User, 'organization_id'):
                user_count = User.query.filter_by(organization_id=org.id).count()
            else:
                user_count = 0  # Organization not linked to users
            
            result.append({
                'id': org.id,
                'name': org.name,
                'user_count': user_count,
                'created_at': org.created_at.isoformat() if org.created_at else None
            })
        
        return jsonify({
            'organizations': result,
            'total_count': len(result)
        })
        
    except Exception as e:
        logger.error(f"Error getting organizations: {e}")
        return jsonify({'error': 'Failed to get organizations'}), 500

@user_management_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@require_permission('system.users.update')
def reset_user_password(user_id):
    """Reset user password (admin only)"""
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Hash new password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({
            'message': 'Password reset successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to reset password'}), 500

@user_management_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user management statistics - STRICT TENANT ISOLATION"""
    try:
        # Get current user ID from JWT (already verified by @jwt_required())
        try:
            current_user_id = get_jwt_identity()
        except Exception as jwt_error:
            logger.error(f"JWT error in get_user_stats: {jwt_error}")
            return jsonify({'error': 'JWT token error', 'message': str(jwt_error)}), 401
        
        if not current_user_id:
            return jsonify({'error': 'Authentication required', 'message': 'User ID not found in JWT token'}), 401
        
        # Get user and check if admin
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admin bypass - admin can view stats without explicit permission
        is_admin = user.role and user.role.role_name == 'admin'
        
        # Non-admin users need system.users.read permission
        if not is_admin:
            if not PermissionManager.user_has_permission(current_user_id, 'system.users.read'):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': 'This action requires the "system.users.read" permission'
                }), 403
        
        # STRICT TENANT ISOLATION: Automatic tenant filtering
        # Total users in tenant
        total_users = tenant_query(User).count()
        
        # Active users (if is_active column exists)
        try:
            active_users = tenant_query(User).filter_by(is_active=True).count()
        except:
            active_users = total_users  # Fallback if column doesn't exist
        
        # Users by role within tenant
        tenant_id = get_current_user_tenant_id()
        role_stats = db.session.query(
            Role.role_name,
            db.func.count(User.id).label('user_count')
        ).join(User).filter(
            User.tenant_id == tenant_id  # Required for join query
        ).group_by(Role.id, Role.role_name).all()
        
        # Recent logins (last 7 days) within tenant
        try:
            from datetime import datetime, timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_logins = tenant_query(User).filter(
                User.last_login >= seven_days_ago
            ).count()
        except:
            recent_logins = 0  # Fallback if column doesn't exist
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'recent_logins': recent_logins,
            'role_distribution': [
                {'role': role, 'count': count} 
                for role, count in role_stats
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return jsonify({'error': 'Failed to get user stats'}), 500
