from flask import Blueprint

def init_sales_module(app):
    """Initialize the sales module"""
    from .routes import bp as sales_bp
    app.register_blueprint(sales_bp)
    
    print("Sales module initialized successfully")

