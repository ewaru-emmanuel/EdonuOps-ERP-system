#!/usr/bin/env python3
"""
Check what's causing registration to fail
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('config.env')

from app import create_app, db
from modules.core.models import User, Role
from modules.core.tenant_models import Tenant

app = create_app()

with app.app_context():
    print("🔍 Checking registration prerequisites...")
    
    # Check if roles exist
    print("\n1. Checking roles...")
    roles = Role.query.all()
    print(f"   Found {len(roles)} roles:")
    for role in roles:
        print(f"   - {role.role_name}")
    
    superadmin = Role.query.filter_by(role_name="superadmin").first()
    if superadmin:
        print(f"   ✅ Superadmin role exists (ID: {superadmin.id})")
    else:
        print(f"   ❌ Superadmin role does NOT exist!")
    
    # Check if any users exist
    print("\n2. Checking users...")
    user_count = User.query.count()
    print(f"   Found {user_count} users")
    
    # Check if any tenants exist
    print("\n3. Checking tenants...")
    tenant_count = Tenant.query.count()
    print(f"   Found {tenant_count} tenants")
    
    # Check if email_verification_tokens table exists
    print("\n4. Checking email_verification_tokens table...")
    try:
        result = db.session.execute(db.text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'email_verification_tokens'
        """))
        table_exists = result.fetchone() is not None
        if table_exists:
            print(f"   ✅ email_verification_tokens table exists")
        else:
            print(f"   ❌ email_verification_tokens table does NOT exist!")
    except Exception as e:
        print(f"   ⚠️  Error checking table: {e}")
    
    print("\n✅ Diagnosis complete!")


