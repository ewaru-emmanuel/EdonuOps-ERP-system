"""Check user_modules table to see what's actually stored"""
from app import create_app, db
from modules.dashboard.models import UserModules

app = create_app()
with app.app_context():
    modules = UserModules.query.all()
    print(f'Total user_modules records: {len(modules)}')
    print('\nAll user_modules:')
    for m in modules:
        print(f'  User {m.user_id}: {m.module_id} (active={m.is_active}, enabled={m.is_enabled}, created={m.created_at})')
    
    # Check for a specific user (you can change this)
    print('\n--- Checking by user_id ---')
    for user_id in set(m.user_id for m in modules):
        user_modules = UserModules.query.filter_by(user_id=user_id).all()
        active_modules = [m for m in user_modules if m.is_active and m.is_enabled]
        print(f'User {user_id}: {len(user_modules)} total, {len(active_modules)} active')
        for m in active_modules:
            print(f'  - {m.module_id}')

