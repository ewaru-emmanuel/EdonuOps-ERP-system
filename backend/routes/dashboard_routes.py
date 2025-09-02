# Dashboard routes for EdonuOps ERP
from flask import Blueprint, jsonify
from app import db
from modules.finance.models import JournalEntry, JournalLine, Account
from modules.crm.models import Contact, Lead, Opportunity
from modules.inventory.models import Product
from modules.hcm.models import Employee
from datetime import datetime, timedelta
import sqlalchemy as sa

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary data with real calculations"""
    try:
        # Calculate total revenue from journal entries (sum of credit amounts for revenue accounts)
        revenue_query = db.session.query(
            sa.func.sum(JournalLine.credit_amount).label('total_revenue')
        ).join(JournalEntry).join(Account).filter(
            Account.type == 'revenue'
        ).scalar()
        total_revenue = float(revenue_query) if revenue_query else 0.0

        # Get counts from database
        total_customers = Contact.query.filter_by(type='customer').count()
        total_leads = Lead.query.count()
        total_opportunities = Opportunity.query.count()
        total_products = Product.query.count()
        total_employees = Employee.query.count()

        # Get recent activities (last 7 days)
        recent_activities = []
        
        # Recent contacts
        recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(3).all()
        for contact in recent_contacts:
            recent_activities.append({
                'type': 'customer',
                'message': f'New {contact.type} added: {contact.first_name} {contact.last_name}',
                'time': contact.created_at.strftime('%Y-%m-%d %H:%M') if contact.created_at else 'Unknown'
            })

        # Recent products
        recent_products = Product.query.order_by(Product.created_at.desc()).limit(3).all()
        for product in recent_products:
            recent_activities.append({
                'type': 'product',
                'message': f'New product added: {product.name}',
                'time': product.created_at.strftime('%Y-%m-%d %H:%M') if product.created_at else 'Unknown'
            })

        # Recent journal entries
        recent_entries = JournalEntry.query.order_by(JournalEntry.created_at.desc()).limit(3).all()
        for entry in recent_entries:
            recent_activities.append({
                'type': 'finance',
                'message': f'Journal entry created: {entry.reference}',
                'time': entry.created_at.strftime('%Y-%m-%d %H:%M') if entry.created_at else 'Unknown'
            })

        # Sort activities by time (most recent first)
        recent_activities.sort(key=lambda x: x['time'], reverse=True)
        recent_activities = recent_activities[:5]  # Limit to 5 most recent

        return jsonify({
            'status': 'success',
            'data': {
                'totalRevenue': total_revenue,
                'totalCustomers': total_customers,
                'totalLeads': total_leads,
                'totalOpportunities': total_opportunities,
                'totalProducts': total_products,
                'totalEmployees': total_employees,
                'systemStatus': 'operational',
                'recentActivity': recent_activities
            },
            'message': 'Dashboard summary ready'
        })
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return jsonify({
            'status': 'error',
            'data': {
                'totalRevenue': 0,
                'totalCustomers': 0,
                'totalLeads': 0,
                'totalOpportunities': 0,
                'totalProducts': 0,
                'totalEmployees': 0,
                'systemStatus': 'operational',
                'recentActivity': []
            },
            'message': 'Dashboard data unavailable'
        }), 500
