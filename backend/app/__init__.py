# backend/app/__init__.py

from flask import Flask, g, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import logging
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv('config.env')

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='development'):
    """Create and configure Flask application with enterprise features"""
    
    app = Flask(__name__)
    
    # Load configuration
    from config.settings import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    # Import environment configuration
    from config.environments import EnvironmentConfig
    
    # Configure CORS based on environment
    cors_origins = EnvironmentConfig.get_cors_origins()
    
    # Auto-detect Render environment and setup CORS
    if os.getenv('RENDER'):
        print("🚀 Render environment detected - setting up CORS for deployment")
        # Get Render URLs from environment variables
        render_frontend_url = os.getenv('RENDER_FRONTEND_URL')
        render_backend_url = os.getenv('RENDER_BACKEND_URL')
        
        if render_frontend_url:
            EnvironmentConfig.setup_render_cors(render_frontend_url, render_backend_url)
            cors_origins = EnvironmentConfig.get_cors_origins()
            print(f"✅ CORS configured for Render frontend: {render_frontend_url}")
        else:
            print("⚠️  RENDER_FRONTEND_URL not set - using default CORS origins")
    
    CORS(app, origins=cors_origins, supports_credentials=True, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Setup logging
    setup_logging(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    try:
        from modules.core.models import User, Role, Organization
        from modules.finance.models import Account, JournalEntry, JournalLine
        # Import advanced finance models
        from modules.finance.advanced_models import (
            ChartOfAccounts, GeneralLedgerEntry, AccountsPayable, AccountsReceivable,
            FixedAsset, Budget, TaxRecord, BankReconciliation, APPayment, ARPayment,
            FinanceVendor, FinanceCustomer, AuditTrail, FinancialReport, Currency, ExchangeRate,
            DepreciationSchedule, InvoiceLineItem, FinancialPeriod, JournalHeader, MaintenanceRecord,
            TaxFilingHistory, ComplianceReport, UserActivity, BankStatement, KPI, CompanySettings
        )
        from modules.inventory.models import Category, Product, Warehouse, BasicInventoryTransaction
        # Import advanced inventory models
        from modules.inventory.advanced_models import (
            InventoryProduct, ProductVariant, SerialNumber, LotBatch,
            AdvancedWarehouse, AdvancedLocation, Zone, Aisle,
            UnitOfMeasure, ProductCategory, InventorySupplier,
            InventoryTransaction
        )
        from modules.crm.models import Contact, Lead, Opportunity
        from modules.hcm.models import Employee, Department, Payroll, Recruitment
    except ImportError as e:
        print(f"Warning: Could not import some models: {e}")
    
    # Initialize enterprise services
    try:
        initialize_enterprise_services(app)
    except Exception as e:
        print(f"Warning: Could not initialize enterprise services: {e}")
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup middleware
    try:
        setup_middleware(app)
    except Exception as e:
        print(f"Warning: Could not setup middleware: {e}")
    
    # Initialize modules
    try:
        _initialize_modules(app)
    except Exception as e:
        print(f"Warning: Could not initialize modules: {e}")
    
    # Add root endpoint
    @app.route('/')
    def root():
        return jsonify({
            "message": "EdonuOps ERP Backend API",
            "status": "running",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "test": "/test",
                "api": "/api"
            },
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    # Add test endpoint
    @app.route('/test')
    def test():
        return jsonify({'message': 'Backend is running!', 'status': 'success'})
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }), 200
    
    return app

def setup_logging(app):
    """Setup application logging"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        handlers=[
            logging.FileHandler(app.config.get('LOG_FILE', 'logs/edonuops.log')),
            logging.StreamHandler()
        ]
    )

def initialize_enterprise_services(app):
    """Initialize enterprise services"""
    from services.cache_service import cache_service
    from modules.core.tenancy import tenant_manager, tenant_middleware
    from modules.security.enterprise_security import security_middleware
    from modules.workflow.workflow_engine import workflow_engine
    from modules.integration.integration_framework import integration_manager
    
    # Initialize cache service
    cache_service._connect()
    
    # Initialize tenant manager
    app.tenant_manager = tenant_manager
    
    # Initialize security middleware
    app.security_middleware = security_middleware
    
    # Initialize workflow engine
    app.workflow_engine = workflow_engine
    
    # Initialize integration manager
    app.integration_manager = integration_manager
    
    logger = logging.getLogger(__name__)
    logger.info("Enterprise services initialized successfully")

def setup_middleware(app):
    """Setup application middleware"""
    from modules.core.tenancy import tenant_middleware
    from modules.security.enterprise_security import security_middleware
    
    # Tenant middleware
    @app.before_request
    def before_request():
        # Apply tenant middleware
        tenant_middleware()()
        
        # Apply security middleware
        security_middleware.authenticate_request(request)
        
        # Add request ID for tracking
        if not hasattr(g, 'request_id'):
            g.request_id = request.headers.get('X-Request-ID', 'unknown')
    
    @app.after_request
    def after_request(response):
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Add request ID to response
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response

def register_blueprints(app):
    """Register Flask blueprints"""
    try:
        from modules.core.routes import core_bp
        app.register_blueprint(core_bp, url_prefix='/api/core')
    except ImportError as e:
        print(f"Warning: Could not import core blueprint: {e}")
    
    try:
        from modules.core.visitor_routes import visitor_bp
        app.register_blueprint(visitor_bp, url_prefix='/api')
        print("✓ Visitor Management API loaded")
    except ImportError as e:
        print(f"Warning: Could not import visitor blueprint: {e}")
    
    try:
        from modules.finance.advanced_routes import advanced_finance_bp
        app.register_blueprint(advanced_finance_bp, url_prefix='/api/finance')
        print("✓ Finance API loaded")
    except ImportError as e:
        print(f"Warning: Could not import finance blueprint: {e}")
    
    try:
        from modules.crm.routes import crm_bp
        app.register_blueprint(crm_bp, url_prefix='/api/crm')
    except ImportError as e:
        print(f"Warning: Could not import CRM blueprint: {e}")
    
    try:
        from modules.hcm.routes import hcm_bp
        app.register_blueprint(hcm_bp, url_prefix='/api/hcm')
    except ImportError as e:
        print(f"Warning: Could not import HCM blueprint: {e}")
    
    try:
        from modules.inventory.routes import inventory_bp
        app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    except ImportError as e:
        print(f"Warning: Could not import inventory blueprint: {e}")
    
    try:
        from modules.inventory.advanced_routes import advanced_inventory_bp
        app.register_blueprint(advanced_inventory_bp, url_prefix='/api/inventory/advanced')
    except ImportError as e:
        print(f"Warning: Could not import advanced inventory blueprint: {e}")
    
    try:
        from modules.onboarding.onboarding_routes import onboarding_bp
        app.register_blueprint(onboarding_bp, url_prefix='/api/onboarding')
        print("✓ Onboarding System API loaded")
    except ImportError as e:
        print(f"Warning: Could not import onboarding blueprint: {e}")
    
    # Register enterprise admin APIs
    try:
        from api.admin.cors_management import cors_admin_bp
        app.register_blueprint(cors_admin_bp, url_prefix='/api/admin')
        print("✓ CORS Management API loaded")
    except ImportError as e:
        print(f"Warning: Could not import CORS management blueprint: {e}")
    
    try:
        from modules.inventory.data_integrity_routes import data_integrity_bp
        app.register_blueprint(data_integrity_bp, url_prefix='/api/inventory/data-integrity')
    except ImportError as e:
        print(f"Warning: Could not import data integrity blueprint: {e}")
    
    try:
        from modules.inventory.inventory_taking import inventory_taking_bp
        app.register_blueprint(inventory_taking_bp, url_prefix='/api/inventory/taking')
    except ImportError as e:
        print(f"Warning: Could not import inventory taking blueprint: {e}")
    
    try:
        from modules.integration.cross_module_routes import cross_module_bp
        app.register_blueprint(cross_module_bp, url_prefix='/api/integration')
        print("✓ Cross-Module Integration API loaded")
    except ImportError as e:
        print(f"Warning: Could not import cross-module integration blueprint: {e}")
    
    # Load all new modules
    
    try:
        from modules.integration.auto_journal import auto_journal_engine
        print("✓ Automated Journal Entry Engine loaded")
    except ImportError as e:
        print(f"Warning: Could not import auto journal engine: {e}")
    
    try:
        from modules.integration.cogs_reconciliation import cogs_reconciliation
        print("✓ COGS Reconciliation System loaded")
    except ImportError as e:
        print(f"Warning: Could not import COGS reconciliation: {e}")
    
    try:
        from modules.inventory.adjustments import stock_adjustment
        print("✓ Stock Adjustment System loaded")
    except ImportError as e:
        print(f"Warning: Could not import stock adjustments: {e}")
    
    try:
        from modules.finance.aging_reports import aging_reports
        print("✓ Aging Reports System loaded")
    except ImportError as e:
        print(f"Warning: Could not import aging reports: {e}")
    
    try:
        from modules.finance.multi_currency import multi_currency
        print("✓ Multi-Currency Support loaded")
    except ImportError as e:
        print(f"Warning: Could not import multi-currency: {e}")
    
    try:
        from modules.workflows.approval_engine import approval_workflow
        print("✓ Approval Workflow Engine loaded")
    except ImportError as e:
        print(f"Warning: Could not import approval workflows: {e}")
    
    # Load Enterprise Hardening Systems
    try:
        from modules.inventory.enterprise_routes import enterprise_bp
        app.register_blueprint(enterprise_bp, url_prefix='/api/enterprise')
        print("✓ Enterprise Hardening Systems loaded")
    except ImportError as e:
        print(f"Warning: Could not import enterprise hardening systems: {e}")
    
    try:
        from modules.inventory.manager_dashboard_routes import manager_dashboard_bp
        app.register_blueprint(manager_dashboard_bp, url_prefix='/api/inventory/manager')
        print("✓ Manager Dashboard API loaded")
    except ImportError as e:
        print(f"Warning: Could not import manager dashboard routes: {e}")
    
    try:
        from modules.inventory.warehouse_operations_routes import warehouse_ops_bp
        app.register_blueprint(warehouse_ops_bp, url_prefix='/api/inventory/warehouse')
        print("✓ Warehouse Operations API loaded")
    except ImportError as e:
        print(f"Warning: Could not import warehouse operations routes: {e}")
    
    try:
        from modules.inventory.analytics_routes import analytics_bp
        app.register_blueprint(analytics_bp, url_prefix='/api/inventory/analytics')
        print("✓ Inventory Analytics API loaded")
    except ImportError as e:
        print(f"Warning: Could not import inventory analytics routes: {e}")
    

    
    try:
        from modules.inventory.core_routes import core_inventory_bp
        app.register_blueprint(core_inventory_bp, url_prefix='/api/inventory/core')
        print("✓ Core Inventory API loaded")
    except ImportError as e:
        print(f"Warning: Could not import core inventory routes: {e}")
    
    try:
        from modules.inventory.wms_routes import wms_bp
        app.register_blueprint(wms_bp, url_prefix='/api/inventory/wms')
        print("✓ WMS API loaded")
    except ImportError as e:
        print(f"Warning: Could not import WMS routes: {e}")
    
    try:
        from routes.performance_routes import performance_bp
        app.register_blueprint(performance_bp, url_prefix='/api/performance')
    except ImportError as e:
        print(f"Warning: Could not import performance blueprint: {e}")
    
    try:
        from routes.security_routes import security_bp
        app.register_blueprint(security_bp, url_prefix='/api/security')
    except ImportError as e:
        print(f"Warning: Could not import security blueprint: {e}")
    
    try:
        from modules.ecommerce.routes import ecommerce_bp
        app.register_blueprint(ecommerce_bp, url_prefix='/api/ecommerce')
    except ImportError as e:
        print(f"Warning: Could not import ecommerce blueprint: {e}")
    
    try:
        from modules.ai.routes import ai_bp
        app.register_blueprint(ai_bp, url_prefix='/api/ai')
    except ImportError as e:
        print(f"Warning: Could not import AI blueprint: {e}")
    
    try:
        from modules.procurement.routes import bp as procurement_bp
        app.register_blueprint(procurement_bp, url_prefix='/api/procurement')
        print("✓ Procurement API loaded")
    except ImportError as e:
        print(f"Warning: Could not import procurement blueprint: {e}")
    
    try:
        from modules.sustainability.routes import sustainability_bp
        app.register_blueprint(sustainability_bp, url_prefix='/api/sustainability')
    except ImportError as e:
        print(f"Warning: Could not import sustainability blueprint: {e}")
    
    try:
        from routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    except ImportError as e:
        print(f"Warning: Could not import dashboard blueprint: {e}")
    
    try:
        from routes.automation_routes import automation_bp
        app.register_blueprint(automation_bp, url_prefix='/api/automation')
    except ImportError as e:
        print(f"Warning: Could not import automation blueprint: {e}")
    
    # try:
    #     from routes.performance_routes import performance_bp
    #     app.register_blueprint(performance_bp, url_prefix='/api/performance')
    # except ImportError as e:
    #     print(f"Warning: Could not import performance blueprint: {e}")
    
    # try:
    #     from routes.enterprise_auth_routes import enterprise_auth_bp
    #     app.register_blueprint(enterprise_auth_bp, url_prefix='/api/enterprise')
    # except ImportError as e:
    #     print(f"Warning: Could not import enterprise auth blueprint: {e}")

def _initialize_modules(app):
    """Initialize all modules with enterprise features"""
    try:
        init_finance_module(app)
    except Exception as e:
        print(f"Warning: Could not initialize finance module: {e}")
    
    try:
        init_crm_module(app)
    except Exception as e:
        print(f"Warning: Could not initialize CRM module: {e}")
    
    try:
        init_hcm_module(app)
    except Exception as e:
        print(f"Warning: Could not initialize HCM module: {e}")
    
    try:
        init_inventory_module(app)
    except Exception as e:
        print(f"Warning: Could not initialize inventory module: {e}")
    
    try:
        init_ecommerce_module(app)
    except Exception as e:
        print(f"Warning: Could not initialize ecommerce module: {e}")
    
    try:
        init_ai_module(app)
    except Exception as e:
        print(f"Warning: Could not initialize AI module: {e}")
    
    try:
        init_sustainability_module(app)
    except Exception as e:
        print(f"Warning: Could not initialize sustainability module: {e}")

def init_finance_module(app):
    """Initialize finance module with enterprise features"""
    from modules.finance.models import Account, JournalEntry, Invoice, Payment
    from modules.workflow.workflow_engine import workflow_engine
    from modules.workflow.workflow_engine import create_invoice_approval_workflow
    
    # Register finance workflows
    workflow_engine.register_workflow(create_invoice_approval_workflow())
    
    logger = logging.getLogger(__name__)
    logger.info("Finance module initialized with enterprise features")

def init_crm_module(app):
    """Initialize CRM module with enterprise features"""
    from modules.crm.models import Contact, Lead, Opportunity, Customer
    from modules.integration.integration_framework import integration_manager
    
    # Register CRM integrations
    # This would connect to Salesforce, HubSpot, etc.
    
    logger = logging.getLogger(__name__)
    logger.info("CRM module initialized with enterprise features")

def init_hcm_module(app):
    """Initialize HCM module with enterprise features"""
    # Models are already imported above
    
    logger = logging.getLogger(__name__)
    logger.info("HCM module initialized with enterprise features")

def init_inventory_module(app):
    """Initialize inventory module with enterprise features"""
    from modules.inventory.models import Product, Category, Warehouse, StockMovement
    
    logger = logging.getLogger(__name__)
    logger.info("Inventory module initialized with enterprise features")

def init_ecommerce_module(app):
    """Initialize ecommerce module with enterprise features"""
    from modules.ecommerce.models import EcommerceProduct, EcommerceOrder, EcommerceCustomer
    from modules.integration.integration_framework import integration_manager
    
    # Register ecommerce integrations
    # This would connect to Shopify, WooCommerce, etc.
    
    logger = logging.getLogger(__name__)
    logger.info("Ecommerce module initialized with enterprise features")

def init_ai_module(app):
    """Initialize AI module with enterprise features"""
    from modules.ai.models import AIPrediction, AIInsight, AIRecommendation
    
    logger = logging.getLogger(__name__)
    logger.info("AI module initialized with enterprise features")

def init_sustainability_module(app):
    """Initialize sustainability module with enterprise features"""
    from modules.sustainability.models import EnvironmentalMetric, SocialMetric, GovernanceMetric, ESGReport
    
    logger = logging.getLogger(__name__)
    logger.info("Sustainability module initialized with enterprise features")

# Error handlers
def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden'}, 403

# Create the application instance
app = create_app()

# Register error handlers
register_error_handlers(app)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)