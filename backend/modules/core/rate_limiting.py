"""
Rate Limiting & Abuse Protection System
Multi-layered protection for tenant isolation and API security
"""

from flask import request, g, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import redis
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimitingService:
    """Advanced rate limiting service with multiple protection layers"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.limiter = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize rate limiting with Flask app"""
        self.app = app
        
        # Initialize Redis for distributed rate limiting
        try:
            self.redis_client = redis.Redis(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                db=app.config.get('REDIS_DB', 0),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connected for rate limiting")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, using in-memory rate limiting: {e}")
            self.redis_client = None
        
        # Initialize Flask-Limiter
        self.limiter = Limiter(
            app=app,
            key_func=self._get_rate_limit_key,
            storage_uri=self._get_storage_uri(),
            default_limits=["1000 per hour", "100 per minute"]
        )
        
        # Register rate limiting decorators
        self._register_decorators()
    
    def _get_storage_uri(self):
        """Get storage URI for rate limiting"""
        if self.redis_client:
            return "redis://localhost:6379"
        return "memory://"
    
    def _get_rate_limit_key(self):
        """Get rate limiting key based on tenant and IP"""
        # Priority: tenant_id > user_id > IP address
        if hasattr(g, 'tenant_context') and g.tenant_context.tenant_id:
            return f"tenant:{g.tenant_context.tenant_id}"
        elif hasattr(g, 'tenant_context') and g.tenant_context.user_id:
            return f"user:{g.tenant_context.user_id}"
        else:
            return get_remote_address()
    
    def _register_decorators(self):
        """Register custom rate limiting decorators"""
        
        # Tenant-based rate limiting
        def tenant_rate_limit(requests_per_minute=60, requests_per_hour=1000):
            """Rate limit based on tenant"""
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    if not hasattr(g, 'tenant_context') or not g.tenant_context.tenant_id:
                        return f(*args, **kwargs)
                    
                    tenant_id = g.tenant_context.tenant_id
                    current_time = time.time()
                    
                    # Check tenant rate limits
                    if self._check_tenant_limits(tenant_id, requests_per_minute, requests_per_hour):
                        return f(*args, **kwargs)
                    else:
                        from flask import jsonify
                        return jsonify({
                            'error': 'Rate limit exceeded for tenant',
                            'message': f'Maximum {requests_per_minute} requests per minute allowed',
                            'retry_after': 60
                        }), 429
                
                return decorated_function
            return decorator
        
        # Endpoint-specific rate limiting
        def endpoint_rate_limit(requests_per_minute=30):
            """Rate limit specific endpoints"""
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    endpoint = request.endpoint
                    key = f"endpoint:{endpoint}:{self._get_rate_limit_key()}"
                    
                    if self._check_endpoint_limits(key, requests_per_minute):
                        return f(*args, **kwargs)
                    else:
                        from flask import jsonify
                        return jsonify({
                            'error': 'Rate limit exceeded for endpoint',
                            'message': f'Maximum {requests_per_minute} requests per minute for this endpoint',
                            'retry_after': 60
                        }), 429
                
                return decorated_function
            return decorator
        
        # IP-based rate limiting
        def ip_rate_limit(requests_per_minute=100):
            """Rate limit based on IP address"""
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    ip = get_remote_address()
                    key = f"ip:{ip}"
                    
                    if self._check_ip_limits(key, requests_per_minute):
                        return f(*args, **kwargs)
                    else:
                        from flask import jsonify
                        return jsonify({
                            'error': 'Rate limit exceeded for IP',
                            'message': f'Maximum {requests_per_minute} requests per minute from this IP',
                            'retry_after': 60
                        }), 429
                
                return decorated_function
            return decorator
        
        # Store decorators for use
        self.tenant_rate_limit = tenant_rate_limit
        self.endpoint_rate_limit = endpoint_rate_limit
        self.ip_rate_limit = ip_rate_limit
    
    def _check_tenant_limits(self, tenant_id, requests_per_minute, requests_per_hour):
        """Check tenant-specific rate limits"""
        try:
            current_time = time.time()
            minute_key = f"tenant:{tenant_id}:minute:{int(current_time // 60)}"
            hour_key = f"tenant:{tenant_id}:hour:{int(current_time // 3600)}"
            
            if self.redis_client:
                # Redis-based rate limiting
                pipe = self.redis_client.pipeline()
                pipe.incr(minute_key)
                pipe.expire(minute_key, 60)
                pipe.incr(hour_key)
                pipe.expire(hour_key, 3600)
                results = pipe.execute()
                
                minute_count = results[0]
                hour_count = results[2]
            else:
                # In-memory rate limiting (fallback)
                minute_count = self._get_memory_count(minute_key, 60)
                hour_count = self._get_memory_count(hour_key, 3600)
            
            return minute_count <= requests_per_minute and hour_count <= requests_per_hour
            
        except Exception as e:
            logger.error(f"Error checking tenant limits: {e}")
            return True  # Allow request if rate limiting fails
    
    def _check_endpoint_limits(self, key, requests_per_minute):
        """Check endpoint-specific rate limits"""
        try:
            current_time = time.time()
            minute_key = f"{key}:minute:{int(current_time // 60)}"
            
            if self.redis_client:
                count = self.redis_client.incr(minute_key)
                self.redis_client.expire(minute_key, 60)
                return count <= requests_per_minute
            else:
                count = self._get_memory_count(minute_key, 60)
                return count <= requests_per_minute
                
        except Exception as e:
            logger.error(f"Error checking endpoint limits: {e}")
            return True
    
    def _check_ip_limits(self, key, requests_per_minute):
        """Check IP-based rate limits"""
        try:
            current_time = time.time()
            minute_key = f"{key}:minute:{int(current_time // 60)}"
            
            if self.redis_client:
                count = self.redis_client.incr(minute_key)
                self.redis_client.expire(minute_key, 60)
                return count <= requests_per_minute
            else:
                count = self._get_memory_count(minute_key, 60)
                return count <= requests_per_minute
                
        except Exception as e:
            logger.error(f"Error checking IP limits: {e}")
            return True
    
    def _get_memory_count(self, key, ttl):
        """Get count from memory storage (fallback)"""
        # This is a simplified in-memory implementation
        # In production, you'd want a more sophisticated approach
        if not hasattr(self, '_memory_counts'):
            self._memory_counts = {}
        
        current_time = time.time()
        
        # Clean expired entries
        expired_keys = [k for k, (count, timestamp) in self._memory_counts.items() 
                       if current_time - timestamp > ttl]
        for k in expired_keys:
            del self._memory_counts[k]
        
        # Get or create count
        if key not in self._memory_counts:
            self._memory_counts[key] = (1, current_time)
        else:
            count, timestamp = self._memory_counts[key]
            if current_time - timestamp < ttl:
                self._memory_counts[key] = (count + 1, timestamp)
            else:
                self._memory_counts[key] = (1, current_time)
        
        return self._memory_counts[key][0]
    
    def get_rate_limit_status(self, tenant_id=None, endpoint=None, ip=None):
        """Get current rate limit status"""
        try:
            status = {
                'tenant_limits': {},
                'endpoint_limits': {},
                'ip_limits': {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if tenant_id:
                # Get tenant rate limit status
                current_time = time.time()
                minute_key = f"tenant:{tenant_id}:minute:{int(current_time // 60)}"
                hour_key = f"tenant:{tenant_id}:hour:{int(current_time // 3600)}"
                
                if self.redis_client:
                    minute_count = self.redis_client.get(minute_key) or 0
                    hour_count = self.redis_client.get(hour_key) or 0
                else:
                    minute_count = self._get_memory_count(minute_key, 60)
                    hour_count = self._get_memory_count(hour_key, 3600)
                
                status['tenant_limits'] = {
                    'minute_count': int(minute_count),
                    'hour_count': int(hour_count),
                    'minute_limit': 60,
                    'hour_limit': 1000
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {'error': 'Failed to get rate limit status'}
    
    def reset_rate_limits(self, tenant_id=None, endpoint=None, ip=None):
        """Reset rate limits for specific keys"""
        try:
            if self.redis_client:
                if tenant_id:
                    pattern = f"tenant:{tenant_id}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                
                if endpoint:
                    pattern = f"endpoint:{endpoint}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                
                if ip:
                    pattern = f"ip:{ip}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting rate limits: {e}")
            return False

# Global rate limiting service instance
rate_limiting_service = RateLimitingService()

# Convenience decorators
def tenant_rate_limit(requests_per_minute=60, requests_per_hour=1000):
    """Rate limit based on tenant"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting - just call the function
            # TODO: Implement proper tenant-based rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def endpoint_rate_limit(requests_per_minute=30):
    """Rate limit specific endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting - just call the function
            # TODO: Implement proper endpoint-based rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def ip_rate_limit(requests_per_minute=100):
    """Rate limit based on IP address"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting - just call the function
            # TODO: Implement proper IP-based rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Advanced rate limiting decorators
def sensitive_endpoint_limit():
    """Rate limit for sensitive endpoints"""
    return tenant_rate_limit(20, 200)

def api_endpoint_limit():
    """Rate limit for general API endpoints"""
    return tenant_rate_limit(100, 1000)

def public_endpoint_limit():
    """Rate limit for public endpoints"""
    return ip_rate_limit(50)

def admin_endpoint_limit():
    """Rate limit for admin endpoints"""
    return tenant_rate_limit(200, 2000)

