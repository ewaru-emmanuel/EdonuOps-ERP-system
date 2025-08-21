# Business Process Automation API Routes for EdonuOps ERP
from flask import Blueprint, request, jsonify
from modules.automation.workflow_engine import WorkflowEngine, create_invoice_approval_workflow, create_purchase_order_workflow
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
automation_bp = Blueprint('automation', __name__)

# Initialize workflow engine
workflow_engine = WorkflowEngine()

# Register default workflows
workflow_engine.register_workflow(create_invoice_approval_workflow())
workflow_engine.register_workflow(create_purchase_order_workflow())

@automation_bp.route('/api/automation/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows"""
    try:
        workflows = []
        for workflow_id, workflow in workflow_engine.workflows.items():
            workflows.append({
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'version': workflow.version,
                'status': workflow.status.value,
                'steps_count': len(workflow.steps),
                'triggers_count': len(workflow.triggers),
                'created_at': workflow.created_at.isoformat(),
                'updated_at': workflow.updated_at.isoformat()
            })
        
        return jsonify({
            'status': 'success',
            'workflows': workflows,
            'count': len(workflows)
        })
    except Exception as e:
        logger.error(f"Get workflows error: {e}")
        return jsonify({'error': 'Failed to retrieve workflows'}), 500

@automation_bp.route('/api/automation/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        workflow_type = data.get('type', 'approval')
        
        if not name:
            return jsonify({'error': 'Workflow name required'}), 400
        
        # Create workflow definition
        workflow_def = {
            'id': f"workflow_{uuid.uuid4().hex[:8]}",
            'name': name,
            'description': description,
            'version': '1.0',
            'status': 'active',
            'steps': [
                {
                    'id': 'step_1',
                    'name': f'{workflow_type.title()} Step',
                    'type': workflow_type,
                    'assigned_to': 'manager',
                    'due_date_hours': 24
                }
            ],
            'triggers': [],
            'conditions': []
        }
        
        # Register workflow
        success = workflow_engine.register_workflow(workflow_def)
        
        if success:
            return jsonify({
                'status': 'success',
                'workflow': workflow_def,
                'message': 'Workflow created successfully'
            })
        else:
            return jsonify({'error': 'Failed to create workflow'}), 500
            
    except Exception as e:
        logger.error(f"Create workflow error: {e}")
        return jsonify({'error': 'Failed to create workflow'}), 500

@automation_bp.route('/api/automation/workflows/<workflow_id>/start', methods=['POST'])
def start_workflow(workflow_id):
    """Start a workflow instance"""
    try:
        data = request.get_json() or {}
        
        # Start workflow
        instance_id = workflow_engine.start_workflow(workflow_id, data)
        
        if instance_id:
            return jsonify({
                'status': 'success',
                'instance_id': instance_id,
                'message': 'Workflow started successfully'
            })
        else:
            return jsonify({'error': 'Failed to start workflow'}), 500
            
    except Exception as e:
        logger.error(f"Start workflow error: {e}")
        return jsonify({'error': 'Failed to start workflow'}), 500

@automation_bp.route('/api/automation/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        # Mock tasks data for now
        tasks = [
            {
                'id': 'task_1',
                'name': 'Invoice Review',
                'status': 'pending',
                'assigned_to': 'finance_manager',
                'due_date': '2024-01-15T10:00:00Z',
                'workflow_instance_id': 'instance_1',
                'task_type': 'approval'
            },
            {
                'id': 'task_2',
                'name': 'Purchase Order Approval',
                'status': 'completed',
                'assigned_to': 'procurement_manager',
                'due_date': '2024-01-14T15:00:00Z',
                'workflow_instance_id': 'instance_2',
                'task_type': 'approval'
            },
            {
                'id': 'task_3',
                'name': 'Payment Processing',
                'status': 'pending',
                'assigned_to': 'system',
                'due_date': '2024-01-16T09:00:00Z',
                'workflow_instance_id': 'instance_1',
                'task_type': 'automated'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'tasks': tasks,
            'count': len(tasks)
        })
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        return jsonify({'error': 'Failed to retrieve tasks'}), 500

@automation_bp.route('/api/automation/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Complete a task"""
    try:
        data = request.get_json() or {}
        
        # Complete task
        success = workflow_engine.complete_task(task_id, data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Task completed successfully'
            })
        else:
            return jsonify({'error': 'Failed to complete task'}), 500
            
    except Exception as e:
        logger.error(f"Complete task error: {e}")
        return jsonify({'error': 'Failed to complete task'}), 500

@automation_bp.route('/api/automation/integrations', methods=['GET'])
def get_integrations():
    """Get all integrations"""
    try:
        # Mock integrations data
        integrations = [
            {
                'id': 'integration_1',
                'name': 'Email Integration',
                'description': 'Send automated emails for workflow notifications',
                'status': 'active',
                'type': 'email',
                'config': {
                    'smtp_server': 'smtp.company.com',
                    'port': 587
                }
            },
            {
                'id': 'integration_2',
                'name': 'Slack Integration',
                'description': 'Send notifications to Slack channels',
                'status': 'active',
                'type': 'slack',
                'config': {
                    'webhook_url': 'https://hooks.slack.com/...',
                    'channel': '#workflows'
                }
            },
            {
                'id': 'integration_3',
                'name': 'Webhook Integration',
                'description': 'Trigger external systems via webhooks',
                'status': 'inactive',
                'type': 'webhook',
                'config': {
                    'endpoint': 'https://api.external.com/webhook',
                    'method': 'POST'
                }
            }
        ]
        
        return jsonify({
            'status': 'success',
            'integrations': integrations,
            'count': len(integrations)
        })
    except Exception as e:
        logger.error(f"Get integrations error: {e}")
        return jsonify({'error': 'Failed to retrieve integrations'}), 500

@automation_bp.route('/api/automation/triggers', methods=['POST'])
def trigger_workflow():
    """Trigger workflows based on event"""
    try:
        data = request.get_json()
        trigger_type = data.get('type')
        trigger_data = data.get('data', {})
        
        if not trigger_type:
            return jsonify({'error': 'Trigger type required'}), 400
        
        # Trigger workflows
        instance_ids = workflow_engine.trigger_workflow(trigger_type, trigger_data)
        
        return jsonify({
            'status': 'success',
            'triggered_instances': instance_ids,
            'count': len(instance_ids),
            'message': f'Triggered {len(instance_ids)} workflow instances'
        })
        
    except Exception as e:
        logger.error(f"Trigger workflow error: {e}")
        return jsonify({'error': 'Failed to trigger workflow'}), 500

@automation_bp.route('/api/automation/instances', methods=['GET'])
def get_workflow_instances():
    """Get workflow instances"""
    try:
        instances = []
        for instance_id, instance in workflow_engine.instances.items():
            instances.append({
                'id': instance.id,
                'workflow_id': instance.workflow_id,
                'status': instance.status.value,
                'current_step': instance.current_step,
                'started_at': instance.started_at.isoformat(),
                'completed_at': instance.completed_at.isoformat() if instance.completed_at else None
            })
        
        return jsonify({
            'status': 'success',
            'instances': instances,
            'count': len(instances)
        })
    except Exception as e:
        logger.error(f"Get instances error: {e}")
        return jsonify({'error': 'Failed to retrieve instances'}), 500
