"""
Automatic Tenant-Aware Query Filtering
Prevents security issues by automatically adding tenant_id filter to all queries
"""

from flask import g
from sqlalchemy.orm import Query
from sqlalchemy import event
from app import db
from modules.core.tenant_helpers import get_current_user_tenant_id
import logging

logger = logging.getLogger(__name__)


class TenantAwareQuery(Query):
    """
    Custom Query class that automatically filters by tenant_id
    This prevents developers from forgetting to add tenant filtering
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_id = None
    
    def _apply_tenant_filter(self):
        """Automatically apply tenant_id filter if model has tenant_id column"""
        if self._tenant_id is None:
            # Get tenant_id from current user
            self._tenant_id = get_current_user_tenant_id()
        
        # Check if the model has a tenant_id column
        if hasattr(self.column_descriptions[0]['entity'], 'tenant_id') if self.column_descriptions else False:
            if self._tenant_id:
                # Automatically filter by tenant_id
                model_class = self.column_descriptions[0]['entity']
                return self.filter(model_class.tenant_id == self._tenant_id)
        
        return self
    
    def all(self):
        """Override all() to apply tenant filter"""
        self = self._apply_tenant_filter()
        return super().all()
    
    def first(self):
        """Override first() to apply tenant filter"""
        self = self._apply_tenant_filter()
        return super().first()
    
    def one(self):
        """Override one() to apply tenant filter"""
        self = self._apply_tenant_filter()
        return super().one()
    
    def one_or_none(self):
        """Override one_or_none() to apply tenant filter"""
        self = self._apply_tenant_filter()
        return super().one_or_none()
    
    def count(self):
        """Override count() to apply tenant filter"""
        self = self._apply_tenant_filter()
        return super().count()
    
    def get(self, ident):
        """Override get() - still need tenant check"""
        result = super().get(ident)
        if result and hasattr(result, 'tenant_id'):
            tenant_id = get_current_user_tenant_id()
            if tenant_id and result.tenant_id != tenant_id:
                logger.warning(f"Access denied: User tried to access {result.__class__.__name__} {ident} from different tenant")
                return None
        return result


class TenantAwareBase(db.Model):
    """
    Base model class for tenant-aware models
    Automatically uses TenantAwareQuery for all queries
    """
    __abstract__ = True
    
    tenant_id = db.Column(db.String(50), nullable=True, index=True)
    
    # Use custom query class
    query_class = TenantAwareQuery
    
    def __init__(self, **kwargs):
        # Automatically set tenant_id if not provided
        if 'tenant_id' not in kwargs:
            tenant_id = get_current_user_tenant_id()
            if tenant_id:
                kwargs['tenant_id'] = tenant_id
        super().__init__(**kwargs)
    
    def save(self):
        """Save with automatic tenant_id assignment"""
        if not self.tenant_id:
            tenant_id = get_current_user_tenant_id()
            if tenant_id:
                self.tenant_id = tenant_id
        db.session.add(self)
        db.session.commit()
        return self


def get_tenant_aware_query(model_class, tenant_id=None):
    """
    Helper function to get a tenant-aware query
    Usage: query = get_tenant_aware_query(User)
    """
    if tenant_id is None:
        tenant_id = get_current_user_tenant_id()
    
    if tenant_id and hasattr(model_class, 'tenant_id'):
        return model_class.query.filter_by(tenant_id=tenant_id)
    else:
        return model_class.query


def require_tenant_in_query(query, model_class, tenant_id=None):
    """
    Decorator/helper to ensure tenant_id is in query
    Usage: query = require_tenant_in_query(User.query, User)
    """
    if tenant_id is None:
        tenant_id = get_current_user_tenant_id()
    
    if tenant_id and hasattr(model_class, 'tenant_id'):
        return query.filter(model_class.tenant_id == tenant_id)
    
    return query

