from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class SecurityPolicy(db.Model):
    """
    Security policies configuration
    """
    __tablename__ = 'security_policies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Password policy settings
    password_min_length = Column(Integer, default=8)
    password_require_uppercase = Column(Boolean, default=True)
    password_require_lowercase = Column(Boolean, default=True)
    password_require_numbers = Column(Boolean, default=True)
    password_require_special = Column(Boolean, default=False)
    password_expiry_days = Column(Integer, default=90)
    
    # Login policy settings
    max_login_attempts = Column(Integer, default=5)
    lockout_duration_minutes = Column(Integer, default=30)
    
    # Session policy settings
    session_timeout_minutes = Column(Integer, default=60)
    
    # 2FA settings
    require_2fa = Column(Boolean, default=False)
    
    # Policy status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # Removed ForeignKey to avoid circular import issues
    
    # Relationships removed to avoid circular import issues
    # creator = relationship("User", backref="created_policies")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'password_min_length': self.password_min_length,
            'password_require_uppercase': self.password_require_uppercase,
            'password_require_lowercase': self.password_require_lowercase,
            'password_require_numbers': self.password_require_numbers,
            'password_require_special': self.password_require_special,
            'password_expiry_days': self.password_expiry_days,
            'max_login_attempts': self.max_login_attempts,
            'lockout_duration_minutes': self.lockout_duration_minutes,
            'session_timeout_minutes': self.session_timeout_minutes,
            'require_2fa': self.require_2fa,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

class PasswordHistory(db.Model):
    """
    Track password history for password reuse prevention
    """
    __tablename__ = 'password_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Removed ForeignKey to avoid circular import issues
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", backref="password_history")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserSession(db.Model):
    """
    Track active user sessions
    """
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Removed ForeignKey to avoid circular import issues
    session_id = Column(String(100), nullable=False, unique=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Session management
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Session metadata
    login_method = Column(String(50), default='password')  # password, 2fa, sso, etc.
    device_info = Column(JSON, nullable=True)
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", backref="sessions")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'login_method': self.login_method,
            'device_info': self.device_info
        }

class AccountLockout(db.Model):
    """
    Track account lockout events
    """
    __tablename__ = 'account_lockouts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Removed ForeignKey to avoid circular import issues
    locked_at = Column(DateTime, default=datetime.utcnow)
    unlock_at = Column(DateTime, nullable=True)
    reason = Column(String(200), nullable=False)  # failed_attempts, admin_lock, etc.
    ip_address = Column(String(45), nullable=True)
    
    # Lockout details
    failed_attempts = Column(Integer, default=0)
    is_permanent = Column(Boolean, default=False)
    unlocked_by = Column(Integer, nullable=True)  # Removed ForeignKey to avoid circular import issues
    unlocked_at = Column(DateTime, nullable=True)
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", foreign_keys=[user_id], backref="lockouts")
    # unlocked_by_user = relationship("User", foreign_keys=[unlocked_by], backref="unlocked_accounts")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'unlock_at': self.unlock_at.isoformat() if self.unlock_at else None,
            'reason': self.reason,
            'ip_address': self.ip_address,
            'failed_attempts': self.failed_attempts,
            'is_permanent': self.is_permanent,
            'unlocked_by': self.unlocked_by,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None
        }

class TwoFactorAuth(db.Model):
    """
    Two-factor authentication settings and tokens
    """
    __tablename__ = 'two_factor_auth'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)  # Removed ForeignKey to avoid circular import issues
    is_enabled = Column(Boolean, default=False)
    
    # TOTP settings
    secret_key = Column(String(255), nullable=True)  # Encrypted TOTP secret
    backup_codes = Column(JSON, nullable=True)  # Backup codes for recovery
    
    # SMS settings (if implemented)
    phone_number = Column(String(20), nullable=True)
    sms_enabled = Column(Boolean, default=False)
    
    # Email settings
    email_enabled = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", backref="two_factor_auth")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_enabled': self.is_enabled,
            'backup_codes': self.backup_codes,
            'phone_number': self.phone_number,
            'sms_enabled': self.sms_enabled,
            'email_enabled': self.email_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }

class SecurityEvent(db.Model):
    """
    Track security-related events
    """
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False)  # PASSWORD_CHANGE, LOGIN_FAILED, etc.
    severity = Column(String(20), nullable=False, default='INFO')  # INFO, WARNING, ERROR, CRITICAL
    
    # Event details
    user_id = Column(Integer, nullable=True)  # Removed ForeignKey to avoid circular import issues
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Event data
    event_data = Column(JSON, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, nullable=True)  # Removed ForeignKey to avoid circular import issues
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships removed to avoid circular import issues
    # user = relationship("User", foreign_keys=[user_id], backref="security_events")
    # resolver = relationship("User", foreign_keys=[resolved_by], backref="resolved_security_events")
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'severity': self.severity,
            'user_id': self.user_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'event_data': self.event_data,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
