"""Check tenants and users in the database"""
from app import create_app, db
from modules.core.models import User
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Check if tenants table exists
    try:
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'tenants'"))
        has_tenants_table = result.fetchone() is not None
        
        if has_tenants_table:
            # Get all tenants
            tenants_result = db.session.execute(text("SELECT id, name, domain, status, subscription_plan FROM tenants"))
            tenants = tenants_result.fetchall()
            print(f'\n=== TENANTS ({len(tenants)} total) ===\n')
            for t in tenants:
                print(f'ID: {t[0]}')
                print(f'Name: {t[1]}')
                print(f'Domain: {t[2]}')
                print(f'Status: {t[3]}')
                print(f'Plan: {t[4]}')
                print('---')
        else:
            print('\n=== NO TENANTS TABLE FOUND ===\n')
    except Exception as e:
        print(f'\n=== ERROR CHECKING TENANTS: {e} ===\n')
    
    # Get all users
    users = User.query.all()
    print(f'\n=== USERS ({len(users)} total) ===\n')
    
    # Group users by tenant
    users_by_tenant = {}
    for u in users:
        tenant_id = u.tenant_id if hasattr(u, 'tenant_id') and u.tenant_id else 'NO_TENANT'
        if tenant_id not in users_by_tenant:
            users_by_tenant[tenant_id] = []
        users_by_tenant[tenant_id].append(u)
    
    # Print users grouped by tenant
    for tenant_id, user_list in sorted(users_by_tenant.items()):
        print(f'\n--- TENANT: {tenant_id} ({len(user_list)} users) ---')
        for u in user_list:
            role_name = u.role.role_name if u.role else 'None'
            print(f'  User ID: {u.id}')
            print(f'  Username: {u.username}')
            print(f'  Email: {u.email}')
            print(f'  Role: {role_name}')
            tenant_attr = getattr(u, 'tenant_id', None)
            print(f'  Tenant ID: {tenant_attr}')
            print()

