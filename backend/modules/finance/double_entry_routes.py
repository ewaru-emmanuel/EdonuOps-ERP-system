"""
Double Entry Accounting API Routes
Date: September 18, 2025
Purpose: API endpoints to demonstrate complete double entry system
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
import logging

from modules.finance.double_entry_service import (
    DoubleEntryService, demo_complete_procurement_cycle, 
    demo_complete_sales_cycle, get_system_status
)

logger = logging.getLogger(__name__)

# Create blueprint
double_entry_bp = Blueprint('double_entry', __name__, url_prefix='/api/finance/double-entry')

@double_entry_bp.route('/demo/procurement-cycle', methods=['POST'])
def demo_procurement_cycle():
    """
    Demo complete procurement cycle with GR/IR clearing
    POST /api/finance/double-entry/demo/procurement-cycle
    """
    try:
        data = request.get_json() or {}
        service = DoubleEntryService()
        
        # Use provided data or defaults
        procurement_data = {
            'item_name': data.get('item_name', 'Demo Item'),
            'quantity': data.get('quantity', 10),
            'unit_cost': data.get('unit_cost', 50.00),
            'vendor_name': data.get('vendor_name', 'Demo Vendor'),
            'po_number': data.get('po_number', f'PO-DEMO-{datetime.now().strftime("%Y%m%d%H%M")}'),
            'invoice_number': data.get('invoice_number', f'INV-DEMO-{datetime.now().strftime("%Y%m%d%H%M")}'),
            'payment_reference': data.get('payment_reference', f'PAY-DEMO-{datetime.now().strftime("%Y%m%d%H%M")}'),
            'goods_received': data.get('goods_received', True),
            'invoice_received': data.get('invoice_received', True),
            'payment_made': data.get('payment_made', True),
            'vendor_id': data.get('vendor_id', 1),
            'item_id': data.get('item_id', 1),
            'po_id': data.get('po_id', 1)
        }
        
        result = service.process_complete_procurement_cycle(procurement_data)
        
        return jsonify({
            'success': True,
            'message': 'Procurement cycle demo completed',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in procurement cycle demo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@double_entry_bp.route('/demo/sales-cycle', methods=['POST'])
def demo_sales_cycle():
    """
    Demo complete sales cycle
    POST /api/finance/double-entry/demo/sales-cycle
    """
    try:
        data = request.get_json() or {}
        service = DoubleEntryService()
        
        # Calculate amounts
        quantity = data.get('quantity', 20)
        unit_cost = data.get('unit_cost', 30.00)
        unit_price = data.get('unit_price', 50.00)
        invoice_amount = quantity * unit_price
        
        sales_data = {
            'customer_name': data.get('customer_name', 'Demo Customer'),
            'item_name': data.get('item_name', 'Demo Product'),
            'quantity': quantity,
            'unit_cost': unit_cost,
            'unit_price': unit_price,
            'invoice_amount': invoice_amount,
            'payment_amount': invoice_amount,
            'invoice_number': data.get('invoice_number', f'INV-SALES-{datetime.now().strftime("%Y%m%d%H%M")}'),
            'payment_reference': data.get('payment_reference', f'PAY-SALES-{datetime.now().strftime("%Y%m%d%H%M")}'),
            'invoice_created': data.get('invoice_created', True),
            'inventory_sold': data.get('inventory_sold', True),
            'payment_received': data.get('payment_received', True),
            'customer_id': data.get('customer_id', 1),
            'item_id': data.get('item_id', 1)
        }
        
        result = service.process_complete_sales_cycle(sales_data)
        
        return jsonify({
            'success': True,
            'message': 'Sales cycle demo completed',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in sales cycle demo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@double_entry_bp.route('/posting-rules', methods=['GET'])
def get_posting_rules():
    """
    Get all configured posting rules
    GET /api/finance/double-entry/posting-rules
    """
    try:
        service = DoubleEntryService()
        rules = service.get_posting_rules_summary()
        
        return jsonify({
            'success': True,
            'data': rules
        })
        
    except Exception as e:
        logger.error(f"Error getting posting rules: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@double_entry_bp.route('/trial-balance', methods=['GET'])
def get_trial_balance():
    """
    Get trial balance as of a specific date
    GET /api/finance/double-entry/trial-balance?as_of_date=2025-09-18
    """
    try:
        # Get date parameter
        as_of_date_str = request.args.get('as_of_date')
        as_of_date = None
        
        if as_of_date_str:
            as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
        
        service = DoubleEntryService()
        trial_balance = service.get_trial_balance(as_of_date)
        
        return jsonify({
            'success': True,
            'data': trial_balance
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error getting trial balance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@double_entry_bp.route('/system-validation', methods=['GET'])
def validate_system():
    """
    Validate system integrity
    GET /api/finance/double-entry/system-validation
    """
    try:
        service = DoubleEntryService()
        validation = service.validate_system_integrity()
        
        return jsonify({
            'success': True,
            'data': validation
        })
        
    except Exception as e:
        logger.error(f"Error validating system: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@double_entry_bp.route('/system-status', methods=['GET'])
def get_complete_system_status():
    """
    Get complete system status including rules, trial balance, and validation
    GET /api/finance/double-entry/system-status
    """
    try:
        status = get_system_status()
        
        return jsonify({
            'success': True,
            'message': 'Complete double entry system status',
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@double_entry_bp.route('/quick-demo', methods=['POST'])
def quick_demo():
    """
    Quick demo of both procurement and sales cycles
    POST /api/finance/double-entry/quick-demo
    """
    try:
        # Run both demos
        procurement_result = demo_complete_procurement_cycle()
        sales_result = demo_complete_sales_cycle()
        
        # Get updated system status
        system_status = get_system_status()
        
        return jsonify({
            'success': True,
            'message': 'Quick demo completed - both procurement and sales cycles',
            'data': {
                'procurement_cycle': procurement_result,
                'sales_cycle': sales_result,
                'system_status': system_status
            },
            'summary': {
                'procurement_entries': len(procurement_result.get('journal_entries', [])),
                'sales_entries': len(sales_result.get('journal_entries', [])),
                'total_entries': len(procurement_result.get('journal_entries', [])) + len(sales_result.get('journal_entries', [])),
                'system_balanced': system_status.get('trial_balance', {}).get('totals', {}).get('is_balanced', False)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in quick demo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

