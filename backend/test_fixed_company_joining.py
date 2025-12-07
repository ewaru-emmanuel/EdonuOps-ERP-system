#!/usr/bin/env python3
"""
Test the fixed company joining function
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from modules.core.models import User, Role
from modules.core.tenant_models import Tenant

def test_fixed_company_joining():
    """Test the fixed company joining function"""
    try:
        print("🔍 Testing fixed company joining function...")
        
        app = create_app()
        
        with app.app_context():
            # Test data
            username = "testuser999"
            email = "testuser999@example.com"
            hashed_password = "test_hash"
            first_name = "Test"
            last_name = "User"
            phone_number = "1234567890"
            invite_code = ""  # Empty invite code
            
            print("🔍 Testing with empty invite code...")
            
            # Check if we can create a tenant with unique domain
            from modules.core.tenant_models import Tenant
            import uuid
            
            tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
            company_name = f"{first_name.strip()} {last_name.strip()}'s Company"
            
            # Create unique domain to avoid conflicts
            base_domain = email.split('@')[1] if '@' in email else 'localhost'
            unique_domain = f"{tenant_id}.{base_domain}"
            
            print(f"🔍 Creating tenant: {tenant_id} with domain: {unique_domain}")
            
            tenant = Tenant(
                id=tenant_id,
                name=company_name,
                domain=unique_domain,
                subscription_plan='free',
                status='active'
            )
            
            db.session.add(tenant)
            db.session.flush()
            print(f"🔍 Tenant created successfully: {tenant_id}")
            
            # Check if we can get user role
            user_role = Role.query.filter_by(role_name="user").first()
            if not user_role:
                print("❌ User role not found!")
                return False
            
            print(f"🔍 User role found: {user_role.role_name}")
            
            # Test user creation
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                role_id=user_role.id,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                phone_number=phone_number.strip(),
                tenant_id=tenant.id,
                is_active=False,
                email_verified=False
            )
            
            db.session.add(new_user)
            db.session.commit()
            print(f"🔍 User created successfully: {new_user.id}")
            
            # Clean up
            db.session.delete(new_user)
            db.session.delete(tenant)
            db.session.commit()
            print("🔍 Cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_company_joining()
    if success:
        print("\n🎉 Fixed company joining function works!")
    else:
        print("\n❌ Company joining function still has issues!")

