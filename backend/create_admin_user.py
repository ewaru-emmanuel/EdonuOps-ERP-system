#!/usr/bin/env python3
"""
Create admin user for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.user_models import User
from modules.core.tenant_models import Tenant
from modules.core.permission_models import Role, UserRole
from app import create_app
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    """Create an admin user for the ERP system."""
    app = create_app()
    
    with app.app_context():
        try:
            print("👤 Creating admin user...")
            
            # Create tables if they don't exist
            db.create_all()
            
            # Create default tenant if it doesn't exist
            tenant = Tenant.query.filter_by(subdomain="default").first()
            if not tenant:
                tenant = Tenant(
                    name="Default Company",
                    subdomain="default",
                    created_at=datetime.utcnow()
                )
                db.session.add(tenant)
                db.session.flush()
                print(f"✅ Created default tenant: {tenant.name}")
            else:
                print(f"✅ Using existing tenant: {tenant.name}")
            
            # Check if admin user already exists
            existing_admin = User.query.filter_by(email="admin@edonuerp.com").first()
            if existing_admin:
                print(f"⚠️  Admin user already exists: {existing_admin.email}")
                print("   Updating admin user...")
                
                # Update existing admin user
                existing_admin.username = "admin"
                existing_admin.first_name = "System"
                existing_admin.last_name = "Administrator"
                existing_admin.is_active = True
                existing_admin.tenant_id = tenant.id
                existing_admin.updated_at = datetime.utcnow()
                
                # Update password
                new_password = "password"
                existing_admin.password_hash = generate_password_hash(new_password)
                
                print(f"✅ Updated existing admin user")
                print(f"   Email: {existing_admin.email}")
                print(f"   Username: {existing_admin.username}")
                print(f"   Password: {new_password}")
                
            else:
                # Create new admin user
                admin_user = User(
                    username="admin",
                    email="admin@edonuerp.com",
                    password_hash=generate_password_hash("password"),
                    first_name="System",
                    last_name="Administrator",
                    is_active=True,
                    tenant_id=tenant.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(admin_user)
                db.session.flush()
                print(f"✅ Created new admin user: {admin_user.email}")
            
            # Assign admin role
            admin_role = Role.query.filter_by(name="admin").first()
            if admin_role:
                # Check if user already has admin role
                user = existing_admin if existing_admin else admin_user
                existing_role = UserRole.query.filter_by(user_id=user.id, role_id=admin_role.id).first()
                
                if not existing_role:
                    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
                    db.session.add(user_role)
                    print(f"✅ Assigned admin role to user: {user.email}")
                else:
                    print(f"✅ User already has admin role: {user.email}")
            else:
                print("⚠️  Admin role not found. Please create roles first.")
            
            # Commit all changes
            db.session.commit()
            
            print("🎉 Admin user setup completed!")
            print("🔑 Admin credentials:")
            print("   Email: admin@edonuerp.com")
            print("   Password: password")
            print("⚠️  Please change the password after first login!")
            
            # Additional security recommendations
            print("\n🔒 Security Recommendations:")
            print("   1. Change the default password immediately")
            print("   2. Enable two-factor authentication")
            print("   3. Use strong, unique passwords")
            print("   4. Regularly audit user accounts")
            print("   5. Monitor login attempts and failed authentications")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_admin_user()







