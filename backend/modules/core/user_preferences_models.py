"""
User Preferences Models
Stores user-specific module configurations and preferences
"""

from app import db
from datetime import datetime
from sqlalchemy import Index

class UserPreferences(db.Model):
    """User-specific preferences and module configurations"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, unique=True)
    
    # Module configurations
    selected_modules = db.Column(db.Text)  # JSON string of selected modules
    module_settings = db.Column(db.Text)   # JSON string of module-specific settings
    
    # Dashboard preferences
    dashboard_layout = db.Column(db.Text)  # JSON string of dashboard layout
    default_currency = db.Column(db.String(10), default='USD')
    timezone = db.Column(db.String(50), default='UTC')
    date_format = db.Column(db.String(20), default='YYYY-MM-DD')
    
    # UI preferences
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # Business context
    industry = db.Column(db.String(100))
    business_size = db.Column(db.String(50))
    company_name = db.Column(db.String(200))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_preferences_user_id', 'user_id'),
    )
    
    def __repr__(self):
        return f'<UserPreferences {self.user_id}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'selected_modules': self.get_selected_modules(),
            'module_settings': self.get_module_settings(),
            'dashboard_layout': self.get_dashboard_layout(),
            'default_currency': self.default_currency,
            'timezone': self.timezone,
            'date_format': self.date_format,
            'theme': self.theme,
            'language': self.language,
            'notifications_enabled': self.notifications_enabled,
            'industry': self.industry,
            'business_size': self.business_size,
            'company_name': self.company_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_selected_modules(self):
        """Get selected modules as list"""
        import json
        try:
            return json.loads(self.selected_modules) if self.selected_modules else []
        except:
            return []
    
    def set_selected_modules(self, modules):
        """Set selected modules from list"""
        import json
        self.selected_modules = json.dumps(modules)
    
    def get_module_settings(self):
        """Get module settings as dict"""
        import json
        try:
            return json.loads(self.module_settings) if self.module_settings else {}
        except:
            return {}
    
    def set_module_settings(self, settings):
        """Set module settings from dict"""
        import json
        self.module_settings = json.dumps(settings)
    
    def get_dashboard_layout(self):
        """Get dashboard layout as dict"""
        import json
        try:
            return json.loads(self.dashboard_layout) if self.dashboard_layout else {}
        except:
            return {}
    
    def set_dashboard_layout(self, layout):
        """Set dashboard layout from dict"""
        import json
        self.dashboard_layout = json.dumps(layout)
    
    @classmethod
    def get_user_preferences(cls, user_id):
        """Get user preferences by user ID"""
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def create_or_update(cls, user_id, **kwargs):
        """Create or update user preferences"""
        preferences = cls.get_user_preferences(user_id)
        
        if not preferences:
            preferences = cls(user_id=user_id)
            db.session.add(preferences)
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(preferences, key):
                if key == 'selected_modules' and isinstance(value, list):
                    preferences.set_selected_modules(value)
                elif key == 'module_settings' and isinstance(value, dict):
                    preferences.set_module_settings(value)
                elif key == 'dashboard_layout' and isinstance(value, dict):
                    preferences.set_dashboard_layout(value)
                else:
                    setattr(preferences, key, value)
        
        preferences.updated_at = datetime.utcnow()
        db.session.commit()
        return preferences











