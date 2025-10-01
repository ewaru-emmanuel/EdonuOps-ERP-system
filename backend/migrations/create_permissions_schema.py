#!/usr/bin/env python3
"""
Create permissions schema for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.database import db
from modules.core.permission_models import Permission, Role, UserRole
from app import create_app

def create_permissions_schema():
    """Create the permissions schema and default permissions."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Creating permissions schema...")
            
            # Create tables
            db.create_all()
            
            # Define permission categories
            permission_categories = {
                "Core": [
                    ("user.create", "Create users"),
                    ("user.read", "Read user data"),
                    ("user.update", "Update users"),
                    ("user.delete", "Delete users"),
                    ("tenant.create", "Create tenants"),
                    ("tenant.read", "Read tenant data"),
                    ("tenant.update", "Update tenants"),
                    ("tenant.delete", "Delete tenants")
                ],
                "Finance": [
                    ("finance.create", "Create financial records"),
                    ("finance.read", "Read financial data"),
                    ("finance.update", "Update financial records"),
                    ("finance.delete", "Delete financial records"),
                    ("finance.reports", "Generate financial reports"),
                    ("finance.settings", "Manage financial settings")
                ],
                "Sales": [
                    ("sales.create", "Create sales records"),
                    ("sales.read", "Read sales data"),
                    ("sales.update", "Update sales records"),
                    ("sales.delete", "Delete sales records"),
                    ("sales.reports", "Generate sales reports"),
                    ("sales.settings", "Manage sales settings")
                ],
                "Inventory": [
                    ("inventory.create", "Create inventory records"),
                    ("inventory.read", "Read inventory data"),
                    ("inventory.update", "Update inventory records"),
                    ("inventory.delete", "Delete inventory records"),
                    ("inventory.reports", "Generate inventory reports"),
                    ("inventory.settings", "Manage inventory settings")
                ],
                "HR": [
                    ("hr.create", "Create HR records"),
                    ("hr.read", "Read HR data"),
                    ("hr.update", "Update HR records"),
                    ("hr.delete", "Delete HR records"),
                    ("hr.reports", "Generate HR reports"),
                    ("hr.settings", "Manage HR settings")
                ],
                "System": [
                    ("admin.access", "Access admin functions"),
                    ("reports.generate", "Generate system reports"),
                    ("settings.manage", "Manage system settings"),
                    ("audit.view", "View audit logs"),
                    ("backup.create", "Create system backups"),
                    ("backup.restore", "Restore system backups")
                ]
            }
            
            # Create permissions
            created_permissions = []
            for category, permissions in permission_categories.items():
                print(f"\n📋 Creating {category} permissions...")
                for perm_name, perm_desc in permissions:
                    existing = Permission.query.filter_by(name=perm_name).first()
                    if not existing:
                        permission = Permission(
                            name=perm_name,
                            description=perm_desc,
                            category=category
                        )
                        db.session.add(permission)
                        created_permissions.append(permission)
                        print(f"  ✅ {perm_name}")
                    else:
                        print(f"  ⚠️  {perm_name} (already exists)")
            
            # Define role hierarchies
            role_definitions = {
                "super_admin": {
                    "description": "Super Administrator with full system access",
                    "permissions": "all"
                },
                "admin": {
                    "description": "System Administrator",
                    "permissions": [
                        "user.create", "user.read", "user.update", "user.delete",
                        "finance.create", "finance.read", "finance.update", "finance.delete", "finance.reports",
                        "sales.create", "sales.read", "sales.update", "sales.delete", "sales.reports",
                        "inventory.create", "inventory.read", "inventory.update", "inventory.delete", "inventory.reports",
                        "hr.create", "hr.read", "hr.update", "hr.delete", "hr.reports",
                        "admin.access", "reports.generate", "settings.manage", "audit.view"
                    ]
                },
                "manager": {
                    "description": "Department Manager",
                    "permissions": [
                        "user.read", "user.update",
                        "finance.read", "finance.update", "finance.reports",
                        "sales.read", "sales.update", "sales.reports",
                        "inventory.read", "inventory.update", "inventory.reports",
                        "hr.read", "hr.update", "hr.reports",
                        "reports.generate"
                    ]
                },
                "user": {
                    "description": "Standard User",
                    "permissions": [
                        "finance.read", "finance.create",
                        "sales.read", "sales.create",
                        "inventory.read", "inventory.create",
                        "hr.read", "hr.create"
                    ]
                },
                "viewer": {
                    "description": "Read-Only User",
                    "permissions": [
                        "finance.read", "sales.read", "inventory.read", "hr.read", "reports.generate"
                    ]
                }
            }
            
            # Create roles and assign permissions
            for role_name, role_config in role_definitions.items():
                print(f"\n👥 Creating role: {role_name}")
                
                existing_role = Role.query.filter_by(name=role_name).first()
                if not existing_role:
                    role = Role(
                        name=role_name,
                        description=role_config["description"]
                    )
                    db.session.add(role)
                    db.session.flush()
                    print(f"  ✅ Created role: {role_name}")
                else:
                    role = existing_role
                    print(f"  ⚠️  Role already exists: {role_name}")
                
                # Assign permissions to role
                if role_config["permissions"] == "all":
                    # Super admin gets all permissions
                    for permission in Permission.query.all():
                        existing_assignment = UserRole.query.filter_by(
                            role_id=role.id, 
                            permission_id=permission.id
                        ).first()
                        if not existing_assignment:
                            assignment = UserRole(
                                role_id=role.id,
                                permission_id=permission.id
                            )
                            db.session.add(assignment)
                            print(f"    ✅ Assigned: {permission.name}")
                else:
                    # Assign specific permissions
                    for perm_name in role_config["permissions"]:
                        permission = Permission.query.filter_by(name=perm_name).first()
                        if permission:
                            existing_assignment = UserRole.query.filter_by(
                                role_id=role.id,
                                permission_id=permission.id
                            ).first()
                            if not existing_assignment:
                                assignment = UserRole(
                                    role_id=role.id,
                                    permission_id=permission.id
                                )
                                db.session.add(assignment)
                                print(f"    ✅ Assigned: {perm_name}")
                        else:
                            print(f"    ❌ Permission not found: {perm_name}")
            
            # Commit all changes
            db.session.commit()
            
            print("\n🎉 Permissions schema created successfully!")
            print(f"📊 Created {len(created_permissions)} new permissions")
            print(f"👥 Created {len(role_definitions)} roles")
            print("🔑 Permission system is ready for use!")
            
        except Exception as e:
            print(f"❌ Error creating permissions schema: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_permissions_schema()







