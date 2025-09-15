"""
API routes for statutory module management
"""

from flask import Blueprint, jsonify, request
from app import db
from .statutory_modules import get_statutory_module_manager
from .models import Account
import logging

statutory_bp = Blueprint('statutory', __name__)

@statutory_bp.route('/modules', methods=['GET'])
def get_statutory_modules():
    """Get all statutory modules for the company's country"""
    try:
        country = request.args.get('country', 'US')
        manager = get_statutory_module_manager(country)
        
        modules = []
        for module in manager.modules.values():
            can_activate, activate_message = module.can_activate()
            can_deactivate, deactivate_message, issues = module.can_deactivate()
            
            modules.append({
                'id': module.id,
                'name': module.name,
                'description': module.description,
                'country': module.country,
                'is_active': module.is_active,
                'activation_date': module.activation_date.isoformat() if module.activation_date else None,
                'deactivation_date': module.deactivation_date.isoformat() if module.deactivation_date else None,
                'required_accounts': module.required_accounts,
                'compliance_forms': module.compliance_forms,
                'can_activate': can_activate,
                'can_deactivate': can_deactivate,
                'activation_message': activate_message,
                'deactivation_message': deactivate_message,
                'deactivation_issues': issues
            })
        
        return jsonify({
            'modules': modules,
            'country': country,
            'total_modules': len(modules)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching statutory modules: {e}")
        return jsonify({'error': 'Failed to fetch statutory modules'}), 500

@statutory_bp.route('/modules/<module_id>/activate', methods=['POST'])
def activate_module(module_id):
    """Activate a statutory module"""
    try:
        country = request.json.get('country', 'US') if request.json else 'US'
        manager = get_statutory_module_manager(country)
        
        success, message = manager.activate_module(module_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'module_id': module_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'module_id': module_id
            }), 400
            
    except Exception as e:
        logging.error(f"Error activating module {module_id}: {e}")
        return jsonify({'error': f'Failed to activate module: {str(e)}'}), 500

@statutory_bp.route('/modules/<module_id>/deactivate', methods=['POST'])
def deactivate_module(module_id):
    """Deactivate a statutory module"""
    try:
        data = request.json or {}
        country = data.get('country', 'US')
        force = data.get('force', False)
        
        manager = get_statutory_module_manager(country)
        
        success, message, issues = manager.deactivate_module(module_id, force)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'module_id': module_id,
                'issues': issues
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'module_id': module_id,
                'issues': issues
            }), 400
            
    except Exception as e:
        logging.error(f"Error deactivating module {module_id}: {e}")
        return jsonify({'error': f'Failed to deactivate module: {str(e)}'}), 500

@statutory_bp.route('/modules/<module_id>/status', methods=['GET'])
def get_module_status(module_id):
    """Get detailed status of a specific module"""
    try:
        country = request.args.get('country', 'US')
        manager = get_statutory_module_manager(country)
        
        module = manager.get_module(module_id)
        if not module:
            return jsonify({'error': 'Module not found'}), 404
        
        can_activate, activate_message = module.can_activate()
        can_deactivate, deactivate_message, issues = module.can_deactivate()
        
        # Get account details
        account_details = []
        for account_code in module.required_accounts:
            account = Account.query.filter_by(code=account_code).first()
            if account:
                account_details.append({
                    'code': account.code,
                    'name': account.name,
                    'type': account.type,
                    'balance': float(account.balance) if account.balance else 0.0,
                    'is_active': account.is_active
                })
        
        return jsonify({
            'module': {
                'id': module.id,
                'name': module.name,
                'description': module.description,
                'country': module.country,
                'is_active': module.is_active,
                'activation_date': module.activation_date.isoformat() if module.activation_date else None,
                'deactivation_date': module.deactivation_date.isoformat() if module.deactivation_date else None,
                'required_accounts': module.required_accounts,
                'compliance_forms': module.compliance_forms
            },
            'status': {
                'can_activate': can_activate,
                'can_deactivate': can_deactivate,
                'activation_message': activate_message,
                'deactivation_message': deactivate_message,
                'deactivation_issues': issues
            },
            'accounts': account_details
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching module status for {module_id}: {e}")
        return jsonify({'error': f'Failed to fetch module status: {str(e)}'}), 500

@statutory_bp.route('/compliance/status', methods=['GET'])
def get_compliance_status():
    """Get overall compliance status for the company"""
    try:
        country = request.args.get('country', 'US')
        manager = get_statutory_module_manager(country)
        
        status = manager.get_compliance_status()
        return jsonify(status), 200
        
    except Exception as e:
        logging.error(f"Error fetching compliance status: {e}")
        return jsonify({'error': 'Failed to fetch compliance status'}), 500

@statutory_bp.route('/compliance/forms', methods=['GET'])
def get_compliance_forms():
    """Get all compliance forms for active modules"""
    try:
        country = request.args.get('country', 'US')
        manager = get_statutory_module_manager(country)
        
        active_modules = manager.get_active_modules()
        forms = []
        
        for module in active_modules:
            for form in module.compliance_forms:
                forms.append({
                    'form_name': form,
                    'module_id': module.id,
                    'module_name': module.name,
                    'country': module.country,
                    'description': f"{form} for {module.name}"
                })
        
        return jsonify({
            'forms': forms,
            'total_forms': len(forms),
            'country': country
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching compliance forms: {e}")
        return jsonify({'error': 'Failed to fetch compliance forms'}), 500

@statutory_bp.route('/accounts/statutory', methods=['GET'])
def get_statutory_accounts():
    """Get all accounts that belong to statutory modules"""
    try:
        country = request.args.get('country', 'US')
        manager = get_statutory_module_manager(country)
        
        statutory_accounts = []
        for module in manager.modules.values():
            for account_code in module.required_accounts:
                account = Account.query.filter_by(code=account_code).first()
                if account:
                    statutory_accounts.append({
                        'id': account.id,
                        'code': account.code,
                        'name': account.name,
                        'type': account.type,
                        'balance': float(account.balance) if account.balance else 0.0,
                        'is_active': account.is_active,
                        'module_id': module.id,
                        'module_name': module.name,
                        'is_module_active': module.is_active
                    })
        
        return jsonify({
            'accounts': statutory_accounts,
            'total_accounts': len(statutory_accounts),
            'country': country
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching statutory accounts: {e}")
        return jsonify({'error': 'Failed to fetch statutory accounts'}), 500

