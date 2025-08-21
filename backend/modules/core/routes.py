# Core routes for EdonuOps ERP
from flask import Blueprint, jsonify

core_bp = Blueprint('core', __name__)

@core_bp.route('/health', methods=['GET'])
def health_check():
    """Core health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'core',
        'message': 'Core service is running'
    })

@core_bp.route('/version', methods=['GET'])
def get_version():
    """Get application version"""
    return jsonify({
        'version': '1.0.0',
        'name': 'EdonuOps ERP',
        'description': 'Enterprise Resource Planning System'
    })
