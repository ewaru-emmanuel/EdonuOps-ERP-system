from flask import Blueprint, jsonify, request
from app import db
from datetime import datetime
import os

bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

# Import models
from modules.inventory.models import Category, Product, Warehouse, InventoryTransaction

# Product Category endpoints
@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        categories = Category.query.all()
        return jsonify([{
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "parent_id": cat.parent_id,
            "is_active": cat.is_active,
            "created_at": cat.created_at.isoformat() if cat.created_at else None
        } for cat in categories]), 200
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return jsonify({"error": "Failed to fetch categories"}), 500

@bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new product category"""
    try:
        data = request.get_json()
        
        category = Category(
            name=data['name'],
            description=data.get('description', ''),
            parent_id=data.get('parent_id'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "parent_id": category.parent_id,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat() if category.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating category: {e}")
        return jsonify({"error": "Failed to create category"}), 500

@bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a product category"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.parent_id = data.get('parent_id', category.parent_id)
        category.is_active = data.get('is_active', category.is_active)
        
        db.session.commit()
        
        return jsonify({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "parent_id": category.parent_id,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat() if category.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating category: {e}")
        return jsonify({"error": "Failed to update category"}), 500

@bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a product category"""
    try:
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting category: {e}")
        return jsonify({"error": "Failed to delete category"}), 500

# Product endpoints
@bp.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        products = Product.query.all()
        return jsonify([{
            "id": prod.id,
            "sku": prod.sku,
            "name": prod.name,
            "description": prod.description,
            "category_id": prod.category_id,
            "unit": prod.unit,
            "cost_method": prod.cost_method,
            "standard_cost": prod.standard_cost,
            "current_cost": prod.current_cost,
            "current_stock": prod.current_stock,
            "min_stock": prod.min_stock,
            "max_stock": prod.max_stock,
            "is_active": prod.is_active,
            "created_at": prod.created_at.isoformat() if prod.created_at else None
        } for prod in products]), 200
    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500

@bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        product = Product(
            sku=data['sku'],
            name=data['name'],
            description=data.get('description', ''),
            category_id=data.get('category_id'),
            unit=data.get('unit', 'pcs'),
            cost_method=data.get('cost_method', 'FIFO'),
            standard_cost=data.get('standard_cost', 0.0),
            current_cost=data.get('current_cost', 0.0),
            current_stock=data.get('current_stock', 0),
            min_stock=data.get('min_stock', 0),
            max_stock=data.get('max_stock', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "category_id": product.category_id,
            "unit": product.unit,
            "cost_method": product.cost_method,
            "standard_cost": product.standard_cost,
            "current_cost": product.current_cost,
            "current_stock": product.current_stock,
            "min_stock": product.min_stock,
            "max_stock": product.max_stock,
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat() if product.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating product: {e}")
        return jsonify({"error": "Failed to create product"}), 500

@bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        product.sku = data.get('sku', product.sku)
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.category_id = data.get('category_id', product.category_id)
        product.unit = data.get('unit', product.unit)
        product.cost_method = data.get('cost_method', product.cost_method)
        product.standard_cost = data.get('standard_cost', product.standard_cost)
        product.current_cost = data.get('current_cost', product.current_cost)
        product.current_stock = data.get('current_stock', product.current_stock)
        product.min_stock = data.get('min_stock', product.min_stock)
        product.max_stock = data.get('max_stock', product.max_stock)
        product.is_active = data.get('is_active', product.is_active)
        
        db.session.commit()
        
        return jsonify({
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "category_id": product.category_id,
            "unit": product.unit,
            "cost_method": product.cost_method,
            "standard_cost": product.standard_cost,
            "current_cost": product.current_cost,
            "current_stock": product.current_stock,
            "min_stock": product.min_stock,
            "max_stock": product.max_stock,
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat() if product.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating product: {e}")
        return jsonify({"error": "Failed to update product"}), 500

@bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product: {e}")
        return jsonify({"error": "Failed to delete product"}), 500

# Warehouse endpoints
@bp.route('/warehouses', methods=['GET'])
def get_warehouses():
    """Get all warehouses"""
    try:
        warehouses = Warehouse.query.all()
        return jsonify([{
            "id": wh.id,
            "name": wh.name,
            "location": wh.location,
            "capacity": wh.capacity,
            "is_active": wh.is_active,
            "created_at": wh.created_at.isoformat() if wh.created_at else None
        } for wh in warehouses]), 200
    except Exception as e:
        print(f"Error fetching warehouses: {e}")
        return jsonify({"error": "Failed to fetch warehouses"}), 500

@bp.route('/warehouses', methods=['POST'])
def create_warehouse():
    """Create a new warehouse"""
    try:
        data = request.get_json()
        
        warehouse = Warehouse(
            name=data['name'],
            location=data.get('location', ''),
            capacity=data.get('capacity', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(warehouse)
        db.session.commit()
        
        return jsonify({
            "id": warehouse.id,
            "name": warehouse.name,
            "location": warehouse.location,
            "capacity": warehouse.capacity,
            "is_active": warehouse.is_active,
            "created_at": warehouse.created_at.isoformat() if warehouse.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating warehouse: {e}")
        return jsonify({"error": "Failed to create warehouse"}), 500

@bp.route('/warehouses/<int:warehouse_id>', methods=['PUT'])
def update_warehouse(warehouse_id):
    """Update a warehouse"""
    try:
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        data = request.get_json()
        
        warehouse.name = data.get('name', warehouse.name)
        warehouse.location = data.get('location', warehouse.location)
        warehouse.capacity = data.get('capacity', warehouse.capacity)
        warehouse.is_active = data.get('is_active', warehouse.is_active)
        
        db.session.commit()
        
        return jsonify({
            "id": warehouse.id,
            "name": warehouse.name,
            "location": warehouse.location,
            "capacity": warehouse.capacity,
            "is_active": warehouse.is_active,
            "created_at": warehouse.created_at.isoformat() if warehouse.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating warehouse: {e}")
        return jsonify({"error": "Failed to update warehouse"}), 500

@bp.route('/warehouses/<int:warehouse_id>', methods=['DELETE'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse"""
    try:
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        db.session.delete(warehouse)
        db.session.commit()
        
        return jsonify({"message": "Warehouse deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting warehouse: {e}")
        return jsonify({"error": "Failed to delete warehouse"}), 500

# Inventory Transaction endpoints
@bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Get all inventory transactions"""
    try:
        transactions = InventoryTransaction.query.all()
        return jsonify([{
            "id": trans.id,
            "product_id": trans.product_id,
            "transaction_type": trans.transaction_type,
            "quantity": trans.quantity,
            "unit_cost": trans.unit_cost,
            "total_cost": trans.total_cost,
            "reference": trans.reference,
            "created_at": trans.created_at.isoformat() if trans.created_at else None
        } for trans in transactions]), 200
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return jsonify({"error": "Failed to fetch transactions"}), 500

@bp.route('/transactions', methods=['POST'])
def create_transaction():
    """Create a new inventory transaction"""
    try:
        data = request.get_json()
        
        transaction = InventoryTransaction(
            product_id=data['product_id'],
            transaction_type=data['transaction_type'],
            quantity=data['quantity'],
            unit_cost=data.get('unit_cost', 0.0),
            total_cost=data.get('total_cost', 0.0),
            reference=data.get('reference', '')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "id": transaction.id,
            "product_id": transaction.product_id,
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "unit_cost": transaction.unit_cost,
            "total_cost": transaction.total_cost,
            "reference": transaction.reference,
            "created_at": transaction.created_at.isoformat() if transaction.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating transaction: {e}")
        return jsonify({"error": "Failed to create transaction"}), 500
