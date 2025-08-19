from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Dashboard(db.Model):
    __tablename__ = 'dashboards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_shared = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    layout = db.Column(JSON)  # JSON structure for dashboard layout
    settings = db.Column(JSON)  # JSON structure for dashboard settings
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DashboardWidget(db.Model):
    __tablename__ = 'dashboard_widgets'
    id = db.Column(db.Integer, primary_key=True)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)  # chart, table, metric, filter
    widget_name = db.Column(db.String(100), nullable=False)
    widget_config = db.Column(JSON)  # JSON configuration for the widget
    position = db.Column(JSON)  # JSON structure for widget position and size
    data_source = db.Column(db.String(100))  # Source of data for the widget
    refresh_interval = db.Column(db.Integer, default=0)  # Refresh interval in seconds (0 = manual)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dashboard = db.relationship('Dashboard', backref='widgets')

class WidgetTemplate(db.Model):
    __tablename__ = 'widget_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    widget_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))  # finance, crm, inventory, etc.
    template_config = db.Column(JSON)  # JSON configuration template
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DashboardTemplate(db.Model):
    __tablename__ = 'dashboard_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # finance, crm, inventory, etc.
    template_layout = db.Column(JSON)  # JSON structure for template layout
    default_widgets = db.Column(JSON)  # JSON array of default widgets
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
