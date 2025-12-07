"""Delete default_tenant from database"""
from app import create_app, db
from modules.core.models import User
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Check if default_tenant has any users
    users_in_default = User.query.filter_by(tenant_id='default_tenant').all()
    
    print(f'\n=== CHECKING DEFAULT TENANT ===\n')
    print(f'Users in default_tenant: {len(users_in_default)}')
    if users_in_default:
        print('Users:')
        for u in users_in_default:
            print(f'  - User ID: {u.id}, Username: {u.username}, Email: {u.email}')
    
    # Check if tenant exists
    result = db.session.execute(text("SELECT id, name FROM tenants WHERE id = 'default_tenant'"))
    tenant = result.fetchone()
    
    if tenant:
        print(f'\nFound tenant: {tenant[0]} - {tenant[1]}')
        
        # Delete the tenant
        try:
            db.session.execute(text("DELETE FROM tenants WHERE id = 'default_tenant'"))
            db.session.commit()
            print('\n✅ Successfully deleted default_tenant')
        except Exception as e:
            db.session.rollback()
            print(f'\n❌ Error deleting default_tenant: {e}')
    else:
        print('\n⚠️ default_tenant not found in database')
    
    # Verify remaining tenants and users
    print(f'\n=== REMAINING TENANTS ===\n')
    tenants_result = db.session.execute(text("SELECT id, name FROM tenants"))
    tenants = tenants_result.fetchall()
    for t in tenants:
        print(f'  - {t[0]}: {t[1]}')
    
    print(f'\n=== REMAINING USERS ===\n')
    users = User.query.all()
    for u in users:
        role_name = u.role.role_name if u.role else 'None'
        print(f'  User ID: {u.id}')
        print(f'  Username: {u.username}')
        print(f'  Email: {u.email}')
        print(f'  Role: {role_name}')
        print(f'  Tenant ID: {u.tenant_id}')
        print()


