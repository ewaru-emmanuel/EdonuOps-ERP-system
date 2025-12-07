"""
Analytics API Routes
Provides comprehensive reconciliation analytics and insights
"""

from flask import Blueprint, request, jsonify, current_app
from modules.core.permissions import require_permission
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
import logging
from .analytics_service import reconciliation_analytics
from .performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/finance/analytics')

@analytics_bp.route('/trends', methods=['GET'])
@require_permission('finance.reports.read')
def get_trends():
    """Get reconciliation trends over time"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty trends (for development)
        if not user_id:
            print("Warning: No user context found for trends, returning empty results")
            return jsonify({
                'success': True,
                'trends': []
            }), 200
        
        days = request.args.get('days', 30, type=int)
        trends = reconciliation_analytics.get_reconciliation_trends(days, user_id)
        
        return jsonify({
            'success': True,
            'trends': trends
        })
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/account-performance', methods=['GET'])
@require_permission('finance.reports.read')
def get_account_performance():
    """Get performance metrics for bank accounts"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty performance (for development)
        if not user_id:
            print("Warning: No user context found for account performance, returning empty results")
            return jsonify({
                'success': True,
                'performance': {}
            }), 200
        
        bank_account_id = request.args.get('account_id', type=int)
        performance = reconciliation_analytics.get_account_performance(bank_account_id, user_id)
        
        return jsonify({
            'success': True,
            'performance': performance
        })
    except Exception as e:
        logger.error(f"Error getting account performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/discrepancy-analysis', methods=['GET'])
@require_permission('finance.reports.read')
def get_discrepancy_analysis():
    """Analyze reconciliation discrepancies"""
    try:
        days = request.args.get('days', 30, type=int)
        analysis = reconciliation_analytics.get_discrepancy_analysis(days)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error getting discrepancy analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/matching-efficiency', methods=['GET'])
@require_permission('finance.reports.read')
def get_matching_efficiency():
    """Analyze transaction matching efficiency"""
    try:
        days = request.args.get('days', 30, type=int)
        efficiency = reconciliation_analytics.get_matching_efficiency(days)
        
        return jsonify({
            'success': True,
            'efficiency': efficiency
        })
    except Exception as e:
        logger.error(f"Error getting matching efficiency: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/optimization-recommendations', methods=['GET'])
@require_permission('finance.reports.read')
def get_optimization_recommendations():
    """Get optimization recommendations"""
    try:
        recommendations = reconciliation_analytics.get_optimization_recommendations()
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        logger.error(f"Error getting optimization recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/performance-metrics', methods=['GET'])
@require_permission('finance.reports.read')
def get_performance_metrics():
    """Get system performance metrics"""
    try:
        metrics = performance_monitor.get_system_performance()
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/bottlenecks', methods=['GET'])
@require_permission('finance.reports.read')
def get_bottlenecks():
    """Identify performance bottlenecks"""
    try:
        bottlenecks = performance_monitor.identify_performance_bottlenecks()
        
        return jsonify({
            'success': True,
            'bottlenecks': bottlenecks
        })
    except Exception as e:
        logger.error(f"Error getting bottlenecks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/cache-stats', methods=['GET'])
@require_permission('finance.reports.read')
def get_cache_stats():
    """Get cache statistics"""
    try:
        from .caching_service import reconciliation_cache
        stats = reconciliation_cache.get_cache_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/dashboard-summary', methods=['GET'])
@require_permission('finance.reports.read')
def get_dashboard_summary():
    """Get comprehensive dashboard summary"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty summary (for development)
        if not user_id:
            print("Warning: No user context found for analytics dashboard, returning empty results")
            return jsonify({
                'trends': [],
                'account_performance': [],
                'discrepancy_analysis': {},
                'matching_efficiency': {},
                'optimization_recommendations': [],
                'performance_metrics': {}
            }), 200
        
        days = request.args.get('days', 30, type=int)
        
        # Get all analytics data
        trends = reconciliation_analytics.get_reconciliation_trends(days)
        account_performance = reconciliation_analytics.get_account_performance()
        discrepancy_analysis = reconciliation_analytics.get_discrepancy_analysis(days)
        matching_efficiency = reconciliation_analytics.get_matching_efficiency(days)
        optimization_recommendations = reconciliation_analytics.get_optimization_recommendations()
        performance_metrics = performance_monitor.get_system_performance()
        
        summary = {
            'trends': trends,
            'account_performance': account_performance,
            'discrepancy_analysis': discrepancy_analysis,
            'matching_efficiency': matching_efficiency,
            'optimization_recommendations': optimization_recommendations,
            'performance_metrics': performance_metrics,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export-report', methods=['POST'])
@require_permission('finance.reports.read')
def export_report():
    """Export analytics report"""
    try:
        data = request.get_json()
        report_type = data.get('type', 'comprehensive')
        format_type = data.get('format', 'json')
        date_range = data.get('date_range', 30)
        
        # Generate report data
        if report_type == 'comprehensive':
            report_data = {
                'trends': reconciliation_analytics.get_reconciliation_trends(date_range),
                'account_performance': reconciliation_analytics.get_account_performance(),
                'discrepancy_analysis': reconciliation_analytics.get_discrepancy_analysis(date_range),
                'matching_efficiency': reconciliation_analytics.get_matching_efficiency(date_range),
                'optimization_recommendations': reconciliation_analytics.get_optimization_recommendations()
            }
        elif report_type == 'performance':
            report_data = performance_monitor.get_system_performance()
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        # Add metadata
        report_data['metadata'] = {
            'generated_at': datetime.utcnow().isoformat(),
            'generated_by': get_jwt_identity(),
            'report_type': report_type,
            'date_range': date_range,
            'format': format_type
        }
        
        if format_type == 'json':
            return jsonify({
                'success': True,
                'report': report_data
            })
        else:
            # For other formats, you would implement conversion logic
            return jsonify({'error': 'Format not supported yet'}), 400
            
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/quick-actions', methods=['GET'])
@require_permission('finance.reports.read')
def get_quick_actions():
    """Get quick actions for mobile interface"""
    try:
        actions = [
            {
                'id': 'start_reconciliation',
                'title': 'Start Reconciliation',
                'description': 'Begin new reconciliation process',
                'icon': 'AccountBalance',
                'color': 'primary',
                'endpoint': '/api/finance/reconciliation-sessions'
            },
            {
                'id': 'sync_accounts',
                'title': 'Sync Accounts',
                'description': 'Sync bank account data',
                'icon': 'Sync',
                'color': 'secondary',
                'endpoint': '/api/finance/bank-feed/sync-transactions'
            },
            {
                'id': 'auto_match',
                'title': 'Auto Match',
                'description': 'Automatically match transactions',
                'icon': 'CompareArrows',
                'color': 'success',
                'endpoint': '/api/finance/auto-match'
            },
            {
                'id': 'generate_report',
                'title': 'Generate Report',
                'description': 'Create reconciliation report',
                'icon': 'Assessment',
                'color': 'info',
                'endpoint': '/api/finance/analytics/export-report'
            }
        ]
        
        return jsonify({
            'success': True,
            'actions': actions
        })
    except Exception as e:
        logger.error(f"Error getting quick actions: {str(e)}")
        return jsonify({'error': str(e)}), 500








