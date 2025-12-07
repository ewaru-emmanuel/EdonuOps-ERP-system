"""Check user 28's complete onboarding information"""
from app import create_app, db
from modules.core.models import User
from modules.core.tenant_models import Tenant
from sqlalchemy import text
import json

app = create_app()
with app.app_context():
    print('\n' + '='*80)
    print('USER 28 ONBOARDING DATA VERIFICATION')
    print('='*80 + '\n')
    
    # Get user 28
    user = User.query.get(28)
    if not user:
        print('❌ User 28 not found')
        exit(1)
    
    print(f'👤 USER INFORMATION:')
    print('-' * 80)
    print(f'   ID: {user.id}')
    print(f'   Username: {user.username}')
    print(f'   Email: {user.email}')
    print(f'   First Name: {getattr(user, "first_name", "Not set")}')
    print(f'   Last Name: {getattr(user, "last_name", "Not set")}')
    print(f'   Phone: {getattr(user, "phone_number", "Not set")}')
    print(f'   Role: {user.role.role_name if user.role else "Not set"}')
    print(f'   Tenant ID: {user.tenant_id}')
    print()
    
    # Get tenant information
    if user.tenant_id:
        tenant = Tenant.query.filter_by(id=user.tenant_id).first()
        if tenant:
            print(f'🏢 TENANT INFORMATION:')
            print('-' * 80)
            print(f'   Tenant ID: {tenant.id}')
            print(f'   Tenant Name: {tenant.name}')
            print(f'   Domain: {tenant.domain}')
            print(f'   Subscription Plan: {tenant.subscription_plan}')
            print(f'   Status: {tenant.status}')
            print(f'   Created At: {tenant.created_at}')
            print()
    
    # Check company data in users table
    print('📊 COMPANY DATA (from users table):')
    print('-' * 80)
    
    company_fields = {
        'company_name': getattr(user, 'company_name', None),
        'company_size': getattr(user, 'company_size', None),
        'industry': getattr(user, 'industry', None),
        'company_website': getattr(user, 'company_website', None),
        'company_address': getattr(user, 'company_address', None),
        'company_phone': getattr(user, 'company_phone', None),
        'company_email': getattr(user, 'company_email', None),
        'annual_revenue': getattr(user, 'annual_revenue', None),
    }
    
    has_company_data = False
    for field, value in company_fields.items():
        if value:
            print(f'   ✅ {field}: {value}')
            has_company_data = True
        else:
            print(f'   ❌ {field}: Not set')
    
    if not has_company_data:
        print('\n   ⚠️  No company data found in users table')
    print()
    
    # Check onboarding status
    print('📋 ONBOARDING STATUS:')
    print('-' * 80)
    
    onboarding_fields = {
        'onboarding_completed': getattr(user, 'onboarding_completed', None),
        'onboarding_step': getattr(user, 'onboarding_step', None),
        'onboarding_started_at': getattr(user, 'onboarding_started_at', None),
        'onboarding_completed_at': getattr(user, 'onboarding_completed_at', None),
        'profile_completion_percentage': getattr(user, 'profile_completion_percentage', None),
    }
    
    for field, value in onboarding_fields.items():
        if value is not None:
            print(f'   ✅ {field}: {value}')
        else:
            print(f'   ❌ {field}: Not set')
    print()
    
    # Check onboarding_progress table
    print('📦 ONBOARDING PROGRESS RECORDS:')
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
            print(f'   ✅ Found {len(progress_records)} onboarding progress records:\n')
            for record in progress_records:
                print(f'   📝 Step: {record[1]} (Order: {record[2]})')
                print(f'      ID: {record[0]}')
                print(f'      Completed: {record[3]}')
                print(f'      Completed At: {record[4] or "Not set"}')
                print(f'      Skipped: {record[5]}')
                print(f'      Tenant ID: {record[7]}')
                print(f'      Created At: {record[8]}')
                
                # Parse JSONB data if present
                if record[6]:
                    try:
                        if isinstance(record[6], str):
                            data = json.loads(record[6])
                        else:
                            data = record[6]
                        
                        print(f'      Data (JSONB):')
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, (list, dict)):
                                    value_str = json.dumps(value, indent=8)
                                    if len(value_str) > 200:
                                        print(f'         {key}: {value_str[:200]}...')
                                    else:
                                        print(f'         {key}: {value_str}')
                                else:
                                    print(f'         {key}: {value}')
                        else:
                            print(f'         {data}')
                    except Exception as e:
                        print(f'      Data (raw): {str(record[6])[:200]}...')
                        print(f'      ⚠️  Error parsing JSON: {e}')
                else:
                    print(f'      Data: None')
                print()
        else:
            print('   ❌ No onboarding progress records found')
            print('   This means no onboarding steps have been completed via the API')
    except Exception as e:
        print(f'   ❌ Error querying onboarding_progress: {e}')
        import traceback
        traceback.print_exc()
    print()
    
    # Check user modules (if any)
    print('🔧 USER MODULES:')
    print('-' * 80)
    
    try:
        modules_result = db.session.execute(
            text("""
                SELECT module_id, module_name, is_active, activated_at
                FROM user_modules 
                WHERE user_id = 28
                ORDER BY module_name
            """)
        )
        modules = modules_result.fetchall()
        
        if modules:
            print(f'   ✅ Found {len(modules)} modules:\n')
            for module in modules:
                print(f'   📦 {module[1]} (ID: {module[0]})')
                print(f'      Active: {module[2]}')
                print(f'      Activated At: {module[3] or "Not set"}')
                print()
        else:
            print('   ℹ️  No modules found (user may not have selected modules yet)')
    except Exception as e:
        print(f'   ⚠️  Could not check user_modules: {e}')
    print()
    
    # Summary
    print('='*80)
    print('SUMMARY:')
    print('='*80)
    
    has_company_data = any(company_fields.values())
    has_onboarding_progress = len(progress_records) > 0 if 'progress_records' in locals() else False
    onboarding_complete = onboarding_fields.get('onboarding_completed', False)
    tenant_name_updated = tenant.name != f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}'s Company" if tenant else False
    
    print(f'   Company Data Saved: {"✅ YES" if has_company_data else "❌ NO"}')
    print(f'   Onboarding Progress: {"✅ YES" if has_onboarding_progress else "❌ NO"}')
    print(f'   Onboarding Completed: {"✅ YES" if onboarding_complete else "❌ NO"}')
    print(f'   Tenant Name Updated: {"✅ YES" if tenant_name_updated else "❌ NO"}')
    
    if has_company_data:
        print(f'\n   📝 Company Name: {company_fields.get("company_name", "Not set")}')
        print(f'   📝 Industry: {company_fields.get("industry", "Not set")}')
        print(f'   📝 Company Size: {company_fields.get("company_size", "Not set")}')
    
    if tenant:
        print(f'\n   🏢 Tenant Name: {tenant.name}')
    
    print()

