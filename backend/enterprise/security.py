"""
Enterprise Security Management
SAP/Oracle-style security and authentication system
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import request, current_app

class SecurityManager:
    """Enterprise security management system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get('jwt_secret', 'default-secret')
        self.jwt_expiration = config.get('jwt_expiration', 3600)
        self.bcrypt_rounds = config.get('bcrypt_rounds', 12)
        self.rate_limit = config.get('rate_limit', '1000/hour')
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'user_data': user_data,
            'exp': datetime.utcnow() + timedelta(seconds=self.jwt_expiration),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_client_ip(self) -> str:
        """Get client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr
    
    def get_user_agent(self) -> str:
        """Get user agent string"""
        return request.headers.get('User-Agent', 'Unknown')
    
    def validate_request_origin(self, allowed_origins: list) -> bool:
        """Validate request origin"""
        origin = request.headers.get('Origin')
        if not origin:
            return True  # Allow requests without origin (e.g., mobile apps)
        return origin in allowed_origins

