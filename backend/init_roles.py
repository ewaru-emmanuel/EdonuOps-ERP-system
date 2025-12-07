#!/usr/bin/env python3
"""
PostgreSQL Role Initialization Script for EdonuOps ERP
Creates default roles in PostgreSQL database
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import text

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.core.models import Role

def create_default_roles():
    """Create default roles in PostgreSQL database"""
    
    # Define default roles with permissions
    DEFAULT_ROLES = [
        {
            "role_name": "superadmin",
            "description": "System administrator with full access to all features",
            "permissions": json.dumps(["*"]),  # All permissions
            "is_active": True
        },
        {
            "role_name": "admin", 
            "description": "Company administrator with management access",
            "permissions": json.dumps([
                "users.*", "settings.*", "reports.*", 
                "finance.*", "inventory.*", "crm.*", "sales.*"
            ]),
            "is_active": True
        },
        {
            "role_name": "manager",
            "description": "Department manager with team oversight",
            "permissions": json.dumps([
                "finance.read", "inventory.*", "crm.*", 
                "reports.read", "sales.read", "users.read"
            ]),
            "is_active": True
        },
        {
            "role_name": "accountant",
            "description": "Financial specialist with accounting access",
            "permissions": json.dumps([
                "finance.*", "reports.read", "inventory.read", 
                "settings.read"
            ]),
            "is_active": True
        },
        {
            "role_name": "user",
            "description": "Regular employee with basic access",
            "permissions": json.dumps([
                "finance.read", "inventory.read", "crm.read", 
                "reports.read"
            ]),
            "is_active": True
        }
    ]
    
    print("🔧 Initializing default roles in PostgreSQL...")
    
    created_count = 0
    skipped_count = 0
    
    for role_data in DEFAULT_ROLES:
        # Check if role already exists in PostgreSQL
        existing_role = Role.query.filter_by(role_name=role_data["role_name"]).first()
        
        if existing_role:
            print(f"   ⏭️  Role '{role_data['role_name']}' already exists in PostgreSQL - skipping")
            skipped_count += 1
        else:
            # Create new role in PostgreSQL
            new_role = Role(
                role_name=role_data["role_name"],
                description=role_data["description"],
                permissions=role_data["permissions"],
                is_active=role_data["is_active"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(new_role)
            print(f"   ✅ Created role '{role_data['role_name']}' in PostgreSQL")
            created_count += 1
    
    # Commit all changes to PostgreSQL
    try:
        db.session.commit()
        print(f"\n🎉 PostgreSQL role initialization completed!")
        print(f"   📊 Created: {created_count} roles")
        print(f"   ⏭️  Skipped: {skipped_count} roles")
        print(f"   📋 Total roles: {created_count + skipped_count}")
        
        # Display all roles from PostgreSQL
        print(f"\n📋 Available roles in PostgreSQL:")
        all_roles = Role.query.all()
        for role in all_roles:
            permissions = json.loads(role.permissions) if role.permissions else []
            print(f"   • {role.role_name}: {role.description}")
            print(f"     Permissions: {', '.join(permissions[:3])}{'...' if len(permissions) > 3 else ''}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating roles in PostgreSQL: {str(e)}")
        return False

def main():
    """Main function to initialize roles in PostgreSQL"""
    print("🚀 EdonuOps ERP - PostgreSQL Role Initialization")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Test PostgreSQL connection
            db.session.execute(text('SELECT 1'))
            print("✅ PostgreSQL connection successful")
            
            # Create default roles in PostgreSQL
            success = create_default_roles()
            
            if success:
                print("\n🎯 Next steps:")
                print("   1. Register the first user (they will get 'superadmin' role)")
                print("   2. Super admin can then invite other users")
                print("   3. Assign appropriate roles to team members")
                print("\n🌐 Ready for registration at: http://localhost:3000/register")
            else:
                print("\n❌ PostgreSQL role initialization failed")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {str(e)}")
            print("\n🔧 Troubleshooting:")
            print("   1. Check your DATABASE_URL in config.env")
            print("   2. Ensure PostgreSQL is running")
            print("   3. Verify AWS RDS credentials")
            sys.exit(1)

if __name__ == "__main__":
    main()
