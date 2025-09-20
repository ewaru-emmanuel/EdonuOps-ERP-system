from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from app import db
from modules.core.audit_models import AuditLog, LoginHistory, PermissionChange, SystemEvent
from services.audit_logger_service import audit_logger
from modules.core.permissions import require_permission

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@require_permission('system.audit.read')
def get_audit_logs():
    """Get audit logs with filtering and pagination"""
    try:
        # Parse query parameters
        user_id = request.args.get('user_id', type=int)
        module = request.args.get('module')
        action = request.args.get('action')
        entity_type = request.args.get('entity_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = min(request.args.get('limit', 100, type=int), 1000)  # Max 1000
        offset = request.args.get('offset', 0, type=int)
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get audit logs
        result = audit_logger.get_audit_logs(
            user_id=user_id,
            module=module,
            action=action,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'data': result['logs'],
            'pagination': {
                'total': result['total_count'],
                'offset': result['offset'],
                'limit': result['limit'],
                'has_more': result['offset'] + result['limit'] < result['total_count']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audit_bp.route('/login-history', methods=['GET'])
@jwt_required()
@require_permission('system.audit.read')
def get_login_history():
    """Get login history with filtering and pagination"""
    try:
        # Parse query parameters
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get login history
        result = audit_logger.get_login_history(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'data': result['logs'],
            'pagination': {
                'total': result['total_count'],
                'offset': result['offset'],
                'limit': result['limit'],
                'has_more': result['offset'] + result['limit'] < result['total_count']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audit_bp.route('/permission-changes', methods=['GET'])
@jwt_required()
@require_permission('system.audit.read')
def get_permission_changes():
    """Get permission changes with filtering and pagination"""
    try:
        # Parse query parameters
        admin_user_id = request.args.get('admin_user_id', type=int)
        target_user_id = request.args.get('target_user_id', type=int)
        change_type = request.args.get('change_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Build query
        query = db.session.query(PermissionChange)
        
        if admin_user_id:
            query = query.filter(PermissionChange.admin_user_id == admin_user_id)
        if target_user_id:
            query = query.filter(PermissionChange.target_user_id == target_user_id)
        if change_type:
            query = query.filter(PermissionChange.change_type == change_type)
        if start_date:
            query = query.filter(PermissionChange.timestamp >= start_date)
        if end_date:
            query = query.filter(PermissionChange.timestamp <= end_date)
        
        # Order and paginate
        total_count = query.count()
        changes = query.order_by(desc(PermissionChange.timestamp)).offset(offset).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [change.to_dict() for change in changes],
            'pagination': {
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audit_bp.route('/system-events', methods=['GET'])
@jwt_required()
@require_permission('system.audit.read')
def get_system_events():
    """Get system events with filtering and pagination"""
    try:
        # Parse query parameters
        event_type = request.args.get('event_type')
        event_category = request.args.get('event_category')
        severity = request.args.get('severity')
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Build query
        query = db.session.query(SystemEvent)
        
        if event_type:
            query = query.filter(SystemEvent.event_type == event_type)
        if event_category:
            query = query.filter(SystemEvent.event_category == event_category)
        if severity:
            query = query.filter(SystemEvent.severity == severity)
        if user_id:
            query = query.filter(SystemEvent.user_id == user_id)
        if start_date:
            query = query.filter(SystemEvent.timestamp >= start_date)
        if end_date:
            query = query.filter(SystemEvent.timestamp <= end_date)
        
        # Order and paginate
        total_count = query.count()
        events = query.order_by(desc(SystemEvent.timestamp)).offset(offset).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [event.to_dict() for event in events],
            'pagination': {
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audit_bp.route('/security-summary', methods=['GET'])
@jwt_required()
@require_permission('system.audit.read')
def get_security_summary():
    """Get security summary for dashboard"""
    try:
        days = request.args.get('days', 30, type=int)
        
        summary = audit_logger.get_security_summary(days=days)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audit_bp.route('/audit-stats', methods=['GET'])
@jwt_required()
@require_permission('system.audit.read')
def get_audit_stats():
    """Get audit statistics for analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        
        # Activity by module
        module_stats = db.session.query(
            AuditLog.module,
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= cutoff_date
        ).group_by(AuditLog.module).all()
        
        # Activity by action
        action_stats = db.session.query(
            AuditLog.action,
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= cutoff_date
        ).group_by(AuditLog.action).all()
        
        # Daily activity
        daily_activity = db.session.query(
            db.func.date(AuditLog.timestamp).label('date'),
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= cutoff_date
        ).group_by(db.func.date(AuditLog.timestamp)).all()
        
        # Top users
        top_users = db.session.query(
            AuditLog.username,
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= cutoff_date,
            AuditLog.username.isnot(None)
        ).group_by(AuditLog.username).order_by(
            db.func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'module_stats': [{'module': m[0], 'count': m[1]} for m in module_stats],
                'action_stats': [{'action': a[0], 'count': a[1]} for a in action_stats],
                'daily_activity': [{'date': str(d[0]), 'count': d[1]} for d in daily_activity],
                'top_users': [{'username': u[0], 'count': u[1]} for u in top_users],
                'period_days': days
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audit_bp.route('/export-audit-logs', methods=['POST'])
@jwt_required()
@require_permission('system.audit.export')
def export_audit_logs():
    """Export audit logs to CSV format"""
    try:
        data = request.get_json() or {}
        
        # Parse filters
        user_id = data.get('user_id')
        module = data.get('module')
        action = data.get('action')
        entity_type = data.get('entity_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get all matching logs (no pagination for export)
        result = audit_logger.get_audit_logs(
            user_id=user_id,
            module=module,
            action=action,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date,
            limit=10000,  # Large limit for export
            offset=0
        )
        
        # For now, return JSON data (CSV conversion can be done on frontend)
        return jsonify({
            'success': True,
            'data': result['logs'],
            'export_info': {
                'total_records': result['total_count'],
                'exported_at': datetime.utcnow().isoformat(),
                'filters_applied': {
                    'user_id': user_id,
                    'module': module,
                    'action': action,
                    'entity_type': entity_type,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
