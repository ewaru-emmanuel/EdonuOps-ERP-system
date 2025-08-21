from flask import request, g, current_app
from functools import wraps
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TenantManager:
    """Multi-tenancy manager for enterprise applications"""
    
    def __init__(self):
        self.tenants = {}
        self.current_tenant = None
    
    def get_tenant_id(self) -> Optional[str]:
        """Get current tenant ID from request"""
        # Check header first
        tenant_id = request.headers.get(current_app.config.get('TENANT_HEADER', 'X-Tenant-ID'))
        
        # Check subdomain
        if not tenant_id and request.host:
            subdomain = request.host.split('.')[0]
            if subdomain != 'www' and subdomain != 'api':
                tenant_id = subdomain
        
        # Check query parameter
        if not tenant_id:
            tenant_id = request.args.get('tenant_id')
        
        # Check JWT token
        if not tenant_id and hasattr(g, 'jwt_user'):
            tenant_id = getattr(g.jwt_user, 'tenant_id', None)
        
        return tenant_id or current_app.config.get('DEFAULT_TENANT', 'default')
    
    def set_current_tenant(self, tenant_id: str):
        """Set current tenant for request"""
        self.current_tenant = tenant_id
        g.current_tenant = tenant_id
    
    def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant configuration"""
        # In a real implementation, this would fetch from database
        return {
            'id': tenant_id,
            'name': f'Tenant {tenant_id}',
            'database_schema': f'schema_{tenant_id}',
            'features': ['finance', 'crm', 'hcm', 'inventory'],
            'settings': {
                'timezone': 'UTC',
                'currency': 'USD',
                'language': 'en',
                'date_format': 'YYYY-MM-DD'
            },
            'limits': {
                'max_users': 1000,
                'max_storage_gb': 100,
                'api_rate_limit': 10000
            }
        }
    
    def validate_tenant_access(self, tenant_id: str, user_id: str) -> bool:
        """Validate if user has access to tenant"""
        # In a real implementation, check user-tenant relationship
        return True
    
    def get_tenant_database_url(self, tenant_id: str) -> str:
        """Get tenant-specific database URL"""
        base_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        if 'postgresql' in base_url:
            # For PostgreSQL, use schema-based isolation
            return f"{base_url}?options=-csearch_path%3Dschema_{tenant_id}"
        else:
            # For other databases, use separate databases
            return base_url.replace('/edonuops_erp', f'/edonuops_tenant_{tenant_id}')

# Global tenant manager
tenant_manager = TenantManager()

def require_tenant(f):
    """Decorator to require valid tenant"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = tenant_manager.get_tenant_id()
        
        if not tenant_id:
            return {'error': 'Tenant ID required'}, 400
        
        # Set current tenant
        tenant_manager.set_current_tenant(tenant_id)
        
        # Validate tenant access if user is authenticated
        if hasattr(g, 'jwt_user'):
            if not tenant_manager.validate_tenant_access(tenant_id, g.jwt_user.id):
                return {'error': 'Access denied to tenant'}, 403
        
        return f(*args, **kwargs)
    return decorated_function

def tenant_aware(f):
    """Decorator to make function tenant-aware"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = tenant_manager.get_tenant_id()
        tenant_manager.set_current_tenant(tenant_id)
        return f(*args, **kwargs)
    return decorated_function

class TenantAwareModel:
    """Base class for tenant-aware models"""
    
    def __init__(self):
        self.tenant_id = None
    
    def set_tenant(self, tenant_id: str):
        """Set tenant for model operations"""
        self.tenant_id = tenant_id
    
    def get_tenant_filter(self):
        """Get tenant filter for queries"""
        if self.tenant_id:
            return {'tenant_id': self.tenant_id}
        return {}
    
    def before_insert(self, mapper, connection, target):
        """Set tenant_id before insert"""
        if hasattr(target, 'tenant_id') and not target.tenant_id:
            target.tenant_id = getattr(g, 'current_tenant', 'default')
    
    def before_update(self, mapper, connection, target):
        """Ensure tenant_id is set before update"""
        if hasattr(target, 'tenant_id') and not target.tenant_id:
            target.tenant_id = getattr(g, 'current_tenant', 'default')

# Tenant middleware
def tenant_middleware():
    """Flask middleware for tenant handling"""
    def middleware():
        tenant_id = tenant_manager.get_tenant_id()
        tenant_manager.set_current_tenant(tenant_id)
        
        # Add tenant info to request context
        g.current_tenant = tenant_id
        g.tenant_config = tenant_manager.get_tenant_config(tenant_id)
        
        logger.info(f"Request for tenant: {tenant_id}")
    
    return middleware

# Tenant utilities
def get_current_tenant() -> str:
    """Get current tenant ID"""
    return getattr(g, 'current_tenant', 'default')

def get_tenant_config() -> Dict[str, Any]:
    """Get current tenant configuration"""
    return getattr(g, 'tenant_config', {})

def is_multi_tenant() -> bool:
    """Check if multi-tenancy is enabled"""
    return current_app.config.get('ENABLE_MULTI_TENANCY', True)

def get_tenant_cache_key(key: str) -> str:
    """Get tenant-specific cache key"""
    tenant_id = get_current_tenant()
    return f"tenant:{tenant_id}:{key}"

# Database schema management for PostgreSQL
def create_tenant_schema(tenant_id: str):
    """Create database schema for tenant"""
    from sqlalchemy import text
    from flask_sqlalchemy import SQLAlchemy
    
    db = SQLAlchemy()
    schema_name = f'schema_{tenant_id}'
    
    try:
        # Create schema
        db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS {schema_name}'))
        db.session.commit()
        logger.info(f"Created schema for tenant: {tenant_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to create schema for tenant {tenant_id}: {e}")
        db.session.rollback()
        return False

def drop_tenant_schema(tenant_id: str):
    """Drop database schema for tenant"""
    from sqlalchemy import text
    from flask_sqlalchemy import SQLAlchemy
    
    db = SQLAlchemy()
    schema_name = f'schema_{tenant_id}'
    
    try:
        # Drop schema and all objects
        db.session.execute(text(f'DROP SCHEMA IF EXISTS {schema_name} CASCADE'))
        db.session.commit()
        logger.info(f"Dropped schema for tenant: {tenant_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to drop schema for tenant {tenant_id}: {e}")
        db.session.rollback()
        return False
