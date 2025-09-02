"""
Enterprise Audit Service
SAP/Oracle-style audit trail and logging system
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, current_app

class AuditService:
    """Enterprise audit trail service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_activity(self, user_id: int, action: str, resource: str, 
                    details: Dict[str, Any], ip_address: str = None):
        """Log user activity"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': details,
            'ip_address': ip_address or self._get_client_ip(),
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'request_id': request.headers.get('X-Request-ID', 'Unknown')
        }
        
        self.logger.info(f"AUDIT: {json.dumps(audit_entry)}")
        return audit_entry
    
    def log_security_event(self, event_type: str, severity: str, 
                          details: Dict[str, Any], user_id: Optional[int] = None):
        """Log security events"""
        security_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'user_id': user_id,
            'details': details,
            'ip_address': self._get_client_ip(),
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        
        if severity == 'high':
            self.logger.error(f"SECURITY_HIGH: {json.dumps(security_entry)}")
        elif severity == 'medium':
            self.logger.warning(f"SECURITY_MEDIUM: {json.dumps(security_entry)}")
        else:
            self.logger.info(f"SECURITY_LOW: {json.dumps(security_entry)}")
        
        return security_entry
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr

