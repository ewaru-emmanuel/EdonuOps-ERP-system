"""
Security Helper Functions
Provides utilities for BOLA protection, input validation, and security checks
"""

from flask import request, jsonify, g
from flask_jwt_extended import get_jwt_identity
from app import db
from modules.core.models import User
from modules.core.tenant_helpers import get_current_user_tenant_id
import logging

logger = logging.getLogger(__name__)


def verify_user_owns_resource(resource, user_id=None):
    """
    Verify that the current user owns or has access to a resource.
    This prevents Broken Object Level Authorization (BOLA) attacks.
    
    Args:
        resource: Database model instance with tenant_id or user_id attribute
        user_id: Optional user ID to check (defaults to current user from JWT)
    
    Returns:
        tuple: (is_authorized: bool, error_message: str or None)
    """
    if not resource:
        return False, "Resource not found"
    
    if user_id is None:
        user_id = get_jwt_identity()
        if not user_id:
            return False, "Authentication required"
    
    # Check tenant isolation
    user_tenant_id = get_current_user_tenant_id()
    if hasattr(resource, 'tenant_id') and resource.tenant_id:
        if resource.tenant_id != user_tenant_id:
            logger.warning(
                f"BOLA attempt blocked: User {user_id} tried to access resource "
                f"from tenant {resource.tenant_id} (user's tenant: {user_tenant_id})"
            )
            return False, "Access denied: Resource belongs to different tenant"
    
    # Check user ownership (if resource has created_by or user_id)
    if hasattr(resource, 'created_by') and resource.created_by:
        if resource.created_by != int(user_id):
            # Check if user has admin role (admins can access all resources in their tenant)
            user = User.query.get(user_id)
            if not (user and user.role and user.role.role_name == 'admin'):
                logger.warning(
                    f"BOLA attempt blocked: User {user_id} tried to access resource "
                    f"created by user {resource.created_by}"
                )
                return False, "Access denied: Resource belongs to another user"
    
    if hasattr(resource, 'user_id') and resource.user_id:
        if resource.user_id != int(user_id):
            user = User.query.get(user_id)
            if not (user and user.role and user.role.role_name == 'admin'):
                logger.warning(
                    f"BOLA attempt blocked: User {user_id} tried to access resource "
                    f"belonging to user {resource.user_id}"
                )
                return False, "Access denied: Resource belongs to another user"
    
    return True, None


def verify_tenant_access(tenant_id, user_id=None):
    """
    Verify that the current user has access to a specific tenant.
    
    Args:
        tenant_id: Tenant ID to check access for
        user_id: Optional user ID to check (defaults to current user from JWT)
    
    Returns:
        tuple: (is_authorized: bool, error_message: str or None)
    """
    if user_id is None:
        user_id = get_jwt_identity()
        if not user_id:
            return False, "Authentication required"
    
    user_tenant_id = get_current_user_tenant_id()
    
    if tenant_id != user_tenant_id:
        logger.warning(
            f"Tenant access denied: User {user_id} tried to access tenant {tenant_id} "
            f"(user's tenant: {user_tenant_id})"
        )
        return False, "Access denied: Tenant access not authorized"
    
    return True, None


def require_resource_ownership(resource):
    """
    Decorator helper to require resource ownership.
    Use this in route handlers to automatically check BOLA.
    
    Example:
        @require_permission('finance.accounts.read')
        def get_account(account_id):
            account = Account.query.get(account_id)
            if not account:
                return jsonify({'error': 'Account not found'}), 404
            
            authorized, error = require_resource_ownership(account)
            if not authorized:
                return jsonify({'error': error}), 403
            
            return jsonify(account.to_dict())
    """
    authorized, error = verify_user_owns_resource(resource)
    if not authorized:
        return False, error
    return True, None


def sanitize_input(value, input_type='string'):
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        value: Input value to sanitize
        input_type: Type of input ('string', 'integer', 'float', 'email', 'url')
    
    Returns:
        Sanitized value or None if invalid
    """
    if value is None:
        return None
    
    if input_type == 'string':
        # Remove null bytes, trim whitespace
        value = str(value).replace('\x00', '').strip()
        # Limit length (prevent DoS)
        if len(value) > 10000:
            return None
        return value
    
    elif input_type == 'integer':
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    elif input_type == 'float':
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    elif input_type == 'email':
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        value = str(value).strip().lower()
        if re.match(email_pattern, value):
            return value
        return None
    
    elif input_type == 'url':
        import re
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        value = str(value).strip()
        if re.match(url_pattern, value):
            return value
        return None
    
    return None


def validate_request_data(required_fields, optional_fields=None):
    """
    Validate and sanitize request JSON data.
    
    Args:
        required_fields: Dict of {field_name: input_type}
        optional_fields: Dict of {field_name: input_type}
    
    Returns:
        tuple: (validated_data: dict, errors: list)
    """
    data = request.get_json()
    if not data:
        return None, ["Request body is required"]
    
    validated = {}
    errors = []
    
    # Validate required fields
    for field, input_type in required_fields.items():
        if field not in data:
            errors.append(f"Required field '{field}' is missing")
        else:
            sanitized = sanitize_input(data[field], input_type)
            if sanitized is None:
                errors.append(f"Invalid value for field '{field}'")
            else:
                validated[field] = sanitized
    
    # Validate optional fields
    if optional_fields:
        for field, input_type in optional_fields.items():
            if field in data:
                sanitized = sanitize_input(data[field], input_type)
                if sanitized is not None:
                    validated[field] = sanitized
    
    if errors:
        return None, errors
    
    return validated, []


def log_security_event(event_type, user_id, details, severity='INFO', resource_id=None):
    """
    Log security events for audit trail.
    
    Args:
        event_type: Type of event (AUTH_FAILED, BOLA_BLOCKED, SENSITIVE_ACCESS, etc.)
        user_id: User ID associated with event
        details: Dict with event details
        severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
        resource_id: Optional resource ID if event is resource-specific
    """
    try:
        from modules.core.audit_models import AuditLog
        from datetime import datetime
        
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            details=details,
            severity=severity,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            resource_id=resource_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Also log to application logger
        log_message = f"Security Event: {event_type} - User: {user_id}, Details: {details}"
        if severity == 'CRITICAL':
            logger.critical(log_message)
        elif severity == 'ERROR':
            logger.error(log_message)
        elif severity == 'WARNING':
            logger.warning(log_message)
        else:
            logger.info(log_message)
            
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

