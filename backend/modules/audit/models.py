from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, view, export, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # contact, lead, invoice, po, etc.
    entity_id = db.Column(db.Integer)  # ID of the affected entity
    old_values = db.Column(JSON)  # Previous values (for updates)
    new_values = db.Column(JSON)  # New values
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))  # Browser/application info
    session_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    additional_data = db.Column(JSON)  # Any additional context data

class AuditLogFilter(db.Model):
    __tablename__ = 'audit_log_filters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filter_criteria = db.Column(JSON)  # JSON structure for filter criteria
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLogExport(db.Model):
    __tablename__ = 'audit_log_exports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    export_name = db.Column(db.String(100), nullable=False)
    filter_criteria = db.Column(JSON)  # JSON structure for export filter
    file_path = db.Column(db.String(500))  # Path to exported file
    file_size = db.Column(db.Integer)  # File size in bytes
    export_format = db.Column(db.String(20), default='csv')  # csv, excel, pdf
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    total_records = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
