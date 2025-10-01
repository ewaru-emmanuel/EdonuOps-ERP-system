"""
Tenant Analytics API Routes
APIs for tenant-specific analytics and reporting
"""

from flask import Blueprint, request, jsonify, g
from app import db
from datetime import datetime, timedelta
from modules.core.tenant_context import (
    require_tenant, 
    get_tenant_context, 
    require_permission,
    require_module
)
from modules.finance.tenant_analytics_service import TenantAnalyticsService
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
tenant_analytics_bp = Blueprint('tenant_analytics', __name__, url_prefix='/api/analytics')

# ============================================================================
# TENANT ANALYTICS ENDPOINTS
# ============================================================================

@tenant_analytics_bp.route('/tenant/overview', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_overview():
    """Get comprehensive tenant overview"""
    try:
        tenant_context = get_tenant_context()
        
        overview = TenantAnalyticsService.get_tenant_overview(tenant_context.tenant_id)
        
        if not overview:
            return jsonify({'error': 'Failed to generate tenant overview'}), 500
        
        return jsonify({
            'success': True,
            'data': overview
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tenant overview: {e}")
        return jsonify({'error': 'Failed to get tenant overview'}), 500

@tenant_analytics_bp.route('/tenant/finance-metrics', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_finance_metrics():
    """Get finance metrics for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        metrics = TenantAnalyticsService.get_finance_metrics(tenant_context.tenant_id)
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting finance metrics: {e}")
        return jsonify({'error': 'Failed to get finance metrics'}), 500

@tenant_analytics_bp.route('/tenant/usage-metrics', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_usage_metrics():
    """Get usage metrics for tenant"""
    try:
        tenant_context = get_tenant_context();
        
        metrics = TenantAnalyticsService.get_usage_metrics(tenant_context.tenant_id)
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting usage metrics: {e}")
        return jsonify({'error': 'Failed to get usage metrics'}), 500

@tenant_analytics_bp.route('/tenant/performance-metrics', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_performance_metrics():
    """Get performance metrics for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        metrics = TenantAnalyticsService.get_performance_metrics(tenant_context.tenant_id)
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({'error': 'Failed to get performance metrics'}), 500

@tenant_analytics_bp.route('/tenant/recent-activity', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_recent_activity():
    """Get recent activity for tenant"""
    try:
        tenant_context = get_tenant_context()
        limit = request.args.get('limit', 10, type=int)
        
        activities = TenantAnalyticsService.get_recent_activity(
            tenant_context.tenant_id, 
            limit
        )
        
        return jsonify({
            'success': True,
            'data': activities
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return jsonify({'error': 'Failed to get recent activity'}), 500

@tenant_analytics_bp.route('/tenant/trends', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_trends():
    """Get trends for tenant"""
    try:
        tenant_context = get_tenant_context()
        days = request.args.get('days', 30, type=int)
        
        trends = TenantAnalyticsService.get_tenant_trends(tenant_context.tenant_id, days)
        
        return jsonify({
            'success': True,
            'data': trends
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tenant trends: {e}")
        return jsonify({'error': 'Failed to get tenant trends'}), 500

@tenant_analytics_bp.route('/tenant/comparison', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_comparison():
    """Compare tenant metrics with system averages"""
    try:
        tenant_context = get_tenant_context()
        
        comparison = TenantAnalyticsService.get_tenant_comparison(tenant_context.tenant_id)
        
        return jsonify({
            'success': True,
            'data': comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tenant comparison: {e}")
        return jsonify({'error': 'Failed to get tenant comparison'}), 500

@tenant_analytics_bp.route('/tenant/report', methods=['GET'])
@require_tenant
@require_module('analytics')
def generate_tenant_report():
    """Generate tenant report"""
    try:
        tenant_context = get_tenant_context()
        report_type = request.args.get('type', 'comprehensive')
        
        report = TenantAnalyticsService.generate_tenant_report(
            tenant_context.tenant_id, 
            report_type
        )
        
        if not report:
            return jsonify({'error': 'Failed to generate report'}), 500
        
        return jsonify({
            'success': True,
            'data': report,
            'report_type': report_type,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating tenant report: {e}")
        return jsonify({'error': 'Failed to generate report'}), 500

# ============================================================================
# SYSTEM-WIDE ANALYTICS (Admin Only)
# ============================================================================

@tenant_analytics_bp.route('/system/overview', methods=['GET'])
@require_tenant
@require_permission('analytics.system.view')
def get_system_overview():
    """Get system-wide analytics overview (admin only)"""
    try:
        # This would typically require admin permissions
        # For now, return basic system metrics
        
        from modules.core.tenant_models import Tenant, UserTenant, TenantModule
        
        # System metrics
        total_tenants = Tenant.query.count()
        active_tenants = Tenant.query.filter_by(status='active').count()
        total_users = UserTenant.query.count()
        total_modules = TenantModule.query.count()
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_tenants = Tenant.query.filter(
            Tenant.created_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'tenants': {
                    'total': total_tenants,
                    'active': active_tenants,
                    'recent': recent_tenants
                },
                'users': {
                    'total': total_users
                },
                'modules': {
                    'total': total_modules
                },
                'generated_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system overview: {e}")
        return jsonify({'error': 'Failed to get system overview'}), 500

@tenant_analytics_bp.route('/system/tenant-performance', methods=['GET'])
@require_tenant
@require_permission('analytics.system.view')
def get_system_tenant_performance():
    """Get performance metrics for all tenants (admin only)"""
    try:
        from modules.core.tenant_models import Tenant
        
        # Get all tenants with basic metrics
        tenants = Tenant.query.all()
        
        tenant_performance = []
        for tenant in tenants:
            try:
                overview = TenantAnalyticsService.get_tenant_overview(tenant.id)
                if overview:
                    tenant_performance.append({
                        'tenant_id': tenant.id,
                        'tenant_name': tenant.name,
                        'subscription_plan': tenant.subscription_plan,
                        'status': tenant.status,
                        'metrics': overview.get('finance_metrics', {}),
                        'usage': overview.get('usage_metrics', {})
                    })
            except Exception as e:
                logger.error(f"Error getting metrics for tenant {tenant.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'data': tenant_performance
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system tenant performance: {e}")
        return jsonify({'error': 'Failed to get system tenant performance'}), 500

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@tenant_analytics_bp.route('/dashboard', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_dashboard_data():
    """Get comprehensive dashboard data for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        # Get all dashboard data in parallel
        overview = TenantAnalyticsService.get_tenant_overview(tenant_context.tenant_id)
        trends = TenantAnalyticsService.get_tenant_trends(tenant_context.tenant_id, 30)
        comparison = TenantAnalyticsService.get_tenant_comparison(tenant_context.tenant_id)
        
        dashboard_data = {
            'overview': overview,
            'trends': trends,
            'comparison': comparison,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500

@tenant_analytics_bp.route('/dashboard/widgets', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_dashboard_widgets():
    """Get data for specific dashboard widgets"""
    try:
        tenant_context = get_tenant_context()
        widgets = request.args.getlist('widgets')
        
        widget_data = {}
        
        for widget in widgets:
            try:
                if widget == 'finance_summary':
                    widget_data[widget] = TenantAnalyticsService.get_finance_metrics(tenant_context.tenant_id)
                elif widget == 'usage_summary':
                    widget_data[widget] = TenantAnalyticsService.get_usage_metrics(tenant_context.tenant_id)
                elif widget == 'performance_summary':
                    widget_data[widget] = TenantAnalyticsService.get_performance_metrics(tenant_context.tenant_id)
                elif widget == 'recent_activity':
                    widget_data[widget] = TenantAnalyticsService.get_recent_activity(tenant_context.tenant_id, 5)
                elif widget == 'trends':
                    widget_data[widget] = TenantAnalyticsService.get_tenant_trends(tenant_context.tenant_id, 7)
            except Exception as e:
                logger.error(f"Error getting widget data for {widget}: {e}")
                widget_data[widget] = None
        
        return jsonify({
            'success': True,
            'data': widget_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard widgets: {e}")
        return jsonify({'error': 'Failed to get dashboard widgets'}), 500












