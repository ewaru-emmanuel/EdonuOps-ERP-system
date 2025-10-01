from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.dashboard.models import UserModules, Dashboard, DashboardWidget, WidgetTemplate, DashboardTemplate

module_activation_bp = Blueprint('module_activation', __name__, url_prefix='/api/dashboard/modules')

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

@module_activation_bp.route('/available', methods=['GET'])
def get_available_modules():
    """Get all available modules"""
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for available modules, returning empty results")
            return jsonify([]), 200
        
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

@module_activation_bp.route('/user', methods=['GET'])
def get_user_modules():
    """Get user's activated modules"""
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
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for user modules, returning empty results")
            return jsonify([]), 200
        
        # Get user's modules
        user_modules = UserModules.get_user_modules(user_id)
        
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
        
        return jsonify(modules_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/activate', methods=['POST'])
def activate_module():
    """Activate a module for the current user"""
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
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
        
        data = request.get_json()
        module_id = data.get('module_id')
        permissions = data.get('permissions')
        
        if not module_id:
            return jsonify({'error': 'module_id is required'}), 400
        
        # Check if module is available
        if module_id not in AVAILABLE_MODULES:
            return jsonify({'error': f'Module {module_id} is not available'}), 400
        
        # Activate module
        user_module = UserModules.enable_module(
            user_id=user_id,
            module_id=module_id,
            permissions=permissions,
            created_by=user_id
        )
        
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
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/deactivate', methods=['POST'])
def deactivate_module():
    """Deactivate a module for the current user"""
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
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
        
        data = request.get_json()
        module_id = data.get('module_id')
        
        if not module_id:
            return jsonify({'error': 'module_id is required'}), 400
        
        # Deactivate module
        success = UserModules.disable_module(user_id=user_id, module_id=module_id)
        
        if not success:
            return jsonify({'error': f'Module {module_id} not found for user'}), 404
        
        module_info = AVAILABLE_MODULES.get(module_id, {})
        
        return jsonify({
            'message': f'Module {module_info.get("name", module_id)} deactivated successfully',
            'module_id': module_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@module_activation_bp.route('/check/<module_id>', methods=['GET'])
def check_module_access(module_id):
    """Check if user has access to a specific module"""
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
        
        # If still no user_id, return false (for development)
        if not user_id:
            return jsonify({
                'has_access': False,
                'module_id': module_id,
                'user_id': None
            }), 200
        
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
def bulk_activate_modules():
    """Activate multiple modules for the current user"""
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
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
        
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




