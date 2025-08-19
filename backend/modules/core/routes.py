from flask import Blueprint, request, jsonify
from app import db
from modules.core.models import User, Organization, Role
from modules.crm.models import Contact, Lead, Opportunity
from modules.finance.models import Account, JournalEntry, JournalLine
from modules.inventory.models import Category, Product, InventoryTransaction, Warehouse
from modules.hr.models import Employee, Payroll, Recruitment
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('core', __name__)

@bp.route('/dashboard/summary', methods=['GET'])
def dashboard_summary():
    """Get dashboard summary data"""
    try:
        # Get counts from different modules
        total_customers = Contact.query.count()
        total_leads = Lead.query.count()
        total_opportunities = Opportunity.query.count()
        total_products = Product.query.count()
        total_employees = Employee.query.count()
        
        # Calculate total revenue (sum of all journal entries with credit amounts)
        total_revenue = db.session.query(func.sum(JournalLine.credit_amount)).scalar() or 0
        
        # Get recent transactions (last 5 journal entries)
        recent_transactions = JournalEntry.query.order_by(JournalEntry.created_at.desc()).limit(5).all()
        
        # Get system status
        system_status = {
            'database': 'Online',
            'api_services': 'Online',
            'file_storage': 'Online',
            'email_service': 'Online'
        }
        
        # Format recent transactions
        transactions = []
        for entry in recent_transactions:
            transactions.append({
                'id': entry.id,
                'type': 'Journal Entry',
                'amount': float(entry.total_debit or 0),
                'reference': entry.reference,
                'date': entry.doc_date.isoformat() if entry.doc_date else entry.created_at.isoformat()
            })
        
        summary_data = {
            'totalRevenue': float(total_revenue),
            'totalCustomers': total_customers,
            'totalLeads': total_leads,
            'totalOpportunities': total_opportunities,
            'totalProducts': total_products,
            'totalEmployees': total_employees,
            'recentTransactions': transactions,
            'systemStatus': system_status
        }
        
        return jsonify(summary_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@bp.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        user = User(
            username=data['username'],
            email=data['email']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
