"""
Enterprise Monitoring Service
SAP/Oracle-style monitoring and health checks
"""

import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import current_app

class MonitoringService:
    """Enterprise monitoring and health check service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.utcnow()
        self.metrics = {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': self.get_uptime(),
            'system_resources': self.get_system_resources(),
            'database_status': self.get_database_status(),
            'api_status': self.get_api_status(),
            'memory_usage': self.get_memory_usage(),
            'cpu_usage': self.get_cpu_usage(),
            'disk_usage': self.get_disk_usage()
        }
    
    def get_uptime(self) -> str:
        """Get application uptime"""
        uptime = datetime.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': self.get_network_io()
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage details"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'free': memory.free
        }
    
    def get_cpu_usage(self) -> Dict[str, Any]:
        """Get CPU usage details"""
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage details"""
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }
    
    def get_network_io(self) -> Dict[str, Any]:
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception as e:
            self.logger.error(f"Error getting network I/O: {e}")
            return {}
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get database connection status"""
        try:
            from app import db
            # Try to execute a simple query
            db.session.execute('SELECT 1')
            return {
                'status': 'connected',
                'type': 'sqlite',  # This should be dynamic based on config
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'disconnected',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API endpoints status"""
        return {
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'api': '/api',
                'test': '/test'
            },
            'last_check': datetime.utcnow().isoformat()
        }
    
    def log_metric(self, metric_name: str, value: Any, tags: Dict[str, str] = None):
        """Log a custom metric"""
        self.metrics[metric_name] = {
            'value': value,
            'timestamp': datetime.utcnow().isoformat(),
            'tags': tags or {}
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all logged metrics"""
        return self.metrics
    
    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'overall_status': 'healthy',
            'checks': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check system resources
        memory = self.get_memory_usage()
        if memory['percent'] > 90:
            health_status['checks']['memory'] = {'status': 'critical', 'message': 'High memory usage'}
            health_status['overall_status'] = 'degraded'
        elif memory['percent'] > 80:
            health_status['checks']['memory'] = {'status': 'warning', 'message': 'Elevated memory usage'}
        else:
            health_status['checks']['memory'] = {'status': 'healthy', 'message': 'Normal memory usage'}
        
        # Check CPU
        cpu = self.get_cpu_usage()
        if cpu['percent'] > 90:
            health_status['checks']['cpu'] = {'status': 'critical', 'message': 'High CPU usage'}
            health_status['overall_status'] = 'degraded'
        elif cpu['percent'] > 80:
            health_status['checks']['cpu'] = {'status': 'warning', 'message': 'Elevated CPU usage'}
        else:
            health_status['checks']['cpu'] = {'status': 'healthy', 'message': 'Normal CPU usage'}
        
        # Check disk
        disk = self.get_disk_usage()
        if disk['percent'] > 90:
            health_status['checks']['disk'] = {'status': 'critical', 'message': 'High disk usage'}
            health_status['overall_status'] = 'degraded'
        elif disk['percent'] > 80:
            health_status['checks']['disk'] = {'status': 'warning', 'message': 'Elevated disk usage'}
        else:
            health_status['checks']['disk'] = {'status': 'healthy', 'message': 'Normal disk usage'}
        
        # Check database
        db_status = self.get_database_status()
        if db_status['status'] == 'connected':
            health_status['checks']['database'] = {'status': 'healthy', 'message': 'Database connected'}
        else:
            health_status['checks']['database'] = {'status': 'critical', 'message': 'Database disconnected'}
            health_status['overall_status'] = 'unhealthy'
        
        return health_status

