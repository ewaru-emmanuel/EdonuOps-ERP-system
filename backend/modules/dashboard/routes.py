from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.dashboard.models import Dashboard, DashboardWidget, WidgetTemplate, DashboardTemplate

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# Sample data
dashboards = []
dashboard_widgets = []
widget_templates = []
dashboard_templates = []

@bp.route('/dashboards', methods=['GET'])
def get_dashboards():
    """Get user dashboards"""
    user_id = request.args.get('user_id', type=int)
    filtered_dashboards = dashboards
    if user_id:
        filtered_dashboards = [d for d in dashboards if d.get('user_id') == user_id]
    return jsonify(filtered_dashboards)

@bp.route('/dashboards', methods=['POST'])
def create_dashboard():
    """Create a new dashboard"""
    data = request.get_json()
    new_dashboard = {
        "id": len(dashboards) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "user_id": data.get('user_id'),
        "is_shared": data.get('is_shared', False),
        "is_default": data.get('is_default', False),
        "layout": data.get('layout', {}),
        "settings": data.get('settings', {}),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    dashboards.append(new_dashboard)
    return jsonify(new_dashboard), 201

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
