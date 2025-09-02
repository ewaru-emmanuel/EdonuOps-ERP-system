from flask import Blueprint, request, jsonify
from datetime import datetime
import time

# Import enterprise systems
from .concurrency_management import concurrency_manager
from .recovery_audit import recovery_audit_system
from .performance_optimization import performance_optimizer
from .api_ecosystem import api_ecosystem

# Create Blueprint
enterprise_bp = Blueprint('enterprise', __name__)

# ============================================================================
# CONCURRENCY & RACE CONDITION MANAGEMENT
# ============================================================================

@enterprise_bp.route('/api/enterprise/concurrency/stock-adjustment', methods=['POST'])
def process_stock_adjustment_with_locking():
    """Process stock adjustment with full concurrency protection"""
    try:
        start_time = time.time()
        
        data = request.get_json()
        
        # Process with concurrency protection
        result = concurrency_manager.process_stock_adjustment_with_locking(data)
        
        # Create immutable transaction record
        if result['success']:
            transaction_data = {
                'type': 'stock_adjustment',
                'user_id': data.get('user_id'),
                'data': data,
                'result': result
            }
            
            audit_result = recovery_audit_system.create_immutable_transaction(transaction_data)
            
            # Trigger webhook event
            api_ecosystem.trigger_webhook_event('inventory.adjustment_created', {
                'adjustment_id': result.get('transaction_id'),
                'item_id': data.get('item_id'),
                'quantity': data.get('quantity')
            })
        
        response_time = time.time() - start_time
        api_ecosystem.track_api_request('/api/enterprise/concurrency/stock-adjustment', response_time)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing stock adjustment: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/concurrency/metrics', methods=['GET'])
def get_concurrency_metrics():
    """Get concurrency performance metrics"""
    try:
        metrics = concurrency_manager.get_concurrency_metrics()
        return jsonify(metrics), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting concurrency metrics: {str(e)}'
        }), 500

# ============================================================================
# RECOVERY & AUDIT SYSTEM
# ============================================================================

@enterprise_bp.route('/api/enterprise/recovery/create-point', methods=['POST'])
def create_recovery_point():
    """Create a point-in-time recovery snapshot"""
    try:
        data = request.get_json()
        result = recovery_audit_system.create_recovery_point(
            description=data.get('description', 'Manual recovery point'),
            user_id=data.get('user_id', 'system')
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creating recovery point: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/recovery/audit-trail', methods=['GET'])
def get_audit_trail():
    """Get comprehensive audit trail"""
    try:
        transaction_id = request.args.get('transaction_id')
        result = recovery_audit_system.get_audit_trail(transaction_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting audit trail: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/recovery/integrity-report', methods=['GET'])
def get_system_integrity_report():
    """Get system integrity report"""
    try:
        result = recovery_audit_system.get_system_integrity_report()
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting integrity report: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/recovery/void-transaction', methods=['POST'])
def void_transaction():
    """Void a transaction by creating a reversing entry"""
    try:
        data = request.get_json()
        result = recovery_audit_system.void_transaction(
            transaction_id=data['transaction_id'],
            void_reason=data['void_reason'],
            user_id=data['user_id']
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error voiding transaction: {str(e)}'
        }), 500

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

@enterprise_bp.route('/api/enterprise/performance/materialized-view', methods=['POST'])
def create_materialized_view():
    """Create or refresh materialized view"""
    try:
        data = request.get_json()
        result = performance_optimizer.create_materialized_view(
            view_name=data['view_name'],
            query_data=data.get('query_data', {})
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creating materialized view: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/performance/materialized-view/<view_name>', methods=['GET'])
def get_materialized_view(view_name):
    """Get materialized view data"""
    try:
        result = performance_optimizer.get_materialized_view(view_name)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting materialized view: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/performance/optimized-valuation', methods=['GET'])
def get_optimized_inventory_valuation():
    """Get optimized inventory valuation using materialized views"""
    try:
        start_time = time.time()
        
        result = performance_optimizer.optimize_inventory_valuation_query()
        
        response_time = time.time() - start_time
        api_ecosystem.track_api_request('/api/enterprise/performance/optimized-valuation', response_time)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting optimized valuation: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/performance/metrics', methods=['GET'])
def get_performance_metrics():
    """Get performance optimization metrics"""
    try:
        result = performance_optimizer.get_performance_metrics()
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting performance metrics: {str(e)}'
        }), 500

# ============================================================================
# API ECOSYSTEM & WEBHOOKS
# ============================================================================

@enterprise_bp.route('/api/enterprise/webhooks/register', methods=['POST'])
def register_webhook():
    """Register a new webhook subscription"""
    try:
        data = request.get_json()
        result = api_ecosystem.register_webhook(data)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error registering webhook: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/webhooks/trigger', methods=['POST'])
def trigger_webhook_event():
    """Manually trigger webhook event"""
    try:
        data = request.get_json()
        result = api_ecosystem.trigger_webhook_event(
            event_type=data['event_type'],
            event_data=data['event_data']
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error triggering webhook: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/api-keys/create', methods=['POST'])
def create_api_key():
    """Create new API key for external integrations"""
    try:
        data = request.get_json()
        result = api_ecosystem.create_api_key(data)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creating API key: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/api-keys/validate', methods=['POST'])
def validate_api_key():
    """Validate API key and check rate limits"""
    try:
        data = request.get_json()
        result = api_ecosystem.validate_api_key(data['api_key'])
        
        return jsonify(result), 200 if result['valid'] else 401
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Error validating API key: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/analytics', methods=['GET'])
def get_api_analytics():
    """Get comprehensive API analytics"""
    try:
        result = api_ecosystem.get_api_analytics()
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting analytics: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/documentation', methods=['GET'])
def get_api_documentation():
    """Get API documentation for developers"""
    try:
        result = api_ecosystem.get_api_documentation()
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting documentation: {str(e)}'
        }), 500

# ============================================================================
# ENTERPRISE HEALTH & MONITORING
# ============================================================================

@enterprise_bp.route('/api/enterprise/health/status', methods=['GET'])
def get_enterprise_health_status():
    """Get comprehensive enterprise system health status"""
    try:
        # Collect health metrics from all systems
        concurrency_metrics = concurrency_manager.get_concurrency_metrics()
        performance_metrics = performance_optimizer.get_performance_metrics()
        api_analytics = api_ecosystem.get_api_analytics()
        integrity_report = recovery_audit_system.get_system_integrity_report()
        
        # Determine overall system health
        system_health = 'HEALTHY'
        issues = []
        
        # Check concurrency
        if concurrency_metrics.get('active_locks', 0) > 10:
            system_health = 'DEGRADED'
            issues.append('High number of active locks detected')
        
        # Check performance
        if performance_metrics.get('success') and performance_metrics.get('performance_metrics', {}).get('average_query_time_seconds', 0) > 1.0:
            system_health = 'DEGRADED'
            issues.append('Slow query performance detected')
        
        # Check API health
        if api_analytics.get('success') and api_analytics.get('analytics', {}).get('total_requests', 0) > 10000:
            system_health = 'DEGRADED'
            issues.append('High API request volume')
        
        # Check data integrity
        if integrity_report.get('success') and integrity_report.get('integrity_report', {}).get('system_health') != 'HEALTHY':
            system_health = 'CRITICAL'
            issues.append('Data integrity issues detected')
        
        health_status = {
            'success': True,
            'system_health': system_health,
            'timestamp': datetime.utcnow().isoformat(),
            'issues': issues,
            'metrics': {
                'concurrency': concurrency_metrics,
                'performance': performance_metrics.get('performance_metrics', {}) if performance_metrics.get('success') else {},
                'api_analytics': api_analytics.get('analytics', {}) if api_analytics.get('success') else {},
                'integrity': integrity_report.get('integrity_report', {}) if integrity_report.get('success') else {}
            }
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'system_health': 'UNKNOWN',
            'error': f'Error getting health status: {str(e)}'
        }), 500

@enterprise_bp.route('/api/enterprise/health/alerts', methods=['GET'])
def get_enterprise_alerts():
    """Get active enterprise system alerts"""
    try:
        alerts = []
        
        # Check for concurrency issues
        concurrency_metrics = concurrency_manager.get_concurrency_metrics()
        if concurrency_metrics.get('active_locks', 0) > 5:
            alerts.append({
                'type': 'CONCURRENCY',
                'severity': 'WARNING',
                'message': f"High number of active locks: {concurrency_metrics.get('active_locks')}",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for performance issues
        performance_metrics = performance_optimizer.get_performance_metrics()
        if performance_metrics.get('success'):
            avg_time = performance_metrics.get('performance_metrics', {}).get('average_query_time_seconds', 0)
            if avg_time > 0.5:
                alerts.append({
                    'type': 'PERFORMANCE',
                    'severity': 'WARNING',
                    'message': f"Slow average query time: {avg_time:.3f}s",
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        # Check for API issues
        api_analytics = api_ecosystem.get_api_analytics()
        if api_analytics.get('success'):
            total_requests = api_analytics.get('analytics', {}).get('total_requests', 0)
            if total_requests > 5000:
                alerts.append({
                    'type': 'API',
                    'severity': 'INFO',
                    'message': f"High API request volume: {total_requests} requests",
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_alerts': len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting alerts: {str(e)}'
        }), 500
