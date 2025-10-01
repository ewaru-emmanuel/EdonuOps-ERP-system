from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.dashboard.models import Dashboard, DashboardWidget, WidgetTemplate, DashboardTemplate, UserModules

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/summary', methods=['GET', 'OPTIONS'])
def dashboard_summary():
    if request.method == 'OPTIONS':
        return ('', 200)
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
        
        # If still no user_id, return empty summary (for development)
        if not user_id:
            print("Warning: No user context found for dashboard summary, returning empty results")
            return jsonify({
                'totalRevenue': 0,
                'totalCustomers': 0,
                'totalLeads': 0,
                'totalOpportunities': 0,
                'totalProducts': 0,
                'totalEmployees': 0,
                'recentActivity': [],
                'systemStatus': 'operational',
                'user_id': None
            }), 200
        
        # Get real user-specific dashboard metrics
        import sqlalchemy as sa
        from modules.finance.models import JournalEntry, JournalLine, Account
        
        # Calculate total revenue from journal entries (sum of credit amounts for revenue accounts)
        revenue_query = db.session.query(
            sa.func.sum(JournalLine.credit_amount).label('total_revenue')
        ).join(JournalEntry).join(Account).filter(
            Account.type == 'revenue',
            JournalEntry.user_id == int(user_id)
        ).scalar()
        total_revenue = float(revenue_query) if revenue_query else 0.0

        # Get counts from database using direct SQL queries
        total_customers = db.session.execute(
            sa.text("SELECT COUNT(*) FROM contacts WHERE type = 'customer' AND user_id = :user_id"),
            {'user_id': int(user_id)}
        ).scalar()
        
        total_leads = db.session.execute(
            sa.text("SELECT COUNT(*) FROM leads WHERE user_id = :user_id"),
            {'user_id': int(user_id)}
        ).scalar()
        
        total_opportunities = db.session.execute(
            sa.text("SELECT COUNT(*) FROM opportunities WHERE user_id = :user_id"),
            {'user_id': int(user_id)}
        ).scalar()
        
        total_products = db.session.execute(
            sa.text("SELECT COUNT(*) FROM products WHERE user_id = :user_id"),
            {'user_id': int(user_id)}
        ).scalar()
        
        total_employees = db.session.execute(
            sa.text("SELECT COUNT(*) FROM employees WHERE user_id = :user_id"),
            {'user_id': int(user_id)}
        ).scalar()

        # Get recent activities
        recent_activities = []
        
        # Recent contacts
        recent_contacts = db.session.execute(
            sa.text("SELECT first_name, last_name, type, created_at FROM contacts WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 3"),
            {'user_id': int(user_id)}
        ).fetchall()
        
        for contact in recent_contacts:
            recent_activities.append({
                'type': 'customer',
                'message': f'New {contact.type} added: {contact.first_name} {contact.last_name}',
                'time': str(contact.created_at) if contact.created_at else 'Unknown'
            })

        # Recent products
        recent_products = db.session.execute(
            sa.text("SELECT name, created_at FROM products WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 3"),
            {'user_id': int(user_id)}
        ).fetchall()
        
        for product in recent_products:
            recent_activities.append({
                'type': 'product',
                'message': f'New product added: {product.name}',
                'time': str(product.created_at) if product.created_at else 'Unknown'
            })

        # Recent journal entries
        recent_entries = db.session.execute(
            sa.text("SELECT reference, created_at FROM journal_entries WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 3"),
            {'user_id': int(user_id)}
        ).fetchall()
        
        for entry in recent_entries:
            recent_activities.append({
                'type': 'finance',
                'message': f'Journal entry created: {entry.reference}',
                'time': str(entry.created_at) if entry.created_at else 'Unknown'
            })

        # Sort activities by time
        recent_activities.sort(key=lambda x: x['time'], reverse=True)
        recent_activities = recent_activities[:5]

        summary = {
            'totalRevenue': total_revenue,
            'totalCustomers': total_customers,
            'totalLeads': total_leads,
            'totalOpportunities': total_opportunities,
            'totalProducts': total_products,
            'totalEmployees': total_employees,
            'recentActivity': recent_activities,
            'systemStatus': 'operational',
            'user_id': user_id
        }
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 200

@bp.route('/dashboards', methods=['GET'])
def get_dashboards():
    """Get user dashboards"""
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
        print("Warning: No user context found for dashboards, returning empty results")
        return jsonify([]), 200
    
    # Get dashboards from database - filter by user
    user_dashboards = Dashboard.query.filter_by(user_id=user_id, is_active=True).all()
    
    dashboards_data = []
    for dashboard in user_dashboards:
        dashboards_data.append({
            'id': dashboard.id,
            'name': dashboard.name,
            'description': dashboard.description,
            'layout': dashboard.layout,
            'settings': dashboard.settings,
            'is_shared': dashboard.is_shared,
            'is_default': dashboard.is_default,
            'is_active': dashboard.is_active,
            'created_at': dashboard.created_at.isoformat(),
            'updated_at': dashboard.updated_at.isoformat()
        })
    
    return jsonify(dashboards_data)

@bp.route('/dashboards', methods=['POST'])
def create_dashboard():
    """Create a new dashboard"""
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
    
    # Create dashboard in database
    new_dashboard = Dashboard(
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description'),
        layout=data.get('layout', {}),
        settings=data.get('settings', {}),
        is_shared=data.get('is_shared', False),
        is_default=data.get('is_default', False),
        is_active=data.get('is_active', True),
        created_by=user_id
    )
    
    db.session.add(new_dashboard)
    db.session.commit()
    
    return jsonify({
        'id': new_dashboard.id,
        'name': new_dashboard.name,
        'description': new_dashboard.description,
        'user_id': new_dashboard.user_id,
        'is_shared': new_dashboard.is_shared,
        'is_default': new_dashboard.is_default,
        'layout': new_dashboard.layout,
        'settings': new_dashboard.settings,
        'is_active': new_dashboard.is_active,
        'created_at': new_dashboard.created_at.isoformat()
    }), 201

@bp.route('/widgets', methods=['GET'])
def get_widgets():
    """Get dashboard widgets"""
    dashboard_id = request.args.get('dashboard_id', type=int)
    filtered_widgets = dashboard_widgets
    if dashboard_id:
        filtered_widgets = [w for w in dashboard_widgets if w.get('dashboard_id') == dashboard_id]
    return jsonify(filtered_widgets)

@bp.route('/widgets', methods=['POST'])
def create_widget():
    """Create a new dashboard widget"""
    data = request.get_json()
    new_widget = {
        "id": len(dashboard_widgets) + 1,
        "dashboard_id": data.get('dashboard_id'),
        "widget_type": data.get('widget_type'),
        "widget_name": data.get('widget_name'),
        "widget_config": data.get('widget_config', {}),
        "position": data.get('position', {}),
        "data_source": data.get('data_source'),
        "refresh_interval": data.get('refresh_interval', 0),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    dashboard_widgets.append(new_widget)
    return jsonify(new_widget), 201

@bp.route('/templates', methods=['GET'])
def get_templates():
    """Get dashboard templates"""
    category = request.args.get('category')
    filtered_templates = dashboard_templates
    if category:
        filtered_templates = [t for t in dashboard_templates if t.get('category') == category]
    return jsonify(filtered_templates)
