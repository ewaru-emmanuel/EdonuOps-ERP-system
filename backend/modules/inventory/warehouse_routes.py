from flask import Blueprint, jsonify, request
from app import db
from modules.inventory.advanced_models import (
    WarehouseActivity, AdvancedWarehouse, AdvancedLocation, InventoryProduct
)
from datetime import datetime, timedelta
import random

# Create blueprint for warehouse routes
warehouse_bp = Blueprint('warehouse', __name__, url_prefix='/api/inventory/warehouse')

@warehouse_bp.route('/pick-lists', methods=['GET'])
def get_pick_lists():
    """Get pick lists for warehouse operations"""
    try:
        # Mock pick lists data for now
        pick_lists = [
            {
                'id': 1,
                'order_number': 'ORD-001',
                'priority': 'high',
                'status': 'pending',
                'items': [
                    {'product_name': 'Product A', 'quantity': 5, 'location': 'A1-B2-C3'},
                    {'product_name': 'Product B', 'quantity': 3, 'location': 'A2-B1-C4'}
                ],
                'assigned_to': 'picker_001',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'order_number': 'ORD-002',
                'priority': 'medium',
                'status': 'in_progress',
                'items': [
                    {'product_name': 'Product C', 'quantity': 2, 'location': 'A3-B2-C1'},
                    {'product_name': 'Product D', 'quantity': 1, 'location': 'A1-B3-C2'}
                ],
                'assigned_to': 'picker_002',
                'created_at': (datetime.now() - timedelta(hours=1)).isoformat()
            }
        ]
        
        return jsonify({
            'status': 'success',
            'pick_lists': pick_lists
        }), 200
    except Exception as e:
        print(f"Error in get_pick_lists: {str(e)}")
        return jsonify({'error': str(e)}), 500

@warehouse_bp.route('/cycle-counts', methods=['GET'])
def get_cycle_counts():
    """Get cycle count data for warehouse operations"""
    try:
        # Mock cycle count data for now
        cycle_counts = [
            {
                'id': 1,
                'location': 'A1-B2-C3',
                'product_name': 'Product A',
                'expected_quantity': 100,
                'actual_quantity': 98,
                'variance': -2,
                'variance_percentage': -2.0,
                'status': 'completed',
                'counted_by': 'counter_001',
                'counted_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'location': 'A2-B1-C4',
                'product_name': 'Product B',
                'expected_quantity': 50,
                'actual_quantity': 52,
                'variance': 2,
                'variance_percentage': 4.0,
                'status': 'pending',
                'counted_by': 'counter_002',
                'counted_at': (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
        
        return jsonify({
            'status': 'success',
            'cycle_counts': cycle_counts
        }), 200
    except Exception as e:
        print(f"Error in get_cycle_counts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@warehouse_bp.route('/live-activity', methods=['GET'])
def get_live_activity():
    """Get live warehouse activity for operations dashboard"""
    try:
        # Get recent warehouse activities
        today = datetime.now()
        hour_ago = today - timedelta(hours=1)
        
        activities = WarehouseActivity.query.filter(
            WarehouseActivity.activity_timestamp >= hour_ago
        ).order_by(WarehouseActivity.activity_timestamp.desc()).limit(30).all()
        
        activity_data = []
        for activity in activities:
            activity_data.append({
                'id': activity.id,
                'warehouse_name': activity.warehouse.name if activity.warehouse else 'Unknown Warehouse',
                'location_name': activity.location.location_name if activity.location else 'Unknown Location',
                'user_id': activity.user_id,
                'activity_type': activity.activity_type,
                'activity_timestamp': activity.activity_timestamp.isoformat(),
                'efficiency_score': activity.efficiency_score,
                'duration_seconds': activity.duration_seconds,
                'notes': activity.notes
            })
        
        # If no real data, return mock data
        if not activity_data:
            activity_data = [
                {
                    'id': 1,
                    'warehouse_name': 'Main Warehouse',
                    'location_name': 'A1-B2-C3',
                    'user_id': 'picker_001',
                    'activity_type': 'pick',
                    'activity_timestamp': datetime.now().isoformat(),
                    'efficiency_score': 0.95,
                    'duration_seconds': 120,
                    'notes': 'Picked 5 items for order ORD-001'
                },
                {
                    'id': 2,
                    'warehouse_name': 'Main Warehouse',
                    'location_name': 'A2-B1-C4',
                    'user_id': 'picker_002',
                    'activity_type': 'putaway',
                    'activity_timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                    'efficiency_score': 0.88,
                    'duration_seconds': 180,
                    'notes': 'Put away 10 items from receiving'
                }
            ]
        
        return jsonify({
            'status': 'success',
            'activities': activity_data
        }), 200
    except Exception as e:
        print(f"Error in get_live_activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

