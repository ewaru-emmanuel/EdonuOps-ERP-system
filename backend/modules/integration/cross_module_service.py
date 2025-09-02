#!/usr/bin/env python3
"""
Cross-Module Integration Service
Connects Finance ↔ Inventory ↔ CRM
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
import logging

logger = logging.getLogger(__name__)

class CrossModuleIntegrationService:
    """Service for cross-module integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_purchase_order_with_ap(self, supplier_id, items, total_amount):
        """Create PO and AP invoice"""
        try:
            from modules.inventory.advanced_models import PurchaseOrder, PurchaseOrderLine
            from modules.finance.advanced_models import AccountsPayable
            
            # Create PO
            po = PurchaseOrder(
                po_number=f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                supplier_id=supplier_id,
                warehouse_id=1,  # Default warehouse
                order_date=datetime.now().date(),
                expected_delivery_date=datetime.now().date() + timedelta(days=7),
                total_amount=total_amount,
                status='confirmed',
                created_by=1
            )
            db.session.add(po)
            db.session.flush()
            
            # Create AP Invoice
            ap_invoice = AccountsPayable(
                vendor_id=supplier_id,
                invoice_number=f"INV-{po.po_number}",
                invoice_date=datetime.now().date(),
                due_date=datetime.now().date() + timedelta(days=30),
                total_amount=total_amount,
                outstanding_amount=total_amount
            )
            db.session.add(ap_invoice)
            
            db.session.commit()
            return {'po_id': po.id, 'ap_invoice_id': ap_invoice.id}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating PO with AP: {str(e)}")
            raise
    
    def process_goods_receipt(self, po_id, received_items):
        """Process goods receipt and update inventory"""
        try:
            from modules.inventory.advanced_models import StockLevel, AdvancedInventoryTransaction
            
            total_received_amount = 0
            
            for item in received_items:
                # Update Stock Level
                stock_level = StockLevel.query.filter_by(
                    product_id=item['product_id'],
                    location_id=item.get('location_id', 1)
                ).first()
                
                if stock_level:
                    stock_level.quantity_on_hand += item['quantity_received']
                else:
                    stock_level = StockLevel(
                        product_id=item['product_id'],
                        location_id=item.get('location_id', 1),
                        quantity_on_hand=item['quantity_received'],
                        quantity_allocated=0,
                        quantity_available=item['quantity_received'],
                        average_cost=item['unit_cost'],
                        last_updated=datetime.utcnow()
                    )
                    db.session.add(stock_level)
                
                total_received_amount += item['quantity_received'] * item['unit_cost']
            
            db.session.commit()
            return {'total_amount': total_received_amount}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error processing goods receipt: {str(e)}")
            raise
    
    def get_cross_module_analytics(self):
        """Get cross-module analytics"""
        try:
            from modules.finance.advanced_models import AccountsReceivable, AccountsPayable
            from modules.inventory.advanced_models import StockLevel
            from modules.crm.models import Lead, Opportunity
            
            analytics = {
                'financial_summary': {
                    'total_ar': db.session.query(func.sum(AccountsReceivable.total_amount)).scalar() or 0,
                    'total_ap': db.session.query(func.sum(AccountsPayable.total_amount)).scalar() or 0
                },
                'inventory_summary': {
                    'total_products': db.session.query(func.count(StockLevel.id)).scalar() or 0,
                    'total_stock_value': db.session.query(
                        func.sum(StockLevel.quantity_on_hand * StockLevel.average_cost)
                    ).scalar() or 0
                },
                'crm_summary': {
                    'total_leads': db.session.query(func.count(Lead.id)).scalar() or 0,
                    'total_opportunities': db.session.query(func.count(Opportunity.id)).scalar() or 0
                }
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting analytics: {str(e)}")
            raise
