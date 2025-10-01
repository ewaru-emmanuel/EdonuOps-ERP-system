#!/usr/bin/env python3
"""
Apply permissions middleware to the ERP system.
This script sets up the permission enforcement middleware.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.permission_models import Permission, Role, UserRole
from modules.core.user_models import User
from app import create_app
from functools import wraps
from flask import request, jsonify, g
import jwt

def require_permission(permission_name):
    """Decorator to require a specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user from JWT token
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                # Remove 'Bearer ' prefix if present
                if token.startswith('Bearer '):
                    token = token[7:]
                
                # Decode JWT token
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get('sub') or payload.get('user_id')
                
                if not user_id:
                    return jsonify({'error': 'Invalid token'}), 401
                
                # Get user
                user = User.query.filter_by(id=user_id).first()
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                # Check if user has required permission
                if not user_has_permission(user, permission_name):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Store user in g for use in route
                g.current_user = user
                
                return f(*args, **kwargs)
                
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                return jsonify({'error': 'Authentication error'}), 401
        
        return decorated_function
    return decorator

def require_role(role_name):
    """Decorator to require a specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user from JWT token
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                # Remove 'Bearer ' prefix if present
                if token.startswith('Bearer '):
                    token = token[7:]
                
                # Decode JWT token
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get('sub') or payload.get('user_id')
                
                if not user_id:
                    return jsonify({'error': 'Invalid token'}), 401
                
                # Get user
                user = User.query.filter_by(id=user_id).first()
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                # Check if user has required role
                if not user_has_role(user, role_name):
                    return jsonify({'error': 'Insufficient role'}), 403
                
                # Store user in g for use in route
                g.current_user = user
                
                return f(*args, **kwargs)
                
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                return jsonify({'error': 'Authentication error'}), 401
        
        return decorated_function
    return decorator

def user_has_permission(user, permission_name):
    """Check if a user has a specific permission."""
    # Get user's roles
    user_roles = UserRole.query.filter_by(user_id=user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    # Get permission
    permission = Permission.query.filter_by(name=permission_name).first()
    if not permission:
        return False
    
    # Check if any of user's roles have this permission
    for role_id in role_ids:
        role_permission = UserRole.query.filter_by(
            role_id=role_id,
            permission_id=permission.id
        ).first()
        if role_permission:
            return True
    
    return False

def user_has_role(user, role_name):
    """Check if a user has a specific role."""
    # Get user's roles
    user_roles = UserRole.query.filter_by(user_id=user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    # Get role
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return False
    
    # Check if user has this role
    return role.id in role_ids

def get_user_permissions(user):
    """Get all permissions for a user."""
    # Get user's roles
    user_roles = UserRole.query.filter_by(user_id=user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    # Get all permissions for these roles
    permissions = []
    for role_id in role_ids:
        role_permissions = UserRole.query.filter_by(role_id=role_id).all()
        for rp in role_permissions:
            permission = Permission.query.filter_by(id=rp.permission_id).first()
            if permission and permission.name not in permissions:
                permissions.append(permission.name)
    
    return sorted(permissions)

def get_user_roles(user):
    """Get all roles for a user."""
    user_roles = UserRole.query.filter_by(user_id=user.id).all()
    roles = []
    
    for ur in user_roles:
        role = Role.query.filter_by(id=ur.role_id).first()
        if role:
            roles.append(role.name)
    
    return roles

def setup_permissions_middleware():
    """Setup the permissions middleware system."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Setting up permissions middleware...")
            
            # Create tables if they don't exist
            db.create_all()
            
            print("✅ Permissions middleware setup completed!")
            print("🎯 Middleware functions available:")
            print("  - require_permission(permission_name)")
            print("  - require_role(role_name)")
            print("  - user_has_permission(user, permission_name)")
            print("  - user_has_role(user, role_name)")
            print("  - get_user_permissions(user)")
            print("  - get_user_roles(user)")
            
        except Exception as e:
            print(f"❌ Error setting up permissions middleware: {e}")
            raise

if __name__ == "__main__":
    setup_permissions_middleware()







