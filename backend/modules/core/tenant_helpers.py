"""
Tenant Isolation Helpers
Provides utilities for extracting tenant context and enforcing tenant isolation
"""

from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from modules.core.models import User
import logging

logger = logging.getLogger(__name__)

def get_current_user_id():
    """
    Get current user ID from verified JWT token.
    
    SECURITY: For finance applications, this ONLY accepts JWT tokens.
    No header fallbacks are allowed - this prevents authentication bypass vulnerabilities.
    
    This function requires that @jwt_required() has been called on the route.
    """
    try:
        # SECURITY: Only get user ID from verified JWT token
        # The route must have @jwt_required() decorator for this to work
        user_id = get_jwt_identity()
        if user_id:
            return int(user_id)
    except Exception as e:
        logger.warning(f"Failed to get user ID from JWT: {e}")
        # No fallback - JWT is required for security
        return None
    
    return None

def get_current_user_tenant_id():
    """
    Get current user's tenant_id for strict tenant isolation.
    Returns None if user not found or tenant_id not set.
    """
    user_id = get_current_user_id()
    if not user_id:
        logger.warning("No user ID found - cannot determine tenant")
        return None
    
    try:
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return None
        
        # Get tenant_id from user
        tenant_id = getattr(user, 'tenant_id', None)
        if tenant_id:
            logger.debug(f"User {user_id} belongs to tenant {tenant_id}")
            return tenant_id
        else:
            logger.warning(f"User {user_id} has no tenant_id assigned")
            return None
            
    except Exception as e:
        logger.error(f"Error getting tenant_id for user {user_id}: {e}")
        return None

def require_tenant_context():
    """
    Ensure current user has a tenant_id.
    Returns (user_id, tenant_id) or (None, None) if not available.
    """
    user_id = get_current_user_id()
    if not user_id:
        return None, None
    
    tenant_id = get_current_user_tenant_id()
    if not tenant_id:
        logger.warning(f"User {user_id} has no tenant context")
        return user_id, None
    
    return user_id, tenant_id

