#!/usr/bin/env python3
"""Simple startup script for EdonuOps backend"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, socketio
    
    print("🚀 Starting EdonuOps backend...")
    
    app = create_app()
    
    print("✅ App created successfully")
    print("🌐 Starting server on http://localhost:5000")
    
    # Start the server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()


