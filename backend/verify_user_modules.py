"""Verify user modules in database"""
from app import create_app, db
from modules.dashboard.models import UserModules

app = create_app()
with app.app_context():
    print('=' * 60)
    print('USER MODULES VERIFICATION')
    print('=' * 60)
    
    # Get all user modules
    all_modules = UserModules.query.all()
    print(f'\nTotal user_modules records: {len(all_modules)}')
    
    if len(all_modules) == 0:
        print('\n⚠️ NO MODULES FOUND IN DATABASE!')
        print('This means modules are NOT being saved during onboarding.')
    else:
        print('\n📊 All User Modules:')
        print('-' * 60)
        for m in all_modules:
            print(f'  User {m.user_id}: {m.module_id}')
            print(f'    - Active: {m.is_active}')
            print(f'    - Enabled: {m.is_enabled}')
            print(f'    - Created: {m.created_at}')
            print(f'    - Activated: {m.activated_at}')
            print()
    
    # Group by user
    print('\n📊 Modules by User:')
    print('-' * 60)
    users = {}
    for m in all_modules:
        if m.user_id not in users:
            users[m.user_id] = []
        users[m.user_id].append(m)
    
    for user_id, modules in users.items():
        active_modules = [m for m in modules if m.is_active and m.is_enabled]
        print(f'\nUser {user_id}:')
        print(f'  Total records: {len(modules)}')
        print(f'  Active & Enabled: {len(active_modules)}')
        print(f'  Module IDs: {[m.module_id for m in active_modules]}')
        
        # Check for inactive modules
        inactive = [m for m in modules if not (m.is_active and m.is_enabled)]
        if inactive:
            print(f'  ⚠️ Inactive modules: {[m.module_id for m in inactive]}')
    
    print('\n' + '=' * 60)






