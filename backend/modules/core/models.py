from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSetting {self.setting_key}>'

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text)  # JSON string of permissions
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Organization {self.name}>'

class UserData(db.Model):
    """Store user-specific data like business profile, COA template, etc."""
    __tablename__ = 'user_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_type = db.Column(db.String(100), nullable=False)  # e.g., 'business_profile', 'coa_template', 'organization_setup'
    data = db.Column(db.Text, nullable=False)  # JSON string of the actual data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure one data type per user (unique constraint)
    __table_args__ = (db.UniqueConstraint('user_id', 'data_type', name='unique_user_data_type'),)
    
    def __repr__(self):
        return f'<UserData {self.user_id}:{self.data_type}>'
    
    @classmethod
    def save_user_data(cls, user_id, data_type, data):
        """Save or update user data"""
        import json
        
        # Convert data to JSON string
        data_json = json.dumps(data) if not isinstance(data, str) else data
        
        # Check if data already exists
        existing = cls.query.filter_by(user_id=user_id, data_type=data_type).first()
        
        if existing:
            # Update existing
            existing.data = data_json
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            existing = cls(user_id=user_id, data_type=data_type, data=data_json)
            db.session.add(existing)
        
        db.session.commit()
        return existing
    
    @classmethod
    def load_user_data(cls, user_id, data_type):
        """Load user data by type"""
        import json
        
        record = cls.query.filter_by(user_id=user_id, data_type=data_type).first()
        if record:
            try:
                return json.loads(record.data)
            except json.JSONDecodeError:
                return record.data  # Return as string if not valid JSON
        return None
    
    @classmethod
    def get_all_user_data(cls, user_id):
        """Get all data for a user"""
        import json
        
        records = cls.query.filter_by(user_id=user_id).all()
        result = {}
        
        for record in records:
            try:
                result[record.data_type] = json.loads(record.data)
            except json.JSONDecodeError:
                result[record.data_type] = record.data  # Return as string if not valid JSON
        
        return result
    
    @classmethod
    def delete_user_data(cls, user_id, data_type):
        """Delete specific user data"""
        record = cls.query.filter_by(user_id=user_id, data_type=data_type).first()
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False
    
    @classmethod
    def clear_all_user_data(cls, user_id):
        """Clear all data for a user"""
        records = cls.query.filter_by(user_id=user_id).all()
        count = len(records)
        for record in records:
            db.session.delete(record)
        db.session.commit()
        return count