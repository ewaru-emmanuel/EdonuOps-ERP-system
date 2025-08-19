"""
Analytics Module for EdonuOps
Handles reporting and analytics functionality
"""

def init_analytics_module(app):
    """Initialize analytics module"""
    from .dashboard import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    print("✅ Analytics module initialized")
