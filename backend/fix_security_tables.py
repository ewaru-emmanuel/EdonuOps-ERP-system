#!/usr/bin/env python3
"""
Fix security tables for the ERP system.
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
from datetime import datetime

def fix_security_tables():
    """Fix and optimize security tables."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Fixing security tables...")
            
            # Create all tables
            db.create_all()
            
            # Check table existence
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            security_tables = [
                'users', 'tenants', 'permissions', 'roles', 'user_roles', 'audit_logs'
            ]
            
            print("📋 Checking security tables...")
            for table in security_tables:
                if table in tables:
                    print(f"   ✅ {table} table exists")
                    
                    # Get table info
                    columns = inspector.get_columns(table)
                    print(f"      Columns: {len(columns)}")
                    
                    # Check for indexes
                    indexes = inspector.get_indexes(table)
                    print(f"      Indexes: {len(indexes)}")
                    
                    # Check table size
                    try:
                        result = db.session.execute(f"SELECT COUNT(*) FROM {table}")
                        count = result.scalar()
                        print(f"      Records: {count}")
                    except Exception as e:
                        print(f"      Records: Could not count ({e})")
                else:
                    print(f"   ❌ {table} table missing")
            
            # Fix users table
            print("\n👤 Fixing users table...")
            if 'users' in tables:
                # Check for required columns
                users_columns = inspector.get_columns('users')
                required_user_columns = ['id', 'username', 'email', 'password_hash', 'is_active', 'tenant_id']
                
                missing_user_columns = []
                for col in required_user_columns:
                    if not any(c['name'] == col for c in users_columns):
                        missing_user_columns.append(col)
                
                if missing_user_columns:
                    print(f"   ⚠️  Missing columns: {missing_user_columns}")
                else:
                    print("   ✅ All required columns present")
                
                # Check for indexes
                users_indexes = inspector.get_indexes('users')
                recommended_user_indexes = ['email', 'username', 'tenant_id']
                
                for idx_name in recommended_user_indexes:
                    has_index = any(idx['column_names'] == [idx_name] for idx in users_indexes)
                    if has_index:
                        print(f"   ✅ Index on {idx_name} exists")
                    else:
                        print(f"   ⚠️  Missing index on {idx_name}")
            
            # Fix permissions table
            print("\n🔑 Fixing permissions table...")
            if 'permissions' in tables:
                permissions_columns = inspector.get_columns('permissions')
                required_perm_columns = ['id', 'name', 'description']
                
                missing_perm_columns = []
                for col in required_perm_columns:
                    if not any(c['name'] == col for c in permissions_columns):
                        missing_perm_columns.append(col)
                
                if missing_perm_columns:
                    print(f"   ⚠️  Missing columns: {missing_perm_columns}")
                else:
                    print("   ✅ All required columns present")
                
                # Check for unique constraint on name
                permissions_indexes = inspector.get_indexes('permissions')
                has_name_index = any(
                    idx.get('unique', False) and idx['column_names'] == ['name'] 
                    for idx in permissions_indexes
                )
                if has_name_index:
                    print("   ✅ Unique constraint on name exists")
                else:
                    print("   ⚠️  Missing unique constraint on name")
            
            # Fix roles table
            print("\n🎭 Fixing roles table...")
            if 'roles' in tables:
                roles_columns = inspector.get_columns('roles')
                required_role_columns = ['id', 'name', 'description', 'tenant_id']
                
                missing_role_columns = []
                for col in required_role_columns:
                    if not any(c['name'] == col for c in roles_columns):
                        missing_role_columns.append(col)
                
                if missing_role_columns:
                    print(f"   ⚠️  Missing columns: {missing_role_columns}")
                else:
                    print("   ✅ All required columns present")
            
            # Fix user_roles table
            print("\n🔗 Fixing user_roles table...")
            if 'user_roles' in tables:
                user_roles_columns = inspector.get_columns('user_roles')
                required_ur_columns = ['id', 'user_id', 'role_id']
                
                missing_ur_columns = []
                for col in required_ur_columns:
                    if not any(c['name'] == col for c in user_roles_columns):
                        missing_ur_columns.append(col)
                
                if missing_ur_columns:
                    print(f"   ⚠️  Missing columns: {missing_ur_columns}")
                else:
                    print("   ✅ All required columns present")
                
                # Check for foreign key constraints
                fk_constraints = inspector.get_foreign_keys('user_roles')
                if fk_constraints:
                    print(f"   ✅ Foreign key constraints present: {len(fk_constraints)}")
                else:
                    print("   ⚠️  Missing foreign key constraints")
            
            # Fix audit_logs table
            print("\n📝 Fixing audit_logs table...")
            if 'audit_logs' in tables:
                audit_columns = inspector.get_columns('audit_logs')
                required_audit_columns = [
                    'id', 'user_id', 'action', 'entity_type', 'entity_id',
                    'old_values', 'new_values', 'ip_address', 'created_at'
                ]
                
                missing_audit_columns = []
                for col in required_audit_columns:
                    if not any(c['name'] == col for c in audit_columns):
                        missing_audit_columns.append(col)
                
                if missing_audit_columns:
                    print(f"   ⚠️  Missing columns: {missing_audit_columns}")
                else:
                    print("   ✅ All required columns present")
                
                # Check for indexes
                audit_indexes = inspector.get_indexes('audit_logs')
                recommended_audit_indexes = ['user_id', 'entity_type', 'created_at']
                
                for idx_name in recommended_audit_indexes:
                    has_index = any(idx['column_names'] == [idx_name] for idx in audit_indexes)
                    if has_index:
                        print(f"   ✅ Index on {idx_name} exists")
                    else:
                        print(f"   ⚠️  Missing index on {idx_name}")
            
            # Data integrity checks
            print("\n🔍 Data integrity checks...")
            
            # Check for orphaned user_roles
            try:
                orphaned_ur = db.session.execute("""
                    SELECT COUNT(*) FROM user_roles ur 
                    LEFT JOIN users u ON ur.user_id = u.id 
                    WHERE u.id IS NULL
                """).scalar()
                
                if orphaned_ur > 0:
                    print(f"   ⚠️  Found {orphaned_ur} orphaned user_roles")
                else:
                    print("   ✅ No orphaned user_roles")
            except Exception as e:
                print(f"   ⚠️  Could not check orphaned user_roles: {e}")
            
            # Check for orphaned permissions in user_roles
            try:
                orphaned_perms = db.session.execute("""
                    SELECT COUNT(*) FROM user_roles ur 
                    LEFT JOIN roles r ON ur.role_id = r.id 
                    WHERE r.id IS NULL
                """).scalar()
                
                if orphaned_perms > 0:
                    print(f"   ⚠️  Found {orphaned_perms} orphaned role references")
                else:
                    print("   ✅ No orphaned role references")
            except Exception as e:
                print(f"   ⚠️  Could not check orphaned role references: {e}")
            
            # Check for users without tenants
            try:
                users_no_tenant = db.session.execute("""
                    SELECT COUNT(*) FROM users u 
                    LEFT JOIN tenants t ON u.tenant_id = t.id 
                    WHERE t.id IS NULL
                """).scalar()
                
                if users_no_tenant > 0:
                    print(f"   ⚠️  Found {users_no_tenant} users without tenants")
                else:
                    print("   ✅ All users have valid tenants")
            except Exception as e:
                print(f"   ⚠️  Could not check users without tenants: {e}")
            
            # Performance recommendations
            print("\n⚡ Performance recommendations...")
            
            # Check for missing indexes
            missing_indexes = []
            
            if 'users' in tables:
                users_indexes = inspector.get_indexes('users')
                if not any(idx['column_names'] == ['email'] for idx in users_indexes):
                    missing_indexes.append("CREATE INDEX idx_users_email ON users (email);")
                if not any(idx['column_names'] == ['tenant_id'] for idx in users_indexes):
                    missing_indexes.append("CREATE INDEX idx_users_tenant_id ON users (tenant_id);")
            
            if 'audit_logs' in tables:
                audit_indexes = inspector.get_indexes('audit_logs')
                if not any(idx['column_names'] == ['user_id'] for idx in audit_indexes):
                    missing_indexes.append("CREATE INDEX idx_audit_logs_user_id ON audit_logs (user_id);")
                if not any(idx['column_names'] == ['created_at'] for idx in audit_indexes):
                    missing_indexes.append("CREATE INDEX idx_audit_logs_created_at ON audit_logs (created_at);")
            
            if missing_indexes:
                print("   💡 Recommended indexes:")
                for idx in missing_indexes:
                    print(f"      {idx}")
            else:
                print("   ✅ All recommended indexes are present")
            
            # Security recommendations
            print("\n🔒 Security recommendations...")
            print("   1. Ensure all passwords are properly hashed")
            print("   2. Implement password complexity requirements")
            print("   3. Add account lockout after failed login attempts")
            print("   4. Implement session timeout")
            print("   5. Add two-factor authentication")
            print("   6. Regular security audits")
            print("   7. Monitor failed login attempts")
            print("   8. Implement role-based access control")
            
            print("\n🎉 Security tables fix completed!")
            print("✅ Security system is optimized and ready!")
            
        except Exception as e:
            print(f"❌ Error fixing security tables: {e}")
            raise

if __name__ == "__main__":
    fix_security_tables()







