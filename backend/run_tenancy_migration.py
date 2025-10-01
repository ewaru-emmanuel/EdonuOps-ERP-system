#!/usr/bin/env python3
"""
Run Multi-Tenancy Migration
Executes the complete migration process
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the multi-tenancy migration"""
    print("🚀 Starting Multi-Tenancy Migration...")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Import and run the migration
        from migrations.add_multi_tenancy_support import main as run_migration
        run_migration()
        
        print("\n" + "=" * 60)
        print("🎉 Multi-Tenancy Migration Completed Successfully!")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        print("\n📋 Migration Summary:")
        print("✅ Created tenant tables (tenants, user_tenants, tenant_modules, tenant_settings)")
        print("✅ Added tenant_id to all existing tables")
        print("✅ Created performance indexes")
        print("✅ Created default tenant for existing data")
        print("✅ Migrated all existing data to default tenant")
        print("✅ Activated all modules for default tenant")
        
        print("\n📝 Next Steps:")
        print("1. 🔧 Update your authentication system to include tenant context")
        print("2. 🛡️  Add tenant filtering to all API endpoints")
        print("3. 🎨 Update frontend components to be tenant-aware")
        print("4. 🧪 Test tenant isolation thoroughly")
        print("5. 📊 Monitor performance with tenant indexes")
        
        print("\n🔍 Verification Commands:")
        print("   - Check tenant tables: SELECT * FROM tenants;")
        print("   - Check tenant_id columns: PRAGMA table_info(advanced_general_ledger_entries);")
        print("   - Check indexes: .indexes")
        print("   - Check migrated data: SELECT COUNT(*) FROM advanced_general_ledger_entries WHERE tenant_id = 'default_tenant';")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("🔧 Troubleshooting:")
        print("   1. Check database connection")
        print("   2. Ensure all dependencies are installed")
        print("   3. Check for any existing tenant_id columns")
        print("   4. Review error logs for specific issues")
        sys.exit(1)

if __name__ == '__main__':
    main()












