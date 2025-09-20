import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import request, g
from sqlalchemy import desc, and_, or_
from app import db
from modules.core.audit_models import AuditLog, LoginHistory, PermissionChange, SystemEvent

class AuditLoggerService:
    """
    Enhanced audit logging service with comprehensive tracking
    """
    
    @staticmethod
    def get_request_context():
        """Extract request context information"""
        context = {
            'ip_address': None,
            'user_agent': None,
            'request_method': None,
            'request_url': None,
            'session_id': None
        }
        
        try:
            if request:
                # Get IP address (handle proxies)
                context['ip_address'] = (
                    request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
                    request.environ.get('HTTP_X_REAL_IP', '') or
                    request.remote_addr
                )
                
                context['user_agent'] = request.environ.get('HTTP_USER_AGENT', '')
                context['request_method'] = request.method
                context['request_url'] = request.url
                context['session_id'] = request.environ.get('SESSION_ID')
        except:
            pass
            
        return context
    
    @staticmethod
    def get_user_context(user_id: Optional[int] = None):
        """Extract user context information"""
        user_context = {
            'user_id': None,
            'username': None,
            'user_role': None
        }
        
        try:
            if user_id:
                from modules.core.models import User
                user = User.query.get(user_id)
                if user:
                    user_context['user_id'] = user.id
                    user_context['username'] = user.username
                    user_context['user_role'] = user.role.role_name if user.role else None
            elif hasattr(g, 'current_user') and g.current_user:
                user_context['user_id'] = g.current_user.id
                user_context['username'] = g.current_user.username
                user_context['user_role'] = g.current_user.role.role_name if g.current_user.role else None
        except:
            pass
            
        return user_context
    
    @classmethod
    def log_action(cls, 
                   action: str,
                   entity_type: str,
                   entity_id: Optional[str] = None,
                   old_values: Optional[Dict] = None,
                   new_values: Optional[Dict] = None,
                   module: str = 'general',
                   source: str = 'api',
                   success: bool = True,
                   error_message: Optional[str] = None,
                   changes_summary: Optional[str] = None,
                   user_id: Optional[int] = None,
                   correlation_id: Optional[str] = None):
        """
        Log a general action to the audit trail
        """
        try:
            request_context = cls.get_request_context()
            user_context = cls.get_user_context(user_id)
            
            # Generate changes summary if not provided
            if not changes_summary and old_values and new_values:
                changes_summary = cls._generate_changes_summary(old_values, new_values)
            
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                user_id=user_context['user_id'],
                username=user_context['username'],
                user_role=user_context['user_role'],
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                ip_address=request_context['ip_address'],
                user_agent=request_context['user_agent'],
                request_method=request_context['request_method'],
                request_url=request_context['request_url'],
                old_values=old_values,
                new_values=new_values,
                changes_summary=changes_summary,
                module=module,
                source=source,
                success=success,
                error_message=error_message,
                session_id=request_context['session_id'],
                correlation_id=correlation_id
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            return audit_log.id
            
        except Exception as e:
            print(f"Audit logging error: {str(e)}")
            db.session.rollback()
            return None
    
    @classmethod
    def log_login(cls, 
                  user_id: int,
                  username: str,
                  action: str = 'LOGIN',
                  success: bool = True,
                  failure_reason: Optional[str] = None,
                  is_suspicious: bool = False):
        """
        Log login/logout events
        """
        try:
            request_context = cls.get_request_context()
            
            login_history = LoginHistory(
                timestamp=datetime.utcnow(),
                user_id=user_id,
                username=username,
                action=action,
                ip_address=request_context['ip_address'],
                user_agent=request_context['user_agent'],
                session_id=request_context['session_id'],
                success=success,
                failure_reason=failure_reason,
                is_suspicious=is_suspicious
            )
            
            db.session.add(login_history)
            db.session.commit()
            
            return login_history.id
            
        except Exception as e:
            print(f"Login logging error: {str(e)}")
            db.session.rollback()
            return None
    
    @classmethod
    def log_permission_change(cls,
                             admin_user_id: int,
                             target_user_id: int,
                             change_type: str,
                             old_role: Optional[str] = None,
                             new_role: Optional[str] = None,
                             permissions_added: Optional[List] = None,
                             permissions_removed: Optional[List] = None,
                             reason: Optional[str] = None):
        """
        Log permission and role changes
        """
        try:
            request_context = cls.get_request_context()
            
            permission_change = PermissionChange(
                timestamp=datetime.utcnow(),
                admin_user_id=admin_user_id,
                target_user_id=target_user_id,
                change_type=change_type,
                old_role=old_role,
                new_role=new_role,
                permissions_added=permissions_added,
                permissions_removed=permissions_removed,
                reason=reason,
                ip_address=request_context['ip_address']
            )
            
            db.session.add(permission_change)
            db.session.commit()
            
            return permission_change.id
            
        except Exception as e:
            print(f"Permission change logging error: {str(e)}")
            db.session.rollback()
            return None
    
    @classmethod
    def log_system_event(cls,
                        event_type: str,
                        event_category: str,
                        description: str,
                        severity: str = 'INFO',
                        details: Optional[Dict] = None,
                        user_id: Optional[int] = None):
        """
        Log system-level events
        """
        try:
            request_context = cls.get_request_context()
            user_context = cls.get_user_context(user_id)
            
            system_event = SystemEvent(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                event_category=event_category,
                severity=severity,
                user_id=user_context['user_id'],
                username=user_context['username'],
                description=description,
                details=details,
                ip_address=request_context['ip_address']
            )
            
            db.session.add(system_event)
            db.session.commit()
            
            return system_event.id
            
        except Exception as e:
            print(f"System event logging error: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def _generate_changes_summary(old_values: Dict, new_values: Dict) -> str:
        """Generate human-readable changes summary"""
        changes = []
        
        for key in set(old_values.keys()) | set(new_values.keys()):
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                if old_val is None:
                    changes.append(f"Added {key}: {new_val}")
                elif new_val is None:
                    changes.append(f"Removed {key}: {old_val}")
                else:
                    changes.append(f"Changed {key}: {old_val} → {new_val}")
        
        return "; ".join(changes)
    
    @classmethod
    def get_audit_logs(cls,
                      user_id: Optional[int] = None,
                      module: Optional[str] = None,
                      action: Optional[str] = None,
                      entity_type: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      limit: int = 100,
                      offset: int = 0):
        """
        Retrieve audit logs with filtering
        """
        try:
            query = db.session.query(AuditLog)
            
            # Apply filters
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if module:
                query = query.filter(AuditLog.module == module)
            if action:
                query = query.filter(AuditLog.action == action)
            if entity_type:
                query = query.filter(AuditLog.entity_type == entity_type)
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            # Order by timestamp descending
            query = query.order_by(desc(AuditLog.timestamp))
            
            # Apply pagination
            total_count = query.count()
            logs = query.offset(offset).limit(limit).all()
            
            return {
                'logs': [log.to_dict() for log in logs],
                'total_count': total_count,
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            print(f"Error retrieving audit logs: {str(e)}")
            return {'logs': [], 'total_count': 0, 'offset': offset, 'limit': limit}
    
    @classmethod
    def get_login_history(cls,
                         user_id: Optional[int] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: int = 100,
                         offset: int = 0):
        """
        Retrieve login history with filtering
        """
        try:
            query = db.session.query(LoginHistory)
            
            if user_id:
                query = query.filter(LoginHistory.user_id == user_id)
            if start_date:
                query = query.filter(LoginHistory.timestamp >= start_date)
            if end_date:
                query = query.filter(LoginHistory.timestamp <= end_date)
            
            query = query.order_by(desc(LoginHistory.timestamp))
            
            total_count = query.count()
            logs = query.offset(offset).limit(limit).all()
            
            return {
                'logs': [log.to_dict() for log in logs],
                'total_count': total_count,
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            print(f"Error retrieving login history: {str(e)}")
            return {'logs': [], 'total_count': 0, 'offset': offset, 'limit': limit}
    
    @classmethod
    def get_security_summary(cls, days: int = 30):
        """
        Get security summary for dashboard
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Failed logins
            failed_logins = db.session.query(LoginHistory).filter(
                and_(
                    LoginHistory.timestamp >= cutoff_date,
                    LoginHistory.success == False
                )
            ).count()
            
            # Successful logins
            successful_logins = db.session.query(LoginHistory).filter(
                and_(
                    LoginHistory.timestamp >= cutoff_date,
                    LoginHistory.success == True
                )
            ).count()
            
            # Suspicious activities
            suspicious_activities = db.session.query(LoginHistory).filter(
                and_(
                    LoginHistory.timestamp >= cutoff_date,
                    LoginHistory.is_suspicious == True
                )
            ).count()
            
            # Permission changes
            permission_changes = db.session.query(PermissionChange).filter(
                PermissionChange.timestamp >= cutoff_date
            ).count()
            
            # Recent activity
            recent_activity = db.session.query(AuditLog).filter(
                AuditLog.timestamp >= cutoff_date
            ).count()
            
            return {
                'failed_logins': failed_logins,
                'successful_logins': successful_logins,
                'suspicious_activities': suspicious_activities,
                'permission_changes': permission_changes,
                'recent_activity': recent_activity,
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error generating security summary: {str(e)}")
            return {
                'failed_logins': 0,
                'successful_logins': 0,
                'suspicious_activities': 0,
                'permission_changes': 0,
                'recent_activity': 0,
                'period_days': days
            }

# Create global instance
audit_logger = AuditLoggerService()
