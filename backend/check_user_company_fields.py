"""Check user company fields"""
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Get user 28's company fields
    result = db.session.execute(
        text("""
            SELECT 
                id, username, email, tenant_id,
                company_name, company_size, company_website,
                company_address, company_phone, company_email
            FROM users 
            WHERE id = 28
        """)
    )
    user = result.fetchone()
    
    if user:
        print(f'\n=== USER 28 COMPANY INFORMATION ===\n')
        print(f'User ID: {user[0]}')
        print(f'Username: {user[1]}')
        print(f'Email: {user[2]}')
        print(f'Tenant ID: {user[3]}')
        print(f'\n--- Company Fields ---')
        print(f'Company Name: {user[4] or "Not set"}')
        print(f'Company Size: {user[5] or "Not set"}')
        print(f'Company Website: {user[6] or "Not set"}')
        print(f'Company Address: {user[7] or "Not set"}')
        print(f'Company Phone: {user[8] or "Not set"}')
        print(f'Company Email: {user[9] or "Not set"}')
        
        # Also get tenant name
        tenant_result = db.session.execute(
            text("SELECT name FROM tenants WHERE id = :tenant_id"),
            {'tenant_id': user[3]}
        )
        tenant = tenant_result.fetchone()
        if tenant:
            print(f'\n--- Tenant/Company Name (from tenants table) ---')
            print(f'Registered Company Name: {tenant[0]}')
    else:
        print('\n❌ User 28 not found')


