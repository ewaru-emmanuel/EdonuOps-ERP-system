from app import db
from datetime import datetime

class SecurityRole(db.Model):
    """Security roles for granular permissions"""
    __tablename__ = 'security_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    role_type = db.Column(db.String(50), default='custom')  # system, custom, inherited
    parent_role_id = db.Column(db.Integer, db.ForeignKey('security_roles.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_role = db.relationship('SecurityRole', remote_side=[id], backref='child_roles')
    permissions = db.relationship('RolePermission', backref='role', lazy=True, cascade='all, delete-orphan')
    user_roles = db.relationship('UserRole', backref='security_role', lazy=True)

class Permission(db.Model):
    """System permissions"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    module = db.Column(db.String(100), nullable=False)  # finance, crm, inventory, etc.
    resource = db.Column(db.String(100), nullable=False)  # customer, invoice, product, etc.
    action = db.Column(db.String(100), nullable=False)  # create, read, update, delete, approve
    permission_type = db.Column(db.String(50), default='object')  # object, field, row
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    role_permissions = db.relationship('RolePermission', backref='permission', lazy=True)

class RolePermission(db.Model):
    """Role-permission assignments"""
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('security_roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    granted = db.Column(db.Boolean, default=True)
    conditions = db.Column(db.JSON)  # Store permission conditions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),)

class UserRole(db.Model):
    """User-role assignments"""
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('security_roles.id'), nullable=False)
    entity_id = db.Column(db.Integer)  # For entity-specific roles
    entity_type = db.Column(db.String(100))  # For entity-specific roles
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    granted_by_user = db.relationship('User', foreign_keys=[granted_by])
    
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', 'entity_id', name='uq_user_role'),)

class RowLevelSecurity(db.Model):
    """Row-level security policies"""
    __tablename__ = 'row_level_security'
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)
    policy_name = db.Column(db.String(100), nullable=False)
    policy_type = db.Column(db.String(50), nullable=False)  # select, insert, update, delete
    condition_expression = db.Column(db.Text, nullable=False)  # SQL condition
    roles = db.Column(db.JSON)  # Roles this policy applies to
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ColumnLevelSecurity(db.Model):
    """Column-level security policies"""
    __tablename__ = 'column_level_security'
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)
    column_name = db.Column(db.String(100), nullable=False)
    policy_name = db.Column(db.String(100), nullable=False)
    roles = db.Column(db.JSON)  # Roles that can access this column
    masking_type = db.Column(db.String(50))  # none, partial, full, custom
    masking_expression = db.Column(db.Text)  # Custom masking expression
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityAuditLog(db.Model):
    """Comprehensive security audit trail"""
    __tablename__ = 'security_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(100))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(100))  # table, file, api, etc.
    resource_id = db.Column(db.String(100))
    resource_name = db.Column(db.String(200))
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(200))
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    audit_metadata = db.Column(db.JSON)  # Additional audit metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])

class SecuritySession(db.Model):
    """User security sessions"""
    __tablename__ = 'security_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(200))
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    session_data = db.Column(db.JSON)  # Store session data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])

class SecurityIncident(db.Model):
    """Security incident tracking"""
    __tablename__ = 'security_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_type = db.Column(db.String(100), nullable=False)  # unauthorized_access, data_breach, suspicious_activity
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    affected_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    affected_resource = db.Column(db.String(200))
    incident_data = db.Column(db.JSON)  # Store incident details
    status = db.Column(db.String(50), default='open')  # open, investigating, resolved, closed
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    affected_user = db.relationship('User', foreign_keys=[affected_user_id])
    assigned_user = db.relationship('User', foreign_keys=[assigned_to])

class ComplianceCertification(db.Model):
    """Compliance certifications and standards"""
    __tablename__ = 'compliance_certifications'
    
    id = db.Column(db.Integer, primary_key=True)
    certification_name = db.Column(db.String(200), nullable=False)  # SOC2, ISO27001, GDPR, etc.
    certification_type = db.Column(db.String(100), nullable=False)  # security, privacy, quality, etc.
    version = db.Column(db.String(50))
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, certified, expired
    certification_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    certifying_body = db.Column(db.String(200))
    certificate_number = db.Column(db.String(100))
    scope = db.Column(db.Text)  # Scope of certification
    requirements = db.Column(db.JSON)  # Store certification requirements
    evidence = db.Column(db.JSON)  # Store compliance evidence
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityPolicy(db.Model):
    """Security policies and procedures"""
    __tablename__ = 'security_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String(200), nullable=False)
    policy_type = db.Column(db.String(100), nullable=False)  # password, access, data, network
    version = db.Column(db.String(50), default='1.0')
    status = db.Column(db.String(50), default='draft')  # draft, active, deprecated
    content = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.JSON)  # Store policy requirements
    enforcement_level = db.Column(db.String(50), default='recommended')  # recommended, required, mandatory
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    effective_date = db.Column(db.Date)

class DataClassification(db.Model):
    """Data classification and handling"""
    __tablename__ = 'data_classifications'
    
    id = db.Column(db.Integer, primary_key=True)
    classification_level = db.Column(db.String(50), nullable=False)  # public, internal, confidential, restricted
    description = db.Column(db.Text)
    handling_requirements = db.Column(db.JSON)  # Store handling requirements
    retention_period = db.Column(db.Integer)  # Days
    encryption_required = db.Column(db.Boolean, default=False)
    access_controls = db.Column(db.JSON)  # Store access control requirements
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EncryptionKey(db.Model):
    """Encryption key management"""
    __tablename__ = 'encryption_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(100), nullable=False)
    key_type = db.Column(db.String(50), nullable=False)  # aes, rsa, etc.
    key_size = db.Column(db.Integer)  # Key size in bits
    key_purpose = db.Column(db.String(100))  # data_encryption, api_encryption, etc.
    key_status = db.Column(db.String(50), default='active')  # active, inactive, expired, compromised
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    rotation_date = db.Column(db.DateTime)
    key_metadata = db.Column(db.JSON)  # Store key metadata

class SecurityMonitoring(db.Model):
    """Security monitoring and alerts"""
    __tablename__ = 'security_monitoring'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(100), nullable=False)  # failed_login, suspicious_activity, data_access
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    alert_data = db.Column(db.JSON)  # Store alert details
    status = db.Column(db.String(50), default='new')  # new, acknowledged, investigating, resolved
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_user = db.relationship('User', foreign_keys=[assigned_to])

class SecurityTraining(db.Model):
    """Security training and awareness"""
    __tablename__ = 'security_training'
    
    id = db.Column(db.Integer, primary_key=True)
    training_name = db.Column(db.String(200), nullable=False)
    training_type = db.Column(db.String(100), nullable=False)  # awareness, technical, compliance
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer)
    required_frequency = db.Column(db.String(50))  # once, annually, quarterly
    target_roles = db.Column(db.JSON)  # Roles that need this training
    content_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserTraining(db.Model):
    """User training records"""
    __tablename__ = 'user_training'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    training_id = db.Column(db.Integer, db.ForeignKey('security_training.id'), nullable=False)
    status = db.Column(db.String(50), default='assigned')  # assigned, in_progress, completed, overdue
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    score = db.Column(db.Float)  # Training completion score
    certificate_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    training = db.relationship('SecurityTraining', foreign_keys=[training_id])

# User model is defined in core.models
