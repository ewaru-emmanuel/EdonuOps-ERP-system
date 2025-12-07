"""
Simple Tenant Query Helper
Automatically enforces tenant_id filtering to prevent security issues
"""

from flask import g
from modules.core.tenant_helpers import get_current_user_tenant_id
from app import db
import logging

logger = logging.getLogger(__name__)


def tenant_query(model_class, tenant_id=None):
    """
    Get a query automatically filtered by tenant_id
    
    Usage:
        # Instead of: User.query.filter_by(tenant_id=tenant_id).all()
        # Use: tenant_query(User).all()
        
        users = tenant_query(User).all()
        account = tenant_query(Account, tenant_id="specific_tenant").first()
    """
    if tenant_id is None:
        tenant_id = get_current_user_tenant_id()
    
    if not tenant_id:
        logger.error("SECURITY RISK: No tenant_id available - refusing to return unfiltered query!")
        # SECURITY: Raise exception to prevent data leak
        raise ValueError(
            "SECURITY VIOLATION: Cannot query tenant-specific data without tenant_id. "
            "This would expose data from all tenants. User must be authenticated and have a tenant_id."
        )
    
    if not hasattr(model_class, 'tenant_id'):
        logger.warning(f"{model_class.__name__} does not have tenant_id column")
        return model_class.query
    
    return model_class.query.filter_by(tenant_id=tenant_id)


def get_user_role_in_tenant(user_id, tenant_id=None):
    """
    Get user's role in a specific tenant (for many-to-many)
    
    Usage:
        role = get_user_role_in_tenant(user_id=5, tenant_id="tenant_123")
        # Returns: 'admin', 'manager', 'user', 'viewer', or None
    """
    from modules.core.tenant_models import UserTenant
    
    if tenant_id is None:
        tenant_id = get_current_user_tenant_id()
    
    if not tenant_id:
        return None
    
    user_tenant = UserTenant.query.filter_by(
        user_id=str(user_id),
        tenant_id=tenant_id
    ).first()
    
    if user_tenant:
        return user_tenant.role
    
    return None


def require_role_in_tenant(required_role, user_id=None, tenant_id=None):
    """
    Check if user has required role in tenant
    
    Usage:
        if not require_role_in_tenant('admin'):
            return jsonify({'error': 'Admin access required'}), 403
    """
    from modules.core.tenant_helpers import get_current_user_id
    
    if user_id is None:
        user_id = get_current_user_id()
    
    if tenant_id is None:
        tenant_id = get_current_user_tenant_id()
    
    if not user_id or not tenant_id:
        return False
    
    user_role = get_user_role_in_tenant(user_id, tenant_id)
    
    if not user_role:
        return False
    
    # Role hierarchy: superadmin > admin > manager > user > viewer
    role_hierarchy = {
        'superadmin': 5,
        'admin': 4,
        'manager': 3,
        'user': 2,
        'viewer': 1
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level

