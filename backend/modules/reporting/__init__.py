"""
Reporting Module for EdonuOps
Handles report generation and management
"""

def init_reporting_module(app):
    """Initialize reporting module"""
    from .routes import reporting_bp
    app.register_blueprint(reporting_bp, url_prefix="/api/reporting")
    print("✅ Reporting module initialized")
