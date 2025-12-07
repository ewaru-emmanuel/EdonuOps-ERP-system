"""Check user_modules table schema"""
from app import create_app, db

app = create_app()
with app.app_context():
    # Check table structure
    result = db.session.execute(db.text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'user_modules' 
        ORDER BY ordinal_position
    """))
    
    print('=' * 60)
    print('user_modules TABLE SCHEMA')
    print('=' * 60)
    for row in result:
        print(f'{row[0]}: {row[1]} (nullable={row[2]}, default={row[3]})')
    
    # Check foreign key constraints
    print('\n' + '=' * 60)
    print('FOREIGN KEY CONSTRAINTS')
    print('=' * 60)
    fk_result = db.session.execute(db.text("""
        SELECT
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = 'user_modules'
    """))
    
    for row in fk_result:
        print(f'{row[2]} -> {row[3]}.{row[4]} (constraint: {row[0]})')






