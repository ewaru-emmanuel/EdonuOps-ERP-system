from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from app import db
from modules.core.security_models import SecurityPolicy, PasswordHistory, UserSession, AccountLockout, TwoFactorAuth, SecurityEvent
from services.security_service import security_service
from modules.core.permissions import require_permission

security_bp = Blueprint('security_management', __name__)

# Security Policies Routes
@security_bp.route('/policies', methods=['GET'])
@jwt_required()
@require_permission('system.security.read')
def get_security_policies():
    """Get all security policies"""
    try:
        policies = SecurityPolicy.query.all()
        return jsonify({
            'success': True,
            'data': [policy.to_dict() for policy in policies]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/policies/<policy_name>', methods=['GET'])
@jwt_required()
@require_permission('system.security.read')
def get_security_policy(policy_name):
    """Get specific security policy"""
    try:
        policy = SecurityPolicy.query.filter_by(policy_name=policy_name).first()
        if not policy:
            return jsonify({
                'success': False,
                'error': 'Policy not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': policy.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/policies', methods=['POST'])
@jwt_required()
@require_permission('system.security.update')
def update_security_policy():
    """Update security policy"""
    try:
        data = request.get_json()
        policy_name = data.get('policy_name')
        policy_type = data.get('policy_type')
        configuration = data.get('configuration')
        is_enabled = data.get('is_enabled', True)
        
        if not policy_name or not policy_type or not configuration:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Get or create policy
        policy = SecurityPolicy.query.filter_by(policy_name=policy_name).first()
        if not policy:
            policy = SecurityPolicy(
                policy_name=policy_name,
                policy_type=policy_type,
                configuration=configuration,
                is_enabled=is_enabled,
                created_by=get_jwt_identity()
            )
            db.session.add(policy)
        else:
            policy.configuration = configuration
            policy.is_enabled = is_enabled
            policy.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Policy updated successfully',
            'data': policy.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Password Validation Routes
@security_bp.route('/validate-password', methods=['POST'])
@jwt_required()
def validate_password():
    """Validate password against security policy"""
    try:
        data = request.get_json()
        password = data.get('password')
        username = data.get('username')
        user_id = data.get('user_id')
        
        if not password:
            return jsonify({
                'success': False,
                'error': 'Password is required'
            }), 400
        
        is_valid, errors = security_service.validate_password(password, username, user_id)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Session Management Routes
@security_bp.route('/sessions', methods=['GET'])
@jwt_required()
@require_permission('system.security.read')
def get_user_sessions():
    """Get user sessions"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            user_id = get_jwt_identity()
        
        sessions = UserSession.query.filter_by(user_id=user_id).order_by(desc(UserSession.created_at)).all()
        
        return jsonify({
            'success': True,
            'data': [session.to_dict() for session in sessions]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/sessions/<session_id>', methods=['DELETE'])
@jwt_required()
def terminate_session(session_id):
    """Terminate a specific session"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user can terminate this session
        session = UserSession.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Users can only terminate their own sessions (or admins can terminate any)
        if session.user_id != current_user_id:
            # Check if user has admin permissions
            from modules.core.permissions import user_has_permission
            if not user_has_permission(current_user_id, 'system.security.manage'):
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions'
                }), 403
        
        success = security_service.invalidate_session(session_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session terminated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to terminate session'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/sessions/terminate-all', methods=['POST'])
@jwt_required()
def terminate_all_sessions():
    """Terminate all sessions for current user"""
    try:
        user_id = get_jwt_identity()
        success = security_service.invalidate_all_user_sessions(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'All sessions terminated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to terminate sessions'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Two-Factor Authentication Routes
@security_bp.route('/2fa/setup', methods=['POST'])
@jwt_required()
def setup_two_factor_auth():
    """Setup 2FA for current user"""
    try:
        user_id = get_jwt_identity()
        
        success, secret_key, qr_uri = security_service.setup_two_factor_auth(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'data': {
                    'secret_key': secret_key,
                    'qr_uri': qr_uri
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to setup 2FA'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/2fa/verify', methods=['POST'])
@jwt_required()
def verify_two_factor_token():
    """Verify 2FA token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is required'
            }), 400
        
        user_id = get_jwt_identity()
        is_valid = security_service.verify_two_factor_token(user_id, token)
        
        if is_valid:
            # Enable 2FA after verification
            security_service.enable_two_factor_auth(user_id)
            
            return jsonify({
                'success': True,
                'message': '2FA verified and enabled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/2fa/status', methods=['GET'])
@jwt_required()
def get_two_factor_status():
    """Get 2FA status for current user"""
    try:
        user_id = get_jwt_identity()
        
        two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        
        if two_factor:
            return jsonify({
                'success': True,
                'data': {
                    'is_enabled': two_factor.is_enabled,
                    'is_setup': bool(two_factor.secret_key),
                    'created_at': two_factor.created_at.isoformat() if two_factor.created_at else None,
                    'last_used': two_factor.last_used.isoformat() if two_factor.last_used else None
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'is_enabled': False,
                    'is_setup': False,
                    'created_at': None,
                    'last_used': None
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/2fa/disable', methods=['POST'])
@jwt_required()
def disable_two_factor_auth():
    """Disable 2FA for current user"""
    try:
        user_id = get_jwt_identity()
        
        # Require password confirmation for security
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'success': False,
                'error': 'Password confirmation is required'
            }), 400
        
        # Verify password
        from modules.core.models import User
        from werkzeug.security import check_password_hash
        
        user = User.query.get(user_id)
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({
                'success': False,
                'error': 'Invalid password'
            }), 400
        
        success = security_service.disable_two_factor_auth(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '2FA disabled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to disable 2FA'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Security Events Routes
@security_bp.route('/events', methods=['GET'])
@jwt_required()
@require_permission('system.security.read')
def get_security_events():
    """Get security events"""
    try:
        # Parse query parameters
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        user_id = request.args.get('user_id', type=int)
        resolved = request.args.get('resolved')
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = SecurityEvent.query
        
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        if severity:
            query = query.filter(SecurityEvent.severity == severity)
        if user_id:
            query = query.filter(SecurityEvent.user_id == user_id)
        if resolved is not None:
            query = query.filter(SecurityEvent.resolved == (resolved.lower() == 'true'))
        
        # Order and paginate
        total_count = query.count()
        events = query.order_by(desc(SecurityEvent.created_at)).offset(offset).limit(limit).all()
        
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

@security_bp.route('/events/<int:event_id>/resolve', methods=['POST'])
@jwt_required()
@require_permission('system.security.manage')
def resolve_security_event(event_id):
    """Resolve a security event"""
    try:
        event = SecurityEvent.query.get(event_id)
        if not event:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        event.resolved = True
        event.resolved_at = datetime.utcnow()
        event.resolved_by = get_jwt_identity()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Event resolved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Account Lockout Management
@security_bp.route('/lockouts', methods=['GET'])
@jwt_required()
@require_permission('system.security.read')
def get_account_lockouts():
    """Get account lockout information"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        if user_id:
            lockouts = AccountLockout.query.filter_by(user_id=user_id).order_by(desc(AccountLockout.locked_at)).all()
        else:
            # Get all active lockouts
            lockouts = AccountLockout.query.filter(
                AccountLockout.unlocked_at.is_(None)
            ).order_by(desc(AccountLockout.locked_at)).all()
        
        return jsonify({
            'success': True,
            'data': [lockout.to_dict() for lockout in lockouts]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/lockouts/<int:lockout_id>/unlock', methods=['POST'])
@jwt_required()
@require_permission('system.security.manage')
def unlock_account(lockout_id):
    """Unlock an account"""
    try:
        lockout = AccountLockout.query.get(lockout_id)
        if not lockout:
            return jsonify({
                'success': False,
                'error': 'Lockout record not found'
            }), 404
        
        lockout.unlocked_at = datetime.utcnow()
        lockout.unlocked_by = get_jwt_identity()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account unlocked successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
