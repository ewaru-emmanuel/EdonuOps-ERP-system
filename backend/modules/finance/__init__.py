from flask import Blueprint
from flask_socketio import SocketIO

def init_finance_module(app, socketio=None):
    """Initialize finance module"""
    from . import models, routes, daily_cycle_models, daily_cycle_routes, daily_cycle_notifications, enhanced_daily_balance_routes
    
    # Register daily cycle blueprints
    app.register_blueprint(daily_cycle_routes.daily_cycle_bp)
    app.register_blueprint(daily_cycle_notifications.daily_cycle_notifications_bp)
    app.register_blueprint(enhanced_daily_balance_routes.enhanced_daily_balance_bp)
    
    print("✅ Finance module initialized with enhanced daily balance flow and notifications")