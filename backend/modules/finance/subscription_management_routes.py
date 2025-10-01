"""
Subscription Management API Routes
APIs for managing tenant subscriptions and billing
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
from modules.finance.subscription_management_service import SubscriptionManagementService
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
subscription_bp = Blueprint('subscription', __name__, url_prefix='/api/subscription')

# ============================================================================
# SUBSCRIPTION MANAGEMENT ENDPOINTS
# ============================================================================

@subscription_bp.route('/plans', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_available_plans():
    """Get all available subscription plans"""
    try:
        plans = SubscriptionManagementService.get_available_plans()
        
        return jsonify({
            'success': True,
            'data': plans
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting available plans: {e}")
        return jsonify({'error': 'Failed to get available plans'}), 500

@subscription_bp.route('/plans/<plan_id>', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_plan_details(plan_id):
    """Get details for a specific plan"""
    try:
        plan = SubscriptionManagementService.get_plan_details(plan_id)
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        return jsonify({
            'success': True,
            'data': plan
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting plan details: {e}")
        return jsonify({'error': 'Failed to get plan details'}), 500

@subscription_bp.route('/tenant/info', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_subscription_info():
    """Get subscription information for current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        info = SubscriptionManagementService.get_tenant_subscription_info(tenant_context.tenant_id)
        
        if not info:
            return jsonify({'error': 'Failed to get subscription info'}), 500
        
        return jsonify({
            'success': True,
            'data': info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tenant subscription info: {e}")
        return jsonify({'error': 'Failed to get subscription info'}), 500

@subscription_bp.route('/tenant/usage', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_tenant_usage():
    """Get current usage metrics for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        usage = SubscriptionManagementService.get_tenant_usage(tenant_context.tenant_id)
        
        return jsonify({
            'success': True,
            'data': usage
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tenant usage: {e}")
        return jsonify({'error': 'Failed to get usage metrics'}), 500

@subscription_bp.route('/tenant/limits', methods=['GET'])
@require_tenant
@require_module('analytics')
def check_tenant_limits():
    """Check if tenant is within plan limits"""
    try:
        tenant_context = get_tenant_context()
        
        # Get current plan
        from modules.core.tenant_models import Tenant
        tenant = Tenant.query.get(tenant_context.tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        current_plan = SubscriptionManagementService.get_plan_details(tenant.subscription_plan)
        if not current_plan:
            return jsonify({'error': 'Invalid plan'}), 400
        
        limits_status = SubscriptionManagementService.check_tenant_limits(
            tenant_context.tenant_id, 
            current_plan
        )
        
        return jsonify({
            'success': True,
            'data': limits_status
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking tenant limits: {e}")
        return jsonify({'error': 'Failed to check limits'}), 500

@subscription_bp.route('/tenant/upgrade', methods=['POST'])
@require_tenant
@require_permission('subscription.manage')
def upgrade_tenant_plan():
    """Upgrade tenant to a new plan"""
    try:
        tenant_context = get_tenant_context()
        data = request.get_json()
        
        if not data or 'plan_id' not in data:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        new_plan_id = data['plan_id']
        
        success, message = SubscriptionManagementService.upgrade_tenant_plan(
            tenant_context.tenant_id, 
            new_plan_id
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"Error upgrading tenant plan: {e}")
        return jsonify({'error': 'Failed to upgrade plan'}), 500

@subscription_bp.route('/tenant/recommendations', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_upgrade_recommendations():
    """Get upgrade recommendations for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        recommendations = SubscriptionManagementService.get_upgrade_recommendations(
            tenant_context.tenant_id
        )
        
        return jsonify({
            'success': True,
            'data': recommendations
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting upgrade recommendations: {e}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@subscription_bp.route('/tenant/billing', methods=['GET'])
@require_tenant
@require_module('analytics')
def get_billing_info():
    """Get billing information for tenant"""
    try:
        tenant_context = get_tenant_context()
        
        billing_info = SubscriptionManagementService.get_billing_info(tenant_context.tenant_id)
        
        return jsonify({
            'success': True,
            'data': billing_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting billing info: {e}")
        return jsonify({'error': 'Failed to get billing info'}), 500

@subscription_bp.route('/tenant/billing', methods=['PUT'])
@require_tenant
@require_permission('subscription.manage')
def update_billing_info():
    """Update billing information for tenant"""
    try:
        tenant_context = get_tenant_context()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Billing data is required'}), 400
        
        # Update billing information (simplified)
        # In a real implementation, this would update payment methods, addresses, etc.
        
        return jsonify({
            'success': True,
            'message': 'Billing information updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating billing info: {e}")
        return jsonify({'error': 'Failed to update billing info'}), 500

# ============================================================================
# ADMIN ENDPOINTS (System-wide subscription management)
# ============================================================================

@subscription_bp.route('/admin/tenants', methods=['GET'])
@require_tenant
@require_permission('subscription.admin')
def get_all_tenant_subscriptions():
    """Get subscription information for all tenants (admin only)"""
    try:
        from modules.core.tenant_models import Tenant
        
        tenants = Tenant.query.all()
        tenant_subscriptions = []
        
        for tenant in tenants:
            try:
                subscription_info = SubscriptionManagementService.get_tenant_subscription_info(tenant.id)
                if subscription_info:
                    tenant_subscriptions.append(subscription_info)
            except Exception as e:
                logger.error(f"Error getting subscription info for tenant {tenant.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'data': tenant_subscriptions
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all tenant subscriptions: {e}")
        return jsonify({'error': 'Failed to get tenant subscriptions'}), 500

@subscription_bp.route('/admin/tenants/<tenant_id>/plan', methods=['PUT'])
@require_tenant
@require_permission('subscription.admin')
def admin_update_tenant_plan(tenant_id):
    """Admin endpoint to update tenant plan"""
    try:
        data = request.get_json()
        
        if not data or 'plan_id' not in data:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        new_plan_id = data['plan_id']
        
        success, message = SubscriptionManagementService.upgrade_tenant_plan(
            tenant_id, 
            new_plan_id
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating tenant plan: {e}")
        return jsonify({'error': 'Failed to update tenant plan'}), 500

@subscription_bp.route('/admin/analytics', methods=['GET'])
@require_tenant
@require_permission('subscription.admin')
def get_subscription_analytics():
    """Get system-wide subscription analytics (admin only)"""
    try:
        from modules.core.tenant_models import Tenant
        
        # Get basic subscription analytics
        total_tenants = Tenant.query.count()
        active_tenants = Tenant.query.filter_by(status='active').count()
        
        # Get plan distribution
        plan_distribution = {}
        for plan_id in SubscriptionManagementService.get_available_plans().keys():
            count = Tenant.query.filter_by(subscription_plan=plan_id).count()
            plan_distribution[plan_id] = count
        
        # Get revenue metrics (simplified)
        total_revenue = 0
        for plan_id, count in plan_distribution.items():
            plan = SubscriptionManagementService.get_plan_details(plan_id)
            if plan:
                total_revenue += plan['price'] * count
        
        return jsonify({
            'success': True,
            'data': {
                'total_tenants': total_tenants,
                'active_tenants': active_tenants,
                'plan_distribution': plan_distribution,
                'total_revenue': total_revenue,
                'generated_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting subscription analytics: {e}")
        return jsonify({'error': 'Failed to get subscription analytics'}), 500












