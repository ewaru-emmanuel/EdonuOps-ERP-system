"""
Progressive Complexity Service
Handles the three-tier system: Inventory Only, Basic Location, Advanced WMS
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import and_, or_, func
from app import db
from .advanced_models import (
    InventorySystemConfig, StockLevel, InventoryTransaction,
    SimpleWarehouse, BasicLocation, AdvancedLocation,
    InventoryProduct, SerialNumber, LotBatch
)

logger = logging.getLogger(__name__)

class ProgressiveComplexityService:
    """
    Service to handle progressive complexity tiers
    """
    
    @classmethod
    def get_system_config(cls) -> Dict[str, Any]:
        """Get current system configuration"""
        try:
            config = InventorySystemConfig.query.first()
            if not config:
                # Create default Tier 1 configuration
                config = InventorySystemConfig(
                    complexity_tier=1,
                    enable_location_tracking=False,
                    enable_warehouse_hierarchy=False,
                    enable_mobile_wms=False,
                    enable_advanced_analytics=False,
                    show_warehouse_operations=False,
                    show_location_management=False,
                    show_advanced_reports=False,
                    business_type='retail',
                    inventory_size='small',
                    warehouse_count=1
                )
                db.session.add(config)
                db.session.commit()
            
            return {
                'complexity_tier': config.complexity_tier,
                'enable_location_tracking': config.enable_location_tracking,
                'enable_warehouse_hierarchy': config.enable_warehouse_hierarchy,
                'enable_mobile_wms': config.enable_mobile_wms,
                'enable_advanced_analytics': config.enable_advanced_analytics,
                'show_warehouse_operations': config.show_warehouse_operations,
                'show_location_management': config.show_location_management,
                'show_advanced_reports': config.show_advanced_reports,
                'business_type': config.business_type,
                'inventory_size': config.inventory_size,
                'warehouse_count': config.warehouse_count
            }
        except Exception as e:
            logger.error(f"Error getting system config: {str(e)}")
            return {}
    
    @classmethod
    def set_complexity_tier(cls, tier: int, business_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Set complexity tier and configure system accordingly"""
        try:
            config = InventorySystemConfig.query.first()
            if not config:
                config = InventorySystemConfig()
                db.session.add(config)
            
            config.complexity_tier = tier
            
            # Configure based on tier
            if tier == 1:  # Inventory Only
                config.enable_location_tracking = False
                config.enable_warehouse_hierarchy = False
                config.enable_mobile_wms = False
                config.enable_advanced_analytics = False
                config.show_warehouse_operations = False
                config.show_location_management = False
                config.show_advanced_reports = False
                
            elif tier == 2:  # Basic Location
                config.enable_location_tracking = True
                config.enable_warehouse_hierarchy = False
                config.enable_mobile_wms = False
                config.enable_advanced_analytics = True
                config.show_warehouse_operations = True
                config.show_location_management = True
                config.show_advanced_reports = True
                
            elif tier == 3:  # Advanced WMS
                config.enable_location_tracking = True
                config.enable_warehouse_hierarchy = True
                config.enable_mobile_wms = True
                config.enable_advanced_analytics = True
                config.show_warehouse_operations = True
                config.show_location_management = True
                config.show_advanced_reports = True
            
            # Set business context if provided
            if business_context:
                config.business_type = business_context.get('business_type', 'retail')
                config.inventory_size = business_context.get('inventory_size', 'small')
                config.warehouse_count = business_context.get('warehouse_count', 1)
            
            db.session.commit()
            
            return cls.get_system_config()
            
        except Exception as e:
            logger.error(f"Error setting complexity tier: {str(e)}")
            db.session.rollback()
            return {}
    
    @classmethod
    def get_stock_levels(cls, product_id: Optional[int] = None, warehouse_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get stock levels adapted to current complexity tier"""
        try:
            config = cls.get_system_config()
            tier = config.get('complexity_tier', 1)
            
            query = StockLevel.query.join(InventoryProduct)
            
            if product_id:
                query = query.filter(StockLevel.product_id == product_id)
            
            if tier == 1:  # Inventory Only - Simple warehouse tracking
                if warehouse_id:
                    query = query.filter(StockLevel.simple_warehouse_id == warehouse_id)
                
                stock_levels = query.all()
                result = []
                
                for stock in stock_levels:
                    warehouse_name = stock.simple_warehouse.name if stock.simple_warehouse else 'Unknown'
                    result.append({
                        'product_id': stock.product_id,
                        'product_name': stock.product.name,
                        'sku': stock.product.sku,
                        'warehouse': warehouse_name,
                        'quantity_on_hand': stock.quantity_on_hand,
                        'quantity_available': stock.quantity_available,
                        'unit_cost': stock.unit_cost,
                        'total_value': stock.total_value,
                        'tier': 1
                    })
                
            elif tier == 2:  # Basic Location - Location breakdown
                if warehouse_id:
                    query = query.join(BasicLocation).filter(BasicLocation.warehouse_id == warehouse_id)
                
                stock_levels = query.all()
                result = []
                
                for stock in stock_levels:
                    location_info = {
                        'location_code': stock.basic_location.location_code if stock.basic_location else None,
                        'location_name': stock.basic_location.location_name if stock.basic_location else None
                    }
                    
                    result.append({
                        'product_id': stock.product_id,
                        'product_name': stock.product.name,
                        'sku': stock.product.sku,
                        'warehouse': stock.basic_location.warehouse.name if stock.basic_location else 'Unknown',
                        'location': location_info,
                        'quantity_on_hand': stock.quantity_on_hand,
                        'quantity_available': stock.quantity_available,
                        'unit_cost': stock.unit_cost,
                        'total_value': stock.total_value,
                        'tier': 2
                    })
                
            elif tier == 3:  # Advanced WMS - Full hierarchy
                if warehouse_id:
                    # This would need to be implemented with the full hierarchy
                    pass
                
                stock_levels = query.all()
                result = []
                
                for stock in stock_levels:
                    location_info = {
                        'location_code': stock.advanced_location.location_code if stock.advanced_location else None,
                        'location_name': stock.advanced_location.location_name if stock.advanced_location else None,
                        'barcode': stock.advanced_location.barcode if stock.advanced_location else None,
                        'zone': stock.advanced_location.level.rack.aisle.zone.name if stock.advanced_location else None,
                        'aisle': stock.advanced_location.level.rack.aisle.name if stock.advanced_location else None,
                        'rack': stock.advanced_location.level.rack.name if stock.advanced_location else None,
                        'level': stock.advanced_location.level.level_number if stock.advanced_location else None
                    }
                    
                    result.append({
                        'product_id': stock.product_id,
                        'product_name': stock.product.name,
                        'sku': stock.product.sku,
                        'warehouse': stock.advanced_location.level.rack.aisle.zone.warehouse.name if stock.advanced_location else 'Unknown',
                        'location': location_info,
                        'quantity_on_hand': stock.quantity_on_hand,
                        'quantity_available': stock.quantity_available,
                        'unit_cost': stock.unit_cost,
                        'total_value': stock.total_value,
                        'tier': 3
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting stock levels: {str(e)}")
            return []
    
    @classmethod
    def create_stock_transaction(cls, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create stock transaction adapted to current complexity tier"""
        try:
            config = cls.get_system_config()
            tier = config.get('complexity_tier', 1)
            
            # Create transaction based on tier
            transaction = InventoryTransaction(
                transaction_type=transaction_data['transaction_type'],
                product_id=transaction_data['product_id'],
                quantity=transaction_data['quantity'],
                unit_cost=transaction_data.get('unit_cost', 0.0),
                total_cost=transaction_data.get('total_cost', 0.0),
                reference_number=transaction_data.get('reference_number'),
                reference_type=transaction_data.get('reference_type'),
                notes=transaction_data.get('notes'),
                created_by=transaction_data.get('created_by')
            )
            
            if tier == 1:  # Simple warehouse tracking
                transaction.from_simple_warehouse_id = transaction_data.get('from_warehouse_id')
                transaction.to_simple_warehouse_id = transaction_data.get('to_warehouse_id')
                
            elif tier == 2:  # Basic location tracking
                transaction.from_basic_location_id = transaction_data.get('from_location_id')
                transaction.to_basic_location_id = transaction_data.get('to_location_id')
                
            elif tier == 3:  # Advanced location tracking
                transaction.from_advanced_location_id = transaction_data.get('from_location_id')
                transaction.to_advanced_location_id = transaction_data.get('to_location_id')
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'status': 'success',
                'transaction_id': transaction.id,
                'tier': tier
            }
            
        except Exception as e:
            logger.error(f"Error creating stock transaction: {str(e)}")
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}
    
    @classmethod
    def get_ui_configuration(cls) -> Dict[str, Any]:
        """Get UI configuration based on complexity tier"""
        try:
            config = cls.get_system_config()
            tier = config.get('complexity_tier', 1)
            
            ui_config = {
                'tier': tier,
                'show_warehouse_operations': config.get('show_warehouse_operations', False),
                'show_location_management': config.get('show_location_management', False),
                'show_advanced_reports': config.get('show_advanced_reports', False),
                'enable_mobile_wms': config.get('enable_mobile_wms', False),
                'enable_advanced_analytics': config.get('enable_advanced_analytics', False),
                'menu_items': [],
                'features': []
            }
            
            # Configure menu items based on tier
            if tier == 1:  # Inventory Only
                ui_config['menu_items'] = [
                    {'label': 'Dashboard', 'icon': 'dashboard', 'enabled': True},
                    {'label': 'Products', 'icon': 'inventory', 'enabled': True},
                    {'label': 'Stock Levels', 'icon': 'assessment', 'enabled': True},
                    {'label': 'Reports', 'icon': 'analytics', 'enabled': True},
                    {'label': 'Settings', 'icon': 'settings', 'enabled': True}
                ]
                ui_config['features'] = [
                    'Basic inventory tracking',
                    'Product management',
                    'Stock level monitoring',
                    'Simple reports'
                ]
                
            elif tier == 2:  # Basic Location
                ui_config['menu_items'] = [
                    {'label': 'Dashboard', 'icon': 'dashboard', 'enabled': True},
                    {'label': 'Products', 'icon': 'inventory', 'enabled': True},
                    {'label': 'Stock Levels', 'icon': 'assessment', 'enabled': True},
                    {'label': 'Locations', 'icon': 'location_on', 'enabled': True},
                    {'label': 'Operations', 'icon': 'build', 'enabled': True},
                    {'label': 'Reports', 'icon': 'analytics', 'enabled': True},
                    {'label': 'Settings', 'icon': 'settings', 'enabled': True}
                ]
                ui_config['features'] = [
                    'Basic inventory tracking',
                    'Location-based stock management',
                    'Product management',
                    'Stock level monitoring',
                    'Basic operations',
                    'Enhanced reports'
                ]
                
            elif tier == 3:  # Advanced WMS
                ui_config['menu_items'] = [
                    {'label': 'Dashboard', 'icon': 'dashboard', 'enabled': True},
                    {'label': 'Products', 'icon': 'inventory', 'enabled': True},
                    {'label': 'Stock Levels', 'icon': 'assessment', 'enabled': True},
                    {'label': 'Warehouse Map', 'icon': 'map', 'enabled': True},
                    {'label': 'Locations', 'icon': 'location_on', 'enabled': True},
                    {'label': 'Operations', 'icon': 'build', 'enabled': True},
                    {'label': 'Mobile WMS', 'icon': 'phone_android', 'enabled': True},
                    {'label': 'Analytics', 'icon': 'analytics', 'enabled': True},
                    {'label': 'Reports', 'icon': 'assessment', 'enabled': True},
                    {'label': 'Settings', 'icon': 'settings', 'enabled': True}
                ]
                ui_config['features'] = [
                    'Advanced inventory tracking',
                    'Full warehouse hierarchy',
                    'Mobile WMS support',
                    'Advanced analytics',
                    'Real-time operations',
                    'Comprehensive reporting',
                    'Barcode scanning',
                    'Directed picking'
                ]
            
            return ui_config
            
        except Exception as e:
            logger.error(f"Error getting UI configuration: {str(e)}")
            return {}

