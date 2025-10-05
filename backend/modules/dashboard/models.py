from app import db
from datetime import datetime

class UserModules(db.Model):
    """User module activation and permissions"""
    __tablename__ = 'user_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.String(50), nullable=False)  # 'finance', 'crm', 'inventory', etc.
    is_active = db.Column(db.Boolean, default=True)
    is_enabled = db.Column(db.Boolean, default=True)
    permissions = db.Column(db.JSON)  # Store module-specific permissions
    activated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deactivated_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)  # Standardized user identification)  # User who activated this
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate user-module combinations
    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_id', name='unique_user_module'),
    )
    
    def __repr__(self):
        return f'<UserModules {self.user_id}:{self.module_id}>'
    
    @classmethod
    def get_user_modules(cls, user_id):
        """Get all active modules for a user"""
        return cls.query.filter_by(user_id=user_id, is_active=True, is_enabled=True).all()
    
    @classmethod
    def is_module_enabled(cls, user_id, module_id):
        """Check if a specific module is enabled for a user"""
        return cls.query.filter_by(
            user_id=user_id, 
            module_id=module_id, 
            is_active=True, 
            is_enabled=True
        ).first() is not None
    
    @classmethod
    def enable_module(cls, user_id, module_id, permissions=None, created_by=None):
        """Enable a module for a user"""
        existing = cls.query.filter_by(user_id=user_id, module_id=module_id).first()
        
        if existing:
            # Update existing record
            existing.is_active = True
            existing.is_enabled = True
            existing.permissions = permissions or existing.permissions
            existing.updated_at = datetime.utcnow()
            if not existing.activated_at:
                existing.activated_at = datetime.utcnow()
            db.session.commit()
            return existing
        else:
            # Create new record
            user_module = cls(
                user_id=user_id,
                module_id=module_id,
                is_active=True,
                is_enabled=True,
                permissions=permissions,
                created_by=created_by or user_id
            )
            db.session.add(user_module)
            db.session.commit()
            return user_module
    
    @classmethod
    def disable_module(cls, user_id, module_id):
        """Disable a module for a user"""
        user_module = cls.query.filter_by(user_id=user_id, module_id=module_id).first()
        if user_module:
            user_module.is_active = False
            user_module.is_enabled = False
            user_module.deactivated_at = datetime.utcnow()
            user_module.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False


class Dashboard(db.Model):
    """User dashboards"""
    __tablename__ = 'dashboards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    layout = db.Column(db.JSON)  # Dashboard layout configuration
    settings = db.Column(db.JSON)  # Dashboard settings
    is_shared = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Dashboard {self.name}>'


class DashboardWidget(db.Model):
    """Dashboard widgets"""
    __tablename__ = 'dashboard_widgets'
    
    id = db.Column(db.Integer, primary_key=True)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)  # 'chart', 'table', 'metric', etc.
    title = db.Column(db.String(200), nullable=False)
    config = db.Column(db.JSON)  # Widget configuration
    position = db.Column(db.JSON)  # Widget position and size
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DashboardWidget {self.title}>'


class WidgetTemplate(db.Model):
    """Widget templates for different modules"""
    __tablename__ = 'widget_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.String(50), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    config = db.Column(db.JSON)  # Default widget configuration
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WidgetTemplate {self.name}>'


class DashboardTemplate(db.Model):
    """Dashboard templates for different user types"""
    __tablename__ = 'dashboard_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_type = db.Column(db.String(50))  # 'admin', 'manager', 'user', etc.
    layout = db.Column(db.JSON)  # Template layout
    widgets = db.Column(db.JSON)  # Template widgets
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DashboardTemplate {self.name}>'