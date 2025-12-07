"""
🔧 EDONUOPS ERP - TENANT CONTEXT MIDDLEWARE
============================================================

Implements tenant context management for Flask application:
- Automatic tenant detection from JWT tokens
- Tenant context setting in PostgreSQL sessions
- Tenant validation and access control
- Audit logging for tenant access

Author: EdonuOps Team
Date: 2024
"""

import os
import logging
from functools import wraps
from flask import request, g, current_app, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import jwt

logger = logging.getLogger(__name__)

class TenantContextManager:
    """Manages tenant context for multi-tenant ERP system"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the tenant context manager with Flask app"""
        self.app = app
        
        # Register before_request handler
        app.before_request(self.set_tenant_context)
        
        # Register after_request handler
        app.after_request(self.cleanup_tenant_context)
        
        logger.info("✅ Tenant context manager initialized")
    
    def set_tenant_context(self):
        """Set tenant context for the current request"""
        try:
            # Get tenant_id from JWT token
            tenant_id = self._extract_tenant_from_token()
            
            if tenant_id:
                # Set tenant context in PostgreSQL session
                self._set_postgresql_tenant_context(tenant_id)
                
                # Store in Flask g object for access in views
                g.tenant_id = tenant_id
                g.tenant_context_set = True
                
                logger.debug(f"✅ Tenant context set: {tenant_id}")
            else:
                # No tenant context - this might be a public endpoint
                g.tenant_id = None
                g.tenant_context_set = False
                
                logger.debug("⚠️  No tenant context set")
                
        except Exception as e:
            logger.error(f"❌ Failed to set tenant context: {e}")
            g.tenant_id = None
            g.tenant_context_set = False
    
    def cleanup_tenant_context(self, response):
        """Clean up tenant context after request"""
        try:
            # Clear tenant context from PostgreSQL session
            if hasattr(g, 'tenant_context_set') and g.tenant_context_set:
                self._clear_postgresql_tenant_context()
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup tenant context: {e}")
        
        return response
    
    def _extract_tenant_from_token(self):
        """Extract tenant_id from JWT token"""
        try:
            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return None
            
            # Extract token
            if not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Decode JWT token
            jwt_secret = os.getenv('JWT_SECRET_KEY')
            if not jwt_secret:
                logger.error("❌ JWT_SECRET_KEY not set")
                return None
            
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            
            # Extract tenant_id
            tenant_id = payload.get('tenant_id')
            
            if tenant_id:
                logger.debug(f"✅ Extracted tenant_id from token: {tenant_id}")
                return tenant_id
            else:
                logger.warning("⚠️  No tenant_id in JWT token")
                return None
                
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️  JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️  Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting tenant from token: {e}")
            return None
    
    def _set_postgresql_tenant_context(self, tenant_id):
        """Set tenant context in PostgreSQL session"""
        try:
            from app import db
            
            # Set tenant context using our custom function
            db.session.execute(text("SELECT set_tenant_context(:tenant_id)"), {
                'tenant_id': tenant_id
            })
            
            # Also set user context for audit logging
            user_id = self._extract_user_from_token()
            if user_id:
                db.session.execute(text("SELECT set_config('my.user_id', :user_id, false)"), {
                    'user_id': str(user_id)
                })
            
            # Set user agent for audit logging
            user_agent = request.headers.get('User-Agent', 'Unknown')
            db.session.execute(text("SELECT set_config('my.user_agent', :user_agent, false)"), {
                'user_agent': user_agent
            })
            
            db.session.commit()
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to set PostgreSQL tenant context: {e}")
            raise
    
    def _clear_postgresql_tenant_context(self):
        """Clear tenant context from PostgreSQL session"""
        try:
            from app import db
            
            # Clear tenant context
            db.session.execute(text("SELECT set_config('my.tenant_id', '', false)"))
            db.session.execute(text("SELECT set_config('my.user_id', '', false)"))
            db.session.execute(text("SELECT set_config('my.user_agent', '', false)"))
            
            db.session.commit()
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to clear PostgreSQL tenant context: {e}")
    
    def _extract_user_from_token(self):
        """Extract user_id from JWT token"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header[7:]
            jwt_secret = os.getenv('JWT_SECRET_KEY')
            
            if not jwt_secret:
                return None
            
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            return payload.get('user_id')
            
        except Exception as e:
            logger.error(f"❌ Error extracting user from token: {e}")
            return None

def require_tenant_context(f):
    """Decorator to require tenant context for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'tenant_context_set') or not g.tenant_context_set:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'This endpoint requires a valid tenant context'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_tenant_access(user_id, tenant_id):
    """Validate that user has access to the specified tenant"""
    try:
        from app import db
        
        # Use our PostgreSQL function to validate access
        result = db.session.execute(text("""
            SELECT validate_tenant_access(:user_id, :tenant_id)
        """), {
            'user_id': user_id,
            'tenant_id': tenant_id
        })
        
        has_access = result.scalar()
        
        if has_access:
            logger.debug(f"✅ User {user_id} has access to tenant {tenant_id}")
            return True
        else:
            logger.warning(f"❌ User {user_id} denied access to tenant {tenant_id}")
            return False
            
    except SQLAlchemyError as e:
        logger.error(f"❌ Error validating tenant access: {e}")
        return False

def audit_tenant_access(user_id, tenant_id, action, table_name, record_id=None):
    """Audit tenant access for compliance"""
    try:
        from app import db
        
        # Use our PostgreSQL function to audit access
        db.session.execute(text("""
            SELECT audit_tenant_access(:user_id, :tenant_id, :action, :table_name, :record_id)
        """), {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'action': action,
            'table_name': table_name,
            'record_id': record_id
        })
        
        db.session.commit()
        
        logger.debug(f"✅ Audited tenant access: {action} on {table_name}")
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Error auditing tenant access: {e}")

def get_current_tenant():
    """Get current tenant ID from context"""
    return getattr(g, 'tenant_id', None)

def get_current_user():
    """Get current user ID from context"""
    return getattr(g, 'user_id', None)

# Example usage in API endpoints:
"""
from flask import Blueprint, request, jsonify, g
from .tenant_context import require_tenant_context, get_current_tenant, audit_tenant_access

api = Blueprint('api', __name__)

@api.route('/invoices', methods=['GET'])
@require_tenant_context
def get_invoices():
    tenant_id = get_current_tenant()
    user_id = get_current_user()
    
    # Audit the access
    audit_tenant_access(user_id, tenant_id, 'READ', 'invoices')
    
    # Query will automatically be filtered by RLS
    invoices = Invoice.query.all()
    
    return jsonify([invoice.to_dict() for invoice in invoices])
"""