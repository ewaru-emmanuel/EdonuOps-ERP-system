from flask import Blueprint, request, jsonify
from app import db
from modules.inventory.advanced_models import WarehouseActivity, AdvancedWarehouse, AdvancedLocation
from datetime import datetime, timedelta

warehouse_ops_bp = Blueprint('warehouse_operations', __name__)

@warehouse_ops_bp.route('/pick-lists', methods=['GET'])
def get_pick_lists():
    """Get all pick lists"""
    try:
        pick_lists = [
            {
                'id': 1,
                'pick_list_number': 'PL-2024-001',
                'assigned_to': 'John Smith',
                'status': 'in_progress',
                'total_lines': 15,
                'completed_lines': 8,
                'priority': 'high'
            },
            {
                'id': 2,
                'pick_list_number': 'PL-2024-002',
                'assigned_to': 'Sarah Johnson',
                'status': 'pending',
                'total_lines': 12,
                'completed_lines': 0,
                'priority': 'normal'
            }
        ]
        return jsonify(pick_lists)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/pick-lists/<int:pick_list_id>', methods=['GET'])
def get_pick_list_details(pick_list_id):
    """Get detailed information for a specific pick list"""
    try:
        # Mock data for pick list details
        pick_list_details = {
            'id': pick_list_id,
            'pick_list_number': f'PL-2024-{pick_list_id:03d}',
            'warehouse_id': 1,
            'assigned_to': 'John Smith',
            'status': 'in_progress',
            'pick_date': datetime.now().isoformat(),
            'completed_at': None,
            'lines': [
                {
                    'id': 1,
                    'product_id': 1,
                    'product_name': 'Laptop Pro X1',
                    'quantity_ordered': 5,
                    'quantity_picked': 3,
                    'status': 'in_progress',
                    'location': 'A1-B2-C3',
                    'picked_at': None
                },
                {
                    'id': 2,
                    'product_id': 2,
                    'product_name': 'Wireless Mouse',
                    'quantity_ordered': 10,
                    'quantity_picked': 10,
                    'status': 'completed',
                    'location': 'A2-B1-C4',
                    'picked_at': datetime.now().isoformat()
                }
            ],
            'total_lines': 2,
            'completed_lines': 1
        }
        
        return jsonify(pick_list_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/pick-lists/<int:pick_list_id>/assign', methods=['POST'])
def assign_pick_list(pick_list_id):
    """Assign a pick list to a picker"""
    try:
        data = request.get_json()
        picker_name = data.get('picker_name')
        
        if not picker_name:
            return jsonify({'error': 'Picker name is required'}), 400
        
        # Mock assignment - in real implementation, this would update the database
        return jsonify({'message': f'Pick list {pick_list_id} assigned to {picker_name} successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/cycle-counts', methods=['GET'])
def get_cycle_counts():
    """Get all cycle counts"""
    try:
        cycle_counts = [
            {
                'id': 1,
                'count_number': 'CC-2024-001',
                'count_type': 'cycle',
                'assigned_to': 'Mike Wilson',
                'status': 'completed',
                'total_lines': 50,
                'completed_lines': 50
            },
            {
                'id': 2,
                'count_number': 'CC-2024-002',
                'count_type': 'full',
                'assigned_to': 'Lisa Brown',
                'status': 'in_progress',
                'total_lines': 200,
                'completed_lines': 75
            }
        ]
        return jsonify(cycle_counts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/cycle-counts', methods=['POST'])
def create_cycle_count():
    """Create a new cycle count"""
    try:
        data = request.get_json()
        
        cycle_count = CycleCount(
            count_number=f"CC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            warehouse_id=data.get('warehouse_id'),
            count_type=data.get('count_type', 'cycle'),
            assigned_to=data.get('assigned_to'),
            status='pending',
            created_date=datetime.utcnow()
        )
        
        db.session.add(cycle_count)
        db.session.commit()
        
        return jsonify({
            'message': 'Cycle count created successfully',
            'id': cycle_count.id,
            'count_number': cycle_count.count_number
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/live-activity', methods=['GET'])
def get_warehouse_live_activity():
    """Get live warehouse activity"""
    try:
        activities = [
            {
                'id': 1,
                'user_name': 'John Smith',
                'activity_type': 'Pick Completed',
                'activity_timestamp': datetime.utcnow().isoformat(),
                'location_name': 'Zone A - Aisle 1',
                'efficiency_score': 92.5
            },
            {
                'id': 2,
                'user_name': 'Sarah Johnson',
                'activity_type': 'Cycle Count',
                'activity_timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                'location_name': 'Zone B - Aisle 3',
                'efficiency_score': 88.3
            }
        ]
        return jsonify(activities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/activity-log', methods=['POST'])
def log_warehouse_activity():
    """Log a new warehouse activity"""
    try:
        data = request.get_json()
        
        activity = WarehouseActivity(
            warehouse_id=data.get('warehouse_id'),
            user_id=data.get('user_id'),
            user_name=data.get('user_name'),
            activity_type=data.get('activity_type'),
            activity_timestamp=datetime.utcnow(),
            location_name=data.get('location_name'),
            efficiency_score=data.get('efficiency_score'),
            duration_seconds=data.get('duration_seconds'),
            activity_details=data.get('activity_details')
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'message': 'Activity logged successfully', 'id': activity.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
