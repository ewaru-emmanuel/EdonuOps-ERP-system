"""Check onboarding data for user 28"""
from app import create_app, db
from modules.core.models import User
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Get user 28's complete onboarding data
    result = db.session.execute(
        text("""
            SELECT 
                id, username, email, tenant_id,
                company_name, company_size, industry, company_website,
                company_address, company_phone, company_email,
                onboarding_completed, onboarding_step,
                onboarding_started_at, onboarding_completed_at,
                profile_completion_percentage
            FROM users 
            WHERE id = 28
        """)
    )
    user = result.fetchone()
    
    if user:
        print(f'\n=== USER 28 ONBOARDING DATA ===\n')
        print(f'User ID: {user[0]}')
        print(f'Username: {user[1]}')
        print(f'Email: {user[2]}')
        print(f'Tenant ID: {user[3]}')
        
        print(f'\n--- Company Information ---')
        print(f'Company Name: {user[4] or "❌ Not set"}')
        print(f'Company Size: {user[5] or "❌ Not set"}')
        print(f'Industry: {user[6] or "❌ Not set"}')
        print(f'Company Website: {user[7] or "❌ Not set"}')
        print(f'Company Address: {user[8] or "❌ Not set"}')
        print(f'Company Phone: {user[9] or "❌ Not set"}')
        print(f'Company Email: {user[10] or "❌ Not set"}')
        
        print(f'\n--- Onboarding Status ---')
        print(f'Onboarding Completed: {user[11]}')
        print(f'Onboarding Step: {user[12]}')
        print(f'Onboarding Started At: {user[13] or "❌ Not started"}')
        print(f'Onboarding Completed At: {user[14] or "❌ Not completed"}')
        print(f'Profile Completion: {user[15]}%')
        
        # Check if there's an onboarding_data table or JSON field
        try:
            result2 = db.session.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name LIKE '%onboarding%'")
            )
            onboarding_columns = result2.fetchall()
            if onboarding_columns:
                print(f'\n--- Additional Onboarding Columns ---')
                for col in onboarding_columns:
                    print(f'  - {col[0]}')
        except Exception as e:
            print(f'\nNote: Could not check for onboarding columns: {e}')
        
        # Check for onboarding_data table
        try:
            result3 = db.session.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%onboarding%'")
            )
            onboarding_tables = result3.fetchall()
            if onboarding_tables:
                print(f'\n--- Onboarding Tables Found ---')
                for table in onboarding_tables:
                    print(f'  - {table[0]}')
                    # Try to get data from this table for user 28
                    try:
                        table_data = db.session.execute(
                            text(f"SELECT * FROM {table[0]} WHERE user_id = 28")
                        )
                        data = table_data.fetchall()
                        if data:
                            print(f'    Data found: {len(data)} records')
                            for row in data:
                                print(f'    {row}')
                    except Exception as e:
                        print(f'    Could not query: {e}')
        except Exception as e:
            print(f'\nNote: Could not check for onboarding tables: {e}')
    else:
        print('\n❌ User 28 not found')


