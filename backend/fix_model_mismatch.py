#!/usr/bin/env python3
"""
Fix Model Mismatch
Temporarily removes product_id from model, restarts server, then adds it back
"""

import os
import shutil
import time

def backup_model_file():
    """Backup the original model file"""
    try:
        shutil.copy2('modules/inventory/advanced_models.py', 'modules/inventory/advanced_models_backup.py')
        print("✅ Model file backed up")
        return True
    except Exception as e:
        print(f"❌ Failed to backup model file: {e}")
        return False

def remove_product_id_from_model():
    """Temporarily remove product_id field from model"""
    try:
        with open('modules/inventory/advanced_models.py', 'r') as f:
            content = f.read()
        
        # Remove the product_id line
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        
        for line in lines:
            if 'product_id = db.Column(db.String(50), unique=True, nullable=True)' in line:
                print("🗑️ Removing product_id field from model")
                skip_next = True
                continue
            if skip_next and line.strip() == '':
                skip_next = False
                continue
            new_lines.append(line)
        
        with open('modules/inventory/advanced_models.py', 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Removed product_id field from model")
        return True
    except Exception as e:
        print(f"❌ Failed to remove product_id: {e}")
        return False

def restore_product_id_to_model():
    """Restore product_id field to model"""
    try:
        with open('modules/inventory/advanced_models.py', 'r') as f:
            content = f.read()
        
        # Find the sku line and add product_id after it
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            if 'sku = db.Column(db.String(50), unique=True, nullable=True)' in line:
                # Add product_id field after sku
                new_lines.append('    product_id = db.Column(db.String(50), unique=True, nullable=True)  # Added product_id field')
                print("✅ Restored product_id field to model")
        
        with open('modules/inventory/advanced_models.py', 'w') as f:
            f.write('\n'.join(new_lines))
        
        return True
    except Exception as e:
        print(f"❌ Failed to restore product_id: {e}")
        return False

def restart_server():
    """Restart the Flask server"""
    try:
        import subprocess
        import signal
        
        # Kill existing Python processes
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, check=False)
        
        time.sleep(2)
        
        # Start server in background
        subprocess.Popen(['python', 'run.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        print("✅ Server restarted")
        return True
    except Exception as e:
        print(f"❌ Failed to restart server: {e}")
        return False

def test_endpoint():
    """Test the products endpoint"""
    try:
        import urllib.request
        import json
        
        time.sleep(5)  # Wait for server to start
        
        req = urllib.request.Request('http://localhost:5000/api/inventory/advanced/products')
        response = urllib.request.urlopen(req)
        products = json.loads(response.read())
        print(f"✅ Products endpoint works! Found {len(products)} products")
        return True
    except Exception as e:
        print(f"❌ Products endpoint failed: {e}")
        return False

def main():
    """Main function to fix model mismatch"""
    print("🔧 Fixing Model Mismatch")
    print("=" * 40)
    
    # Step 1: Backup model file
    if not backup_model_file():
        return
    
    # Step 2: Remove product_id from model
    if not remove_product_id_from_model():
        return
    
    # Step 3: Restart server
    if not restart_server():
        return
    
    # Step 4: Test endpoint
    if not test_endpoint():
        print("❌ Endpoint still failing")
        return
    
    # Step 5: Restore product_id to model
    if not restore_product_id_to_model():
        return
    
    # Step 6: Restart server again
    if not restart_server():
        return
    
    # Step 7: Test endpoint again
    if not test_endpoint():
        print("❌ Endpoint failing after restore")
        return
    
    print("\n🎉 Model mismatch fixed successfully!")
    print("✅ All endpoints should now work with product_id support")

if __name__ == "__main__":
    main()

