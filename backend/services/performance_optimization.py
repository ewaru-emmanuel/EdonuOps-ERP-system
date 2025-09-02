#!/usr/bin/env python3
"""
Performance Optimization Service
Implements caching, query optimization, and performance monitoring
"""

import time
import functools
from datetime import datetime, timedelta
from sqlalchemy import func, text
from app import db
import logging
import json

logger = logging.getLogger(__name__)

class PerformanceOptimizationService:
    """Service for performance optimization and monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.query_stats = {}
        self.performance_metrics = {}
    
    # ============================================================================
    # CACHING SYSTEM
    # ============================================================================
    
    def cache_result(self, key, data, ttl_seconds=300):
        """Cache data with TTL"""
        try:
            self.cache[key] = {
                'data': data,
                'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds),
                'created_at': datetime.utcnow()
            }
            return True
        except Exception as e:
            self.logger.error(f"Error caching data: {str(e)}")
            return False
    
    def get_cached_result(self, key):
        """Get cached data if not expired"""
        try:
            if key in self.cache:
                cached_item = self.cache[key]
                if datetime.utcnow() < cached_item['expires_at']:
                    return cached_item['data']
                else:
                    # Remove expired cache
                    del self.cache[key]
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached data: {str(e)}")
            return None
    
    def clear_cache(self, key=None):
        """Clear cache by key or all cache"""
        try:
            if key:
                if key in self.cache:
                    del self.cache[key]
            else:
                self.cache.clear()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    # ============================================================================
    # QUERY OPTIMIZATION
    # ============================================================================
    
    def optimize_query(self, query, limit=None, offset=None, order_by=None):
        """Optimize database query with pagination and ordering"""
        try:
            if order_by:
                query = query.order_by(order_by)
            
            if limit:
                query = query.limit(limit)
            
            if offset:
                query = query.offset(offset)
            
            return query
        except Exception as e:
            self.logger.error(f"Error optimizing query: {str(e)}")
            return query
    
    def batch_query(self, model, ids, batch_size=100):
        """Execute batch queries to avoid N+1 problem"""
        try:
            results = []
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                batch_results = model.query.filter(model.id.in_(batch_ids)).all()
                results.extend(batch_results)
            return results
        except Exception as e:
            self.logger.error(f"Error in batch query: {str(e)}")
            return []
    
    def prefetch_relationships(self, query, relationships):
        """Prefetch relationships to avoid lazy loading"""
        try:
            for relationship in relationships:
                query = query.options(db.joinedload(relationship))
            return query
        except Exception as e:
            self.logger.error(f"Error prefetching relationships: {str(e)}")
            return query
    
    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================
    
    def monitor_query_performance(self, query_name):
        """Decorator to monitor query performance"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Record performance metrics
                    if query_name not in self.query_stats:
                        self.query_stats[query_name] = {
                            'count': 0,
                            'total_time': 0,
                            'avg_time': 0,
                            'min_time': float('inf'),
                            'max_time': 0,
                            'errors': 0
                        }
                    
                    stats = self.query_stats[query_name]
                    stats['count'] += 1
                    stats['total_time'] += execution_time
                    stats['avg_time'] = stats['total_time'] / stats['count']
                    stats['min_time'] = min(stats['min_time'], execution_time)
                    stats['max_time'] = max(stats['max_time'], execution_time)
                    
                    # Log slow queries
                    if execution_time > 1.0:  # Log queries taking more than 1 second
                        self.logger.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    if query_name in self.query_stats:
                        self.query_stats[query_name]['errors'] += 1
                    self.logger.error(f"Query error in {query_name}: {str(e)}")
                    raise
            return wrapper
        return decorator
    
    def get_performance_metrics(self):
        """Get comprehensive performance metrics"""
        try:
            metrics = {
                'cache_stats': {
                    'total_cached_items': len(self.cache),
                    'cache_hit_rate': self._calculate_cache_hit_rate(),
                    'memory_usage': self._estimate_cache_memory_usage()
                },
                'query_stats': self.query_stats,
                'system_metrics': self._get_system_metrics(),
                'database_metrics': self._get_database_metrics()
            }
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            return {}
    
    def _calculate_cache_hit_rate(self):
        """Calculate cache hit rate"""
        try:
            # This is a simplified calculation
            # In a real system, you'd track actual hits vs misses
            total_requests = sum(stats.get('count', 0) for stats in self.query_stats.values())
            cache_hits = len(self.cache)  # Simplified
            return (cache_hits / total_requests * 100) if total_requests > 0 else 0
        except Exception as e:
            self.logger.error(f"Error calculating cache hit rate: {str(e)}")
            return 0
    
    def _estimate_cache_memory_usage(self):
        """Estimate cache memory usage"""
        try:
            cache_size = len(json.dumps(self.cache))
            return f"{cache_size} bytes"
        except Exception as e:
            self.logger.error(f"Error estimating cache memory usage: {str(e)}")
            return "Unknown"
    
    def _get_system_metrics(self):
        """Get system performance metrics"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            return {}
    
    def _get_database_metrics(self):
        """Get database performance metrics"""
        try:
            # Get database connection pool stats
            engine = db.engine
            pool = engine.pool
            
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except Exception as e:
            self.logger.error(f"Error getting database metrics: {str(e)}")
            return {}
    
    # ============================================================================
    # PERFORMANCE OPTIMIZATION RECOMMENDATIONS
    # ============================================================================
    
    def get_optimization_recommendations(self):
        """Get performance optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze query performance
            slow_queries = [
                name for name, stats in self.query_stats.items()
                if stats.get('avg_time', 0) > 0.5  # Queries taking more than 0.5s on average
            ]
            
            if slow_queries:
                recommendations.append({
                    'type': 'slow_queries',
                    'priority': 'high',
                    'message': f"Found {len(slow_queries)} slow queries that need optimization",
                    'details': slow_queries
                })
            
            # Check cache efficiency
            cache_hit_rate = self._calculate_cache_hit_rate()
            if cache_hit_rate < 50:
                recommendations.append({
                    'type': 'cache_efficiency',
                    'priority': 'medium',
                    'message': f"Cache hit rate is low ({cache_hit_rate:.1f}%). Consider increasing cache TTL or adding more cache keys.",
                    'details': {'current_hit_rate': cache_hit_rate}
                })
            
            # Check system resources
            system_metrics = self._get_system_metrics()
            if 'cpu_percent' in system_metrics and system_metrics['cpu_percent'] > 80:
                recommendations.append({
                    'type': 'high_cpu',
                    'priority': 'high',
                    'message': f"High CPU usage detected ({system_metrics['cpu_percent']:.1f}%). Consider optimizing queries or scaling up.",
                    'details': {'cpu_percent': system_metrics['cpu_percent']}
                })
            
            if 'memory_percent' in system_metrics and system_metrics['memory_percent'] > 80:
                recommendations.append({
                    'type': 'high_memory',
                    'priority': 'high',
                    'message': f"High memory usage detected ({system_metrics['memory_percent']:.1f}%). Consider optimizing memory usage or scaling up.",
                    'details': {'memory_percent': system_metrics['memory_percent']}
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting optimization recommendations: {str(e)}")
            return []
    
    # ============================================================================
    # AUTOMATIC OPTIMIZATION
    # ============================================================================
    
    def auto_optimize_queries(self):
        """Automatically optimize slow queries"""
        try:
            optimizations_applied = []
            
            for query_name, stats in self.query_stats.items():
                if stats.get('avg_time', 0) > 1.0:  # Queries taking more than 1s
                    # Apply automatic optimizations
                    optimization = self._apply_query_optimization(query_name)
                    if optimization:
                        optimizations_applied.append(optimization)
            
            return optimizations_applied
            
        except Exception as e:
            self.logger.error(f"Error in auto optimization: {str(e)}")
            return []
    
    def _apply_query_optimization(self, query_name):
        """Apply specific optimizations to a query"""
        try:
            # This is a placeholder for actual query optimization logic
            # In a real system, you'd analyze the query and apply specific optimizations
            
            return {
                'query_name': query_name,
                'optimization_type': 'index_suggestion',
                'message': f"Consider adding database indexes for {query_name}",
                'applied_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error applying query optimization: {str(e)}")
            return None

