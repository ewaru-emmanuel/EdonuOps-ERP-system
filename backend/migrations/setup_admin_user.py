#!/usr/bin/env python3
"""
Setup admin user for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.database import db
from modules.core.user_models import User
from modules.core.tenant_models import Tenant
from modules.core.permission_models import Role
from app import create_app
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_admin_user():
    """Create default admin user and tenant."""
    app = create_app()
    
    with app.app_context():
        try:
            print("👤 Setting up admin user...")
            
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
            
            # Create admin user if it doesn't exist
            admin_user = User.query.filter_by(email="admin@edonuerp.com").first()
            if not admin_user:
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
                print(f"✅ Created admin user: {admin_user.email}")
            else:
                print(f"✅ Admin user already exists: {admin_user.email}")
            
            # Assign admin role
            admin_role = Role.query.filter_by(name="admin").first()
            if admin_role and admin_user:
                # Check if user already has admin role
                from modules.core.permission_models import UserRole
                existing_role = UserRole.query.filter_by(user_id=admin_user.id, role_id=admin_role.id).first()
                if not existing_role:
                    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
                    db.session.add(user_role)
                    print(f"✅ Assigned admin role to user: {admin_user.email}")
                else:
                    print(f"✅ User already has admin role: {admin_user.email}")
            
            # Commit all changes
            db.session.commit()
            
            print("🎉 Admin user setup completed!")
            print("🔑 Admin credentials:")
            print("   Email: admin@edonuerp.com")
            print("   Password: password")
            print("⚠️  Please change the password after first login!")
            
        except Exception as e:
            print(f"❌ Error setting up admin user: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    setup_admin_user()







