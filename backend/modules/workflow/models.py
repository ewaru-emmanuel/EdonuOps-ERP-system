from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class WorkflowRule(db.Model):
    __tablename__ = 'workflow_rules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    trigger_type = db.Column(db.String(50), nullable=False)  # create, update, delete, status_change
    entity_type = db.Column(db.String(50), nullable=False)  # lead, contact, opportunity, task, po, etc.
    conditions = db.Column(JSON)  # JSON structure for conditions
    actions = db.Column(JSON)  # JSON structure for actions
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)  # Higher priority rules execute first
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowExecution(db.Model):
    __tablename__ = 'workflow_executions'
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('workflow_rules.id'), nullable=False)
    trigger_type = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    trigger_data = db.Column(JSON)  # Data that triggered the workflow
    execution_status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rule = db.relationship('WorkflowRule', backref='executions')

class WorkflowAction(db.Model):
    __tablename__ = 'workflow_actions'
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.Integer, db.ForeignKey('workflow_executions.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # assign, notify, create, update, etc.
    action_data = db.Column(JSON)  # Data for the action
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    result = db.Column(JSON)  # Result of the action
    error_message = db.Column(db.Text)
    executed_at = db.Column(db.DateTime)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    execution = db.relationship('WorkflowExecution', backref='actions')

class WorkflowTemplate(db.Model):
    __tablename__ = 'workflow_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # crm, finance, procurement, etc.
    template_data = db.Column(JSON)  # JSON structure for the template
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
