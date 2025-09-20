from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from modules.security.models import (
    SecurityRole, Permission, RolePermission, UserRole, RowLevelSecurity,
    ColumnLevelSecurity, SecurityAuditLog, SecuritySession, SecurityIncident,
    ComplianceCertification, SecurityPolicy, DataClassification, EncryptionKey,
    SecurityMonitoring, SecurityTraining, UserTraining
)
import uuid

bp = Blueprint('enterprise_security', __name__, url_prefix='/api/security')

# Sample data for initial state
security_roles = []
permissions = []
role_permissions = []
user_roles = []
row_level_security = []
column_level_security = []
security_audit_logs = []
security_sessions = []
security_incidents = []
compliance_certifications = []
security_policies = []
data_classifications = []
encryption_keys = []
security_monitoring = []
security_training = []
user_training = []

# Security Role endpoints
@bp.route('/roles', methods=['GET'])
def get_security_roles():
    """Get all security roles"""
    role_type = request.args.get('role_type')
    is_active = request.args.get('is_active', type=bool)
    
    filtered_roles = security_roles
    if role_type:
        filtered_roles = [r for r in security_roles if r.get('role_type') == role_type]
    if is_active is not None:
        filtered_roles = [r for r in security_roles if r.get('is_active') == is_active]
    
    return jsonify(filtered_roles)

@bp.route('/roles', methods=['POST'])
def create_security_role():
    """Create a new security role"""
    data = request.get_json()
    
    new_role = {
        "id": len(security_roles) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "role_type": data.get('role_type', 'custom'),
        "parent_role_id": data.get('parent_role_id'),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    security_roles.append(new_role)
    return jsonify(new_role), 201

# Permission endpoints
@bp.route('/permissions', methods=['GET'])
def get_permissions():
    """Get all permissions"""
    module = request.args.get('module')
    resource = request.args.get('resource')
    
    filtered_permissions = permissions
    if module:
        filtered_permissions = [p for p in permissions if p.get('module') == module]
    if resource:
        filtered_permissions = [p for p in permissions if p.get('resource') == resource]
    
    return jsonify(filtered_permissions)

@bp.route('/permissions', methods=['POST'])
def create_permission():
    """Create a new permission"""
    data = request.get_json()
    
    new_permission = {
        "id": len(permissions) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "module": data.get('module'),
        "resource": data.get('resource'),
        "action": data.get('action'),
        "permission_type": data.get('permission_type', 'object'),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    permissions.append(new_permission)
    return jsonify(new_permission), 201

# Role Permission endpoints
@bp.route('/roles/<int:role_id>/permissions', methods=['GET'])
def get_role_permissions(role_id):
    """Get permissions for a specific role"""
    role_perms = [rp for rp in role_permissions if rp.get('role_id') == role_id]
    return jsonify(role_perms)

@bp.route('/roles/<int:role_id>/permissions', methods=['POST'])
def assign_permission_to_role(role_id):
    """Assign a permission to a role"""
    data = request.get_json()
    
    new_role_permission = {
        "id": len(role_permissions) + 1,
        "role_id": role_id,
        "permission_id": data.get('permission_id'),
        "granted": data.get('granted', True),
        "conditions": data.get('conditions', {}),
        "created_at": datetime.utcnow().isoformat()
    }
    
    role_permissions.append(new_role_permission)
    return jsonify(new_role_permission), 201

# User Role endpoints
@bp.route('/users/<int:user_id>/roles', methods=['GET'])
def get_user_roles(user_id):
    """Get roles for a specific user"""
    user_roles_list = [ur for ur in user_roles if ur.get('user_id') == user_id]
    return jsonify(user_roles_list)

@bp.route('/users/<int:user_id>/roles', methods=['POST'])
def assign_role_to_user(user_id):
    """Assign a role to a user"""
    data = request.get_json()
    
    new_user_role = {
        "id": len(user_roles) + 1,
        "user_id": user_id,
        "role_id": data.get('role_id'),
        "entity_id": data.get('entity_id'),
        "entity_type": data.get('entity_type'),
        "granted_at": datetime.utcnow().isoformat(),
        "granted_by": data.get('granted_by'),
        "expires_at": data.get('expires_at'),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    user_roles.append(new_user_role)
    return jsonify(new_user_role), 201

# Row Level Security endpoints
@bp.route('/row-level-security', methods=['GET'])
def get_row_level_security():
    """Get row level security policies"""
    table_name = request.args.get('table_name')
    
    filtered_policies = row_level_security
    if table_name:
        filtered_policies = [p for p in row_level_security if p.get('table_name') == table_name]
    
    return jsonify(filtered_policies)

@bp.route('/row-level-security', methods=['POST'])
def create_row_level_security():
    """Create a new row level security policy"""
    data = request.get_json()
    
    new_policy = {
        "id": len(row_level_security) + 1,
        "table_name": data.get('table_name'),
        "policy_name": data.get('policy_name'),
        "policy_type": data.get('policy_type'),
        "condition_expression": data.get('condition_expression'),
        "roles": data.get('roles', []),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    row_level_security.append(new_policy)
    return jsonify(new_policy), 201

# Column Level Security endpoints
@bp.route('/column-level-security', methods=['GET'])
def get_column_level_security():
    """Get column level security policies"""
    table_name = request.args.get('table_name')
    
    filtered_policies = column_level_security
    if table_name:
        filtered_policies = [p for p in column_level_security if p.get('table_name') == table_name]
    
    return jsonify(filtered_policies)

@bp.route('/column-level-security', methods=['POST'])
def create_column_level_security():
    """Create a new column level security policy"""
    data = request.get_json()
    
    new_policy = {
        "id": len(column_level_security) + 1,
        "table_name": data.get('table_name'),
        "column_name": data.get('column_name'),
        "policy_name": data.get('policy_name'),
        "roles": data.get('roles', []),
        "masking_type": data.get('masking_type', 'none'),
        "masking_expression": data.get('masking_expression'),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    column_level_security.append(new_policy)
    return jsonify(new_policy), 201

# Security Audit Log endpoints
@bp.route('/audit-logs', methods=['GET'])
def get_security_audit_logs():
    """Get security audit logs"""
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    
    filtered_logs = security_audit_logs
    if user_id:
        filtered_logs = [l for l in security_audit_logs if l.get('user_id') == user_id]
    if action:
        filtered_logs = [l for l in security_audit_logs if l.get('action') == action]
    if resource_type:
        filtered_logs = [l for l in security_audit_logs if l.get('resource_type') == resource_type]
    
    return jsonify(filtered_logs)

# Security Session endpoints
@bp.route('/sessions', methods=['GET'])
def get_security_sessions():
    """Get security sessions"""
    user_id = request.args.get('user_id', type=int)
    is_active = request.args.get('is_active', type=bool)
    
    filtered_sessions = security_sessions
    if user_id:
        filtered_sessions = [s for s in security_sessions if s.get('user_id') == user_id]
    if is_active is not None:
        filtered_sessions = [s for s in security_sessions if s.get('is_active') == is_active]
    
    return jsonify(filtered_sessions)

# Security Incident endpoints
@bp.route('/incidents', methods=['GET'])
def get_security_incidents():
    """Get security incidents"""
    severity = request.args.get('severity')
    status = request.args.get('status')
    
    filtered_incidents = security_incidents
    if severity:
        filtered_incidents = [i for i in security_incidents if i.get('severity') == severity]
    if status:
        filtered_incidents = [i for i in security_incidents if i.get('status') == status]
    
    return jsonify(filtered_incidents)

@bp.route('/incidents', methods=['POST'])
def create_security_incident():
    """Create a new security incident"""
    data = request.get_json()
    
    new_incident = {
        "id": len(security_incidents) + 1,
        "incident_type": data.get('incident_type'),
        "severity": data.get('severity'),
        "title": data.get('title'),
        "description": data.get('description'),
        "affected_user_id": data.get('affected_user_id'),
        "affected_resource": data.get('affected_resource'),
        "incident_data": data.get('incident_data', {}),
        "status": data.get('status', 'open'),
        "assigned_to": data.get('assigned_to'),
        "detected_at": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    security_incidents.append(new_incident)
    return jsonify(new_incident), 201

# Compliance Certification endpoints
@bp.route('/certifications', methods=['GET'])
def get_compliance_certifications():
    """Get compliance certifications"""
    certification_type = request.args.get('certification_type')
    status = request.args.get('status')
    
    filtered_certifications = compliance_certifications
    if certification_type:
        filtered_certifications = [c for c in compliance_certifications if c.get('certification_type') == certification_type]
    if status:
        filtered_certifications = [c for c in compliance_certifications if c.get('status') == status]
    
    return jsonify(filtered_certifications)

@bp.route('/certifications', methods=['POST'])
def create_compliance_certification():
    """Create a new compliance certification"""
    data = request.get_json()
    
    new_certification = {
        "id": len(compliance_certifications) + 1,
        "certification_name": data.get('certification_name'),
        "certification_type": data.get('certification_type'),
        "version": data.get('version'),
        "status": data.get('status', 'pending'),
        "certification_date": data.get('certification_date'),
        "expiry_date": data.get('expiry_date'),
        "certifying_body": data.get('certifying_body'),
        "certificate_number": data.get('certificate_number'),
        "scope": data.get('scope'),
        "requirements": data.get('requirements', {}),
        "evidence": data.get('evidence', {}),
        "created_at": datetime.utcnow().isoformat()
    }
    
    compliance_certifications.append(new_certification)
    return jsonify(new_certification), 201

# Security Policy endpoints
@bp.route('/policies', methods=['GET'])
def get_security_policies():
    """Get security policies"""
    policy_type = request.args.get('policy_type')
    status = request.args.get('status')
    
    filtered_policies = security_policies
    if policy_type:
        filtered_policies = [p for p in security_policies if p.get('policy_type') == policy_type]
    if status:
        filtered_policies = [p for p in security_policies if p.get('status') == status]
    
    return jsonify(filtered_policies)

@bp.route('/policies', methods=['POST'])
def create_security_policy():
    """Create a new security policy"""
    data = request.get_json()
    
    new_policy = {
        "id": len(security_policies) + 1,
        "policy_name": data.get('policy_name'),
        "policy_type": data.get('policy_type'),
        "version": data.get('version', '1.0'),
        "status": data.get('status', 'draft'),
        "content": data.get('content'),
        "requirements": data.get('requirements', {}),
        "enforcement_level": data.get('enforcement_level', 'recommended'),
        "effective_date": data.get('effective_date'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    security_policies.append(new_policy)
    return jsonify(new_policy), 201

# Data Classification endpoints
@bp.route('/data-classifications', methods=['GET'])
def get_data_classifications():
    """Get data classifications"""
    return jsonify(data_classifications)

@bp.route('/data-classifications', methods=['POST'])
def create_data_classification():
    """Create a new data classification"""
    data = request.get_json()
    
    new_classification = {
        "id": len(data_classifications) + 1,
        "classification_level": data.get('classification_level'),
        "description": data.get('description'),
        "handling_requirements": data.get('handling_requirements', {}),
        "retention_period": data.get('retention_period'),
        "encryption_required": data.get('encryption_required', False),
        "access_controls": data.get('access_controls', {}),
        "created_at": datetime.utcnow().isoformat()
    }
    
    data_classifications.append(new_classification)
    return jsonify(new_classification), 201

# Encryption Key endpoints
@bp.route('/encryption-keys', methods=['GET'])
def get_encryption_keys():
    """Get encryption keys"""
    key_purpose = request.args.get('key_purpose')
    key_status = request.args.get('key_status')
    
    filtered_keys = encryption_keys
    if key_purpose:
        filtered_keys = [k for k in encryption_keys if k.get('key_purpose') == key_purpose]
    if key_status:
        filtered_keys = [k for k in encryption_keys if k.get('key_status') == key_status]
    
    return jsonify(filtered_keys)

@bp.route('/encryption-keys', methods=['POST'])
def create_encryption_key():
    """Create a new encryption key"""
    data = request.get_json()
    
    new_key = {
        "id": len(encryption_keys) + 1,
        "key_name": data.get('key_name'),
        "key_type": data.get('key_type'),
        "key_size": data.get('key_size'),
        "key_purpose": data.get('key_purpose'),
        "key_status": data.get('key_status', 'active'),
        "expires_at": data.get('expires_at'),
        "rotation_date": data.get('rotation_date'),
        "metadata": data.get('metadata', {}),
        "created_at": datetime.utcnow().isoformat()
    }
    
    encryption_keys.append(new_key)
    return jsonify(new_key), 201

# Security Monitoring endpoints
@bp.route('/monitoring/alerts', methods=['GET'])
def get_security_alerts():
    """Get security monitoring alerts"""
    alert_type = request.args.get('alert_type')
    severity = request.args.get('severity')
    status = request.args.get('status')
    
    filtered_alerts = security_monitoring
    if alert_type:
        filtered_alerts = [a for a in security_monitoring if a.get('alert_type') == alert_type]
    if severity:
        filtered_alerts = [a for a in security_monitoring if a.get('severity') == severity]
    if status:
        filtered_alerts = [a for a in security_monitoring if a.get('status') == status]
    
    return jsonify(filtered_alerts)

# Security Training endpoints
@bp.route('/training', methods=['GET'])
def get_security_training():
    """Get security training programs"""
    training_type = request.args.get('training_type')
    
    filtered_training = security_training
    if training_type:
        filtered_training = [t for t in security_training if t.get('training_type') == training_type]
    
    return jsonify(filtered_training)

@bp.route('/training', methods=['POST'])
def create_security_training():
    """Create a new security training program"""
    data = request.get_json()
    
    new_training = {
        "id": len(security_training) + 1,
        "training_name": data.get('training_name'),
        "training_type": data.get('training_type'),
        "description": data.get('description'),
        "duration_minutes": data.get('duration_minutes'),
        "required_frequency": data.get('required_frequency'),
        "target_roles": data.get('target_roles', []),
        "content_url": data.get('content_url'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    security_training.append(new_training)
    return jsonify(new_training), 201

# User Training endpoints
@bp.route('/users/<int:user_id>/training', methods=['GET'])
def get_user_training(user_id):
    """Get training records for a specific user"""
    user_training_list = [ut for ut in user_training if ut.get('user_id') == user_id]
    return jsonify(user_training_list)

@bp.route('/users/<int:user_id>/training', methods=['POST'])
def assign_training_to_user(user_id):
    """Assign training to a user"""
    data = request.get_json()
    
    new_user_training = {
        "id": len(user_training) + 1,
        "user_id": user_id,
        "training_id": data.get('training_id'),
        "status": data.get('status', 'assigned'),
        "assigned_date": datetime.utcnow().isoformat(),
        "completed_date": data.get('completed_date'),
        "score": data.get('score'),
        "certificate_url": data.get('certificate_url'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    user_training.append(new_user_training)
    return jsonify(new_user_training), 201

# Analytics and Reporting endpoints
@bp.route('/analytics/security-summary', methods=['GET'])
def get_security_summary():
    """Get security summary analytics"""
    summary = {
        "total_roles": len(security_roles),
        "active_roles": len([r for r in security_roles if r.get('is_active')]),
        "total_permissions": len(permissions),
        "active_sessions": len([s for s in security_sessions if s.get('is_active')]),
        "open_incidents": len([i for i in security_incidents if i.get('status') == 'open']),
        "active_certifications": len([c for c in compliance_certifications if c.get('status') == 'certified']),
        "total_audit_logs": len(security_audit_logs),
        "security_score": 95.5  # Mock calculation
    }
    
    return jsonify(summary)

@bp.route('/analytics/incident-trends', methods=['GET'])
def get_incident_trends():
    """Get security incident trends"""
    trends = {
        "total_incidents": len(security_incidents),
        "incidents_by_severity": {
            "critical": len([i for i in security_incidents if i.get('severity') == 'critical']),
            "high": len([i for i in security_incidents if i.get('severity') == 'high']),
            "medium": len([i for i in security_incidents if i.get('severity') == 'medium']),
            "low": len([i for i in security_incidents if i.get('severity') == 'low'])
        },
        "incidents_by_type": {
            "unauthorized_access": len([i for i in security_incidents if i.get('incident_type') == 'unauthorized_access']),
            "data_breach": len([i for i in security_incidents if i.get('incident_type') == 'data_breach']),
            "suspicious_activity": len([i for i in security_incidents if i.get('incident_type') == 'suspicious_activity'])
        }
    }
    
    return jsonify(trends)

# Initialize sample data
def init_sample_data():
    """Initialize sample security data"""
    global security_roles, permissions, compliance_certifications, security_policies
    
    # Sample security roles
    security_roles.extend([
        {
            "id": 1,
            "name": "System Administrator",
            "description": "Full system access and administration",
            "role_type": "system",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "name": "Finance Manager",
            "description": "Finance module access with approval rights",
            "role_type": "custom",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample permissions
    permissions.extend([
        {
            "id": 1,
            "name": "finance.read",
            "description": "Read finance data",
            "module": "finance",
            "resource": "finance",
            "action": "read",
            "permission_type": "object",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "name": "finance.write",
            "description": "Write finance data",
            "module": "finance",
            "resource": "finance",
            "action": "write",
            "permission_type": "object",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample compliance certifications
    compliance_certifications.extend([
        {
            "id": 1,
            "certification_name": "SOC 2 Type II",
            "certification_type": "security",
            "version": "2024",
            "status": "certified",
            "certification_date": "2024-01-15",
            "expiry_date": "2025-01-15",
            "certifying_body": "AICPA",
            "certificate_number": "SOC2-2024-001",
            "scope": "Security, Availability, Processing Integrity",
            "requirements": {"security_controls": True, "availability_monitoring": True},
            "evidence": {"audit_report": "soc2_report_2024.pdf"},
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample security policies
    security_policies.extend([
        {
            "id": 1,
            "policy_name": "Password Policy",
            "policy_type": "password",
            "version": "1.0",
            "status": "active",
            "content": "Passwords must be at least 12 characters long and include uppercase, lowercase, numbers, and special characters.",
            "requirements": {"min_length": 12, "complexity": True, "expiry_days": 90},
            "enforcement_level": "mandatory",
            "effective_date": "2024-01-01",
            "created_at": datetime.utcnow().isoformat()
        }
    ])

# Initialize sample data when module loads
init_sample_data()
