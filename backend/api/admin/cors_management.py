"""
CORS Management API
Enterprise CORS configuration management endpoints
"""

from flask import Blueprint, request, jsonify
from enterprise.config import EnterpriseConfig
from enterprise.security import SecurityManager
from enterprise.audit import AuditService
import logging

# Create blueprint
cors_admin_bp = Blueprint('cors_admin', __name__)

# Initialize services
config = EnterpriseConfig()
audit_service = AuditService()
logger = logging.getLogger(__name__)

@cors_admin_bp.route('/cors/origins', methods=['GET'])
def get_cors_origins():
    """Get current CORS origins for all environments"""
    try:
        origins = config.cors_config
        return jsonify({
            'status': 'success',
            'current_environment': config.get_environment(),
            'origins': origins
        }), 200
    except Exception as e:
        logger.error(f"Error getting CORS origins: {e}")
        return jsonify({'error': str(e)}), 500

@cors_admin_bp.route('/cors/origins', methods=['POST'])
def add_cors_origin():
    """Add a new CORS origin"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'origin' not in data:
            return jsonify({'error': 'origin is required'}), 400
        
        origin = data['origin']
        environment = data.get('environment', config.get_environment())
        
        # Add the origin
        success = config.add_cors_origin(origin, environment)
        
        if success:
            # Log the activity
            audit_service.log_activity(
                user_id=1,  # Admin user
                action='add_cors_origin',
                resource='cors_config',
                details={'origin': origin, 'environment': environment}
            )
            
            return jsonify({
                'status': 'success',
                'message': f'CORS origin {origin} added to {environment}',
                'origin': origin,
                'environment': environment
            }), 201
        else:
            return jsonify({'error': 'Failed to add CORS origin'}), 500
            
    except Exception as e:
        logger.error(f"Error adding CORS origin: {e}")
        return jsonify({'error': str(e)}), 500

@cors_admin_bp.route('/cors/origins', methods=['DELETE'])
def remove_cors_origin():
    """Remove a CORS origin"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'origin' not in data:
            return jsonify({'error': 'origin is required'}), 400
        
        origin = data['origin']
        environment = data.get('environment', config.get_environment())
        
        # Remove the origin
        success = config.remove_cors_origin(origin, environment)
        
        if success:
            # Log the activity
            audit_service.log_activity(
                user_id=1,  # Admin user
                action='remove_cors_origin',
                resource='cors_config',
                details={'origin': origin, 'environment': environment}
            )
            
            return jsonify({
                'status': 'success',
                'message': f'CORS origin {origin} removed from {environment}',
                'origin': origin,
                'environment': environment
            }), 200
        else:
            return jsonify({'error': 'Failed to remove CORS origin'}), 500
            
    except Exception as e:
        logger.error(f"Error removing CORS origin: {e}")
        return jsonify({'error': str(e)}), 500

@cors_admin_bp.route('/cors/environment', methods=['GET'])
def get_current_environment():
    """Get current environment"""
    try:
        return jsonify({
            'status': 'success',
            'environment': config.get_environment(),
            'available_environments': config.environment_config.get('available', [])
        }), 200
    except Exception as e:
        logger.error(f"Error getting environment: {e}")
        return jsonify({'error': str(e)}), 500

@cors_admin_bp.route('/cors/environment', methods=['POST'])
def set_environment():
    """Set current environment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'environment' not in data:
            return jsonify({'error': 'environment is required'}), 400
        
        environment = data['environment']
        available = config.environment_config.get('available', [])
        
        if environment not in available:
            return jsonify({
                'error': f'Invalid environment. Available: {available}'
            }), 400
        
        # Set the environment
        success = config.set_environment(environment)
        
        if success:
            # Log the activity
            audit_service.log_activity(
                user_id=1,  # Admin user
                action='set_environment',
                resource='environment_config',
                details={'environment': environment}
            )
            
            return jsonify({
                'status': 'success',
                'message': f'Environment set to {environment}',
                'environment': environment
            }), 200
        else:
            return jsonify({'error': 'Failed to set environment'}), 500
            
    except Exception as e:
        logger.error(f"Error setting environment: {e}")
        return jsonify({'error': str(e)}), 500

@cors_admin_bp.route('/cors/quick-add', methods=['POST'])
def quick_add_cors():
    """Quick add CORS origin for common scenarios"""
    try:
        data = request.get_json()
        
        if not data or 'scenario' not in data:
            return jsonify({'error': 'scenario is required'}), 400
        
        scenario = data['scenario']
        environment = data.get('environment', config.get_environment())
        
        # Predefined scenarios
        scenarios = {
            'localhost': 'http://localhost:3000',
            'localhost_alt': 'http://127.0.0.1:3000',
            'aws': 'https://your-aws-domain.com',
            'azure': 'https://your-azure-domain.com',
            'gcp': 'https://your-gcp-domain.com',
            'production': 'https://edonuops.com',
            'staging': 'https://staging.edonuops.com'
        }
        
        if scenario not in scenarios:
            return jsonify({
                'error': f'Invalid scenario. Available: {list(scenarios.keys())}'
            }), 400
        
        origin = scenarios[scenario]
        success = config.add_cors_origin(origin, environment)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'CORS origin added for {scenario}',
                'origin': origin,
                'environment': environment
            }), 201
        else:
            return jsonify({'error': 'Failed to add CORS origin'}), 500
            
    except Exception as e:
        logger.error(f"Error in quick add CORS: {e}")
        return jsonify({'error': str(e)}), 500

