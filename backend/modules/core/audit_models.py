from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class AuditLog(Base):
    """
    Comprehensive audit trail for all system activities
    """
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # User information  
    user_id = Column(Integer, nullable=True)  # Removed ForeignKey to avoid circular import issues
    username = Column(String(100), nullable=True)  # Redundant for performance
    user_role = Column(String(50), nullable=True)  # Redundant for performance
    
    # Action details
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    entity_type = Column(String(100), nullable=False)  # journal_entry, user, customer, etc.
    entity_id = Column(String(100), nullable=True)  # ID of the affected entity
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_url = Column(String(500), nullable=True)
    
    # Change tracking
    old_values = Column(JSON, nullable=True)  # Previous values
    new_values = Column(JSON, nullable=True)  # New values
    changes_summary = Column(Text, nullable=True)  # Human-readable summary
    
    # Module and context
    module = Column(String(50), nullable=False)  # finance, inventory, sales, etc.
    source = Column(String(100), nullable=True)  # api, ui, batch_job, etc.
    
    # Result and status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Additional metadata
    session_id = Column(String(100), nullable=True)
    correlation_id = Column(String(100), nullable=True)  # For tracking related actions
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", backref="audit_logs", lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id,
            'username': self.username,
            'user_role': self.user_role,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_method': self.request_method,
            'request_url': self.request_url,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'changes_summary': self.changes_summary,
            'module': self.module,
            'source': self.source,
            'success': self.success,
            'error_message': self.error_message,
            'session_id': self.session_id,
            'correlation_id': self.correlation_id
        }

class LoginHistory(Base):
    """
    Detailed login/logout tracking
    """
    __tablename__ = 'login_history'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # User information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    username = Column(String(100), nullable=False)
    
    # Login details
    action = Column(String(20), nullable=False)  # LOGIN, LOGOUT, FAILED_LOGIN
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Success/failure details
    success = Column(Boolean, default=True)
    failure_reason = Column(String(200), nullable=True)  # Wrong password, account locked, etc.
    
    # Security details
    is_suspicious = Column(Boolean, default=False)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", backref="login_history", lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'success': self.success,
            'failure_reason': self.failure_reason,
            'is_suspicious': self.is_suspicious,
            'country': self.country,
            'city': self.city
        }

class PermissionChange(Base):
    """
    Track permission and role changes
    """
    __tablename__ = 'permission_changes'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # User information
    admin_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Who made the change
    target_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Who was affected
    
    # Change details
    change_type = Column(String(50), nullable=False)  # ROLE_ASSIGNED, ROLE_REMOVED, PERMISSION_GRANTED, etc.
    old_role = Column(String(50), nullable=True)
    new_role = Column(String(50), nullable=True)
    permissions_added = Column(JSON, nullable=True)
    permissions_removed = Column(JSON, nullable=True)
    
    # Context
    reason = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Relationships removed to avoid circular import issues
    # admin_user = relationship("User", foreign_keys=[admin_user_id], backref="admin_changes", lazy='select')
    # target_user = relationship("User", foreign_keys=[target_user_id], backref="user_changes", lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'admin_user_id': self.admin_user_id,
            'target_user_id': self.target_user_id,
            'change_type': self.change_type,
            'old_role': self.old_role,
            'new_role': self.new_role,
            'permissions_added': self.permissions_added,
            'permissions_removed': self.permissions_removed,
            'reason': self.reason,
            'ip_address': self.ip_address
        }

class SystemEvent(Base):
    """
    Track system-level events and configuration changes
    """
    __tablename__ = 'system_events'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # CONFIG_CHANGE, BACKUP_CREATED, etc.
    event_category = Column(String(50), nullable=False)  # SYSTEM, SECURITY, CONFIG, etc.
    severity = Column(String(20), nullable=False, default='INFO')  # INFO, WARNING, ERROR, CRITICAL
    
    # User context (if applicable)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    username = Column(String(100), nullable=True)
    
    # Event data
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", backref="system_events", lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'severity': self.severity,
            'user_id': self.user_id,
            'username': self.username,
            'description': self.description,
            'details': self.details,
            'ip_address': self.ip_address
        }
