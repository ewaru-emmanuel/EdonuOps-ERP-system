# Inventory routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.inventory.models import Product, Category, Warehouse, BasicInventoryTransaction
from datetime import datetime
from modules.core.permissions import require_permission, require_module_access

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/products', methods=['GET'])
@require_permission('inventory.products.read')
def get_products():
    """Get all products from database"""
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
            print("Warning: No user context found for products, returning empty results")
            return jsonify([]), 200
        
        # Filter by user - include records with no created_by for backward compatibility
        products = Product.query.filter(
            (Product.created_by == user_id) | (Product.created_by.is_(None))
        ).all()
        return jsonify([{
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price) if product.price else 0.0,
            "current_stock": product.current_stock,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else None,
            "status": product.status,
            "current_cost": float(product.current_cost) if product.current_cost else 0.0,
            "min_stock": product.min_stock,
            "unit": product.unit,
            "created_at": product.created_at.isoformat() if product.created_at else None
        } for product in products]), 200
    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500

@inventory_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories from database"""
    try:
        categories = Category.query.all()
        return jsonify([{
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat() if category.created_at else None
        } for category in categories]), 200
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return jsonify({"error": "Failed to fetch categories"}), 500

@inventory_bp.route('/warehouses', methods=['GET'])
def get_warehouses():
    """Get all warehouses from database"""
    try:
        warehouses = Warehouse.query.all()
        return jsonify([{
            "id": warehouse.id,
            "name": warehouse.name,
            "location": warehouse.location,
            "capacity": warehouse.capacity,
            "is_active": warehouse.is_active,
            "created_at": warehouse.created_at.isoformat() if warehouse.created_at else None
        } for warehouse in warehouses]), 200
    except Exception as e:
        print(f"Error fetching warehouses: {e}")
        return jsonify({"error": "Failed to fetch warehouses"}), 500

@inventory_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Get all inventory transactions from database"""
    try:
        transactions = BasicInventoryTransaction.query.all()
        return jsonify([{
            "id": transaction.id,
            "product_id": transaction.product_id,
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "unit_cost": float(transaction.unit_cost) if transaction.unit_cost else 0.0,
            "total_cost": float(transaction.total_cost) if transaction.total_cost else 0.0,
            "reference": transaction.reference,
            "created_at": transaction.created_at.isoformat() if transaction.created_at else None
        } for transaction in transactions]), 200
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return jsonify({"error": "Failed to fetch transactions"}), 500

@inventory_bp.route('/products', methods=['POST'])
@require_permission('inventory.products.create')
def create_product():
    """Create a new product in database"""
    try:
        data = request.get_json()
        
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
            print("Warning: No user context found for product creation, using default user ID")
        
        # Handle category mapping - frontend sends 'category' as string, we need category_id
        category_id = None
        if data.get('category'):
            # Try to find category by name
            category = Category.query.filter_by(name=data.get('category')).first()
            if category:
                category_id = category.id
            else:
                # Create new category if it doesn't exist
                new_category = Category(name=data.get('category'))
                db.session.add(new_category)
                db.session.flush()  # Get the ID without committing
                category_id = new_category.id
        
        # Generate unique SKU if not provided
        sku = data.get('sku')
        if not sku:
            sku = f"SKU-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        new_product = Product(
            name=data.get('name'),
            sku=sku,
            price=float(data.get('price', 0.0)),
            current_stock=float(data.get('stock', 0)),
            category_id=category_id,
            status=data.get('status', 'active'),
            current_cost=float(data.get('price', 0.0)),  # Use price as current_cost
            min_stock=float(data.get('min_stock', 0)),
            unit=data.get('unit', 'pcs'),
            created_by=user_id  # Associate with current user
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({
            "message": "Product created successfully",
            "id": new_product.id,
            "product": {
                "id": new_product.id,
                "name": new_product.name,
                "sku": new_product.sku,
                "price": float(new_product.price) if new_product.price else 0.0,
                "current_stock": new_product.current_stock,
                "category_id": new_product.category_id,
                "category_name": new_product.category.name if new_product.category else None,
                "status": new_product.status,
                "current_cost": float(new_product.current_cost) if new_product.current_cost else 0.0,
                "min_stock": new_product.min_stock,
                "unit": new_product.unit
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating product: {e}")
        return jsonify({"error": f"Failed to create product: {str(e)}"}), 500

@inventory_bp.route('/products/<int:product_id>', methods=['PUT'])
@require_permission('inventory.products.update')
def update_product(product_id):
    """Update a product in database"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for product update, using default user ID")
        
        # Get product and check ownership
        product = Product.query.get_or_404(product_id)
        
        # Ensure user can only update their own products (or products with no created_by for backward compatibility)
        if product.created_by is not None and product.created_by != user_id:
            return jsonify({"error": "Access denied: You can only update your own products"}), 403
        
        data = request.get_json()
        
        product.name = data.get('name', product.name)
        product.sku = data.get('sku', product.sku)
        product.price = data.get('price', product.price)
        product.current_stock = data.get('current_stock', product.current_stock)
        product.category_id = data.get('category_id', product.category_id)
        product.status = data.get('status', product.status)
        product.current_cost = data.get('current_cost', product.current_cost)
        product.min_stock = data.get('min_stock', product.min_stock)
        product.unit = data.get('unit', product.unit)
        
        db.session.commit()
        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "sku": product.sku,
                "price": float(product.price) if product.price else 0.0,
                "current_stock": product.current_stock,
                "category_id": product.category_id,
                "status": product.status,
                "current_cost": float(product.current_cost) if product.current_cost else 0.0,
                "min_stock": product.min_stock,
                "unit": product.unit
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating product: {e}")
        return jsonify({"error": "Failed to update product"}), 500

@inventory_bp.route('/products/<int:product_id>', methods=['DELETE'])
@require_permission('inventory.products.delete')
def delete_product(product_id):
    """Delete a product from database"""
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, use a default for development
        if not user_id:
            user_id = 1  # Default user for development
            print("Warning: No user context found for product deletion, using default user ID")
        
        # Get product and check ownership
        product = Product.query.get_or_404(product_id)
        
        # Ensure user can only delete their own products (or products with no created_by for backward compatibility)
        if product.created_by is not None and product.created_by != user_id:
            return jsonify({"error": "Access denied: You can only delete your own products"}), 403
        
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product: {e}")
        return jsonify({"error": "Failed to delete product"}), 500

@inventory_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category in database"""
    try:
        data = request.get_json()
        new_category = Category(
            name=data.get('name'),
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_category)
        db.session.commit()
        return jsonify({
            "message": "Category created successfully",
            "id": new_category.id,
            "category": {
                "id": new_category.id,
                "name": new_category.name,
                "description": new_category.description,
                "is_active": new_category.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating category: {e}")
        return jsonify({"error": "Failed to create category"}), 500

@inventory_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a category in database"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.is_active = data.get('is_active', category.is_active)
        
        db.session.commit()
        return jsonify({
            "message": "Category updated successfully",
            "category": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "is_active": category.is_active
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating category: {e}")
        return jsonify({"error": "Failed to update category"}), 500

@inventory_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category from database"""
    try:
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting category: {e}")
        return jsonify({"error": "Failed to delete category"}), 500

@inventory_bp.route('/warehouses', methods=['POST'])
def create_warehouse():
    """Create a new warehouse in database"""
    try:
        data = request.get_json()
        new_warehouse = Warehouse(
            name=data.get('name'),
            location=data.get('location'),
            capacity=data.get('capacity', 0),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_warehouse)
        db.session.commit()
        return jsonify({
            "message": "Warehouse created successfully",
            "id": new_warehouse.id,
            "warehouse": {
                "id": new_warehouse.id,
                "name": new_warehouse.name,
                "location": new_warehouse.location,
                "capacity": new_warehouse.capacity,
                "is_active": new_warehouse.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating warehouse: {e}")
        return jsonify({"error": "Failed to create warehouse"}), 500

@inventory_bp.route('/warehouses/<int:warehouse_id>', methods=['PUT'])
def update_warehouse(warehouse_id):
    """Update a warehouse in database"""
    try:
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        data = request.get_json()
        
        warehouse.name = data.get('name', warehouse.name)
        warehouse.location = data.get('location', warehouse.location)
        warehouse.capacity = data.get('capacity', warehouse.capacity)
        warehouse.is_active = data.get('is_active', warehouse.is_active)
        
        db.session.commit()
        return jsonify({
            "message": "Warehouse updated successfully",
            "warehouse": {
                "id": warehouse.id,
                "name": warehouse.name,
                "location": warehouse.location,
                "capacity": warehouse.capacity,
                "is_active": warehouse.is_active
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating warehouse: {e}")
        return jsonify({"error": "Failed to update warehouse"}), 500

@inventory_bp.route('/warehouses/<int:warehouse_id>', methods=['DELETE'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse from database"""
    try:
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        db.session.delete(warehouse)
        db.session.commit()
        return jsonify({"message": "Warehouse deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting warehouse: {e}")
        return jsonify({"error": "Failed to delete warehouse"}), 500
