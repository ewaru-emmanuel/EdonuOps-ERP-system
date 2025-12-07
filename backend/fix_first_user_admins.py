#!/usr/bin/env python3
"""
Migration Script: Find and Promote All First Users to Admin
Identifies first users per tenant/company and promotes them to admin role
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import User, Role
from sqlalchemy import func

def is_multi_tenant():
    """Check if system is multi-tenant"""
    try:
        from modules.core.tenant_models import Tenant
        # Check if tenants table exists and has data
        tenant_count = Tenant.query.count()
        return tenant_count > 0
    except:
        return False

def find_and_promote_first_users():
    """Find first users and promote them to admin"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Finding First Users to Promote")
            print("=" * 60)
            
            # Get admin role
            admin_role = Role.query.filter_by(role_name='admin').first()
            if not admin_role:
                print("❌ Admin role not found!")
                return False
            
            print(f"✅ Admin role found (ID: {admin_role.id})")
            
            # Check if multi-tenant
            is_multi = is_multi_tenant()
            print(f"📊 System type: {'Multi-tenant' if is_multi else 'Single-tenant'}")
            
            first_users = []
            
            if is_multi:
                # Multi-tenant: Find first user per tenant
                try:
                    from modules.core.tenant_models import UserTenant
                    
                    # Get all tenants
                    from modules.core.tenant_models import Tenant
                    tenants = Tenant.query.all()
                    
                    for tenant in tenants:
                        # Get users for this tenant, ordered by created_at
                        tenant_users = db.session.query(User).join(
                            UserTenant, User.id == UserTenant.user_id
                        ).filter(
                            UserTenant.tenant_id == tenant.id
                        ).order_by(User.created_at.asc()).all()
                        
                        if tenant_users:
                            first_user = tenant_users[0]
                            if first_user.role_id != admin_role.id:
                                first_users.append({
                                    'user': first_user,
                                    'tenant': tenant,
                                    'reason': f'First user for tenant {tenant.name}'
                                })
                except Exception as e:
                    print(f"⚠️  Error checking tenants: {e}")
                    # Fallback to single-tenant logic
                    is_multi = False
            
            if not is_multi:
                # Single-tenant: Find first user globally
                all_users = User.query.order_by(User.created_at.asc()).all()
                
                if all_users:
                    first_user = all_users[0]
                    if first_user.role_id != admin_role.id:
                        first_users.append({
                            'user': first_user,
                            'tenant': None,
                            'reason': 'First user globally'
                        })
            
            if not first_users:
                print("✅ No first users found that need promotion (all are already admins)")
                return True
            
            print(f"\n📋 Found {len(first_users)} first user(s) to promote:")
            for item in first_users:
                user = item['user']
                print(f"   - User {user.id}: {user.username} ({user.email})")
                print(f"     Reason: {item['reason']}")
                print(f"     Current Role ID: {user.role_id}")
            
            # Confirm and promote
            print(f"\n🔧 Promoting {len(first_users)} user(s) to admin...")
            promoted_count = 0
            
            for item in first_users:
                user = item['user']
                old_role_id = user.role_id
                user.role_id = admin_role.id
                promoted_count += 1
                print(f"   ✅ Promoted user {user.id} ({user.username})")
            
            db.session.commit()
            print(f"\n✅ Successfully promoted {promoted_count} user(s) to admin role!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error in migration: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = find_and_promote_first_users()
    sys.exit(0 if success else 1)


