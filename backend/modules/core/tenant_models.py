from app import db
from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSON

class Tenant(db.Model):
    """
    Core tenant table for multi-tenancy
    Each tenant represents a separate company/organization
    """
    __tablename__ = 'tenants'
    
    id = db.Column(db.String(50), primary_key=True)  # tenant_123, company_abc
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), unique=True)  # company.com
    subscription_plan = db.Column(db.String(50), default='free')  # free, basic, premium, enterprise
    status = db.Column(db.String(20), default='active')  # active, suspended, cancelled
    
    # Settings and configuration
    settings = db.Column(JSON)  # Per-tenant settings
    tenant_metadata = db.Column(JSON)  # Additional tenant metadata
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_tenants = db.relationship('UserTenant', backref='tenant', lazy='dynamic')
    modules = db.relationship('TenantModule', backref='tenant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Tenant {self.id}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'subscription_plan': self.subscription_plan,
            'status': self.status,
            'settings': self.settings or {},
            'tenant_metadata': self.tenant_metadata or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

class UserTenant(db.Model):
    """
    User-Tenant mapping table
    Supports users belonging to multiple tenants with different roles
    """
    __tablename__ = 'user_tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # User identifier
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenants.id'), nullable=False)
    role = db.Column(db.String(50), default='user')  # admin, manager, user, viewer
    is_default = db.Column(db.Boolean, default=False)  # Default tenant for user
    
    # Permissions and access control
    permissions = db.Column(JSON)  # Specific permissions for this user-tenant combination
    
    # Audit fields
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tenant_id', name='unique_user_tenant'),
        Index('idx_user_tenants_user', 'user_id'),
        Index('idx_user_tenants_tenant', 'tenant_id'),
    )
    
    def __repr__(self):
        return f'<UserTenant {self.user_id} -> {self.tenant_id} ({self.role})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'role': self.role,
            'is_default': self.is_default,
            'permissions': self.permissions or {},
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

class TenantModule(db.Model):
    """
    Tenant-specific module activation
    Controls which modules/features are available per tenant
    """
    __tablename__ = 'tenant_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenants.id'), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)  # finance, inventory, crm, etc.
    enabled = db.Column(db.Boolean, default=False)
    activated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # For time-limited access
    
    # Module-specific configuration
    configuration = db.Column(JSON)  # Module-specific settings
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'module_name', name='unique_tenant_module'),
        Index('idx_tenant_modules_tenant', 'tenant_id'),
        Index('idx_tenant_modules_module', 'module_name'),
    )
    
    def __repr__(self):
        return f'<TenantModule {self.tenant_id}: {self.module_name} ({self.enabled})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'module_name': self.module_name,
            'enabled': self.enabled,
            'activated_at': self.activated_at.isoformat() if self.activated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'configuration': self.configuration or {}
        }

class TenantSettings(db.Model):
    """
    Per-tenant settings and configuration
    Stores tenant-specific preferences and configurations
    """
    __tablename__ = 'tenant_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenants.id'), nullable=False)
    setting_key = db.Column(db.String(100), nullable=False)  # currency, timezone, date_format, etc.
    setting_value = db.Column(db.Text)  # JSON string or simple value
    setting_type = db.Column(db.String(20), default='string')  # string, number, boolean, json
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(100))
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'setting_key', name='unique_tenant_setting'),
        Index('idx_tenant_settings_tenant', 'tenant_id'),
    )
    
    def __repr__(self):
        return f'<TenantSettings {self.tenant_id}: {self.setting_key} = {self.setting_value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'setting_type': self.setting_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }
