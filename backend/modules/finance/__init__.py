from flask import Blueprint
from flask_socketio import SocketIO

def init_finance_module(app, socketio=None):
    """Initialize finance module"""
    from . import models, routes, daily_cycle_models, daily_cycle_routes, daily_cycle_notifications, enhanced_daily_balance_routes, double_entry_routes, transaction_routes, accounting_period_routes, cost_center_routes
    
    # Register daily cycle blueprints
    app.register_blueprint(daily_cycle_routes.daily_cycle_bp)
    app.register_blueprint(daily_cycle_notifications.daily_cycle_notifications_bp)
    app.register_blueprint(enhanced_daily_balance_routes.enhanced_daily_balance_bp)
    
    # Register double-entry accounting blueprint
    app.register_blueprint(double_entry_routes.double_entry_bp)
    
    # Register transaction templates blueprint
    app.register_blueprint(transaction_routes.transaction_bp)
    
    # Register accounting periods blueprint
    app.register_blueprint(accounting_period_routes.accounting_period_bp)
    
    # Register cost center blueprint
    app.register_blueprint(cost_center_routes.cost_center_bp)
    
    print("✅ Finance module initialized with enhanced daily balance flow and notifications")
    print("✅ Double-entry accounting API loaded")
    print("✅ Transaction templates API loaded")
    print("✅ Accounting periods API loaded")
    print("✅ Cost center, department, and project management API loaded")