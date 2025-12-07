# Dashboard routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.finance.models import JournalEntry, JournalLine, Account
from datetime import datetime, timedelta
import sqlalchemy as sa

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/debug', methods=['GET'])
def debug_dashboard():
    """Debug endpoint to test database queries"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        # Test direct SQL query
        result = db.session.execute(
            sa.text("SELECT COUNT(*) FROM contacts WHERE type = 'customer' AND user_id = :user_id"),
            {'user_id': int(user_id)}
        ).scalar()
        
        return jsonify({
            'user_id': user_id,
            'user_id_type': type(user_id),
            'int_user_id': int(user_id),
            'customer_count': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary data with real calculations filtered by user"""
    try:
        # Get user ID from request headers
        user_id = request.headers.get('X-User-ID')
        print(f"[DASHBOARD] Received request with X-User-ID header: {user_id}")
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User authentication required'
            }), 401
        
        # Calculate total revenue from journal entries (sum of credit amounts for revenue accounts) - FILTERED BY USER
        revenue_query = db.session.query(
            sa.func.sum(JournalLine.credit_amount).label('total_revenue')
        ).join(JournalEntry).join(Account).filter(
            Account.type == 'revenue',
            JournalEntry.user_id == int(user_id)
        ).scalar()
        total_revenue = float(revenue_query) if revenue_query else 0.0

        # Get counts from database - FILTERED BY USER (using direct SQL queries)
        print(f"DEBUG: user_id = {user_id}, type = {type(user_id)}")
        
        # Try to get counts with user_id filter, fallback to total count if column doesn't exist
        try:
            total_customers = db.session.execute(
                sa.text("SELECT COUNT(*) FROM contacts WHERE type = 'customer' AND user_id = :user_id"),
                {'user_id': int(user_id)}
            ).scalar()
        except Exception as e:
            print(f"Warning: user_id column not found in contacts table: {e}")
            total_customers = db.session.execute(sa.text("SELECT COUNT(*) FROM contacts WHERE type = 'customer'")).scalar()
        print(f"DEBUG: total_customers = {total_customers}")
        
        try:
            total_leads = db.session.execute(
                sa.text("SELECT COUNT(*) FROM leads WHERE user_id = :user_id"),
                {'user_id': int(user_id)}
            ).scalar()
        except Exception as e:
            print(f"Warning: user_id column not found in leads table: {e}")
            total_leads = db.session.execute(sa.text("SELECT COUNT(*) FROM leads")).scalar()
        
        try:
            total_opportunities = db.session.execute(
                sa.text("SELECT COUNT(*) FROM opportunities WHERE user_id = :user_id"),
                {'user_id': int(user_id)}
            ).scalar()
        except Exception as e:
            print(f"Warning: user_id column not found in opportunities table: {e}")
            total_opportunities = db.session.execute(sa.text("SELECT COUNT(*) FROM opportunities")).scalar()
        
        try:
            total_products = db.session.execute(
                sa.text("SELECT COUNT(*) FROM products WHERE user_id = :user_id"),
                {'user_id': int(user_id)}
            ).scalar()
        except Exception as e:
            print(f"Warning: user_id column not found in products table: {e}")
            total_products = db.session.execute(sa.text("SELECT COUNT(*) FROM products")).scalar()
        
        try:
            total_employees = db.session.execute(
                sa.text("SELECT COUNT(*) FROM employees WHERE user_id = :user_id"),
                {'user_id': int(user_id)}
            ).scalar()
        except Exception as e:
            print(f"Warning: user_id column not found in employees table: {e}")
            total_employees = db.session.execute(sa.text("SELECT COUNT(*) FROM employees")).scalar()

        # Get recent activities (last 7 days)
        recent_activities = []
        
        # Recent contacts - FILTERED BY USER (using direct SQL queries)
        try:
            recent_contacts = db.session.execute(
                sa.text("SELECT first_name, last_name, type, created_at FROM contacts WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 3"),
                {'user_id': int(user_id)}
            ).fetchall()
        except Exception as e:
            print(f"Warning: user_id column not found in contacts table for recent activities: {e}")
            recent_contacts = db.session.execute(
                sa.text("SELECT first_name, last_name, type, created_at FROM contacts ORDER BY created_at DESC LIMIT 3")
            ).fetchall()
        
        for contact in recent_contacts:
            recent_activities.append({
                'type': 'customer',
                'message': f'New {contact.type} added: {contact.first_name} {contact.last_name}',
                'time': contact.created_at.strftime('%Y-%m-%d %H:%M') if contact.created_at else 'Unknown'
            })

        # Recent products - FILTERED BY USER (using direct SQL queries)
        try:
            recent_products = db.session.execute(
                sa.text("SELECT name, created_at FROM products WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 3"),
                {'user_id': int(user_id)}
            ).fetchall()
        except Exception as e:
            print(f"Warning: user_id column not found in products table for recent activities: {e}")
            recent_products = db.session.execute(
                sa.text("SELECT name, created_at FROM products ORDER BY created_at DESC LIMIT 3")
            ).fetchall()
        
        for product in recent_products:
            recent_activities.append({
                'type': 'product',
                'message': f'New product added: {product.name}',
                'time': product.created_at.strftime('%Y-%m-%d %H:%M') if product.created_at else 'Unknown'
            })

        # Recent journal entries - FILTERED BY USER (using direct SQL queries)
        recent_entries = db.session.execute(
            sa.text("SELECT reference, created_at FROM journal_entries WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 3"),
            {'user_id': int(user_id)}
        ).fetchall()
        
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
