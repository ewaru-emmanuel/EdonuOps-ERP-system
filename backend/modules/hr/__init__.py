"""
HR Module for EdonuOps
Handles Human Capital Management functionality
"""

def init_hr_module(app):
    """Initialize HR module"""
    from .routes import bp as hr_bp
    app.register_blueprint(hr_bp, url_prefix="/api/hr")
    print("✅ HR module initialized")
