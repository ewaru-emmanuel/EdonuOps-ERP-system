#!/usr/bin/env python3
"""
Test script to check if all backend imports work correctly
"""

def test_imports():
    try:
        print("Testing backend imports...")
        
        # Test core modules
        print("✓ Testing core modules...")
        from modules.core.auth import auth_bp
        from modules.core.organization import org_bp
        print("  ✓ Core modules imported successfully")
        
        # Test business modules
        print("✓ Testing business modules...")
        from modules.finance import init_finance_module
        from modules.crm import init_crm_module
        from modules.procurement import init_procurement_module
        from modules.inventory import init_inventory_module
        from modules.tax import init_tax_module
        from modules.workflow import init_workflow_module
        from modules.customization import init_customization_module
        from modules.dashboard import init_dashboard_module
        from modules.audit import init_audit_module
        from modules.ai import init_ai_module
        print("  ✓ Business modules imported successfully")
        
        # Test app creation
        print("✓ Testing app creation...")
        from app import create_app
        app = create_app()
        print("  ✓ App created successfully")
        
        print("\n🎉 All imports successful! Backend is ready to run.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports()


