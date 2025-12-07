#!/usr/bin/env python3
"""
Clean up test data and check what's causing the 400 error
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

def cleanup_and_check():
    app = create_app()
    
    with app.app_context():
        try:
            print("🧹 Cleaning up test data...")
            
            # Get all users
            users = User.query.all()
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - {user.username} ({user.email}) - ID: {user.id}")
            
            # Get all tenants
            tenants = Tenant.query.all()
            print(f"Found {len(tenants)} tenants:")
            for tenant in tenants:
                print(f"  - {tenant.id} ({tenant.name})")
            
            # Clean up test data
            print("\nCleaning up test data...")
            for user in users:
                if user.email == "test@example.com" or user.username == "testuser":
                    print(f"Deleting test user: {user.username} ({user.email})")
                    db.session.delete(user)
            
            for tenant in tenants:
                if tenant.id.startswith("tenant_"):
                    print(f"Deleting test tenant: {tenant.id} ({tenant.name})")
                    db.session.delete(tenant)
            
            db.session.commit()
            print("✅ Test data cleaned up")
            
            # Check final state
            user_count = User.query.count()
            tenant_count = Tenant.query.count()
            print(f"\nFinal state:")
            print(f"  Users: {user_count}")
            print(f"  Tenants: {tenant_count}")
            
            return True
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = cleanup_and_check()
    if success:
        print("\n🎉 Cleanup completed successfully!")
    else:
        print("\n❌ Cleanup failed!")

