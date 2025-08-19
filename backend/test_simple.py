#!/usr/bin/env python3
"""
Simple test script to check backend startup and identify errors
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testing backend imports...")
    
    # Test basic Flask imports
    from flask import Flask
    print("✅ Flask imported successfully")
    
    # Test SQLAlchemy
    from flask_sqlalchemy import SQLAlchemy
    print("✅ SQLAlchemy imported successfully")
    
    # Test app creation
    from app import create_app
    print("✅ App factory imported successfully")
    
    # Test app creation
    app = create_app()
    print("✅ App created successfully")
    
    # Test database
    with app.app_context():
        from app import db
        print("✅ Database context created successfully")
        
        # Test if tables exist
        try:
            from modules.crm.models import Contact
            print("✅ CRM models imported successfully")
            
            # Try to query contacts
            contacts = Contact.query.all()
            print(f"✅ CRM query successful, found {len(contacts)} contacts")
            
        except Exception as e:
            print(f"❌ CRM query failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Backend test completed successfully!")
    
except Exception as e:
    print(f"❌ Backend test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

