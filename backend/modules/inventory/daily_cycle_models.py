"""
Daily Inventory Cycle Models
Date: September 18, 2025
Purpose: Daily opening/closing inventory cycles like finance module
"""

from app import db
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from sqlalchemy.dialects.postgresql import JSON
import json

class DailyInventoryBalance(db.Model):
    """
    Daily inventory balances - opening and closing quantities for each product/location
    Similar to DailyBalance in finance module
    """
    __tablename__ = 'daily_inventory_balances'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_date = db.Column(db.Date, nullable=False, index=True)
    
    # Product identification
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    
    # Location identification (multi-tier support)
    simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    basic_location_id = db.Column(db.Integer, db.ForeignKey('inventory_basic_locations.id'))
    advanced_location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    
    # Lot/Serial tracking
    lot_batch_id = db.Column(db.Integer, db.ForeignKey('inventory_lot_batches.id'))
    
    # Opening balances (start of day)
    opening_quantity = db.Column(db.Float, default=0.0)
    opening_unit_cost = db.Column(db.Float, default=0.0)
    opening_total_value = db.Column(db.Float, default=0.0)
    
    # Closing balances (end of day)
    closing_quantity = db.Column(db.Float, default=0.0)
    closing_unit_cost = db.Column(db.Float, default=0.0)
    closing_total_value = db.Column(db.Float, default=0.0)
    
    # Daily movements
    quantity_received = db.Column(db.Float, default=0.0)
    quantity_issued = db.Column(db.Float, default=0.0)
    quantity_transferred_in = db.Column(db.Float, default=0.0)
    quantity_transferred_out = db.Column(db.Float, default=0.0)
    quantity_adjusted = db.Column(db.Float, default=0.0)
    
    # Value movements
    value_received = db.Column(db.Float, default=0.0)
    value_issued = db.Column(db.Float, default=0.0)
    value_transferred_in = db.Column(db.Float, default=0.0)
    value_transferred_out = db.Column(db.Float, default=0.0)
    value_adjusted = db.Column(db.Float, default=0.0)
    
    # Net changes
    net_quantity_change = db.Column(db.Float, default=0.0)
    net_value_change = db.Column(db.Float, default=0.0)
    
    # Cost method used
    cost_method = db.Column(db.String(20), default='FIFO')  # FIFO, LIFO, Average, Standard
    
    # Currency support
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    base_currency_opening_value = db.Column(db.Float, default=0.0)
    base_currency_closing_value = db.Column(db.Float, default=0.0)
    
    # Status and locking (like finance module)
    is_locked = db.Column(db.Boolean, default=False)
    locked_at = db.Column(db.DateTime)
    locked_by = db.Column(db.String(100))
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='daily_balances')
    variant = db.relationship('ProductVariant', backref='daily_balances')
    simple_warehouse = db.relationship('SimpleWarehouse', backref='daily_balances')
    
    # Composite index for performance
    __table_args__ = (
        db.Index('idx_daily_inv_bal_date_product', 'cycle_date', 'product_id'),
        db.Index('idx_daily_inv_bal_date_location', 'cycle_date', 'simple_warehouse_id'),
    )

class DailyInventoryCycleStatus(db.Model):
    """
    Daily inventory cycle status tracking
    Similar to DailyCycleStatus in finance module
    """
    __tablename__ = 'daily_inventory_cycle_status'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_date = db.Column(db.Date, nullable=False, unique=True, index=True)
    
    # Opening cycle status
    opening_status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, error
    opening_started_at = db.Column(db.DateTime)
    opening_completed_at = db.Column(db.DateTime)
    opening_started_by = db.Column(db.String(100))
    opening_records_count = db.Column(db.Integer, default=0)
    
    # Closing cycle status  
    closing_status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, error
    closing_started_at = db.Column(db.DateTime)
    closing_completed_at = db.Column(db.DateTime)
    closing_started_by = db.Column(db.String(100))
    closing_records_count = db.Column(db.Integer, default=0)
    
    # Summary data
    total_products_processed = db.Column(db.Integer, default=0)
    total_locations_processed = db.Column(db.Integer, default=0)
    total_inventory_value = db.Column(db.Float, default=0.0)
    total_quantity_on_hand = db.Column(db.Float, default=0.0)
    
    # Error handling
    error_message = db.Column(db.Text)
    error_count = db.Column(db.Integer, default=0)
    
    # Grace period and locking
    grace_period_end = db.Column(db.DateTime)
    is_locked = db.Column(db.Boolean, default=False)
    locked_at = db.Column(db.DateTime)
    locked_by = db.Column(db.String(100))
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_pending_cycles(cls, limit: int = 10):
        """Get pending inventory cycles that need processing"""
        return cls.query.filter(
            or_(
                cls.opening_status == 'pending',
                and_(cls.opening_status == 'completed', cls.closing_status == 'pending')
            )
        ).order_by(cls.cycle_date.asc()).limit(limit).all()
    
    @classmethod
    def get_cycle_status(cls, cycle_date: date):
        """Get status for a specific cycle date"""
        return cls.query.filter_by(cycle_date=cycle_date).first()
    
    def is_complete(self) -> bool:
        """Check if both opening and closing cycles are complete"""
        return (self.opening_status == 'completed' and 
                self.closing_status == 'completed')

class DailyInventoryTransactionSummary(db.Model):
    """
    Daily inventory transaction summary by product and location
    Similar to DailyTransactionSummary in finance module
    """
    __tablename__ = 'daily_inventory_transaction_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    summary_date = db.Column(db.Date, nullable=False, index=True)
    
    # Product identification
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    
    # Location identification
    simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    basic_location_id = db.Column(db.Integer, db.ForeignKey('inventory_basic_locations.id'))
    advanced_location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    
    # Transaction counts by type
    receipts_count = db.Column(db.Integer, default=0)
    issues_count = db.Column(db.Integer, default=0)
    transfers_in_count = db.Column(db.Integer, default=0)
    transfers_out_count = db.Column(db.Integer, default=0)
    adjustments_count = db.Column(db.Integer, default=0)
    cycle_counts_count = db.Column(db.Integer, default=0)
    
    # Quantity summaries by type
    receipts_quantity = db.Column(db.Float, default=0.0)
    issues_quantity = db.Column(db.Float, default=0.0)
    transfers_in_quantity = db.Column(db.Float, default=0.0)
    transfers_out_quantity = db.Column(db.Float, default=0.0)
    adjustments_quantity = db.Column(db.Float, default=0.0)
    cycle_counts_quantity = db.Column(db.Float, default=0.0)
    
    # Value summaries by type
    receipts_value = db.Column(db.Float, default=0.0)
    issues_value = db.Column(db.Float, default=0.0)
    transfers_in_value = db.Column(db.Float, default=0.0)
    transfers_out_value = db.Column(db.Float, default=0.0)
    adjustments_value = db.Column(db.Float, default=0.0)
    cycle_counts_value = db.Column(db.Float, default=0.0)
    
    # Net totals
    total_transactions = db.Column(db.Integer, default=0)
    net_quantity_change = db.Column(db.Float, default=0.0)
    net_value_change = db.Column(db.Float, default=0.0)
    
    # Cost analysis
    average_unit_cost = db.Column(db.Float, default=0.0)
    cost_method = db.Column(db.String(20), default='FIFO')
    
    # Currency
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='daily_summaries')
    variant = db.relationship('ProductVariant', backref='daily_summaries')
    simple_warehouse = db.relationship('SimpleWarehouse', backref='daily_summaries')
    
    # Composite index
    __table_args__ = (
        db.Index('idx_daily_inv_summary_date_product', 'summary_date', 'product_id'),
        db.Index('idx_daily_inv_summary_date_location', 'summary_date', 'simple_warehouse_id'),
    )
    
    @classmethod
    def get_summary_for_date_range(cls, start_date: date, end_date: date, 
                                  product_id: int = None, location_id: int = None):
        """Get transaction summaries for a date range"""
        query = cls.query.filter(
            cls.summary_date >= start_date,
            cls.summary_date <= end_date
        )
        
        if product_id:
            query = query.filter(cls.product_id == product_id)
        if location_id:
            query = query.filter(cls.simple_warehouse_id == location_id)
        
        return query.order_by(cls.summary_date.desc()).all()

class InventoryAdjustmentEntry(db.Model):
    """
    Inventory adjustments made during daily cycles
    Similar to AdjustmentEntry in finance module
    """
    __tablename__ = 'inventory_adjustment_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_date = db.Column(db.Date, nullable=False, index=True)
    
    # Product and location
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    lot_batch_id = db.Column(db.Integer, db.ForeignKey('inventory_lot_batches.id'))
    
    # Adjustment details
    adjustment_type = db.Column(db.String(50), nullable=False)  # cycle_count, shrinkage, damage, revaluation
    reason_code = db.Column(db.String(20))  # SHRINK, DAMAGE, COUNT, REVALUE, OTHER
    
    # Quantities
    system_quantity = db.Column(db.Float, nullable=False)
    physical_quantity = db.Column(db.Float, nullable=False)
    adjustment_quantity = db.Column(db.Float, nullable=False)  # physical - system
    
    # Values
    system_unit_cost = db.Column(db.Float, default=0.0)
    adjusted_unit_cost = db.Column(db.Float, default=0.0)
    adjustment_value = db.Column(db.Float, default=0.0)
    
    # Approval workflow
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    requires_approval = db.Column(db.Boolean, default=True)
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    approval_threshold_exceeded = db.Column(db.Boolean, default=False)
    
    # Documentation
    notes = db.Column(db.Text)
    reference_document = db.Column(db.String(100))
    supporting_documents = db.Column(JSON)  # JSON array of document references
    
    # Audit trail
    user_id = db.Column(db.Integer)  # Standardized user identification, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # GL integration
    journal_entry_id = db.Column(db.String(50))  # Reference to GL journal entry
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='adjustments')
    simple_warehouse = db.relationship('SimpleWarehouse', backref='adjustments')

class DailyInventoryCycleAuditLog(db.Model):
    """
    Audit log for daily inventory cycle operations
    Similar to DailyCycleAuditLog in finance module
    """
    __tablename__ = 'daily_inventory_cycle_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_date = db.Column(db.Date, nullable=False, index=True)
    
    # Operation details
    operation = db.Column(db.String(50), nullable=False)  # opening_capture, closing_calculation, adjustment
    operation_status = db.Column(db.String(20), nullable=False)  # started, completed, error
    
    # User context
    user_id = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100))
    user_role = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    
    # Operation data
    records_processed = db.Column(db.Integer, default=0)
    records_created = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    errors_encountered = db.Column(db.Integer, default=0)
    
    # Performance metrics
    processing_time_seconds = db.Column(db.Float, default=0.0)
    memory_usage_mb = db.Column(db.Float, default=0.0)
    
    # Details and errors
    operation_details = db.Column(JSON)  # Structured operation data
    error_details = db.Column(JSON)  # Error information if any
    
    # Timestamps
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def log_operation(cls, cycle_date: date, operation: str, user_id: str, 
                     operation_status: str = 'started', **kwargs):
        """Create an audit log entry for an inventory cycle operation"""
        log_entry = cls(
            cycle_date=cycle_date,
            operation=operation,
            operation_status=operation_status,
            user_id=user_id,
            user_name=kwargs.get('user_name'),
            user_role=kwargs.get('user_role'),
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            records_processed=kwargs.get('records_processed', 0),
            records_created=kwargs.get('records_created', 0),
            records_updated=kwargs.get('records_updated', 0),
            errors_encountered=kwargs.get('errors_encountered', 0),
            processing_time_seconds=kwargs.get('processing_time_seconds', 0.0),
            operation_details=kwargs.get('operation_details'),
            error_details=kwargs.get('error_details'),
            started_at=kwargs.get('started_at', datetime.utcnow()),
            completed_at=kwargs.get('completed_at')
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry

