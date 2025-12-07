from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.dashboard.models import Dashboard, DashboardWidget, WidgetTemplate, DashboardTemplate, UserModules
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.core.tenant_sql_helper import tenant_sql_scalar

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/summary', methods=['GET', 'OPTIONS'])
@jwt_required()
def dashboard_summary():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        # SECURITY: Get tenant_id from verified JWT token
        from flask_jwt_extended import get_jwt_identity
        from modules.core.tenant_helpers import get_current_user_tenant_id
        
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Authentication required', 'message': 'User identity not found in JWT token'}), 401
        
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID in token'}), 400
        
        # Get tenant_id for tenant-centric filtering
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            # Fallback for development
            tenant_id = 'default'
        
        # Get real tenant-specific dashboard metrics (tenant-centric isolation)
        import sqlalchemy as sa
        from modules.finance.models import JournalEntry, JournalLine, Account
        
        # SECURITY: Calculate total revenue filtered by tenant_id (tenant-centric isolation)
        try:
            revenue_query = db.session.query(
                sa.func.sum(JournalLine.credit_amount).label('total_revenue')
            ).join(JournalEntry).join(Account).filter(
                Account.type == 'revenue',
                JournalEntry.tenant_id == tenant_id  # Tenant-centric isolation
            ).scalar()
            total_revenue = float(revenue_query) if revenue_query else 0.0
        except Exception as e:
            print(f"Warning: Could not query revenue with tenant_id: {e}")
            total_revenue = 0.0

        # Get counts from database using direct SQL queries with proper tenant isolation
        # Try to get counts with tenant_id filter, fallback to 0 if table doesn't exist
        
        try:
            total_customers = tenant_sql_scalar(
                "SELECT COUNT(*) FROM contacts WHERE type = 'customer' AND tenant_id = :tenant_id"
            )
        except Exception as e:
            print(f"Warning: Could not query contacts table with tenant_id: {e}")
            db.session.rollback()
            total_customers = 0
        
        try:
            total_leads = tenant_sql_scalar(
                "SELECT COUNT(*) FROM leads WHERE tenant_id = :tenant_id"
            )
        except Exception as e:
            print(f"Warning: Could not query leads table with tenant_id: {e}")
            db.session.rollback()
            total_leads = 0
        
        try:
            total_opportunities = tenant_sql_scalar(
                "SELECT COUNT(*) FROM opportunities WHERE tenant_id = :tenant_id"
            )
        except Exception as e:
            print(f"Warning: Could not query opportunities table with tenant_id: {e}")
            db.session.rollback()
            total_opportunities = 0
        
        try:
            total_products = tenant_sql_scalar(
                "SELECT COUNT(*) FROM products WHERE tenant_id = :tenant_id"
            )
        except Exception as e:
            print(f"Warning: Could not query products table with tenant_id: {e}")
            db.session.rollback()
            total_products = 0
        
        try:
            total_employees = tenant_sql_scalar(
                "SELECT COUNT(*) FROM employees WHERE tenant_id = :tenant_id"
            )
        except Exception as e:
            print(f"Warning: Could not query employees table with tenant_id: {e}")
            db.session.rollback()
            total_employees = 0

        # Recent activities - query tables with tenant_id
        recent_activities = []
        
        # Recent contacts (tenant-centric)
        try:
            from modules.core.tenant_sql_helper import tenant_sql_fetchall
            recent_contacts = tenant_sql_fetchall(
                "SELECT first_name, last_name, type, created_at FROM contacts WHERE tenant_id = :tenant_id ORDER BY created_at DESC LIMIT 3"
            )
            
            for contact in recent_contacts:
                recent_activities.append({
                    'type': 'customer',
                    'message': f'New {contact.type} added: {contact.first_name} {contact.last_name}',
                    'time': str(contact.created_at) if contact.created_at else 'Unknown'
                })
        except Exception as e:
            print(f"Warning: Could not query recent contacts: {e}")
            db.session.rollback()

        # Recent products (tenant-centric)
        try:
            recent_products = tenant_sql_fetchall(
                "SELECT name, created_at FROM products WHERE tenant_id = :tenant_id ORDER BY created_at DESC LIMIT 3"
            )
            
            for product in recent_products:
                recent_activities.append({
                    'type': 'product',
                    'message': f'New product added: {product.name}',
                    'time': str(product.created_at) if product.created_at else 'Unknown'
                })
        except Exception as e:
            print(f"Warning: Could not query recent products: {e}")
            db.session.rollback()

        # Recent journal entries (tenant-centric)
        try:
            recent_entries = tenant_sql_fetchall(
                "SELECT reference, created_at FROM journal_entries WHERE tenant_id = :tenant_id ORDER BY created_at DESC LIMIT 3"
            )
            
            for entry in recent_entries:
                recent_activities.append({
                    'type': 'finance',
                    'message': f'Journal entry created: {entry.reference}',
                    'time': str(entry.created_at) if entry.created_at else 'Unknown'
                })
        except Exception as e:
            print(f"Warning: Could not query recent journal entries: {e}")
            db.session.rollback()

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
@jwt_required()
def get_dashboards():
    """Get user dashboards - JWT REQUIRED"""
    # SECURITY: Get user ID from verified JWT token only
    user_id_str = get_jwt_identity()
    
    if not user_id_str:
        return jsonify({
            'error': 'Authentication required',
            'message': 'User identity not found in JWT token'
        }), 401
    
    # Convert to int (JWT identity is stored as string)
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid user ID in token'}), 400
    
    # STRICT USER ISOLATION: Get dashboards from database - filter by user_id only
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
@jwt_required()
def create_dashboard():
    """Create a new dashboard - JWT REQUIRED"""
    # SECURITY: Get user ID from verified JWT token only
    user_id_str = get_jwt_identity()
    
    if not user_id_str:
        return jsonify({
            'status': 'error',
            'message': 'User identity not found in JWT token'
        }), 401
    
    # Convert to int (JWT identity is stored as string)
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid user ID in token'}), 400
    
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
