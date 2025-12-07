from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.dashboard.models import UserModules, Dashboard, DashboardWidget, WidgetTemplate, DashboardTemplate
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.core.module_permission_service import grant_module_permissions, revoke_module_permissions
import logging

logger = logging.getLogger(__name__)

module_activation_bp = Blueprint('module_activation', __name__)  # Prefix set during registration

# Available modules configuration
AVAILABLE_MODULES = {
    'finance': {
        'name': 'Finance',
        'description': 'Financial management, accounting, and reporting',
        'features': ['general-ledger', 'chart-of-accounts', 'accounts-payable', 'accounts-receivable', 'fixed-assets', 'budgeting', 'tax-management', 'bank-reconciliation', 'financial-reports', 'audit-trail']
    },
    'crm': {
        'name': 'CRM',
        'description': 'Customer relationship management',
        'features': ['contacts', 'leads', 'opportunities', 'pipeline', 'companies', 'activities', 'tasks', 'tickets', 'reports', 'automations']
    },
    'inventory': {
        'name': 'Inventory',
        'description': 'Inventory and warehouse management',
        'features': ['products', 'categories', 'warehouses', 'stock-levels', 'transactions', 'reports', 'settings']
    },
    'procurement': {
        'name': 'Procurement',
        'description': 'Procurement and vendor management',
        'features': ['vendors', 'purchase-orders', 'receiving', 'invoicing', 'contracts', 'reports']
    },
    'hr': {
        'name': 'Human Resources',
        'description': 'Human resources and payroll management',
        'features': ['employees', 'payroll', 'recruitment', 'benefits', 'time-tracking', 'reports']
    },
    'analytics': {
        'name': 'Analytics',
        'description': 'Business intelligence and analytics',
        'features': ['dashboards', 'reports', 'kpis', 'forecasting', 'data-visualization']
    }
}

@module_activation_bp.route('/available', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_available_modules():
    """Get all available modules - JWT REQUIRED"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        # SECURITY: Get user ID from verified JWT token only
        user_id_str = get_jwt_identity()
        
        if not user_id_str:
            print("❌ SECURITY: No user identity in JWT token")
            return jsonify({
                'error': 'Authentication required',
                'message': 'User identity not found in JWT token'
            }), 401
        
        # Convert to int (JWT identity is stored as string)
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID in token'}), 400
        
        # Get user's current modules
        user_modules = UserModules.get_user_modules(user_id)
        user_module_ids = {um.module_id for um in user_modules}
        
        # Return available modules with activation status
        available_modules = []
        for module_id, module_info in AVAILABLE_MODULES.items():
            available_modules.append({
                'id': module_id,
                'name': module_info['name'],
                'description': module_info['description'],
                'features': module_info['features'],
                'is_enabled': module_id in user_module_ids,
                'is_active': module_id in user_module_ids
            })
        
        return jsonify(available_modules), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/user', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_user_modules():
    """Get user's activated modules - JWT REQUIRED"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 200)
    
    try:
        # SECURITY: Get user ID from verified JWT token only
        from flask_jwt_extended import get_jwt_identity
        user_id_str = get_jwt_identity()
        
        if not user_id_str:
            print("❌ SECURITY: No user identity in JWT token")
            return jsonify({
                'error': 'Authentication required',
                'message': 'User identity not found in JWT token'
            }), 401
        
        # Convert to int (JWT identity is stored as string)
        try:
            user_id = int(user_id_str)
            print(f'✅ get_user_modules - User ID from JWT: {user_id}')
        except (ValueError, TypeError) as e:
            print(f'❌ get_user_modules - Invalid user ID format: {user_id_str}, error: {e}')
            return jsonify({'error': 'Invalid user ID in token'}), 400
        
        # SECURITY: Get user's modules (strict user isolation - model filters by user_id)
        print(f'🔍 Fetching modules for user_id={user_id}')
        user_modules = UserModules.get_user_modules(user_id)
        print(f'📊 Found {len(user_modules)} active modules for user {user_id}')
        
        modules_data = []
        for user_module in user_modules:
            module_info = AVAILABLE_MODULES.get(user_module.module_id, {})
            modules_data.append({
                'id': user_module.module_id,
                'name': module_info.get('name', user_module.module_id.title()),
                'description': module_info.get('description', ''),
                'features': module_info.get('features', []),
                'is_enabled': user_module.is_enabled,
                'is_active': user_module.is_active,
                'permissions': user_module.permissions,
                'activated_at': user_module.activated_at.isoformat() if user_module.activated_at else None,
                'created_at': user_module.created_at.isoformat()
            })
        
        print(f'✅ Returning {len(modules_data)} modules for user {user_id}')
        return jsonify(modules_data), 200
        
    except Exception as e:
        print(f'❌ Error in get_user_modules: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/activate', methods=['POST'])
@jwt_required()
def activate_module():
    """Activate a module for the current user - JWT REQUIRED"""
    try:
        # SECURITY: Get user ID from verified JWT token only
        user_id_str = get_jwt_identity()
        
        if not user_id_str:
            print('❌ No user identity in JWT token')
            return jsonify({
                'status': 'error',
                'message': 'User identity not found in JWT token'
            }), 401
        
        # Convert to int (JWT identity is stored as string)
        try:
            user_id = int(user_id_str)
            print(f'✅ Activate module - User ID from JWT: {user_id}')
        except (ValueError, TypeError) as e:
            print(f'❌ Invalid user ID format: {user_id_str}, error: {e}')
            return jsonify({'error': 'Invalid user ID in token'}), 400
        
        data = request.get_json()
        module_id = data.get('module_id')
        permissions = data.get('permissions')
        
        print(f'📦 Activation request: user_id={user_id}, module_id={module_id}, permissions={permissions}')
        
        if not module_id:
            print('❌ No module_id provided')
            return jsonify({'error': 'module_id is required'}), 400
        
        # SECURITY: Validate module_id (prevent injection)
        if not isinstance(module_id, str) or len(module_id) > 50:
            print(f'❌ Invalid module_id format: {module_id}')
            return jsonify({'error': 'Invalid module_id format'}), 400
        
        # Check if module is available
        if module_id not in AVAILABLE_MODULES:
            print(f'❌ Module not available: {module_id}')
            return jsonify({'error': f'Module {module_id} is not available'}), 400
        
        # SECURITY: Activate module (strict user isolation - model filters by user_id)
        print(f'💾 Saving module activation to database: user_id={user_id}, module_id={module_id}')
        user_module = UserModules.enable_module(
            user_id=user_id,
            module_id=module_id,
            permissions=permissions
        )
        
        print(f'✅ Module activated successfully: user_id={user_id}, module_id={module_id}, is_active={user_module.is_active}, is_enabled={user_module.is_enabled}')
        
        # SECURITY: Auto-grant module permissions to user's role
        logger.info(f"🔐 Auto-granting permissions for module '{module_id}' to user {user_id}")
        print(f"🔐 Auto-granting permissions for module '{module_id}' to user {user_id}")
        permission_result = grant_module_permissions(
            user_id=user_id,
            module_id=module_id,
            granted_by_user_id=user_id
        )
        
        if permission_result['success']:
            logger.info(f"✅ Successfully granted {len(permission_result['granted'])} permissions for module '{module_id}'")
            print(f"✅ Successfully granted {len(permission_result['granted'])} permissions for module '{module_id}'")
        else:
            logger.warning(f"⚠️  Some permissions failed to grant for module '{module_id}': {permission_result['errors']}")
            print(f"⚠️  Some permissions failed to grant for module '{module_id}': {permission_result['errors']}")
            # Don't fail the activation, but log the warning
        
        module_info = AVAILABLE_MODULES[module_id]
        
        return jsonify({
            'message': f'Module {module_info["name"]} activated successfully',
            'module': {
                'id': user_module.module_id,
                'name': module_info['name'],
                'description': module_info['description'],
                'features': module_info['features'],
                'is_enabled': user_module.is_enabled,
                'is_active': user_module.is_active,
                'permissions': user_module.permissions,
                'activated_at': user_module.activated_at.isoformat()
            },
            'permissions_granted': len(permission_result['granted']),
            'permissions_failed': len(permission_result['failed'])
        }), 200
        
    except Exception as e:
        print(f'❌ Error activating module: {str(e)}')
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_module():
    """Deactivate a module for the current user - JWT REQUIRED"""
    try:
        # SECURITY: Get user ID from verified JWT token only
        user_id_str = get_jwt_identity()
        
        if not user_id_str:
            return jsonify({
                'status': 'error',
                'message': 'User identity not found in JWT token'
            }), 401
        
        # Convert to int (JWT identity is stored as string)
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID in token'}), 400
        
        data = request.get_json()
        module_id = data.get('module_id')
        
        if not module_id:
            return jsonify({'error': 'module_id is required'}), 400
        
        # SECURITY: Validate module_id (prevent injection)
        if not isinstance(module_id, str) or len(module_id) > 50:
            return jsonify({'error': 'Invalid module_id format'}), 400
        
        # SECURITY: Deactivate module (strict user isolation - model filters by user_id)
        success = UserModules.disable_module(user_id=user_id, module_id=module_id)
        
        if not success:
            return jsonify({'error': f'Module {module_id} not found for user'}), 404
        
        # SECURITY: Auto-revoke module permissions from user's role
        logger.info(f"🔐 Auto-revoking permissions for module '{module_id}' from user {user_id}")
        print(f"🔐 Auto-revoking permissions for module '{module_id}' from user {user_id}")
        permission_result = revoke_module_permissions(
            user_id=user_id,
            module_id=module_id,
            revoked_by_user_id=user_id
        )
        
        if permission_result['success']:
            logger.info(f"✅ Successfully revoked {len(permission_result['revoked'])} permissions for module '{module_id}'")
            print(f"✅ Successfully revoked {len(permission_result['revoked'])} permissions for module '{module_id}'")
        else:
            logger.warning(f"⚠️  Some permissions failed to revoke for module '{module_id}': {permission_result['errors']}")
            print(f"⚠️  Some permissions failed to revoke for module '{module_id}': {permission_result['errors']}")
            # Don't fail the deactivation, but log the warning
        
        module_info = AVAILABLE_MODULES.get(module_id, {})
        
        return jsonify({
            'message': f'Module {module_info.get("name", module_id)} deactivated successfully',
            'module_id': module_id,
            'permissions_revoked': len(permission_result['revoked']),
            'permissions_failed': len(permission_result['failed'])
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/check/<module_id>', methods=['GET'])
@jwt_required()
def check_module_access(module_id):
    """Check if user has access to a specific module - JWT REQUIRED"""
    try:
        # SECURITY: Get user ID from verified JWT token only
        user_id_str = get_jwt_identity()
        
        if not user_id_str:
            return jsonify({
                'has_access': False,
                'module_id': module_id,
                'user_id': None,
                'error': 'User identity not found in JWT token'
            }), 401
        
        # Convert to int (JWT identity is stored as string)
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID in token'}), 400
        
        # Check module access
        has_access = UserModules.is_module_enabled(user_id, module_id)
        
        return jsonify({
            'has_access': has_access,
            'module_id': module_id,
            'user_id': user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/bulk-activate', methods=['POST'])
@jwt_required()
def bulk_activate_modules():
    """Activate multiple modules for the current user - JWT REQUIRED"""
    try:
        # SECURITY: Get user ID from verified JWT token only
        user_id_str = get_jwt_identity()
        
        if not user_id_str:
            return jsonify({
                'status': 'error',
                'message': 'User identity not found in JWT token'
            }), 401
        
        # Convert to int (JWT identity is stored as string)
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID in token'}), 400
        
        data = request.get_json()
        module_ids = data.get('module_ids', [])
        permissions = data.get('permissions', {})
        
        if not module_ids:
            return jsonify({'error': 'module_ids is required'}), 400
        
        activated_modules = []
        failed_modules = []
        
        for module_id in module_ids:
            try:
                # Check if module is available
                if module_id not in AVAILABLE_MODULES:
                    failed_modules.append({
                        'module_id': module_id,
                        'error': f'Module {module_id} is not available'
                    })
                    continue
                
                # Activate module
                user_module = UserModules.enable_module(
                    user_id=user_id,
                    module_id=module_id,
                    permissions=permissions.get(module_id),
                    created_by=user_id
                )
                
                module_info = AVAILABLE_MODULES[module_id]
                activated_modules.append({
                    'id': user_module.module_id,
                    'name': module_info['name'],
                    'description': module_info['description'],
                    'features': module_info['features']
                })
                
            except Exception as e:
                failed_modules.append({
                    'module_id': module_id,
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Activated {len(activated_modules)} modules',
            'activated_modules': activated_modules,
            'failed_modules': failed_modules
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




