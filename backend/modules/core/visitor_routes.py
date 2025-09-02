from flask import Blueprint, request, jsonify
from app import db
from datetime import datetime
import json

# Create visitor management blueprint
visitor_bp = Blueprint('visitor', __name__)

# In-memory storage for visitors (in production, use database)
visitors = {}

@visitor_bp.route('/api/visitors/initialize', methods=['POST'])
def initialize_visitor():
    """Initialize a new visitor session"""
    try:
        data = request.get_json()
        visitor_id = data.get('visitorId')
        session_id = data.get('sessionId')
        user_agent = data.get('userAgent')
        
        if not visitor_id or not session_id:
            return jsonify({'success': False, 'error': 'Missing visitor or session ID'}), 400
        
        # Store visitor information
        visitors[visitor_id] = {
            'session_id': session_id,
            'user_agent': user_agent,
            'created_at': datetime.utcnow().isoformat(),
            'last_seen': datetime.utcnow().isoformat(),
            'preferences': None,
            'modules_selected': []
        }
        
        return jsonify({
            'success': True,
            'message': 'Visitor initialized successfully',
            'visitor_id': visitor_id,
            'session_id': session_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@visitor_bp.route('/api/visitors/<visitor_id>/preferences', methods=['POST'])
def update_visitor_preferences(visitor_id):
    """Update visitor preferences and module selections"""
    try:
        data = request.get_json()
        
        if visitor_id not in visitors:
            return jsonify({'success': False, 'error': 'Visitor not found'}), 404
        
        # Update visitor preferences
        visitors[visitor_id].update({
            'preferences': data,
            'modules_selected': data.get('selectedModules', []),
            'last_seen': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully',
            'visitor_id': visitor_id
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@visitor_bp.route('/api/visitors/<visitor_id>', methods=['GET'])
def get_visitor_info(visitor_id):
    """Get visitor information"""
    try:
        if visitor_id not in visitors:
            return jsonify({'success': False, 'error': 'Visitor not found'}), 404
        
        visitor = visitors[visitor_id]
        return jsonify({
            'success': True,
            'visitor': visitor
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@visitor_bp.route('/api/visitors/stats', methods=['GET'])
def get_visitor_stats():
    """Get visitor statistics (admin only)"""
    try:
        total_visitors = len(visitors)
        active_visitors = len([v for v in visitors.values() if v.get('preferences')])
        
        module_stats = {}
        for visitor in visitors.values():
            if visitor.get('modules_selected'):
                for module in visitor['modules_selected']:
                    module_stats[module] = module_stats.get(module, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_visitors': total_visitors,
                'active_visitors': active_visitors,
                'module_popularity': module_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
