"""Check user registration details and company name"""
from app import create_app, db
from modules.core.models import User
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Get user 28 details
    user = User.query.get(28)
    
    if user:
        print(f'\n=== USER 28 REGISTRATION DETAILS ===\n')
        print(f'User ID: {user.id}')
        print(f'Username: {user.username}')
        print(f'Email: {user.email}')
        print(f'Tenant ID: {user.tenant_id}')
        
        # Get tenant details
        if user.tenant_id:
            result = db.session.execute(
                text("SELECT id, name, domain, status, subscription_plan, created_at FROM tenants WHERE id = :tenant_id"),
                {'tenant_id': user.tenant_id}
            )
            tenant = result.fetchone()
            
            if tenant:
                print(f'\n=== TENANT/COMPANY DETAILS ===\n')
                print(f'Tenant ID: {tenant[0]}')
                print(f'Company Name: {tenant[1]}')
                print(f'Domain: {tenant[2]}')
                print(f'Status: {tenant[3]}')
                print(f'Plan: {tenant[4]}')
                print(f'Created At: {tenant[5]}')
        
        # Check if there's a company_name field in users table
        try:
            result = db.session.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name LIKE '%company%'")
            )
            company_columns = result.fetchall()
            if company_columns:
                print(f'\n=== COMPANY-RELATED COLUMNS IN USERS TABLE ===\n')
                for col in company_columns:
                    print(f'  - {col[0]}')
        except Exception as e:
            print(f'\nNote: Could not check for company columns: {e}')
        
        # Check user creation date
        if hasattr(user, 'created_at'):
            print(f'\nUser Created At: {user.created_at}')
    else:
        print('\n❌ User 28 not found')


