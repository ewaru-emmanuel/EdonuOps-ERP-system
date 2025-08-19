#!/usr/bin/env python3
"""
Minimal test to check basic imports
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testing basic imports...")
    
    # Test Flask import
    from flask import Flask
    print("✅ Flask import successful")
    
    # Test SQLAlchemy import
    from flask_sqlalchemy import SQLAlchemy
    print("✅ SQLAlchemy import successful")
    
    # Test basic app creation
    app = Flask(__name__)
    print("✅ Flask app creation successful")
    
    print("🎉 Basic imports test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

