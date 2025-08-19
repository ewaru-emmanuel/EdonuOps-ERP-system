from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.audit.models import AuditLog, AuditLogFilter, AuditLogExport

bp = Blueprint('audit', __name__, url_prefix='/api/audit')

# Sample data
audit_logs = []
audit_filters = []
audit_exports = []

@bp.route('/logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs with filters"""
    user_id = request.args.get('user_id', type=int)
    entity_type = request.args.get('entity_type')
    action = request.args.get('action')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    filtered_logs = audit_logs
    if user_id:
        filtered_logs = [l for l in filtered_logs if l.get('user_id') == user_id]
    if entity_type:
        filtered_logs = [l for l in filtered_logs if l.get('entity_type') == entity_type]
    if action:
        filtered_logs = [l for l in filtered_logs if l.get('action') == action]
    
    return jsonify(filtered_logs)

@bp.route('/logs', methods=['POST'])
def create_audit_log():
    """Create a new audit log entry"""
    data = request.get_json()
    new_log = {
        "id": len(audit_logs) + 1,
        "user_id": data.get('user_id'),
        "action": data.get('action'),
        "entity_type": data.get('entity_type'),
        "entity_id": data.get('entity_id'),
        "old_values": data.get('old_values'),
        "new_values": data.get('new_values'),
        "ip_address": data.get('ip_address'),
        "user_agent": data.get('user_agent'),
        "session_id": data.get('session_id'),
        "additional_data": data.get('additional_data', {}),
        "timestamp": datetime.utcnow().isoformat()
    }
    audit_logs.append(new_log)
    return jsonify(new_log), 201

@bp.route('/exports', methods=['GET'])
def get_audit_exports():
    """Get audit log exports"""
    user_id = request.args.get('user_id', type=int)
    filtered_exports = audit_exports
    if user_id:
        filtered_exports = [e for e in audit_exports if e.get('user_id') == user_id]
    return jsonify(filtered_exports)

@bp.route('/exports', methods=['POST'])
def create_audit_export():
    """Create a new audit log export"""
    data = request.get_json()
    new_export = {
        "id": len(audit_exports) + 1,
        "user_id": data.get('user_id'),
        "export_name": data.get('export_name'),
        "filter_criteria": data.get('filter_criteria', {}),
        "export_format": data.get('export_format', 'csv'),
        "status": 'pending',
        "created_at": datetime.utcnow().isoformat()
    }
    audit_exports.append(new_export)
    return jsonify(new_export), 201
