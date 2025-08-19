from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.workflow.models import WorkflowRule, WorkflowExecution, WorkflowAction, WorkflowTemplate

bp = Blueprint('workflow', __name__, url_prefix='/api/workflow')

# Sample data (replace with database queries)
workflow_rules = []
workflow_executions = []
workflow_actions = []
workflow_templates = []

# Workflow Rule endpoints
@bp.route('/rules', methods=['GET'])
def get_workflow_rules():
    """Get all workflow rules"""
    return jsonify(workflow_rules)

@bp.route('/rules', methods=['POST'])
def create_workflow_rule():
    """Create a new workflow rule"""
    data = request.get_json()
    new_rule = {
        "id": len(workflow_rules) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "trigger_type": data.get('trigger_type'),
        "entity_type": data.get('entity_type'),
        "conditions": data.get('conditions', {}),
        "actions": data.get('actions', []),
        "is_active": data.get('is_active', True),
        "priority": data.get('priority', 1),
        "created_by": data.get('created_by'),
        "created_at": datetime.utcnow().isoformat()
    }
    workflow_rules.append(new_rule)
    return jsonify(new_rule), 201

@bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_workflow_rule(rule_id):
    """Update a workflow rule"""
    data = request.get_json()
    rule = next((r for r in workflow_rules if r['id'] == rule_id), None)
    if rule:
        rule.update(data)
        rule['updated_at'] = datetime.utcnow().isoformat()
        return jsonify(rule)
    return jsonify({"error": "Workflow rule not found"}), 404

# Workflow Execution endpoints
@bp.route('/executions', methods=['GET'])
def get_workflow_executions():
    """Get workflow executions with filters"""
    rule_id = request.args.get('rule_id', type=int)
    status = request.args.get('status')
    entity_type = request.args.get('entity_type')
    
    filtered_executions = workflow_executions
    if rule_id:
        filtered_executions = [e for e in filtered_executions if e.get('rule_id') == rule_id]
    if status:
        filtered_executions = [e for e in filtered_executions if e.get('execution_status') == status]
    if entity_type:
        filtered_executions = [e for e in filtered_executions if e.get('entity_type') == entity_type]
    
    return jsonify(filtered_executions)

@bp.route('/executions', methods=['POST'])
def create_workflow_execution():
    """Create a new workflow execution"""
    data = request.get_json()
    new_execution = {
        "id": len(workflow_executions) + 1,
        "rule_id": data.get('rule_id'),
        "trigger_type": data.get('trigger_type'),
        "entity_type": data.get('entity_type'),
        "entity_id": data.get('entity_id'),
        "trigger_data": data.get('trigger_data', {}),
        "execution_status": 'pending',
        "started_at": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    workflow_executions.append(new_execution)
    return jsonify(new_execution), 201

# Workflow Template endpoints
@bp.route('/templates', methods=['GET'])
def get_workflow_templates():
    """Get workflow templates"""
    category = request.args.get('category')
    
    filtered_templates = workflow_templates
    if category:
        filtered_templates = [t for t in filtered_templates if t.get('category') == category]
    
    return jsonify(filtered_templates)

@bp.route('/templates', methods=['POST'])
def create_workflow_template():
    """Create a new workflow template"""
    data = request.get_json()
    new_template = {
        "id": len(workflow_templates) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "category": data.get('category'),
        "template_data": data.get('template_data', {}),
        "is_active": data.get('is_active', True),
        "created_by": data.get('created_by'),
        "created_at": datetime.utcnow().isoformat()
    }
    workflow_templates.append(new_template)
    return jsonify(new_template), 201

# Workflow Engine endpoint
@bp.route('/execute', methods=['POST'])
def execute_workflow():
    """Execute workflow for a trigger"""
    data = request.get_json()
    trigger_type = data.get('trigger_type')
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    trigger_data = data.get('trigger_data', {})
    
    # Find applicable rules
    applicable_rules = [r for r in workflow_rules 
                       if r.get('trigger_type') == trigger_type and 
                       r.get('entity_type') == entity_type and 
                       r.get('is_active', True)]
    
    # Sort by priority (highest first)
    applicable_rules.sort(key=lambda x: x.get('priority', 1), reverse=True)
    
    executions = []
    for rule in applicable_rules:
        # Check conditions
        conditions_met = True  # TODO: Implement condition checking logic
        
        if conditions_met:
            # Create execution
            execution = {
                "id": len(workflow_executions) + 1,
                "rule_id": rule['id'],
                "trigger_type": trigger_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "trigger_data": trigger_data,
                "execution_status": 'running',
                "started_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            workflow_executions.append(execution)
            executions.append(execution)
            
            # Execute actions
            actions = rule.get('actions', [])
            for action in actions:
                # TODO: Implement action execution logic
                pass
            
            execution['execution_status'] = 'completed'
            execution['completed_at'] = datetime.utcnow().isoformat()
    
    return jsonify({
        "trigger_type": trigger_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "executions": executions
    })

# Analytics endpoints
@bp.route('/analytics', methods=['GET'])
def get_workflow_analytics():
    """Get workflow analytics"""
    total_rules = len(workflow_rules)
    active_rules = len([r for r in workflow_rules if r.get('is_active', True)])
    total_executions = len(workflow_executions)
    completed_executions = len([e for e in workflow_executions if e.get('execution_status') == 'completed'])
    failed_executions = len([e for e in workflow_executions if e.get('execution_status') == 'failed'])
    
    return jsonify({
        "total_rules": total_rules,
        "active_rules": active_rules,
        "total_executions": total_executions,
        "completed_executions": completed_executions,
        "failed_executions": failed_executions,
        "success_rate": (completed_executions / total_executions * 100) if total_executions > 0 else 0
    })
