import redis
import json
import pickle
from datetime import timedelta
from typing import Any, Optional, Union
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for enterprise performance"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url
        self.client = None
        # Don't connect immediately - will connect when needed
    
    def _get_redis_url(self):
        """Get Redis URL from config or use default"""
        if self.redis_url:
            return self.redis_url
        try:
            from flask import current_app
            return current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        except RuntimeError:
            return 'redis://localhost:6379/0'
    
    def _ensure_connected(self):
        """Ensure Redis connection is established"""
        if self.client is None:
            self._connect()
    
    def _connect(self):
        """Establish Redis connection with error handling"""
        try:
            redis_url = self._get_redis_url()
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.client.ping()
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None
        except Exception as e:
            logger.error(f"Unexpected Redis error: {e}")
            self.client = None
    
    def _get_key(self, key: str, tenant_id: str = None) -> str:
        """Generate cache key with tenant prefix"""
        if tenant_id:
            return f"tenant:{tenant_id}:{key}"
        return key
    
    def set(self, key: str, value: Any, ttl: int = 3600, tenant_id: str = None) -> bool:
        """Set cache value with TTL"""
        self._ensure_connected()
        if not self.client:
            return False
        
        try:
            cache_key = self._get_key(key, tenant_id)
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            return self.client.setex(cache_key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str, tenant_id: str = None) -> Optional[Any]:
        """Get cache value"""
        self._ensure_connected()
        if not self.client:
            return None
        
        try:
            cache_key = self._get_key(key, tenant_id)
            value = self.client.get(cache_key)
            
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str, tenant_id: str = None) -> bool:
        """Delete cache key"""
        self._ensure_connected()
        if not self.client:
            return False
        
        try:
            cache_key = self._get_key(key, tenant_id)
            return bool(self.client.delete(cache_key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str, tenant_id: str = None) -> bool:
        """Check if key exists"""
        self._ensure_connected()
        if not self.client:
            return False
        
        try:
            cache_key = self._get_key(key, tenant_id)
            return bool(self.client.exists(cache_key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def expire(self, key: str, ttl: int, tenant_id: str = None) -> bool:
        """Set expiration for key"""
        self._ensure_connected()
        if not self.client:
            return False
        
        try:
            cache_key = self._get_key(key, tenant_id)
            return bool(self.client.expire(cache_key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    def clear_tenant_cache(self, tenant_id: str) -> bool:
        """Clear all cache for a specific tenant"""
        if not self.client:
            return False
        
        try:
            pattern = f"tenant:{tenant_id}:*"
            keys = self.client.keys(pattern)
            if keys:
                return bool(self.client.delete(*keys))
            return True
        except Exception as e:
            logger.error(f"Clear tenant cache error: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache (use with caution)"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.flushdb())
        except Exception as e:
            logger.error(f"Clear all cache error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.client:
            return {"error": "Redis not connected"}
        
        try:
            info = self.client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.error(f"Get cache stats error: {e}")
            return {"error": str(e)}

# Global cache instance
cache_service = CacheService()

# Cache decorators for easy use
def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Decorator to invalidate cache after function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Invalidate cache based on pattern
            if cache_service.client:
                keys = cache_service.client.keys(pattern)
                if keys:
                    cache_service.client.delete(*keys)
            return result
        return wrapper
    return decorator
