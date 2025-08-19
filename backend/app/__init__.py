# backend/app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load environment variables from config file
    from dotenv import load_dotenv
    load_dotenv('config.env')
    
    # Configuration
    if config_name == 'production':
        app.config.from_object('config.settings.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('config.settings.TestingConfig')
    else:
        app.config.from_object('config.settings.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Configure logging
    _configure_logging(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Initialize modules
    _initialize_modules(app)
    
    return app

def _configure_logging(app):
    """Configure application logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/edonuops.log', maxBytes=10240000, backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('EdonuOps startup')

def _register_blueprints(app):
    """Register all application blueprints"""
    # Import core models first to ensure User model is available
    from modules.core import models as core_models
    
    # Core modules - only register the ones that exist
    from modules.core.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    try:
        from modules.core.routes import bp as core_bp
        app.register_blueprint(core_bp, url_prefix="/api")
        print("✅ Core blueprint registered")
    except ImportError:
        print("⚠️ Core module not available")
    
    # Register only the modules we have
    try:
        from modules.finance.routes import bp as finance_bp
        app.register_blueprint(finance_bp, url_prefix="/api/finance")
        print("✅ Finance blueprint registered")
    except ImportError:
        print("⚠️ Finance module not available")
    
    try:
        from modules.crm.routes import bp as crm_bp
        app.register_blueprint(crm_bp, url_prefix="/api/crm")
        print("✅ CRM blueprint registered")
    except ImportError:
        print("⚠️ CRM module not available")
    
    try:
        from modules.inventory.routes import bp as inventory_bp
        app.register_blueprint(inventory_bp, url_prefix="/api/inventory")
        print("✅ Inventory blueprint registered")
    except ImportError:
        print("⚠️ Inventory module not available")
    
    try:
        from modules.hr.routes import bp as hr_bp
        app.register_blueprint(hr_bp, url_prefix="/api/hr")
        print("✅ HR blueprint registered")
    except ImportError:
        print("⚠️ HR module not available")
    
    try:
        from modules.ecommerce.routes import ecommerce_bp
        app.register_blueprint(ecommerce_bp, url_prefix="/api/ecommerce")
        print("✅ E-commerce blueprint registered")
    except ImportError:
        print("⚠️ E-commerce module not available")
    
    try:
        from modules.ai.routes import ai_bp
        app.register_blueprint(ai_bp, url_prefix="/api/ai")
        print("✅ AI blueprint registered")
    except ImportError:
        print("⚠️ AI module not available")
    
    try:
        from modules.sustainability.routes import sustainability_bp
        app.register_blueprint(sustainability_bp, url_prefix="/api/sustainability")
        print("✅ Sustainability blueprint registered")
    except ImportError:
        print("⚠️ Sustainability module not available")

def _initialize_modules(app):
    """Initialize all modules with their dependencies"""
    try:
        # Initialize only the modules we have
        try:
            from modules.finance import init_finance_module
            init_finance_module(app, socketio)
            print("✅ Finance module initialized")
        except ImportError:
            print("⚠️ Finance module initialization not available")
        
        try:
            from modules.crm import init_crm_module
            init_crm_module(app)
            print("✅ CRM module initialized")
        except ImportError:
            print("⚠️ CRM module initialization not available")
        
        try:
            from modules.inventory import init_inventory_module
            init_inventory_module(app)
            print("✅ Inventory module initialized")
        except ImportError:
            print("⚠️ Inventory module initialization not available")
        
        try:
            from modules.hr import init_hr_module
            init_hr_module(app)
            print("✅ HR module initialized")
        except ImportError:
            print("⚠️ HR module initialization not available")
        
        try:
            from modules.ecommerce import init_ecommerce_module
            init_ecommerce_module(app)
            print("✅ E-commerce module initialized")
        except ImportError:
            print("⚠️ E-commerce module initialization not available")
        
        try:
            from modules.ai import init_ai_module
            init_ai_module(app)
            print("✅ AI module initialized")
        except ImportError:
            print("⚠️ AI module initialization not available")
        
        try:
            from modules.sustainability import init_sustainability_module
            init_sustainability_module(app)
            print("✅ Sustainability module initialized")
        except ImportError:
            print("⚠️ Sustainability module initialization not available")
        
        print("✅ Core modules initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing modules: {e}")
        import traceback
        traceback.print_exc()

# Create tables
def create_tables():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)