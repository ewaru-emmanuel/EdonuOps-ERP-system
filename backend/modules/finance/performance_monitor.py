"""
Performance Monitoring Service
Tracks and optimizes reconciliation performance
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from sqlalchemy import text, func
from ..database import db

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and optimize reconciliation performance"""
    
    def __init__(self):
        self.metrics_enabled = os.getenv('PERFORMANCE_METRICS_ENABLED', 'true').lower() == 'true'
        self.slow_query_threshold = float(os.getenv('SLOW_QUERY_THRESHOLD', '1.0'))  # seconds
        self.metrics = {}
    
    def track_operation(self, operation_name: str, start_time: float, end_time: float, 
                      success: bool = True, metadata: Optional[Dict] = None):
        """Track operation performance"""
        if not self.metrics_enabled:
            return
        
        try:
            duration = end_time - start_time
            is_slow = duration > self.slow_query_threshold
            
            metric = {
                'operation': operation_name,
                'duration': duration,
                'success': success,
                'is_slow': is_slow,
                'timestamp': datetime.utcnow(),
                'metadata': metadata or {}
            }
            
            # Store in memory (in production, use a proper metrics store)
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
            
            self.metrics[operation_name].append(metric)
            
            # Log slow operations
            if is_slow:
                logger.warning(f"Slow operation detected: {operation_name} took {duration:.2f}s")
            
            # Keep only last 1000 metrics per operation
            if len(self.metrics[operation_name]) > 1000:
                self.metrics[operation_name] = self.metrics[operation_name][-1000:]
                
        except Exception as e:
            logger.error(f"Error tracking operation: {str(e)}")
    
    def get_operation_stats(self, operation_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get performance statistics for an operation"""
        try:
            if operation_name not in self.metrics:
                return {'error': 'Operation not found'}
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_metrics = [
                m for m in self.metrics[operation_name] 
                if m['timestamp'] >= cutoff_time
            ]
            
            if not recent_metrics:
                return {'error': 'No recent data'}
            
            durations = [m['duration'] for m in recent_metrics]
            successes = [m for m in recent_metrics if m['success']]
            slow_operations = [m for m in recent_metrics if m['is_slow']]
            
            return {
                'operation': operation_name,
                'total_operations': len(recent_metrics),
                'success_rate': len(successes) / len(recent_metrics) * 100,
                'average_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'slow_operations': len(slow_operations),
                'slow_operation_rate': len(slow_operations) / len(recent_metrics) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting operation stats: {str(e)}")
            return {'error': str(e)}
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        try:
            # Database performance
            db_stats = self.get_database_performance()
            
            # Cache performance
            cache_stats = self.get_cache_performance()
            
            # Operation performance
            operation_stats = {}
            for operation_name in self.metrics.keys():
                operation_stats[operation_name] = self.get_operation_stats(operation_name)
            
            return {
                'timestamp': datetime.utcnow(),
                'database': db_stats,
                'cache': cache_stats,
                'operations': operation_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting system performance: {str(e)}")
            return {'error': str(e)}
    
    def get_database_performance(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            with current_app.app_context():
                # Get table sizes
                table_sizes = {}
                tables = ['bank_accounts', 'bank_transactions', 'reconciliation_sessions', 'advanced_general_ledger_entries']
                
                for table in tables:
                    try:
                        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        table_sizes[table] = count
                    except Exception as e:
                        logger.warning(f"Could not get size for table {table}: {str(e)}")
                        table_sizes[table] = 0
                
                # Get recent activity
                recent_sessions = db.session.execute(text("""
                    SELECT COUNT(*) FROM reconciliation_sessions 
                    WHERE created_at >= datetime('now', '-24 hours')
                """)).scalar()
                
                recent_transactions = db.session.execute(text("""
                    SELECT COUNT(*) FROM bank_transactions 
                    WHERE created_at >= datetime('now', '-24 hours')
                """)).scalar()
                
                return {
                    'table_sizes': table_sizes,
                    'recent_sessions_24h': recent_sessions,
                    'recent_transactions_24h': recent_transactions
                }
                
        except Exception as e:
            logger.error(f"Error getting database performance: {str(e)}")
            return {'error': str(e)}
    
    def get_cache_performance(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        try:
            from .caching_service import reconciliation_cache
            return reconciliation_cache.get_cache_stats()
        except Exception as e:
            logger.error(f"Error getting cache performance: {str(e)}")
            return {'error': str(e)}
    
    def identify_performance_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        try:
            bottlenecks = []
            
            # Check for slow operations
            for operation_name, metrics in self.metrics.items():
                recent_metrics = metrics[-100:]  # Last 100 operations
                if not recent_metrics:
                    continue
                
                slow_count = sum(1 for m in recent_metrics if m['is_slow'])
                if slow_count > 10:  # More than 10% slow operations
                    bottlenecks.append({
                        'type': 'slow_operations',
                        'operation': operation_name,
                        'slow_count': slow_count,
                        'total_count': len(recent_metrics),
                        'recommendation': 'Consider optimizing query or adding indexes'
                    })
            
            # Check for high error rates
            for operation_name, metrics in self.metrics.items():
                recent_metrics = metrics[-100:]
                if not recent_metrics:
                    continue
                
                error_count = sum(1 for m in recent_metrics if not m['success'])
                error_rate = error_count / len(recent_metrics) * 100
                
                if error_rate > 5:  # More than 5% error rate
                    bottlenecks.append({
                        'type': 'high_error_rate',
                        'operation': operation_name,
                        'error_count': error_count,
                        'error_rate': error_rate,
                        'recommendation': 'Investigate and fix error causes'
                    })
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {str(e)}")
            return []
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        try:
            recommendations = []
            
            # Check database table sizes
            db_stats = self.get_database_performance()
            if 'table_sizes' in db_stats:
                for table, size in db_stats['table_sizes'].items():
                    if size > 100000:  # More than 100k records
                        recommendations.append({
                            'type': 'large_table',
                            'table': table,
                            'size': size,
                            'recommendation': f'Consider archiving old data from {table} table'
                        })
            
            # Check for missing indexes
            recommendations.extend(self.get_index_recommendations())
            
            # Check cache performance
            cache_stats = self.get_cache_performance()
            if cache_stats.get('enabled') and cache_stats.get('keyspace_misses', 0) > 1000:
                recommendations.append({
                    'type': 'cache_misses',
                    'misses': cache_stats.get('keyspace_misses', 0),
                    'recommendation': 'Consider increasing cache TTL or improving cache keys'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {str(e)}")
            return []
    
    def get_index_recommendations(self) -> List[Dict[str, Any]]:
        """Get database index recommendations"""
        try:
            recommendations = []
            
            # Common index recommendations for reconciliation tables
            index_suggestions = [
                {
                    'table': 'bank_transactions',
                    'columns': ['bank_account_id', 'transaction_date'],
                    'reason': 'Frequent queries by account and date'
                },
                {
                    'table': 'bank_transactions',
                    'columns': ['matched', 'bank_account_id'],
                    'reason': 'Queries for unmatched transactions'
                },
                {
                    'table': 'reconciliation_sessions',
                    'columns': ['bank_account_id', 'status'],
                    'reason': 'Queries by account and status'
                },
                {
                    'table': 'advanced_general_ledger_entries',
                    'columns': ['bank_account_id', 'reconciled'],
                    'reason': 'Queries for unreconciled GL entries'
                }
            ]
            
            for suggestion in index_suggestions:
                recommendations.append({
                    'type': 'missing_index',
                    'table': suggestion['table'],
                    'columns': suggestion['columns'],
                    'recommendation': f"Consider adding index on {', '.join(suggestion['columns'])} for {suggestion['table']}",
                    'reason': suggestion['reason']
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting index recommendations: {str(e)}")
            return []

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def track_performance(operation_name: str):
    """Decorator to track function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            metadata = {}
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                metadata['error'] = str(e)
                raise
            finally:
                end_time = time.time()
                performance_monitor.track_operation(
                    operation_name, start_time, end_time, success, metadata
                )
        
        return wrapper
    return decorator












