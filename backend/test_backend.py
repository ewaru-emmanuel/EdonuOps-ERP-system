#!/usr/bin/env python3
"""
Simple test script to check if the backend can start without errors
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testing backend imports...")
    
    # Test basic imports
    from app import create_app, db
    print("✅ Basic app imports successful")
    
    # Test creating the app
    app = create_app()
    print("✅ App creation successful")
    
    # Test database connection
    with app.app_context():
        db.engine.execute("SELECT 1")
        print("✅ Database connection successful")
    
    print("🎉 Backend test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

