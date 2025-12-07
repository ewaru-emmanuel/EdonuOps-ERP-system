#!/usr/bin/env python3
"""
🎉 EDONUOPS ERP - PHASE 2 FINALIZATION
============================================================

Finalizes Phase 2 database implementation with remaining fixes.

Author: EdonuOps Team
Date: 2024
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    # Load environment variables
    load_dotenv('config.env')
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url, echo=False)

    print('🔧 FINALIZING PHASE 2 IMPLEMENTATION')
    print('=' * 50)

    with engine.connect() as conn:
        # Fix materialized view refresh function
        conn.execute(text('''
            CREATE OR REPLACE FUNCTION refresh_tenant_activity_views()
            RETURNS VOID AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW tenant_login_summary;
                REFRESH MATERIALIZED VIEW tenant_token_usage;
                REFRESH MATERIALIZED VIEW tenant_security_alerts;
            END;
            $$ LANGUAGE plpgsql;
        '''))
        print('✅ Fixed materialized view refresh function')
        
        # Add unique constraint to sample queries
        conn.execute(text('''
            ALTER TABLE sample_queries 
            ADD CONSTRAINT unique_query_name UNIQUE (query_name);
        '''))
        print('✅ Added unique constraint to sample queries')
        
        # Insert sample queries
        sample_queries = [
            ('get_tenant_users', 'Get all users for current tenant', 'SELECT id, username, email, is_active, last_login FROM users WHERE tenant_id = current_setting(\'my.tenant_id\', true);', 'users'),
            ('get_login_attempts_summary', 'Get login attempt summary for current tenant', 'SELECT DATE(attempt_time) as date, COUNT(*) as attempts, COUNT(CASE WHEN success = TRUE THEN 1 END) as successful FROM login_attempts WHERE tenant_id = current_setting(\'my.tenant_id\', true) GROUP BY DATE(attempt_time) ORDER BY date DESC LIMIT 7;', 'security'),
            ('get_active_tokens', 'Get active tokens for current tenant', 'SELECT \'email_verification\' as type, COUNT(*) as active FROM email_verification_tokens WHERE tenant_id = current_setting(\'my.tenant_id\', true) AND expires_at > NOW() AND used = FALSE UNION ALL SELECT \'password_reset\' as type, COUNT(*) as active FROM password_reset_tokens WHERE tenant_id = current_setting(\'my.tenant_id\', true) AND expires_at > NOW() AND used = FALSE;', 'security'),
            ('get_tenant_audit_logs', 'Get recent audit logs for current tenant', 'SELECT table_name, action_type, timestamp, user_id FROM audit_logs WHERE tenant_id = current_setting(\'my.tenant_id\', true) ORDER BY timestamp DESC LIMIT 50;', 'audit')
        ]
        
        for name, desc, query, category in sample_queries:
            conn.execute(text('''
                INSERT INTO sample_queries (query_name, description, query_sql, category)
                VALUES (:name, :description, :query, :category)
                ON CONFLICT (query_name) DO NOTHING
            '''), {'name': name, 'description': desc, 'query': query, 'category': category})
        
        print('✅ Inserted sample queries')
        
        conn.commit()
        print('🎉 PHASE 2 DATABASE IMPLEMENTATION COMPLETE!')

if __name__ == "__main__":
    main()
