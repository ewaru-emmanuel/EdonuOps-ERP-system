#!/usr/bin/env python3
"""
Minimal backend test to identify startup issues
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backend():
    try:
        print("🔍 Testing backend startup...")
        
        # Test basic imports
        from flask import Flask
        print("✅ Flask imported")
        
        from flask_sqlalchemy import SQLAlchemy
        print("✅ SQLAlchemy imported")
        
        # Test app creation
        from app import create_app
        print("✅ App factory imported")
        
        # Create app
        app = create_app()
        print("✅ App created")
        
        # Test database context
        with app.app_context():
            from app import db
            print("✅ Database context created")
            
            # Test if we can access the database
            print("✅ Database accessible")
        
        print("🎉 Backend test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backend()
    if not success:
        sys.exit(1)

