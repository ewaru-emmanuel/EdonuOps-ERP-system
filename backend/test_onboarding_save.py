"""Test onboarding data saving with user isolation"""
from app import create_app, db
from modules.core.models import User
from modules.core.tenant_helpers import get_current_user_tenant_id, get_current_user_id
from sqlalchemy import text
import json

app = create_app()
with app.app_context():
    print('\n' + '='*80)
    print('TESTING ONBOARDING DATA SAVING - USER ISOLATION')
    print('='*80 + '\n')
    
    # Get user 28
    user = User.query.get(28)
    if not user:
        print('❌ User 28 not found')
        exit(1)
    
    tenant_id = user.tenant_id
    user_id = user.id
    
    print(f'👤 Testing with User ID: {user_id}')
    print(f'🏢 Tenant ID: {tenant_id}')
    print()
    
    # Simulate company_info step data
    company_data = {
        'company_name': 'Test Company Name',
        'company_size': 'small',
        'industry': 'retail',
        'company_website': 'https://testcompany.com',
        'company_address': '123 Test Street',
        'company_phone': '+1234567890',
        'company_email': 'info@testcompany.com',
        'challenges': ['inventory_issues', 'financial_chaos'],
        'pain_points': ['inventory_issues', 'financial_chaos'],
        'goals': ['grow_revenue', 'improve_efficiency'],
        'annualRevenue': '100000'
    }
    
    print('📝 Simulating company_info step save...')
    print(f'   Data: {json.dumps(company_data, indent=2)}')
    print()
    
    # Test 1: Save company info to users table
    print('TEST 1: Saving company info to users table...')
    try:
        # Map frontend fields to database columns
        update_fields = []
        update_values = {}
        
        field_mapping = {
            'company_name': 'company_name',
            'company_size': 'company_size',
            'industry': 'industry',
            'company_website': 'company_website',
            'company_address': 'company_address',
            'company_phone': 'company_phone',
            'company_email': 'company_email',
        }
        
        for field, value in company_data.items():
            if field in field_mapping and value:
                db_field = field_mapping[field]
                update_fields.append(f"{db_field} = :{db_field}")
                update_values[db_field] = value
        
        if update_fields:
            update_sql = f"""
                UPDATE users 
                SET {', '.join(update_fields)}, last_profile_update = NOW()
                WHERE id = :user_id AND tenant_id = :tenant_id
            """
            update_values['user_id'] = user_id
            update_values['tenant_id'] = tenant_id
            
            result = db.session.execute(text(update_sql), update_values)
            db.session.commit()
            
            print(f'   ✅ Updated {result.rowcount} row(s) in users table')
        else:
            print('   ⚠️  No fields to update')
    except Exception as e:
        db.session.rollback()
        print(f'   ❌ Error: {e}')
        import traceback
        traceback.print_exc()
    
    # Test 2: Save to onboarding_progress table
    print('\nTEST 2: Saving to onboarding_progress table...')
    try:
        # Check if complete_onboarding_step function exists
        try:
            result = db.session.execute(
                text("""
                    SELECT complete_onboarding_step(:user_id, :step_name, :data, :skipped)
                """),
                {
                    'user_id': user_id,
                    'step_name': 'company_info',
                    'data': json.dumps(company_data),
                    'skipped': False
                }
            )
            success = result.scalar()
            db.session.commit()
            
            if success:
                print('   ✅ Saved to onboarding_progress using complete_onboarding_step function')
            else:
                print('   ⚠️  Function returned False')
        except Exception as e:
            # If function doesn't exist, insert directly
            print(f'   ⚠️  Function not available, inserting directly: {e}')
            
            # Get step order
            step_order_result = db.session.execute(
                text("""
                    SELECT step_order FROM onboarding_steps 
                    WHERE step_name = 'company_info' 
                    LIMIT 1
                """)
            )
            step_order_row = step_order_result.fetchone()
            step_order = step_order_row[0] if step_order_row else 3
            
            # Insert directly
            insert_sql = text("""
                INSERT INTO onboarding_progress 
                (user_id, step_name, step_order, completed, completed_at, skipped, data, tenant_id, created_at, updated_at)
                VALUES 
                (:user_id, :step_name, :step_order, :completed, NOW(), :skipped, :data::jsonb, :tenant_id, NOW(), NOW())
                ON CONFLICT (user_id, step_name) 
                DO UPDATE SET 
                    completed = :completed,
                    completed_at = NOW(),
                    skipped = :skipped,
                    data = :data::jsonb,
                    updated_at = NOW()
            """)
            
            db.session.execute(insert_sql, {
                'user_id': user_id,
                'step_name': 'company_info',
                'step_order': step_order,
                'completed': True,
                'skipped': False,
                'data': json.dumps(company_data),
                'tenant_id': tenant_id
            })
            db.session.commit()
            print('   ✅ Saved to onboarding_progress table directly')
    except Exception as e:
        db.session.rollback()
        print(f'   ❌ Error: {e}')
        import traceback
        traceback.print_exc()
    
    # Test 3: Mark onboarding as complete
    print('\nTEST 3: Marking onboarding as complete...')
    try:
        db.session.execute(
            text("""
                UPDATE users 
                SET onboarding_completed = TRUE, onboarding_completed_at = NOW()
                WHERE id = :user_id AND tenant_id = :tenant_id
            """),
            {'user_id': user_id, 'tenant_id': tenant_id}
        )
        db.session.commit()
        print('   ✅ Marked onboarding as complete')
    except Exception as e:
        db.session.rollback()
        print(f'   ❌ Error: {e}')
    
    # Verify the data was saved
    print('\n' + '='*80)
    print('VERIFICATION:')
    print('='*80 + '\n')
    
    # Reload user
    db.session.refresh(user)
    
    print('📊 Users Table:')
    print(f'   company_name: {user.company_name or "Not set"}')
    print(f'   company_size: {user.company_size or "Not set"}')
    print(f'   industry: {user.industry or "Not set"}')
    print(f'   onboarding_completed: {user.onboarding_completed}')
    print()
    
    # Check onboarding_progress
    result = db.session.execute(
        text("""
            SELECT step_name, completed, data 
            FROM onboarding_progress 
            WHERE user_id = :user_id AND tenant_id = :tenant_id
        """),
        {'user_id': user_id, 'tenant_id': tenant_id}
    )
    progress = result.fetchall()
    
    print('📦 Onboarding Progress:')
    if progress:
        for record in progress:
            print(f'   Step: {record[0]}, Completed: {record[1]}')
            if record[2]:
                data = json.loads(record[2]) if isinstance(record[2], str) else record[2]
                print(f'   Data keys: {list(data.keys()) if isinstance(data, dict) else "N/A"}')
    else:
        print('   No records found')
    print()
    
    print('✅ Test complete!')
    print()


