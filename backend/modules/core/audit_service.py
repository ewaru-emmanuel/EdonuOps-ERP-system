# backend/modules/core/audit_service.py

from app import db
from modules.core.audit_models import AuditLog, TenantUsageStats, PlatformMetrics
from flask import request, g
from datetime import datetime, date
import json
import logging

class AuditService:
    """Centralized audit logging service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_action(self, action, resource, resource_id=None, details=None, severity='INFO', module=None):
        """Log an action to the audit trail"""
        try:
            # Extract context from Flask request and g
            tenant_id = getattr(g, 'tenant_id', None)
            user_id = getattr(g, 'user_id', None)
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            # Create audit log entry
            audit_entry = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=str(resource_id) if resource_id else None,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                module=module,
                severity=severity
            )
            
            db.session.add(audit_entry)
            db.session.commit()
            
            self.logger.info(f"Audit logged: {action} on {resource} by user {user_id} in tenant {tenant_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to log audit action: {str(e)}")
            db.session.rollback()
    
    def log_user_action(self, user_id, action, resource, resource_id=None, details=None):
        """Log a user-specific action"""
        self.log_action(action, resource, resource_id, details, 'INFO', 'user')
    
    def log_tenant_action(self, tenant_id, action, resource, resource_id=None, details=None):
        """Log a tenant-specific action"""
        self.log_action(action, resource, resource_id, details, 'INFO', 'tenant')
    
    def log_module_action(self, module, action, resource, resource_id=None, details=None):
        """Log a module-specific action"""
        self.log_action(action, resource, resource_id, details, 'INFO', module)
    
    def log_error(self, action, resource, error_message, resource_id=None, details=None):
        """Log an error"""
        error_details = {
            'error_message': str(error_message),
            'details': details
        }
        self.log_action(action, resource, resource_id, error_details, 'ERROR')
    
    def log_security_event(self, action, resource, details=None):
        """Log a security-related event"""
        self.log_action(action, resource, details=details, severity='WARNING', module='security')
    
    def get_tenant_audit_logs(self, tenant_id, limit=100, offset=0):
        """Get audit logs for a specific tenant"""
        return AuditLog.query.filter_by(tenant_id=tenant_id)\
                           .order_by(AuditLog.timestamp.desc())\
                           .limit(limit)\
                           .offset(offset)\
                           .all()
    
    def get_user_audit_logs(self, user_id, limit=100, offset=0):
        """Get audit logs for a specific user"""
        return AuditLog.query.filter_by(user_id=user_id)\
                           .order_by(AuditLog.timestamp.desc())\
                           .limit(limit)\
                           .offset(offset)\
                           .all()
    
    def get_audit_logs_by_action(self, action, limit=100, offset=0):
        """Get audit logs for a specific action"""
        return AuditLog.query.filter_by(action=action)\
                           .order_by(AuditLog.timestamp.desc())\
                           .limit(limit)\
                           .offset(offset)\
                           .all()
    
    def get_recent_errors(self, limit=50):
        """Get recent error logs"""
        return AuditLog.query.filter(AuditLog.severity.in_(['ERROR', 'CRITICAL']))\
                           .order_by(AuditLog.timestamp.desc())\
                           .limit(limit)\
                           .all()
    
    def update_tenant_usage_stats(self, tenant_id, active_users=None, api_calls=None, storage_mb=None, modules_used=None, errors_count=None):
        """Update daily usage statistics for a tenant"""
        try:
            today = date.today()
            
            # Get or create today's stats
            stats = TenantUsageStats.query.filter_by(tenant_id=tenant_id, date=today).first()
            if not stats:
                stats = TenantUsageStats(tenant_id=tenant_id, date=today)
                db.session.add(stats)
            
            # Update stats
            if active_users is not None:
                stats.active_users = active_users
            if api_calls is not None:
                stats.api_calls += api_calls  # Increment API calls
            if storage_mb is not None:
                stats.storage_used_mb = storage_mb
            if modules_used is not None:
                stats.modules_used = json.dumps(modules_used)
            if errors_count is not None:
                stats.errors_count += errors_count  # Increment error count
            
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to update tenant usage stats: {str(e)}")
            db.session.rollback()
    
    def update_platform_metrics(self):
        """Update platform-wide metrics"""
        try:
            today = date.today()
            
            # Get or create today's metrics
            metrics = PlatformMetrics.query.filter_by(date=today).first()
            if not metrics:
                metrics = PlatformMetrics(date=today)
                db.session.add(metrics)
            
            # Calculate platform-wide stats
            from modules.core.tenant_models import Tenant, UserTenant
            from modules.core.models import User
            
            # Total tenants
            metrics.total_tenants = Tenant.query.count()
            
            # Active tenants (with activity in last 30 days)
            thirty_days_ago = datetime.utcnow().replace(day=datetime.utcnow().day - 30)
            active_tenants = db.session.query(Tenant.id).join(AuditLog, Tenant.id == AuditLog.tenant_id)\
                .filter(AuditLog.timestamp >= thirty_days_ago)\
                .distinct().count()
            metrics.active_tenants = active_tenants
            
            # Total users
            metrics.total_users = User.query.count()
            
            # Total API calls today
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            metrics.total_api_calls = AuditLog.query.filter(
                AuditLog.timestamp >= today_start,
                AuditLog.timestamp <= today_end
            ).count()
            
            # Error rate
            total_actions = AuditLog.query.filter(
                AuditLog.timestamp >= today_start,
                AuditLog.timestamp <= today_end
            ).count()
            error_actions = AuditLog.query.filter(
                AuditLog.timestamp >= today_start,
                AuditLog.timestamp <= today_end,
                AuditLog.severity.in_(['ERROR', 'CRITICAL'])
            ).count()
            metrics.error_rate = (error_actions / total_actions * 100) if total_actions > 0 else 0
            
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to update platform metrics: {str(e)}")
            db.session.rollback()

# Global audit service instance
audit_service = AuditService()












