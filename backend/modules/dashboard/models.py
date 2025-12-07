from app import db
from datetime import datetime

class UserModules(db.Model):
    """User module activation and permissions"""
    __tablename__ = 'user_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.String(50), nullable=False)  # 'finance', 'crm', 'inventory', etc.
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenants.id'), nullable=False, default='default_tenant')
    is_active = db.Column(db.Boolean, default=True)
    is_enabled = db.Column(db.Boolean, default=True)
    permissions = db.Column(db.JSON)  # Store module-specific permissions
    activated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deactivated_at = db.Column(db.DateTime)
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
    def _get_or_create_default_tenant(cls):
        """Get or create default tenant for single-user installations"""
        from modules.core.tenant_models import Tenant
        default_tenant = Tenant.query.filter_by(id='default_tenant').first()
        if not default_tenant:
            print('➕ Creating default_tenant...')
            default_tenant = Tenant(
                id='default_tenant',
                name='Default Tenant',
                domain='default.localhost',  # Required field
                subscription_plan='free',
                status='active'
            )
            db.session.add(default_tenant)
            try:
                db.session.commit()
                print('✅ Created default_tenant')
            except Exception as e:
                db.session.rollback()
                print(f'⚠️ Error creating default_tenant (might already exist): {e}')
                # Try to fetch again in case it was created by another process
                default_tenant = Tenant.query.filter_by(id='default_tenant').first()
                if not default_tenant:
                    raise
        return default_tenant.id
    
    @classmethod
    def enable_module(cls, user_id, module_id, permissions=None):
        """Enable a module for a user"""
        try:
            print(f'🔍 enable_module called: user_id={user_id}, module_id={module_id}')
            
            # Ensure default tenant exists
            tenant_id = cls._get_or_create_default_tenant()
            print(f'🏢 Using tenant_id: {tenant_id}')
            
            existing = cls.query.filter_by(user_id=user_id, module_id=module_id).first()
            
            if existing:
                # Update existing record
                print(f'📝 Updating existing module record: id={existing.id}')
                existing.is_active = True
                existing.is_enabled = True
                existing.permissions = permissions or existing.permissions
                existing.tenant_id = tenant_id  # Ensure tenant_id is set
                existing.updated_at = datetime.utcnow()
                if not existing.activated_at:
                    existing.activated_at = datetime.utcnow()
                db.session.commit()
                print(f'✅ Updated module record: id={existing.id}, is_active={existing.is_active}, is_enabled={existing.is_enabled}')
                return existing
            else:
                # Create new record
                print(f'➕ Creating new module record: user_id={user_id}, module_id={module_id}, tenant_id={tenant_id}')
                user_module = cls(
                    user_id=user_id,
                    module_id=module_id,
                    tenant_id=tenant_id,
                    is_active=True,
                    is_enabled=True,
                    permissions=permissions
                )
                db.session.add(user_module)
                db.session.commit()
                print(f'✅ Created module record: id={user_module.id}, is_active={user_module.is_active}, is_enabled={user_module.is_enabled}')
                return user_module
        except Exception as e:
            print(f'❌ Error in enable_module: {str(e)}')
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise
    
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
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
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
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DashboardTemplate {self.name}>'