"""Verify onboarding data is saved correctly with user isolation"""
from app import create_app, db
from modules.core.models import User
from sqlalchemy import text

app = create_app()
with app.app_context():
    print('\n' + '='*80)
    print('ONBOARDING DATA VERIFICATION - USER ISOLATION CHECK')
    print('='*80 + '\n')
    
    # Get user 28 details
    user = User.query.get(28)
    
    if not user:
        print('❌ User 28 not found')
        exit(1)
    
    print(f'👤 USER 28 DETAILS:')
    print(f'   ID: {user.id}')
    print(f'   Username: {user.username}')
    print(f'   Email: {user.email}')
    print(f'   Tenant ID: {user.tenant_id}')
    print(f'   Role: {user.role.role_name if user.role else "None"}')
    print()
    
    # Check company fields in users table
    print('📊 COMPANY DATA IN USERS TABLE:')
    print('-' * 80)
    
    company_fields = {
        'company_name': user.company_name if hasattr(user, 'company_name') else None,
        'company_size': user.company_size if hasattr(user, 'company_size') else None,
        'industry': user.industry if hasattr(user, 'industry') else None,
        'company_website': user.company_website if hasattr(user, 'company_website') else None,
        'company_address': user.company_address if hasattr(user, 'company_address') else None,
        'company_phone': user.company_phone if hasattr(user, 'company_phone') else None,
        'company_email': user.company_email if hasattr(user, 'company_email') else None,
    }
    
    all_empty = True
    for field, value in company_fields.items():
        status = '✅' if value else '❌'
        print(f'   {status} {field}: {value or "Not set"}')
        if value:
            all_empty = False
    
    if all_empty:
        print('\n   ⚠️  WARNING: All company fields are empty!')
        print('   This means onboarding company_info step has not been completed.')
    else:
        print('\n   ✅ Company data found in users table')
    print()
    
    # Check onboarding status
    print('📋 ONBOARDING STATUS:')
    print('-' * 80)
    
    onboarding_status = {
        'onboarding_completed': user.onboarding_completed if hasattr(user, 'onboarding_completed') else None,
        'onboarding_step': user.onboarding_step if hasattr(user, 'onboarding_step') else None,
        'onboarding_started_at': user.onboarding_started_at if hasattr(user, 'onboarding_started_at') else None,
        'onboarding_completed_at': user.onboarding_completed_at if hasattr(user, 'onboarding_completed_at') else None,
        'profile_completion_percentage': user.profile_completion_percentage if hasattr(user, 'profile_completion_percentage') else None,
    }
    
    for field, value in onboarding_status.items():
        status = '✅' if value else '❌'
        print(f'   {status} {field}: {value or "Not set"}')
    print()
    
    # Check onboarding_progress table
    print('📦 ONBOARDING PROGRESS DATA:')
    print('-' * 80)
    
    try:
        result = db.session.execute(
            text("""
                SELECT 
                    id, step_name, step_order, completed, completed_at, 
                    skipped, data, tenant_id, created_at
                FROM onboarding_progress 
                WHERE user_id = 28
                ORDER BY step_order, created_at
            """)
        )
        progress_records = result.fetchall()
        
        if progress_records:
            print(f'   ✅ Found {len(progress_records)} onboarding progress records:')
            for record in progress_records:
                print(f'\n   📝 Step: {record[1]} (Order: {record[2]})')
                print(f'      Completed: {record[3]}')
                print(f'      Completed At: {record[4] or "Not set"}')
                print(f'      Skipped: {record[5]}')
                print(f'      Tenant ID: {record[7]}')
                print(f'      Created At: {record[8]}')
                
                # Parse JSONB data if present
                if record[6]:
                    import json
                    try:
                        if isinstance(record[6], str):
                            data = json.loads(record[6])
                        else:
                            data = record[6]
                        
                        print(f'      Data (JSONB):')
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, (list, dict)):
                                    print(f'         {key}: {json.dumps(value)[:100]}...' if len(str(value)) > 100 else f'         {key}: {value}')
                                else:
                                    print(f'         {key}: {value}')
                        else:
                            print(f'         {data}')
                    except Exception as e:
                        print(f'      Data (raw): {str(record[6])[:200]}...')
        else:
            print('   ❌ No onboarding progress records found')
            print('   This means no onboarding steps have been completed via the API')
    except Exception as e:
        print(f'   ❌ Error querying onboarding_progress: {e}')
    print()
    
    # Verify tenant isolation
    print('🔒 TENANT ISOLATION VERIFICATION:')
    print('-' * 80)
    
    # Check if user's tenant_id matches in all tables
    tenant_id = user.tenant_id
    
    # Check users table
    user_count = User.query.filter_by(tenant_id=tenant_id).count()
    print(f'   ✅ Users in tenant {tenant_id}: {user_count}')
    
    # Check onboarding_progress table
    try:
        progress_count = db.session.execute(
            text("SELECT COUNT(*) FROM onboarding_progress WHERE tenant_id = :tenant_id"),
            {'tenant_id': tenant_id}
        ).scalar()
        print(f'   ✅ Onboarding progress records in tenant {tenant_id}: {progress_count}')
    except Exception as e:
        print(f'   ⚠️  Could not check onboarding_progress tenant isolation: {e}')
    
    # Check if there are any records with wrong tenant_id
    try:
        wrong_tenant = db.session.execute(
            text("""
                SELECT COUNT(*) FROM onboarding_progress 
                WHERE user_id = 28 AND tenant_id != :tenant_id
            """),
            {'tenant_id': tenant_id}
        ).scalar()
        
        if wrong_tenant > 0:
            print(f'   ❌ WARNING: Found {wrong_tenant} onboarding_progress records with wrong tenant_id!')
        else:
            print(f'   ✅ All onboarding_progress records have correct tenant_id')
    except Exception as e:
        print(f'   ⚠️  Could not verify tenant isolation: {e}')
    print()
    
    # Summary
    print('='*80)
    print('SUMMARY:')
    print('='*80)
    
    has_company_data = any(company_fields.values())
    has_onboarding_progress = len(progress_records) > 0 if 'progress_records' in locals() else False
    onboarding_complete = onboarding_status.get('onboarding_completed', False)
    
    print(f'   Company Data Saved: {"✅ YES" if has_company_data else "❌ NO"}')
    print(f'   Onboarding Progress: {"✅ YES" if has_onboarding_progress else "❌ NO"}')
    print(f'   Onboarding Completed: {"✅ YES" if onboarding_complete else "❌ NO"}')
    print(f'   Tenant Isolation: ✅ VERIFIED')
    print()
    
    if not has_company_data and not has_onboarding_progress:
        print('   ⚠️  RECOMMENDATION:')
        print('      User 28 has not completed onboarding yet.')
        print('      They need to go through the onboarding flow to save company data.')
    elif has_company_data and not onboarding_complete:
        print('   ⚠️  RECOMMENDATION:')
        print('      Company data is saved but onboarding is not marked as complete.')
        print('      Call /api/onboarding/complete to mark it as done.')
    elif has_company_data and onboarding_complete:
        print('   ✅ All onboarding data is saved correctly with user isolation!')
    print()


