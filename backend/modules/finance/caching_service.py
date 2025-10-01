"""
Caching Service for Bank Reconciliation
Optimizes performance with intelligent caching
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
from flask import current_app
from functools import wraps
import redis
from sqlalchemy import text

logger = logging.getLogger(__name__)

class ReconciliationCache:
    """Intelligent caching service for reconciliation data"""
    
    def __init__(self):
        self.redis_client = None
        self.cache_enabled = os.getenv('REDIS_CACHE_ENABLED', 'false').lower() == 'true'
        self.default_ttl = int(os.getenv('CACHE_DEFAULT_TTL', '3600'))  # 1 hour
        
        if self.cache_enabled:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', '6379')),
                    db=int(os.getenv('REDIS_DB', '0')),
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connection established")
            except Exception as e:
                logger.warning(f"Redis cache not available: {str(e)}")
                self.cache_enabled = False
    
    def get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        try:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            key_string = f"{prefix}:{json.dumps(sorted_kwargs, sort_keys=True)}"
            return hashlib.md5(key_string.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating cache key: {str(e)}")
            return f"{prefix}:{hashlib.md5(str(kwargs).encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache value: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache value: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            logger.error(f"Error deleting cache value: {str(e)}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern"""
        if not self.cache_enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {str(e)}")
            return 0
    
    def get_reconciliation_sessions(self, bank_account_id: Optional[int] = None, 
                                  status: Optional[str] = None, 
                                  limit: int = 100) -> Optional[List[Dict]]:
        """Get cached reconciliation sessions"""
        cache_key = self.get_cache_key(
            'reconciliation_sessions',
            bank_account_id=bank_account_id,
            status=status,
            limit=limit
        )
        return self.get(cache_key)
    
    def set_reconciliation_sessions(self, sessions: List[Dict], 
                                  bank_account_id: Optional[int] = None,
                                  status: Optional[str] = None,
                                  ttl: Optional[int] = None) -> bool:
        """Cache reconciliation sessions"""
        cache_key = self.get_cache_key(
            'reconciliation_sessions',
            bank_account_id=bank_account_id,
            status=status,
            limit=len(sessions)
        )
        return self.set(cache_key, sessions, ttl)
    
    def get_bank_transactions(self, bank_account_id: int, 
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> Optional[List[Dict]]:
        """Get cached bank transactions"""
        cache_key = self.get_cache_key(
            'bank_transactions',
            bank_account_id=bank_account_id,
            start_date=start_date,
            end_date=end_date
        )
        return self.get(cache_key)
    
    def set_bank_transactions(self, transactions: List[Dict], 
                            bank_account_id: int,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            ttl: Optional[int] = None) -> bool:
        """Cache bank transactions"""
        cache_key = self.get_cache_key(
            'bank_transactions',
            bank_account_id=bank_account_id,
            start_date=start_date,
            end_date=end_date
        )
        return self.set(cache_key, transactions, ttl)
    
    def get_gl_entries(self, bank_account_id: int, 
                      reconciled: Optional[bool] = None) -> Optional[List[Dict]]:
        """Get cached GL entries"""
        cache_key = self.get_cache_key(
            'gl_entries',
            bank_account_id=bank_account_id,
            reconciled=reconciled
        )
        return self.get(cache_key)
    
    def set_gl_entries(self, entries: List[Dict], 
                      bank_account_id: int,
                      reconciled: Optional[bool] = None,
                      ttl: Optional[int] = None) -> bool:
        """Cache GL entries"""
        cache_key = self.get_cache_key(
            'gl_entries',
            bank_account_id=bank_account_id,
            reconciled=reconciled
        )
        return self.set(cache_key, entries, ttl)
    
    def invalidate_reconciliation_cache(self, bank_account_id: Optional[int] = None):
        """Invalidate reconciliation-related cache"""
        patterns = [
            'reconciliation_sessions:*',
            'bank_transactions:*',
            'gl_entries:*'
        ]
        
        if bank_account_id:
            patterns = [f"*:bank_account_id={bank_account_id}*"]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.invalidate_pattern(pattern)
        
        logger.info(f"Invalidated {total_invalidated} cache entries")
        return total_invalidated
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache_enabled or not self.redis_client:
            return {'enabled': False}
        
        try:
            info = self.redis_client.info()
            return {
                'enabled': True,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'enabled': True, 'error': str(e)}

# Global cache instance
reconciliation_cache = ReconciliationCache()

def cache_result(ttl: int = 3600, key_prefix: str = 'default'):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = reconciliation_cache.get_cache_key(
                key_prefix,
                function=func.__name__,
                args=args,
                kwargs=kwargs
            )
            
            # Try to get from cache
            cached_result = reconciliation_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            reconciliation_cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        return wrapper
    return decorator

def invalidate_cache_on_change(func):
    """Decorator to invalidate cache when data changes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Invalidate relevant cache
        reconciliation_cache.invalidate_reconciliation_cache()
        
        return result
    return wrapper












