#!/usr/bin/env python3
"""
Migration script to create audit trail tables
"""

import sqlite3
import os

def create_audit_tables():
    """Create all audit-related tables"""
    
    # Get database path - check multiple possible locations
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'edonuops.db'),
        os.path.join(os.path.dirname(__file__), '..', 'edonuops.db'),
        'edonuops.db',
        '../edonuops.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"Database not found in any of these locations: {possible_paths}")
        return False
    
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Creating audit trail tables...")
        
        # Create audit_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                username VARCHAR(100),
                user_role VARCHAR(50),
                action VARCHAR(100) NOT NULL,
                entity_type VARCHAR(100) NOT NULL,
                entity_id VARCHAR(100),
                ip_address VARCHAR(45),
                user_agent TEXT,
                request_method VARCHAR(10),
                request_url VARCHAR(500),
                old_values JSON,
                new_values JSON,
                changes_summary TEXT,
                module VARCHAR(50) NOT NULL,
                source VARCHAR(100),
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                session_id VARCHAR(100),
                correlation_id VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create login_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                username VARCHAR(100) NOT NULL,
                action VARCHAR(20) NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                session_id VARCHAR(100),
                success BOOLEAN DEFAULT 1,
                failure_reason VARCHAR(200),
                is_suspicious BOOLEAN DEFAULT 0,
                country VARCHAR(100),
                city VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create permission_changes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permission_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                admin_user_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                change_type VARCHAR(50) NOT NULL,
                old_role VARCHAR(50),
                new_role VARCHAR(50),
                permissions_added JSON,
                permissions_removed JSON,
                reason TEXT,
                ip_address VARCHAR(45),
                FOREIGN KEY (admin_user_id) REFERENCES users (id),
                FOREIGN KEY (target_user_id) REFERENCES users (id)
            )
        ''')
        
        # Create system_events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                event_type VARCHAR(100) NOT NULL,
                event_category VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL DEFAULT 'INFO',
                user_id INTEGER,
                username VARCHAR(100),
                description TEXT NOT NULL,
                details JSON,
                ip_address VARCHAR(45),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes for performance
        print("Creating indexes...")
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_module ON audit_logs (module)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs (action)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs (entity_type)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_history_timestamp ON login_history (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_history_success ON login_history (success)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_permission_changes_timestamp ON permission_changes (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_permission_changes_admin_user_id ON permission_changes (admin_user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_permission_changes_target_user_id ON permission_changes (target_user_id)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_events_event_type ON system_events (event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events (severity)')
        
        # Commit changes
        conn.commit()
        
        print("✅ Audit trail tables created successfully!")
        
        # Log the system event
        cursor.execute('''
            INSERT INTO system_events (event_type, event_category, severity, description, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'MIGRATION_COMPLETED',
            'SYSTEM',
            'INFO',
            'Audit trail tables created successfully',
            '{"tables": ["audit_logs", "login_history", "permission_changes", "system_events"], "indexes_created": 10}'
        ))
        
        conn.commit()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating audit tables: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    success = create_audit_tables()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("Audit trail system is now ready for use.")
    else:
        print("\n💥 Migration failed!")
        exit(1)
