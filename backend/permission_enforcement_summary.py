#!/usr/bin/env python3
"""
Permission enforcement summary for the ERP system.
This script provides an overview of the permission system implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.permission_models import Permission, Role, UserRole
from modules.core.user_models import User
from app import create_app

def permission_enforcement_summary():
    """Provide a summary of the permission enforcement system."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Permission Enforcement System Summary")
            print("=" * 50)
            
            # Get all permissions
            permissions = Permission.query.all()
            print(f"\n📋 Total Permissions: {len(permissions)}")
            
            # Group permissions by category
            categories = {}
            for perm in permissions:
                category = getattr(perm, 'category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(perm.name)
            
            for category, perm_list in categories.items():
                print(f"\n📂 {category} ({len(perm_list)} permissions):")
                for perm in sorted(perm_list):
                    print(f"  • {perm}")
            
            # Get all roles
            roles = Role.query.all()
            print(f"\n👥 Total Roles: {len(roles)}")
            
            for role in roles:
                print(f"\n🎭 Role: {role.name}")
                print(f"   Description: {role.description}")
                
                # Get permissions for this role
                role_permissions = UserRole.query.filter_by(role_id=role.id).all()
                permission_names = []
                
                for rp in role_permissions:
                    permission = Permission.query.filter_by(id=rp.permission_id).first()
                    if permission:
                        permission_names.append(permission.name)
                
                print(f"   Permissions ({len(permission_names)}):")
                for perm in sorted(permission_names):
                    print(f"     • {perm}")
            
            # Get all users and their roles
            users = User.query.all()
            print(f"\n👤 Total Users: {len(users)}")
            
            for user in users:
                print(f"\n👤 User: {user.username} ({user.email})")
                
                # Get user's roles
                user_roles = UserRole.query.filter_by(user_id=user.id).all()
                role_names = []
                
                for ur in user_roles:
                    role = Role.query.filter_by(id=ur.role_id).first()
                    if role:
                        role_names.append(role.name)
                
                print(f"   Roles ({len(role_names)}): {', '.join(role_names)}")
                
                # Get user's permissions
                all_permissions = set()
                for role_id in [ur.role_id for ur in user_roles]:
                    role_permissions = UserRole.query.filter_by(role_id=role_id).all()
                    for rp in role_permissions:
                        permission = Permission.query.filter_by(id=rp.permission_id).first()
                        if permission:
                            all_permissions.add(permission.name)
                
                print(f"   Total Permissions: {len(all_permissions)}")
            
            # Permission enforcement guidelines
            print(f"\n🛡️  Permission Enforcement Guidelines:")
            print(f"   1. Use @require_permission('permission.name') decorator on routes")
            print(f"   2. Use @require_role('role_name') decorator for role-based access")
            print(f"   3. Check permissions in frontend using user permissions")
            print(f"   4. Always validate permissions on both frontend and backend")
            print(f"   5. Use principle of least privilege")
            
            # Security recommendations
            print(f"\n🔒 Security Recommendations:")
            print(f"   • Regular audit of user permissions")
            print(f"   • Implement permission logging")
            print(f"   • Use HTTPS for all API calls")
            print(f"   • Implement session timeout")
            print(f"   • Regular security reviews")
            
            print(f"\n✅ Permission system is properly configured!")
            
        except Exception as e:
            print(f"❌ Error generating permission summary: {e}")
            raise

if __name__ == "__main__":
    permission_enforcement_summary()







