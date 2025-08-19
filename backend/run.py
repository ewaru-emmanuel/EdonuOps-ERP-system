#!/usr/bin/env python3
"""
Main application entry point for EdonuOps
Handles all API routes and database operations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from app import create_app, db
from modules.core.models import User, Role, Organization
from modules.finance.models import Account, JournalEntry, JournalLine
from modules.inventory.models import Category, Product, Warehouse, InventoryTransaction
from modules.crm.models import Contact, Lead, Opportunity
from modules.hr.models import Employee
from werkzeug.security import check_password_hash
import os
from datetime import datetime, timedelta

app = create_app()
CORS(app)
jwt = JWTManager(app)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Get user role and organization
            role = Role.query.get(user.role_id)
            organization = Organization.query.get(user.organization_id)
            
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": role.role_name if role else "user",
                    "organization": organization.name if organization else "Default",
                    "permissions": role.permissions if role else []
                }
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

# Finance endpoints
@app.route('/api/finance/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    """Get all chart of accounts"""
    try:
        accounts = Account.query.all()
        return jsonify([{
            "id": acc.id,
            "code": acc.code,
            "name": acc.name,
            "type": acc.type,
            "parent_id": acc.parent_id,
            "is_active": acc.is_active,
            "created_at": acc.created_at.isoformat() if acc.created_at else None
        } for acc in accounts]), 200
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts"}), 500

@app.route('/api/finance/journal-entries', methods=['GET'])
@jwt_required()
def get_journal_entries():
    """Get all journal entries"""
    try:
        entries = JournalEntry.query.all()
        return jsonify([{
            "id": entry.id,
            "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "status": entry.status,
            "total_debit": entry.total_debit,
            "total_credit": entry.total_credit,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "lines": [{
                "id": line.id,
                "account_id": line.account_id,
                "debit_amount": line.debit_amount,
                "credit_amount": line.credit_amount,
                "description": line.description
            } for line in entry.lines]
        } for entry in entries]), 200
    except Exception as e:
        print(f"Error fetching journal entries: {e}")
        return jsonify({"error": "Failed to fetch journal entries"}), 500

# Inventory endpoints
@app.route('/api/inventory/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all inventory categories"""
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

@app.route('/api/inventory/products', methods=['GET'])
@jwt_required()
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

# CRM endpoints
@app.route('/api/crm/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    """Get all contacts"""
    try:
        contacts = Contact.query.all()
        return jsonify([{
            "id": contact.id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "type": contact.type,
            "status": contact.status,
            "created_at": contact.created_at.isoformat() if contact.created_at else None
        } for contact in contacts]), 200
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return jsonify({"error": "Failed to fetch contacts"}), 500

# HR endpoints
@app.route('/api/hr/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """Get all employees"""
    try:
        employees = Employee.query.all()
        return jsonify([{
            "id": emp.id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "phone": emp.phone,
            "position": emp.position,
            "department": emp.department,
            "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
            "salary": emp.salary,
            "status": emp.status,
            "created_at": emp.created_at.isoformat() if emp.created_at else None
        } for emp in employees]), 200
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return jsonify({"error": "Failed to fetch employees"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
