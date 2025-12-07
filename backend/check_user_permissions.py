#!/usr/bin/env python3
"""Check user permissions and role"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import User, Role
from modules.core.permissions import Permission, RolePermission, PermissionManager

app = create_app()

with app.app_context():
    user_id = 28
    user = User.query.get(user_id)
    
    if user:
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role ID: {user.role_id}")
        
        if user.role:
            print(f"Role Name: {user.role.role_name}")
            print(f"Role Description: {user.role.description}")
        else:
            print("⚠️  User has no role assigned!")
        
        # Check permissions
        print("\n🔍 Checking permissions...")
        has_read = PermissionManager.user_has_permission(user_id, 'system.users.read')
        has_manage = PermissionManager.user_has_permission(user_id, 'system.roles.manage')
        
        print(f"Has system.users.read: {has_read}")
        print(f"Has system.roles.manage: {has_manage}")
        
        # Get all user permissions
        permissions = PermissionManager.get_user_permissions(user_id)
        print(f"\nTotal permissions: {len(permissions)}")
        for perm in permissions[:10]:  # Show first 10
            print(f"  - {perm.name}")
        
        # Check role permissions
        if user.role:
            print(f"\n🔍 Checking role permissions for role '{user.role.role_name}'...")
            role_perms = RolePermission.query.filter_by(role_id=user.role.id).all()
            print(f"Role has {len(role_perms)} permissions assigned")
            for rp in role_perms[:10]:
                perm = Permission.query.get(rp.permission_id)
                if perm:
                    print(f"  - {perm.name} (granted: {rp.granted})")
    else:
        print(f"❌ User {user_id} not found!")


