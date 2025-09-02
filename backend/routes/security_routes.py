#!/usr/bin/env python3
"""
Security Monitoring Routes
API endpoints for security monitoring and management
"""

from flask import Blueprint, jsonify
from services.security import SecurityService
import logging

# Create security blueprint
security_bp = Blueprint('security', __name__)
security_service = SecurityService()

@security_bp.route('/metrics', methods=['GET'])
def get_security_metrics():
    """Get security metrics"""
    try:
        metrics = security_service.get_security_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for security service"""
    return jsonify({
        'status': 'healthy',
        'service': 'security-monitoring'
    }), 200

