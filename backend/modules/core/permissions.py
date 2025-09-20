# backend/modules/core/permissions.py

from app import db
from modules.core.models import User, Role
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import get_jwt_identity, jwt_required
import logging

logger = logging.getLogger(__name__)

class Permission(db.Model):
    """Permission model for fine-grained access control"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    module = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Permission {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'module': self.module,
            'action': self.action,
            'resource': self.resource,
            'description': self.description
        }

class RolePermission(db.Model):
    """Junction table for role-permission relationships"""
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    granted = db.Column(db.Boolean, default=True)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    granted_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Relationships
    role = db.relationship('Role', backref='role_permissions')
    permission = db.relationship('Permission', backref='role_permissions')
    granted_by_user = db.relationship('User', foreign_keys=[granted_by])
    
    def __repr__(self):
        return f'<RolePermission {self.role.role_name} -> {self.permission.name}>'

class PermissionManager:
    """Utility class for permission management"""
    
    @staticmethod
    def user_has_permission(user_id, permission_name):
        """Check if a user has a specific permission"""
        try:
            user = User.query.get(user_id)
            if not user or not user.role:
                return False
            
            # Admin role has all permissions
            if user.role.role_name == 'admin':
                return True
            
            # Check if user's role has the specific permission
            permission = Permission.query.filter_by(name=permission_name).first()
            if not permission:
                logger.warning(f"Permission '{permission_name}' not found")
                return False
            
            role_permission = RolePermission.query.filter_by(
                role_id=user.role.id,
                permission_id=permission.id,
                granted=True
            ).first()
            
            return role_permission is not None
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    @staticmethod
    def user_has_module_access(user_id, module_name):
        """Check if user has any access to a module"""
        try:
            user = User.query.get(user_id)
            if not user or not user.role:
                return False
            
            # Admin role has all access
            if user.role.role_name == 'admin':
                return True
            
            # Check if user has any permission in the module
            permissions = db.session.query(Permission).join(
                RolePermission, Permission.id == RolePermission.permission_id
            ).filter(
                RolePermission.role_id == user.role.id,
                RolePermission.granted == True,
                Permission.module == module_name
            ).first()
            
            return permissions is not None
            
        except Exception as e:
            logger.error(f"Error checking module access: {e}")
            return False
    
    @staticmethod
    def get_user_permissions(user_id):
        """Get all permissions for a user"""
        try:
            user = User.query.get(user_id)
            if not user or not user.role:
                return []
            
            # Admin gets all permissions
            if user.role.role_name == 'admin':
                return Permission.query.all()
            
            # Get user's role permissions
            permissions = db.session.query(Permission).join(
                RolePermission, Permission.id == RolePermission.permission_id
            ).filter(
                RolePermission.role_id == user.role.id,
                RolePermission.granted == True
            ).all()
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    @staticmethod
    def get_user_modules(user_id):
        """Get all modules a user has access to"""
        try:
            permissions = PermissionManager.get_user_permissions(user_id)
            modules = list(set([perm.module for perm in permissions]))
            return modules
            
        except Exception as e:
            logger.error(f"Error getting user modules: {e}")
            return []

# Decorators for permission checking
def require_permission(permission_name):
    """Decorator to require a specific permission"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                # Handle different JWT identity formats
                if isinstance(current_user_id, str) and current_user_id == 'admin@edonuops.com':
                    # Hardcoded admin case - has all permissions
                    return f(*args, **kwargs)
                
                if not PermissionManager.user_has_permission(current_user_id, permission_name):
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_permission': permission_name,
                        'message': f'This action requires the "{permission_name}" permission'
                    }), 403
                
                # Store user info in g for use in the route
                g.current_user_id = current_user_id
                g.required_permission = permission_name
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Permission check error: {e}")
                return jsonify({
                    'error': 'Permission check failed',
                    'message': 'Unable to verify permissions'
                }), 500
        
        return decorated_function
    return decorator

def require_module_access(module_name):
    """Decorator to require access to a specific module"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                # Handle different JWT identity formats
                if isinstance(current_user_id, str) and current_user_id == 'admin@edonuops.com':
                    # Hardcoded admin case - has all access
                    return f(*args, **kwargs)
                
                if not PermissionManager.user_has_module_access(current_user_id, module_name):
                    return jsonify({
                        'error': 'Module access denied',
                        'required_module': module_name,
                        'message': f'Access to the "{module_name}" module is required'
                    }), 403
                
                # Store user info in g for use in the route
                g.current_user_id = current_user_id
                g.required_module = module_name
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Module access check error: {e}")
                return jsonify({
                    'error': 'Module access check failed',
                    'message': 'Unable to verify module access'
                }), 500
        
        return decorated_function
    return decorator

def require_any_permission(*permission_names):
    """Decorator to require any of the specified permissions"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                # Handle different JWT identity formats
                if isinstance(current_user_id, str) and current_user_id == 'admin@edonuops.com':
                    # Hardcoded admin case - has all permissions
                    return f(*args, **kwargs)
                
                # Check if user has any of the required permissions
                has_permission = False
                for permission_name in permission_names:
                    if PermissionManager.user_has_permission(current_user_id, permission_name):
                        has_permission = True
                        break
                
                if not has_permission:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_permissions': list(permission_names),
                        'message': f'This action requires one of these permissions: {", ".join(permission_names)}'
                    }), 403
                
                # Store user info in g for use in the route
                g.current_user_id = current_user_id
                g.required_permissions = permission_names
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Permission check error: {e}")
                return jsonify({
                    'error': 'Permission check failed',
                    'message': 'Unable to verify permissions'
                }), 500
        
        return decorated_function
    return decorator

