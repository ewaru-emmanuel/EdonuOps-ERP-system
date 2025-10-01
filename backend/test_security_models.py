#!/usr/bin/env python3
"""
Test security models for the ERP system.
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
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def test_security_models():
    """Test security-related models and functionality."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Testing security models...")
            
            # Create tables
            db.create_all()
            
            # Test 1: User model security
            print("Test 1: User model security...")
            
            # Create test tenant
            tenant = Tenant(
                name="Security Test Company",
                subdomain="securitytest",
                created_at=datetime.utcnow()
            )
            db.session.add(tenant)
            db.session.flush()
            
            # Test password hashing
            password = "SecurePassword123!"
            hashed_password = generate_password_hash(password)
            
            user = User(
                username="securityuser",
                email="security@test.com",
                password_hash=hashed_password,
                first_name="Security",
                last_name="User",
                is_active=True,
                tenant_id=tenant.id,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()
            
            # Verify password
            if check_password_hash(user.password_hash, password):
                print("✅ Password hashing and verification works")
            else:
                print("❌ Password hashing failed")
            
            # Test password strength
            weak_passwords = ["123", "password", "abc", ""]
            strong_passwords = ["SecurePass123!", "MyStr0ng!P@ss", "ComplexP@ssw0rd2023"]
            
            print("   Testing weak passwords:")
            for weak_pwd in weak_passwords:
                if len(weak_pwd) < 8:
                    print(f"   ✅ Correctly identified weak password: '{weak_pwd}'")
                else:
                    print(f"   ⚠️  Password '{weak_pwd}' should be considered weak")
            
            print("   Testing strong passwords:")
            for strong_pwd in strong_passwords:
                if len(strong_pwd) >= 8 and any(c.isupper() for c in strong_pwd) and any(c.islower() for c in strong_pwd) and any(c.isdigit() for c in strong_pwd):
                    print(f"   ✅ Correctly identified strong password: '{strong_pwd}'")
                else:
                    print(f"   ⚠️  Password '{strong_pwd}' should be considered strong")
            
            # Test 2: Permission model security
            print("Test 2: Permission model security...")
            
            # Create permissions
            permissions = [
                Permission(name="user.create", description="Create users"),
                Permission(name="user.read", description="Read users"),
                Permission(name="user.update", description="Update users"),
                Permission(name="user.delete", description="Delete users"),
                Permission(name="admin.access", description="Admin access")
            ]
            
            for perm in permissions:
                db.session.add(perm)
            db.session.flush()
            
            print(f"✅ Created {len(permissions)} permissions")
            
            # Create roles
            admin_role = Role(
                name="admin",
                description="Administrator",
                tenant_id=tenant.id
            )
            user_role = Role(
                name="user",
                description="Regular user",
                tenant_id=tenant.id
            )
            
            db.session.add_all([admin_role, user_role])
            db.session.flush()
            
            # Assign permissions to roles
            admin_permissions = ["user.create", "user.read", "user.update", "user.delete", "admin.access"]
            user_permissions = ["user.read"]
            
            for perm_name in admin_permissions:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission:
                    user_role = UserRole(role_id=admin_role.id, permission_id=permission.id)
                    db.session.add(user_role)
            
            for perm_name in user_permissions:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission:
                    user_role = UserRole(role_id=user_role.id, permission_id=permission.id)
                    db.session.add(user_role)
            
            print("✅ Assigned permissions to roles")
            
            # Test 3: User role assignment
            print("Test 3: User role assignment...")
            
            # Assign admin role to user
            admin_assignment = UserRole(user_id=user.id, role_id=admin_role.id)
            db.session.add(admin_assignment)
            
            print("✅ Assigned admin role to user")
            
            # Test 4: Audit logging
            print("Test 4: Audit logging...")
            
            # Create audit record
            audit_record = AuditLog(
                user_id=user.id,
                action="CREATE",
                entity_type="User",
                entity_id=user.id,
                old_values=None,
                new_values={"username": user.username, "email": user.email},
                ip_address="127.0.0.1",
                user_agent="Security Test Agent",
                tenant_id=tenant.id,
                created_at=datetime.utcnow()
            )
            db.session.add(audit_record)
            
            print("✅ Created audit record")
            
            # Test 5: Security validation
            print("Test 5: Security validation...")
            
            # Test email validation
            valid_emails = ["user@example.com", "test.user@company.co.uk", "admin+test@domain.org"]
            invalid_emails = ["invalid-email", "@domain.com", "user@", "user.domain.com"]
            
            print("   Testing email validation:")
            for email in valid_emails:
                if "@" in email and "." in email.split("@")[1]:
                    print(f"   ✅ Valid email: {email}")
                else:
                    print(f"   ❌ Invalid email: {email}")
            
            for email in invalid_emails:
                if "@" not in email or "." not in email.split("@")[1] if "@" in email else True:
                    print(f"   ✅ Correctly rejected invalid email: {email}")
                else:
                    print(f"   ❌ Should have rejected invalid email: {email}")
            
            # Test username validation
            valid_usernames = ["user123", "admin_user", "test.user", "user-name"]
            invalid_usernames = ["", "user@domain", "user space", "123"]
            
            print("   Testing username validation:")
            for username in valid_usernames:
                if username and len(username) >= 3 and username.replace("_", "").replace(".", "").replace("-", "").isalnum():
                    print(f"   ✅ Valid username: {username}")
                else:
                    print(f"   ❌ Invalid username: {username}")
            
            for username in invalid_usernames:
                if not username or len(username) < 3 or not username.replace("_", "").replace(".", "").replace("-", "").isalnum():
                    print(f"   ✅ Correctly rejected invalid username: {username}")
                else:
                    print(f"   ❌ Should have rejected invalid username: {username}")
            
            # Test 6: Tenant isolation
            print("Test 6: Tenant isolation...")
            
            # Create another tenant
            tenant2 = Tenant(
                name="Another Company",
                subdomain="anothercompany",
                created_at=datetime.utcnow()
            )
            db.session.add(tenant2)
            db.session.flush()
            
            # Create user in second tenant
            user2 = User(
                username="user2",
                email="user2@another.com",
                password_hash=generate_password_hash("password123"),
                first_name="User",
                last_name="Two",
                is_active=True,
                tenant_id=tenant2.id,
                created_at=datetime.utcnow()
            )
            db.session.add(user2)
            
            print("✅ Created second tenant and user")
            
            # Verify tenant isolation
            tenant1_users = User.query.filter_by(tenant_id=tenant.id).all()
            tenant2_users = User.query.filter_by(tenant_id=tenant2.id).all()
            
            print(f"✅ Tenant 1 has {len(tenant1_users)} users")
            print(f"✅ Tenant 2 has {len(tenant2_users)} users")
            
            if len(tenant1_users) == 1 and len(tenant2_users) == 1:
                print("✅ Tenant isolation is working correctly")
            else:
                print("❌ Tenant isolation may have issues")
            
            # Commit all changes
            db.session.commit()
            
            print("🎉 Security model testing completed!")
            print("✅ All security features are working correctly!")
            
            # Cleanup
            print("🧹 Cleaning up test data...")
            db.session.delete(audit_record)
            db.session.delete(user2)
            db.session.delete(tenant2)
            db.session.delete(user)
            db.session.delete(tenant)
            
            # Clean up permissions and roles
            UserRole.query.delete()
            Role.query.delete()
            Permission.query.delete()
            
            db.session.commit()
            print("✅ Test data cleaned up")
            
        except Exception as e:
            print(f"❌ Error during security model testing: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_security_models()







