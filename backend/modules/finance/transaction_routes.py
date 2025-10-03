"""
Transaction Templates API Routes
===============================

This module provides API endpoints for the transaction templates system.
Users can create business transactions using simple templates instead of
manual journal entries.

Phase 2: Business Logic Templates API
"""

from flask import Blueprint, request, jsonify
from app import db
from modules.finance.transaction_templates import transaction_manager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Debug: Check if transaction_manager is loaded
logger.info(f"Transaction manager loaded: {transaction_manager}")
logger.info(f"Available templates: {list(transaction_manager.templates.keys()) if transaction_manager else 'None'}")

# Create blueprint
transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/finance/transactions')

@transaction_bp.route('/templates', methods=['GET'])
def get_transaction_templates():
    """Get all available transaction templates"""
    try:
        templates = transaction_manager.get_all_templates()
        return jsonify({
            "success": True,
            "templates": templates
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transaction templates: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get transaction templates"
        }), 500

@transaction_bp.route('/templates/<template_id>', methods=['GET'])
def get_transaction_template(template_id):
    """Get a specific transaction template"""
    try:
        template = transaction_manager.get_template(template_id)
        if not template:
            return jsonify({
                "success": False,
                "error": f"Template '{template_id}' not found"
            }), 404
        
        return jsonify({
            "success": True,
            "template": {
                "id": template.template_id,
                "name": template.name,
                "description": template.description,
                "required_fields": template.get_required_fields()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transaction template: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get transaction template"
        }), 500

@transaction_bp.route('/create', methods=['POST'])
def create_transaction():
    """Create a transaction using a template"""
    try:
        data = request.get_json()
        user_id = request.headers.get('X-User-ID')
        
        logger.info(f"Creating transaction with data: {data}, user_id: {user_id}")
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User authentication required"
            }), 401
        
        user_id_int = int(user_id)
        template_id = data.get('template_id')
        
        if not template_id:
            return jsonify({
                "success": False,
                "error": "Template ID is required"
            }), 400
        
        # Validate required fields
        template = transaction_manager.get_template(template_id)
        if not template:
            return jsonify({
                "success": False,
                "error": f"Template '{template_id}' not found"
            }), 404
        
        # Check required fields
        required_fields = template.get_required_fields()
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields
            }), 400
        
        logger.info(f"Creating transaction with template {template_id} for user {user_id_int}")
        
        # Create the transaction
        result = transaction_manager.create_transaction(template_id, user_id_int, **data)
        
        logger.info(f"Transaction created successfully: {result}")
        
        return jsonify({
            "success": True,
            "message": result["message"],
            "transaction": {
                "entry_id": result["entry_id"],
                "reference": result["reference"],
                "template_used": result["template_used"],
                "total_debits": result["total_debits"],
                "total_credits": result["total_credits"]
            }
        }), 201
        
    except ValueError as e:
        logger.error(f"ValueError in create_transaction: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating transaction: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": "Failed to create transaction"
        }), 500

@transaction_bp.route('/examples', methods=['GET'])
def get_transaction_examples():
    """Get example transactions for each template"""
    try:
        examples = {
            "cash_sales": {
                "template_id": "cash_sales",
                "name": "Cash Sales",
                "example": {
                    "amount": 500.00,
                    "description": "Sale of product to customer"
                },
                "explanation": "Creates: Cash (Debit $500) + Sales Revenue (Credit $500)"
            },
            "bank_sales": {
                "template_id": "bank_sales",
                "name": "Bank Sales",
                "example": {
                    "amount": 1000.00,
                    "description": "Bank transfer payment received"
                },
                "explanation": "Creates: Bank Account (Debit $1000) + Sales Revenue (Credit $1000)"
            },
            "expense_payment": {
                "template_id": "expense_payment",
                "name": "Expense Payment",
                "example": {
                    "amount": 150.00,
                    "description": "Office supplies purchase",
                    "payment_method": "cash"
                },
                "explanation": "Creates: Operating Expenses (Debit $150) + Cash (Credit $150)"
            },
            "purchase": {
                "template_id": "purchase",
                "name": "Purchase",
                "example": {
                    "amount": 800.00,
                    "description": "Inventory purchase from supplier",
                    "payment_method": "bank",
                    "purchase_type": "inventory"
                },
                "explanation": "Creates: Inventory (Debit $800) + Bank Account (Credit $800)"
            },
            "loan_receipt": {
                "template_id": "loan_receipt",
                "name": "Loan Receipt",
                "example": {
                    "amount": 5000.00,
                    "description": "Business loan from bank"
                },
                "explanation": "Creates: Bank Account (Debit $5000) + Accounts Payable (Credit $5000)"
            }
        }
        
        return jsonify({
            "success": True,
            "examples": examples
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transaction examples: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get transaction examples"
        }), 500

@transaction_bp.route('/validate', methods=['POST'])
def validate_transaction():
    """Validate transaction data without creating it"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        
        if not template_id:
            return jsonify({
                "success": False,
                "error": "Template ID is required"
            }), 400
        
        template = transaction_manager.get_template(template_id)
        if not template:
            return jsonify({
                "success": False,
                "error": f"Template '{template_id}' not found"
            }), 404
        
        # Validate input
        is_valid = template.validate_input(**data)
        
        if is_valid:
            # Try to create journal entry data (without saving)
            try:
                journal_data = template.create_journal_entry(**data)
                return jsonify({
                    "success": True,
                    "valid": True,
                    "preview": {
                        "description": journal_data["description"],
                        "payment_method": journal_data["payment_method"],
                        "lines": journal_data["lines"],
                        "total_debits": journal_data["total_debits"],
                        "total_credits": journal_data["total_credits"],
                        "is_balanced": journal_data["total_debits"] == journal_data["total_credits"]
                    }
                }), 200
            except Exception as e:
                return jsonify({
                    "success": True,
                    "valid": False,
                    "error": str(e)
                }), 200
        else:
            required_fields = template.get_required_fields()
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({
                "success": True,
                "valid": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields
            }), 200
        
    except Exception as e:
        logger.error(f"Error validating transaction: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to validate transaction"
        }), 500
