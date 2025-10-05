"""
Cost Layer Models for FIFO/LIFO Inventory Costing
Date: September 18, 2025
Purpose: Precise cost tracking with layer-based costing methods
"""

from app import db
from datetime import datetime, date
from typing import Dict, List, Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.dialects.postgresql import JSON
import json

class InventoryCostLayer(db.Model):
    """
    Cost layers for precise FIFO/LIFO/Average cost tracking
    Each receipt creates a new cost layer, issues deplete from appropriate layers
    """
    __tablename__ = 'inventory_cost_layers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Product and location identification
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    lot_batch_id = db.Column(db.Integer, db.ForeignKey('inventory_lot_batches.id'))
    
    # Layer identification
    layer_sequence = db.Column(db.Integer, nullable=False)  # Sequential layer number
    receipt_date = db.Column(db.Date, nullable=False)
    receipt_reference = db.Column(db.String(100))  # PO number, transfer reference, etc.
    
    # Cost information
    unit_cost = db.Column(db.Float, nullable=False)
    original_quantity = db.Column(db.Float, nullable=False)
    remaining_quantity = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    remaining_cost = db.Column(db.Float, nullable=False)
    
    # Currency support
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    base_currency_unit_cost = db.Column(db.Float, nullable=False)
    base_currency_total_cost = db.Column(db.Float, nullable=False)
    
    # Layer status
    is_depleted = db.Column(db.Boolean, default=False)
    depleted_date = db.Column(db.Date)
    
    # Source tracking
    source_transaction_id = db.Column(db.Integer)  # Link to original receipt transaction
    source_document_type = db.Column(db.String(50))  # PO, Transfer, Adjustment, etc.
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='cost_layers')
    variant = db.relationship('ProductVariant', backref='cost_layers')
    simple_warehouse = db.relationship('SimpleWarehouse', backref='cost_layers')
    
    # Composite index for performance
    __table_args__ = (
        db.Index('idx_cost_layers_product_date', 'product_id', 'receipt_date'),
        db.Index('idx_cost_layers_fifo', 'product_id', 'simple_warehouse_id', 'layer_sequence'),
        db.Index('idx_cost_layers_lifo', 'product_id', 'simple_warehouse_id', 'receipt_date', 'layer_sequence'),
    )
    
    @classmethod
    def get_available_layers(cls, product_id: int, warehouse_id: int = None, 
                           cost_method: str = 'FIFO', limit_quantity: float = None):
        """
        Get available cost layers for a product using specified method
        """
        query = cls.query.filter(
            cls.product_id == product_id,
            cls.remaining_quantity > 0,
            cls.is_depleted == False
        )
        
        if warehouse_id:
            query = query.filter(cls.simple_warehouse_id == warehouse_id)
        
        # Order by cost method
        if cost_method.upper() == 'FIFO':
            query = query.order_by(cls.receipt_date.asc(), cls.layer_sequence.asc())
        elif cost_method.upper() == 'LIFO':
            query = query.order_by(cls.receipt_date.desc(), cls.layer_sequence.desc())
        else:  # Average or other methods
            query = query.order_by(cls.receipt_date.asc(), cls.layer_sequence.asc())
        
        layers = query.all()
        
        # If limit_quantity specified, only return layers needed
        if limit_quantity:
            selected_layers = []
            remaining_needed = limit_quantity
            
            for layer in layers:
                if remaining_needed <= 0:
                    break
                    
                selected_layers.append(layer)
                remaining_needed -= layer.remaining_quantity
            
            return selected_layers
        
        return layers
    
    def deplete_layer(self, quantity_to_deplete: float) -> Dict:
        """
        Deplete quantity from this cost layer
        Returns cost information for GL posting
        """
        if quantity_to_deplete <= 0:
            return {'depleted_quantity': 0, 'depleted_cost': 0, 'unit_cost': self.unit_cost}
        
        # Calculate actual depletion (can't deplete more than available)
        actual_depletion = min(quantity_to_deplete, self.remaining_quantity)
        depleted_cost = actual_depletion * self.unit_cost
        
        # Update layer
        self.remaining_quantity -= actual_depletion
        self.remaining_cost -= depleted_cost
        
        # Mark as depleted if fully consumed
        if self.remaining_quantity <= 0.001:  # Allow for floating point precision
            self.is_depleted = True
            self.depleted_date = date.today()
            self.remaining_quantity = 0
            self.remaining_cost = 0
        
        return {
            'depleted_quantity': actual_depletion,
            'depleted_cost': depleted_cost,
            'unit_cost': self.unit_cost,
            'layer_id': self.id,
            'remaining_in_layer': self.remaining_quantity
        }

class CostLayerTransaction(db.Model):
    """
    Track cost layer depletion transactions for audit trail
    """
    __tablename__ = 'cost_layer_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Link to cost layer
    cost_layer_id = db.Column(db.Integer, db.ForeignKey('inventory_cost_layers.id'), nullable=False)
    
    # Transaction details
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # issue, adjustment, writeoff
    transaction_reference = db.Column(db.String(100))
    
    # Depletion details
    quantity_depleted = db.Column(db.Float, nullable=False)
    cost_depleted = db.Column(db.Float, nullable=False)
    unit_cost_used = db.Column(db.Float, nullable=False)
    
    # GL integration
    journal_entry_id = db.Column(db.String(50))  # Link to GL journal entry
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    cost_layer = db.relationship('InventoryCostLayer', backref='depletion_transactions')

class InventoryValuationSnapshot(db.Model):
    """
    Daily inventory valuation snapshots for historical reporting
    """
    __tablename__ = 'inventory_valuation_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    
    # Product identification
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    
    # Valuation by method
    fifo_quantity = db.Column(db.Float, default=0.0)
    fifo_unit_cost = db.Column(db.Float, default=0.0)
    fifo_total_value = db.Column(db.Float, default=0.0)
    
    lifo_quantity = db.Column(db.Float, default=0.0)
    lifo_unit_cost = db.Column(db.Float, default=0.0)
    lifo_total_value = db.Column(db.Float, default=0.0)
    
    average_quantity = db.Column(db.Float, default=0.0)
    average_unit_cost = db.Column(db.Float, default=0.0)
    average_total_value = db.Column(db.Float, default=0.0)
    
    standard_quantity = db.Column(db.Float, default=0.0)
    standard_unit_cost = db.Column(db.Float, default=0.0)
    standard_total_value = db.Column(db.Float, default=0.0)
    
    # Active method valuation (what's actually used)
    active_cost_method = db.Column(db.String(20), nullable=False)
    active_quantity = db.Column(db.Float, default=0.0)
    active_unit_cost = db.Column(db.Float, default=0.0)
    active_total_value = db.Column(db.Float, default=0.0)
    
    # Variance analysis
    method_variance_fifo_vs_avg = db.Column(db.Float, default=0.0)
    method_variance_lifo_vs_avg = db.Column(db.Float, default=0.0)
    method_variance_std_vs_actual = db.Column(db.Float, default=0.0)
    
    # Aging analysis
    days_on_hand = db.Column(db.Integer, default=0)
    aging_category = db.Column(db.String(20))  # fast_moving, slow_moving, dead_stock
    last_movement_date = db.Column(db.Date)
    
    # Currency
    currency = db.Column(db.String(3), default='USD')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='valuation_snapshots')
    
    # Composite index
    __table_args__ = (
        db.Index('idx_valuation_snapshot_date_product', 'snapshot_date', 'product_id'),
        db.Index('idx_valuation_snapshot_aging', 'aging_category', 'days_on_hand'),
    )
