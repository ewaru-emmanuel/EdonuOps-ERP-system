# backend/modules/core/audit_models.py

from app import db
from datetime import datetime
import uuid

class AuditLog(db.Model):
    """Global audit logging for all tenant activities"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource = db.Column(db.String(100), nullable=False)  # user, tenant, finance, inventory, etc.
    resource_id = db.Column(db.String(100), nullable=True)  # ID of the affected resource
    details = db.Column(db.Text, nullable=True)  # JSON string with additional details
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.Text, nullable=True)
    module = db.Column(db.String(50), nullable=True)  # finance, inventory, crm, etc.
    severity = db.Column(db.String(20), default='INFO')  # INFO, WARNING, ERROR, CRITICAL
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_audit_tenant_timestamp', 'tenant_id', 'timestamp'),
        db.Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        db.Index('idx_audit_action_timestamp', 'action', 'timestamp'),
        db.Index('idx_audit_resource', 'resource', 'resource_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'module': self.module,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class TenantUsageStats(db.Model):
    """Track usage statistics per tenant"""
    __tablename__ = 'tenant_usage_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    active_users = db.Column(db.Integer, default=0)
    api_calls = db.Column(db.Integer, default=0)
    storage_used_mb = db.Column(db.Float, default=0.0)
    modules_used = db.Column(db.Text, nullable=True)  # JSON array of modules used
    errors_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint on tenant_id + date
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'date', name='unique_tenant_date'),
        db.Index('idx_usage_tenant_date', 'tenant_id', 'date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'date': self.date.isoformat() if self.date else None,
            'active_users': self.active_users,
            'api_calls': self.api_calls,
            'storage_used_mb': self.storage_used_mb,
            'modules_used': self.modules_used,
            'errors_count': self.errors_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PlatformMetrics(db.Model):
    """Platform-wide metrics for admin dashboard"""
    __tablename__ = 'platform_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_tenants = db.Column(db.Integer, default=0)
    active_tenants = db.Column(db.Integer, default=0)
    total_users = db.Column(db.Integer, default=0)
    total_api_calls = db.Column(db.Integer, default=0)
    total_storage_gb = db.Column(db.Float, default=0.0)
    error_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_tenants': self.total_tenants,
            'active_tenants': self.active_tenants,
            'total_users': self.total_users,
            'total_api_calls': self.total_api_calls,
            'total_storage_gb': self.total_storage_gb,
            'error_rate': self.error_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LoginHistory(db.Model):
    """Track user login history for security"""
    __tablename__ = 'login_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    success = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(100), nullable=True)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_login_user_time', 'user_id', 'login_time'),
        db.Index('idx_login_ip', 'ip_address'),
        db.Index('idx_login_tenant', 'tenant_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'failure_reason': self.failure_reason,
            'tenant_id': self.tenant_id
        }

class PermissionChange(db.Model):
    """Track permission changes for audit"""
    __tablename__ = 'permission_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.Boolean, nullable=True)
    new_value = db.Column(db.Boolean, nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_permission_user', 'user_id'),
        db.Index('idx_permission_changed_by', 'changed_by'),
        db.Index('idx_permission_tenant', 'tenant_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'changed_by': self.changed_by,
            'permission': self.permission,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'reason': self.reason,
            'tenant_id': self.tenant_id
        }

class SystemEvent(db.Model):
    """Track system events for monitoring"""
    __tablename__ = 'system_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), default='INFO')
    source = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=True)
    event_metadata = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_system_event_type', 'event_type'),
        db.Index('idx_system_event_severity', 'severity'),
        db.Index('idx_system_event_tenant', 'tenant_id'),
        db.Index('idx_system_event_created', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_name': self.event_name,
            'description': self.description,
            'severity': self.severity,
            'source': self.source,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'event_metadata': self.event_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }