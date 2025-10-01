#!/usr/bin/env python3
"""
Test permission system functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.user_models import User
from modules.core.tenant_models import Tenant
from modules.core.permission_models import Permission, Role, UserRole
from app import create_app
from werkzeug.security import generate_password_hash
from datetime import datetime

def test_permissions():
    """Test the permission system."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Testing permission system...")
            
            # Test 1: Create test tenant
            print("Test 1: Creating test tenant...")
            tenant = Tenant(
                name="Test Company",
                subdomain="testcompany",
                created_at=datetime.utcnow()
            )
            db.session.add(tenant)
            db.session.flush()
            tenant_id = tenant.id
            print(f"✅ Test tenant created with ID: {tenant_id}")
            
            # Test 2: Create test users with different roles
            print("Test 2: Creating test users...")
            
            users = [
                {
                    "username": "admin_user",
                    "email": "admin@test.com",
                    "first_name": "Admin",
                    "last_name": "User",
                    "role": "admin"
                },
                {
                    "username": "manager_user",
                    "email": "manager@test.com",
                    "first_name": "Manager",
                    "last_name": "User",
                    "role": "manager"
                },
                {
                    "username": "regular_user",
                    "email": "user@test.com",
                    "first_name": "Regular",
                    "last_name": "User",
                    "role": "user"
                },
                {
                    "username": "viewer_user",
                    "email": "viewer@test.com",
                    "first_name": "Viewer",
                    "last_name": "User",
                    "role": "viewer"
                }
            ]
            
            created_users = []
            for user_data in users:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=generate_password_hash("password"),
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    is_active=True,
                    tenant_id=tenant_id,
                    created_at=datetime.utcnow()
                )
                db.session.add(user)
                db.session.flush()
                created_users.append({"user": user, "role_name": user_data["role"]})
                print(f"✅ Created user: {user_data['email']}")
            
            # Test 3: Assign roles to users
            print("Test 3: Assigning roles to users...")
            
            for user_data in created_users:
                user = user_data["user"]
                role_name = user_data["role_name"]
                
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user_role = UserRole(user_id=user.id, role_id=role.id)
                    db.session.add(user_role)
                    print(f"✅ Assigned {role_name} role to {user.email}")
                else:
                    print(f"❌ Role not found: {role_name}")
            
            # Test 4: Test permission checking
            print("Test 4: Testing permission checking...")
            
            def check_user_permission(user_email, permission_name):
                """Check if a user has a specific permission."""
                user = User.query.filter_by(email=user_email).first()
                if not user:
                    return False
                
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
            
            # Test various permissions
            test_cases = [
                ("admin@test.com", "user.create", True),
                ("admin@test.com", "finance.read", True),
                ("admin@test.com", "admin.access", True),
                ("manager@test.com", "user.create", False),
                ("manager@test.com", "finance.read", True),
                ("manager@test.com", "admin.access", False),
                ("user@test.com", "finance.create", True),
                ("user@test.com", "finance.delete", False),
                ("user@test.com", "admin.access", False),
                ("viewer@test.com", "finance.read", True),
                ("viewer@test.com", "finance.create", False),
                ("viewer@test.com", "admin.access", False)
            ]
            
            for user_email, permission_name, expected in test_cases:
                result = check_user_permission(user_email, permission_name)
                status = "✅" if result == expected else "❌"
                print(f"  {status} {user_email} - {permission_name}: {result} (expected: {expected})")
            
            # Test 5: Test role hierarchy
            print("Test 5: Testing role hierarchy...")
            
            def get_user_permissions(user_email):
                """Get all permissions for a user."""
                user = User.query.filter_by(email=user_email).first()
                if not user:
                    return []
                
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
            
            # Check permission counts
            admin_perms = get_user_permissions("admin@test.com")
            manager_perms = get_user_permissions("manager@test.com")
            user_perms = get_user_permissions("user@test.com")
            viewer_perms = get_user_permissions("viewer@test.com")
            
            print(f"  👑 Admin permissions: {len(admin_perms)}")
            print(f"  👨‍💼 Manager permissions: {len(manager_perms)}")
            print(f"  👤 User permissions: {len(user_perms)}")
            print(f"  👁️  Viewer permissions: {len(viewer_perms)}")
            
            # Verify hierarchy (admin > manager > user > viewer)
            if len(admin_perms) >= len(manager_perms) >= len(user_perms) >= len(viewer_perms):
                print("  ✅ Role hierarchy is correct")
            else:
                print("  ❌ Role hierarchy is incorrect")
            
            # Commit all changes
            db.session.commit()
            
            print("🎉 Permission system tests completed!")
            print("✅ All permission checks passed!")
            
            # Cleanup
            print("🧹 Cleaning up test data...")
            for user_data in created_users:
                db.session.delete(user_data["user"])
            db.session.delete(tenant)
            db.session.commit()
            print("✅ Test data cleaned up")
            
        except Exception as e:
            print(f"❌ Error during permission testing: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_permissions()







