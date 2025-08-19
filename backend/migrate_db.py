#!/usr/bin/env python3
"""
SQLAlchemy Migration Helper
Provides simple database migration commands for development
"""

import os
from app import create_app

def init_migrations():
    """Initialize Flask-Migrate for database migrations"""
    try:
        from flask_migrate import init
        app = create_app()
        
        with app.app_context():
            if not os.path.exists('migrations'):
                init()
                print("✅ Migration repository initialized")
            else:
                print("⚠️  Migration repository already exists")
    except ImportError:
        print("❌ Flask-Migrate not installed. Install with: pip install Flask-Migrate")

def create_migration(message="Auto migration"):
    """Create a new migration"""
    try:
        from flask_migrate import migrate
        app = create_app()
        
        with app.app_context():
            migrate(message=message)
            print(f"✅ Migration created: {message}")
    except ImportError:
        print("❌ Flask-Migrate not installed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

def apply_migrations():
    """Apply pending migrations"""
    try:
        from flask_migrate import upgrade
        app = create_app()
        
        with app.app_context():
            upgrade()
            print("✅ Migrations applied successfully")
    except ImportError:
        print("❌ Flask-Migrate not installed")
    except Exception as e:
        print(f"❌ Migration upgrade failed: {e}")

def migration_status():
    """Show current migration status"""
    try:
        from flask_migrate import current, show
        app = create_app()
        
        with app.app_context():
            current_rev = current()
            print(f"📍 Current migration: {current_rev}")
            
            # Show migration history
            show()
    except ImportError:
        print("❌ Flask-Migrate not installed")
    except Exception as e:
        print(f"❌ Cannot check migration status: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("📋 SQLAlchemy Migration Helper")
        print("Usage:")
        print("  python migrate_db.py init          - Initialize migrations")
        print("  python migrate_db.py create [msg]  - Create new migration")
        print("  python migrate_db.py apply         - Apply migrations")
        print("  python migrate_db.py status        - Show status")
    else:
        command = sys.argv[1]
        
        if command == 'init':
            init_migrations()
        elif command == 'create':
            message = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else "Auto migration"
            create_migration(message)
        elif command == 'apply':
            apply_migrations()
        elif command == 'status':
            migration_status()
        else:
            print(f"❌ Unknown command: {command}")







