#!/usr/bin/env python3
"""
Fix SystemSetting model and create missing permissions
1. Add section, data, version columns to system_settings table
2. Create missing permissions: system.users.read, system.roles.manage
3. Assign permissions to admin role
"""

import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import Role
from modules.core.permissions import Permission, RolePermission, PermissionManager

def fix_system_settings_table():
    """Add missing columns to system_settings table"""
    print("🔧 Fixing system_settings table...")
    
    try:
        # Check if section column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='system_settings' AND column_name='section'
        """))
        
        if not result.fetchone():
            print("   ➕ Adding 'section' column...")
            db.session.execute(text("""
                ALTER TABLE system_settings 
                ADD COLUMN section VARCHAR(100)
            """))
        
        # Check if data column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='system_settings' AND column_name='data'
        """))
        
        if not result.fetchone():
            print("   ➕ Adding 'data' column (JSONB)...")
            db.session.execute(text("""
                ALTER TABLE system_settings 
                ADD COLUMN data JSONB
            """))
        
        # Check if version column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='system_settings' AND column_name='version'
        """))
        
        if not result.fetchone():
            print("   ➕ Adding 'version' column...")
            db.session.execute(text("""
                ALTER TABLE system_settings 
                ADD COLUMN version INTEGER DEFAULT 1
            """))
        
        db.session.commit()
        print("   ✅ system_settings table updated")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"   ❌ Error updating system_settings: {e}")
        return False

def create_missing_permissions():
    """Create missing system permissions"""
    print("🔧 Creating missing permissions...")
    
    try:
        permissions_to_create = [
            {
                'name': 'system.users.read',
                'module': 'system',
                'action': 'read',
                'resource': 'users',
                'description': 'Read user information'
            },
            {
                'name': 'system.users.create',
                'module': 'system',
                'action': 'create',
                'resource': 'users',
                'description': 'Create new users'
            },
            {
                'name': 'system.users.update',
                'module': 'system',
                'action': 'update',
                'resource': 'users',
                'description': 'Update user information'
            },
            {
                'name': 'system.users.delete',
                'module': 'system',
                'action': 'delete',
                'resource': 'users',
                'description': 'Delete users'
            },
            {
                'name': 'system.roles.manage',
                'module': 'system',
                'action': 'manage',
                'resource': 'roles',
                'description': 'Manage roles and permissions'
            },
            {
                'name': 'system.roles.read',
                'module': 'system',
                'action': 'read',
                'resource': 'roles',
                'description': 'Read role information'
            },
            {
                'name': 'system.settings.read',
                'module': 'system',
                'action': 'read',
                'resource': 'settings',
                'description': 'Read system settings'
            },
            {
                'name': 'system.settings.update',
                'module': 'system',
                'action': 'update',
                'resource': 'settings',
                'description': 'Update system settings'
            }
        ]
        
        created_count = 0
        for perm_data in permissions_to_create:
            existing = Permission.query.filter_by(name=perm_data['name']).first()
            if not existing:
                permission = Permission(
                    name=perm_data['name'],
                    module=perm_data['module'],
                    action=perm_data['action'],
                    resource=perm_data['resource'],
                    description=perm_data['description']
                )
                db.session.add(permission)
                created_count += 1
                print(f"   ✅ Created permission: {perm_data['name']}")
            else:
                print(f"   ⏭️  Permission already exists: {perm_data['name']}")
        
        db.session.commit()
        print(f"   ✅ Created {created_count} new permissions")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"   ❌ Error creating permissions: {e}")
        import traceback
        traceback.print_exc()
        return False

def assign_permissions_to_admin():
    """Assign system permissions to admin role"""
    print("🔧 Assigning permissions to admin role...")
    
    try:
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            print("   ⚠️  Admin role not found, skipping permission assignment")
            return False
        
        # Get all system permissions
        system_permissions = Permission.query.filter(
            Permission.name.like('system.%')
        ).all()
        
        assigned_count = 0
        for permission in system_permissions:
            # Check if already assigned
            existing = RolePermission.query.filter_by(
                role_id=admin_role.id,
                permission_id=permission.id
            ).first()
            
            if not existing:
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    granted=True
                )
                db.session.add(role_permission)
                assigned_count += 1
                print(f"   ✅ Assigned {permission.name} to admin role")
        
        db.session.commit()
        print(f"   ✅ Assigned {assigned_count} permissions to admin role")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"   ❌ Error assigning permissions: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Fixing System Settings and Permissions")
        print("=" * 60)
        
        success = True
        success &= fix_system_settings_table()
        success &= create_missing_permissions()
        success &= assign_permissions_to_admin()
        
        if success:
            print("\n✅ All fixes applied successfully!")
        else:
            print("\n⚠️  Some fixes may have failed. Check errors above.")
        
        return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


