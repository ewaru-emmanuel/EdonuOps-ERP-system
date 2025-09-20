import re
import hashlib
import secrets
import pyotp
import qrcode
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_, or_, desc
from app import db
from modules.core.security_models import (
    SecurityPolicy, PasswordHistory, UserSession, AccountLockout, 
    TwoFactorAuth, SecurityEvent
)
from modules.core.models import User
from services.audit_logger_service import audit_logger

class SecurityService:
    """
    Comprehensive security service for password policies, session management, and 2FA
    """
    
    # Default password policy
    DEFAULT_PASSWORD_POLICY = {
        'min_length': 8,
        'max_length': 128,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_special_chars': True,
        'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
        'prevent_common_passwords': True,
        'prevent_username_in_password': True,
        'prevent_recent_passwords': True,
        'recent_password_count': 5,
        'password_expiry_days': 90,
        'warn_before_expiry_days': 7
    }
    
    # Default session policy
    DEFAULT_SESSION_POLICY = {
        'session_timeout_minutes': 30,
        'max_concurrent_sessions': 3,
        'inactive_timeout_minutes': 15,
        'extend_on_activity': True,
        'require_reauth_for_sensitive': True
    }
    
    # Default login policy
    DEFAULT_LOGIN_POLICY = {
        'max_failed_attempts': 5,
        'lockout_duration_minutes': 30,
        'permanent_lockout_after': 10,
        'track_suspicious_activity': True,
        'require_email_verification': True
    }
    
    @classmethod
    def get_password_policy(cls) -> Dict:
        """Get current password policy"""
        try:
            policy = SecurityPolicy.query.filter_by(
                policy_name='password_policy',
                policy_type='PASSWORD'
            ).first()
            
            if policy:
                return {**cls.DEFAULT_PASSWORD_POLICY, **policy.configuration}
            
            return cls.DEFAULT_PASSWORD_POLICY
        except Exception as e:
            print(f"Error getting password policy: {e}")
            return cls.DEFAULT_PASSWORD_POLICY
    
    @classmethod
    def validate_password(cls, password: str, username: str = None, user_id: int = None) -> Tuple[bool, List[str]]:
        """
        Validate password against security policy
        Returns (is_valid, list_of_errors)
        """
        policy = cls.get_password_policy()
        errors = []
        
        # Length validation
        if len(password) < policy['min_length']:
            errors.append(f"Password must be at least {policy['min_length']} characters long")
        
        if len(password) > policy['max_length']:
            errors.append(f"Password must be no more than {policy['max_length']} characters long")
        
        # Character requirements
        if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy['require_lowercase'] and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy['require_numbers'] and not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one number")
        
        if policy['require_special_chars']:
            special_chars = policy['special_chars']
            if not any(char in password for char in special_chars):
                errors.append(f"Password must contain at least one special character ({special_chars})")
        
        # Prevent username in password
        if policy['prevent_username_in_password'] and username:
            if username.lower() in password.lower():
                errors.append("Password cannot contain your username")
        
        # Check against common passwords
        if policy['prevent_common_passwords']:
            common_passwords = [
                'password', '123456', 'password123', 'admin', 'qwerty',
                'letmein', 'welcome', 'monkey', '1234567890', 'abc123'
            ]
            if password.lower() in common_passwords:
                errors.append("Password is too common and easily guessable")
        
        # Check recent passwords
        if policy['prevent_recent_passwords'] and user_id:
            recent_passwords = cls.get_recent_passwords(user_id, policy['recent_password_count'])
            password_hash = generate_password_hash(password)
            for old_hash in recent_passwords:
                if check_password_hash(old_hash, password):
                    errors.append(f"Cannot reuse any of your last {policy['recent_password_count']} passwords")
                    break
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_recent_passwords(cls, user_id: int, count: int) -> List[str]:
        """Get recent password hashes for a user"""
        try:
            recent_passwords = PasswordHistory.query.filter_by(user_id=user_id)\
                .order_by(desc(PasswordHistory.created_at))\
                .limit(count).all()
            return [pwd.password_hash for pwd in recent_passwords]
        except Exception as e:
            print(f"Error getting recent passwords: {e}")
            return []
    
    @classmethod
    def save_password_to_history(cls, user_id: int, password_hash: str):
        """Save password to history"""
        try:
            password_entry = PasswordHistory(
                user_id=user_id,
                password_hash=password_hash
            )
            db.session.add(password_entry)
            db.session.commit()
        except Exception as e:
            print(f"Error saving password to history: {e}")
            db.session.rollback()
    
    @classmethod
    def create_session(cls, user_id: int, session_id: str, ip_address: str = None, 
                      user_agent: str = None) -> bool:
        """Create a new user session"""
        try:
            # Check session limits
            session_policy = cls.get_session_policy()
            active_sessions = UserSession.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).count()
            
            if active_sessions >= session_policy['max_concurrent_sessions']:
                # Deactivate oldest session
                oldest_session = UserSession.query.filter_by(
                    user_id=user_id, 
                    is_active=True
                ).order_by(UserSession.created_at).first()
                
                if oldest_session:
                    oldest_session.is_active = False
            
            # Create new session
            expires_at = datetime.utcnow() + timedelta(minutes=session_policy['session_timeout_minutes'])
            
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.session.add(session)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Error creating session: {e}")
            db.session.rollback()
            return False
    
    @classmethod
    def update_session_activity(cls, session_id: str) -> bool:
        """Update last activity for a session"""
        try:
            session = UserSession.query.filter_by(session_id=session_id, is_active=True).first()
            if session:
                session.last_activity = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating session activity: {e}")
            return False
    
    @classmethod
    def is_session_valid(cls, session_id: str) -> bool:
        """Check if session is valid and not expired"""
        try:
            session = UserSession.query.filter_by(session_id=session_id, is_active=True).first()
            if not session:
                return False
            
            # Check if session is expired
            if session.expires_at and datetime.utcnow() > session.expires_at:
                session.is_active = False
                db.session.commit()
                return False
            
            # Check inactive timeout
            session_policy = cls.get_session_policy()
            inactive_timeout = timedelta(minutes=session_policy['inactive_timeout_minutes'])
            if datetime.utcnow() - session.last_activity > inactive_timeout:
                session.is_active = False
                db.session.commit()
                return False
            
            return True
            
        except Exception as e:
            print(f"Error checking session validity: {e}")
            return False
    
    @classmethod
    def invalidate_session(cls, session_id: str) -> bool:
        """Invalidate a specific session"""
        try:
            session = UserSession.query.filter_by(session_id=session_id).first()
            if session:
                session.is_active = False
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error invalidating session: {e}")
            return False
    
    @classmethod
    def invalidate_all_user_sessions(cls, user_id: int) -> bool:
        """Invalidate all sessions for a user"""
        try:
            sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
            for session in sessions:
                session.is_active = False
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error invalidating user sessions: {e}")
            return False
    
    @classmethod
    def get_session_policy(cls) -> Dict:
        """Get current session policy"""
        try:
            policy = SecurityPolicy.query.filter_by(
                policy_name='session_policy',
                policy_type='SESSION'
            ).first()
            
            if policy:
                return {**cls.DEFAULT_SESSION_POLICY, **policy.configuration}
            
            return cls.DEFAULT_SESSION_POLICY
        except Exception as e:
            print(f"Error getting session policy: {e}")
            return cls.DEFAULT_SESSION_POLICY
    
    @classmethod
    def get_login_policy(cls) -> Dict:
        """Get current login policy"""
        try:
            policy = SecurityPolicy.query.filter_by(
                policy_name='login_policy',
                policy_type='LOGIN'
            ).first()
            
            if policy:
                return {**cls.DEFAULT_LOGIN_POLICY, **policy.configuration}
            
            return cls.DEFAULT_LOGIN_POLICY
        except Exception as e:
            print(f"Error getting login policy: {e}")
            return cls.DEFAULT_LOGIN_POLICY
    
    @classmethod
    def check_account_lockout(cls, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if account is locked out
        Returns (is_locked, unlock_time)
        """
        try:
            lockout = AccountLockout.query.filter_by(
                user_id=user_id,
                is_permanent=False
            ).filter(
                or_(
                    AccountLockout.unlock_at.is_(None),
                    AccountLockout.unlock_at > datetime.utcnow()
                )
            ).first()
            
            if lockout:
                unlock_time = lockout.unlock_at.isoformat() if lockout.unlock_at else None
                return True, unlock_time
            
            return False, None
            
        except Exception as e:
            print(f"Error checking account lockout: {e}")
            return False, None
    
    @classmethod
    def record_failed_login(cls, user_id: int, ip_address: str = None) -> bool:
        """Record a failed login attempt"""
        try:
            login_policy = cls.get_login_policy()
            
            # Check if user should be locked out
            failed_attempts = LoginHistory.query.filter_by(
                user_id=user_id,
                success=False
            ).filter(
                LoginHistory.timestamp >= datetime.utcnow() - timedelta(hours=1)
            ).count() + 1
            
            if failed_attempts >= login_policy['max_failed_attempts']:
                # Lock the account
                lockout_duration = timedelta(minutes=login_policy['lockout_duration_minutes'])
                unlock_at = datetime.utcnow() + lockout_duration
                
                lockout = AccountLockout(
                    user_id=user_id,
                    unlock_at=unlock_at,
                    reason='failed_attempts',
                    ip_address=ip_address,
                    failed_attempts=failed_attempts
                )
                
                db.session.add(lockout)
                
                # Log security event
                cls.log_security_event(
                    event_type='ACCOUNT_LOCKED',
                    severity='WARNING',
                    user_id=user_id,
                    description=f'Account locked due to {failed_attempts} failed login attempts',
                    ip_address=ip_address,
                    event_data={'failed_attempts': failed_attempts}
                )
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Error recording failed login: {e}")
            db.session.rollback()
            return False
    
    @classmethod
    def clear_failed_logins(cls, user_id: int) -> bool:
        """Clear failed login attempts for successful login"""
        try:
            # Remove any temporary lockouts
            lockouts = AccountLockout.query.filter_by(
                user_id=user_id,
                is_permanent=False
            ).all()
            
            for lockout in lockouts:
                lockout.unlocked_at = datetime.utcnow()
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Error clearing failed logins: {e}")
            db.session.rollback()
            return False
    
    @classmethod
    def log_security_event(cls, event_type: str, severity: str, user_id: int = None,
                          description: str = '', ip_address: str = None, 
                          event_data: Dict = None) -> bool:
        """Log a security event"""
        try:
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                description=description,
                ip_address=ip_address,
                event_data=event_data
            )
            
            db.session.add(event)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Error logging security event: {e}")
            db.session.rollback()
            return False
    
    @classmethod
    def setup_two_factor_auth(cls, user_id: int) -> Tuple[bool, str, str]:
        """
        Setup 2FA for a user
        Returns (success, secret_key, qr_code_data_url)
        """
        try:
            # Generate secret key
            secret_key = pyotp.random_base32()
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                return False, None, None
            
            # Create or update 2FA record
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor:
                two_factor = TwoFactorAuth(user_id=user_id)
                db.session.add(two_factor)
            
            two_factor.secret_key = secret_key
            two_factor.created_at = datetime.utcnow()
            
            db.session.commit()
            
            # Generate QR code
            totp = pyotp.TOTP(secret_key)
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="EdonuOps ERP"
            )
            
            # Create QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # For now, return the URI (frontend can generate QR code)
            return True, secret_key, provisioning_uri
            
        except Exception as e:
            print(f"Error setting up 2FA: {e}")
            db.session.rollback()
            return False, None, None
    
    @classmethod
    def verify_two_factor_token(cls, user_id: int, token: str) -> bool:
        """Verify 2FA token"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor or not two_factor.secret_key:
                return False
            
            totp = pyotp.TOTP(two_factor.secret_key)
            is_valid = totp.verify(token, valid_window=1)  # Allow 1 window of tolerance
            
            if is_valid:
                two_factor.last_used = datetime.utcnow()
                db.session.commit()
            
            return is_valid
            
        except Exception as e:
            print(f"Error verifying 2FA token: {e}")
            return False
    
    @classmethod
    def enable_two_factor_auth(cls, user_id: int) -> bool:
        """Enable 2FA for user after verification"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if two_factor and two_factor.secret_key:
                two_factor.is_enabled = True
                db.session.commit()
                
                # Log security event
                cls.log_security_event(
                    event_type='2FA_ENABLED',
                    severity='INFO',
                    user_id=user_id,
                    description='Two-factor authentication enabled'
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error enabling 2FA: {e}")
            db.session.rollback()
            return False
    
    @classmethod
    def disable_two_factor_auth(cls, user_id: int) -> bool:
        """Disable 2FA for user"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if two_factor:
                two_factor.is_enabled = False
                two_factor.secret_key = None
                two_factor.backup_codes = None
                db.session.commit()
                
                # Log security event
                cls.log_security_event(
                    event_type='2FA_DISABLED',
                    severity='WARNING',
                    user_id=user_id,
                    description='Two-factor authentication disabled'
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error disabling 2FA: {e}")
            db.session.rollback()
            return False

# Create global instance
security_service = SecurityService()