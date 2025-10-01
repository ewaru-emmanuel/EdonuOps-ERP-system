#!/usr/bin/env python3
"""
Recreate security tables for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.user_models import User
from modules.core.tenant_models import Tenant
from modules.core.permission_models import Permission, Role, UserRole
from modules.core.audit_models import AuditLog
from app import create_app
from datetime import datetime

def recreate_security_tables():
    """Recreate security tables from scratch."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Recreating security tables...")
            
            # Drop existing security tables
            print("🗑️  Dropping existing security tables...")
            
            tables_to_drop = [
                'audit_logs',
                'user_roles', 
                'roles',
                'permissions',
                'users',
                'tenants'
            ]
            
            for table in tables_to_drop:
                try:
                    db.session.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"   ✅ Dropped {table}")
                except Exception as e:
                    print(f"   ⚠️  Could not drop {table}: {e}")
            
            # Create all tables
            print("🏗️  Creating security tables...")
            db.create_all()
            
            # Verify table creation
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("📋 Created tables:")
            for table in tables_to_drop:
                if table in tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} (failed to create)")
            
            # Create default data
            print("📝 Creating default data...")
            
            # Create default tenant
            default_tenant = Tenant(
                name="Default Company",
                subdomain="default",
                created_at=datetime.utcnow()
            )
            db.session.add(default_tenant)
            db.session.flush()
            print(f"   ✅ Created default tenant: {default_tenant.name}")
            
            # Create default permissions
            default_permissions = [
                Permission(name="user.create", description="Create users"),
                Permission(name="user.read", description="Read users"),
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
            
            for permission in default_permissions:
                db.session.add(permission)
            print(f"   ✅ Created {len(default_permissions)} permissions")
            
            # Create default roles
            default_roles = [
                Role(name="admin", description="System Administrator", tenant_id=default_tenant.id),
                Role(name="manager", description="Department Manager", tenant_id=default_tenant.id),
                Role(name="user", description="Standard User", tenant_id=default_tenant.id),
                Role(name="viewer", description="Read-Only User", tenant_id=default_tenant.id)
            ]
            
            for role in default_roles:
                db.session.add(role)
            db.session.flush()
            print(f"   ✅ Created {len(default_roles)} roles")
            
            # Assign permissions to roles
            print("🔗 Assigning permissions to roles...")
            
            # Admin role gets all permissions
            admin_role = Role.query.filter_by(name="admin").first()
            if admin_role:
                for permission in Permission.query.all():
                    user_role = UserRole(role_id=admin_role.id, permission_id=permission.id)
                    db.session.add(user_role)
                print(f"   ✅ Assigned all permissions to admin role")
            
            # Manager role gets most permissions except user management
            manager_role = Role.query.filter_by(name="manager").first()
            if manager_role:
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
                        db.session.add(user_role)
                print(f"   ✅ Assigned {len(manager_permissions)} permissions to manager role")
            
            # User role gets limited permissions
            user_role = Role.query.filter_by(name="user").first()
            if user_role:
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
                        db.session.add(user_role)
                print(f"   ✅ Assigned {len(user_permissions)} permissions to user role")
            
            # Viewer role gets read-only permissions
            viewer_role = Role.query.filter_by(name="viewer").first()
            if viewer_role:
                viewer_permissions = [
                    "finance.read", "sales.read", "inventory.read", "hr.read", "reports.generate"
                ]
                for perm_name in viewer_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        user_role = UserRole(role_id=viewer_role.id, permission_id=permission.id)
                        db.session.add(user_role)
                print(f"   ✅ Assigned {len(viewer_permissions)} permissions to viewer role")
            
            # Commit all changes
            db.session.commit()
            
            # Verify data creation
            print("🔍 Verifying data creation...")
            
            tenant_count = Tenant.query.count()
            permission_count = Permission.query.count()
            role_count = Role.query.count()
            user_role_count = UserRole.query.count()
            
            print(f"   📊 Tenants: {tenant_count}")
            print(f"   📊 Permissions: {permission_count}")
            print(f"   📊 Roles: {role_count}")
            print(f"   📊 Role-Permission assignments: {user_role_count}")
            
            # Create indexes for better performance
            print("⚡ Creating performance indexes...")
            
            try:
                # Users table indexes
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users (tenant_id)")
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)")
                print("   ✅ Created users table indexes")
            except Exception as e:
                print(f"   ⚠️  Could not create users indexes: {e}")
            
            try:
                # Audit logs table indexes
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id)")
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs (entity_type)")
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at)")
                print("   ✅ Created audit_logs table indexes")
            except Exception as e:
                print(f"   ⚠️  Could not create audit_logs indexes: {e}")
            
            try:
                # User roles table indexes
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles (user_id)")
                db.session.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles (role_id)")
                print("   ✅ Created user_roles table indexes")
            except Exception as e:
                print(f"   ⚠️  Could not create user_roles indexes: {e}")
            
            # Final verification
            print("✅ Final verification...")
            
            # Check table structure
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'tenants', 'permissions', 'roles', 'user_roles', 'audit_logs']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                print(f"   ❌ Missing tables: {missing_tables}")
            else:
                print("   ✅ All security tables are present")
            
            # Check data integrity
            if tenant_count > 0 and permission_count > 0 and role_count > 0:
                print("   ✅ Default data created successfully")
            else:
                print("   ❌ Default data creation failed")
            
            print("🎉 Security tables recreation completed!")
            print("🔐 Security system is ready for use!")
            print("\n📋 Next steps:")
            print("   1. Create admin user: python create_admin_user.py")
            print("   2. Test the system: python test_permissions.py")
            print("   3. Configure additional tenants as needed")
            print("   4. Set up user accounts")
            
        except Exception as e:
            print(f"❌ Error recreating security tables: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    recreate_security_tables()







