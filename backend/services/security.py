#!/usr/bin/env python3
"""
Security Service
Simple authentication and security monitoring
"""

import hashlib
import secrets
import re
from datetime import datetime, timedelta
from flask import request
import logging

logger = logging.getLogger(__name__)

class SecurityService:
    """Simple security service"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.security_events = []
    
    def hash_password(self, password):
        """Hash password"""
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            return None
    
    def verify_password(self, password, hashed_password):
        """Verify password"""
        try:
            return self.hash_password(password) == hashed_password
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def generate_token(self, length=32):
        """Generate secure token"""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            return None
    
    def validate_password_strength(self, password):
        """Validate password strength"""
        try:
            if len(password) < 8:
                return False, "Password too short"
            
            if not re.search(r"[A-Z]", password):
                return False, "Need uppercase letter"
            
            if not re.search(r"\d", password):
                return False, "Need digit"
            
            return True, "Password OK"
            
        except Exception as e:
            logger.error(f"Error validating password: {str(e)}")
            return False, "Validation error"
    
    def check_rate_limit(self, identifier, max_attempts=5):
        """Check rate limiting"""
        try:
            current_time = datetime.utcnow()
            
            if identifier not in self.failed_attempts:
                self.failed_attempts[identifier] = []
            
            # Remove old attempts (older than 15 minutes)
            window_start = current_time - timedelta(minutes=15)
            self.failed_attempts[identifier] = [
                attempt for attempt in self.failed_attempts[identifier]
                if attempt > window_start
            ]
            
            if len(self.failed_attempts[identifier]) >= max_attempts:
                return False, "Rate limit exceeded"
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return False, "Error"
    
    def record_failed_attempt(self, identifier):
        """Record failed attempt"""
        try:
            if identifier not in self.failed_attempts:
                self.failed_attempts[identifier] = []
            
            self.failed_attempts[identifier].append(datetime.utcnow())
            
        except Exception as e:
            logger.error(f"Error recording failed attempt: {str(e)}")
    
    def sanitize_input(self, input_string):
        """Sanitize input"""
        try:
            if not input_string:
                return ""
            
            sanitized = re.sub(r'[<>"\']', '', str(input_string))
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"Error sanitizing input: {str(e)}")
            return ""
    
    def log_security_event(self, event_type, details):
        """Log security event"""
        try:
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'details': details,
                'ip_address': request.remote_addr if request else 'unknown'
            }
            
            self.security_events.append(event)
            
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
                
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
    
    def get_security_metrics(self):
        """Get security metrics"""
        try:
            return {
                'total_events': len(self.security_events),
                'failed_attempts': len(self.failed_attempts),
                'rate_limited': len([
                    ip for ip, attempts in self.failed_attempts.items()
                    if len(attempts) >= 5
                ])
            }
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {str(e)}")
            return {}

