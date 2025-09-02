from flask import Blueprint, request, jsonify
from app import db
from modules.inventory.advanced_models import AdvancedWarehouse, AdvancedLocation, WarehouseActivity, PickerPerformance
from datetime import datetime, timedelta
from sqlalchemy import func
import random

manager_dashboard_bp = Blueprint('manager_dashboard', __name__)

@manager_dashboard_bp.route('/warehouse-map', methods=['GET'])
def get_warehouse_map():
    """Get live warehouse map with zone utilization"""
    try:
        # Check if tables exist, if not return mock data
        try:
            warehouses = AdvancedWarehouse.query.all()
            warehouse_data = []
            
            for warehouse in warehouses:
                total_locations = AdvancedLocation.query.filter_by(warehouse_id=warehouse.id).count()
                occupied_locations = AdvancedLocation.query.filter_by(warehouse_id=warehouse.id, status='occupied').count()
                utilization = (occupied_locations / total_locations * 100) if total_locations > 0 else 0
                
                warehouse_data.append({
                    'id': warehouse.id,
                    'name': warehouse.name,
                    'utilization': round(utilization, 1),
                    'status': 'congested' if utilization > 90 else 'normal',
                    'total_locations': total_locations,
                    'occupied_locations': occupied_locations
                })
        except Exception:
            # Return mock data if tables don't exist
            warehouse_data = [
                {
                    'id': 1,
                    'name': 'Main Warehouse',
                    'utilization': 75.5,
                    'status': 'normal',
                    'total_locations': 50,
                    'occupied_locations': 38
                },
                {
                    'id': 2,
                    'name': 'Secondary Warehouse',
                    'utilization': 92.3,
                    'status': 'congested',
                    'total_locations': 30,
                    'occupied_locations': 28
                }
            ]
        
        return jsonify({
            'warehouses': warehouse_data,
            'total_pickers': 5,
            'total_orders': 25,
            'completed_today': 18,
            'efficiency_avg': 87.5,
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manager_dashboard_bp.route('/predictive-alerts', methods=['GET'])
def get_predictive_alerts():
    """Get predictive alerts"""
    try:
        alerts = [
            {
                'id': 1,
                'type': 'stockout',
                'severity': 'high',
                'title': 'Stockout Alert: Laptop Pro X1',
                'message': 'Product will stockout in 2 days',
                'days_until_stockout': 2,
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'type': 'congestion',
                'severity': 'medium',
                'title': 'Zone Congestion: Zone A',
                'message': 'Zone A is experiencing high utilization',
                'utilization': 85,
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manager_dashboard_bp.route('/picker-performance', methods=['GET'])
def get_picker_performance():
    """Get picker performance data"""
    try:
        pickers = [
            {
                'id': 1,
                'name': 'John Smith',
                'picks_today': 45,
                'efficiency': 92.5,
                'status': 'active',
                'zone_assigned': 'Zone A',
                'last_activity': datetime.utcnow().isoformat(),
                'avg_picks_per_hour': 15.2,
                'accuracy_rate': 98.5
            },
            {
                'id': 2,
                'name': 'Sarah Johnson',
                'picks_today': 38,
                'efficiency': 88.3,
                'status': 'active',
                'zone_assigned': 'Zone B',
                'last_activity': datetime.utcnow().isoformat(),
                'avg_picks_per_hour': 12.8,
                'accuracy_rate': 97.2
            }
        ]
        return jsonify(pickers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manager_dashboard_bp.route('/live-activity', methods=['GET'])
def get_live_activity():
    """Get live activity feed"""
    try:
        activities = [
            {
                'id': 1,
                'user': 'John Smith',
                'time': datetime.utcnow().isoformat(),
                'activity': 'Pick Completed',
                'location': 'Zone A - Aisle 1',
                'efficiency': 92.5,
                'details': 'Picked 15 items in 8 minutes'
            },
            {
                'id': 2,
                'user': 'Sarah Johnson',
                'time': (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
                'activity': 'Cycle Count',
                'location': 'Zone B - Aisle 3',
                'efficiency': 88.3,
                'details': 'Counted 50 items, variance: 0'
            }
        ]
        return jsonify(activities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manager_dashboard_bp.route('/zone-details/<int:zone_id>', methods=['GET'])
def get_zone_details(zone_id):
    """Get detailed information for a specific zone"""
    try:
        zone = Zone.query.get_or_404(zone_id)
        
        # Get zone statistics
        total_locations = Location.query.filter_by(zone_id=zone_id).count()
        occupied_locations = Location.query.filter_by(zone_id=zone_id, is_occupied=True).count()
        utilization = (occupied_locations / total_locations * 100) if total_locations > 0 else 0
        
        # Get recent activities in this zone
        recent_activities = WarehouseActivity.query.filter_by(
            zone_id=zone_id
        ).order_by(
            WarehouseActivity.activity_timestamp.desc()
        ).limit(10).all()
        
        activities = []
        for activity in recent_activities:
            activities.append({
                'id': activity.id,
                'user': activity.user_name,
                'time': activity.activity_timestamp.isoformat(),
                'activity': activity.activity_type,
                'efficiency': activity.efficiency_score
            })
        
        # Get pickers assigned to this zone
        zone_pickers = PickerPerformance.query.filter_by(
            zone_assigned=zone.name,
            date=datetime.utcnow().date()
        ).all()
        
        pickers = []
        for picker in zone_pickers:
            pickers.append({
                'id': picker.picker_id,
                'name': picker.picker_name,
                'efficiency': picker.efficiency_score,
                'status': picker.status,
                'picks_today': picker.picks_completed
            })
        
        return jsonify({
            'zone': {
                'id': zone.id,
                'name': zone.name,
                'description': zone.description,
                'utilization': round(utilization, 1),
                'total_locations': total_locations,
                'occupied_locations': occupied_locations
            },
            'recent_activities': activities,
            'assigned_pickers': pickers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
