"""
User Preferences API Routes
Handles user-specific module configurations and preferences
"""

from flask import Blueprint, request, jsonify
from app import db
from .user_preferences_models import UserPreferences
from .tenant_context import require_tenant
import logging

logger = logging.getLogger(__name__)

# Create blueprint
user_preferences_bp = Blueprint('user_preferences', __name__, url_prefix='/api/user-preferences')

@user_preferences_bp.route('/', methods=['GET'])
# @require_tenant  # Temporarily disabled for development
# @require_permission('user.preferences.read')  # Temporarily disabled for development
def get_user_preferences():
    """Get current user's preferences"""
    try:
        # Extract user ID from JWT token directly (development mode)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            import jwt
            # Decode JWT token to get user info
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('sub') or payload.get('user_id') or 'user_1'
        except:
            # Fallback for simple tokens
            user_id = 'user_1'
        
        preferences = UserPreferences.get_user_preferences(user_id)
        
        if not preferences:
            # Create default preferences for new user
            preferences = UserPreferences.create_or_update(
                user_id=user_id,
                selected_modules=['financials', 'inventory', 'crm', 'procurement'],
                industry='retail',
                business_size='small',
                company_name='My Company'
            )
        
        return jsonify({
            'status': 'success',
            'preferences': preferences.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return jsonify({'error': 'Failed to get user preferences'}), 500

@user_preferences_bp.route('/', methods=['POST', 'PUT'])
# @require_tenant  # Temporarily disabled for development
def update_user_preferences():
    """Update current user's preferences"""
    try:
        # Extract user ID from JWT token directly (development mode)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            import jwt
            # Decode JWT token to get user info
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('sub') or payload.get('user_id') or 'user_1'
        except:
            # Fallback for simple tokens
            user_id = 'user_1'
        
        data = request.get_json() or {}
        
        # Update preferences
        preferences = UserPreferences.create_or_update(user_id, **data)
        
        return jsonify({
            'status': 'success',
            'message': 'Preferences updated successfully',
            'preferences': preferences.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        return jsonify({'error': 'Failed to update user preferences'}), 500

@user_preferences_bp.route('/modules', methods=['GET'])
@require_tenant
def get_user_modules():
    """Get current user's enabled modules"""
    try:
        from .tenant_context import get_tenant_context
        tenant_context = get_tenant_context()
        user_id = tenant_context.user_id
        
        preferences = UserPreferences.get_user_preferences(user_id)
        
        if not preferences:
            # Return default modules for new user
            default_modules = ['financials', 'inventory', 'crm', 'procurement']
            return jsonify({
                'status': 'success',
                'modules': default_modules,
                'is_default': True
            }), 200
        
        modules = preferences.get_selected_modules()
        return jsonify({
            'status': 'success',
            'modules': modules,
            'is_default': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user modules: {e}")
        return jsonify({'error': 'Failed to get user modules'}), 500

@user_preferences_bp.route('/modules', methods=['POST'])
@require_tenant
def update_user_modules():
    """Update current user's enabled modules"""
    try:
        from .tenant_context import get_tenant_context
        tenant_context = get_tenant_context()
        user_id = tenant_context.user_id
        
        data = request.get_json() or {}
        modules = data.get('modules', [])
        
        if not isinstance(modules, list):
            return jsonify({'error': 'Modules must be a list'}), 400
        
        # Update modules
        preferences = UserPreferences.create_or_update(
            user_id=user_id,
            selected_modules=modules
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Modules updated successfully',
            'modules': preferences.get_selected_modules()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating user modules: {e}")
        return jsonify({'error': 'Failed to update user modules'}), 500

@user_preferences_bp.route('/dashboard', methods=['GET'])
@require_tenant
def get_dashboard_preferences():
    """Get current user's dashboard preferences"""
    try:
        from .tenant_context import get_tenant_context
        tenant_context = get_tenant_context()
        user_id = tenant_context.user_id
        
        preferences = UserPreferences.get_user_preferences(user_id)
        
        if not preferences:
            return jsonify({
                'status': 'success',
                'dashboard': {},
                'is_default': True
            }), 200
        
        dashboard_layout = preferences.get_dashboard_layout()
        return jsonify({
            'status': 'success',
            'dashboard': dashboard_layout,
            'is_default': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard preferences: {e}")
        return jsonify({'error': 'Failed to get dashboard preferences'}), 500

@user_preferences_bp.route('/dashboard', methods=['POST'])
@require_tenant
def update_dashboard_preferences():
    """Update current user's dashboard preferences"""
    try:
        from .tenant_context import get_tenant_context
        tenant_context = get_tenant_context()
        user_id = tenant_context.user_id
        
        data = request.get_json() or {}
        dashboard_layout = data.get('dashboard', {})
        
        # Update dashboard layout
        preferences = UserPreferences.create_or_update(
            user_id=user_id,
            dashboard_layout=dashboard_layout
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Dashboard preferences updated successfully',
            'dashboard': preferences.get_dashboard_layout()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating dashboard preferences: {e}")
        return jsonify({'error': 'Failed to update dashboard preferences'}), 500

@user_preferences_bp.route('/reset', methods=['POST'])
@require_tenant
def reset_user_preferences():
    """Reset current user's preferences to defaults"""
    try:
        from .tenant_context import get_tenant_context
        tenant_context = get_tenant_context()
        user_id = tenant_context.user_id
        
        # Reset to default preferences
        preferences = UserPreferences.create_or_update(
            user_id=user_id,
            selected_modules=['financials', 'inventory', 'crm', 'procurement'],
            industry='retail',
            business_size='small',
            company_name='My Company',
            theme='light',
            language='en',
            default_currency='USD',
            timezone='UTC',
            date_format='YYYY-MM-DD',
            notifications_enabled=True,
            module_settings={},
            dashboard_layout={}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Preferences reset to defaults',
            'preferences': preferences.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error resetting user preferences: {e}")
        return jsonify({'error': 'Failed to reset user preferences'}), 500

