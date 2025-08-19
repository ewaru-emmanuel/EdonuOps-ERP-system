from app import db
from datetime import datetime
# Use db.JSON for SQLite compatibility

class APIKey(db.Model):
    """API keys for external integrations"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(200), nullable=False)
    key_hash = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permissions = db.Column(db.JSON)  # Store API permissions
    rate_limit = db.Column(db.Integer, default=1000)  # Requests per hour
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    api_calls = db.relationship('APICall', backref='api_key', lazy=True)

class APICall(db.Model):
    """API call tracking and analytics"""
    __tablename__ = 'api_calls'
    
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)  # GET, POST, PUT, DELETE
    status_code = db.Column(db.Integer, nullable=False)
    response_time = db.Column(db.Float)  # Response time in milliseconds
    request_size = db.Column(db.Integer)  # Request size in bytes
    response_size = db.Column(db.Integer)  # Response size in bytes
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    call_metadata = db.Column(db.JSON)  # Store additional call metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class APIVersion(db.Model):
    """API versioning and documentation"""
    __tablename__ = 'api_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False)  # v1, v2, etc.
    status = db.Column(db.String(50), default='beta')  # alpha, beta, stable, deprecated
    release_date = db.Column(db.Date)
    deprecation_date = db.Column(db.Date)
    changelog = db.Column(db.Text)
    documentation_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class APIEndpoint(db.Model):
    """API endpoint definitions"""
    __tablename__ = 'api_endpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('api_versions.id'), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.JSON)  # Store parameter definitions
    response_schema = db.Column(db.JSON)  # Store response schema
    rate_limit = db.Column(db.Integer)
    authentication_required = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    version = db.relationship('APIVersion', foreign_keys=[version_id])

class Integration(db.Model):
    """Third-party integrations"""
    __tablename__ = 'integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    integration_type = db.Column(db.String(100), nullable=False)  # payment, shipping, accounting, crm
    provider = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(50), default='1.0')
    status = db.Column(db.String(50), default='active')  # active, inactive, error, maintenance
    configuration = db.Column(db.JSON)  # Store integration configuration
    credentials = db.Column(db.JSON)  # Store encrypted credentials
    webhook_url = db.Column(db.String(500))
    api_endpoints = db.Column(db.JSON)  # Store API endpoint mappings
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IntegrationEvent(db.Model):
    """Integration event tracking"""
    __tablename__ = 'integration_events'
    
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('integrations.id'), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)  # sync, webhook, error, etc.
    direction = db.Column(db.String(20), nullable=False)  # inbound, outbound
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    payload = db.Column(db.JSON)  # Store event payload
    response = db.Column(db.JSON)  # Store response data
    error_message = db.Column(db.Text)
    processing_time = db.Column(db.Float)  # Processing time in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    integration = db.relationship('Integration', foreign_keys=[integration_id])

class MarketplaceApp(db.Model):
    """Marketplace applications"""
    __tablename__ = 'marketplace_apps'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # finance, crm, inventory, etc.
    app_type = db.Column(db.String(100), nullable=False)  # integration, extension, connector
    version = db.Column(db.String(50), default='1.0')
    status = db.Column(db.String(50), default='draft')  # draft, pending, approved, rejected, published
    pricing_model = db.Column(db.String(50), default='free')  # free, subscription, one_time
    price = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    download_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    app_file_url = db.Column(db.String(500))
    documentation_url = db.Column(db.String(500))
    support_url = db.Column(db.String(500))
    tags = db.Column(db.JSON)  # Store app tags
    screenshots = db.Column(db.JSON)  # Store screenshot URLs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    developer = db.relationship('User', foreign_keys=[developer_id])
    reviews = db.relationship('AppReview', backref='app', lazy=True)
    installations = db.relationship('AppInstallation', backref='app', lazy=True)

class AppReview(db.Model):
    """App reviews and ratings"""
    __tablename__ = 'app_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('marketplace_apps.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])

class AppInstallation(db.Model):
    """App installation tracking"""
    __tablename__ = 'app_installations'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('marketplace_apps.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='installed')  # installed, active, inactive, uninstalled
    configuration = db.Column(db.JSON)  # Store app configuration
    installed_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    deactivated_at = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])

class DeveloperAccount(db.Model):
    """Developer accounts for marketplace"""
    __tablename__ = 'developer_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(200))
    website = db.Column(db.String(500))
    description = db.Column(db.Text)
    contact_email = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    address = db.Column(db.JSON)
    verification_status = db.Column(db.String(50), default='pending')  # pending, verified, rejected
    verification_documents = db.Column(db.JSON)  # Store verification documents
    payment_info = db.Column(db.JSON)  # Store payment information
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])

class Webhook(db.Model):
    """Webhook configurations"""
    __tablename__ = 'webhooks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    events = db.Column(db.JSON)  # Store event types to listen for
    secret_key = db.Column(db.String(255))  # For webhook signature verification
    is_active = db.Column(db.Boolean, default=True)
    retry_count = db.Column(db.Integer, default=3)
    timeout = db.Column(db.Integer, default=30)  # Timeout in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    deliveries = db.relationship('WebhookDelivery', backref='webhook', lazy=True)

class WebhookDelivery(db.Model):
    """Webhook delivery tracking"""
    __tablename__ = 'webhook_deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhooks.id'), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON)  # Store webhook payload
    response_status = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    response_headers = db.Column(db.JSON)
    delivery_time = db.Column(db.Float)  # Delivery time in seconds
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    delivered_at = db.Column(db.DateTime, default=datetime.utcnow)

class APIDocumentation(db.Model):
    """API documentation and guides"""
    __tablename__ = 'api_documentation'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), default='markdown')  # markdown, html, text
    category = db.Column(db.String(100), nullable=False)  # getting_started, reference, tutorials, examples
    version_id = db.Column(db.Integer, db.ForeignKey('api_versions.id'))
    order_index = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    version = db.relationship('APIVersion', foreign_keys=[version_id])

class SandboxEnvironment(db.Model):
    """Sandbox environments for developers"""
    __tablename__ = 'sandbox_environments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    environment_name = db.Column(db.String(200), nullable=False)
    environment_type = db.Column(db.String(50), default='development')  # development, testing, staging
    status = db.Column(db.String(50), default='active')  # active, suspended, deleted
    configuration = db.Column(db.JSON)  # Store environment configuration
    data_snapshot = db.Column(db.JSON)  # Store sample data
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])

class PartnerProgram(db.Model):
    """Partner program management"""
    __tablename__ = 'partner_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(200), nullable=False)
    partner_type = db.Column(db.String(100), nullable=False)  # reseller, implementer, developer, consultant
    contact_person = db.Column(db.String(200))
    contact_email = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    website = db.Column(db.String(500))
    description = db.Column(db.Text)
    certification_level = db.Column(db.String(50), default='bronze')  # bronze, silver, gold, platinum
    certification_date = db.Column(db.Date)
    commission_rate = db.Column(db.Float, default=0.0)  # Commission percentage
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# User model is defined in core.models
