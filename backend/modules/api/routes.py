from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from modules.api.models import (
    APIKey, APICall, APIVersion, APIEndpoint, Integration, IntegrationEvent,
    MarketplaceApp, AppReview, AppInstallation, DeveloperAccount, Webhook,
    WebhookDelivery, APIDocumentation, SandboxEnvironment, PartnerProgram
)
import uuid

bp = Blueprint('api', __name__, url_prefix='/api/ecosystem')

# Sample data for initial state
api_keys = []
api_calls = []
api_versions = []
api_endpoints = []
integrations = []
integration_events = []
marketplace_apps = []
app_reviews = []
app_installations = []
developer_accounts = []
webhooks = []
webhook_deliveries = []
api_documentation = []
sandbox_environments = []
partner_programs = []

# API Key endpoints
@bp.route('/keys', methods=['GET'])
def get_api_keys():
    """Get all API keys"""
    user_id = request.args.get('user_id', type=int)
    is_active = request.args.get('is_active', type=bool)
    
    filtered_keys = api_keys
    if user_id:
        filtered_keys = [k for k in api_keys if k.get('user_id') == user_id]
    if is_active is not None:
        filtered_keys = [k for k in api_keys if k.get('is_active') == is_active]
    
    return jsonify(filtered_keys)

@bp.route('/keys', methods=['POST'])
def create_api_key():
    """Create a new API key"""
    data = request.get_json()
    
    # Generate a unique key hash
    key_hash = f"edonuops_{uuid.uuid4().hex[:32]}"
    
    new_key = {
        "id": len(api_keys) + 1,
        "key_name": data.get('key_name'),
        "key_hash": key_hash,
        "user_id": data.get('user_id'),
        "permissions": data.get('permissions', {}),
        "rate_limit": data.get('rate_limit', 1000),
        "is_active": data.get('is_active', True),
        "expires_at": data.get('expires_at'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    api_keys.append(new_key)
    return jsonify(new_key), 201

# API Call tracking endpoints
@bp.route('/calls', methods=['GET'])
def get_api_calls():
    """Get API call history"""
    api_key_id = request.args.get('api_key_id', type=int)
    endpoint = request.args.get('endpoint')
    
    filtered_calls = api_calls
    if api_key_id:
        filtered_calls = [c for c in api_calls if c.get('api_key_id') == api_key_id]
    if endpoint:
        filtered_calls = [c for c in api_calls if c.get('endpoint') == endpoint]
    
    return jsonify(filtered_calls)

# API Version endpoints
@bp.route('/versions', methods=['GET'])
def get_api_versions():
    """Get API versions"""
    status = request.args.get('status')
    
    filtered_versions = api_versions
    if status:
        filtered_versions = [v for v in api_versions if v.get('status') == status]
    
    return jsonify(filtered_versions)

@bp.route('/versions', methods=['POST'])
def create_api_version():
    """Create a new API version"""
    data = request.get_json()
    
    new_version = {
        "id": len(api_versions) + 1,
        "version": data.get('version'),
        "status": data.get('status', 'beta'),
        "release_date": data.get('release_date'),
        "deprecation_date": data.get('deprecation_date'),
        "changelog": data.get('changelog'),
        "documentation_url": data.get('documentation_url'),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    api_versions.append(new_version)
    return jsonify(new_version), 201

# API Endpoint endpoints
@bp.route('/endpoints', methods=['GET'])
def get_api_endpoints():
    """Get API endpoints"""
    version_id = request.args.get('version_id', type=int)
    method = request.args.get('method')
    
    filtered_endpoints = api_endpoints
    if version_id:
        filtered_endpoints = [e for e in api_endpoints if e.get('version_id') == version_id]
    if method:
        filtered_endpoints = [e for e in api_endpoints if e.get('method') == method]
    
    return jsonify(filtered_endpoints)

@bp.route('/endpoints', methods=['POST'])
def create_api_endpoint():
    """Create a new API endpoint"""
    data = request.get_json()
    
    new_endpoint = {
        "id": len(api_endpoints) + 1,
        "version_id": data.get('version_id'),
        "path": data.get('path'),
        "method": data.get('method'),
        "description": data.get('description'),
        "parameters": data.get('parameters', {}),
        "response_schema": data.get('response_schema', {}),
        "rate_limit": data.get('rate_limit'),
        "authentication_required": data.get('authentication_required', True),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    api_endpoints.append(new_endpoint)
    return jsonify(new_endpoint), 201

# Integration endpoints
@bp.route('/integrations', methods=['GET'])
def get_integrations():
    """Get integrations"""
    integration_type = request.args.get('integration_type')
    provider = request.args.get('provider')
    status = request.args.get('status')
    
    filtered_integrations = integrations
    if integration_type:
        filtered_integrations = [i for i in integrations if i.get('integration_type') == integration_type]
    if provider:
        filtered_integrations = [i for i in integrations if i.get('provider') == provider]
    if status:
        filtered_integrations = [i for i in integrations if i.get('status') == status]
    
    return jsonify(filtered_integrations)

@bp.route('/integrations', methods=['POST'])
def create_integration():
    """Create a new integration"""
    data = request.get_json()
    
    new_integration = {
        "id": len(integrations) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "integration_type": data.get('integration_type'),
        "provider": data.get('provider'),
        "version": data.get('version', '1.0'),
        "status": data.get('status', 'active'),
        "configuration": data.get('configuration', {}),
        "credentials": data.get('credentials', {}),
        "webhook_url": data.get('webhook_url'),
        "api_endpoints": data.get('api_endpoints', {}),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    integrations.append(new_integration)
    return jsonify(new_integration), 201

# Integration Event endpoints
@bp.route('/integrations/<int:integration_id>/events', methods=['GET'])
def get_integration_events(integration_id):
    """Get events for a specific integration"""
    event_type = request.args.get('event_type')
    status = request.args.get('status')
    
    filtered_events = [e for e in integration_events if e.get('integration_id') == integration_id]
    if event_type:
        filtered_events = [e for e in filtered_events if e.get('event_type') == event_type]
    if status:
        filtered_events = [e for e in filtered_events if e.get('status') == status]
    
    return jsonify(filtered_events)

# Marketplace App endpoints
@bp.route('/marketplace/apps', methods=['GET'])
def get_marketplace_apps():
    """Get marketplace apps"""
    category = request.args.get('category')
    app_type = request.args.get('app_type')
    status = request.args.get('status')
    
    filtered_apps = marketplace_apps
    if category:
        filtered_apps = [a for a in marketplace_apps if a.get('category') == category]
    if app_type:
        filtered_apps = [a for a in marketplace_apps if a.get('app_type') == app_type]
    if status:
        filtered_apps = [a for a in marketplace_apps if a.get('status') == status]
    
    return jsonify(filtered_apps)

@bp.route('/marketplace/apps', methods=['POST'])
def create_marketplace_app():
    """Create a new marketplace app"""
    data = request.get_json()
    
    new_app = {
        "id": len(marketplace_apps) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "developer_id": data.get('developer_id'),
        "category": data.get('category'),
        "app_type": data.get('app_type'),
        "version": data.get('version', '1.0'),
        "status": data.get('status', 'draft'),
        "pricing_model": data.get('pricing_model', 'free'),
        "price": data.get('price', 0.0),
        "currency": data.get('currency', 'USD'),
        "download_count": data.get('download_count', 0),
        "rating": data.get('rating', 0.0),
        "review_count": data.get('review_count', 0),
        "app_file_url": data.get('app_file_url'),
        "documentation_url": data.get('documentation_url'),
        "support_url": data.get('support_url'),
        "tags": data.get('tags', []),
        "screenshots": data.get('screenshots', []),
        "created_at": datetime.utcnow().isoformat()
    }
    
    marketplace_apps.append(new_app)
    return jsonify(new_app), 201

# App Review endpoints
@bp.route('/marketplace/apps/<int:app_id>/reviews', methods=['GET'])
def get_app_reviews(app_id):
    """Get reviews for a specific app"""
    reviews = [r for r in app_reviews if r.get('app_id') == app_id]
    return jsonify(reviews)

@bp.route('/marketplace/apps/<int:app_id>/reviews', methods=['POST'])
def create_app_review(app_id):
    """Create a new app review"""
    data = request.get_json()
    
    new_review = {
        "id": len(app_reviews) + 1,
        "app_id": app_id,
        "user_id": data.get('user_id'),
        "rating": data.get('rating'),
        "review_text": data.get('review_text'),
        "is_verified": data.get('is_verified', False),
        "helpful_count": data.get('helpful_count', 0),
        "created_at": datetime.utcnow().isoformat()
    }
    
    app_reviews.append(new_review)
    return jsonify(new_review), 201

# App Installation endpoints
@bp.route('/marketplace/apps/<int:app_id>/installations', methods=['GET'])
def get_app_installations(app_id):
    """Get installations for a specific app"""
    installations = [i for i in app_installations if i.get('app_id') == app_id]
    return jsonify(installations)

@bp.route('/marketplace/apps/<int:app_id>/install', methods=['POST'])
def install_app(app_id):
    """Install an app"""
    data = request.get_json()
    
    new_installation = {
        "id": len(app_installations) + 1,
        "app_id": app_id,
        "user_id": data.get('user_id'),
        "status": data.get('status', 'installed'),
        "configuration": data.get('configuration', {}),
        "installed_at": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    app_installations.append(new_installation)
    return jsonify(new_installation), 201

# Developer Account endpoints
@bp.route('/developers', methods=['GET'])
def get_developer_accounts():
    """Get developer accounts"""
    verification_status = request.args.get('verification_status')
    
    filtered_accounts = developer_accounts
    if verification_status:
        filtered_accounts = [a for a in developer_accounts if a.get('verification_status') == verification_status]
    
    return jsonify(filtered_accounts)

@bp.route('/developers', methods=['POST'])
def create_developer_account():
    """Create a new developer account"""
    data = request.get_json()
    
    new_account = {
        "id": len(developer_accounts) + 1,
        "user_id": data.get('user_id'),
        "company_name": data.get('company_name'),
        "website": data.get('website'),
        "description": data.get('description'),
        "contact_email": data.get('contact_email'),
        "contact_phone": data.get('contact_phone'),
        "address": data.get('address', {}),
        "verification_status": data.get('verification_status', 'pending'),
        "verification_documents": data.get('verification_documents', {}),
        "payment_info": data.get('payment_info', {}),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    developer_accounts.append(new_account)
    return jsonify(new_account), 201

# Webhook endpoints
@bp.route('/webhooks', methods=['GET'])
def get_webhooks():
    """Get webhooks"""
    user_id = request.args.get('user_id', type=int)
    is_active = request.args.get('is_active', type=bool)
    
    filtered_webhooks = webhooks
    if user_id:
        filtered_webhooks = [w for w in webhooks if w.get('user_id') == user_id]
    if is_active is not None:
        filtered_webhooks = [w for w in webhooks if w.get('is_active') == is_active]
    
    return jsonify(filtered_webhooks)

@bp.route('/webhooks', methods=['POST'])
def create_webhook():
    """Create a new webhook"""
    data = request.get_json()
    
    new_webhook = {
        "id": len(webhooks) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "user_id": data.get('user_id'),
        "url": data.get('url'),
        "events": data.get('events', []),
        "secret_key": data.get('secret_key'),
        "is_active": data.get('is_active', True),
        "retry_count": data.get('retry_count', 3),
        "timeout": data.get('timeout', 30),
        "created_at": datetime.utcnow().isoformat()
    }
    
    webhooks.append(new_webhook)
    return jsonify(new_webhook), 201

# Webhook Delivery endpoints
@bp.route('/webhooks/<int:webhook_id>/deliveries', methods=['GET'])
def get_webhook_deliveries(webhook_id):
    """Get deliveries for a specific webhook"""
    deliveries = [d for d in webhook_deliveries if d.get('webhook_id') == webhook_id]
    return jsonify(deliveries)

# API Documentation endpoints
@bp.route('/documentation', methods=['GET'])
def get_api_documentation():
    """Get API documentation"""
    category = request.args.get('category')
    version_id = request.args.get('version_id', type=int)
    
    filtered_docs = api_documentation
    if category:
        filtered_docs = [d for d in api_documentation if d.get('category') == category]
    if version_id:
        filtered_docs = [d for d in api_documentation if d.get('version_id') == version_id]
    
    return jsonify(filtered_docs)

@bp.route('/documentation', methods=['POST'])
def create_api_documentation():
    """Create new API documentation"""
    data = request.get_json()
    
    new_doc = {
        "id": len(api_documentation) + 1,
        "title": data.get('title'),
        "content": data.get('content'),
        "content_type": data.get('content_type', 'markdown'),
        "category": data.get('category'),
        "version_id": data.get('version_id'),
        "order_index": data.get('order_index', 0),
        "is_published": data.get('is_published', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    api_documentation.append(new_doc)
    return jsonify(new_doc), 201

# Sandbox Environment endpoints
@bp.route('/sandbox', methods=['GET'])
def get_sandbox_environments():
    """Get sandbox environments"""
    user_id = request.args.get('user_id', type=int)
    environment_type = request.args.get('environment_type')
    
    filtered_environments = sandbox_environments
    if user_id:
        filtered_environments = [e for e in sandbox_environments if e.get('user_id') == user_id]
    if environment_type:
        filtered_environments = [e for e in sandbox_environments if e.get('environment_type') == environment_type]
    
    return jsonify(filtered_environments)

@bp.route('/sandbox', methods=['POST'])
def create_sandbox_environment():
    """Create a new sandbox environment"""
    data = request.get_json()
    
    new_environment = {
        "id": len(sandbox_environments) + 1,
        "user_id": data.get('user_id'),
        "environment_name": data.get('environment_name'),
        "environment_type": data.get('environment_type', 'development'),
        "status": data.get('status', 'active'),
        "configuration": data.get('configuration', {}),
        "data_snapshot": data.get('data_snapshot', {}),
        "expires_at": data.get('expires_at'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    sandbox_environments.append(new_environment)
    return jsonify(new_environment), 201

# Partner Program endpoints
@bp.route('/partners', methods=['GET'])
def get_partner_programs():
    """Get partner programs"""
    partner_type = request.args.get('partner_type')
    certification_level = request.args.get('certification_level')
    
    filtered_partners = partner_programs
    if partner_type:
        filtered_partners = [p for p in partner_programs if p.get('partner_type') == partner_type]
    if certification_level:
        filtered_partners = [p for p in partner_programs if p.get('certification_level') == certification_level]
    
    return jsonify(filtered_partners)

@bp.route('/partners', methods=['POST'])
def create_partner_program():
    """Create a new partner program"""
    data = request.get_json()
    
    new_partner = {
        "id": len(partner_programs) + 1,
        "partner_name": data.get('partner_name'),
        "partner_type": data.get('partner_type'),
        "contact_person": data.get('contact_person'),
        "contact_email": data.get('contact_email'),
        "contact_phone": data.get('contact_phone'),
        "website": data.get('website'),
        "description": data.get('description'),
        "certification_level": data.get('certification_level', 'bronze'),
        "certification_date": data.get('certification_date'),
        "commission_rate": data.get('commission_rate', 0.0),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    partner_programs.append(new_partner)
    return jsonify(new_partner), 201

# Analytics and Reporting endpoints
@bp.route('/analytics/ecosystem-summary', methods=['GET'])
def get_ecosystem_summary():
    """Get ecosystem summary analytics"""
    summary = {
        "total_api_keys": len(api_keys),
        "active_api_keys": len([k for k in api_keys if k.get('is_active')]),
        "total_api_calls": len(api_calls),
        "total_integrations": len(integrations),
        "active_integrations": len([i for i in integrations if i.get('is_active')]),
        "total_marketplace_apps": len(marketplace_apps),
        "published_apps": len([a for a in marketplace_apps if a.get('status') == 'published']),
        "total_developers": len(developer_accounts),
        "verified_developers": len([d for d in developer_accounts if d.get('verification_status') == 'verified']),
        "total_webhooks": len(webhooks),
        "active_webhooks": len([w for w in webhooks if w.get('is_active')]),
        "total_partners": len(partner_programs),
        "active_partners": len([p for p in partner_programs if p.get('is_active')])
    }
    
    return jsonify(summary)

@bp.route('/analytics/api-usage', methods=['GET'])
def get_api_usage_analytics():
    """Get API usage analytics"""
    usage = {
        "total_calls": len(api_calls),
        "calls_by_endpoint": {},
        "calls_by_status": {
            "success": len([c for c in api_calls if c.get('status_code', 200) < 400]),
            "error": len([c for c in api_calls if c.get('status_code', 200) >= 400])
        },
        "average_response_time": sum([c.get('response_time', 0) for c in api_calls]) / max(len(api_calls), 1),
        "top_api_keys": []
    }
    
    return jsonify(usage)

# Initialize sample data
def init_sample_data():
    """Initialize sample API ecosystem data"""
    global api_versions, api_endpoints, integrations, marketplace_apps, developer_accounts
    
    # Sample API versions
    api_versions.extend([
        {
            "id": 1,
            "version": "v1",
            "status": "stable",
            "release_date": "2024-01-01",
            "documentation_url": "https://docs.edonuops.com/api/v1",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "version": "v2",
            "status": "beta",
            "release_date": "2024-06-01",
            "documentation_url": "https://docs.edonuops.com/api/v2",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample API endpoints
    api_endpoints.extend([
        {
            "id": 1,
            "version_id": 1,
            "path": "/api/v1/finance/accounts",
            "method": "GET",
            "description": "Get financial accounts",
            "parameters": {"page": "integer", "limit": "integer"},
            "response_schema": {"type": "object", "properties": {"accounts": {"type": "array"}}},
            "rate_limit": 1000,
            "authentication_required": True,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample integrations
    integrations.extend([
        {
            "id": 1,
            "name": "Stripe Payment Integration",
            "description": "Payment processing integration with Stripe",
            "integration_type": "payment",
            "provider": "Stripe",
            "version": "1.0",
            "status": "active",
            "configuration": {"webhook_secret": "whsec_xxx"},
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample marketplace apps
    marketplace_apps.extend([
        {
            "id": 1,
            "name": "Advanced Analytics Dashboard",
            "description": "Enhanced analytics and reporting dashboard",
            "developer_id": 1,
            "category": "analytics",
            "app_type": "extension",
            "version": "1.0",
            "status": "published",
            "pricing_model": "subscription",
            "price": 99.0,
            "currency": "USD",
            "download_count": 150,
            "rating": 4.5,
            "review_count": 25,
            "tags": ["analytics", "dashboard", "reporting"],
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample developer accounts
    developer_accounts.extend([
        {
            "id": 1,
            "user_id": 1,
            "company_name": "Tech Solutions Inc",
            "website": "https://techsolutions.com",
            "description": "Leading technology solutions provider",
            "contact_email": "dev@techsolutions.com",
            "verification_status": "verified",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ])

# Initialize sample data when module loads
init_sample_data()
