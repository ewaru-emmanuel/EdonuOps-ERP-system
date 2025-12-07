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
        render_frontend_url = os.getenv('RENDER_FRONTEND_URL')
        render_backend_url = os.getenv('RENDER_BACKEND_URL')
        if render_frontend_url:
            EnvironmentConfig.setup_render_cors(render_frontend_url, render_backend_url)
            cors_origins = EnvironmentConfig.get_cors_origins()
    
    # Configure CORS
    CORS(
        app,
        resources={r"/api/.*": {"origins": cors_origins}},
        supports_credentials=True,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'X-Request-ID', 'X-Tenant-ID', 'X-User-ID'],
        expose_headers=['Content-Type', 'Authorization', 'X-Request-ID'],
        max_age=3600
    )
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.WARNING)
    
    # Import all models to ensure they're registered
    try:
        from modules.core.models import User, Role, Organization, SystemSetting, UserData
        from modules.core.tenant_models import Tenant, UserTenant, TenantModule, TenantSettings
        from modules.core.user_preferences_models import UserPreferences
        from modules.core.security_models import PasswordHistory, UserSession, AccountLockout, TwoFactorAuth, SecurityEvent
        from modules.core.audit_models import AuditLog
        from modules.dashboard.models import UserModules, DashboardWidget, DashboardTemplate, WidgetTemplate
        from modules.finance.models import Account, JournalEntry, JournalLine, Payment, Budget, Invoice
        from modules.finance.cost_center_models import Department, CostCenter, Project
        from modules.finance.currency_models import Currency, ExchangeRate, CurrencyConversion
        from modules.finance.advanced_models import ChartOfAccounts, GeneralLedgerEntry, JournalHeader, CompanySettings, BankReconciliation, FinancialPeriod, TaxRecord, InvoiceLineItem, FixedAsset, BudgetEntry, AccountsPayable, AccountsReceivable, DepreciationSchedule, MaintenanceRecord, APPayment, ARPayment, BankTransaction, BankStatement, FinancialReport, KPI
        from modules.finance.payment_models import PaymentMethod, BankAccount, PaymentTransaction, PartialPayment, ReconciliationSession, AccountingPeriod
        from modules.inventory.models import Product, InventoryProduct, InventoryTransaction, StockMovement, InventoryLevel, InventoryUOM, InventoryUOMConversion, ProductCategory, Warehouse, InventoryLocation, InventoryZone, InventoryAisle, InventoryRack, InventoryLotBatch, InventorySerialNumber, InventoryValuationSnapshot, InventoryAdjustmentEntry, InventoryCostLayer, CostLayerTransaction, InventoryWarehouseActivity, InventoryStockLevel, InventoryAdvancedLocation, InventoryAdvancedWarehouse, InventoryProductVariant, InventoryPickerPerformance, DailyInventoryBalance, DailyInventoryTransactionSummary, BasicInventoryTransaction, InventoryBasicLocation, InventorySimpleWarehouse, InventoryProductCategories, InventorySuppliers, InventoryCustomers, InventoryAuditTrail, InventoryReports, DailyInventoryCycleStatus, DailyInventoryCycleAuditLogs, InventorySystemConfig
        from modules.crm.models import Contact, Lead, Opportunity, Communication, FollowUp, Ticket, TimeEntry, BehavioralEvent, LeadIntake, KnowledgeBaseArticle, KnowledgeBaseAttachment, Pipeline
        from modules.procurement.models import Vendor, RFQ, RFQItem, RFQInvitation, RFQResponse, RFQResponseItem, PurchaseOrder, PurchaseOrderItem, POAttachment, Contract, ContractDocument, VendorDocument, VendorCommunication
        from modules.workflow.models import WorkflowRule, WorkflowTemplate, WorkflowExecution, WorkflowAction
        from modules.analytics.models import PlatformMetric
        from modules.permissions.models import Permission, RolePermission, PermissionChange
        from modules.security.models import SecurityPolicy, SystemEvent, LoginHistory
        from modules.tenant.models import TenantUsageStat
    except Exception as e:
        pass  # Silently handle import errors in production
    
    # Initialize enterprise services
    try:
        from services.enterprise_service import EnterpriseService
        EnterpriseService.initialize()
    except Exception as e:
        pass  # Silently handle initialization errors in production
    
    # Setup middleware
    try:
        from middleware.request_logging import RequestLoggingMiddleware
        from middleware.tenant_middleware import TenantMiddleware
        from middleware.security_middleware import SecurityMiddleware
        
        app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)
        app.wsgi_app = TenantMiddleware(app.wsgi_app)
        app.wsgi_app = SecurityMiddleware(app.wsgi_app)
    except Exception as e:
        pass  # Silently handle middleware errors in production
    
    # Initialize modules
    try:
        from modules.core.daily_cycle import DailyCycleManager
        DailyCycleManager.initialize()
    except Exception as e:
        pass  # Silently handle module initialization errors in production
    
    # Sync database schema on startup (adds missing columns automatically)
    try:
        with app.app_context():
            from modules.database.schema_sync import sync_all_models
            sync_all_models()
    except Exception as e:
        # Log but don't crash - schema sync is non-critical
        import logging
        logging.getLogger(__name__).warning(f"Database schema sync warning: {e}")
    
    # SECURITY: Seed permissions on startup (ensures all permissions exist)
    try:
        with app.app_context():
            from modules.core.permission_seeder import seed_all_permissions
            result = seed_all_permissions()
            if result['created'] > 0:
                logging.getLogger(__name__).info(f"✅ Seeded {result['created']} new permissions on startup")
                print(f"✅ Seeded {result['created']} new permissions on startup")
            elif result['errors']:
                logging.getLogger(__name__).warning(f"⚠️  Permission seeding encountered {len(result['errors'])} errors")
    except Exception as e:
        # Log but don't crash - permission seeding is non-critical for startup
        import logging
        logging.getLogger(__name__).warning(f"Permission seeding warning: {e}")
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Setup request context
    setup_request_context(app)
    
    # Setup global route protection
    try:
        from middleware.route_protection import require_authentication
        require_authentication(app)
        print("✅ Global route protection enabled - all routes require authentication")
    except Exception as e:
        print(f"⚠️  Warning: Could not setup route protection: {e}")
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })

    # Test endpoint for basic connectivity
    @app.route('/test')
    def test_endpoint():
        """Test endpoint for basic connectivity"""
        return jsonify({
            'message': 'EdonuOps API is running',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    
    # Enhanced authentication with security features (includes login, register, verify-token, etc.)
    try:
        from modules.core.auth_enhanced import auth_enhanced_bp
        app.register_blueprint(auth_enhanced_bp, url_prefix='/api/auth')
        print("✅ Registered auth_enhanced_bp with prefix /api/auth")
    except Exception as e:
        print(f"⚠️  Warning: Could not register auth_enhanced_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Note: auth.py is incomplete (references undefined auth_bp) - using auth_enhanced.py instead
    # try:
    #     from modules.core.auth import auth_bp
    #     app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # except Exception as e:
    #     pass
    
    # Invite management system
    try:
        from modules.core.invite_management import invite_management_bp
        app.register_blueprint(invite_management_bp, url_prefix='/api/invites')
    except Exception as e:
        pass
    
    # Comprehensive onboarding system
    try:
        from modules.core.onboarding_api import onboarding_bp
        app.register_blueprint(onboarding_bp, url_prefix='/api/onboarding')
    except Exception as e:
        pass
    
    try:
        from modules.core.permissions_routes import permissions_bp
        app.register_blueprint(permissions_bp, url_prefix='/api/core/permissions')
    except Exception as e:
        pass
    
    try:
        from modules.core.user_management_routes import user_management_bp
        app.register_blueprint(user_management_bp, url_prefix='/api/admin')
    except Exception as e:
        pass
    
    try:
        from modules.core.audit_routes import audit_bp
        app.register_blueprint(audit_bp, url_prefix='/api/audit')
    except Exception as e:
        pass
    
    # Register core security routes (policies, 2fa, events) - This is the main one
    try:
        from modules.core.security_routes import security_bp
        app.register_blueprint(security_bp, url_prefix='/api/security')
        print(f"✅ Registered security_bp with prefix /api/security")
    except Exception as e:
        print(f"⚠️  Failed to register core security routes: {e}")
        import traceback
        traceback.print_exc()
    
    # Also register enterprise security routes if available (different endpoints)
    try:
        from modules.security.routes import bp as enterprise_security_bp
        app.register_blueprint(enterprise_security_bp)  # Already has /api/security prefix
        print(f"✅ Registered enterprise_security_bp")
    except Exception as e:
        pass  # Optional
    
    # Tenant management
    try:
        from modules.tenant.tenant_routes import tenant_management_bp
        app.register_blueprint(tenant_management_bp)
    except Exception as e:
        pass
    
    try:
        from modules.tenant.tenant_creation_routes import tenant_creation_bp
        app.register_blueprint(tenant_creation_bp)
    except Exception as e:
        pass
    
    try:
        from modules.core.user_preferences_routes import user_preferences_bp
        app.register_blueprint(user_preferences_bp)
    except Exception as e:
        pass
    
    # Enterprise features
    try:
        from modules.tenant.tenant_analytics_routes import tenant_analytics_bp
        app.register_blueprint(tenant_analytics_bp)
    except Exception as e:
        pass
    
    try:
        from modules.tenant.subscription_routes import subscription_bp
        app.register_blueprint(subscription_bp)
    except Exception as e:
        pass
    
    try:
        from modules.core.rate_limiting import rate_limiting_bp
        app.register_blueprint(rate_limiting_bp)
    except Exception as e:
        pass
    
    # Core modules
    try:
        from modules.core.routes import core_bp
        app.register_blueprint(core_bp, url_prefix='/api/core')
    except Exception as e:
        pass
    
    try:
        from modules.core.visitor_routes import visitor_bp
        app.register_blueprint(visitor_bp, url_prefix='/api')
    except Exception as e:
        pass
    
    # Finance module
    try:
        from modules.finance.routes import finance_bp
        app.register_blueprint(finance_bp, url_prefix='/api/finance')
    except Exception as e:
        pass
    
    try:
        from modules.finance.currency_routes import currency_bp
        app.register_blueprint(currency_bp, url_prefix='/api/finance')
    except Exception as e:
        pass
    
    try:
        from modules.finance.payment_routes import payment_bp
        app.register_blueprint(payment_bp)
    except Exception as e:
        pass
    
    try:
        from modules.finance.advanced_payment_routes import advanced_payment_bp
        app.register_blueprint(advanced_payment_bp)
    except Exception as e:
        pass
    
    try:
        from modules.finance.bank_reconciliation_routes import bank_reconciliation_bp
        app.register_blueprint(bank_reconciliation_bp)
    except Exception as e:
        pass
    
    try:
        from modules.finance.bank_feed_routes import bank_feed_bp
        app.register_blueprint(bank_feed_bp)
    except Exception as e:
        pass
    
    try:
        from modules.finance.analytics_routes import analytics_bp
        app.register_blueprint(analytics_bp)
    except Exception as e:
        pass
    
    try:
        from modules.finance.double_entry_routes import double_entry_bp
        app.register_blueprint(double_entry_bp)
        # Count routes after registration (blueprint doesn't have url_map before registration)
        route_count = len([r for r in app.url_map.iter_rules() if r.endpoint.startswith('double_entry.')])
        print(f"✅ Registered double_entry_bp with {route_count} routes")
    except Exception as e:
        print(f"❌ Error registering double_entry_bp: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from modules.finance.advanced_routes import advanced_finance_bp
        app.register_blueprint(advanced_finance_bp, url_prefix='/api/finance/advanced')
        print(f"✅ Registered advanced_finance_bp with prefix /api/finance/advanced")
    except Exception as e:
        print(f"❌ Error registering advanced_finance_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Inventory-Finance integration
    try:
        from modules.inventory.daily_cycle_routes import inventory_daily_cycle_bp
        app.register_blueprint(inventory_daily_cycle_bp)
    except Exception as e:
        pass
    
    try:
        from modules.inventory.inventory_finance_integration_routes import inventory_finance_integration_bp
        app.register_blueprint(inventory_finance_integration_bp)
    except Exception as e:
        pass
    
    try:
        from modules.inventory.variance_reports_routes import variance_reports_bp
        app.register_blueprint(variance_reports_bp)
    except Exception as e:
        pass
    
    try:
        from modules.inventory.finance_inventory_validation_routes import finance_inventory_validation_bp
        app.register_blueprint(finance_inventory_validation_bp)
    except Exception as e:
        pass
    
    # Finance advanced features
    try:
        from modules.finance.statutory_routes import statutory_bp
        app.register_blueprint(statutory_bp, url_prefix='/api/finance/statutory')
    except Exception as e:
        pass
    
    try:
        from modules.finance.tagging_routes import tagging_bp
        app.register_blueprint(tagging_bp, url_prefix='/api/finance/tagging')
    except Exception as e:
        pass
    
    try:
        from modules.finance.localization_routes import localization_bp
        app.register_blueprint(localization_bp, url_prefix='/api/finance/localization')
    except Exception as e:
        pass
    
    # CRM module
    try:
        from modules.crm.routes import crm_bp
        app.register_blueprint(crm_bp, url_prefix='/api/crm')
    except Exception as e:
        pass
    
    # Inventory module
    try:
        from modules.inventory.routes import inventory_bp
        app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.advanced_routes import advanced_inventory_bp
        app.register_blueprint(advanced_inventory_bp, url_prefix='/api/inventory/advanced')
    except Exception as e:
        pass
    
    # Onboarding system
    try:
        from modules.onboarding.onboarding_routes import onboarding_bp
        app.register_blueprint(onboarding_bp, url_prefix='/api/onboarding')
    except Exception as e:
        pass
    
    # Admin features
    try:
        from modules.core.cors_admin_routes import cors_admin_bp
        app.register_blueprint(cors_admin_bp, url_prefix='/api/admin')
    except Exception as e:
        pass
    
    # Inventory advanced features
    try:
        from modules.inventory.data_integrity_routes import data_integrity_bp
        app.register_blueprint(data_integrity_bp, url_prefix='/api/inventory/data-integrity')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.inventory_taking_routes import inventory_taking_bp
        app.register_blueprint(inventory_taking_bp, url_prefix='/api/inventory/taking')
    except Exception as e:
        pass
    
    # Cross-module integration
    try:
        from modules.integration.cross_module_routes import cross_module_bp
        app.register_blueprint(cross_module_bp, url_prefix='/api/integration')
    except Exception as e:
        pass
    
    # Automated systems
    try:
        from modules.finance.auto_journal_engine import auto_journal_bp
        app.register_blueprint(auto_journal_bp, url_prefix='/api/finance/auto-journal')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.cogs_reconciliation_routes import cogs_reconciliation_bp
        app.register_blueprint(cogs_reconciliation_bp, url_prefix='/api/inventory/cogs')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.stock_adjustment_routes import stock_adjustment_bp
        app.register_blueprint(stock_adjustment_bp, url_prefix='/api/inventory/adjustments')
    except Exception as e:
        pass
    
    try:
        from modules.finance.aging_reports_routes import aging_reports_bp
        app.register_blueprint(aging_reports_bp, url_prefix='/api/finance/aging')
    except Exception as e:
        pass
    
    try:
        from modules.finance.multi_currency_routes import multi_currency_bp
        app.register_blueprint(multi_currency_bp, url_prefix='/api/finance/multi-currency')
    except Exception as e:
        pass
    
    try:
        from modules.workflow.approval_workflow_routes import approval_workflow_bp
        app.register_blueprint(approval_workflow_bp, url_prefix='/api/workflow/approval')
    except Exception as e:
        pass
    
    # Enterprise hardening
    try:
        from modules.enterprise.enterprise_routes import enterprise_bp
        app.register_blueprint(enterprise_bp, url_prefix='/api/enterprise')
    except Exception as e:
        pass
    
    # Inventory management
    try:
        from modules.inventory.manager_dashboard_routes import manager_dashboard_bp
        app.register_blueprint(manager_dashboard_bp, url_prefix='/api/inventory/manager')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.analytics_routes import analytics_bp
        app.register_blueprint(analytics_bp, url_prefix='/api/inventory/analytics')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.warehouse_routes import warehouse_bp
        app.register_blueprint(warehouse_bp, url_prefix='/api/inventory/warehouse')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.core_routes import core_inventory_bp
        app.register_blueprint(core_inventory_bp, url_prefix='/api/inventory/core')
    except Exception as e:
        pass
    
    try:
        from modules.inventory.wms_routes import wms_bp
        app.register_blueprint(wms_bp, url_prefix='/api/inventory/wms')
    except Exception as e:
        pass
    
    # Performance monitoring
    try:
        from modules.performance.performance_routes import performance_bp
        app.register_blueprint(performance_bp, url_prefix='/api/performance')
    except Exception as e:
        pass
    
    # Procurement module
    try:
        from modules.procurement.routes import bp as procurement_bp
        app.register_blueprint(procurement_bp)  # Already has /api/procurement prefix
    except Exception as e:
        print(f"Warning: Could not register procurement_bp: {e}")
        pass
    
    # Dashboard module
    try:
        from modules.dashboard.routes import bp as dashboard_bp
        app.register_blueprint(dashboard_bp)  # Already has /api/dashboard prefix
    except Exception as e:
        print(f"Warning: Could not register dashboard_bp: {e}")
        pass
    
    try:
        from modules.dashboard.module_activation_routes import module_activation_bp
        # Register with /api/dashboard/modules to get final path /api/dashboard/modules/user
        app.register_blueprint(module_activation_bp, url_prefix='/api/dashboard/modules')
        print(f"✅ Registered module_activation_bp with prefix /api/dashboard/modules")
        print(f"   Routes: /api/dashboard/modules/user, /api/dashboard/modules/available, etc.")
    except Exception as e:
        print(f"❌ Failed to register module_activation_bp: {e}")
        import traceback
        traceback.print_exc()
        pass
    
    try:
        from modules.core.user_data_routes import user_data_bp
        app.register_blueprint(user_data_bp)  # Already has /api/user-data prefix
    except Exception as e:
        print(f"Warning: Could not register user_data_bp: {e}")
        pass
    
    # Transaction templates
    try:
        from modules.finance.transaction_routes import transaction_bp
        app.register_blueprint(transaction_bp, url_prefix='/api/finance/transactions')
    except Exception as e:
        pass
    
    # Tenant-aware finance routes
    try:
        from modules.finance.tenant_aware_routes import tenant_finance_bp
        app.register_blueprint(tenant_finance_bp, url_prefix='/api/finance/tenant')
    except Exception as e:
        pass

def setup_error_handlers(app):
    """Setup error handlers for the application"""
    
    # JWT error handlers - these return 401 instead of 422
    from flask_jwt_extended.exceptions import JWTDecodeError, NoAuthorizationError, InvalidHeaderError, WrongTokenError, RevokedTokenError, FreshTokenRequired
    
    # Setup JWT loader functions to catch errors early
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({'error': 'Unauthorized', 'message': 'Missing or invalid token'}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({'error': 'Unauthorized', 'message': 'Signature verification failed'}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_data):
        return jsonify({'error': 'Unauthorized', 'message': 'Token has expired'}), 401

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_data):
        return jsonify({'error': 'Unauthorized', 'message': 'Token has been revoked'}), 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_response(jwt_header, jwt_data):
        return jsonify({'error': 'Unauthorized', 'message': 'Fresh token required'}), 401
    
    # Also register as error handlers for additional coverage
    @app.errorhandler(NoAuthorizationError)
    def handle_no_auth(error):
        return jsonify({'error': 'Missing authorization header', 'message': 'JWT token is required'}), 401
    
    @app.errorhandler(JWTDecodeError)
    def handle_jwt_decode_error(error):
        return jsonify({'error': 'Invalid JWT token', 'message': 'Token could not be decoded'}), 401
    
    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header(error):
        return jsonify({'error': 'Invalid authorization header', 'message': 'Authorization header must be in format: Bearer <token>'}), 401
    
    @app.errorhandler(WrongTokenError)
    def handle_wrong_token(error):
        return jsonify({'error': 'Wrong token type', 'message': 'Token type mismatch'}), 401
    
    @app.errorhandler(RevokedTokenError)
    def handle_revoked_token(error):
        return jsonify({'error': 'Token revoked', 'message': 'This token has been revoked'}), 401
    
    @app.errorhandler(FreshTokenRequired)
    def handle_fresh_token_required(error):
        return jsonify({'error': 'Fresh token required', 'message': 'This endpoint requires a fresh token'}), 401
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized access'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden access'}), 403

def setup_request_context(app):
    """Setup request context for the application"""
    
    @app.before_request
    def before_request():
        g.start_time = datetime.utcnow()
        g.request_id = request.headers.get('X-Request-ID', 'unknown')
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = (datetime.utcnow() - g.start_time).total_seconds()
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response