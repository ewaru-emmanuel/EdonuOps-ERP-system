#!/usr/bin/env python3
"""
Performance Monitoring Routes
API endpoints for performance monitoring and optimization
"""

from flask import Blueprint, jsonify
from services.performance_service import PerformanceService
import logging

# Create performance blueprint
performance_bp = Blueprint('performance', __name__)
performance_service = PerformanceService()

@performance_bp.route('/metrics', methods=['GET'])
def get_performance_metrics():
    """Get performance metrics"""
    try:
        metrics = performance_service.get_performance_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for performance service"""
    return jsonify({
        'status': 'healthy',
        'service': 'performance-monitoring'
    }), 200

