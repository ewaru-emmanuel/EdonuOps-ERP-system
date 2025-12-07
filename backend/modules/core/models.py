from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Enhanced profile fields
    tenant_id = db.Column(db.String(50), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    mobile_number = db.Column(db.String(20), nullable=True)
    middle_name = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    profile_picture_url = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    
    # Professional information
    job_title = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    employee_id = db.Column(db.String(50), nullable=True)
    manager_id = db.Column(db.Integer, nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    employment_type = db.Column(db.String(50), nullable=True)
    work_location = db.Column(db.String(100), nullable=True)
    
    # Company information
    company_name = db.Column(db.String(200), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    company_website = db.Column(db.String(255), nullable=True)
    company_address = db.Column(db.Text, nullable=True)
    company_phone = db.Column(db.String(20), nullable=True)
    company_email = db.Column(db.String(255), nullable=True)
    
    # Address information
    address_line1 = db.Column(db.String(255), nullable=True)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    
    # Emergency contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    emergency_contact_relationship = db.Column(db.String(50), nullable=True)
    
    # Onboarding and preferences
    onboarding_completed = db.Column(db.Boolean, default=False)
    onboarding_step = db.Column(db.Integer, default=0)
    onboarding_started_at = db.Column(db.DateTime, nullable=True)
    onboarding_completed_at = db.Column(db.DateTime, nullable=True)
    profile_completion_percentage = db.Column(db.Integer, default=0)
    last_profile_update = db.Column(db.DateTime, nullable=True)
    
    # Soft delete fields
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, nullable=True)
    deletion_reason = db.Column(db.Text, nullable=True)
    
    # Relationship
    role = db.relationship('Role', backref='users')
    
    def __repr__(self):
        return f'<User {self.username}>'

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=True)  # Made nullable for section-based approach
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # New columns for section-based settings
    section = db.Column(db.String(100), index=True)  # Section name (currency, tax, etc.)
    data = db.Column(db.JSON)  # JSON data for section settings
    version = db.Column(db.Integer, default=1)  # Version for optimistic concurrency
    
    # Tenant-centric architecture: tenant_id for company-wide settings, user_id for audit trail
    tenant_id = db.Column(db.String(50), nullable=True, index=True)  # Company/tenant identifier - direct lookup
    last_modified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin who last modified (audit trail)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        if self.section:
            return f'<SystemSetting section={self.section}>'
        return f'<SystemSetting {self.setting_key}>'

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text)  # JSON string of permissions
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Role {self.role_name}>'

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
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenants.id'), nullable=False, default='default_tenant')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure one data type per user (unique constraint)
    __table_args__ = (db.UniqueConstraint('user_id', 'data_type', name='unique_user_data_type'),)
    
    def __repr__(self):
        return f'<UserData {self.user_id}:{self.data_type}>'
    
    @classmethod
    def _get_or_create_default_tenant(cls):
        """Get or create default tenant for single-user installations"""
        from modules.core.tenant_models import Tenant
        default_tenant = Tenant.query.filter_by(id='default_tenant').first()
        if not default_tenant:
            print('➕ Creating default_tenant for user_data...')
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
                print('✅ Created default_tenant for user_data')
            except Exception as e:
                db.session.rollback()
                print(f'⚠️ Error creating default_tenant (might already exist): {e}')
                # Try to fetch again in case it was created by another process
                default_tenant = Tenant.query.filter_by(id='default_tenant').first()
                if not default_tenant:
                    raise
        return default_tenant.id
    
    @classmethod
    def save_user_data(cls, user_id, data_type, data):
        """Save or update user data"""
        import json
        
        # Ensure default tenant exists
        tenant_id = cls._get_or_create_default_tenant()
        
        # Convert data to JSON string
        data_json = json.dumps(data) if not isinstance(data, str) else data
        
        # Check if data already exists
        existing = cls.query.filter_by(user_id=user_id, data_type=data_type).first()
        
        if existing:
            # Update existing
            existing.data = data_json
            existing.tenant_id = tenant_id  # Ensure tenant_id is set
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            existing = cls(
                user_id=user_id, 
                data_type=data_type, 
                data=data_json,
                tenant_id=tenant_id
            )
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