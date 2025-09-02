#!/usr/bin/env python3
"""
Force Restart Server
Kills all Python processes and restarts the server to clear SQLAlchemy cache
"""

import os
import subprocess
import time
import signal

def kill_python_processes():
    """Kill all Python processes"""
    try:
        # On Windows
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, check=False)
        print("✅ Killed all Python processes")
    except Exception as e:
        print(f"⚠️ Could not kill processes: {e}")

def clear_pycache():
    """Clear Python cache files"""
    try:
        # Remove __pycache__ directories
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    cache_path = os.path.join(root, dir_name)
                    import shutil
                    shutil.rmtree(cache_path)
                    print(f"🗑️ Removed cache: {cache_path}")
        print("✅ Cleared Python cache")
    except Exception as e:
        print(f"⚠️ Could not clear cache: {e}")

def restart_server():
    """Restart the Flask server"""
    try:
        print("🚀 Starting Flask server...")
        # Start server in background
        subprocess.Popen(['python', 'run.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        print("✅ Server started in background")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main function to force restart"""
    print("🔄 Force Restarting Server")
    print("=" * 40)
    
    # Kill existing processes
    kill_python_processes()
    
    # Wait a moment
    time.sleep(2)
    
    # Clear cache
    clear_pycache()
    
    # Wait a moment
    time.sleep(1)
    
    # Restart server
    restart_server()
    
    print("\n⏳ Waiting for server to start...")
    time.sleep(5)
    
    print("✅ Server restart completed!")
    print("🔗 Server should be available at: http://localhost:5000")

if __name__ == "__main__":
    main()

