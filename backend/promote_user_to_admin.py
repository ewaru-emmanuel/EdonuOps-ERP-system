#!/usr/bin/env python3
"""
Immediate Fix: Promote User 28 to Admin Role
Promotes a specific user to admin role so they can access admin features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import User, Role

def promote_user_to_admin(user_id):
    """Promote a user to admin role"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                print(f"❌ User {user_id} not found!")
                return False
            
            print(f"👤 User: {user.username} ({user.email})")
            print(f"   Current Role ID: {user.role_id}")
            
            # Get admin role
            admin_role = Role.query.filter_by(role_name='admin').first()
            if not admin_role:
                print("❌ Admin role not found!")
                return False
            
            print(f"   Admin Role ID: {admin_role.id}")
            
            # Check if already admin
            if user.role_id == admin_role.id:
                print("✅ User is already an admin!")
                return True
            
            # Promote to admin
            old_role_id = user.role_id
            user.role_id = admin_role.id
            db.session.commit()
            
            print(f"✅ Successfully promoted user {user_id} to admin role!")
            print(f"   Changed from role ID {old_role_id} to role ID {admin_role.id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error promoting user: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🚀 Promoting User 28 to Admin Role")
    print("=" * 60)
    success = promote_user_to_admin(28)
    sys.exit(0 if success else 1)


