#!/usr/bin/env python3
"""
Clean up all users and tenants from database
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config.env')

from app import create_app, db
from modules.core.models import User
from modules.core.tenant_models import Tenant, TenantSettings

def cleanup_database():
    """Clean up all users and tenants"""
    try:
        print("🧹 Cleaning up database...")
        
        app = create_app()
        
        with app.app_context():
            # Get counts before cleanup
            user_count = User.query.count()
            tenant_count = Tenant.query.count()
            settings_count = TenantSettings.query.count()
            
            print(f"📊 Current counts:")
            print(f"   Users: {user_count}")
            print(f"   Tenants: {tenant_count}")
            print(f"   Tenant Settings: {settings_count}")
            
            if user_count == 0 and tenant_count == 0:
                print("✅ Database is already clean!")
                return True
            
            # Delete in correct order (foreign key constraints)
            print("\n🗑️ Deleting tenant settings...")
            TenantSettings.query.delete()
            
            print("🗑️ Deleting users...")
            User.query.delete()
            
            print("🗑️ Deleting tenants...")
            Tenant.query.delete()
            
            # Commit changes
            db.session.commit()
            
            # Verify cleanup
            final_user_count = User.query.count()
            final_tenant_count = Tenant.query.count()
            final_settings_count = TenantSettings.query.count()
            
            print(f"\n✅ Cleanup completed!")
            print(f"📊 Final counts:")
            print(f"   Users: {final_user_count}")
            print(f"   Tenants: {final_tenant_count}")
            print(f"   Tenant Settings: {final_settings_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = cleanup_database()
    if success:
        print("\n🎉 Database cleaned successfully!")
        print("🚀 You can now register fresh users!")
    else:
        print("\n❌ Database cleanup failed!")










































