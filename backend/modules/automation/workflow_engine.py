# Business Process Automation Workflow Engine for EdonuOps ERP
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class TaskType(Enum):
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    AUTOMATED = "automated"
    MANUAL = "manual"

@dataclass
class WorkflowDefinition:
    """Workflow definition with steps and conditions"""
    id: str
    name: str
    description: str
    version: str
    status: WorkflowStatus
    steps: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    conditions: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowInstance:
    """Active workflow instance"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: int
    data: Dict[str, Any]
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

@dataclass
class TaskInstance:
    """Individual task within a workflow"""
    id: str
    workflow_instance_id: str
    step_id: str
    task_type: TaskType
    status: TaskStatus
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

class WorkflowEngine:
    """Main workflow engine for business process automation"""
    
    def __init__(self):
        self.workflows = {}
        self.instances = {}
        self.task_handlers = {}
        self.trigger_handlers = {}
        self.integration_handlers = {}
        
        # Initialize default handlers
        self._initialize_default_handlers()
    
    def _initialize_default_handlers(self):
        """Initialize default task and trigger handlers"""
        
        # Default task handlers
        self.register_task_handler("approval", self._handle_approval_task)
        self.register_task_handler("notification", self._handle_notification_task)
        self.register_task_handler("integration", self._handle_integration_task)
        self.register_task_handler("automated", self._handle_automated_task)
        
        # Default trigger handlers
        self.register_trigger_handler("document_created", self._handle_document_created)
        self.register_trigger_handler("amount_threshold", self._handle_amount_threshold)
        self.register_trigger_handler("user_action", self._handle_user_action)
        
        # Default integration handlers
        self.register_integration_handler("email", self._handle_email_integration)
        self.register_integration_handler("slack", self._handle_slack_integration)
        self.register_integration_handler("webhook", self._handle_webhook_integration)
    
    def register_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """Register a new workflow definition"""
        try:
            self.workflows[workflow_def.id] = workflow_def
            logger.info(f"Workflow registered: {workflow_def.name}")
            return True
        except Exception as e:
            logger.error(f"Workflow registration failed: {e}")
            return False
    
    def register_task_handler(self, task_type: str, handler: Callable) -> bool:
        """Register a task handler"""
        try:
            self.task_handlers[task_type] = handler
            return True
        except Exception as e:
            logger.error(f"Task handler registration failed: {e}")
            return False
    
    def register_trigger_handler(self, trigger_type: str, handler: Callable) -> bool:
        """Register a trigger handler"""
        try:
            self.trigger_handlers[trigger_type] = handler
            return True
        except Exception as e:
            logger.error(f"Trigger handler registration failed: {e}")
            return False
    
    def register_integration_handler(self, integration_type: str, handler: Callable) -> bool:
        """Register an integration handler"""
        try:
            self.integration_handlers[integration_type] = handler
            return True
        except Exception as e:
            logger.error(f"Integration handler registration failed: {e}")
            return False
    
    def start_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Optional[str]:
        """Start a new workflow instance"""
        try:
            if workflow_id not in self.workflows:
                return None
            
            workflow = self.workflows[workflow_id]
            instance_id = str(uuid.uuid4())
            
            instance = WorkflowInstance(
                id=instance_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.ACTIVE,
                current_step=0,
                data=data
            )
            
            self.instances[instance_id] = instance
            
            # Create first task
            self._create_task_for_step(instance, 0)
            
            logger.info(f"Workflow started: {workflow.name} - Instance: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Workflow start failed: {e}")
            return None
    
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Complete a task and move to next step"""
        try:
            # Find task and instance
            task = self._find_task(task_id)
            if not task:
                return False
            
            instance = self.instances.get(task.workflow_instance_id)
            if not instance:
                return False
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            # Move to next step
            workflow = self.workflows[instance.workflow_id]
            next_step = instance.current_step + 1
            
            if next_step < len(workflow.steps):
                instance.current_step = next_step
                self._create_task_for_step(instance, next_step)
            else:
                # Workflow completed
                instance.status = WorkflowStatus.COMPLETED
                instance.completed_at = datetime.utcnow()
            
            logger.info(f"Task completed: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Task completion failed: {e}")
            return False
    
    def trigger_workflow(self, trigger_type: str, data: Dict[str, Any]) -> List[str]:
        """Trigger workflows based on event"""
        try:
            triggered_instances = []
            
            for workflow_id, workflow in self.workflows.items():
                if workflow.status != WorkflowStatus.ACTIVE:
                    continue
                
                # Check if workflow should be triggered
                for trigger in workflow.triggers:
                    if trigger.get('type') == trigger_type:
                        # Check conditions
                        if self._evaluate_conditions(workflow.conditions, data):
                            instance_id = self.start_workflow(workflow_id, data)
                            if instance_id:
                                triggered_instances.append(instance_id)
            
            return triggered_instances
            
        except Exception as e:
            logger.error(f"Workflow triggering failed: {e}")
            return []
    
    def _create_task_for_step(self, instance: WorkflowInstance, step_index: int):
        """Create task for current workflow step"""
        try:
            workflow = self.workflows[instance.workflow_id]
            step = workflow.steps[step_index]
            
            task = TaskInstance(
                id=str(uuid.uuid4()),
                workflow_instance_id=instance.id,
                step_id=step['id'],
                task_type=TaskType(step['type']),
                status=TaskStatus.PENDING,
                assigned_to=step.get('assigned_to'),
                due_date=self._calculate_due_date(step.get('due_date_hours', 24))
            )
            
            # Execute task handler
            handler = self.task_handlers.get(step['type'])
            if handler:
                handler(task, instance.data)
            
        except Exception as e:
            logger.error(f"Task creation failed: {e}")
    
    def _find_task(self, task_id: str) -> Optional[TaskInstance]:
        """Find task by ID"""
        # This would typically query the database
        # For now, return None
        return None
    
    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], data: Dict[str, Any]) -> bool:
        """Evaluate workflow conditions"""
        try:
            for condition in conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if field not in data:
                    return False
                
                actual_value = data[field]
                
                if operator == 'equals' and actual_value != value:
                    return False
                elif operator == 'greater_than' and actual_value <= value:
                    return False
                elif operator == 'less_than' and actual_value >= value:
                    return False
                elif operator == 'contains' and value not in str(actual_value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _calculate_due_date(self, hours: int) -> datetime:
        """Calculate task due date"""
        return datetime.utcnow() + timedelta(hours=hours)
    
    # Default task handlers
    def _handle_approval_task(self, task: TaskInstance, data: Dict[str, Any]):
        """Handle approval tasks"""
        logger.info(f"Approval task created: {task.id}")
        # This would typically send notifications to approvers
    
    def _handle_notification_task(self, task: TaskInstance, data: Dict[str, Any]):
        """Handle notification tasks"""
        logger.info(f"Notification task created: {task.id}")
        # This would typically send notifications
    
    def _handle_integration_task(self, task: TaskInstance, data: Dict[str, Any]):
        """Handle integration tasks"""
        logger.info(f"Integration task created: {task.id}")
        # This would typically call external systems
    
    def _handle_automated_task(self, task: TaskInstance, data: Dict[str, Any]):
        """Handle automated tasks"""
        logger.info(f"Automated task created: {task.id}")
        # This would typically execute automated actions
    
    # Default trigger handlers
    def _handle_document_created(self, data: Dict[str, Any]):
        """Handle document creation triggers"""
        logger.info("Document created trigger handled")
    
    def _handle_amount_threshold(self, data: Dict[str, Any]):
        """Handle amount threshold triggers"""
        logger.info("Amount threshold trigger handled")
    
    def _handle_user_action(self, data: Dict[str, Any]):
        """Handle user action triggers"""
        logger.info("User action trigger handled")
    
    # Default integration handlers
    def _handle_email_integration(self, data: Dict[str, Any]):
        """Handle email integrations"""
        logger.info("Email integration handled")
    
    def _handle_slack_integration(self, data: Dict[str, Any]):
        """Handle Slack integrations"""
        logger.info("Slack integration handled")
    
    def _handle_webhook_integration(self, data: Dict[str, Any]):
        """Handle webhook integrations"""
        logger.info("Webhook integration handled")

# Predefined workflows
def create_invoice_approval_workflow() -> WorkflowDefinition:
    """Create invoice approval workflow"""
    return WorkflowDefinition(
        id="invoice_approval",
        name="Invoice Approval Workflow",
        description="Automated invoice approval process",
        version="1.0",
        status=WorkflowStatus.ACTIVE,
        steps=[
            {
                "id": "review",
                "name": "Invoice Review",
                "type": "approval",
                "assigned_to": "manager",
                "due_date_hours": 24
            },
            {
                "id": "finance_approval",
                "name": "Finance Approval",
                "type": "approval",
                "assigned_to": "finance_manager",
                "due_date_hours": 48
            },
            {
                "id": "payment_processing",
                "name": "Payment Processing",
                "type": "automated",
                "due_date_hours": 1
            }
        ],
        triggers=[
            {
                "type": "document_created",
                "document_type": "invoice"
            }
        ],
        conditions=[
            {
                "field": "amount",
                "operator": "greater_than",
                "value": 1000
            }
        ]
    )

def create_purchase_order_workflow() -> WorkflowDefinition:
    """Create purchase order workflow"""
    return WorkflowDefinition(
        id="purchase_order",
        name="Purchase Order Workflow",
        description="Purchase order approval and processing",
        version="1.0",
        status=WorkflowStatus.ACTIVE,
        steps=[
            {
                "id": "department_approval",
                "name": "Department Approval",
                "type": "approval",
                "assigned_to": "department_head",
                "due_date_hours": 24
            },
            {
                "id": "procurement_review",
                "name": "Procurement Review",
                "type": "approval",
                "assigned_to": "procurement_manager",
                "due_date_hours": 48
            },
            {
                "id": "vendor_notification",
                "name": "Vendor Notification",
                "type": "notification",
                "due_date_hours": 1
            }
        ],
        triggers=[
            {
                "type": "document_created",
                "document_type": "purchase_order"
            }
        ],
        conditions=[]
    )

# Global workflow engine instance
workflow_engine = WorkflowEngine()

# Register default workflows
workflow_engine.register_workflow(create_invoice_approval_workflow())
workflow_engine.register_workflow(create_purchase_order_workflow())
