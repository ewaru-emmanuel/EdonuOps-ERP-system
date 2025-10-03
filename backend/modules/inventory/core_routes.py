from flask import Blueprint, request, jsonify
from app import db
from modules.inventory.advanced_models import (
    UnitOfMeasure, UOMConversion, ProductCategory, InventoryProduct, ProductVariant,
    AdvancedLocation, SerialNumber, LotBatch, StockLevel, InventoryTransaction,
    InventorySupplier, InventoryCustomer, InventoryAuditTrail, InventoryReport,
    WarehouseActivity, PredictiveStockout, PickerPerformance, AdvancedWarehouse
)
from modules.finance.valuation_engine import MultiCurrencyValuationEngine
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
import json
import random

# Create advanced inventory blueprint
core_inventory_bp = Blueprint('core_inventory', __name__)

# ============================================================================
# CORE INVENTORY DASHBOARD
# ============================================================================

@core_inventory_bp.route('/dashboard', methods=['GET'])
def get_core_dashboard():
    """Get core inventory dashboard data"""
    try:
        # Get basic counts
        total_products = InventoryProduct.query.count()
        total_stock_levels = StockLevel.query.count()
        
        # Get low stock items
        low_stock_items = db.session.query(StockLevel).join(InventoryProduct).filter(
            StockLevel.quantity_on_hand <= InventoryProduct.reorder_point
        ).count()
        
        # Get out of stock items
        out_of_stock_items = StockLevel.query.filter(
            StockLevel.quantity_on_hand <= 0
        ).count()
        
        # Get total stock value
        total_value = db.session.query(
            func.sum(StockLevel.quantity_on_hand * StockLevel.unit_cost)
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_products': total_products,
                'total_stock_levels': total_stock_levels,
                'low_stock_items': low_stock_items,
                'out_of_stock_items': out_of_stock_items,
                'total_stock_value': float(total_value)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# INVENTORY SETTINGS
# ============================================================================

@core_inventory_bp.route('/settings', methods=['GET'])
def get_inventory_settings():
    """Get inventory settings"""
    try:
        # Mock settings for now - in real app, this would come from database
        settings = {
            'default_currency': 'USD',
            'default_warehouse': 'Main Warehouse',
            'low_stock_threshold': 10,
            'auto_reorder_quantity': 50
        }
        return jsonify(settings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@core_inventory_bp.route('/settings', methods=['POST'])
def save_inventory_settings():
    """Save inventory settings"""
    try:
        data = request.get_json()
        # Mock implementation - in real app, save to database
        # For now, just return success
        return jsonify({'message': 'Settings saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# FOUNDATIONAL DATA INTEGRITY ROUTES
# ============================================================================

# Unit of Measure Routes
@core_inventory_bp.route('/uom', methods=['GET'])
def get_uom():
    """Get all units of measure"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        print(f"[UOM] Received X-User-ID header: {user_id}")
        if not user_id:
            print("[UOM] No user ID provided, returning empty array")
            return jsonify([]), 200
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            print(f"[UOM] Invalid user ID format: {user_id}")
            return jsonify([]), 200
        
        # Filter by user - include records with no user_id for backward compatibility
        uoms = UnitOfMeasure.query.filter(
            UnitOfMeasure.is_active == True,
            (UnitOfMeasure.user_id == user_id_int) | (UnitOfMeasure.user_id.is_(None))
        ).all()
        print(f"[UOM] Found {len(uoms)} UoM records for user {user_id_int}")
        return jsonify([{
            'id': uom.id,
            'code': uom.code,
            'name': uom.name,
            'description': uom.description,
            'is_base_unit': uom.is_base_unit
        } for uom in uoms]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@core_inventory_bp.route('/uom', methods=['POST'])
def create_uom():
    """Create new unit of measure"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        data = request.get_json()
        uom = UnitOfMeasure(
            code=data['code'],
            name=data['name'],
            description=data.get('description'),
            is_base_unit=data.get('is_base_unit', False),
            user_id=user_id  # Multi-tenancy support
        )
        db.session.add(uom)
        db.session.commit()
        return jsonify({'message': 'UoM created successfully', 'id': uom.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@core_inventory_bp.route('/uom/<int:uom_id>', methods=['PUT'])
def update_uom(uom_id):
    """Update unit of measure"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        # Check if UoM exists and belongs to user
        uom = UnitOfMeasure.query.filter(
            UnitOfMeasure.id == uom_id,
            (UnitOfMeasure.user_id == int(user_id)) | (UnitOfMeasure.user_id.is_(None))
        ).first()
        
        if not uom:
            return jsonify({'error': 'UoM not found or access denied'}), 404
        
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

@core_inventory_bp.route('/uom/<int:uom_id>', methods=['DELETE'])
def delete_uom(uom_id):
    """Delete UoM"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        # Check if UoM exists and belongs to user
        uom = UnitOfMeasure.query.filter(
            UnitOfMeasure.id == uom_id,
            (UnitOfMeasure.user_id == int(user_id)) | (UnitOfMeasure.user_id.is_(None))
        ).first()
        
        if not uom:
            return jsonify({'error': 'UoM not found or access denied'}), 404
        
        db.session.delete(uom)
        db.session.commit()
        return jsonify({'message': 'UoM deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# UoM Conversion Routes
@core_inventory_bp.route('/uom-conversions', methods=['GET'])
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

@core_inventory_bp.route('/uom-conversions', methods=['POST'])
def create_uom_conversion():
    """Create new UoM conversion"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        data = request.get_json()
        conversion = UOMConversion(
            from_uom_id=data['from_uom_id'],
            to_uom_id=data['to_uom_id'],
            conversion_factor=data['conversion_factor'],
            user_id=user_id  # Multi-tenancy support
        )
        db.session.add(conversion)
        db.session.commit()
        return jsonify({'message': 'UoM conversion created successfully', 'id': conversion.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Product Category Routes
@core_inventory_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        print(f"[CATEGORIES] Received X-User-ID header: {user_id}")
        if not user_id:
            print("[CATEGORIES] No user ID provided, returning empty array")
            return jsonify([]), 200
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            print(f"[CATEGORIES] Invalid user ID format: {user_id}")
            return jsonify([]), 200
        
        # Filter by user - include records with no user_id for backward compatibility
        categories = ProductCategory.query.filter(
            ProductCategory.is_active == True,
            (ProductCategory.user_id == user_id_int) | (ProductCategory.user_id.is_(None))
        ).all()
        print(f"[CATEGORIES] Found {len(categories)} categories for user {user_id_int}")
        return jsonify([{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'parent_id': cat.parent_id,
            'abc_class': cat.abc_class
        } for cat in categories]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@core_inventory_bp.route('/categories', methods=['POST'])
def create_category():
    """Create new product category"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        data = request.get_json()
        category = ProductCategory(
            name=data['name'],
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            abc_class=data.get('abc_class'),
            user_id=user_id  # Multi-tenancy support
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Category created successfully', 'id': category.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Category
@core_inventory_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update product category"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        # Check if category exists and belongs to user
        category = ProductCategory.query.filter(
            ProductCategory.id == category_id,
            (ProductCategory.user_id == int(user_id)) | (ProductCategory.user_id.is_(None))
        ).first()
        
        if not category:
            return jsonify({'error': 'Category not found or access denied'}), 404
        
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
@core_inventory_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete product category"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        # Check if category exists and belongs to user
        category = ProductCategory.query.filter(
            ProductCategory.id == category_id,
            (ProductCategory.user_id == int(user_id)) | (ProductCategory.user_id.is_(None))
        ).first()
        
        if not category:
            return jsonify({'error': 'Category not found or access denied'}), 404
        
        # Check if category has products (only check user's products)
        products = InventoryProduct.query.filter(
            InventoryProduct.category_id == category_id,
            (InventoryProduct.user_id == int(user_id)) | (InventoryProduct.user_id.is_(None))
        ).all()
        if products:
            return jsonify({'error': 'Cannot delete category with existing products'}), 400
        
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Product Routes
@core_inventory_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with variants"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        print(f"[PRODUCTS] Received X-User-ID header: {user_id}")
        if not user_id:
            print("[PRODUCTS] No user ID provided, returning empty array")
            return jsonify([]), 200
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            print(f"[PRODUCTS] Invalid user ID format: {user_id}")
            return jsonify([]), 200
        
        # Filter by user - include records with no user_id for backward compatibility
        products = InventoryProduct.query.filter(
            InventoryProduct.is_active == True,
            (InventoryProduct.user_id == user_id_int) | (InventoryProduct.user_id.is_(None))
        ).all()
        print(f"[PRODUCTS] Found {len(products)} products for user {user_id_int}")
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
                'min_stock_level': product.min_stock_level,
                'max_stock_level': product.max_stock_level,
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

@core_inventory_bp.route('/products/<int:product_id>', methods=['GET'])
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
                            'min_stock_level': product.min_stock_level,
                'max_stock_level': product.max_stock_level,
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

@core_inventory_bp.route('/products', methods=['POST'])
def create_product():
    """Create new product"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User context required'}), 400
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID format'}), 400
        
        data = request.get_json()
        print(f"[PRODUCTS] Received data: {data}")
        print(f"[PRODUCTS] User ID: {user_id} (converted to {user_id_int})")
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Product name is required'}), 400
        
        if not data.get('base_uom_id'):
            return jsonify({'error': 'Base UoM is required'}), 400
        
        # Check if base_uom_id exists and belongs to user
        try:
            base_uom_id = int(data.get('base_uom_id'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid base UoM ID format'}), 400
        
        base_uom = UnitOfMeasure.query.filter(
            UnitOfMeasure.id == base_uom_id,
            (UnitOfMeasure.user_id == user_id_int) | (UnitOfMeasure.user_id.is_(None))
        ).first()
        
        if not base_uom:
            print(f"[PRODUCTS] Base UoM not found: {base_uom_id} for user: {user_id}")
            return jsonify({'error': 'Base UoM not found or access denied'}), 400
        
        # Check if category_id exists and belongs to user (if provided)
        category_id = None
        if data.get('category_id'):
            try:
                category_id = int(data.get('category_id'))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid category ID format'}), 400
            
            category = ProductCategory.query.filter(
                ProductCategory.id == category_id,
                (ProductCategory.user_id == user_id_int) | (ProductCategory.user_id.is_(None))
            ).first()
            
            if not category:
                print(f"[PRODUCTS] Category not found: {category_id} for user: {user_id}")
                return jsonify({'error': 'Category not found or access denied'}), 400
        
        # Handle empty strings for unique fields - convert to None
        sku = data.get('sku') if data.get('sku') else None
        product_id = data.get('product_id') if data.get('product_id') else None
        print(f"[PRODUCTS] Processing unique fields - SKU: '{data.get('sku')}' -> {sku}, Product ID: '{data.get('product_id')}' -> {product_id}")
        
        product = InventoryProduct(
            sku=sku,
            product_id=product_id,
            name=data['name'],
            description=data.get('description'),
            category_id=category_id,
            product_type=data.get('product_type', 'standard'),
            track_serial_numbers=data.get('track_serial_numbers', False),
            track_lots=data.get('track_lots', False),
            track_expiry=data.get('track_expiry', False),
            base_uom_id=base_uom_id,  # Use the validated integer
            purchase_uom_id=data.get('purchase_uom_id'),
            sales_uom_id=data.get('sales_uom_id'),
            cost_method=data.get('cost_method', 'FIFO'),
            standard_cost=data.get('standard_cost', 0.0),
            current_cost=data.get('current_cost', 0.0),
            min_stock_level=data.get('min_stock_level', 0.0),
            max_stock_level=data.get('max_stock_level', 0.0),
            reorder_point=data.get('reorder_point', 0.0),
            reorder_quantity=data.get('reorder_quantity', 0.0),
            lead_time_days=data.get('lead_time_days', 0),
            user_id=user_id_int  # Multi-tenancy support
        )
        db.session.add(product)
        db.session.commit()
        print(f"[PRODUCTS] Product created successfully: {product.name} (ID: {product.id})")
        return jsonify({'message': 'Product created successfully', 'id': product.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"[PRODUCTS] Error creating product: {str(e)}")
        return jsonify({'error': f'Failed to create product: {str(e)}'}), 500

@core_inventory_bp.route('/products/<int:product_id>', methods=['PUT'])
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

@core_inventory_bp.route('/products/<int:product_id>', methods=['DELETE'])
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
@core_inventory_bp.route('/products/<int:product_id>/variants', methods=['POST'])
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
@core_inventory_bp.route('/stock-levels', methods=['GET'])
def get_stock_levels():
    """Get all stock levels"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for stock levels, returning empty results")
            return jsonify([]), 200
        
        # Filter by user - include records with no user_id for backward compatibility
        stock_levels = StockLevel.query.filter(
            (StockLevel.user_id == int(user_id)) | (StockLevel.user_id.is_(None))
        ).all()
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

@core_inventory_bp.route('/stock-levels', methods=['POST'])
def add_stock():
    """Add stock to a product"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
        
        data = request.get_json()
        print(f"[STOCK-LEVELS] Received data: {data}")
        print(f"[STOCK-LEVELS] User ID: {user_id}")
        
        # Validate required fields
        if not data.get('product_id') or not data.get('quantity'):
            print(f"[STOCK-LEVELS] Validation failed - product_id: {data.get('product_id')}, quantity: {data.get('quantity')}")
            return jsonify({'error': 'Product ID and quantity are required'}), 400
        
        try:
            product_id = int(data['product_id'])  # Ensure it's an integer
            quantity = float(data['quantity'])
        except (ValueError, TypeError) as e:
            print(f"[STOCK-LEVELS] Invalid data types - product_id: {data.get('product_id')}, quantity: {data.get('quantity')}")
            return jsonify({'error': 'Invalid product ID or quantity format'}), 400
        simple_warehouse_id = data.get('simple_warehouse_id', 1)  # Default simple warehouse
        cost = data.get('cost', 0.0)
        notes = data.get('notes', '')
        
        # Check if product exists and belongs to user
        print(f"[STOCK-LEVELS] Looking for product ID: {product_id}, user_id: {user_id}")
        product = InventoryProduct.query.filter(
            and_(
                InventoryProduct.id == product_id,
                (InventoryProduct.user_id == int(user_id)) | (InventoryProduct.user_id.is_(None))
            )
        ).first()
        if not product:
            print(f"[STOCK-LEVELS] Product not found or access denied for product_id: {product_id}, user_id: {user_id}")
            return jsonify({'error': 'Product not found or access denied'}), 404
        print(f"[STOCK-LEVELS] Found product: {product.name} (ID: {product.id})")
        
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
                last_updated=datetime.utcnow(),
                created_by=user_id,  # Associate with current user
                user_id=user_id  # Multi-tenancy support
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
            transaction_date=datetime.utcnow(),
            created_by=user_id,  # Associate with current user
            user_id=user_id  # Multi-tenancy support
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

@core_inventory_bp.route('/stock-take', methods=['POST'])
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
@core_inventory_bp.route('/pick-lists', methods=['GET'])
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
@core_inventory_bp.route('/warehouse-activity', methods=['GET'])
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
@core_inventory_bp.route('/predictive-stockouts', methods=['GET'])
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
@core_inventory_bp.route('/picker-performance', methods=['GET'])
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
@core_inventory_bp.route('/warehouse-map', methods=['GET'])
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
@core_inventory_bp.route('/live-activity', methods=['GET'])
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
@core_inventory_bp.route('/warehouse-zones', methods=['GET'])
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

@core_inventory_bp.route('/warehouse-zones', methods=['POST'])
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

@core_inventory_bp.route('/warehouse-aisles', methods=['GET'])
def get_warehouse_aisles():
    """Get all warehouse aisles"""
    try:
        return jsonify(mock_aisles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@core_inventory_bp.route('/warehouse-aisles', methods=['POST'])
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

# ============================================================================
# INVENTORY ADJUSTMENTS
# ============================================================================

@core_inventory_bp.route('/adjustments', methods=['GET'])
def get_inventory_adjustments():
    """Get all inventory adjustments"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty array (for development)
        if not user_id:
            print("Warning: No user context found for adjustments, returning empty results")
            return jsonify([]), 200
        
        # Filter by user - include records with no created_by for backward compatibility
        adjustments = InventoryTransaction.query.filter(
            and_(
                InventoryTransaction.transaction_type == 'adjustment',
                (InventoryTransaction.created_by == user_id) | (InventoryTransaction.created_by.is_(None))
            )
        ).order_by(InventoryTransaction.transaction_date.desc()).all()
        
        result = []
        for adjustment in adjustments:
            result.append({
                'id': adjustment.id,
                'product_id': adjustment.product_id,
                'adjustment_type': adjustment.transaction_type,
                'quantity': adjustment.quantity,
                'reason': adjustment.notes or 'No reason provided',
                'date': adjustment.transaction_date.isoformat(),
                'user_id': adjustment.created_by
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warehouse Locations Routes
@core_inventory_bp.route('/warehouse-locations', methods=['GET'])
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

@core_inventory_bp.route('/warehouse-locations', methods=['POST'])
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

# ============================================================================
# INVENTORY REPORTS
# ============================================================================

@core_inventory_bp.route('/reports/kpis', methods=['GET'])
def get_inventory_kpis():
    """Get inventory KPIs for reports"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        print(f"[INVENTORY KPIs] Received X-User-ID header: {user_id}")
        if not user_id:
            print("[INVENTORY KPIs] No user ID provided, returning empty KPIs")
            return jsonify({
                'success': True,
                'data': {
                    'total_products': 0,
                    'total_stock_levels': 0,
                    'low_stock_items': 0,
                    'out_of_stock_items': 0,
                    'total_stock_value': 0.0,
                    'average_stock_level': 0.0,
                    'category_breakdown': []
                }
            }), 200
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            print(f"[INVENTORY KPIs] Invalid user ID format: {user_id}")
            return jsonify({'success': False, 'error': 'Invalid user ID format'}), 400
        
        # Get basic KPIs - FILTER BY USER
        total_products = InventoryProduct.query.filter(
            (InventoryProduct.user_id == user_id_int) | (InventoryProduct.user_id.is_(None))
        ).count()
        
        # Get stock levels for user's products
        user_product_ids = [p.id for p in InventoryProduct.query.filter(
            (InventoryProduct.user_id == user_id_int) | (InventoryProduct.user_id.is_(None))
        ).all()]
        
        total_stock_levels = StockLevel.query.filter(
            StockLevel.product_id.in_(user_product_ids)
        ).count()
        
        # Get low stock items
        low_stock_items = db.session.query(StockLevel).join(InventoryProduct).filter(
            StockLevel.product_id.in_(user_product_ids),
            StockLevel.quantity_on_hand <= InventoryProduct.reorder_point
        ).count()
        
        # Get out of stock items
        out_of_stock_items = StockLevel.query.filter(
            StockLevel.product_id.in_(user_product_ids),
            StockLevel.quantity_on_hand <= 0
        ).count()
        
        # Get total stock value
        total_value = db.session.query(
            func.sum(StockLevel.quantity_on_hand * StockLevel.unit_cost)
        ).filter(StockLevel.product_id.in_(user_product_ids)).scalar() or 0
        
        # Get average stock level
        avg_stock = db.session.query(
            func.avg(StockLevel.quantity_on_hand)
        ).filter(StockLevel.product_id.in_(user_product_ids)).scalar() or 0
        
        # Get products by category
        category_counts = db.session.query(
            ProductCategory.name,
            func.count(InventoryProduct.id)
        ).join(InventoryProduct).filter(
            (InventoryProduct.user_id == user_id_int) | (InventoryProduct.user_id.is_(None))
        ).group_by(ProductCategory.name).all()
        
        print(f"[INVENTORY KPIs] Found {total_products} products, {total_stock_levels} stock levels for user {user_id_int}")
        
        return jsonify({
            'success': True,
            'data': {
                'total_products': total_products,
                'total_stock_levels': total_stock_levels,
                'low_stock_items': low_stock_items,
                'out_of_stock_items': out_of_stock_items,
                'total_stock_value': float(total_value),
                'average_stock_level': float(avg_stock),
                'category_breakdown': [{'category': cat, 'count': count} for cat, count in category_counts]
            }
        })
    except Exception as e:
        print(f"[INVENTORY KPIs] Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@core_inventory_bp.route('/reports/stock-levels', methods=['GET'])
def get_stock_levels_report():
    """Get detailed stock levels report"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty report (for development)
        if not user_id:
            print("Warning: No user context found for stock levels report, returning empty results")
            return jsonify({
                'report_data': [],
                'summary': {
                    'total_products': 0,
                    'total_value': 0,
                    'low_stock_count': 0
                }
            }), 200
        
        # Get stock levels with product details - FILTER BY USER
        stock_levels = db.session.query(
            StockLevel,
            InventoryProduct.name,
            InventoryProduct.sku,
            ProductCategory.name.label('category_name')
        ).select_from(
            StockLevel
        ).join(
            InventoryProduct, StockLevel.product_id == InventoryProduct.id
        ).join(
            ProductCategory, InventoryProduct.category_id == ProductCategory.id
        ).filter(
            (StockLevel.created_by == user_id) | (StockLevel.created_by.is_(None))
        ).all()
        
        report_data = []
        for stock, product_name, sku, category_name in stock_levels:
            # Get product details for inventory control fields
            product = InventoryProduct.query.get(stock.product_id)
            report_data.append({
                'product_id': stock.product_id,
                'product_name': product_name,
                'sku': sku,
                'category': category_name,
                'quantity_on_hand': stock.quantity_on_hand,
                'unit_cost': float(stock.unit_cost),
                'total_value': float(stock.quantity_on_hand * stock.unit_cost),
                'reorder_point': product.min_stock_level if product else 0,
                'max_stock_level': product.max_stock_level if product else 0,
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
            })
        
        return jsonify({
            'success': True,
            'data': report_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@core_inventory_bp.route('/reports/trends', methods=['GET'])
def get_inventory_trends():
    """Get inventory trends report"""
    try:
        # Get recent transactions for trend analysis
        recent_transactions = db.session.query(
            InventoryTransaction.transaction_date,
            func.count(InventoryTransaction.id).label('transaction_count'),
            func.sum(InventoryTransaction.quantity).label('total_quantity')
        ).filter(
            InventoryTransaction.transaction_date >= (datetime.utcnow().date() - timedelta(days=30))
        ).group_by(
            func.date(InventoryTransaction.transaction_date)
        ).order_by(
            InventoryTransaction.transaction_date
        ).all()
        
        # Get stock movement by category
        category_movement = db.session.query(
            ProductCategory.name,
            func.sum(InventoryTransaction.quantity).label('total_movement')
        ).select_from(
            InventoryTransaction
        ).join(
            InventoryProduct, InventoryTransaction.product_id == InventoryProduct.id
        ).join(
            ProductCategory, InventoryProduct.category_id == ProductCategory.id
        ).filter(
            InventoryTransaction.transaction_date >= (datetime.utcnow().date() - timedelta(days=30))
        ).group_by(
            ProductCategory.name
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'daily_transactions': [
                    {
                        'date': trans.transaction_date.strftime('%Y-%m-%d'),
                        'transaction_count': trans.transaction_count,
                        'total_quantity': trans.total_quantity
                    } for trans in recent_transactions
                ],
                'category_movement': [
                    {
                        'category': cat,
                        'total_movement': float(movement)
                    } for cat, movement in category_movement
                ]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
