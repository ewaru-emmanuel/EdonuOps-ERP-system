"""
Inventory-Finance Integration API Routes
Date: September 18, 2025
Purpose: API endpoints for inventory-finance synchronization
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import logging

from services.inventory_finance_sync_service import (
    InventoryFinanceSyncService, sync_inventory_transaction, 
    reconcile_daily_balances, run_synchronized_cycle
)

logger = logging.getLogger(__name__)

# Create blueprint
inventory_finance_integration_bp = Blueprint(
    'inventory_finance_integration', __name__, 
    url_prefix='/api/integration/inventory-finance'
)

# Initialize service
sync_service = InventoryFinanceSyncService()

@inventory_finance_integration_bp.route('/process-transaction', methods=['POST'])
def process_inventory_transaction():
    """
    Process inventory transaction with real-time GL integration
    POST /api/integration/inventory-finance/process-transaction
    """
    try:
        data = request.get_json() or {}
        
        # Validate required fields based on transaction type
        transaction_type = data.get('transaction_type')
        required_fields = ['transaction_type', 'product_id']
        
        # Add type-specific required fields
        if transaction_type in ['receive', 'issue', 'transfer']:
            required_fields.append('quantity')
        elif transaction_type == 'adjustment':
            required_fields.append('adjustment_quantity')
        elif transaction_type == 'revaluation':
            required_fields.extend(['quantity', 'old_unit_cost', 'new_unit_cost'])
        elif transaction_type == 'writeoff':
            required_fields.append('quantity')
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Required field missing for {transaction_type}: {field}'
                }), 400
        
        # Process transaction
        result = sync_service.process_inventory_transaction(data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Transaction processing failed'),
                'error': result.get('error'),
                'data': result
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing inventory transaction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_finance_integration_bp.route('/reconcile', methods=['POST'])
def reconcile_balances():
    """
    Reconcile inventory and GL balances for a specific date
    POST /api/integration/inventory-finance/reconcile
    """
    try:
        data = request.get_json() or {}
        
        # Parse date
        date_str = data.get('date')
        if date_str:
            as_of_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            as_of_date = date.today()
        
        # Perform reconciliation
        result = sync_service.reconcile_inventory_gl_balances(as_of_date)
        
        return jsonify({
            'success': True,
            'message': f'Reconciliation completed for {as_of_date}',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error reconciling balances: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_finance_integration_bp.route('/synchronized-cycle', methods=['POST'])
def run_synchronized_daily_cycle():
    """
    Run synchronized daily cycle for both inventory and finance
    POST /api/integration/inventory-finance/synchronized-cycle
    """
    try:
        data = request.get_json() or {}
        
        # Parse date
        date_str = data.get('date')
        if date_str:
            cycle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            cycle_date = date.today()
        
        user_id = data.get('user_id', 'system')
        
        # Execute synchronized cycle
        result = sync_service.execute_synchronized_daily_cycle(cycle_date, user_id)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Synchronized cycle failed'),
                'error': result.get('error'),
                'data': result
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error running synchronized cycle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_finance_integration_bp.route('/status', methods=['GET'])
def get_integration_status():
    """
    Get overall inventory-finance integration status
    GET /api/integration/inventory-finance/status
    """
    try:
        result = sync_service.get_integration_status()
        
        return jsonify({
            'success': True,
            'message': 'Integration status retrieved',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_finance_integration_bp.route('/demo/complete-flow', methods=['POST'])
def demo_complete_inventory_finance_flow():
    """
    Demo complete inventory-finance integration flow
    POST /api/integration/inventory-finance/demo/complete-flow
    """
    try:
        data = request.get_json() or {}
        
        demo_results = {
            'steps': [],
            'journal_entries': [],
            'inventory_updates': [],
            'reconciliation': {}
        }
        
        # Step 1: Purchase Receipt
        receipt_data = {
            'transaction_type': 'receive',
            'product_id': data.get('product_id', 1),
            'item_name': data.get('item_name', 'Demo Product'),
            'quantity': data.get('quantity', 100),
            'unit_cost': data.get('unit_cost', 25.00),
            'po_reference': f'PO-DEMO-{datetime.now().strftime("%Y%m%d%H%M")}',
            'receipt_date': datetime.now(),
            'warehouse_id': data.get('warehouse_id', 1)
        }
        
        receipt_result = sync_service.process_inventory_transaction(receipt_data)
        demo_results['steps'].append('Purchase Receipt Processed')
        demo_results['journal_entries'].extend(receipt_result.get('results', {}).get('journal_entries', []))
        
        # Step 2: Sales Issue (COGS)
        issue_data = {
            'transaction_type': 'issue',
            'product_id': data.get('product_id', 1),
            'item_name': data.get('item_name', 'Demo Product'),
            'quantity': data.get('sales_quantity', 30),
            'unit_cost': data.get('unit_cost', 25.00),
            'reference': f'SALE-DEMO-{datetime.now().strftime("%Y%m%d%H%M")}',
            'issue_date': datetime.now(),
            'customer_id': data.get('customer_id', 1),
            'warehouse_id': data.get('warehouse_id', 1)
        }
        
        issue_result = sync_service.process_inventory_transaction(issue_data)
        demo_results['steps'].append('Sales Issue Processed (COGS Created)')
        demo_results['journal_entries'].extend(issue_result.get('results', {}).get('journal_entries', []))
        
        # Step 3: Inventory Adjustment
        adjustment_data = {
            'transaction_type': 'adjustment',
            'product_id': data.get('product_id', 1),
            'item_name': data.get('item_name', 'Demo Product'),
            'adjustment_quantity': data.get('adjustment_quantity', -5),  # Found 5 less items
            'unit_cost': data.get('unit_cost', 25.00),
            'reason': 'Physical Count',
            'reference': f'ADJ-DEMO-{datetime.now().strftime("%Y%m%d%H%M")}',
            'adjustment_date': datetime.now(),
            'warehouse_id': data.get('warehouse_id', 1)
        }
        
        adjustment_result = sync_service.process_inventory_transaction(adjustment_data)
        demo_results['steps'].append('Inventory Adjustment Processed')
        demo_results['journal_entries'].extend(adjustment_result.get('results', {}).get('journal_entries', []))
        
        # Step 4: Reconciliation
        reconciliation_result = sync_service.reconcile_inventory_gl_balances()
        demo_results['reconciliation'] = reconciliation_result
        demo_results['steps'].append('Inventory-GL Reconciliation Completed')
        
        return jsonify({
            'success': True,
            'message': 'Complete inventory-finance integration demo completed',
            'data': demo_results,
            'summary': {
                'total_steps': len(demo_results['steps']),
                'total_journal_entries': len(demo_results['journal_entries']),
                'is_reconciled': reconciliation_result.get('reconciliation', {}).get('is_balanced', False),
                'demo_timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in complete flow demo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
