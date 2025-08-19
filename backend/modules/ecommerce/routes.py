from flask import Blueprint, request, jsonify
from app import db
from .models import EcommerceProduct, EcommerceOrder, EcommerceCustomer
from datetime import datetime
import uuid

ecommerce_bp = Blueprint('ecommerce', __name__)

# Products
@ecommerce_bp.route('/products', methods=['GET'])
def get_products():
    try:
        products = EcommerceProduct.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price),
            'stock_quantity': p.stock_quantity,
            'category': p.category,
            'status': p.status,
            'created_at': p.created_at.isoformat()
        } for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        product = EcommerceProduct(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            stock_quantity=data.get('stock_quantity', 0),
            category=data.get('category', ''),
            status=data.get('status', 'Active')
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'id': product.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = EcommerceProduct.query.get_or_404(product_id)
        data = request.get_json()
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
        product.category = data.get('category', product.category)
        product.status = data.get('status', product.status)
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = EcommerceProduct.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Orders
@ecommerce_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = EcommerceOrder.query.all()
        return jsonify([{
            'id': o.id,
            'order_number': o.order_number,
            'customer_name': o.customer_name,
            'customer_email': o.customer_email,
            'total_amount': float(o.total_amount),
            'status': o.status,
            'created_at': o.created_at.isoformat()
        } for o in orders]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        order = EcommerceOrder(
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            customer_name=data['customer_name'],
            customer_email=data.get('customer_email', ''),
            total_amount=data['total_amount'],
            status=data.get('status', 'Pending')
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({'message': 'Order created successfully', 'id': order.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        order = EcommerceOrder.query.get_or_404(order_id)
        data = request.get_json()
        
        order.customer_name = data.get('customer_name', order.customer_name)
        order.customer_email = data.get('customer_email', order.customer_email)
        order.total_amount = data.get('total_amount', order.total_amount)
        order.status = data.get('status', order.status)
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Order updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        order = EcommerceOrder.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Customers
@ecommerce_bp.route('/customers', methods=['GET'])
def get_customers():
    try:
        customers = EcommerceCustomer.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'total_orders': c.total_orders,
            'total_spent': float(c.total_spent),
            'created_at': c.created_at.isoformat()
        } for c in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        customer = EcommerceCustomer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            total_orders=data.get('total_orders', 0),
            total_spent=data.get('total_spent', 0)
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify({'message': 'Customer created successfully', 'id': customer.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = EcommerceCustomer.query.get_or_404(customer_id)
        data = request.get_json()
        
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.total_orders = data.get('total_orders', customer.total_orders)
        customer.total_spent = data.get('total_spent', customer.total_spent)
        customer.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Customer updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ecommerce_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = EcommerceCustomer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
