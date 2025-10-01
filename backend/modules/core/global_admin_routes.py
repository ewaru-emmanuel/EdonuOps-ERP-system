# backend/modules/core/global_admin_routes.py

from flask import Blueprint, request, jsonify, g
from app import db
from modules.core.tenant_models import Tenant, UserTenant, TenantModule
from modules.core.audit_models import AuditLog, TenantUsageStats, PlatformMetrics
from modules.core.audit_service import audit_service
from modules.core.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date
import json

global_admin_bp = Blueprint('global_admin', __name__)

def require_superadmin(f):
    """Decorator to require superadmin access"""
    def decorated_function(*args, **kwargs):
        # Check if user is superadmin
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role_id != 1:  # Assuming role_id 1 is superadmin
            return jsonify({"message": "Superadmin access required"}), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@global_admin_bp.route('/api/admin/tenants', methods=['GET'])
@jwt_required()
@require_superadmin
def list_tenants():
    """Get all tenants with their details"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get tenants with pagination
        tenants_query = Tenant.query.order_by(Tenant.created_at.desc())
        tenants_paginated = tenants_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        tenants_data = []
        for tenant in tenants_paginated.items:
            # Get user count for this tenant
            user_count = UserTenant.query.filter_by(tenant_id=tenant.id).count()
            
            # Get module count
            module_count = TenantModule.query.filter_by(tenant_id=tenant.id, enabled=True).count()
            
            # Get recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_activity = AuditLog.query.filter(
                AuditLog.tenant_id == tenant.id,
                AuditLog.timestamp >= week_ago
            ).count()
            
            # Get today's usage stats
            today_stats = TenantUsageStats.query.filter_by(
                tenant_id=tenant.id, 
                date=date.today()
            ).first()
            
            tenants_data.append({
                'id': tenant.id,
                'name': tenant.name,
                'domain': tenant.domain,
                'subscription_plan': tenant.subscription_plan,
                'status': tenant.status,
                'user_count': user_count,
                'module_count': module_count,
                'recent_activity': recent_activity,
                'api_calls_today': today_stats.api_calls if today_stats else 0,
                'errors_today': today_stats.errors_count if today_stats else 0,
                'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
                'last_activity': tenant.last_activity.isoformat() if tenant.last_activity else None
            })
        
        return jsonify({
            'tenants': tenants_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tenants_paginated.total,
                'pages': tenants_paginated.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to fetch tenants',
            'error': str(e)
        }), 500

@global_admin_bp.route('/api/admin/tenants/<tenant_id>', methods=['GET'])
@jwt_required()
@require_superadmin
def get_tenant_details(tenant_id):
    """Get detailed information about a specific tenant"""
    try:
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'message': 'Tenant not found'}), 404
        
        # Get users for this tenant
        user_tenants = UserTenant.query.filter_by(tenant_id=tenant_id).all()
        users_data = []
        for ut in user_tenants:
            user = User.query.get(ut.user_id)
            if user:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': ut.role,
                    'is_default': ut.is_default,
                    'joined_at': ut.created_at.isoformat() if ut.created_at else None
                })
        
        # Get modules for this tenant
        modules = TenantModule.query.filter_by(tenant_id=tenant_id).all()
        modules_data = [{
            'name': m.module_name,
            'enabled': m.enabled,
            'activated_at': m.activated_at.isoformat() if m.activated_at else None,
            'activated_by': m.activated_by
        } for m in modules]
        
        # Get usage stats for last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        usage_stats = TenantUsageStats.query.filter(
            TenantUsageStats.tenant_id == tenant_id,
            TenantUsageStats.date >= thirty_days_ago
        ).order_by(TenantUsageStats.date.desc()).all()
        
        # Get recent audit logs
        recent_logs = audit_service.get_tenant_audit_logs(tenant_id, limit=50)
        
        return jsonify({
            'tenant': {
                'id': tenant.id,
                'name': tenant.name,
                'domain': tenant.domain,
                'subscription_plan': tenant.subscription_plan,
                'status': tenant.status,
                'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
                'last_activity': tenant.last_activity.isoformat() if tenant.last_activity else None
            },
            'users': users_data,
            'modules': modules_data,
            'usage_stats': [s.to_dict() for s in usage_stats],
            'recent_activity': [log.to_dict() for log in recent_logs]
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to fetch tenant details',
            'error': str(e)
        }), 500

@global_admin_bp.route('/api/admin/platform-metrics', methods=['GET'])
@jwt_required()
@require_superadmin
def get_platform_metrics():
    """Get platform-wide metrics"""
    try:
        # Get today's metrics
        today_metrics = PlatformMetrics.query.filter_by(date=date.today()).first()
        
        # Get metrics for last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        historical_metrics = PlatformMetrics.query.filter(
            PlatformMetrics.date >= thirty_days_ago
        ).order_by(PlatformMetrics.date.desc()).all()
        
        # Get recent errors
        recent_errors = audit_service.get_recent_errors(limit=20)
        
        # Get top tenants by activity
        top_tenants = db.session.query(
            Tenant.id, Tenant.name, Tenant.subscription_plan,
            db.func.count(AuditLog.id).label('activity_count')
        ).join(AuditLog, Tenant.id == AuditLog.tenant_id)\
         .filter(AuditLog.timestamp >= datetime.utcnow() - timedelta(days=7))\
         .group_by(Tenant.id, Tenant.name, Tenant.subscription_plan)\
         .order_by(db.func.count(AuditLog.id).desc())\
         .limit(10).all()
        
        return jsonify({
            'today_metrics': today_metrics.to_dict() if today_metrics else None,
            'historical_metrics': [m.to_dict() for m in historical_metrics],
            'recent_errors': [log.to_dict() for log in recent_errors],
            'top_tenants': [{
                'id': t.id,
                'name': t.name,
                'subscription_plan': t.subscription_plan,
                'activity_count': t.activity_count
            } for t in top_tenants]
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to fetch platform metrics',
            'error': str(e)
        }), 500

@global_admin_bp.route('/api/admin/audit-logs', methods=['GET'])
@jwt_required()
@require_superadmin
def get_audit_logs():
    """Get audit logs with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        tenant_id = request.args.get('tenant_id')
        user_id = request.args.get('user_id')
        action = request.args.get('action')
        severity = request.args.get('severity')
        days = request.args.get('days', 7, type=int)
        
        # Build query
        query = AuditLog.query
        
        # Apply filters
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if action:
            query = query.filter_by(action=action)
        if severity:
            query = query.filter_by(severity=severity)
        
        # Date filter
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AuditLog.timestamp >= start_date)
        
        # Order and paginate
        query = query.order_by(AuditLog.timestamp.desc())
        logs_paginated = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logs_paginated.total,
                'pages': logs_paginated.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to fetch audit logs',
            'error': str(e)
        }), 500

@global_admin_bp.route('/api/admin/audit-logs/export', methods=['GET'])
@jwt_required()
@require_superadmin
def export_audit_logs():
    """Export audit logs as CSV"""
    try:
        # Get filter parameters
        tenant_id = request.args.get('tenant_id')
        days = request.args.get('days', 30, type=int)
        
        # Build query
        query = AuditLog.query
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AuditLog.timestamp >= start_date)
        
        logs = query.order_by(AuditLog.timestamp.desc()).limit(10000).all()
        
        # Convert to CSV format
        csv_data = []
        csv_data.append('timestamp,tenant_id,user_id,action,resource,resource_id,severity,module,ip_address')
        
        for log in logs:
            csv_data.append(f"{log.timestamp},{log.tenant_id},{log.user_id},{log.action},{log.resource},{log.resource_id},{log.severity},{log.module},{log.ip_address}")
        
        return jsonify({
            'csv_data': '\n'.join(csv_data),
            'total_records': len(logs)
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to export audit logs',
            'error': str(e)
        }), 500

@global_admin_bp.route('/api/admin/tenants/<tenant_id>/suspend', methods=['POST'])
@jwt_required()
@require_superadmin
def suspend_tenant(tenant_id):
    """Suspend a tenant"""
    try:
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'message': 'Tenant not found'}), 404
        
        tenant.status = 'suspended'
        db.session.commit()
        
        # Log the action
        audit_service.log_action(
            'SUSPEND_TENANT', 'tenant', tenant_id,
            {'suspended_by': get_jwt_identity()}, 'WARNING'
        )
        
        return jsonify({'message': 'Tenant suspended successfully'}), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to suspend tenant',
            'error': str(e)
        }), 500

@global_admin_bp.route('/api/admin/tenants/<tenant_id>/activate', methods=['POST'])
@jwt_required()
@require_superadmin
def activate_tenant(tenant_id):
    """Activate a suspended tenant"""
    try:
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'message': 'Tenant not found'}), 404
        
        tenant.status = 'active'
        db.session.commit()
        
        # Log the action
        audit_service.log_action(
            'ACTIVATE_TENANT', 'tenant', tenant_id,
            {'activated_by': get_jwt_identity()}, 'INFO'
        )
        
        return jsonify({'message': 'Tenant activated successfully'}), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to activate tenant',
            'error': str(e)
        }), 500












