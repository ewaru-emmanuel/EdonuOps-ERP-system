"""Check onboarding progress data including challenges/problems"""
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Check onboarding_progress table structure
    try:
        result = db.session.execute(
            text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'onboarding_progress'
                ORDER BY ordinal_position
            """)
        )
        columns = result.fetchall()
        print(f'\n=== ONBOARDING_PROGRESS TABLE STRUCTURE ===\n')
        for col in columns:
            print(f'  {col[0]}: {col[1]}')
    except Exception as e:
        print(f'\n❌ Error checking table structure: {e}')
    
    # Check for data for user 28
    try:
        result = db.session.execute(
            text("""
                SELECT * FROM onboarding_progress 
                WHERE user_id = 28
            """)
        )
        progress_data = result.fetchall()
        
        if progress_data:
            print(f'\n=== ONBOARDING PROGRESS DATA FOR USER 28 ===\n')
            for row in progress_data:
                print(f'Step: {row[1] if len(row) > 1 else "N/A"}')
                print(f'Data: {row[2] if len(row) > 2 else "N/A"}')
                print(f'Completed: {row[3] if len(row) > 3 else "N/A"}')
                print(f'Completed At: {row[4] if len(row) > 4 else "N/A"}')
                print('---')
        else:
            print(f'\n⚠️ No onboarding progress data found for user 28')
    except Exception as e:
        print(f'\n❌ Error querying onboarding_progress: {e}')
    
    # Check if there's a JSON field or separate table for challenges/pain_points
    try:
        # Check for any JSON columns that might contain onboarding data
        result = db.session.execute(
            text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND (data_type LIKE '%json%' OR data_type LIKE '%text%')
            """)
        )
        json_columns = result.fetchall()
        if json_columns:
            print(f'\n=== POTENTIAL JSON/TEXT COLUMNS IN USERS TABLE ===\n')
            for col in json_columns:
                print(f'  - {col[0]}')
                # Try to get data for user 28
                try:
                    data_result = db.session.execute(
                        text(f"SELECT {col[0]} FROM users WHERE id = 28")
                    )
                    data = data_result.fetchone()
                    if data and data[0]:
                        print(f'    Value: {str(data[0])[:200]}...' if len(str(data[0])) > 200 else f'    Value: {data[0]}')
                except Exception as e:
                    print(f'    Could not read: {e}')
    except Exception as e:
        print(f'\n❌ Error checking JSON columns: {e}')
    
    # Check tenant table for company info
    try:
        result = db.session.execute(
            text("""
                SELECT id, name, domain, status, subscription_plan, created_at
                FROM tenants 
                WHERE id = 'tenant_bda648c1fa13'
            """)
        )
        tenant = result.fetchone()
        if tenant:
            print(f'\n=== TENANT/COMPANY INFO ===\n')
            print(f'Tenant ID: {tenant[0]}')
            print(f'Company Name: {tenant[1]}')
            print(f'Domain: {tenant[2]}')
            print(f'Status: {tenant[3]}')
            print(f'Plan: {tenant[4]}')
            print(f'Created: {tenant[5]}')
    except Exception as e:
        print(f'\n❌ Error checking tenant: {e}')


