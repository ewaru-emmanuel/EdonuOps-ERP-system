"""
Inventory Costing Service - FIFO/LIFO/Average Cost Management
Date: September 18, 2025
Purpose: Precise cost layer management for enterprise inventory costing
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

try:
    from app import db
    from modules.inventory.cost_layer_models import (
        InventoryCostLayer, CostLayerTransaction, InventoryValuationSnapshot
    )
    from modules.inventory.advanced_models import InventoryProduct, StockLevel
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class InventoryCostingService:
    """
    Enterprise-grade inventory costing service
    Handles FIFO, LIFO, Average, and Standard cost methods with precision
    """
    
    def __init__(self):
        self.cost_method_handlers = {
            'FIFO': self._process_fifo_issue,
            'LIFO': self._process_lifo_issue,
            'AVERAGE': self._process_average_issue,
            'STANDARD': self._process_standard_issue
        }
    
    def create_cost_layer_on_receipt(self, receipt_data: Dict) -> Dict:
        """
        Create new cost layer when inventory is received
        """
        if not DB_AVAILABLE:
            return {'error': 'Database not available'}
        
        try:
            product_id = receipt_data['product_id']
            quantity = receipt_data['quantity']
            unit_cost = receipt_data['unit_cost']
            warehouse_id = receipt_data.get('warehouse_id')
            
            # Get next layer sequence for this product/location
            max_sequence = db.session.query(func.max(InventoryCostLayer.layer_sequence)).filter(
                InventoryCostLayer.product_id == product_id,
                InventoryCostLayer.simple_warehouse_id == warehouse_id
            ).scalar() or 0
            
            # Create new cost layer
            cost_layer = InventoryCostLayer(
                product_id=product_id,
                variant_id=receipt_data.get('variant_id'),
                simple_warehouse_id=warehouse_id,
                lot_batch_id=receipt_data.get('lot_batch_id'),
                layer_sequence=max_sequence + 1,
                receipt_date=receipt_data.get('receipt_date', date.today()),
                receipt_reference=receipt_data.get('reference', ''),
                unit_cost=unit_cost,
                original_quantity=quantity,
                remaining_quantity=quantity,
                total_cost=quantity * unit_cost,
                remaining_cost=quantity * unit_cost,
                currency=receipt_data.get('currency', 'USD'),
                exchange_rate=receipt_data.get('exchange_rate', 1.0),
                base_currency_unit_cost=unit_cost * receipt_data.get('exchange_rate', 1.0),
                base_currency_total_cost=(quantity * unit_cost) * receipt_data.get('exchange_rate', 1.0),
                source_transaction_id=receipt_data.get('transaction_id'),
                source_document_type=receipt_data.get('document_type', 'Receipt'),
                created_by=receipt_data.get('user_id', 'system')
            )
            
            db.session.add(cost_layer)
            db.session.commit()
            
            logger.info(f"Created cost layer {cost_layer.id} for product {product_id}: {quantity} units @ ${unit_cost}")
            
            return {
                'success': True,
                'cost_layer_id': cost_layer.id,
                'layer_sequence': cost_layer.layer_sequence,
                'unit_cost': unit_cost,
                'total_cost': cost_layer.total_cost,
                'message': f'Cost layer created for {quantity} units @ ${unit_cost}'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating cost layer: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_inventory_issue(self, issue_data: Dict) -> Dict:
        """
        Process inventory issue using appropriate cost method (FIFO/LIFO/Average)
        Returns cost information for GL posting
        """
        if not DB_AVAILABLE:
            return {'error': 'Database not available'}
        
        try:
            product_id = issue_data['product_id']
            quantity_to_issue = issue_data['quantity']
            warehouse_id = issue_data.get('warehouse_id')
            cost_method = issue_data.get('cost_method', 'FIFO')
            
            # Get cost method handler
            handler = self.cost_method_handlers.get(cost_method.upper(), self._process_fifo_issue)
            
            # Process issue using appropriate method
            costing_result = handler(product_id, quantity_to_issue, warehouse_id, issue_data)
            
            # Create depletion transaction records
            for layer_depletion in costing_result.get('layer_depletions', []):
                depletion_txn = CostLayerTransaction(
                    cost_layer_id=layer_depletion['layer_id'],
                    transaction_date=issue_data.get('issue_date', date.today()),
                    transaction_type='issue',
                    transaction_reference=issue_data.get('reference', ''),
                    quantity_depleted=layer_depletion['quantity_depleted'],
                    cost_depleted=layer_depletion['cost_depleted'],
                    unit_cost_used=layer_depletion['unit_cost'],
                    journal_entry_id=issue_data.get('journal_entry_id'),
                    created_by=issue_data.get('user_id', 'system')
                )
                db.session.add(depletion_txn)
            
            db.session.commit()
            
            return costing_result
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing inventory issue: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_fifo_issue(self, product_id: int, quantity: float, 
                           warehouse_id: int, issue_data: Dict) -> Dict:
        """Process issue using FIFO (First In, First Out) method"""
        
        # Get oldest layers first
        available_layers = InventoryCostLayer.get_available_layers(
            product_id=product_id,
            warehouse_id=warehouse_id,
            cost_method='FIFO',
            limit_quantity=quantity
        )
        
        if not available_layers:
            return {
                'success': False,
                'error': 'No cost layers available for FIFO issue',
                'available_quantity': 0
            }
        
        layer_depletions = []
        total_cost = 0
        remaining_to_issue = quantity
        
        for layer in available_layers:
            if remaining_to_issue <= 0:
                break
            
            # Deplete from this layer
            depletion_result = layer.deplete_layer(remaining_to_issue)
            
            layer_depletions.append({
                'layer_id': layer.id,
                'layer_sequence': layer.layer_sequence,
                'receipt_date': layer.receipt_date.isoformat(),
                'quantity_depleted': depletion_result['depleted_quantity'],
                'cost_depleted': depletion_result['depleted_cost'],
                'unit_cost': depletion_result['unit_cost'],
                'remaining_in_layer': depletion_result['remaining_in_layer']
            })
            
            total_cost += depletion_result['depleted_cost']
            remaining_to_issue -= depletion_result['depleted_quantity']
        
        # Calculate weighted average cost
        actual_quantity_issued = quantity - remaining_to_issue
        weighted_average_cost = total_cost / actual_quantity_issued if actual_quantity_issued > 0 else 0
        
        return {
            'success': True,
            'cost_method': 'FIFO',
            'quantity_issued': actual_quantity_issued,
            'total_cost': total_cost,
            'weighted_average_cost': weighted_average_cost,
            'layer_depletions': layer_depletions,
            'remaining_shortage': remaining_to_issue
        }
    
    def _process_lifo_issue(self, product_id: int, quantity: float, 
                           warehouse_id: int, issue_data: Dict) -> Dict:
        """Process issue using LIFO (Last In, First Out) method"""
        
        # Get newest layers first
        available_layers = InventoryCostLayer.get_available_layers(
            product_id=product_id,
            warehouse_id=warehouse_id,
            cost_method='LIFO',
            limit_quantity=quantity
        )
        
        if not available_layers:
            return {
                'success': False,
                'error': 'No cost layers available for LIFO issue',
                'available_quantity': 0
            }
        
        layer_depletions = []
        total_cost = 0
        remaining_to_issue = quantity
        
        for layer in available_layers:
            if remaining_to_issue <= 0:
                break
            
            # Deplete from this layer
            depletion_result = layer.deplete_layer(remaining_to_issue)
            
            layer_depletions.append({
                'layer_id': layer.id,
                'layer_sequence': layer.layer_sequence,
                'receipt_date': layer.receipt_date.isoformat(),
                'quantity_depleted': depletion_result['depleted_quantity'],
                'cost_depleted': depletion_result['depleted_cost'],
                'unit_cost': depletion_result['unit_cost'],
                'remaining_in_layer': depletion_result['remaining_in_layer']
            })
            
            total_cost += depletion_result['depleted_cost']
            remaining_to_issue -= depletion_result['depleted_quantity']
        
        # Calculate weighted average cost
        actual_quantity_issued = quantity - remaining_to_issue
        weighted_average_cost = total_cost / actual_quantity_issued if actual_quantity_issued > 0 else 0
        
        return {
            'success': True,
            'cost_method': 'LIFO',
            'quantity_issued': actual_quantity_issued,
            'total_cost': total_cost,
            'weighted_average_cost': weighted_average_cost,
            'layer_depletions': layer_depletions,
            'remaining_shortage': remaining_to_issue
        }
    
    def _process_average_issue(self, product_id: int, quantity: float, 
                              warehouse_id: int, issue_data: Dict) -> Dict:
        """Process issue using Moving Average method"""
        
        # Get all available layers to calculate average
        available_layers = InventoryCostLayer.get_available_layers(
            product_id=product_id,
            warehouse_id=warehouse_id,
            cost_method='AVERAGE'
        )
        
        if not available_layers:
            return {
                'success': False,
                'error': 'No cost layers available for Average issue',
                'available_quantity': 0
            }
        
        # Calculate weighted average cost
        total_quantity_available = sum(layer.remaining_quantity for layer in available_layers)
        total_cost_available = sum(layer.remaining_cost for layer in available_layers)
        
        if total_quantity_available <= 0:
            return {
                'success': False,
                'error': 'No quantity available for Average issue',
                'available_quantity': 0
            }
        
        average_unit_cost = total_cost_available / total_quantity_available
        
        # Issue quantity at average cost, depleting layers proportionally
        actual_quantity_issued = min(quantity, total_quantity_available)
        total_cost = actual_quantity_issued * average_unit_cost
        
        layer_depletions = []
        remaining_to_issue = actual_quantity_issued
        
        for layer in available_layers:
            if remaining_to_issue <= 0:
                break
            
            # Calculate proportional depletion
            layer_proportion = layer.remaining_quantity / total_quantity_available
            layer_depletion_qty = min(remaining_to_issue, layer.remaining_quantity, 
                                    actual_quantity_issued * layer_proportion)
            
            if layer_depletion_qty > 0:
                depletion_result = layer.deplete_layer(layer_depletion_qty)
                
                layer_depletions.append({
                    'layer_id': layer.id,
                    'layer_sequence': layer.layer_sequence,
                    'receipt_date': layer.receipt_date.isoformat(),
                    'quantity_depleted': depletion_result['depleted_quantity'],
                    'cost_depleted': depletion_result['depleted_quantity'] * average_unit_cost,  # Use average cost
                    'unit_cost': average_unit_cost,
                    'original_layer_cost': depletion_result['unit_cost'],
                    'remaining_in_layer': depletion_result['remaining_in_layer']
                })
                
                remaining_to_issue -= depletion_result['depleted_quantity']
        
        return {
            'success': True,
            'cost_method': 'AVERAGE',
            'quantity_issued': actual_quantity_issued,
            'total_cost': total_cost,
            'weighted_average_cost': average_unit_cost,
            'layer_depletions': layer_depletions,
            'remaining_shortage': quantity - actual_quantity_issued
        }
    
    def _process_standard_issue(self, product_id: int, quantity: float, 
                               warehouse_id: int, issue_data: Dict) -> Dict:
        """Process issue using Standard Cost method"""
        
        try:
            # Get product standard cost
            product = InventoryProduct.query.get(product_id)
            if not product:
                return {
                    'success': False,
                    'error': f'Product {product_id} not found'
                }
            
            standard_cost = product.standard_cost or 0.0
            total_cost = quantity * standard_cost
            
            # For standard costing, we still need to deplete layers but use standard cost
            available_layers = InventoryCostLayer.get_available_layers(
                product_id=product_id,
                warehouse_id=warehouse_id,
                cost_method='FIFO',  # Use FIFO for layer depletion
                limit_quantity=quantity
            )
            
            layer_depletions = []
            remaining_to_issue = quantity
            
            for layer in available_layers:
                if remaining_to_issue <= 0:
                    break
                
                depletion_result = layer.deplete_layer(remaining_to_issue)
                
                layer_depletions.append({
                    'layer_id': layer.id,
                    'layer_sequence': layer.layer_sequence,
                    'receipt_date': layer.receipt_date.isoformat(),
                    'quantity_depleted': depletion_result['depleted_quantity'],
                    'cost_depleted': depletion_result['depleted_quantity'] * standard_cost,  # Use standard cost
                    'unit_cost': standard_cost,
                    'actual_layer_cost': depletion_result['unit_cost'],
                    'cost_variance': (standard_cost - depletion_result['unit_cost']) * depletion_result['depleted_quantity'],
                    'remaining_in_layer': depletion_result['remaining_in_layer']
                })
                
                remaining_to_issue -= depletion_result['depleted_quantity']
            
            return {
                'success': True,
                'cost_method': 'STANDARD',
                'quantity_issued': quantity - remaining_to_issue,
                'total_cost': total_cost,
                'standard_unit_cost': standard_cost,
                'layer_depletions': layer_depletions,
                'remaining_shortage': remaining_to_issue,
                'total_cost_variance': sum(ld.get('cost_variance', 0) for ld in layer_depletions)
            }
            
        except Exception as e:
            logger.error(f"Error processing standard cost issue: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_valuation_snapshot(self, snapshot_date: date = None) -> Dict:
        """
        Create inventory valuation snapshot for all products using all cost methods
        """
        if not DB_AVAILABLE:
            return {'error': 'Database not available'}
        
        if not snapshot_date:
            snapshot_date = date.today()
        
        try:
            # Get all products with cost layers
            products_with_layers = db.session.query(InventoryCostLayer.product_id).filter(
                InventoryCostLayer.remaining_quantity > 0
            ).distinct().all()
            
            snapshots_created = 0
            total_fifo_value = 0
            total_lifo_value = 0
            total_avg_value = 0
            
            for (product_id,) in products_with_layers:
                # Calculate valuation using each method
                fifo_valuation = self._calculate_fifo_valuation(product_id, snapshot_date)
                lifo_valuation = self._calculate_lifo_valuation(product_id, snapshot_date)
                avg_valuation = self._calculate_average_valuation(product_id, snapshot_date)
                
                # Get product info
                product = InventoryProduct.query.get(product_id)
                active_cost_method = product.cost_method if product else 'FIFO'
                
                # Determine active valuation
                if active_cost_method.upper() == 'FIFO':
                    active_valuation = fifo_valuation
                elif active_cost_method.upper() == 'LIFO':
                    active_valuation = lifo_valuation
                else:
                    active_valuation = avg_valuation
                
                # Create snapshot
                snapshot = InventoryValuationSnapshot(
                    snapshot_date=snapshot_date,
                    product_id=product_id,
                    
                    # FIFO valuation
                    fifo_quantity=fifo_valuation['quantity'],
                    fifo_unit_cost=fifo_valuation['unit_cost'],
                    fifo_total_value=fifo_valuation['total_value'],
                    
                    # LIFO valuation
                    lifo_quantity=lifo_valuation['quantity'],
                    lifo_unit_cost=lifo_valuation['unit_cost'],
                    lifo_total_value=lifo_valuation['total_value'],
                    
                    # Average valuation
                    average_quantity=avg_valuation['quantity'],
                    average_unit_cost=avg_valuation['unit_cost'],
                    average_total_value=avg_valuation['total_value'],
                    
                    # Standard cost (if available)
                    standard_quantity=active_valuation['quantity'],
                    standard_unit_cost=product.standard_cost if product else 0,
                    standard_total_value=(active_valuation['quantity'] * product.standard_cost) if product else 0,
                    
                    # Active method
                    active_cost_method=active_cost_method,
                    active_quantity=active_valuation['quantity'],
                    active_unit_cost=active_valuation['unit_cost'],
                    active_total_value=active_valuation['total_value'],
                    
                    # Variance analysis
                    method_variance_fifo_vs_avg=fifo_valuation['total_value'] - avg_valuation['total_value'],
                    method_variance_lifo_vs_avg=lifo_valuation['total_value'] - avg_valuation['total_value'],
                    method_variance_std_vs_actual=((product.standard_cost * active_valuation['quantity']) - active_valuation['total_value']) if product else 0,
                    
                    # Aging (simplified)
                    days_on_hand=self._calculate_days_on_hand(product_id),
                    aging_category=self._determine_aging_category(product_id)
                )
                
                db.session.add(snapshot)
                snapshots_created += 1
                
                total_fifo_value += fifo_valuation['total_value']
                total_lifo_value += lifo_valuation['total_value']
                total_avg_value += avg_valuation['total_value']
            
            db.session.commit()
            
            return {
                'success': True,
                'snapshot_date': snapshot_date.isoformat(),
                'snapshots_created': snapshots_created,
                'valuation_summary': {
                    'total_fifo_value': total_fifo_value,
                    'total_lifo_value': total_lifo_value,
                    'total_average_value': total_avg_value,
                    'fifo_vs_lifo_variance': total_fifo_value - total_lifo_value,
                    'fifo_vs_avg_variance': total_fifo_value - total_avg_value
                }
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating valuation snapshot: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_fifo_valuation(self, product_id: int, as_of_date: date) -> Dict:
        """Calculate FIFO valuation for a product"""
        layers = InventoryCostLayer.query.filter(
            InventoryCostLayer.product_id == product_id,
            InventoryCostLayer.remaining_quantity > 0,
            InventoryCostLayer.receipt_date <= as_of_date
        ).order_by(InventoryCostLayer.receipt_date.asc()).all()
        
        total_quantity = sum(layer.remaining_quantity for layer in layers)
        total_value = sum(layer.remaining_cost for layer in layers)
        unit_cost = total_value / total_quantity if total_quantity > 0 else 0
        
        return {
            'quantity': total_quantity,
            'total_value': total_value,
            'unit_cost': unit_cost
        }
    
    def _calculate_lifo_valuation(self, product_id: int, as_of_date: date) -> Dict:
        """Calculate LIFO valuation for a product"""
        # Same as FIFO for valuation purposes (layers are the same, just issue order differs)
        return self._calculate_fifo_valuation(product_id, as_of_date)
    
    def _calculate_average_valuation(self, product_id: int, as_of_date: date) -> Dict:
        """Calculate Moving Average valuation for a product"""
        layers = InventoryCostLayer.query.filter(
            InventoryCostLayer.product_id == product_id,
            InventoryCostLayer.remaining_quantity > 0,
            InventoryCostLayer.receipt_date <= as_of_date
        ).all()
        
        total_quantity = sum(layer.remaining_quantity for layer in layers)
        total_value = sum(layer.remaining_cost for layer in layers)
        
        # Moving average calculation
        if total_quantity > 0:
            average_unit_cost = total_value / total_quantity
        else:
            average_unit_cost = 0
        
        return {
            'quantity': total_quantity,
            'total_value': total_value,
            'unit_cost': average_unit_cost
        }
    
    def _calculate_days_on_hand(self, product_id: int) -> int:
        """Calculate average days inventory has been on hand"""
        # Simplified calculation - in full implementation would use transaction history
        return 30  # Placeholder
    
    def _determine_aging_category(self, product_id: int) -> str:
        """Determine aging category for inventory"""
        days = self._calculate_days_on_hand(product_id)
        
        if days <= 30:
            return 'fast_moving'
        elif days <= 90:
            return 'slow_moving'
        else:
            return 'dead_stock'

# Convenience functions
def create_cost_layer(receipt_data: Dict) -> Dict:
    """Create cost layer for inventory receipt"""
    service = InventoryCostingService()
    return service.create_cost_layer_on_receipt(receipt_data)

def process_issue_with_costing(issue_data: Dict) -> Dict:
    """Process inventory issue with precise costing"""
    service = InventoryCostingService()
    return service.process_inventory_issue(issue_data)

def generate_valuation_snapshot(snapshot_date: date = None) -> Dict:
    """Generate inventory valuation snapshot"""
    service = InventoryCostingService()
    return service.create_valuation_snapshot(snapshot_date)

