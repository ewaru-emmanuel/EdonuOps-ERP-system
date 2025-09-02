from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import json

class ApprovalWorkflow:
    """Comprehensive Approval Workflow Engine for Critical Transactions"""
    
    def __init__(self):
        self.workflows = []
        self.approval_history = []
        
        # Workflow templates
        self.workflow_templates = {
            'purchase_order': {
                'name': 'Purchase Order Approval',
                'description': 'Approval workflow for purchase orders',
                'stages': [
                    {
                        'stage': 1,
                        'name': 'Manager Review',
                        'role': 'manager',
                        'timeout_hours': 24,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': True
                    },
                    {
                        'stage': 2,
                        'name': 'Finance Review',
                        'role': 'finance_manager',
                        'timeout_hours': 48,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': True
                    },
                    {
                        'stage': 3,
                        'name': 'Director Approval',
                        'role': 'director',
                        'timeout_hours': 72,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': False
                    }
                ],
                'amount_thresholds': {
                    'low': 1000,
                    'medium': 10000,
                    'high': 50000
                }
            },
            'stock_adjustment': {
                'name': 'Stock Adjustment Approval',
                'description': 'Approval workflow for inventory adjustments',
                'stages': [
                    {
                        'stage': 1,
                        'name': 'Supervisor Review',
                        'role': 'supervisor',
                        'timeout_hours': 12,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': True
                    },
                    {
                        'stage': 2,
                        'name': 'Inventory Manager',
                        'role': 'inventory_manager',
                        'timeout_hours': 24,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': True
                    }
                ],
                'amount_thresholds': {
                    'low': 500,
                    'medium': 2000,
                    'high': 10000
                }
            },
            'journal_entry': {
                'name': 'Journal Entry Approval',
                'description': 'Approval workflow for manual journal entries',
                'stages': [
                    {
                        'stage': 1,
                        'name': 'Accountant Review',
                        'role': 'accountant',
                        'timeout_hours': 24,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': True
                    },
                    {
                        'stage': 2,
                        'name': 'Controller Approval',
                        'role': 'controller',
                        'timeout_hours': 48,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': False
                    }
                ],
                'amount_thresholds': {
                    'low': 1000,
                    'medium': 5000,
                    'high': 25000
                }
            },
            'expense_report': {
                'name': 'Expense Report Approval',
                'description': 'Approval workflow for expense reports',
                'stages': [
                    {
                        'stage': 1,
                        'name': 'Manager Review',
                        'role': 'manager',
                        'timeout_hours': 48,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': True
                    },
                    {
                        'stage': 2,
                        'name': 'Finance Review',
                        'role': 'finance',
                        'timeout_hours': 72,
                        'can_approve': True,
                        'can_reject': True,
                        'can_escalate': False
                    }
                ],
                'amount_thresholds': {
                    'low': 500,
                    'medium': 2000,
                    'high': 10000
                }
            }
        }
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """
        Create a new approval workflow
        """
        try:
            # Validate required fields
            required_fields = ['type', 'reference_id', 'amount', 'initiator']
            for field in required_fields:
                if field not in workflow_data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            workflow_type = workflow_data['type']
            if workflow_type not in self.workflow_templates:
                return {
                    'success': False,
                    'error': f'Invalid workflow type: {workflow_type}'
                }
            
            # Get template
            template = self.workflow_templates[workflow_type]
            
            # Determine required stages based on amount
            amount = workflow_data['amount']
            required_stages = self._determine_required_stages(template, amount)
            
            # Create workflow
            workflow_id = f"WF-{workflow_type.upper()}-{datetime.now().strftime('%Y%m%d')}-{len(self.workflows) + 1:03d}"
            
            workflow = {
                'id': workflow_id,
                'type': workflow_type,
                'name': template['name'],
                'description': template['description'],
                'reference_id': workflow_data['reference_id'],
                'reference_type': workflow_data.get('reference_type', workflow_type),
                'amount': amount,
                'currency': workflow_data.get('currency', 'USD'),
                'initiator': workflow_data['initiator'],
                'initiated_date': datetime.now(),
                'status': 'pending',
                'current_stage': 1,
                'total_stages': len(required_stages),
                'stages': required_stages,
                'approval_history': [],
                'metadata': workflow_data.get('metadata', {}),
                'timeout_date': self._calculate_timeout_date(required_stages[0]['timeout_hours']),
                'escalated': False,
                'escalated_to': None,
                'escalated_date': None
            }
            
            self.workflows.append(workflow)
            
            # Create initial approval history entry
            self._create_approval_history_entry(workflow_id, 'initiated', workflow_data['initiator'], {
                'amount': amount,
                'currency': workflow.get('currency', 'USD'),
                'notes': workflow_data.get('notes', '')
            })
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'workflow': workflow,
                'message': f'Approval workflow created successfully. Awaiting {required_stages[0]["name"]}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating workflow: {str(e)}'
            }
    
    def approve_workflow(self, workflow_id: str, approver: str, notes: str = '') -> Dict:
        """
        Approve a workflow at current stage
        """
        try:
            workflow = self._get_workflow_by_id(workflow_id)
            if not workflow:
                return {
                    'success': False,
                    'error': 'Workflow not found'
                }
            
            if workflow['status'] != 'pending':
                return {
                    'success': False,
                    'error': f'Workflow is not pending (current status: {workflow["status"]})'
                }
            
            current_stage = workflow['current_stage']
            stage_info = workflow['stages'][current_stage - 1]
            
            # Check if approver has permission for this stage
            if not self._can_approve_stage(approver, stage_info):
                return {
                    'success': False,
                    'error': f'User {approver} does not have permission to approve this stage'
                }
            
            # Check if workflow has timed out
            if datetime.now() > workflow['timeout_date']:
                return {
                    'success': False,
                    'error': 'Workflow has timed out and needs to be escalated'
                }
            
            # Record approval
            approval_entry = {
                'stage': current_stage,
                'stage_name': stage_info['name'],
                'approver': approver,
                'action': 'approved',
                'date': datetime.now(),
                'notes': notes
            }
            
            workflow['approval_history'].append(approval_entry)
            
            # Check if this is the final stage
            if current_stage >= workflow['total_stages']:
                # Workflow completed
                workflow['status'] = 'approved'
                workflow['completed_date'] = datetime.now()
                
                # Create final approval history entry
                self._create_approval_history_entry(workflow_id, 'completed', approver, {
                    'final_approver': approver,
                    'notes': notes
                })
                
                # Execute the approved action
                self._execute_approved_action(workflow)
                
                return {
                    'success': True,
                    'workflow_id': workflow_id,
                    'status': 'approved',
                    'message': 'Workflow approved and completed successfully'
                }
            else:
                # Move to next stage
                workflow['current_stage'] = current_stage + 1
                next_stage = workflow['stages'][current_stage]
                workflow['timeout_date'] = self._calculate_timeout_date(next_stage['timeout_hours'])
                
                return {
                    'success': True,
                    'workflow_id': workflow_id,
                    'status': 'pending',
                    'next_stage': next_stage['name'],
                    'message': f'Stage {current_stage} approved. Awaiting {next_stage["name"]}'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error approving workflow: {str(e)}'
            }
    
    def reject_workflow(self, workflow_id: str, rejector: str, reason: str) -> Dict:
        """
        Reject a workflow
        """
        try:
            workflow = self._get_workflow_by_id(workflow_id)
            if not workflow:
                return {
                    'success': False,
                    'error': 'Workflow not found'
                }
            
            if workflow['status'] != 'pending':
                return {
                    'success': False,
                    'error': f'Workflow is not pending (current status: {workflow["status"]})'
                }
            
            current_stage = workflow['current_stage']
            stage_info = workflow['stages'][current_stage - 1]
            
            # Check if rejector has permission for this stage
            if not self._can_approve_stage(rejector, stage_info):
                return {
                    'success': False,
                    'error': f'User {rejector} does not have permission to reject this stage'
                }
            
            # Record rejection
            rejection_entry = {
                'stage': current_stage,
                'stage_name': stage_info['name'],
                'rejector': rejector,
                'action': 'rejected',
                'date': datetime.now(),
                'reason': reason
            }
            
            workflow['approval_history'].append(rejection_entry)
            workflow['status'] = 'rejected'
            workflow['rejected_date'] = datetime.now()
            workflow['rejection_reason'] = reason
            
            # Create rejection history entry
            self._create_approval_history_entry(workflow_id, 'rejected', rejector, {
                'reason': reason,
                'stage': current_stage
            })
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'status': 'rejected',
                'message': 'Workflow rejected successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error rejecting workflow: {str(e)}'
            }
    
    def escalate_workflow(self, workflow_id: str, escalator: str, escalated_to: str, reason: str) -> Dict:
        """
        Escalate a workflow to a higher authority
        """
        try:
            workflow = self._get_workflow_by_id(workflow_id)
            if not workflow:
                return {
                    'success': False,
                    'error': 'Workflow not found'
                }
            
            if workflow['status'] != 'pending':
                return {
                    'success': False,
                    'error': f'Workflow is not pending (current status: {workflow["status"]})'
                }
            
            current_stage = workflow['current_stage']
            stage_info = workflow['stages'][current_stage - 1]
            
            # Check if escalation is allowed for this stage
            if not stage_info.get('can_escalate', False):
                return {
                    'success': False,
                    'error': 'Escalation is not allowed for this stage'
                }
            
            # Record escalation
            escalation_entry = {
                'stage': current_stage,
                'stage_name': stage_info['name'],
                'escalator': escalator,
                'action': 'escalated',
                'date': datetime.now(),
                'escalated_to': escalated_to,
                'reason': reason
            }
            
            workflow['approval_history'].append(escalation_entry)
            workflow['escalated'] = True
            workflow['escalated_to'] = escalated_to
            workflow['escalated_date'] = datetime.now()
            
            # Create escalation history entry
            self._create_approval_history_entry(workflow_id, 'escalated', escalator, {
                'escalated_to': escalated_to,
                'reason': reason,
                'stage': current_stage
            })
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'status': 'escalated',
                'escalated_to': escalated_to,
                'message': f'Workflow escalated to {escalated_to}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error escalating workflow: {str(e)}'
            }
    
    def get_workflows(self, filters: Dict = None) -> List[Dict]:
        """
        Get workflows with optional filtering
        """
        workflows = self.workflows
        
        if filters:
            if 'status' in filters:
                workflows = [w for w in workflows if w['status'] == filters['status']]
            
            if 'type' in filters:
                workflows = [w for w in workflows if w['type'] == filters['type']]
            
            if 'initiator' in filters:
                workflows = [w for w in workflows if w['initiator'] == filters['initiator']]
            
            if 'date_from' in filters:
                workflows = [w for w in workflows if w['initiated_date'] >= filters['date_from']]
            
            if 'date_to' in filters:
                workflows = [w for w in workflows if w['initiated_date'] <= filters['date_to']]
        
        return sorted(workflows, key=lambda x: x['initiated_date'], reverse=True)
    
    def get_pending_approvals(self, user: str) -> List[Dict]:
        """
        Get pending approvals for a specific user
        """
        pending_workflows = []
        
        for workflow in self.workflows:
            if workflow['status'] == 'pending':
                current_stage = workflow['current_stage']
                stage_info = workflow['stages'][current_stage - 1]
                
                # Check if user can approve this stage
                if self._can_approve_stage(user, stage_info):
                    pending_workflows.append(workflow)
        
        return pending_workflows
    
    def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict]:
        """
        Get specific workflow by ID
        """
        return self._get_workflow_by_id(workflow_id)
    
    def _get_workflow_by_id(self, workflow_id: str) -> Optional[Dict]:
        """
        Internal method to find workflow by ID
        """
        for workflow in self.workflows:
            if workflow['id'] == workflow_id:
                return workflow
        return None
    
    def _determine_required_stages(self, template: Dict, amount: float) -> List[Dict]:
        """
        Determine required stages based on amount thresholds
        """
        thresholds = template['amount_thresholds']
        all_stages = template['stages']
        
        if amount <= thresholds['low']:
            return all_stages[:1]  # Only first stage
        elif amount <= thresholds['medium']:
            return all_stages[:2]  # First two stages
        else:
            return all_stages  # All stages
    
    def _calculate_timeout_date(self, timeout_hours: int) -> datetime:
        """
        Calculate timeout date for a stage
        """
        return datetime.now() + timedelta(hours=timeout_hours)
    
    def _can_approve_stage(self, user: str, stage_info: Dict) -> bool:
        """
        Check if user can approve a specific stage
        """
        # Mock user roles - replace with actual user role system
        user_roles = {
            'manager': ['manager', 'finance_manager', 'director', 'controller'],
            'finance_manager': ['finance_manager', 'director', 'controller'],
            'director': ['director'],
            'controller': ['controller'],
            'supervisor': ['supervisor', 'inventory_manager'],
            'inventory_manager': ['inventory_manager'],
            'accountant': ['accountant', 'controller'],
            'finance': ['finance', 'controller']
        }
        
        required_role = stage_info['role']
        user_role_list = user_roles.get(user, [])
        
        return required_role in user_role_list
    
    def _create_approval_history_entry(self, workflow_id: str, action: str, user: str, data: Dict) -> None:
        """
        Create approval history entry
        """
        history_entry = {
            'id': f"HIST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'workflow_id': workflow_id,
            'action': action,
            'user': user,
            'timestamp': datetime.now(),
            'data': data
        }
        
        self.approval_history.append(history_entry)
    
    def _execute_approved_action(self, workflow: Dict) -> None:
        """
        Execute the action after workflow approval
        """
        workflow_type = workflow['type']
        reference_id = workflow['reference_id']
        
        if workflow_type == 'purchase_order':
            # Approve purchase order
            print(f"Approving purchase order: {reference_id}")
        elif workflow_type == 'stock_adjustment':
            # Approve stock adjustment
            print(f"Approving stock adjustment: {reference_id}")
        elif workflow_type == 'journal_entry':
            # Approve journal entry
            print(f"Approving journal entry: {reference_id}")
        elif workflow_type == 'expense_report':
            # Approve expense report
            print(f"Approving expense report: {reference_id}")

# Global instance
approval_workflow = ApprovalWorkflow()



