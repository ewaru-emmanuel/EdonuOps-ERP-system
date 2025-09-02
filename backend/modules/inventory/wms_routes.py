from flask import Blueprint, request, jsonify
from app import db
from modules.inventory.advanced_models import (
    UnitOfMeasure, UOMConversion, ProductCategory, InventoryProduct, ProductVariant,
    AdvancedLocation, SerialNumber, LotBatch, StockLevel, InventoryTransaction,
    InventorySupplier, InventoryCustomer, InventoryAuditTrail, InventoryReport,
    WarehouseActivity, PredictiveStockout, PickerPerformance, AdvancedWarehouse
)
from modules.finance.valuation_engine import MultiCurrencyValuationEngine
from datetime import datetime, date
from sqlalchemy import func, and_, or_, desc
import json
import random

# Create advanced inventory blueprint
wms_bp = Blueprint('wms_inventory', __name__)

# ============================================================================
# FOUNDATIONAL DATA INTEGRITY ROUTES
# ============================================================================

# Unit of Measure Routes
@wms_bp.route('/uom', methods=['GET'])
def get_uom():
    """Get all units of measure"""
    try:
        uoms = UnitOfMeasure.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': uom.id,
            'code': uom.code,
            'name': uom.name,
            'description': uom.description,
            'is_base_unit': uom.is_base_unit
        } for uom in uoms]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/uom', methods=['POST'])
def create_uom():
    """Create new unit of measure"""
    try:
        data = request.get_json()
        uom = UnitOfMeasure(
            code=data['code'],
            name=data['name'],
            description=data.get('description'),
            is_base_unit=data.get('is_base_unit', False)
        )
        db.session.add(uom)
        db.session.commit()
        return jsonify({'message': 'UoM created successfully', 'id': uom.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/uom/<int:uom_id>', methods=['PUT'])
def update_uom(uom_id):
    """Update unit of measure"""
    try:
        uom = UnitOfMeasure.query.get_or_404(uom_id)
        data = request.get_json()
        
        uom.code = data.get('code', uom.code)
        uom.name = data.get('name', uom.name)
        uom.description = data.get('description', uom.description)
        uom.is_base_unit = data.get('is_base_unit', uom.is_base_unit)
        
        db.session.commit()
        return jsonify({'message': 'UoM updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/uom/<int:uom_id>', methods=['DELETE'])
def delete_uom(uom_id):
    """Delete UoM"""
    try:
        uom = UnitOfMeasure.query.get_or_404(uom_id)
        db.session.delete(uom)
        db.session.commit()
        return jsonify({'message': 'UoM deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# UoM Conversion Routes
@wms_bp.route('/uom-conversions', methods=['GET'])
def get_uom_conversions():
    """Get all UoM conversions"""
    try:
        conversions = UOMConversion.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': conv.id,
            'from_uom': {'id': conv.from_uom.id, 'code': conv.from_uom.code, 'name': conv.from_uom.name},
            'to_uom': {'id': conv.to_uom.id, 'code': conv.to_uom.code, 'name': conv.to_uom.name},
            'conversion_factor': conv.conversion_factor
        } for conv in conversions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/uom-conversions', methods=['POST'])
def create_uom_conversion():
    """Create new UoM conversion"""
    try:
        data = request.get_json()
        conversion = UOMConversion(
            from_uom_id=data['from_uom_id'],
            to_uom_id=data['to_uom_id'],
            conversion_factor=data['conversion_factor']
        )
        db.session.add(conversion)
        db.session.commit()
        return jsonify({'message': 'UoM conversion created successfully', 'id': conversion.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Product Category Routes
@wms_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        categories = ProductCategory.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'parent_id': cat.parent_id,
            'abc_class': cat.abc_class
        } for cat in categories]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/categories', methods=['POST'])
def create_category():
    """Create new product category"""
    try:
        data = request.get_json()
        category = ProductCategory(
            name=data['name'],
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            abc_class=data.get('abc_class')
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Category created successfully', 'id': category.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Category
@wms_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update product category"""
    try:
        category = ProductCategory.query.get_or_404(category_id)
        data = request.get_json()
        
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.parent_id = data.get('parent_id', category.parent_id)
        category.abc_class = data.get('abc_class', category.abc_class)
        
        db.session.commit()
        return jsonify({'message': 'Category updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Category
@wms_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete product category"""
    try:
        category = ProductCategory.query.get_or_404(category_id)
        
        # Check if category has products
        products = InventoryProduct.query.filter_by(category_id=category_id).all()
        if products:
            return jsonify({'error': 'Cannot delete category with existing products'}), 400
        
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Product Routes
@wms_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with variants"""
    try:
        products = InventoryProduct.query.filter_by(is_active=True).all()
        result = []
        for product in products:
            # Get current stock level for this product
            stock_level = StockLevel.query.filter_by(product_id=product.id).first()
            current_stock = stock_level.quantity_on_hand if stock_level else 0
            
            product_data = {
                'id': product.id,
                'sku': product.sku,
                'product_id': product.product_id,
                'name': product.name,
                'description': product.description,
                'category_id': product.category_id,
                'product_type': product.product_type,
                'track_serial_numbers': product.track_serial_numbers,
                'track_lots': product.track_lots,
                'track_expiry': product.track_expiry,
                'cost_method': product.cost_method,
                'standard_cost': product.standard_cost,
                'current_cost': product.current_cost,
                'min_stock': product.min_stock,
                'max_stock': product.max_stock,
                'reorder_point': product.reorder_point,
                'reorder_quantity': product.reorder_quantity,
                'lead_time_days': product.lead_time_days,
                'status': product.status,
                'current_stock': current_stock,
                'variants': [{
                    'id': variant.id,
                    'variant_sku': variant.variant_sku,
                    'variant_name': variant.variant_name,
                    'attributes': variant.attributes
                } for variant in product.variants if variant.is_active]
            }
            result.append(product_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = InventoryProduct.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        # Get current stock level for this product
        stock_level = StockLevel.query.filter_by(product_id=product.id).first()
        current_stock = stock_level.quantity_on_hand if stock_level else 0
        
        product_data = {
            'id': product.id,
            'sku': product.sku,
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'category_id': product.category_id,
            'product_type': product.product_type,
            'track_serial_numbers': product.track_serial_numbers,
            'track_lots': product.track_lots,
            'track_expiry': product.track_expiry,
            'cost_method': product.cost_method,
            'standard_cost': product.standard_cost,
            'current_cost': product.current_cost,
            'min_stock': product.min_stock,
            'max_stock': product.max_stock,
            'reorder_point': product.reorder_point,
            'reorder_quantity': product.reorder_quantity,
            'lead_time_days': product.lead_time_days,
            'status': product.status,
            'current_stock': current_stock,
            'variants': [{
                'id': variant.id,
                'variant_sku': variant.variant_sku,
                'variant_name': variant.variant_name,
                'attributes': variant.attributes
            } for variant in product.variants if variant.is_active]
        }
        return jsonify(product_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/products', methods=['POST'])
def create_product():
    """Create new product"""
    try:
        data = request.get_json()
        product = InventoryProduct(
            sku=data.get('sku'),
            product_id=data.get('product_id'),
            name=data['name'],
            description=data.get('description'),
            category_id=data.get('category_id'),
            product_type=data.get('product_type', 'standard'),
            track_serial_numbers=data.get('track_serial_numbers', False),
            track_lots=data.get('track_lots', False),
            track_expiry=data.get('track_expiry', False),
            base_uom_id=data['base_uom_id'],
            purchase_uom_id=data.get('purchase_uom_id'),
            sales_uom_id=data.get('sales_uom_id'),
            cost_method=data.get('cost_method', 'FIFO'),
            standard_cost=data.get('standard_cost', 0.0),
            current_cost=data.get('current_cost', 0.0),
            min_stock_level=data.get('min_stock_level', 0.0),
            max_stock_level=data.get('max_stock_level', 0.0),
            reorder_point=data.get('reorder_point', 0.0),
            reorder_quantity=data.get('reorder_quantity', 0.0),
            lead_time_days=data.get('lead_time_days', 0)
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'id': product.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product"""
    try:
        product = InventoryProduct.query.get_or_404(product_id)
        data = request.get_json()
        
        for field in ['name', 'description', 'category_id', 'product_type', 'track_serial_numbers', 
                     'track_lots', 'track_expiry', 'base_uom_id', 'purchase_uom_id', 'sales_uom_id',
                     'cost_method', 'standard_cost', 'current_cost', 'min_stock_level', 'max_stock_level',
                     'reorder_point', 'reorder_quantity', 'lead_time_days', 'status', 'sku', 'product_id']:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = InventoryProduct.query.get_or_404(product_id)
        
        # Check if product has stock or is referenced elsewhere
        stock_levels = StockLevel.query.filter_by(product_id=product_id).all()
        if stock_levels:
            return jsonify({'error': 'Cannot delete product with existing stock levels'}), 400
        
        # Soft delete - mark as inactive
        product.is_active = False
        product.deleted_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Product Variant Routes
@wms_bp.route('/products/<int:product_id>/variants', methods=['POST'])
def create_product_variant(product_id):
    """Create new product variant"""
    try:
        data = request.get_json()
        variant = ProductVariant(
            product_id=product_id,
            variant_sku=data['variant_sku'],
            variant_name=data['variant_name'],
            attributes=data.get('attributes', {})
        )
        db.session.add(variant)
        db.session.commit()
        return jsonify({'message': 'Variant created successfully', 'id': variant.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Stock Levels Routes
@wms_bp.route('/stock-levels', methods=['GET'])
def get_stock_levels():
    """Get all stock levels"""
    try:
        stock_levels = StockLevel.query.all()
        result = []
        for stock in stock_levels:
            stock_data = {
                'id': stock.id,
                'product_id': stock.product_id,
                'simple_warehouse_id': stock.simple_warehouse_id,
                'basic_location_id': stock.basic_location_id,
                'advanced_location_id': stock.advanced_location_id,
                'quantity_on_hand': stock.quantity_on_hand,
                'quantity_allocated': stock.quantity_allocated,
                'quantity_available': stock.quantity_available,
                'unit_cost': stock.unit_cost,
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
            }
            result.append(stock_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/stock-levels', methods=['POST'])
def add_stock():
    """Add stock to a product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('product_id') or not data.get('quantity'):
            return jsonify({'error': 'Product ID and quantity are required'}), 400
        
        product_id = data['product_id']
        quantity = float(data['quantity'])
        simple_warehouse_id = data.get('simple_warehouse_id', 1)  # Default simple warehouse
        cost = data.get('cost', 0.0)
        notes = data.get('notes', '')
        
        # Check if product exists
        product = InventoryProduct.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if stock level already exists for this product and simple warehouse
        existing_stock = StockLevel.query.filter_by(
            product_id=product_id, 
            simple_warehouse_id=simple_warehouse_id
        ).first()
        
        if existing_stock:
            # Update existing stock
            existing_stock.quantity_on_hand += quantity
            existing_stock.quantity_available += quantity
            if cost > 0:
                # Update unit cost
                total_value = (existing_stock.quantity_on_hand * existing_stock.unit_cost) + (quantity * cost)
                existing_stock.unit_cost = total_value / existing_stock.quantity_on_hand
            existing_stock.last_updated = datetime.utcnow()
            stock_level = existing_stock
        else:
            # Create new stock level
            stock_level = StockLevel(
                product_id=product_id,
                simple_warehouse_id=simple_warehouse_id,
                quantity_on_hand=quantity,
                quantity_available=quantity,
                unit_cost=cost,
                last_updated=datetime.utcnow()
            )
            db.session.add(stock_level)
        
        # Create stock transaction record
        transaction = InventoryTransaction(
            transaction_type='stock_addition',
            product_id=product_id,
            to_simple_warehouse_id=simple_warehouse_id,
            quantity=quantity,
            unit_cost=cost,
            reference_type='Stock Addition',
            reference_number='SA' + str(datetime.utcnow().strftime('%Y%m%d%H%M%S')),
            notes=notes,
            transaction_date=datetime.utcnow()
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Stock added successfully',
            'stock_level': {
                'id': stock_level.id,
                'product_id': stock_level.product_id,
                'simple_warehouse_id': stock_level.simple_warehouse_id,
                'quantity_on_hand': stock_level.quantity_on_hand,
                'quantity_available': stock_level.quantity_available,
                'unit_cost': stock_level.unit_cost
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error adding stock: {str(e)}'}), 500

@wms_bp.route('/stock-take', methods=['POST'])
def record_stock_take():
    """Record a stock take/adjustment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('product_id') or not data.get('counted_quantity'):
            return jsonify({'error': 'Product ID and counted quantity are required'}), 400
        
        product_id = data['product_id']
        counted_quantity = float(data['counted_quantity'])
        location = data.get('location', 'Default Location')
        notes = data.get('notes', '')
        
        # Check if product exists
        product = InventoryProduct.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get current stock level
        current_stock = StockLevel.query.filter_by(product_id=product_id).first()
        current_quantity = current_stock.quantity_on_hand if current_stock else 0
        
        # Calculate adjustment
        adjustment_quantity = counted_quantity - current_quantity
        
        # Update or create stock level
        if current_stock:
            current_stock.quantity_on_hand = counted_quantity
            current_stock.quantity_available = counted_quantity - current_stock.quantity_allocated
            current_stock.last_updated = datetime.utcnow()
        else:
            # Create new stock level
            current_stock = StockLevel(
                product_id=product_id,
                simple_warehouse_id=1,  # Default simple warehouse
                quantity_on_hand=counted_quantity,
                quantity_available=counted_quantity,
                unit_cost=product.current_cost or 0,
                last_updated=datetime.utcnow()
            )
            db.session.add(current_stock)
        
        # Create transaction record
        transaction = InventoryTransaction(
            transaction_type='stock_take',
            product_id=product_id,
            to_simple_warehouse_id=1,  # Default simple warehouse
            quantity=adjustment_quantity,
            unit_cost=product.current_cost or 0,
            reference_type='Stock Take',
            reference_number='ST' + str(datetime.utcnow().strftime('%Y%m%d%H%M%S')),
            notes=f"Stock take: {notes}. Counted: {counted_quantity}, Previous: {current_quantity}",
            transaction_date=datetime.utcnow()
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Stock take recorded successfully',
            'stock_level': {
                'id': current_stock.id,
                'product_id': current_stock.product_id,
                'quantity_on_hand': current_stock.quantity_on_hand,
                'quantity_available': current_stock.quantity_available
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error recording stock take: {str(e)}'}), 500

# Pick Lists Routes
@wms_bp.route('/pick-lists', methods=['GET'])
def get_pick_lists():
    """Get all pick lists"""
    try:
        pick_lists = PickList.query.all()
        result = []
        for pick_list in pick_lists:
            pick_data = {
                'id': pick_list.id,
                'pick_list_number': pick_list.pick_list_number,
                'warehouse_id': pick_list.warehouse_id,
                'sales_order_id': pick_list.sales_order_id,
                'assigned_to': pick_list.assigned_to,
                'status': pick_list.status,
                'pick_date': pick_list.pick_date.isoformat() if pick_list.pick_date else None,
                'completed_at': pick_list.completed_at.isoformat() if pick_list.completed_at else None
            }
            result.append(pick_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warehouse Activity Routes
@wms_bp.route('/warehouse-activity', methods=['GET'])
def get_warehouse_activity():
    """Get warehouse activity"""
    try:
        activities = WarehouseActivity.query.order_by(WarehouseActivity.activity_timestamp.desc()).limit(50).all()
        result = []
        for activity in activities:
            activity_data = {
                'id': activity.id,
                'warehouse_id': activity.warehouse_id,
                'location_id': activity.location_id,
                'user_id': activity.user_id,
                'activity_type': activity.activity_type,
                'activity_timestamp': activity.activity_timestamp.isoformat() if activity.activity_timestamp else None,
                'efficiency_score': activity.efficiency_score,
                'duration_seconds': activity.duration_seconds
            }
            result.append(activity_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Predictive Stockouts Routes
@wms_bp.route('/predictive-stockouts', methods=['GET'])
def get_predictive_stockouts():
    """Get predictive stockouts"""
    try:
        stockouts = PredictiveStockout.query.all()
        result = []
        for stockout in stockouts:
            stockout_data = {
                'id': stockout.id,
                'product_id': stockout.product_id,
                'location_id': stockout.location_id,
                'predicted_stockout_date': stockout.predicted_stockout_date.isoformat() if stockout.predicted_stockout_date else None,
                'days_until_stockout': stockout.days_until_stockout,
                'current_stock': stockout.current_stock,
                'daily_consumption_rate': stockout.daily_consumption_rate,
                'alert_level': stockout.alert_level
            }
            result.append(stockout_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Picker Performance Routes
@wms_bp.route('/picker-performance', methods=['GET'])
def get_picker_performance():
    """Get picker performance"""
    try:
        performances = PickerPerformance.query.order_by(PickerPerformance.performance_date.desc()).limit(20).all()
        result = []
        for performance in performances:
            perf_data = {
                'id': performance.id,
                'user_id': performance.user_id,
                'warehouse_id': performance.warehouse_id,
                'performance_date': performance.performance_date.isoformat() if performance.performance_date else None,
                'total_picks': performance.total_picks,
                'total_items_picked': performance.total_items_picked,
                'total_pick_time_seconds': performance.total_pick_time_seconds,
                'efficiency_score': performance.efficiency_score,
                'picks_per_hour': performance.picks_per_hour,
                'warehouse_average_picks_per_hour': performance.warehouse_average_picks_per_hour
            }
            result.append(perf_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warehouse Map Routes
@wms_bp.route('/warehouse-map', methods=['GET'])
def get_warehouse_map():
    """Get warehouse map data"""
    try:
        warehouses = AdvancedWarehouse.query.all()
        result = []
        for warehouse in warehouses:
            warehouse_data = {
                'id': warehouse.id,
                'name': warehouse.name,
                'code': warehouse.code,
                'address': warehouse.address,
                'total_capacity': warehouse.total_capacity,
                'used_capacity': warehouse.used_capacity,
                'zones': [{
                    'id': zone.id,
                    'name': zone.name,
                    'code': zone.code,
                    'utilization': random.uniform(0.3, 0.9),
                    'picker_count': random.randint(1, 5),
                    'efficiency': random.uniform(0.7, 1.0)
                } for zone in warehouse.zones]
            }
            result.append(warehouse_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Live Activity Routes
@wms_bp.route('/live-activity', methods=['GET'])
def get_live_activity():
    """Get live warehouse activity"""
    try:
        activities = WarehouseActivity.query.order_by(WarehouseActivity.activity_timestamp.desc()).limit(10).all()
        result = []
        for activity in activities:
            activity_data = {
                'id': activity.id,
                'user_id': activity.user_id,
                'activity_type': activity.activity_type,
                'location_id': activity.location_id,
                'efficiency': activity.efficiency_score,
                'timestamp': activity.activity_timestamp.isoformat() if activity.activity_timestamp else None
            }
            result.append(activity_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warehouse Zones Routes
@wms_bp.route('/warehouse-zones', methods=['GET'])
def get_warehouse_zones():
    """Get all warehouse zones"""
    try:
        # Mock data for now - in real implementation, this would come from database
        zones = [
            {
                'id': 1,
                'name': 'Zone A - Picking',
                'description': 'High-velocity picking zone',
                'warehouse_id': 1,
                'capacity': 1000,
                'used_capacity': 750,
                'is_active': True
            },
            {
                'id': 2,
                'name': 'Zone B - Storage',
                'description': 'Bulk storage zone',
                'warehouse_id': 1,
                'capacity': 2000,
                'used_capacity': 1200,
                'is_active': True
            },
            {
                'id': 3,
                'name': 'Zone C - Receiving',
                'description': 'Inbound receiving zone',
                'warehouse_id': 1,
                'capacity': 500,
                'used_capacity': 200,
                'is_active': True
            },
            {
                'id': 4,
                'name': 'Zone D - Shipping',
                'description': 'Outbound shipping zone',
                'warehouse_id': 1,
                'capacity': 800,
                'used_capacity': 400,
                'is_active': True
            }
        ]
        return jsonify(zones), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/warehouse-zones', methods=['POST'])
def create_warehouse_zone():
    """Create a new warehouse zone"""
    try:
        data = request.get_json()
        # Mock implementation - in real app, save to database
        new_zone = {
            'id': len(data) + 1,  # Mock ID generation
            'name': data.get('name'),
            'description': data.get('description'),
            'warehouse_id': data.get('warehouse_id', 1),
            'capacity': data.get('capacity', 0),
            'used_capacity': 0,
            'is_active': True
        }
        return jsonify({'message': 'Zone created successfully', 'zone': new_zone}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warehouse Aisles Routes
# Global storage for mock aisles data
mock_aisles = [
    {
        'id': 1,
        'name': 'Aisle A1',
        'zone_id': 1,
        'zone_name': 'Zone A - Picking',
        'length': 100,
        'width': 10,
        'height': 20,
        'is_active': True
    },
    {
        'id': 2,
        'name': 'Aisle A2',
        'zone_id': 1,
        'zone_name': 'Zone A - Picking',
        'length': 100,
        'width': 10,
        'height': 20,
        'is_active': True
    },
    {
        'id': 3,
        'name': 'Aisle B1',
        'zone_id': 2,
        'zone_name': 'Zone B - Storage',
        'length': 150,
        'width': 12,
        'height': 25,
        'is_active': True
    }
]

@wms_bp.route('/warehouse-aisles', methods=['GET'])
def get_warehouse_aisles():
    """Get all warehouse aisles"""
    try:
        return jsonify(mock_aisles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/warehouse-aisles', methods=['POST'])
def create_warehouse_aisle():
    """Create a new warehouse aisle"""
    try:
        data = request.get_json()
        # Mock implementation
        new_aisle = {
            'id': len(mock_aisles) + 1,
            'name': data.get('name'),
            'zone_id': data.get('zone_id'),
            'zone_name': data.get('zone_name'),
            'length': data.get('length', 0),
            'width': data.get('width', 0),
            'height': data.get('height', 0),
            'is_active': True
        }
        mock_aisles.append(new_aisle)
        return jsonify({'message': 'Aisle created successfully', 'aisle': new_aisle}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warehouse Locations Routes
@wms_bp.route('/warehouse-locations', methods=['GET'])
def get_warehouse_locations():
    """Get all warehouse locations"""
    try:
        # Mock data
        locations = [
            {
                'id': 1,
                'location_code': 'A1-01-01',
                'aisle_id': 1,
                'aisle_name': 'Aisle A1',
                'rack_number': 1,
                'level': 1,
                'position': 1,
                'capacity': 100,
                'used_capacity': 75,
                'is_active': True
            },
            {
                'id': 2,
                'location_code': 'A1-01-02',
                'aisle_id': 1,
                'aisle_name': 'Aisle A1',
                'rack_number': 1,
                'level': 1,
                'position': 2,
                'capacity': 100,
                'used_capacity': 50,
                'is_active': True
            }
        ]
        return jsonify(locations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wms_bp.route('/warehouse-locations', methods=['POST'])
def create_warehouse_location():
    """Create a new warehouse location"""
    try:
        data = request.get_json()
        # Mock implementation
        new_location = {
            'id': len(data) + 1,
            'location_code': data.get('location_code'),
            'aisle_id': data.get('aisle_id'),
            'aisle_name': data.get('aisle_name'),
            'rack_number': data.get('rack_number'),
            'level': data.get('level'),
            'position': data.get('position'),
            'capacity': data.get('capacity', 0),
            'used_capacity': 0,
            'is_active': True
        }
        return jsonify({'message': 'Location created successfully', 'location': new_location}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
