#!/usr/bin/env python3
"""
Check PostgreSQL Database Tables
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def check_database_tables():
    """Check what tables exist in our PostgreSQL database"""
    
    # Load environment variables
    load_dotenv('config.env')
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print('❌ DATABASE_URL not found in config.env')
        return
    
    print('🔗 Connecting to PostgreSQL database...')
    print(f'🔗 Database URL: {database_url[:50]}...')
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            print('\n🗄️  POSTGRESQL DATABASE TABLES')
            print('=' * 50)
            print(f'📊 Total tables: {len(tables)}')
            print()
            
            if not tables:
                print('⚠️  No tables found in database!')
                return
            
            # Group tables by module
            core_tables = []
            finance_tables = []
            inventory_tables = []
            crm_tables = []
            other_tables = []
            
            for table in tables:
                if table in ['users', 'roles', 'organizations', 'user_modules', 'user_preferences', 'audit_logs']:
                    core_tables.append(table)
                elif any(keyword in table for keyword in ['account', 'journal', 'payment', 'bank', 'chart', 'ledger', 'department', 'cost', 'project']):
                    finance_tables.append(table)
                elif any(keyword in table for keyword in ['product', 'inventory', 'stock', 'supplier', 'purchase', 'category']):
                    inventory_tables.append(table)
                elif any(keyword in table for keyword in ['customer', 'lead', 'opportunity', 'contact', 'crm']):
                    crm_tables.append(table)
                else:
                    other_tables.append(table)
            
            # Display tables by module
            if core_tables:
                print('🔧 CORE MODULE TABLES:')
                for table in core_tables:
                    print(f'   • {table}')
                print()
            
            if finance_tables:
                print('💰 FINANCE MODULE TABLES:')
                for table in finance_tables:
                    print(f'   • {table}')
                print()
            
            if inventory_tables:
                print('📦 INVENTORY MODULE TABLES:')
                for table in inventory_tables:
                    print(f'   • {table}')
                print()
            
            if crm_tables:
                print('👥 CRM MODULE TABLES:')
                for table in crm_tables:
                    print(f'   • {table}')
                print()
            
            if other_tables:
                print('🔧 OTHER TABLES:')
                for table in other_tables:
                    print(f'   • {table}')
                print()
            
            # Get detailed info for key tables
            print('📋 KEY TABLE DETAILS:')
            print('=' * 50)
            
            key_tables = ['users', 'roles', 'organizations']
            for table_name in key_tables:
                if table_name in tables:
                    result = conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}' 
                        ORDER BY ordinal_position
                    """))
                    
                    columns = result.fetchall()
                    print(f'\n📊 {table_name.upper()} TABLE ({len(columns)} columns):')
                    for col in columns:
                        nullable = 'NULL' if col[2] == 'YES' else 'NOT NULL'
                        print(f'   • {col[0]} ({col[1]}) - {nullable}')
            
            print('\n✅ Database check completed successfully!')
            
    except Exception as e:
        print(f'❌ Database check failed: {e}')
        print(f'Error type: {type(e).__name__}')

if __name__ == '__main__':
    check_database_tables()

