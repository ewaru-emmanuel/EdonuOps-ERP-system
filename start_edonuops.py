#!/usr/bin/env python3
"""
EdonuOps Startup Script
This script starts both the backend and frontend servers
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class EdonuOpsStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def setup_environment(self):
        """Setup the environment for EdonuOps"""
        print("🚀 Setting up EdonuOps environment...")
        
        # Check if we're in the right directory
        if not os.path.exists('backend') or not os.path.exists('frontend'):
            print("❌ Error: Please run this script from the EdonuOps root directory")
            sys.exit(1)
        
        # Change to backend directory and install dependencies
        print("📦 Installing backend dependencies...")
        os.chdir('backend')
        
        # Check if virtual environment exists
        if not os.path.exists('venv'):
            print("🔧 Creating Python virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Activate virtual environment and install requirements
        if os.name == 'nt':  # Windows
            pip_path = os.path.join('venv', 'Scripts', 'pip')
        else:  # Unix/Linux/Mac
            pip_path = os.path.join('venv', 'bin', 'pip')
        
        print("📦 Installing Python dependencies...")
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        
        # Initialize database
        print("🗄️  Initializing database...")
        python_path = os.path.join('venv', 'Scripts', 'python') if os.name == 'nt' else os.path.join('venv', 'bin', 'python')
        subprocess.run([python_path, 'init_database.py'], check=True)
        
        os.chdir('..')
        
        # Change to frontend directory and install dependencies
        print("📦 Installing frontend dependencies...")
        os.chdir('frontend')
        
        if not os.path.exists('node_modules'):
            print("📦 Installing Node.js dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        os.chdir('..')
        
        print("✅ Environment setup completed!")
    
    def start_backend(self):
        """Start the backend server"""
        print("🔧 Starting backend server...")
        os.chdir('backend')
        
        # Activate virtual environment and start server
        if os.name == 'nt':  # Windows
            python_path = os.path.join('venv', 'Scripts', 'python')
        else:  # Unix/Linux/Mac
            python_path = os.path.join('venv', 'bin', 'python')
        
        self.backend_process = subprocess.Popen(
            [python_path, 'run.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        os.chdir('..')

        # Wait a moment for backend to start
        time.sleep(3)
        
        if self.backend_process.poll() is None:
            print("✅ Backend server started successfully!")
        else:
            print("❌ Backend server failed to start")
            return False
        
        return True
    
    def start_frontend(self):
        """Start the frontend server"""
        print("🎨 Starting frontend server...")
        os.chdir('frontend')
        
        self.frontend_process = subprocess.Popen(
            ['npm', 'start'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        os.chdir('..')
        
        # Wait a moment for frontend to start
        time.sleep(5)
        
        if self.frontend_process.poll() is None:
            print("✅ Frontend server started successfully!")
        else:
            print("❌ Frontend server failed to start")
            return False
        
        return True
    
    def monitor_processes(self):
        """Monitor the running processes"""
        while self.running:
            # Check backend
            if self.backend_process and self.backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly")
                self.running = False
                break
            
            # Check frontend
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                self.running = False
                break
            
            time.sleep(5)
    
    def stop_servers(self):
        """Stop both servers"""
        print("\n🛑 Stopping servers...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ Backend server stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("✅ Frontend server stopped")
    
    def run(self):
        """Main run method"""
        try:
            # Setup environment
            self.setup_environment()
            
            # Start backend
            if not self.start_backend():
                return
            
            # Start frontend
            if not self.start_frontend():
                return
            
            print("\n🎉 EdonuOps is now running!")
            print("📱 Frontend: http://localhost:3000")
            print("🔧 Backend: http://localhost:5000")
            print("🏥 Health Check: http://localhost:5000/health")
            print("\nPress Ctrl+C to stop the servers")
            
            # Monitor processes
            self.monitor_processes()
            
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.stop_servers()

def main():
    """Main function"""
    print("🚀 EdonuOps Enterprise ERP System")
    print("=" * 50)
    
    starter = EdonuOpsStarter()
    starter.run()

if __name__ == "__main__":
    main()
