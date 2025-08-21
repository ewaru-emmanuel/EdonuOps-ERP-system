from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import json
import logging
from flask import current_app, g
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()

class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    APPROVED = "approved"
    REJECTED = "rejected"

class TaskType(Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"

@dataclass
class WorkflowDefinition:
    """Workflow definition with tasks and transitions"""
    id: str
    name: str
    description: str
    version: str
    status: WorkflowStatus
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowInstance:
    """Running workflow instance"""
    id: str
    workflow_id: str
    status: TaskStatus
    current_task: str
    variables: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    created_by: str = ""
    tenant_id: str = ""

@dataclass
class TaskInstance:
    """Task instance within a workflow"""
    id: str
    workflow_instance_id: str
    task_id: str
    status: TaskStatus
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Dict[str, Any] = field(default_factory=dict)
    comments: List[Dict[str, Any]] = field(default_factory=list)

class WorkflowEngine:
    """Enterprise workflow engine for business process automation"""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.trigger_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default task and trigger handlers"""
        # Task handlers
        self.register_task_handler("approval", self._handle_approval_task)
        self.register_task_handler("notification", self._handle_notification_task)
        self.register_task_handler("integration", self._handle_integration_task)
        self.register_task_handler("automated", self._handle_automated_task)
        
        # Trigger handlers
        self.register_trigger_handler("document_created", self._handle_document_created)
        self.register_trigger_handler("amount_threshold", self._handle_amount_threshold)
        self.register_trigger_handler("user_action", self._handle_user_action)
    
    def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register a new workflow definition"""
        try:
            self.workflows[workflow.id] = workflow
            logger.info(f"Registered workflow: {workflow.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register workflow: {e}")
            return False
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler"""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered task handler for: {task_type}")
    
    def register_trigger_handler(self, trigger_type: str, handler: Callable):
        """Register a trigger handler"""
        self.trigger_handlers[trigger_type] = handler
        logger.info(f"Registered trigger handler for: {trigger_type}")
    
    def start_workflow(self, workflow_id: str, variables: Dict[str, Any] = None, 
                      created_by: str = None) -> Optional[str]:
        """Start a new workflow instance"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow not found: {workflow_id}")
            return None
        
        workflow = self.workflows[workflow_id]
        if workflow.status != WorkflowStatus.ACTIVE:
            logger.error(f"Workflow not active: {workflow_id}")
            return None
        
        try:
            instance_id = f"{workflow_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            instance = WorkflowInstance(
                id=instance_id,
                workflow_id=workflow_id,
                status=TaskStatus.PENDING,
                current_task=workflow.tasks[0]['id'] if workflow.tasks else None,
                variables=variables or {},
                created_by=created_by or getattr(g, 'current_user_id', 'system'),
                tenant_id=getattr(g, 'current_tenant', 'default')
            )
            
            self.instances[instance_id] = instance
            
            # Start first task
            if workflow.tasks:
                self._start_task(instance_id, workflow.tasks[0]['id'])
            
            logger.info(f"Started workflow instance: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow: {e}")
            return None
    
    def _start_task(self, instance_id: str, task_id: str) -> bool:
        """Start a specific task in a workflow instance"""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        # Find task definition
        task_def = next((t for t in workflow.tasks if t['id'] == task_id), None)
        if not task_def:
            return False
        
        try:
            # Create task instance
            task_instance = TaskInstance(
                id=f"{instance_id}_{task_id}",
                workflow_instance_id=instance_id,
                task_id=task_id,
                status=TaskStatus.IN_PROGRESS,
                started_at=datetime.utcnow()
            )
            
            # Handle task based on type
            task_type = task_def.get('type', 'manual')
            if task_type in self.task_handlers:
                result = self.task_handlers[task_type](task_instance, instance, task_def)
                if result:
                    task_instance.status = TaskStatus.COMPLETED
                    task_instance.result = result
                else:
                    task_instance.status = TaskStatus.FAILED
            else:
                # Manual task - wait for user action
                task_instance.status = TaskStatus.PENDING
            
            # Store task instance
            instance.current_task = task_id
            
            logger.info(f"Started task: {task_id} in instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start task: {e}")
            return False
    
    def complete_task(self, instance_id: str, task_id: str, result: Dict[str, Any] = None) -> bool:
        """Complete a task and move to next"""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        # Update task status
        task_instance = TaskInstance(
            id=f"{instance_id}_{task_id}",
            workflow_instance_id=instance_id,
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow(),
            result=result or {}
        )
        
        # Find next task
        current_task_index = next((i for i, t in enumerate(workflow.tasks) if t['id'] == task_id), -1)
        if current_task_index >= 0 and current_task_index + 1 < len(workflow.tasks):
            next_task = workflow.tasks[current_task_index + 1]
            self._start_task(instance_id, next_task['id'])
        else:
            # Workflow completed
            instance.status = TaskStatus.COMPLETED
            instance.completed_at = datetime.utcnow()
        
        logger.info(f"Completed task: {task_id} in instance: {instance_id}")
        return True
    
    def trigger_workflow(self, trigger_type: str, data: Dict[str, Any]) -> List[str]:
        """Trigger workflows based on events"""
        triggered_instances = []
        
        for workflow_id, workflow in self.workflows.items():
            if workflow.status != WorkflowStatus.ACTIVE:
                continue
            
            # Check if workflow should be triggered
            for trigger in workflow.triggers:
                if trigger.get('type') == trigger_type:
                    if trigger_type in self.trigger_handlers:
                        should_trigger = self.trigger_handlers[trigger_type](trigger, data)
                        if should_trigger:
                            instance_id = self.start_workflow(workflow_id, data)
                            if instance_id:
                                triggered_instances.append(instance_id)
        
        return triggered_instances
    
    # Default task handlers
    def _handle_approval_task(self, task_instance: TaskInstance, 
                            workflow_instance: WorkflowInstance, 
                            task_def: Dict[str, Any]) -> Dict[str, Any]:
        """Handle approval tasks"""
        # In a real implementation, this would create approval requests
        return {
            "approval_required": True,
            "approvers": task_def.get("approvers", []),
            "message": task_def.get("message", "Approval required")
        }
    
    def _handle_notification_task(self, task_instance: TaskInstance,
                                workflow_instance: WorkflowInstance,
                                task_def: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notification tasks"""
        # In a real implementation, this would send notifications
        return {
            "notification_sent": True,
            "recipients": task_def.get("recipients", []),
            "message": task_def.get("message", "Notification sent")
        }
    
    def _handle_integration_task(self, task_instance: TaskInstance,
                               workflow_instance: WorkflowInstance,
                               task_def: Dict[str, Any]) -> Dict[str, Any]:
        """Handle integration tasks"""
        # In a real implementation, this would call external APIs
        return {
            "integration_completed": True,
            "external_system": task_def.get("external_system", ""),
            "result": "Integration successful"
        }
    
    def _handle_automated_task(self, task_instance: TaskInstance,
                             workflow_instance: WorkflowInstance,
                             task_def: Dict[str, Any]) -> Dict[str, Any]:
        """Handle automated tasks"""
        # In a real implementation, this would execute business logic
        return {
            "automation_completed": True,
            "action": task_def.get("action", ""),
            "result": "Automation successful"
        }
    
    # Default trigger handlers
    def _handle_document_created(self, trigger: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Handle document creation triggers"""
        return data.get("document_type") == trigger.get("document_type")
    
    def _handle_amount_threshold(self, trigger: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Handle amount threshold triggers"""
        amount = data.get("amount", 0)
        threshold = trigger.get("threshold", 0)
        return amount >= threshold
    
    def _handle_user_action(self, trigger: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Handle user action triggers"""
        return data.get("action") == trigger.get("action")

# Predefined workflows
def create_invoice_approval_workflow() -> WorkflowDefinition:
    """Create invoice approval workflow"""
    return WorkflowDefinition(
        id="invoice_approval",
        name="Invoice Approval Workflow",
        description="Automated invoice approval process",
        version="1.0",
        status=WorkflowStatus.ACTIVE,
        tasks=[
            {
                "id": "validate_invoice",
                "name": "Validate Invoice",
                "type": "automated",
                "action": "validate_invoice_data"
            },
            {
                "id": "manager_approval",
                "name": "Manager Approval",
                "type": "approval",
                "approvers": ["finance_manager"],
                "message": "Invoice requires manager approval"
            },
            {
                "id": "process_payment",
                "name": "Process Payment",
                "type": "automated",
                "action": "process_payment"
            },
            {
                "id": "send_notification",
                "name": "Send Notification",
                "type": "notification",
                "recipients": ["invoice_creator"],
                "message": "Invoice processed successfully"
            }
        ],
        triggers=[
            {
                "type": "document_created",
                "document_type": "invoice"
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
        tasks=[
            {
                "id": "validate_po",
                "name": "Validate Purchase Order",
                "type": "automated",
                "action": "validate_po_data"
            },
            {
                "id": "budget_check",
                "name": "Budget Check",
                "type": "automated",
                "action": "check_budget_availability"
            },
            {
                "id": "approval_chain",
                "name": "Approval Chain",
                "type": "approval",
                "approvers": ["department_head", "finance_manager"],
                "message": "Purchase order requires approval"
            },
            {
                "id": "create_order",
                "name": "Create Order",
                "type": "integration",
                "external_system": "supplier_portal"
            }
        ],
        triggers=[
            {
                "type": "document_created",
                "document_type": "purchase_order"
            }
        ]
    )

# Global workflow engine instance
workflow_engine = WorkflowEngine()

# Register default workflows
workflow_engine.register_workflow(create_invoice_approval_workflow())
workflow_engine.register_workflow(create_purchase_order_workflow())
