"""
Daily Inventory Cycle API Routes
Date: September 18, 2025
Purpose: API endpoints for daily inventory opening/closing cycles
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import logging

from services.daily_inventory_cycle_service import DailyInventoryCycleService
from modules.inventory.daily_cycle_models import (
    DailyInventoryBalance, DailyInventoryCycleStatus, DailyInventoryTransactionSummary
)

logger = logging.getLogger(__name__)

# Create blueprint
inventory_daily_cycle_bp = Blueprint('inventory_daily_cycle', __name__, url_prefix='/api/inventory/daily-cycle')

# Initialize service
inventory_cycle_service = DailyInventoryCycleService()

@inventory_daily_cycle_bp.route('/opening', methods=['POST'])
def capture_opening_inventory():
    """
    Capture opening inventory balances for a specific date
    POST /api/inventory/daily-cycle/opening
    """
    try:
        data = request.get_json() or {}
        
        # Parse date
        date_str = data.get('date')
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        # User information
        user_id = data.get('user_id', 'system')
        user_name = data.get('user_name')
        user_role = data.get('user_role')
        
        # Execute opening capture
        result = inventory_cycle_service.capture_opening_inventory(
            cycle_date=cycle_date,
            user_id=user_id,
            user_name=user_name,
            user_role=user_role
        )
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'],
                'error': result.get('error'),
                'data': result
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error capturing opening inventory: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_daily_cycle_bp.route('/closing', methods=['POST'])
def calculate_closing_inventory():
    """
    Calculate closing inventory balances for a specific date
    POST /api/inventory/daily-cycle/closing
    """
    try:
        data = request.get_json() or {}
        
        # Parse date
        date_str = data.get('date')
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        # User information
        user_id = data.get('user_id', 'system')
        user_name = data.get('user_name')
        user_role = data.get('user_role')
        
        # Execute closing calculation
        result = inventory_cycle_service.calculate_closing_inventory(
            cycle_date=cycle_date,
            user_id=user_id,
            user_name=user_name,
            user_role=user_role
        )
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'],
                'error': result.get('error'),
                'data': result
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error calculating closing inventory: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_daily_cycle_bp.route('/full-cycle', methods=['POST'])
def execute_full_inventory_cycle():
    """
    Execute complete inventory cycle (opening + closing)
    POST /api/inventory/daily-cycle/full-cycle
    """
    try:
        data = request.get_json() or {}
        
        # Parse date
        date_str = data.get('date')
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        # User information
        user_id = data.get('user_id', 'system')
        user_name = data.get('user_name')
        user_role = data.get('user_role')
        
        # Execute full cycle
        result = inventory_cycle_service.execute_full_inventory_cycle(
            cycle_date=cycle_date,
            user_id=user_id,
            user_name=user_name,
            user_role=user_role
        )
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'],
                'error': result.get('error'),
                'data': result
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error executing inventory cycle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_daily_cycle_bp.route('/status/<date_str>', methods=['GET'])
@inventory_daily_cycle_bp.route('/status', methods=['GET'])
def get_inventory_cycle_status(date_str=None):
    """
    Get inventory cycle status for a specific date
    GET /api/inventory/daily-cycle/status/2025-09-18
    GET /api/inventory/daily-cycle/status (defaults to today)
    """
    try:
        # Parse date
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        # Get status
        result = inventory_cycle_service.get_inventory_cycle_status(cycle_date)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error getting inventory cycle status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_daily_cycle_bp.route('/balances/<date_str>', methods=['GET'])
@inventory_daily_cycle_bp.route('/balances', methods=['GET'])
def get_daily_inventory_balances(date_str=None):
    """
    Get daily inventory balances for a specific date
    GET /api/inventory/daily-cycle/balances/2025-09-18
    GET /api/inventory/daily-cycle/balances (defaults to today)
    """
    try:
        # Parse date
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        # Get query parameters
        product_id = request.args.get('product_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get user ID from request headers for multi-tenancy
        user_id = request.headers.get('X-User-ID')
        print(f"[INVENTORY DAILY CYCLE] Received X-User-ID header: {user_id}")
        
        if not user_id:
            print("[INVENTORY DAILY CYCLE] No user ID provided, returning empty balances")
            return jsonify({
                'success': True,
                'data': [],
                'summary': {
                    'cycle_date': cycle_date.isoformat(),
                    'total_products': 0,
                    'total_inventory_value': 0.0,
                    'total_quantity_on_hand': 0.0
                }
            }), 200
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            print(f"[INVENTORY DAILY CYCLE] Invalid user ID format: {user_id}")
            return jsonify({'success': False, 'error': 'Invalid user ID format'}), 400
        
        # Get user's product IDs for multi-tenancy
        from modules.inventory.advanced_models import InventoryProduct
        user_product_ids = [p.id for p in InventoryProduct.query.filter(
            InventoryProduct.user_id == user_id_int
        ).all()]
        
        # Build query with multi-tenancy
        query = DailyInventoryBalance.query.filter(
            DailyInventoryBalance.cycle_date == cycle_date,
            DailyInventoryBalance.product_id.in_(user_product_ids)
        )
        
        if product_id and product_id in user_product_ids:
            query = query.filter(DailyInventoryBalance.product_id == product_id)
        if warehouse_id:
            query = query.filter(DailyInventoryBalance.simple_warehouse_id == warehouse_id)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        balances = query.offset(offset).limit(limit).all()
        
        # Format response
        balance_data = []
        for balance in balances:
            balance_data.append({
                'id': balance.id,
                'product_id': balance.product_id,
                'product_name': balance.product.name if balance.product else None,
                'product_sku': balance.product.sku if balance.product else None,
                'warehouse_id': balance.simple_warehouse_id,
                'warehouse_name': balance.simple_warehouse.name if balance.simple_warehouse else None,
                'opening_quantity': balance.opening_quantity,
                'opening_unit_cost': balance.opening_unit_cost,
                'opening_total_value': balance.opening_total_value,
                'closing_quantity': balance.closing_quantity,
                'closing_unit_cost': balance.closing_unit_cost,
                'closing_total_value': balance.closing_total_value,
                'net_quantity_change': balance.net_quantity_change,
                'net_value_change': balance.net_value_change,
                'quantity_received': balance.quantity_received,
                'quantity_issued': balance.quantity_issued,
                'quantity_adjusted': balance.quantity_adjusted,
                'cost_method': balance.cost_method,
                'currency': balance.currency,
                'is_locked': balance.is_locked
            })
        
        return jsonify({
            'success': True,
            'data': {
                'cycle_date': cycle_date.isoformat(),
                'balances': balance_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error getting daily inventory balances: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_daily_cycle_bp.route('/summary/<date_str>', methods=['GET'])
@inventory_daily_cycle_bp.route('/summary', methods=['GET'])
def get_daily_inventory_summary(date_str=None):
    """
    Get daily inventory summary for a specific date
    GET /api/inventory/daily-cycle/summary/2025-09-18
    GET /api/inventory/daily-cycle/summary (defaults to today)
    """
    try:
        # Parse date
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        # Get user ID from request headers for multi-tenancy
        user_id = request.headers.get('X-User-ID')
        print(f"[INVENTORY DAILY CYCLE SUMMARY] Received X-User-ID header: {user_id}")
        
        if not user_id:
            print("[INVENTORY DAILY CYCLE SUMMARY] No user ID provided, returning empty summary")
            return jsonify({
                'success': False,
                'message': f'No inventory cycle found for {cycle_date}',
                'data': {
                    'cycle_date': cycle_date.isoformat(),
                    'status': 'not_found'
                }
            })
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            print(f"[INVENTORY DAILY CYCLE SUMMARY] Invalid user ID format: {user_id}")
            return jsonify({'success': False, 'error': 'Invalid user ID format'}), 400
        
        # Get cycle status
        cycle_status = DailyInventoryCycleStatus.get_cycle_status(cycle_date)
        
        if not cycle_status:
            return jsonify({
                'success': False,
                'message': f'No inventory cycle found for {cycle_date}',
                'data': {
                    'cycle_date': cycle_date.isoformat(),
                    'status': 'not_found'
                }
            })
        
        # Get transaction summaries
        summaries = DailyInventoryTransactionSummary.query.filter_by(
            summary_date=cycle_date
        ).all()
        
        # Calculate summary metrics
        total_transactions = sum(s.total_transactions for s in summaries)
        total_receipts = sum(s.receipts_quantity for s in summaries)
        total_issues = sum(s.issues_quantity for s in summaries)
        total_adjustments = sum(s.adjustments_quantity for s in summaries)
        
        # Get top products by value
        top_products = DailyInventoryBalance.query.filter_by(
            cycle_date=cycle_date
        ).order_by(DailyInventoryBalance.closing_total_value.desc()).limit(10).all()
        
        top_products_data = [{
            'product_id': balance.product_id,
            'product_name': balance.product.name if balance.product else 'Unknown',
            'product_sku': balance.product.sku if balance.product else None,
            'closing_quantity': balance.closing_quantity,
            'closing_value': balance.closing_total_value,
            'net_change': balance.net_value_change
        } for balance in top_products]
        
        return jsonify({
            'success': True,
            'data': {
                'cycle_date': cycle_date.isoformat(),
                'status': {
                    'opening_status': cycle_status.opening_status,
                    'closing_status': cycle_status.closing_status,
                    'is_complete': cycle_status.is_complete(),
                    'is_locked': cycle_status.is_locked
                },
                'metrics': {
                    'total_products_processed': cycle_status.total_products_processed,
                    'total_locations_processed': cycle_status.total_locations_processed,
                    'total_inventory_value': cycle_status.total_inventory_value,
                    'total_quantity_on_hand': cycle_status.total_quantity_on_hand,
                    'total_transactions': total_transactions,
                    'total_receipts': total_receipts,
                    'total_issues': total_issues,
                    'total_adjustments': total_adjustments
                },
                'top_products': top_products_data,
                'timing': {
                    'opening_started_at': cycle_status.opening_started_at.isoformat() if cycle_status.opening_started_at else None,
                    'opening_completed_at': cycle_status.opening_completed_at.isoformat() if cycle_status.opening_completed_at else None,
                    'closing_started_at': cycle_status.closing_started_at.isoformat() if cycle_status.closing_started_at else None,
                    'closing_completed_at': cycle_status.closing_completed_at.isoformat() if cycle_status.closing_completed_at else None
                }
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error getting daily inventory summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_daily_cycle_bp.route('/history', methods=['GET'])
def get_inventory_cycle_history():
    """
    Get inventory cycle history for a date range
    GET /api/inventory/daily-cycle/history?start_date=2025-09-01&end_date=2025-09-18
    """
    try:
        # Parse query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = request.args.get('limit', 30, type=int)
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = date.today() - timedelta(days=30)
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = date.today()
        
        # Get cycle statuses
        cycles = DailyInventoryCycleStatus.query.filter(
            DailyInventoryCycleStatus.cycle_date >= start_date,
            DailyInventoryCycleStatus.cycle_date <= end_date
        ).order_by(DailyInventoryCycleStatus.cycle_date.desc()).limit(limit).all()
        
        cycle_data = []
        for cycle in cycles:
            cycle_data.append({
                'cycle_date': cycle.cycle_date.isoformat(),
                'opening_status': cycle.opening_status,
                'closing_status': cycle.closing_status,
                'is_complete': cycle.is_complete(),
                'total_products': cycle.total_products_processed,
                'total_inventory_value': cycle.total_inventory_value,
                'total_quantity_on_hand': cycle.total_quantity_on_hand,
                'error_message': cycle.error_message,
                'processing_times': {
                    'opening_duration': (
                        (cycle.opening_completed_at - cycle.opening_started_at).total_seconds()
                        if cycle.opening_started_at and cycle.opening_completed_at else None
                    ),
                    'closing_duration': (
                        (cycle.closing_completed_at - cycle.closing_started_at).total_seconds()
                        if cycle.closing_started_at and cycle.closing_completed_at else None
                    )
                }
            })
        
        return jsonify({
            'success': True,
            'data': {
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'cycles': cycle_data,
                'total_cycles': len(cycle_data)
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error getting inventory cycle history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_daily_cycle_bp.route('/demo', methods=['POST'])
def demo_inventory_cycle():
    """
    Demo endpoint to test the complete inventory cycle system
    POST /api/inventory/daily-cycle/demo
    """
    try:
        data = request.get_json() or {}
        
        # Use provided date or today
        date_str = data.get('date')
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        user_id = data.get('user_id', 'demo_user')
        
        # Execute full cycle
        result = inventory_cycle_service.execute_full_inventory_cycle(
            cycle_date=cycle_date,
            user_id=user_id,
            user_name='Demo User',
            user_role='System Admin'
        )
        
        # Get summary
        summary_result = inventory_cycle_service.get_inventory_cycle_status(cycle_date)
        
        return jsonify({
            'success': True,
            'message': 'Inventory cycle demo completed',
            'data': {
                'cycle_result': result,
                'cycle_summary': summary_result,
                'demo_info': {
                    'cycle_date': cycle_date.isoformat(),
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error in inventory cycle demo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

