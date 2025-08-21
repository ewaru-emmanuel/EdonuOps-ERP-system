import jwt
import bcrypt
import secrets
import qrcode
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from flask import request, current_app, g
from functools import wraps
import logging
import hashlib
import hmac
import time

logger = logging.getLogger(__name__)

class EnterpriseSecurity:
    """Enterprise-grade security system with SSO, MFA, and advanced features"""
    
    def __init__(self):
        self.secret_key = None
        self.jwt_secret = None
        self.algorithm = 'HS256'
    
    def _get_config(self):
        """Get configuration from Flask app context"""
        if self.secret_key is None or self.jwt_secret is None:
            try:
                from flask import current_app
                self.secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
                self.jwt_secret = current_app.config.get('JWT_SECRET_KEY', 'default-jwt-secret')
            except RuntimeError:
                self.secret_key = 'default-secret-key'
                self.jwt_secret = 'default-jwt-secret'
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_jwt_token(self, user_id: str, tenant_id: str = None, 
                          roles: List[str] = None, permissions: List[str] = None) -> str:
        """Generate JWT token with user claims"""
        self._get_config()
        payload = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'roles': roles or [],
            'permissions': permissions or [],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'jti': secrets.token_urlsafe(32)  # JWT ID for revocation
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        self._get_config()
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return None
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token for token renewal"""
        self._get_config()
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=30),
            'jti': secrets.token_urlsafe(32)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

class MFAService:
    """Multi-Factor Authentication service"""
    
    def __init__(self):
        self.secret_key = None
    
    def _get_config(self):
        """Get configuration from Flask app context"""
        if self.secret_key is None:
            try:
                from flask import current_app
                self.secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
            except RuntimeError:
                self.secret_key = 'default-secret-key'
    
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret for 2FA"""
        return base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
    
    def generate_totp_qr(self, secret: str, user_email: str, issuer: str = "EdonuOps") -> str:
        """Generate QR code for TOTP setup"""
        uri = f"otpauth://totp/{issuer}:{user_email}?secret={secret}&issuer={issuer}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        # Convert to base64 for embedding in HTML
        img = qr.make_image(fill_color="black", back_color="white")
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    
    def verify_totp(self, secret: str, token: str, window: int = 1) -> bool:
        """Verify TOTP token"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(3).upper()[:8]  # 8-character hex code
            codes.append(code)
        return codes

class SSOService:
    """Single Sign-On service"""
    
    def __init__(self):
        self.providers = {
            'google': self._google_oauth,
            'microsoft': self._microsoft_oauth,
            'saml': self._saml_auth
        }
    
    def _google_oauth(self, code: str) -> Optional[Dict[str, Any]]:
        """Google OAuth authentication"""
        # Implementation for Google OAuth
        pass
    
    def _microsoft_oauth(self, code: str) -> Optional[Dict[str, Any]]:
        """Microsoft OAuth authentication"""
        # Implementation for Microsoft OAuth
        pass
    
    def _saml_auth(self, saml_response: str) -> Optional[Dict[str, Any]]:
        """SAML authentication"""
        # Implementation for SAML
        pass
    
    def authenticate_sso(self, provider: str, auth_data: str) -> Optional[Dict[str, Any]]:
        """Authenticate via SSO provider"""
        if provider in self.providers:
            return self.providers[provider](auth_data)
        return None

class RoleBasedAccessControl:
    """Role-Based Access Control system"""
    
    def __init__(self):
        self.roles = {
            'super_admin': {
                'permissions': ['*'],
                'description': 'Full system access'
            },
            'tenant_admin': {
                'permissions': [
                    'user:manage', 'role:manage', 'settings:manage',
                    'finance:*', 'crm:*', 'hcm:*', 'inventory:*'
                ],
                'description': 'Tenant administrator'
            },
            'finance_manager': {
                'permissions': [
                    'finance:read', 'finance:write', 'finance:approve',
                    'reports:finance'
                ],
                'description': 'Finance module manager'
            },
            'crm_manager': {
                'permissions': [
                    'crm:read', 'crm:write', 'crm:manage',
                    'reports:crm'
                ],
                'description': 'CRM module manager'
            },
            'user': {
                'permissions': [
                    'dashboard:read', 'profile:manage',
                    'finance:read', 'crm:read', 'hcm:read'
                ],
                'description': 'Standard user'
            }
        }
    
    def has_permission(self, user_roles: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        for role in user_roles:
            if role in self.roles:
                permissions = self.roles[role]['permissions']
                if '*' in permissions or required_permission in permissions:
                    return True
        return False
    
    def get_user_permissions(self, user_roles: List[str]) -> List[str]:
        """Get all permissions for user roles"""
        permissions = set()
        for role in user_roles:
            if role in self.roles:
                permissions.update(self.roles[role]['permissions'])
        return list(permissions)

class SecurityMiddleware:
    """Security middleware for request processing"""
    
    def __init__(self):
        self.security = EnterpriseSecurity()
        self.rbac = RoleBasedAccessControl()
    
    def authenticate_request(self, request):
        """Authenticate incoming request"""
        # Extract token from headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        payload = self.security.verify_jwt_token(token)
        
        if payload:
            # Add user info to request context
            g.jwt_user = payload
            g.current_user_id = payload.get('user_id')
            g.current_tenant = payload.get('tenant_id')
            g.user_roles = payload.get('roles', [])
            g.user_permissions = payload.get('permissions', [])
        
        return payload
    
    def rate_limit_check(self, request, user_id: str) -> bool:
        """Check rate limiting for user"""
        # Implementation for rate limiting
        return True
    
    def audit_log(self, request, action: str, resource: str, success: bool):
        """Log security audit events"""
        audit_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': getattr(g, 'current_user_id', 'anonymous'),
            'tenant_id': getattr(g, 'current_tenant', 'default'),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'action': action,
            'resource': resource,
            'success': success,
            'request_id': request.headers.get('X-Request-ID')
        }
        
        logger.info(f"Security audit: {audit_data}")

# Global security instances
security = EnterpriseSecurity()
mfa_service = MFAService()
sso_service = SSOService()
rbac = RoleBasedAccessControl()
security_middleware = SecurityMiddleware()

# Security decorators
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = security_middleware.authenticate_request(request)
        if not payload:
            return {'error': 'Authentication required'}, 401
        
        # Rate limiting check
        if not security_middleware.rate_limit_check(request, payload['user_id']):
            return {'error': 'Rate limit exceeded'}, 429
        
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_roles = getattr(g, 'user_roles', [])
            if not rbac.has_permission(user_roles, permission):
                security_middleware.audit_log(request, 'permission_denied', permission, False)
                return {'error': 'Permission denied'}, 403
            
            security_middleware.audit_log(request, 'permission_granted', permission, True)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role: str):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_roles = getattr(g, 'user_roles', [])
            if role not in user_roles:
                security_middleware.audit_log(request, 'role_denied', role, False)
                return {'error': 'Role required'}, 403
            
            security_middleware.audit_log(request, 'role_granted', role, True)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Security utilities
def get_current_user_id() -> Optional[str]:
    """Get current user ID from request context"""
    return getattr(g, 'current_user_id', None)

def get_current_user_roles() -> List[str]:
    """Get current user roles from request context"""
    return getattr(g, 'user_roles', [])

def get_current_user_permissions() -> List[str]:
    """Get current user permissions from request context"""
    return getattr(g, 'user_permissions', [])

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return get_current_user_id() is not None

def has_permission(permission: str) -> bool:
    """Check if current user has permission"""
    user_roles = get_current_user_roles()
    return rbac.has_permission(user_roles, permission)
