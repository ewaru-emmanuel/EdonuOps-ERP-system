from flask import Blueprint, jsonify, request
from app import db
from modules.inventory.advanced_models import (
    WarehouseActivity, PredictiveStockout, PickerPerformance, 
    AdvancedWarehouse, AdvancedLocation, InventoryProduct
)
from datetime import datetime, timedelta
import random

# Create blueprint for inventory manager routes
manager_inventory_bp = Blueprint('manager_inventory', __name__, url_prefix='/api/inventory/manager')

@manager_inventory_bp.route('/warehouse-map', methods=['GET'])
def get_warehouse_map():
    """Get warehouse map data for manager dashboard"""
    try:
        # Get warehouses and their locations
        warehouses = AdvancedWarehouse.query.all()
        locations = AdvancedLocation.query.all()
        
        warehouse_data = []
        for warehouse in warehouses:
            warehouse_locations = [loc for loc in locations if loc.warehouse_id == warehouse.id]
            warehouse_data.append({
                'id': warehouse.id,
                'name': warehouse.name,
                'type': warehouse.warehouse_type,
                'capacity': warehouse.capacity,
                'utilization': warehouse.utilization_percentage,
                'locations': [
                    {
                        'id': loc.id,
                        'name': loc.location_name,
                        'type': loc.location_type,
                        'capacity': loc.capacity,
                        'utilization': loc.utilization_percentage,
                        'status': loc.status
                    } for loc in warehouse_locations
                ]
            })
        
        return jsonify({
            'status': 'success',
            'warehouses': warehouse_data
        }), 200
    except Exception as e:
        print(f"Error in get_warehouse_map: {str(e)}")
        return jsonify({'error': str(e)}), 500

@manager_inventory_bp.route('/predictive-alerts', methods=['GET'])
def get_predictive_alerts():
    """Get predictive stockout alerts for manager dashboard"""
    try:
        # Get predictive stockouts
        stockouts = PredictiveStockout.query.filter(
            PredictiveStockout.alert_level.in_(['warning', 'critical'])
        ).order_by(PredictiveStockout.predicted_stockout_date).limit(10).all()
        
        alerts_data = []
        for stockout in stockouts:
            alerts_data.append({
                'id': stockout.id,
                'product_name': stockout.product.name if stockout.product else 'Unknown Product',
                'location_name': stockout.location.location_name if stockout.location else 'All Locations',
                'predicted_date': stockout.predicted_stockout_date.isoformat(),
                'days_until_stockout': stockout.days_until_stockout,
                'current_stock': stockout.current_stock,
                'consumption_rate': stockout.daily_consumption_rate,
                'alert_level': stockout.alert_level,
                'confidence_score': stockout.confidence_score
            })
        
        return jsonify({
            'status': 'success',
            'alerts': alerts_data
        }), 200
    except Exception as e:
        print(f"Error in get_predictive_alerts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@manager_inventory_bp.route('/picker-performance', methods=['GET'])
def get_picker_performance():
    """Get picker performance data for manager dashboard"""
    try:
        # Get recent picker performance data
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        performances = PickerPerformance.query.filter(
            PickerPerformance.performance_date >= week_ago
        ).order_by(PickerPerformance.performance_date.desc()).limit(20).all()
        
        performance_data = []
        for perf in performances:
            performance_data.append({
                'id': perf.id,
                'user_id': perf.user_id,
                'warehouse_name': perf.warehouse.name if perf.warehouse else 'Unknown Warehouse',
                'performance_date': perf.performance_date.isoformat(),
                'total_picks': perf.total_picks,
                'total_items_picked': perf.total_items_picked,
                'total_pick_time_seconds': perf.total_pick_time_seconds,
                'efficiency_score': perf.efficiency_score,
                'picks_per_hour': perf.picks_per_hour,
                'warehouse_average_picks_per_hour': perf.warehouse_average_picks_per_hour,
                'accuracy_rate': perf.accuracy_rate
            })
        
        return jsonify({
            'status': 'success',
            'performances': performance_data
        }), 200
    except Exception as e:
        print(f"Error in get_picker_performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@manager_inventory_bp.route('/live-activity', methods=['GET'])
def get_live_activity():
    """Get live warehouse activity for manager dashboard"""
    try:
        # Get recent warehouse activities
        today = datetime.now()
        hour_ago = today - timedelta(hours=1)
        
        activities = WarehouseActivity.query.filter(
            WarehouseActivity.activity_timestamp >= hour_ago
        ).order_by(WarehouseActivity.activity_timestamp.desc()).limit(50).all()
        
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
        
        return jsonify({
            'status': 'success',
            'activities': activity_data
        }), 200
    except Exception as e:
        print(f"Error in get_live_activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

