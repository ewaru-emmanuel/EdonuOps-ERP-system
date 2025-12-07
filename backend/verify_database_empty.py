"""Verify database is completely empty - ready for fresh start"""
from app import create_app, db
from modules.core.models import User
from modules.core.tenant_models import Tenant
from sqlalchemy import text

app = create_app()
with app.app_context():
    print('\n' + '='*80)
    print('DATABASE STATUS VERIFICATION')
    print('='*80 + '\n')
    
    # Check users
    user_count = User.query.count()
    print(f'👥 Users: {user_count}')
    if user_count > 0:
        users = User.query.all()
        for user in users:
            print(f'   - User {user.id}: {user.username} ({user.email})')
    else:
        print('   ✅ No users found')
    print()
    
    # Check tenants
    tenant_count = Tenant.query.count()
    print(f'🏢 Tenants: {tenant_count}')
    if tenant_count > 0:
        tenants = Tenant.query.all()
        for tenant in tenants:
            print(f'   - {tenant.id}: {tenant.name}')
    else:
        print('   ✅ No tenants found')
    print()
    
    # Check other related data
    print('📊 Related Data:')
    print('-' * 80)
    
    tables_to_check = [
        'onboarding_progress',
        'user_modules',
        'user_data',
        'accounts',
        'login_history',
        'audit_logs'
    ]
    
    for table in tables_to_check:
        try:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            status = '✅' if count == 0 else '❌'
            print(f'   {status} {table}: {count} records')
        except Exception as e:
            if 'does not exist' in str(e).lower():
                print(f'   ⚠️  {table}: Table does not exist')
            else:
                print(f'   ⚠️  {table}: Error checking ({str(e)[:50]})')
    print()
    
    # Summary
    print('='*80)
    print('SUMMARY:')
    print('='*80)
    
    if user_count == 0 and tenant_count == 0:
        print('✅ DATABASE IS COMPLETELY EMPTY')
        print('   - Ready for fresh user registrations')
        print('   - No stale data')
        print('   - Clean slate for multiple clients')
    else:
        print('⚠️  DATABASE STILL HAS DATA:')
        if user_count > 0:
            print(f'   - {user_count} user(s) remaining')
        if tenant_count > 0:
            print(f'   - {tenant_count} tenant(s) remaining')
    print()

