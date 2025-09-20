"""
Daily Inventory Cycle Service
Date: September 18, 2025
Purpose: Daily opening/closing inventory cycles like finance module
"""

from __future__ import annotations
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_, text
import json
import time

from app import db
from modules.inventory.daily_cycle_models import (
    DailyInventoryBalance, DailyInventoryCycleStatus, DailyInventoryTransactionSummary,
    InventoryAdjustmentEntry, DailyInventoryCycleAuditLog
)
from modules.inventory.advanced_models import (
    InventoryProduct, StockLevel, InventoryTransaction, SimpleWarehouse
)

logger = logging.getLogger(__name__)

class DailyInventoryCycleService:
    """
    Daily inventory cycle service - handles opening/closing inventory balances
    Similar to DailyCycleService but for inventory management
    """
    
    def __init__(self, grace_period_hours: int = 2):
        self.grace_period_hours = grace_period_hours
    
    def capture_opening_inventory(self, cycle_date: date, user_id: str,
                                user_name: str = None, user_role: str = None) -> Dict:
        """
        Capture opening inventory balances for all products/locations
        Similar to capture_opening_balances in finance module
        """
        start_time = time.time()
        
        try:
            # Check if opening already captured
            cycle_status = DailyInventoryCycleStatus.get_cycle_status(cycle_date)
            if cycle_status and cycle_status.opening_status == 'completed':
                return {
                    "status": "success",
                    "message": f"Opening inventory already captured for {cycle_date}",
                    "cycle_date": cycle_date.isoformat(),
                    "records_processed": cycle_status.opening_records_count
                }
            
            # Create or update cycle status
            if not cycle_status:
                cycle_status = DailyInventoryCycleStatus(
                    cycle_date=cycle_date,
                    opening_status='in_progress',
                    opening_started_at=datetime.utcnow(),
                    opening_started_by=user_id
                )
                db.session.add(cycle_status)
            else:
                cycle_status.opening_status = 'in_progress'
                cycle_status.opening_started_at = datetime.utcnow()
                cycle_status.opening_started_by = user_id
            
            # Log operation start
            audit_log = DailyInventoryCycleAuditLog.log_operation(
                cycle_date=cycle_date,
                operation='opening_capture',
                user_id=user_id,
                operation_status='started',
                user_name=user_name,
                user_role=user_role,
                started_at=datetime.utcnow()
            )
            
            # Get previous day's closing balances (if any)
            previous_date = cycle_date - timedelta(days=1)
            previous_balances = {}
            
            previous_closing = DailyInventoryBalance.query.filter_by(
                cycle_date=previous_date
            ).all()
            
            for balance in previous_closing:
                key = self._get_balance_key(
                    balance.product_id, balance.variant_id,
                    balance.simple_warehouse_id, balance.lot_batch_id
                )
                previous_balances[key] = {
                    'quantity': balance.closing_quantity,
                    'unit_cost': balance.closing_unit_cost,
                    'total_value': balance.closing_total_value
                }
            
            # Get current stock levels for all products/locations
            current_stock = db.session.query(StockLevel).filter(
                StockLevel.quantity_on_hand > 0
            ).all()
            
            records_processed = 0
            records_created = 0
            
            for stock in current_stock:
                # Create daily inventory balance record
                balance_key = self._get_balance_key(
                    stock.product_id, stock.variant_id,
                    stock.simple_warehouse_id, stock.lot_batch_id
                )
                
                # Use previous closing as opening, or current stock if no previous
                if balance_key in previous_balances:
                    opening_qty = previous_balances[balance_key]['quantity']
                    opening_cost = previous_balances[balance_key]['unit_cost']
                    opening_value = previous_balances[balance_key]['total_value']
                else:
                    opening_qty = stock.quantity_on_hand
                    opening_cost = stock.unit_cost
                    opening_value = stock.total_value
                
                daily_balance = DailyInventoryBalance(
                    cycle_date=cycle_date,
                    product_id=stock.product_id,
                    variant_id=stock.variant_id,
                    simple_warehouse_id=stock.simple_warehouse_id,
                    lot_batch_id=stock.lot_batch_id,
                    opening_quantity=opening_qty,
                    opening_unit_cost=opening_cost,
                    opening_total_value=opening_value,
                    closing_quantity=opening_qty,  # Initialize closing with opening
                    closing_unit_cost=opening_cost,
                    closing_total_value=opening_value,
                    cost_method=stock.product.cost_method if stock.product else 'FIFO',
                    currency=stock.cost_currency or 'USD',
                    created_by=user_id
                )
                
                db.session.add(daily_balance)
                records_created += 1
                records_processed += 1
            
            # Update cycle status
            cycle_status.opening_status = 'completed'
            cycle_status.opening_completed_at = datetime.utcnow()
            cycle_status.opening_records_count = records_created
            cycle_status.total_products_processed = len(set(s.product_id for s in current_stock))
            cycle_status.total_locations_processed = len(set(s.simple_warehouse_id for s in current_stock if s.simple_warehouse_id))
            
            # Calculate total inventory value
            total_value = sum(balance.opening_total_value for balance in 
                            db.session.query(DailyInventoryBalance).filter_by(cycle_date=cycle_date).all())
            cycle_status.total_inventory_value = total_value
            
            # Calculate total quantity on hand
            total_quantity = sum(balance.opening_quantity for balance in 
                               db.session.query(DailyInventoryBalance).filter_by(cycle_date=cycle_date).all())
            cycle_status.total_quantity_on_hand = total_quantity
            
            db.session.commit()
            
            # Update audit log
            processing_time = time.time() - start_time
            audit_log.operation_status = 'completed'
            audit_log.completed_at = datetime.utcnow()
            audit_log.records_processed = records_processed
            audit_log.records_created = records_created
            audit_log.processing_time_seconds = processing_time
            db.session.commit()
            
            logger.info(f"Opening inventory captured for {cycle_date}: {records_created} records")
            
            return {
                "status": "success",
                "message": f"Opening inventory captured for {cycle_date}",
                "cycle_date": cycle_date.isoformat(),
                "records_processed": records_processed,
                "records_created": records_created,
                "total_inventory_value": total_value,
                "total_quantity_on_hand": total_quantity,
                "processing_time_seconds": processing_time
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to capture opening inventory for {cycle_date}: {str(e)}")
            
            # Update cycle status and audit log
            if cycle_status:
                cycle_status.opening_status = 'error'
                cycle_status.error_message = str(e)
                cycle_status.error_count += 1
            
            if 'audit_log' in locals():
                audit_log.operation_status = 'error'
                audit_log.completed_at = datetime.utcnow()
                audit_log.error_details = {"error": str(e)}
                audit_log.processing_time_seconds = time.time() - start_time
            
            db.session.commit()
            
            return {
                "status": "error",
                "message": f"Failed to capture opening inventory for {cycle_date}",
                "error": str(e),
                "cycle_date": cycle_date.isoformat()
            }
    
    def calculate_closing_inventory(self, cycle_date: date, user_id: str,
                                  user_name: str = None, user_role: str = None) -> Dict:
        """
        Calculate closing inventory balances based on daily transactions
        Similar to calculate_closing_balances in finance module
        """
        start_time = time.time()
        
        try:
            # Check prerequisites
            cycle_status = DailyInventoryCycleStatus.get_cycle_status(cycle_date)
            if not cycle_status or cycle_status.opening_status != 'completed':
                return {
                    "status": "error",
                    "message": f"Opening inventory must be captured first for {cycle_date}",
                    "cycle_date": cycle_date.isoformat()
                }
            
            if cycle_status.closing_status == 'completed':
                return {
                    "status": "success",
                    "message": f"Closing inventory already calculated for {cycle_date}",
                    "cycle_date": cycle_date.isoformat(),
                    "records_processed": cycle_status.closing_records_count
                }
            
            # Update status
            cycle_status.closing_status = 'in_progress'
            cycle_status.closing_started_at = datetime.utcnow()
            cycle_status.closing_started_by = user_id
            
            # Log operation
            audit_log = DailyInventoryCycleAuditLog.log_operation(
                cycle_date=cycle_date,
                operation='closing_calculation',
                user_id=user_id,
                operation_status='started',
                user_name=user_name,
                user_role=user_role,
                started_at=datetime.utcnow()
            )
            
            # Get all opening balances for the day
            opening_balances = DailyInventoryBalance.query.filter_by(
                cycle_date=cycle_date
            ).all()
            
            records_processed = 0
            records_updated = 0
            
            # Process each balance record
            for balance in opening_balances:
                # Get transactions for this product/location for the day
                transactions = self._get_daily_transactions(
                    cycle_date, balance.product_id, balance.variant_id,
                    balance.simple_warehouse_id, balance.lot_batch_id
                )
                
                # Calculate movements
                movements = self._calculate_movements(transactions, balance.cost_method)
                
                # Update balance record
                balance.quantity_received = movements['received_qty']
                balance.quantity_issued = movements['issued_qty']
                balance.quantity_transferred_in = movements['transfer_in_qty']
                balance.quantity_transferred_out = movements['transfer_out_qty']
                balance.quantity_adjusted = movements['adjusted_qty']
                
                balance.value_received = movements['received_value']
                balance.value_issued = movements['issued_value']
                balance.value_transferred_in = movements['transfer_in_value']
                balance.value_transferred_out = movements['transfer_out_value']
                balance.value_adjusted = movements['adjusted_value']
                
                # Calculate net changes
                balance.net_quantity_change = (
                    movements['received_qty'] + movements['transfer_in_qty'] + movements['adjusted_qty'] -
                    movements['issued_qty'] - movements['transfer_out_qty']
                )
                
                balance.net_value_change = (
                    movements['received_value'] + movements['transfer_in_value'] + movements['adjusted_value'] -
                    movements['issued_value'] - movements['transfer_out_value']
                )
                
                # Calculate closing balances
                balance.closing_quantity = balance.opening_quantity + balance.net_quantity_change
                
                if balance.closing_quantity > 0:
                    balance.closing_total_value = balance.opening_total_value + balance.net_value_change
                    balance.closing_unit_cost = balance.closing_total_value / balance.closing_quantity
                else:
                    balance.closing_total_value = 0.0
                    balance.closing_unit_cost = 0.0
                
                records_updated += 1
                records_processed += 1
            
            # Create transaction summaries
            self._create_transaction_summaries(cycle_date)
            
            # Update cycle status
            cycle_status.closing_status = 'completed'
            cycle_status.closing_completed_at = datetime.utcnow()
            cycle_status.closing_records_count = records_updated
            
            # Recalculate totals
            total_value = sum(balance.closing_total_value for balance in opening_balances)
            total_quantity = sum(balance.closing_quantity for balance in opening_balances)
            cycle_status.total_inventory_value = total_value
            cycle_status.total_quantity_on_hand = total_quantity
            
            db.session.commit()
            
            # Update audit log
            processing_time = time.time() - start_time
            audit_log.operation_status = 'completed'
            audit_log.completed_at = datetime.utcnow()
            audit_log.records_processed = records_processed
            audit_log.records_updated = records_updated
            audit_log.processing_time_seconds = processing_time
            db.session.commit()
            
            logger.info(f"Closing inventory calculated for {cycle_date}: {records_updated} records")
            
            return {
                "status": "success",
                "message": f"Closing inventory calculated for {cycle_date}",
                "cycle_date": cycle_date.isoformat(),
                "records_processed": records_processed,
                "records_updated": records_updated,
                "total_inventory_value": total_value,
                "total_quantity_on_hand": total_quantity,
                "processing_time_seconds": processing_time
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to calculate closing inventory for {cycle_date}: {str(e)}")
            
            # Update status and audit log
            if cycle_status:
                cycle_status.closing_status = 'error'
                cycle_status.error_message = str(e)
                cycle_status.error_count += 1
            
            if 'audit_log' in locals():
                audit_log.operation_status = 'error'
                audit_log.completed_at = datetime.utcnow()
                audit_log.error_details = {"error": str(e)}
                audit_log.processing_time_seconds = time.time() - start_time
            
            db.session.commit()
            
            return {
                "status": "error",
                "message": f"Failed to calculate closing inventory for {cycle_date}",
                "error": str(e),
                "cycle_date": cycle_date.isoformat()
            }
    
    def execute_full_inventory_cycle(self, cycle_date: date, user_id: str,
                                   user_name: str = None, user_role: str = None) -> Dict:
        """
        Execute complete daily inventory cycle: opening + closing
        Similar to execute_full_daily_cycle in finance module
        """
        try:
            # Step 1: Capture opening inventory
            opening_result = self.capture_opening_inventory(
                cycle_date, user_id, user_name, user_role
            )
            if opening_result["status"] == "error":
                return opening_result
            
            # Step 2: Calculate closing inventory
            closing_result = self.calculate_closing_inventory(
                cycle_date, user_id, user_name, user_role
            )
            if closing_result["status"] == "error":
                return closing_result
            
            return {
                "status": "success",
                "message": f"Complete inventory cycle executed for {cycle_date}",
                "cycle_date": cycle_date.isoformat(),
                "opening_result": opening_result,
                "closing_result": closing_result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute inventory cycle for {cycle_date}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute inventory cycle for {cycle_date}",
                "error": str(e),
                "cycle_date": cycle_date.isoformat()
            }
    
    def get_inventory_cycle_status(self, cycle_date: date) -> Dict:
        """Get status of inventory cycle for a specific date"""
        try:
            cycle_status = DailyInventoryCycleStatus.get_cycle_status(cycle_date)
            
            if not cycle_status:
                return {
                    "status": "not_found",
                    "message": f"No inventory cycle found for {cycle_date}",
                    "cycle_date": cycle_date.isoformat()
                }
            
            return {
                "status": "success",
                "cycle_date": cycle_date.isoformat(),
                "opening_status": cycle_status.opening_status,
                "closing_status": cycle_status.closing_status,
                "is_complete": cycle_status.is_complete(),
                "total_products": cycle_status.total_products_processed,
                "total_locations": cycle_status.total_locations_processed,
                "total_inventory_value": cycle_status.total_inventory_value,
                "total_quantity_on_hand": cycle_status.total_quantity_on_hand,
                "opening_records": cycle_status.opening_records_count,
                "closing_records": cycle_status.closing_records_count,
                "error_message": cycle_status.error_message,
                "is_locked": cycle_status.is_locked
            }
            
        except Exception as e:
            logger.error(f"Failed to get inventory cycle status for {cycle_date}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get inventory cycle status",
                "error": str(e),
                "cycle_date": cycle_date.isoformat()
            }
    
    def _get_balance_key(self, product_id: int, variant_id: int = None,
                        location_id: int = None, lot_id: int = None) -> str:
        """Generate unique key for inventory balance"""
        return f"{product_id}_{variant_id or 0}_{location_id or 0}_{lot_id or 0}"
    
    def _get_daily_transactions(self, cycle_date: date, product_id: int,
                              variant_id: int = None, location_id: int = None,
                              lot_id: int = None) -> List:
        """Get all transactions for a product/location on a specific date"""
        query = InventoryTransaction.query.filter(
            func.date(InventoryTransaction.transaction_date) == cycle_date,
            InventoryTransaction.product_id == product_id
        )
        
        if variant_id:
            query = query.filter(InventoryTransaction.variant_id == variant_id)
        if location_id:
            query = query.filter(
                or_(
                    InventoryTransaction.from_simple_warehouse_id == location_id,
                    InventoryTransaction.to_simple_warehouse_id == location_id
                )
            )
        if lot_id:
            query = query.filter(InventoryTransaction.lot_batch_id == lot_id)
        
        return query.all()
    
    def _calculate_movements(self, transactions: List, cost_method: str = 'FIFO') -> Dict:
        """Calculate quantity and value movements from transactions"""
        movements = {
            'received_qty': 0.0, 'received_value': 0.0,
            'issued_qty': 0.0, 'issued_value': 0.0,
            'transfer_in_qty': 0.0, 'transfer_in_value': 0.0,
            'transfer_out_qty': 0.0, 'transfer_out_value': 0.0,
            'adjusted_qty': 0.0, 'adjusted_value': 0.0
        }
        
        for txn in transactions:
            if txn.transaction_type == 'receive':
                movements['received_qty'] += txn.quantity
                movements['received_value'] += txn.total_cost
            elif txn.transaction_type == 'issue':
                movements['issued_qty'] += txn.quantity
                movements['issued_value'] += txn.total_cost
            elif txn.transaction_type == 'transfer':
                # Handle as transfer in or out based on location
                movements['transfer_in_qty'] += txn.quantity
                movements['transfer_in_value'] += txn.total_cost
            elif txn.transaction_type == 'adjustment':
                movements['adjusted_qty'] += txn.quantity  # Can be negative
                movements['adjusted_value'] += txn.total_cost
        
        return movements
    
    def _create_transaction_summaries(self, cycle_date: date):
        """Create daily transaction summaries"""
        # Get all transactions for the day
        transactions = InventoryTransaction.query.filter(
            func.date(InventoryTransaction.transaction_date) == cycle_date
        ).all()
        
        # Group by product and location
        summaries = {}
        
        for txn in transactions:
            key = f"{txn.product_id}_{txn.variant_id or 0}_{txn.from_simple_warehouse_id or 0}"
            
            if key not in summaries:
                summaries[key] = {
                    'product_id': txn.product_id,
                    'variant_id': txn.variant_id,
                    'warehouse_id': txn.from_simple_warehouse_id,
                    'receipts_count': 0, 'receipts_qty': 0.0, 'receipts_value': 0.0,
                    'issues_count': 0, 'issues_qty': 0.0, 'issues_value': 0.0,
                    'transfers_in_count': 0, 'transfers_in_qty': 0.0, 'transfers_in_value': 0.0,
                    'transfers_out_count': 0, 'transfers_out_qty': 0.0, 'transfers_out_value': 0.0,
                    'adjustments_count': 0, 'adjustments_qty': 0.0, 'adjustments_value': 0.0,
                    'total_transactions': 0
                }
            
            summary = summaries[key]
            summary['total_transactions'] += 1
            
            if txn.transaction_type == 'receive':
                summary['receipts_count'] += 1
                summary['receipts_qty'] += txn.quantity
                summary['receipts_value'] += txn.total_cost
            elif txn.transaction_type == 'issue':
                summary['issues_count'] += 1
                summary['issues_qty'] += txn.quantity
                summary['issues_value'] += txn.total_cost
            elif txn.transaction_type == 'adjustment':
                summary['adjustments_count'] += 1
                summary['adjustments_qty'] += txn.quantity
                summary['adjustments_value'] += txn.total_cost
        
        # Create summary records
        for key, data in summaries.items():
            summary_record = DailyInventoryTransactionSummary(
                summary_date=cycle_date,
                product_id=data['product_id'],
                variant_id=data['variant_id'],
                simple_warehouse_id=data['warehouse_id'],
                receipts_count=data['receipts_count'],
                receipts_quantity=data['receipts_qty'],
                receipts_value=data['receipts_value'],
                issues_count=data['issues_count'],
                issues_quantity=data['issues_qty'],
                issues_value=data['issues_value'],
                adjustments_count=data['adjustments_count'],
                adjustments_quantity=data['adjustments_qty'],
                adjustments_value=data['adjustments_value'],
                total_transactions=data['total_transactions'],
                net_quantity_change=(data['receipts_qty'] - data['issues_qty'] + data['adjustments_qty']),
                net_value_change=(data['receipts_value'] - data['issues_value'] + data['adjustments_value'])
            )
            
            db.session.add(summary_record)

