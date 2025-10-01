#!/usr/bin/env python3
"""
Fix Module Activation
Activate modules for the default tenant
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def main():
    """Fix module activation for default tenant"""
    print("🔧 Fixing Module Activation...")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        try:
            modules = [
                'finance', 'inventory', 'sales', 'purchasing', 
                'manufacturing', 'crm', 'hr', 'reporting', 'analytics'
            ]
            
            for module_name in modules:
                try:
                    # Insert module directly without checking
                    db.session.execute(text("""
                        INSERT OR IGNORE INTO tenant_modules (tenant_id, module_name, enabled, activated_at, configuration)
                        VALUES ('default_tenant', ?, 1, CURRENT_TIMESTAMP, '{}')
                    """), (module_name,))
                    print(f"✅ Activated module: {module_name}")
                except Exception as e:
                    print(f"❌ Error activating module {module_name}: {e}")
            
            db.session.commit()
            
            # Verify activation
            result = db.session.execute(text("SELECT COUNT(*) FROM tenant_modules WHERE tenant_id = 'default_tenant' AND enabled = 1"))
            active_modules = result.scalar()
            print(f"\n✅ Total active modules: {active_modules}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    main()












