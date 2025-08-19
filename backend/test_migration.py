#!/usr/bin/env python3
"""
Test script to debug migration issues
"""

import os
import sys

print("Testing Flask-Migrate import...")
try:
    from flask_migrate import init, migrate, upgrade
    print("✅ Flask-Migrate imported successfully")
except ImportError as e:
    print(f"❌ Flask-Migrate import failed: {e}")
    sys.exit(1)

print("Testing app creation...")
try:
    from app import create_app
    app = create_app()
    print("✅ App created successfully")
except Exception as e:
    print(f"❌ App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Testing app context...")
try:
    with app.app_context():
        print("✅ App context works")
        
        # Test if migrations directory exists
        if os.path.exists('migrations'):
            print("✅ Migrations directory exists")
        else:
            print("⚠️  Migrations directory does not exist")
            print("Initializing migrations...")
            try:
                init()
                print("✅ Migrations initialized successfully")
            except Exception as e:
                print(f"❌ Migration initialization failed: {e}")
                import traceback
                traceback.print_exc()
            
        # Apply existing migrations first
        print("Applying existing migrations...")
        try:
            upgrade()
            print("✅ Migrations applied successfully")
        except Exception as e:
            print(f"❌ Migration upgrade failed: {e}")
            import traceback
            traceback.print_exc()
            
        # Test migration creation
        print("Testing migration creation...")
        try:
            migrate(message="Test migration")
            print("✅ Migration created successfully")
        except Exception as e:
            print(f"❌ Migration creation failed: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ App context failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("All tests passed!")
