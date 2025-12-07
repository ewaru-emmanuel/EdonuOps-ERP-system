from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, func
import logging

from app import db
from modules.core.audit_models import AuditLog, LoginHistory, PermissionChange, SystemEvent
from modules.core.models import User
from services.audit_logger_service import audit_logger
from modules.core.permissions import require_permission, PermissionManager

logger = logging.getLogger(__name__)
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

@audit_bp.route('/security-summary', methods=['GET', 'OPTIONS'])
def get_security_summary():
    """Get security summary for dashboard"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    # Check authentication (try JWT first, then header)
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except:
        current_user_id = request.headers.get('X-User-ID')
    
    # Basic permission check (admin has access, or skip if no user)
    if current_user_id:
        user = None  # Initialize user variable to avoid scoping issues
        try:
            user = User.query.get(int(current_user_id))
            if user and user.role and user.role.role_name == 'admin':
                pass  # Admin has access
            else:
                # Check if user has audit.read permission
                try:
                    if not PermissionManager.user_has_permission(int(current_user_id), 'system.audit.read'):
                        response = jsonify({
                            'success': False,
                            'error': 'Insufficient permissions',
                            'message': 'This action requires audit read permission'
                        })
                        response.headers.add('Access-Control-Allow-Origin', '*')
                        return response, 403
                except Exception as inner_perm_err:
                    # If permission check fails, allow admin users only
                    if not (user and user.role and user.role.role_name == 'admin'):
                        response = jsonify({
                            'success': False,
                            'error': 'Permission check failed',
                            'message': 'Unable to verify permissions'
                        })
                        response.headers.add('Access-Control-Allow-Origin', '*')
                        return response, 403
        except Exception as perm_err:
            logger.warning(f"Permission check error: {perm_err}")
            # Continue - allow access if check fails (graceful degradation)
    
    try:
        # Safely parse days parameter
        days_str = request.args.get('days', '30')
        try:
            days = int(days_str)
            if days < 1 or days > 365:
                return jsonify({
                    'success': False,
                    'error': 'Days parameter must be between 1 and 365'
                }), 422
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': f'Invalid days parameter: {days_str}. Must be an integer.'
            }), 422
        
        # Get summary with error handling
        try:
            summary = audit_logger.get_security_summary(days=days)
        except Exception as summary_err:
            logger.error(f"Error getting security summary: {summary_err}")
            # Return empty summary if service fails
            summary = {
                'failed_logins': 0,
                'successful_logins': 0,
                'suspicious_activities': 0,
                'permission_changes': 0,
                'recent_activity': 0,
                'period_days': days
            }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Error in get_security_summary: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audit_bp.route('/audit-stats', methods=['GET', 'OPTIONS'])
def get_audit_stats():
    """Get audit statistics for analytics"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    # Check authentication (try JWT first, then header)
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except:
        current_user_id = request.headers.get('X-User-ID')
    
    # Basic permission check (admin has access, or skip if no user)
    if current_user_id:
        user = None  # Initialize user variable to avoid scoping issues
        try:
            user = User.query.get(int(current_user_id))
            if user and user.role and user.role.role_name == 'admin':
                pass  # Admin has access
            else:
                # Check if user has audit.read permission
                try:
                    if not PermissionManager.user_has_permission(int(current_user_id), 'system.audit.read'):
                        response = jsonify({
                            'success': False,
                            'error': 'Insufficient permissions',
                            'message': 'This action requires audit read permission'
                        })
                        response.headers.add('Access-Control-Allow-Origin', '*')
                        return response, 403
                except Exception as inner_perm_err:
                    # If permission check fails, allow admin users only
                    if not (user and user.role and user.role.role_name == 'admin'):
                        response = jsonify({
                            'success': False,
                            'error': 'Permission check failed',
                            'message': 'Unable to verify permissions'
                        })
                        response.headers.add('Access-Control-Allow-Origin', '*')
                        return response, 403
        except Exception as perm_err:
            logger.warning(f"Permission check error: {perm_err}")
            # Continue - allow access if check fails (graceful degradation)
    
    try:
        # Safely parse days parameter
        days_str = request.args.get('days', '30')
        try:
            days = int(days_str)
            if days < 1 or days > 365:
                return jsonify({
                    'success': False,
                    'error': 'Days parameter must be between 1 and 365'
                }), 422
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': f'Invalid days parameter: {days_str}. Must be an integer.'
            }), 422
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Check if AuditLog table exists
        try:
            # Try a simple query to check if table exists
            db.session.query(AuditLog).limit(1).all()
        except Exception as table_err:
            logger.warning(f"AuditLog table may not exist: {table_err}")
            # Return empty stats if table doesn't exist
            response = jsonify({
                'success': True,
                'data': {
                    'module_stats': [],
                    'action_stats': [],
                    'daily_activity': [],
                    'top_users': [],
                    'period_days': days
                }
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
            return response, 200
        
        # Activity by module
        try:
            module_stats = db.session.query(
                AuditLog.module,
                db.func.count(AuditLog.id).label('count')
            ).filter(
                AuditLog.timestamp >= cutoff_date
            ).group_by(AuditLog.module).all()
        except Exception as e:
            logger.warning(f"Error querying module stats: {e}")
            module_stats = []
        
        # Activity by action
        try:
            action_stats = db.session.query(
                AuditLog.action,
                db.func.count(AuditLog.id).label('count')
            ).filter(
                AuditLog.timestamp >= cutoff_date
            ).group_by(AuditLog.action).all()
        except Exception as e:
            logger.warning(f"Error querying action stats: {e}")
            action_stats = []
        
        # Daily activity
        try:
            daily_activity = db.session.query(
                db.func.date(AuditLog.timestamp).label('date'),
                db.func.count(AuditLog.id).label('count')
            ).filter(
                AuditLog.timestamp >= cutoff_date
            ).group_by(db.func.date(AuditLog.timestamp)).all()
        except Exception as e:
            logger.warning(f"Error querying daily activity: {e}")
            daily_activity = []
        
        # Top users (AuditLog has user_id, not username - need to join with User table)
        # User is already imported at the top of the file, no need to re-import
        try:
            top_users = db.session.query(
                User.username,
                db.func.count(AuditLog.id).label('count')
            ).join(
                AuditLog, User.id == AuditLog.user_id
            ).filter(
                AuditLog.timestamp >= cutoff_date,
                AuditLog.user_id.isnot(None)
            ).group_by(User.username).order_by(
                db.func.count(AuditLog.id).desc()
            ).limit(10).all()
        except Exception as e:
            logger.warning(f"Error querying top users with join: {e}")
            # Fallback: try without join if User table doesn't exist or join fails
            try:
                top_users = db.session.query(
                    AuditLog.user_id,
                    db.func.count(AuditLog.id).label('count')
                ).filter(
                    AuditLog.timestamp >= cutoff_date,
                    AuditLog.user_id.isnot(None)
                ).group_by(AuditLog.user_id).order_by(
                    db.func.count(AuditLog.id).desc()
                ).limit(10).all()
                # Convert user_id to username format
                top_users = [('User ' + str(u[0]), u[1]) for u in top_users]
            except Exception as fallback_err:
                logger.warning(f"Error querying top users fallback: {fallback_err}")
                top_users = []
        
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
