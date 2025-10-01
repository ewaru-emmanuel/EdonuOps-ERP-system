#!/usr/bin/env python3
"""
Warehouse Management Routes
Handles warehouse transfers, valuation, and related operations
"""

from flask import Blueprint, request, jsonify
from app import db
from modules.inventory.models import Warehouse, Product
from modules.inventory.advanced_models import InventoryTransaction
from modules.core.tenant_context import require_tenant, get_tenant_context
from modules.core.rate_limiting import api_endpoint_limit
import logging
from datetime import datetime, date
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Create blueprint
warehouse_bp = Blueprint('warehouse', __name__, url_prefix='/api/inventory/warehouse')

@warehouse_bp.route('/transfers', methods=['GET'])
@api_endpoint_limit()
@require_tenant
def get_warehouse_transfers():
    """Get all warehouse transfers for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        # Get transfers from inventory transactions
        transfers = db.session.query(InventoryTransaction).filter(
            InventoryTransaction.tenant_id == tenant_context.tenant_id,
            InventoryTransaction.transaction_type == 'transfer'
        ).order_by(InventoryTransaction.created_at.desc()).all()
        
        result = []
        for transfer in transfers:
            result.append({
                'id': transfer.id,
                'product_id': transfer.product_id,
                'from_warehouse_id': transfer.from_warehouse_id,
                'to_warehouse_id': transfer.to_warehouse_id,
                'quantity': float(transfer.quantity),
                'reference': transfer.reference,
                'status': transfer.status,
                'created_at': transfer.created_at.isoformat() if transfer.created_at else None,
                'created_by': transfer.created_by
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching warehouse transfers: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch warehouse transfers',
            'details': str(e)
        }), 500

@warehouse_bp.route('/transfers', methods=['POST'])
@api_endpoint_limit()
@require_tenant
def create_warehouse_transfer():
    """Create a new warehouse transfer"""
    try:
        data = request.get_json()
        tenant_context = get_tenant_context()
        
        # Validate required fields
        required_fields = ['product_id', 'from_warehouse_id', 'to_warehouse_id', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create transfer transaction
        transfer = InventoryTransaction(
            tenant_id=tenant_context.tenant_id,
            product_id=data['product_id'],
            from_warehouse_id=data['from_warehouse_id'],
            to_warehouse_id=data['to_warehouse_id'],
            quantity=data['quantity'],
            transaction_type='transfer',
            reference=data.get('reference', ''),
            status='pending',
            created_by=data.get('created_by', 'system')
        )
        
        db.session.add(transfer)
        db.session.commit()
        
        return jsonify({
            'message': 'Warehouse transfer created successfully',
            'transfer_id': transfer.id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating warehouse transfer: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create warehouse transfer',
            'details': str(e)
        }), 500

@warehouse_bp.route('/valuation/warehouse', methods=['GET'])
@api_endpoint_limit()
@require_tenant
def get_warehouse_valuation():
    """Get warehouse valuation data"""
    try:
        tenant_context = get_tenant_context()
        warehouse_id = request.args.get('warehouse_id')
        
        # Get warehouse information
        warehouses = db.session.query(Warehouse).filter(
            Warehouse.tenant_id == tenant_context.tenant_id
        )
        
        if warehouse_id:
            warehouses = warehouses.filter(Warehouse.id == warehouse_id)
        
        warehouses = warehouses.all()
        
        result = []
        for warehouse in warehouses:
            # Calculate total value (simplified - in real implementation, you'd calculate based on inventory levels and costs)
            total_value = 0.0  # This would be calculated from actual inventory levels
            
            result.append({
                'warehouse_id': warehouse.id,
                'warehouse_name': warehouse.name,
                'location': warehouse.location,
                'total_value': total_value,
                'currency': 'USD',
                'last_updated': datetime.utcnow().isoformat()
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching warehouse valuation: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch warehouse valuation',
            'details': str(e)
        }), 500

@warehouse_bp.route('/list', methods=['GET'])
@api_endpoint_limit()
@require_tenant
def get_warehouses():
    """Get all warehouses for the current tenant"""
    try:
        tenant_context = get_tenant_context()
        
        warehouses = db.session.query(Warehouse).filter(
            Warehouse.tenant_id == tenant_context.tenant_id
        ).all()
        
        result = []
        for warehouse in warehouses:
            result.append({
                'id': warehouse.id,
                'name': warehouse.name,
                'location': warehouse.location,
                'is_active': warehouse.is_active,
                'created_at': warehouse.created_at.isoformat() if warehouse.created_at else None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching warehouses: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch warehouses',
            'details': str(e)
        }), 500
