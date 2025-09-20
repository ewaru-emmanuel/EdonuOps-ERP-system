# backend/modules/core/user_management_routes.py

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from modules.core.models import User, Role, Organization
from modules.core.permissions import require_permission, PermissionManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/users', methods=['GET'])
@require_permission('system.users.read')
def get_all_users():
    """Get all users with their roles and permissions"""
    try:
        users = User.query.all()
        result = []
        
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.role_name if user.role else None,
                'role_id': user.role_id,
                'organization': user.organization.name if user.organization else None,
                'organization_id': user.organization_id,
                'is_active': getattr(user, 'is_active', True),
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
                'last_login': user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None
            }
            
            # Get user's permission count
            permissions = PermissionManager.get_user_permissions(user.id)
            user_data['permission_count'] = len(permissions)
            user_data['modules'] = PermissionManager.get_user_modules(user.id)
            
            result.append(user_data)
        
        return jsonify({
            'users': result,
            'total_count': len(result)
        })
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({'error': 'Failed to get users'}), 500

@user_management_bp.route('/users', methods=['POST'])
@require_permission('system.users.create')
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Validate role exists
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Hash password
        password_hash = generate_password_hash(data['password'])
        
        # Create user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash,
            role_id=data['role_id'],
            organization_id=data.get('organization_id', 1)  # Default organization
        )
        
        db.session.add(new_user)
        db.session.commit()
        
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
    """Get specific user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's permissions
        permissions = PermissionManager.get_user_permissions(user_id)
        modules = PermissionManager.get_user_modules(user_id)
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.role_name if user.role else None,
            'role_id': user.role_id,
            'organization': user.organization.name if user.organization else None,
            'organization_id': user.organization_id,
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
    """Update user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'username' in data:
            # Check if username already exists (excluding current user)
            existing = User.query.filter(
                User.username == data['username'],
                User.id != user_id
            ).first()
            if existing:
                return jsonify({'error': 'Username already exists'}), 409
            user.username = data['username']
        
        if 'email' in data:
            # Check if email already exists (excluding current user)
            existing = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists'}), 409
            user.email = data['email']
        
        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({'error': 'Invalid role'}), 400
            user.role_id = data['role_id']
        
        if 'organization_id' in data:
            user.organization_id = data['organization_id']
        
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        if 'is_active' in data:
            if hasattr(user, 'is_active'):
                user.is_active = data['is_active']
        
        db.session.commit()
        
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
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting the last admin
        if user.role and user.role.role_name == 'admin':
            admin_count = User.query.join(Role).filter(Role.role_name == 'admin').count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last admin user'}), 400
        
        # Store user info for response
        deleted_user_info = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User deleted successfully',
            'deleted_user': deleted_user_info
        })
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500

@user_management_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@require_permission('system.users.update')
def activate_user(user_id):
    """Activate a user"""
    try:
        user = User.query.get(user_id)
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
    """Deactivate a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deactivating the last admin
        if user.role and user.role.role_name == 'admin':
            active_admin_count = User.query.join(Role).filter(
                Role.role_name == 'admin',
                User.id != user_id
            ).count()
            if active_admin_count == 0:
                return jsonify({'error': 'Cannot deactivate the last admin user'}), 400
        
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
@require_permission('system.roles.manage')
def get_all_roles():
    """Get all roles with permission counts"""
    try:
        roles = Role.query.all()
        result = []
        
        for role in roles:
            # Count users with this role
            user_count = User.query.filter_by(role_id=role.id).count()
            
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
        organizations = Organization.query.all()
        result = []
        
        for org in organizations:
            user_count = User.query.filter_by(organization_id=org.id).count()
            
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
@require_permission('system.users.read')
def get_user_stats():
    """Get user management statistics"""
    try:
        # Total users
        total_users = User.query.count()
        
        # Active users (if is_active column exists)
        try:
            active_users = User.query.filter_by(is_active=True).count()
        except:
            active_users = total_users  # Fallback if column doesn't exist
        
        # Users by role
        role_stats = db.session.query(
            Role.role_name,
            db.func.count(User.id).label('user_count')
        ).outerjoin(User).group_by(Role.id, Role.role_name).all()
        
        # Recent logins (last 7 days)
        try:
            from datetime import datetime, timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_logins = User.query.filter(
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
