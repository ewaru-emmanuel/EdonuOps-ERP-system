#!/usr/bin/env python3
"""
Create user authentication tables for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.database import db
from modules.core.user_models import User
from modules.core.tenant_models import Tenant
from modules.core.permission_models import Permission, Role, UserRole
from app import create_app

def create_auth_tables():
    """Create user authentication and permission tables."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Creating user authentication tables...")
            
            # Create all tables
            db.create_all()
            
            # Create default permissions
            permissions = [
                Permission(name="user.create", description="Create users"),
                Permission(name="user.read", description="Read user data"),
                Permission(name="user.update", description="Update users"),
                Permission(name="user.delete", description="Delete users"),
                Permission(name="finance.create", description="Create financial records"),
                Permission(name="finance.read", description="Read financial data"),
                Permission(name="finance.update", description="Update financial records"),
                Permission(name="finance.delete", description="Delete financial records"),
                Permission(name="sales.create", description="Create sales records"),
                Permission(name="sales.read", description="Read sales data"),
                Permission(name="sales.update", description="Update sales records"),
                Permission(name="sales.delete", description="Delete sales records"),
                Permission(name="inventory.create", description="Create inventory records"),
                Permission(name="inventory.read", description="Read inventory data"),
                Permission(name="inventory.update", description="Update inventory records"),
                Permission(name="inventory.delete", description="Delete inventory records"),
                Permission(name="hr.create", description="Create HR records"),
                Permission(name="hr.read", description="Read HR data"),
                Permission(name="hr.update", description="Update HR records"),
                Permission(name="hr.delete", description="Delete HR records"),
                Permission(name="admin.access", description="Access admin functions"),
                Permission(name="reports.generate", description="Generate reports"),
                Permission(name="settings.manage", description="Manage system settings")
            ]
            
            for permission in permissions:
                existing = Permission.query.filter_by(name=permission.name).first()
                if not existing:
                    db.session.add(permission)
                    print(f"✅ Created permission: {permission.name}")
                else:
                    print(f"⚠️  Permission already exists: {permission.name}")
            
            # Create default roles
            roles = [
                Role(name="admin", description="System Administrator", tenant_id=None),
                Role(name="manager", description="Department Manager", tenant_id=None),
                Role(name="user", description="Standard User", tenant_id=None),
                Role(name="viewer", description="Read-Only User", tenant_id=None)
            ]
            
            for role in roles:
                existing = Role.query.filter_by(name=role.name).first()
                if not existing:
                    db.session.add(role)
                    print(f"✅ Created role: {role.name}")
                else:
                    print(f"⚠️  Role already exists: {role.name}")
            
            # Commit changes
            db.session.commit()
            
            # Assign permissions to roles
            admin_role = Role.query.filter_by(name="admin").first()
            manager_role = Role.query.filter_by(name="manager").first()
            user_role = Role.query.filter_by(name="user").first()
            viewer_role = Role.query.filter_by(name="viewer").first()
            
            if admin_role:
                # Admin gets all permissions
                for permission in Permission.query.all():
                    user_role = UserRole(role_id=admin_role.id, permission_id=permission.id)
                    existing = UserRole.query.filter_by(role_id=admin_role.id, permission_id=permission.id).first()
                    if not existing:
                        db.session.add(user_role)
                        print(f"✅ Assigned {permission.name} to admin role")
            
            if manager_role:
                # Manager gets most permissions except user management
                manager_permissions = [
                    "finance.create", "finance.read", "finance.update",
                    "sales.create", "sales.read", "sales.update",
                    "inventory.create", "inventory.read", "inventory.update",
                    "hr.create", "hr.read", "hr.update",
                    "reports.generate"
                ]
                for perm_name in manager_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        user_role = UserRole(role_id=manager_role.id, permission_id=permission.id)
                        existing = UserRole.query.filter_by(role_id=manager_role.id, permission_id=permission.id).first()
                        if not existing:
                            db.session.add(user_role)
                            print(f"✅ Assigned {perm_name} to manager role")
            
            if user_role:
                # Standard user gets read and limited create permissions
                user_permissions = [
                    "finance.read", "finance.create",
                    "sales.read", "sales.create",
                    "inventory.read", "inventory.create",
                    "hr.read"
                ]
                for perm_name in user_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        user_role = UserRole(role_id=user_role.id, permission_id=permission.id)
                        existing = UserRole.query.filter_by(role_id=user_role.id, permission_id=permission.id).first()
                        if not existing:
                            db.session.add(user_role)
                            print(f"✅ Assigned {perm_name} to user role")
            
            if viewer_role:
                # Viewer gets only read permissions
                viewer_permissions = [
                    "finance.read", "sales.read", "inventory.read", "hr.read", "reports.generate"
                ]
                for perm_name in viewer_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        user_role = UserRole(role_id=viewer_role.id, permission_id=permission.id)
                        existing = UserRole.query.filter_by(role_id=viewer_role.id, permission_id=permission.id).first()
                        if not existing:
                            db.session.add(user_role)
                            print(f"✅ Assigned {perm_name} to viewer role")
            
            db.session.commit()
            
            print("🎉 User authentication tables created successfully!")
            print("🔑 Default permissions and roles have been set up!")
            
        except Exception as e:
            print(f"❌ Error creating authentication tables: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_auth_tables()







