"""
Rate Limiting API Routes
APIs for monitoring and managing rate limits
"""

from flask import Blueprint, request, jsonify, g
from app import db
from datetime import datetime, timedelta
from modules.core.tenant_context import (
    require_tenant, 
    get_tenant_context, 
    require_permission
)
from modules.core.rate_limiting import rate_limiting_service
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
rate_limiting_bp = Blueprint('rate_limiting', __name__, url_prefix='/api/rate-limiting')

# ============================================================================
# RATE LIMITING MONITORING ENDPOINTS
# ============================================================================

@rate_limiting_bp.route('/status', methods=['GET'])
@require_tenant
@require_permission('analytics.view')
def get_rate_limit_status():
    """Get current rate limit status for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        status = rate_limiting_service.get_rate_limit_status(
            tenant_id=tenant_context.tenant_id
        )
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return jsonify({'error': 'Failed to get rate limit status'}), 500

@rate_limiting_bp.route('/tenant/<tenant_id>/status', methods=['GET'])
@require_tenant
@require_permission('admin.rate_limiting.view')
def get_tenant_rate_limit_status(tenant_id):
    """Get rate limit status for specific tenant (admin only)"""
    try:
        status = rate_limiting_service.get_rate_limit_status(tenant_id=tenant_id)
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tenant rate limit status: {e}")
        return jsonify({'error': 'Failed to get tenant rate limit status'}), 500

@rate_limiting_bp.route('/reset', methods=['POST'])
@require_tenant
@require_permission('admin.rate_limiting.manage')
def reset_rate_limits():
    """Reset rate limits for current tenant"""
    try:
        tenant_context = get_tenant_context()
        data = request.get_json() or {}
        
        # Get reset options
        reset_tenant = data.get('reset_tenant', True)
        reset_endpoint = data.get('reset_endpoint', False)
        reset_ip = data.get('reset_ip', False)
        
        success = rate_limiting_service.reset_rate_limits(
            tenant_id=tenant_context.tenant_id if reset_tenant else None,
            endpoint=data.get('endpoint') if reset_endpoint else None,
            ip=data.get('ip') if reset_ip else None
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Rate limits reset successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to reset rate limits'}), 500
        
    except Exception as e:
        logger.error(f"Error resetting rate limits: {e}")
        return jsonify({'error': 'Failed to reset rate limits'}), 500

@rate_limiting_bp.route('/tenant/<tenant_id>/reset', methods=['POST'])
@require_tenant
@require_permission('admin.rate_limiting.manage')
def reset_tenant_rate_limits(tenant_id):
    """Reset rate limits for specific tenant (admin only)"""
    try:
        success = rate_limiting_service.reset_rate_limits(tenant_id=tenant_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Rate limits reset for tenant {tenant_id}'
            }), 200
        else:
            return jsonify({'error': 'Failed to reset tenant rate limits'}), 500
        
    except Exception as e:
        logger.error(f"Error resetting tenant rate limits: {e}")
        return jsonify({'error': 'Failed to reset tenant rate limits'}), 500

@rate_limiting_bp.route('/analytics', methods=['GET'])
@require_tenant
@require_permission('analytics.view')
def get_rate_limiting_analytics():
    """Get rate limiting analytics for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        # Get rate limit status
        status = rate_limiting_service.get_rate_limit_status(
            tenant_id=tenant_context.tenant_id
        )
        
        # Calculate usage percentages
        analytics = {
            'tenant_id': tenant_context.tenant_id,
            'current_usage': status.get('tenant_limits', {}),
            'usage_percentages': {},
            'recommendations': [],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Calculate usage percentages
        tenant_limits = status.get('tenant_limits', {})
        if tenant_limits:
            minute_usage = (tenant_limits.get('minute_count', 0) / tenant_limits.get('minute_limit', 60)) * 100
            hour_usage = (tenant_limits.get('hour_count', 0) / tenant_limits.get('hour_limit', 1000)) * 100
            
            analytics['usage_percentages'] = {
                'minute_usage': round(minute_usage, 2),
                'hour_usage': round(hour_usage, 2)
            }
            
            # Generate recommendations
            if minute_usage > 80:
                analytics['recommendations'].append({
                    'type': 'warning',
                    'message': 'High minute usage detected. Consider optimizing API calls.',
                    'action': 'Review API usage patterns'
                })
            
            if hour_usage > 80:
                analytics['recommendations'].append({
                    'type': 'warning',
                    'message': 'High hour usage detected. Consider upgrading plan.',
                    'action': 'Contact support for plan upgrade'
                })
            
            if minute_usage > 95:
                analytics['recommendations'].append({
                    'type': 'critical',
                    'message': 'Rate limit nearly exceeded. Immediate action required.',
                    'action': 'Reduce API call frequency'
                })
        
        return jsonify({
            'success': True,
            'data': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting rate limiting analytics: {e}")
        return jsonify({'error': 'Failed to get rate limiting analytics'}), 500

@rate_limiting_bp.route('/config', methods=['GET'])
@require_tenant
@require_permission('admin.rate_limiting.view')
def get_rate_limiting_config():
    """Get rate limiting configuration"""
    try:
        config = {
            'tenant_limits': {
                'requests_per_minute': 60,
                'requests_per_hour': 1000,
                'description': 'Tenant-based rate limiting'
            },
            'endpoint_limits': {
                'sensitive_endpoints': 20,
                'api_endpoints': 100,
                'public_endpoints': 50,
                'admin_endpoints': 200,
                'description': 'Endpoint-specific rate limiting'
            },
            'ip_limits': {
                'requests_per_minute': 100,
                'description': 'IP-based rate limiting'
            },
            'storage': {
                'type': 'redis' if rate_limiting_service.redis_client else 'memory',
                'description': 'Rate limiting storage backend'
            }
        }
        
        return jsonify({
            'success': True,
            'data': config
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting rate limiting config: {e}")
        return jsonify({'error': 'Failed to get rate limiting config'}), 500

@rate_limiting_bp.route('/health', methods=['GET'])
@require_tenant
@require_permission('admin.rate_limiting.view')
def get_rate_limiting_health():
    """Get rate limiting system health"""
    try:
        health = {
            'status': 'healthy',
            'redis_connected': rate_limiting_service.redis_client is not None,
            'storage_type': 'redis' if rate_limiting_service.redis_client else 'memory',
            'limiter_initialized': rate_limiting_service.limiter is not None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Test Redis connection if available
        if rate_limiting_service.redis_client:
            try:
                rate_limiting_service.redis_client.ping()
                health['redis_status'] = 'connected'
            except Exception as e:
                health['redis_status'] = 'disconnected'
                health['redis_error'] = str(e)
                health['status'] = 'degraded'
        
        return jsonify({
            'success': True,
            'data': health
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting rate limiting health: {e}")
        return jsonify({'error': 'Failed to get rate limiting health'}), 500

# ============================================================================
# RATE LIMITING MIDDLEWARE
# ============================================================================

@rate_limiting_bp.before_request
def rate_limiting_middleware():
    """Rate limiting middleware for all requests"""
    try:
        # Skip rate limiting for certain endpoints
        if request.endpoint in ['rate_limiting.health', 'rate_limiting.config']:
            return
        
        # Apply basic rate limiting
        # This is handled by the decorators on individual routes
        pass
        
    except Exception as e:
        logger.error(f"Error in rate limiting middleware: {e}")
        # Don't block requests if rate limiting fails
        pass

# ============================================================================
# RATE LIMITING ALERTS
# ============================================================================

@rate_limiting_bp.route('/alerts', methods=['GET'])
@require_tenant
@require_permission('analytics.view')
def get_rate_limiting_alerts():
    """Get rate limiting alerts for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        # Get current status
        status = rate_limiting_service.get_rate_limit_status(
            tenant_id=tenant_context.tenant_id
        )
        
        alerts = []
        tenant_limits = status.get('tenant_limits', {})
        
        if tenant_limits:
            minute_count = tenant_limits.get('minute_count', 0)
            minute_limit = tenant_limits.get('minute_limit', 60)
            hour_count = tenant_limits.get('hour_count', 0)
            hour_limit = tenant_limits.get('hour_limit', 1000)
            
            # Generate alerts based on usage
            if minute_count > minute_limit * 0.9:
                alerts.append({
                    'type': 'critical',
                    'message': f'Minute rate limit nearly exceeded: {minute_count}/{minute_limit}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'action_required': True
                })
            
            if hour_count > hour_limit * 0.9:
                alerts.append({
                    'type': 'warning',
                    'message': f'Hour rate limit nearly exceeded: {hour_count}/{hour_limit}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'action_required': False
                })
            
            if minute_count >= minute_limit:
                alerts.append({
                    'type': 'error',
                    'message': f'Minute rate limit exceeded: {minute_count}/{minute_limit}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'action_required': True
                })
            
            if hour_count >= hour_limit:
                alerts.append({
                    'type': 'error',
                    'message': f'Hour rate limit exceeded: {hour_count}/{hour_limit}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'action_required': True
                })
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['type'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['type'] == 'warning']),
                'error_alerts': len([a for a in alerts if a['type'] == 'error'])
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting rate limiting alerts: {e}")
        return jsonify({'error': 'Failed to get rate limiting alerts'}), 500












