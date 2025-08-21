# E-commerce routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.ecommerce.models import EcommerceProduct, EcommerceOrder, EcommerceCustomer
from datetime import datetime

ecommerce_bp = Blueprint('ecommerce', __name__)

@ecommerce_bp.route('/products', methods=['GET'])
def get_products():
    """Get all e-commerce products from database"""
    try:
        products = EcommerceProduct.query.all()
        return jsonify([{
            "id": product.id,
            "name": product.name,
            "price": float(product.price) if product.price else 0.0,
            "stock_quantity": product.stock_quantity,
            "category": product.category,
            "status": product.status,
            "sku": product.sku,
            "created_at": product.created_at.isoformat() if product.created_at else None
        } for product in products]), 200
    except Exception as e:
        print(f"Error fetching ecommerce products: {e}")
        return jsonify({"error": "Failed to fetch ecommerce products"}), 500

@ecommerce_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all e-commerce orders from database"""
    try:
        orders = EcommerceOrder.query.all()
        return jsonify([{
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "total_amount": float(order.total_amount) if order.total_amount else 0.0,
            "status": order.status,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "created_at": order.created_at.isoformat() if order.created_at else None
        } for order in orders]), 200
    except Exception as e:
        print(f"Error fetching ecommerce orders: {e}")
        return jsonify({"error": "Failed to fetch ecommerce orders"}), 500

@ecommerce_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all e-commerce customers from database"""
    try:
        customers = EcommerceCustomer.query.all()
        return jsonify([{
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "status": customer.status,
            "created_at": customer.created_at.isoformat() if customer.created_at else None
        } for customer in customers]), 200
    except Exception as e:
        print(f"Error fetching ecommerce customers: {e}")
        return jsonify({"error": "Failed to fetch ecommerce customers"}), 500

@ecommerce_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new e-commerce product in database"""
    try:
        data = request.get_json()
        new_product = EcommerceProduct(
            name=data.get('name'),
            price=data.get('price', 0.0),
            stock_quantity=data.get('stock_quantity', 0),
            category=data.get('category'),
            status=data.get('status', 'active'),
            sku=data.get('sku')
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({
            "message": "E-commerce product created successfully",
            "id": new_product.id,
            "product": {
                "id": new_product.id,
                "name": new_product.name,
                "price": float(new_product.price) if new_product.price else 0.0,
                "stock_quantity": new_product.stock_quantity,
                "category": new_product.category,
                "status": new_product.status,
                "sku": new_product.sku
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating ecommerce product: {e}")
        return jsonify({"error": "Failed to create ecommerce product"}), 500

@ecommerce_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an e-commerce product in database"""
    try:
        product = EcommerceProduct.query.get_or_404(product_id)
        data = request.get_json()
        
        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
        product.category = data.get('category', product.category)
        product.status = data.get('status', product.status)
        product.sku = data.get('sku', product.sku)
        
        db.session.commit()
        return jsonify({
            "message": "E-commerce product updated successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "price": float(product.price) if product.price else 0.0,
                "stock_quantity": product.stock_quantity,
                "category": product.category,
                "status": product.status,
                "sku": product.sku
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating ecommerce product: {e}")
        return jsonify({"error": "Failed to update ecommerce product"}), 500

@ecommerce_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete an e-commerce product from database"""
    try:
        product = EcommerceProduct.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "E-commerce product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting ecommerce product: {e}")
        return jsonify({"error": "Failed to delete ecommerce product"}), 500

@ecommerce_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new e-commerce order in database"""
    try:
        data = request.get_json()
        new_order = EcommerceOrder(
            order_number=data.get('order_number'),
            customer_name=data.get('customer_name'),
            total_amount=data.get('total_amount', 0.0),
            status=data.get('status', 'Processing'),
            order_date=datetime.fromisoformat(data.get('order_date')) if data.get('order_date') else datetime.utcnow()
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({
            "message": "E-commerce order created successfully",
            "id": new_order.id,
            "order": {
                "id": new_order.id,
                "order_number": new_order.order_number,
                "customer_name": new_order.customer_name,
                "total_amount": float(new_order.total_amount) if new_order.total_amount else 0.0,
                "status": new_order.status,
                "order_date": new_order.order_date.isoformat() if new_order.order_date else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating ecommerce order: {e}")
        return jsonify({"error": "Failed to create ecommerce order"}), 500

@ecommerce_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an e-commerce order in database"""
    try:
        order = EcommerceOrder.query.get_or_404(order_id)
        data = request.get_json()
        
        order.order_number = data.get('order_number', order.order_number)
        order.customer_name = data.get('customer_name', order.customer_name)
        order.total_amount = data.get('total_amount', order.total_amount)
        order.status = data.get('status', order.status)
        order.order_date = datetime.fromisoformat(data.get('order_date')) if data.get('order_date') else order.order_date
        
        db.session.commit()
        return jsonify({
            "message": "E-commerce order updated successfully",
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "total_amount": float(order.total_amount) if order.total_amount else 0.0,
                "status": order.status,
                "order_date": order.order_date.isoformat() if order.order_date else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating ecommerce order: {e}")
        return jsonify({"error": "Failed to update ecommerce order"}), 500

@ecommerce_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an e-commerce order from database"""
    try:
        order = EcommerceOrder.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "E-commerce order deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting ecommerce order: {e}")
        return jsonify({"error": "Failed to delete ecommerce order"}), 500

@ecommerce_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create a new e-commerce customer in database"""
    try:
        data = request.get_json()
        new_customer = EcommerceCustomer(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            status=data.get('status', 'active')
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({
            "message": "E-commerce customer created successfully",
            "id": new_customer.id,
            "customer": {
                "id": new_customer.id,
                "name": new_customer.name,
                "email": new_customer.email,
                "phone": new_customer.phone,
                "status": new_customer.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating ecommerce customer: {e}")
        return jsonify({"error": "Failed to create ecommerce customer"}), 500

@ecommerce_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update an e-commerce customer in database"""
    try:
        customer = EcommerceCustomer.query.get_or_404(customer_id)
        data = request.get_json()
        
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.status = data.get('status', customer.status)
        
        db.session.commit()
        return jsonify({
            "message": "E-commerce customer updated successfully",
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "status": customer.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating ecommerce customer: {e}")
        return jsonify({"error": "Failed to update ecommerce customer"}), 500

@ecommerce_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete an e-commerce customer from database"""
    try:
        customer = EcommerceCustomer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "E-commerce customer deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting ecommerce customer: {e}")
        return jsonify({"error": "Failed to delete ecommerce customer"}), 500
