"""Check user 28's registration details to see how tenant name was created"""
from app import create_app, db
from modules.core.models import User
from modules.core.tenant_models import Tenant
from sqlalchemy import text

app = create_app()
with app.app_context():
    print('\n' + '='*80)
    print('USER 28 REGISTRATION DETAILS INVESTIGATION')
    print('='*80 + '\n')
    
    # Get user 28
    user = User.query.get(28)
    if not user:
        print('❌ User 28 not found')
        exit(1)
    
    print('👤 USER REGISTRATION DATA:')
    print('-' * 80)
    print(f'   ID: {user.id}')
    print(f'   Username: {user.username}')
    print(f'   Email: {user.email}')
    print(f'   First Name: "{getattr(user, "first_name", None)}"')
    print(f'   Last Name: "{getattr(user, "last_name", None)}"')
    print(f'   Phone: {getattr(user, "phone_number", None)}')
    print(f'   Created At: {user.created_at}')
    print()
    
    # Get tenant
    tenant = Tenant.query.filter_by(id=user.tenant_id).first()
    if tenant:
        print('🏢 TENANT INFORMATION:')
        print('-' * 80)
        print(f'   Tenant ID: {tenant.id}')
        print(f'   Tenant Name: "{tenant.name}"')
        print(f'   Created At: {tenant.created_at}')
        print()
        
        # Check how tenant name was created
        first_name = getattr(user, 'first_name', '').strip()
        last_name = getattr(user, 'last_name', '').strip()
        expected_tenant_name = f"{first_name} {last_name}'s Company"
        
        print('🔍 TENANT NAME ANALYSIS:')
        print('-' * 80)
        print(f'   User First Name: "{first_name}"')
        print(f'   User Last Name: "{last_name}"')
        print(f'   Expected Tenant Name: "{expected_tenant_name}"')
        print(f'   Actual Tenant Name: "{tenant.name}"')
        print(f'   Match: {"✅ YES" if tenant.name == expected_tenant_name else "❌ NO"}')
        print()
        
        if tenant.name == expected_tenant_name:
            print('   📝 EXPLANATION:')
            print('      The tenant name was automatically created during registration')
            print(f'      using the formula: "{first_name} {last_name}\'s Company"')
            print()
            print('   ⚠️  ISSUE:')
            print(f'      The user registered with first_name="{first_name}" and last_name="{last_name}"')
            print('      This created the tenant name automatically.')
            print('      If this is incorrect, the user data may have been entered incorrectly during registration.')
            print()
    
    # Check if there are other users in this tenant
    other_users = User.query.filter_by(tenant_id=user.tenant_id).filter(User.id != 28).all()
    if other_users:
        print(f'👥 OTHER USERS IN SAME TENANT ({len(other_users)}):')
        print('-' * 80)
        for u in other_users:
            print(f'   - User {u.id}: {u.username} ({u.email})')
            print(f'     First: "{getattr(u, "first_name", None)}", Last: "{getattr(u, "last_name", None)}"')
        print()
    else:
        print('👥 OTHER USERS: None (only user 28 in this tenant)')
        print()
    
    # Check registration audit logs if available
    print('📋 CHECKING FOR REGISTRATION LOGS:')
    print('-' * 80)
    try:
        result = db.session.execute(
            text("""
                SELECT action, entity_type, old_values, new_values, created_at
                FROM audit_logs 
                WHERE entity_type = 'user' 
                AND (old_values::text LIKE '%28%' OR new_values::text LIKE '%28%')
                ORDER BY created_at DESC
                LIMIT 5
            """)
        )
        logs = result.fetchall()
        if logs:
            print(f'   Found {len(logs)} audit log entries:')
            for log in logs:
                print(f'   - {log[0]} at {log[4]}: {log[2]} -> {log[3]}')
        else:
            print('   No audit logs found')
    except Exception as e:
        print(f'   ⚠️  Could not check audit logs: {e}')
    print()
    
    print('='*80)
    print('CONCLUSION:')
    print('='*80)
    print('The tenant name "ewaru emmanuel\'s Company" was created automatically')
    print('during registration using the user\'s first_name and last_name.')
    print()
    print('This means during registration, the user entered:')
    print(f'  - first_name: "ewaru"')
    print(f'  - last_name: "emmanuel"')
    print()
    print('The registration code creates tenant name as:')
    print('  tenant.name = f"{first_name} {last_name}\'s Company"')
    print()
    print('If this is incorrect, the registration data itself may be wrong.')
    print('The tenant name should be updated during onboarding when company')
    print('information is collected, but since onboarding data wasn\'t saved,')
    print('the tenant name remains as the default from registration.')
    print()

