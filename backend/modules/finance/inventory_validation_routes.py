"""
Finance-Inventory Validation API Routes
Date: September 18, 2025
Purpose: API endpoints for validating finance entries against inventory
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from services.inventory_validation_service import (
    InventoryValidationService, validate_finance_entry_against_inventory, 
    create_proper_sales_entry
)

logger = logging.getLogger(__name__)

# Create blueprint
finance_inventory_validation_bp = Blueprint(
    'finance_inventory_validation', __name__, 
    url_prefix='/api/finance/inventory-validation'
)

# Initialize service
validation_service = InventoryValidationService()

@finance_inventory_validation_bp.route('/validate-entry', methods=['POST'])
def validate_journal_entry():
    """
    Validate journal entry against inventory business rules
    POST /api/finance/inventory-validation/validate-entry
    """
    try:
        data = request.get_json() or {}
        
        # Get validation mode
        strict_mode = data.get('strict_mode', True)
        
        # Extract journal entry data
        journal_data = {
            'description': data.get('description', ''),
            'lines': data.get('lines', []),
            'date': data.get('date'),
            'reference': data.get('reference', '')
        }
        
        # Validate entry
        result = validation_service.enforce_inventory_business_rules(journal_data, strict_mode)
        
        return jsonify({
            'success': True,
            'validation_result': result,
            'message': 'Validation completed',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error validating journal entry: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@finance_inventory_validation_bp.route('/create-integrated-sale', methods=['POST'])
def create_integrated_sales_entry():
    """
    Create proper sales entry with automatic inventory and COGS handling
    POST /api/finance/inventory-validation/create-integrated-sale
    """
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ['product_name', 'quantity', 'unit_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Required field missing: {field}'
                }), 400
        
        # Create integrated sales entry
        result = validation_service.create_integrated_sales_entry(data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Failed to create integrated sales entry'),
                'error': result.get('error'),
                'suggestion': result.get('suggestion')
            }), 400
            
    except Exception as e:
        logger.error(f"Error creating integrated sales entry: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@finance_inventory_validation_bp.route('/check-product', methods=['POST'])
def check_product_availability():
    """
    Check if a product exists in inventory and has sufficient stock
    POST /api/finance/inventory-validation/check-product
    """
    try:
        data = request.get_json() or {}
        
        product_name = data.get('product_name', '')
        transaction_amount = data.get('transaction_amount', 0)
        
        if not product_name:
            return jsonify({
                'success': False,
                'error': 'Product name is required'
            }), 400
        
        # Check product inventory
        check_result = validation_service._check_product_inventory(product_name, transaction_amount)
        
        return jsonify({
            'success': True,
            'data': check_result,
            'message': f'Product check completed for "{product_name}"'
        })
        
    except Exception as e:
        logger.error(f"Error checking product availability: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@finance_inventory_validation_bp.route('/demo/problematic-entry', methods=['POST'])
def demo_problematic_entry():
    """
    Demo endpoint showing what happens with problematic entries like "sold juice"
    POST /api/finance/inventory-validation/demo/problematic-entry
    """
    try:
        # Create a problematic journal entry
        problematic_entry = {
            'description': 'sold juice to customer',
            'lines': [
                {
                    'account': 'Cash',
                    'debit': 100,
                    'credit': 0,
                    'description': 'Cash received from juice sale'
                },
                {
                    'account': 'Sales Revenue',
                    'debit': 0,
                    'credit': 100,
                    'description': 'Revenue from juice sale'
                }
            ],
            'date': datetime.now().isoformat(),
            'reference': 'DEMO-PROBLEMATIC-001'
        }
        
        # Validate in strict mode
        strict_result = validation_service.enforce_inventory_business_rules(problematic_entry, strict_mode=True)
        
        # Validate in warning mode
        warning_result = validation_service.enforce_inventory_business_rules(problematic_entry, strict_mode=False)
        
        # Get integration suggestions
        integration_suggestions = validation_service.suggest_inventory_integration(problematic_entry)
        
        return jsonify({
            'success': True,
            'message': 'Problematic entry demo completed',
            'data': {
                'problematic_entry': problematic_entry,
                'strict_mode_result': strict_result,
                'warning_mode_result': warning_result,
                'integration_suggestions': integration_suggestions,
                'explanation': {
                    'problem': 'Entry mentions "juice" but no juice product exists in inventory',
                    'strict_mode': 'BLOCKS the entry - prevents data corruption',
                    'warning_mode': 'ALLOWS the entry but shows warnings',
                    'recommendation': 'Create juice product in inventory first, then use integrated sales process'
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error in problematic entry demo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@finance_inventory_validation_bp.route('/demo/proper-sale', methods=['POST'])
def demo_proper_sales_process():
    """
    Demo endpoint showing the proper way to handle sales with inventory integration
    POST /api/finance/inventory-validation/demo/proper-sale
    """
    try:
        data = request.get_json() or {}
        
        # Use provided data or defaults
        sales_data = {
            'product_name': data.get('product_name', 'Demo Product'),
            'quantity': data.get('quantity', 10),
            'unit_price': data.get('unit_price', 15.00),
            'customer_name': data.get('customer_name', 'Demo Customer'),
            'invoice_reference': f'INV-PROPER-{datetime.now().strftime("%Y%m%d%H%M")}',
            'sale_date': datetime.now(),
            'customer_id': data.get('customer_id', 1),
            'warehouse_id': data.get('warehouse_id', 1)
        }
        
        # Create proper integrated sales entry
        result = validation_service.create_integrated_sales_entry(sales_data)
        
        return jsonify({
            'success': True,
            'message': 'Proper sales process demo completed',
            'data': {
                'sales_data': sales_data,
                'integration_result': result,
                'explanation': {
                    'process': 'Proper ERP sales process with inventory integration',
                    'step_1': 'Check product exists in inventory',
                    'step_2': 'Verify sufficient stock available',
                    'step_3': 'Create customer invoice (A/R + Revenue)',
                    'step_4': 'Create inventory issue (COGS + Inventory reduction)',
                    'step_5': 'Update inventory levels',
                    'result': 'Complete audit trail with accurate costs'
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error in proper sales demo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

