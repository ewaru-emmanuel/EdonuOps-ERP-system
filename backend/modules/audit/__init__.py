from . import routes

def init_audit_module(app):
    """Initialize the Audit Log System module"""
    
    # Blueprint is registered in main app
    print("✅ Audit Log System module initialized")
