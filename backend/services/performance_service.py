#!/usr/bin/env python3
"""
Performance Optimization Service
Simple caching and monitoring
"""

import time
from datetime import datetime, timedelta
from app import db
import logging

logger = logging.getLogger(__name__)

class PerformanceService:
    """Simple performance optimization service"""
    
    def __init__(self):
        self.cache = {}
        self.query_stats = {}
    
    def cache_result(self, key, data, ttl_seconds=300):
        """Cache data with TTL"""
        try:
            self.cache[key] = {
                'data': data,
                'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds)
            }
            return True
        except Exception as e:
            logger.error(f"Error caching data: {str(e)}")
            return False
    
    def get_cached_result(self, key):
        """Get cached data if not expired"""
        try:
            if key in self.cache:
                cached_item = self.cache[key]
                if datetime.utcnow() < cached_item['expires_at']:
                    return cached_item['data']
                else:
                    del self.cache[key]
            return None
        except Exception as e:
            logger.error(f"Error getting cached data: {str(e)}")
            return None
    
    def monitor_query(self, query_name):
        """Decorator to monitor query performance"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if query_name not in self.query_stats:
                        self.query_stats[query_name] = {
                            'count': 0,
                            'total_time': 0,
                            'avg_time': 0
                        }
                    
                    stats = self.query_stats[query_name]
                    stats['count'] += 1
                    stats['total_time'] += execution_time
                    stats['avg_time'] = stats['total_time'] / stats['count']
                    
                    if execution_time > 1.0:
                        logger.warning(f"Slow query: {query_name} took {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    logger.error(f"Query error in {query_name}: {str(e)}")
                    raise
            return wrapper
        return decorator
    
    def get_performance_metrics(self):
        """Get performance metrics"""
        try:
            return {
                'cache_stats': {
                    'total_cached_items': len(self.cache)
                },
                'query_stats': self.query_stats
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return {}

