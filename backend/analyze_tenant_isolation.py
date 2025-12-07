#!/usr/bin/env python3
"""
Tenant Isolation Analysis
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def analyze_tenant_isolation():
    """Analyze current tenant isolation implementation"""
    
    load_dotenv('config.env')
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    print('🏢 EDONUOPS ERP - TENANT ISOLATION ANALYSIS')
    print('=' * 60)
    print()
    
    with engine.connect() as conn:
        # Check which tables have tenant_id columns
        result = conn.execute(text('''
            SELECT table_name, column_name, data_type
            FROM information_schema.columns 
            WHERE column_name = 'tenant_id'
            ORDER BY table_name
        '''))
        
        tenant_tables = result.fetchall()
        
        print('🏢 TABLES WITH TENANT_ID COLUMNS:')
        print('=' * 50)
        
        if tenant_tables:
            for table in tenant_tables:
                print(f'   • {table[0]}: {table[1]} ({table[2]})')
        else:
            print('   ⚠️  No tables with tenant_id found!')
        
        print()
        
        # Check which tables have user_id columns
        result = conn.execute(text('''
            SELECT table_name, column_name, data_type
            FROM information_schema.columns 
            WHERE column_name = 'user_id'
            ORDER BY table_name
        '''))
        
        user_tables = result.fetchall()
        
        print('👤 TABLES WITH USER_ID COLUMNS:')
        print('=' * 50)
        
        if user_tables:
            for table in user_tables:
                print(f'   • {table[0]}: {table[1]} ({table[2]})')
        else:
            print('   ⚠️  No tables with user_id found!')
        
        print()
        
        # Get all table names to see what's missing tenant isolation
        result = conn.execute(text('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name NOT IN ('tenants', 'user_tenants', 'tenant_modules')
            ORDER BY table_name
        '''))
        
        all_tables = [row[0] for row in result.fetchall()]
        tenant_table_names = [t[0] for t in tenant_tables]
        
        print('⚠️  TABLES MISSING TENANT_ID (NEED TENANT ISOLATION):')
        print('=' * 60)
        
        missing_tenant_isolation = [t for t in all_tables if t not in tenant_table_names]
        
        if missing_tenant_isolation:
            for table in missing_tenant_isolation:
                print(f'   • {table}')
        else:
            print('   ✅ All tables have tenant isolation!')
        
        print()
        
        # Categorize tables by module
        print('📊 TENANT ISOLATION BY MODULE:')
        print('=' * 60)
        
        core_tables = []
        finance_tables = []
        inventory_tables = []
        crm_tables = []
        other_tables = []
        
        for table in missing_tenant_isolation:
            if table in ['users', 'roles', 'organizations', 'audit_logs']:
                core_tables.append(table)
            elif any(keyword in table for keyword in ['account', 'journal', 'payment', 'bank', 'chart', 'ledger', 'department', 'cost', 'project']):
                finance_tables.append(table)
            elif any(keyword in table for keyword in ['product', 'inventory', 'stock', 'supplier', 'purchase', 'category']):
                inventory_tables.append(table)
            elif any(keyword in table for keyword in ['customer', 'lead', 'opportunity', 'contact', 'crm']):
                crm_tables.append(table)
            else:
                other_tables.append(table)
        
        if core_tables:
            print('🔧 CORE MODULE (Missing tenant_id):')
            for table in core_tables:
                print(f'   • {table}')
            print()
        
        if finance_tables:
            print('💰 FINANCE MODULE (Missing tenant_id):')
            for table in finance_tables:
                print(f'   • {table}')
            print()
        
        if inventory_tables:
            print('📦 INVENTORY MODULE (Missing tenant_id):')
            for table in inventory_tables:
                print(f'   • {table}')
            print()
        
        if crm_tables:
            print('👥 CRM MODULE (Missing tenant_id):')
            for table in crm_tables:
                print(f'   • {table}')
            print()
        
        if other_tables:
            print('🔧 OTHER MODULES (Missing tenant_id):')
            for table in other_tables:
                print(f'   • {table}')
            print()
        
        print(f'📊 SUMMARY:')
        print(f'   • Total tables: {len(all_tables)}')
        print(f'   • Tables with tenant_id: {len(tenant_tables)}')
        print(f'   • Tables missing tenant_id: {len(missing_tenant_isolation)}')
        print(f'   • Tenant isolation coverage: {len(tenant_tables)/len(all_tables)*100:.1f}%')

if __name__ == '__main__':
    analyze_tenant_isolation()

