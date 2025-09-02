#!/usr/bin/env python3
"""
Security Service
Handles authentication, authorization, and security monitoring
"""

import hashlib
import secrets
import re
from datetime import datetime, timedelta
from flask import request, current_app
import logging

logger = logging.getLogger(__name__)

class SecurityService:
    """Security service for authentication and authorization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.failed_login_attempts = {}
        self.security_events = []
    
    # ============================================================================
    # AUTHENTICATION
    # ============================================================================
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            self.logger.error(f"Error hashing password: {str(e)}")
            return None
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        try:
            return self.hash_password(password) == hashed_password
        except Exception as e:
            self.logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def generate_token(self, length=32):
        """Generate secure random token"""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            self.logger.error(f"Error generating token: {str(e)}")
            return None
    
    def validate_password_strength(self, password):
        """Validate password strength"""
        try:
            if len(password) < 8:
                return False, "Password must be at least 8 characters long"
            
            if not re.search(r"[A-Z]", password):
                return False, "Password must contain at least one uppercase letter"
            
            if not re.search(r"[a-z]", password):
                return False, "Password must contain at least one lowercase letter"
            
            if not re.search(r"\d", password):
                return False, "Password must contain at least one digit"
            
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                return False, "Password must contain at least one special character"
            
            return True, "Password meets strength requirements"
            
        except Exception as e:
            self.logger.error(f"Error validating password strength: {str(e)}")
            return False, "Error validating password"
    
    # ============================================================================
    # RATE LIMITING
    # ============================================================================
    
    def check_rate_limit(self, identifier, max_attempts=5, window_minutes=15):
        """Check rate limiting for login attempts"""
        try:
            current_time = datetime.utcnow()
            
            if identifier not in self.failed_login_attempts:
                self.failed_login_attempts[identifier] = []
            
            # Remove old attempts outside the window
            window_start = current_time - timedelta(minutes=window_minutes)
            self.failed_login_attempts[identifier] = [
                attempt for attempt in self.failed_login_attempts[identifier]
                if attempt > window_start
            ]
            
            # Check if limit exceeded
            if len(self.failed_login_attempts[identifier]) >= max_attempts:
                return False, "Rate limit exceeded. Please try again later."
            
            return True, "Rate limit check passed"
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return False, "Error checking rate limit"
    
    def record_failed_attempt(self, identifier):
        """Record a failed login attempt"""
        try:
            if identifier not in self.failed_login_attempts:
                self.failed_login_attempts[identifier] = []
            
            self.failed_login_attempts[identifier].append(datetime.utcnow())
            
        except Exception as e:
            self.logger.error(f"Error recording failed attempt: {str(e)}")
    
    # ============================================================================
    # INPUT VALIDATION
    # ============================================================================
    
    def sanitize_input(self, input_string):
        """Sanitize user input to prevent injection attacks"""
        try:
            if not input_string:
                return ""
            
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\']', '', str(input_string))
            return sanitized.strip()
            
        except Exception as e:
            self.logger.error(f"Error sanitizing input: {str(e)}")
            return ""
    
    def validate_email(self, email):
        """Validate email format"""
        try:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception as e:
            self.logger.error(f"Error validating email: {str(e)}")
            return False
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        try:
            # Remove all non-digit characters
            digits_only = re.sub(r'\D', '', phone)
            return len(digits_only) >= 10
        except Exception as e:
            self.logger.error(f"Error validating phone: {str(e)}")
            return False
    
    # ============================================================================
    # SECURITY MONITORING
    # ============================================================================
    
    def log_security_event(self, event_type, details, severity='info'):
        """Log security events"""
        try:
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'details': details,
                'severity': severity,
                'ip_address': request.remote_addr if request else 'unknown',
                'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'unknown'
            }
            
            self.security_events.append(event)
            
            # Keep only last 1000 events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
            # Log based on severity
            if severity == 'error':
                self.logger.error(f"Security Event: {event_type} - {details}")
            elif severity == 'warning':
                self.logger.warning(f"Security Event: {event_type} - {details}")
            else:
                self.logger.info(f"Security Event: {event_type} - {details}")
                
        except Exception as e:
            self.logger.error(f"Error logging security event: {str(e)}")
    
    def get_security_events(self, limit=100):
        """Get recent security events"""
        try:
            return self.security_events[-limit:]
        except Exception as e:
            self.logger.error(f"Error getting security events: {str(e)}")
            return []
    
    def get_security_metrics(self):
        """Get security metrics"""
        try:
            current_time = datetime.utcnow()
            last_hour = current_time - timedelta(hours=1)
            last_day = current_time - timedelta(days=1)
            
            recent_events = [
                event for event in self.security_events
                if datetime.fromisoformat(event['timestamp']) > last_hour
            ]
            
            daily_events = [
                event for event in self.security_events
                if datetime.fromisoformat(event['timestamp']) > last_day
            ]
            
            return {
                'total_events': len(self.security_events),
                'events_last_hour': len(recent_events),
                'events_last_day': len(daily_events),
                'failed_login_attempts': len(self.failed_login_attempts),
                'rate_limited_ips': len([
                    ip for ip, attempts in self.failed_login_attempts.items()
                    if len(attempts) >= 5
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting security metrics: {str(e)}")
            return {}
    
    # ============================================================================
    # AUTHORIZATION
    # ============================================================================
    
    def check_permission(self, user_id, resource, action):
        """Check if user has permission for resource and action"""
        try:
            # This is a simplified permission check
            # In a real system, you'd check against user roles and permissions
            
            # Admin users have all permissions
            if user_id == 1:  # Assuming user_id 1 is admin
                return True
            
            # Define basic permissions
            permissions = {
                'finance': ['read', 'write'],
                'inventory': ['read', 'write'],
                'crm': ['read', 'write'],
                'reports': ['read']
            }
            
            if resource in permissions and action in permissions[resource]:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking permission: {str(e)}")
            return False
    
    def require_permission(self, resource, action):
        """Decorator to require specific permission"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Get user_id from request or session
                user_id = getattr(request, 'user_id', None)
                
                if not user_id:
                    return {'error': 'Authentication required'}, 401
                
                if not self.check_permission(user_id, resource, action):
                    return {'error': 'Permission denied'}, 403
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

