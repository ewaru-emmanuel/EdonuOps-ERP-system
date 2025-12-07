"""
Tenant-Aware SQL Query Helper
Wraps direct SQL queries to ensure tenant_id filtering
"""

from flask import g
from sqlalchemy import text
from app import db
from modules.core.tenant_helpers import get_current_user_tenant_id
import logging

logger = logging.getLogger(__name__)


def tenant_sql_query(sql_template, params=None, tenant_id=None):
    """
    Execute SQL query with automatic tenant_id filtering
    
    Usage:
        # Instead of:
        # db.session.execute(text("SELECT * FROM contacts WHERE type = 'customer' AND tenant_id = :tenant_id"), {'tenant_id': tenant_id})
        
        # Use:
        result = tenant_sql_query(
            "SELECT * FROM contacts WHERE type = 'customer' AND tenant_id = :tenant_id",
            {}
        )
    
    Args:
        sql_template: SQL query string with :tenant_id placeholder
        params: Dictionary of parameters (tenant_id will be added automatically)
        tenant_id: Optional specific tenant_id (defaults to current user's tenant)
    
    Returns:
        SQLAlchemy result object
    """
    if tenant_id is None:
        tenant_id = get_current_user_tenant_id()
    
    if not tenant_id:
        logger.error("SECURITY RISK: No tenant_id available for SQL query!")
        raise ValueError(
            "SECURITY VIOLATION: Cannot execute tenant-specific SQL query without tenant_id. "
            "This would expose data from all tenants. User must be authenticated and have a tenant_id."
        )
    
    # Ensure params dict exists
    if params is None:
        params = {}
    
    # Add tenant_id to params if not already present
    if 'tenant_id' not in params:
        params['tenant_id'] = tenant_id
    
    # Verify SQL includes tenant_id filter
    sql_lower = sql_template.lower()
    if 'tenant_id' not in sql_lower and ':tenant_id' not in sql_lower:
        logger.warning(f"SQL query may not filter by tenant_id: {sql_template[:100]}...")
        # Don't raise exception for system queries, but log warning
    
    return db.session.execute(text(sql_template), params)


def tenant_sql_scalar(sql_template, params=None, tenant_id=None):
    """
    Execute SQL query and return scalar result
    
    Usage:
        count = tenant_sql_scalar(
            "SELECT COUNT(*) FROM contacts WHERE type = 'customer' AND tenant_id = :tenant_id"
        )
    """
    result = tenant_sql_query(sql_template, params, tenant_id)
    return result.scalar()


def tenant_sql_fetchone(sql_template, params=None, tenant_id=None):
    """
    Execute SQL query and return one row
    
    Usage:
        row = tenant_sql_fetchone(
            "SELECT * FROM contacts WHERE id = :id AND tenant_id = :tenant_id",
            {'id': contact_id}
        )
    """
    result = tenant_sql_query(sql_template, params, tenant_id)
    return result.fetchone()


def tenant_sql_fetchall(sql_template, params=None, tenant_id=None):
    """
    Execute SQL query and return all rows
    
    Usage:
        rows = tenant_sql_fetchall(
            "SELECT * FROM contacts WHERE type = 'customer' AND tenant_id = :tenant_id"
        )
    """
    result = tenant_sql_query(sql_template, params, tenant_id)
    return result.fetchall()


def safe_sql_query(sql_template, params=None):
    """
    For system queries that don't need tenant filtering
    (e.g., CURRENT_TIMESTAMP, cleanup functions)
    
    Usage:
        timestamp = safe_sql_query("SELECT CURRENT_TIMESTAMP").scalar()
    """
    if params is None:
        params = {}
    return db.session.execute(text(sql_template), params)

