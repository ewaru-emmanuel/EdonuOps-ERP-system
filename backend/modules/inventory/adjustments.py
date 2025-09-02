from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal
import json

class StockAdjustment:
    """Comprehensive Stock Adjustment System with Reason Codes and Approval Workflows"""
    
    def __init__(self):
        self.adjustments = []
        self.approval_workflows = []
        self.audit_trail = []
        
        # Standard reason codes
        self.reason_codes = {
            'damage': {
                'code': 'DAM',
                'name': 'Damage',
                'description': 'Items damaged during handling or storage',
                'requires_approval': True,
                'approval_threshold': 1000.00
            },
            'theft': {
                'code': 'THF',
                'name': 'Theft',
                'description': 'Items stolen or missing due to theft',
                'requires_approval': True,
                'approval_threshold': 500.00
            },
            'counting_error': {
                'code': 'CNT',
                'name': 'Counting Error',
                'description': 'Correction of physical count discrepancies',
                'requires_approval': False,
                'approval_threshold': 0.00
            },
            'expiry': {
                'code': 'EXP',
                'name': 'Expiry',
                'description': 'Items expired and disposed of',
                'requires_approval': True,
                'approval_threshold': 500.00
            },
            'quality_control': {
                'code': 'QC',
                'name': 'Quality Control',
                'description': 'Items rejected during quality inspection',
                'requires_approval': True,
                'approval_threshold': 1000.00
            },
            'system_correction': {
                'code': 'SYS',
                'name': 'System Correction',
                'description': 'Correction of system errors or data entry mistakes',
                'requires_approval': True,
                'approval_threshold': 2000.00
            },
            'return_to_supplier': {
                'code': 'RTS',
                'name': 'Return to Supplier',
                'description': 'Items returned to supplier for credit or replacement',
                'requires_approval': True,
                'approval_threshold': 1000.00
            },
            'sample_removal': {
                'code': 'SMP',
                'name': 'Sample Removal',
                'description': 'Items removed for sampling or testing',
                'requires_approval': False,
                'approval_threshold': 0.00
            },
            'warehouse_transfer': {
                'code': 'TRF',
                'name': 'Warehouse Transfer',
                'description': 'Items transferred between warehouses',
                'requires_approval': False,
                'approval_threshold': 0.00
            },
            'obsolete': {
                'code': 'OBS',
                'name': 'Obsolete',
                'description': 'Items no longer usable or saleable',
                'requires_approval': True,
                'approval_threshold': 500.00
            }
        }
    
    def create_adjustment(self, adjustment_data: Dict) -> Dict:
        """
        Create a new stock adjustment with reason code
        """
        try:
            # Validate required fields
            required_fields = ['item_id', 'quantity', 'reason_code', 'warehouse_id']
            for field in required_fields:
                if field not in adjustment_data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Validate reason code
            reason_code = adjustment_data['reason_code']
            if reason_code not in self.reason_codes:
                return {
                    'success': False,
                    'error': f'Invalid reason code: {reason_code}'
                }
            
            # Calculate adjustment amount
            unit_cost = adjustment_data.get('unit_cost', 0)
            quantity = adjustment_data['quantity']
            adjustment_amount = abs(quantity * unit_cost)
            
            # Determine if approval is required
            reason_info = self.reason_codes[reason_code]
            requires_approval = reason_info['requires_approval'] and adjustment_amount > reason_info['approval_threshold']
            
            # Create adjustment record
            adjustment_id = f"ADJ-{datetime.now().strftime('%Y%m%d')}-{len(self.adjustments) + 1:03d}"
            
            adjustment = {
                'id': adjustment_id,
                'item_id': adjustment_data['item_id'],
                'item_name': adjustment_data.get('item_name', ''),
                'quantity': quantity,
                'unit_cost': unit_cost,
                'adjustment_amount': adjustment_amount,
                'reason_code': reason_code,
                'reason_name': reason_info['name'],
                'reason_description': reason_info['description'],
                'warehouse_id': adjustment_data['warehouse_id'],
                'warehouse_name': adjustment_data.get('warehouse_name', ''),
                'location_bin': adjustment_data.get('location_bin', ''),
                'batch_lot_number': adjustment_data.get('batch_lot_number', ''),
                'serial_number': adjustment_data.get('serial_number', ''),
                'notes': adjustment_data.get('notes', ''),
                'created_by': adjustment_data.get('created_by', 'system'),
                'created_date': datetime.now(),
                'status': 'pending_approval' if requires_approval else 'approved',
                'approved_by': None,
                'approved_date': None,
                'journal_entry_id': None,
                'metadata': {
                    'adjustment_type': 'decrease' if quantity < 0 else 'increase',
                    'requires_approval': requires_approval,
                    'approval_threshold': reason_info['approval_threshold']
                }
            }
            
            self.adjustments.append(adjustment)
            
            # Create audit trail entry
            self._create_audit_entry(adjustment_id, 'created', adjustment_data.get('created_by', 'system'), adjustment)
            
            # Create approval workflow if required
            if requires_approval:
                workflow = self._create_approval_workflow(adjustment_id, adjustment_data)
                self.approval_workflows.append(workflow)
            
            return {
                'success': True,
                'adjustment_id': adjustment_id,
                'requires_approval': requires_approval,
                'adjustment': adjustment,
                'message': 'Stock adjustment created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating stock adjustment: {str(e)}'
            }
    
    def approve_adjustment(self, adjustment_id: str, approver: str, approval_notes: str = '') -> Dict:
        """
        Approve a stock adjustment
        """
        try:
            # Find the adjustment
            adjustment = self._get_adjustment_by_id(adjustment_id)
            if not adjustment:
                return {
                    'success': False,
                    'error': 'Adjustment not found'
                }
            
            if adjustment['status'] != 'pending_approval':
                return {
                    'success': False,
                    'error': f'Adjustment is not pending approval (current status: {adjustment["status"]})'
                }
            
            # Update adjustment status
            adjustment['status'] = 'approved'
            adjustment['approved_by'] = approver
            adjustment['approved_date'] = datetime.now()
            
            # Create audit trail entry
            self._create_audit_entry(adjustment_id, 'approved', approver, {
                'approval_notes': approval_notes,
                'approved_by': approver,
                'approved_date': datetime.now()
            })
            
            # Post journal entry
            journal_result = self._post_journal_entry(adjustment)
            if journal_result['success']:
                adjustment['journal_entry_id'] = journal_result['journal_entry_id']
            
            # Update inventory levels
            self._update_inventory_levels(adjustment)
            
            return {
                'success': True,
                'adjustment_id': adjustment_id,
                'journal_entry_id': adjustment.get('journal_entry_id'),
                'message': 'Stock adjustment approved and posted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error approving adjustment: {str(e)}'
            }
    
    def reject_adjustment(self, adjustment_id: str, rejector: str, rejection_reason: str) -> Dict:
        """
        Reject a stock adjustment
        """
        try:
            # Find the adjustment
            adjustment = self._get_adjustment_by_id(adjustment_id)
            if not adjustment:
                return {
                    'success': False,
                    'error': 'Adjustment not found'
                }
            
            if adjustment['status'] != 'pending_approval':
                return {
                    'success': False,
                    'error': f'Adjustment is not pending approval (current status: {adjustment["status"]})'
                }
            
            # Update adjustment status
            adjustment['status'] = 'rejected'
            adjustment['rejected_by'] = rejector
            adjustment['rejected_date'] = datetime.now()
            adjustment['rejection_reason'] = rejection_reason
            
            # Create audit trail entry
            self._create_audit_entry(adjustment_id, 'rejected', rejector, {
                'rejection_reason': rejection_reason,
                'rejected_by': rejector,
                'rejected_date': datetime.now()
            })
            
            return {
                'success': True,
                'adjustment_id': adjustment_id,
                'message': 'Stock adjustment rejected successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error rejecting adjustment: {str(e)}'
            }
    
    def get_adjustments(self, filters: Dict = None) -> List[Dict]:
        """
        Get stock adjustments with optional filtering
        """
        adjustments = self.adjustments
        
        if filters:
            if 'status' in filters:
                adjustments = [a for a in adjustments if a['status'] == filters['status']]
            
            if 'reason_code' in filters:
                adjustments = [a for a in adjustments if a['reason_code'] == filters['reason_code']]
            
            if 'warehouse_id' in filters:
                adjustments = [a for a in adjustments if a['warehouse_id'] == filters['warehouse_id']]
            
            if 'date_from' in filters:
                adjustments = [a for a in adjustments if a['created_date'] >= filters['date_from']]
            
            if 'date_to' in filters:
                adjustments = [a for a in adjustments if a['created_date'] <= filters['date_to']]
        
        return sorted(adjustments, key=lambda x: x['created_date'], reverse=True)
    
    def get_adjustment_by_id(self, adjustment_id: str) -> Optional[Dict]:
        """
        Get specific adjustment by ID
        """
        return self._get_adjustment_by_id(adjustment_id)
    
    def get_reason_codes(self) -> Dict:
        """
        Get all available reason codes
        """
        return self.reason_codes
    
    def get_adjustment_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """
        Get summary statistics for adjustments
        """
        try:
            adjustments = self.get_adjustments()
            
            if start_date:
                adjustments = [a for a in adjustments if a['created_date'] >= start_date]
            if end_date:
                adjustments = [a for a in adjustments if a['created_date'] <= end_date]
            
            total_adjustments = len(adjustments)
            total_amount = sum(a['adjustment_amount'] for a in adjustments)
            
            # By status
            by_status = {}
            for adj in adjustments:
                status = adj['status']
                if status not in by_status:
                    by_status[status] = {'count': 0, 'amount': 0}
                by_status[status]['count'] += 1
                by_status[status]['amount'] += adj['adjustment_amount']
            
            # By reason code
            by_reason = {}
            for adj in adjustments:
                reason = adj['reason_code']
                if reason not in by_reason:
                    by_reason[reason] = {'count': 0, 'amount': 0, 'name': adj['reason_name']}
                by_reason[reason]['count'] += 1
                by_reason[reason]['amount'] += adj['adjustment_amount']
            
            return {
                'total_adjustments': total_adjustments,
                'total_amount': total_amount,
                'by_status': by_status,
                'by_reason': by_reason,
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
        except Exception as e:
            return {
                'error': f'Error generating adjustment summary: {str(e)}'
            }
    
    def get_pending_approvals(self) -> List[Dict]:
        """
        Get all adjustments pending approval
        """
        return self.get_adjustments({'status': 'pending_approval'})
    
    def _get_adjustment_by_id(self, adjustment_id: str) -> Optional[Dict]:
        """
        Internal method to find adjustment by ID
        """
        for adjustment in self.adjustments:
            if adjustment['id'] == adjustment_id:
                return adjustment
        return None
    
    def _create_approval_workflow(self, adjustment_id: str, adjustment_data: Dict) -> Dict:
        """
        Create approval workflow for an adjustment
        """
        workflow = {
            'id': f"WF-{adjustment_id}",
            'adjustment_id': adjustment_id,
            'type': 'stock_adjustment',
            'created_date': datetime.now(),
            'status': 'pending',
            'approvers': adjustment_data.get('approvers', ['manager']),
            'current_approver': 0,
            'approval_history': [],
            'metadata': adjustment_data
        }
        
        return workflow
    
    def _create_audit_entry(self, adjustment_id: str, action: str, user: str, data: Dict) -> None:
        """
        Create audit trail entry
        """
        audit_entry = {
            'id': f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'adjustment_id': adjustment_id,
            'action': action,
            'user': user,
            'timestamp': datetime.now(),
            'data': data
        }
        
        self.audit_trail.append(audit_entry)
    
    def _post_journal_entry(self, adjustment: Dict) -> Dict:
        """
        Post journal entry for approved adjustment
        """
        try:
            # Import the auto journal engine
            from modules.integration.auto_journal import auto_journal_engine
            
            adjustment_data = {
                'adjustment_amount': adjustment['adjustment_amount'],
                'adjustment_type': adjustment['metadata']['adjustment_type'],
                'reason': adjustment['reason_name'],
                'adjustment_date': adjustment['approved_date'],
                'adjustment_reference': adjustment['id'],
                'item_id': adjustment['item_id']
            }
            
            result = auto_journal_engine.on_inventory_adjustment(adjustment_data)
            
            return {
                'success': result['success'],
                'journal_entry_id': result.get('journal_entry_id')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error posting journal entry: {str(e)}'
            }
    
    def _update_inventory_levels(self, adjustment: Dict) -> None:
        """
        Update inventory levels after adjustment
        """
        # This would update the actual inventory levels in the database
        # For now, we'll just log the action
        print(f"Updating inventory levels for adjustment {adjustment['id']}")
        print(f"Item: {adjustment['item_id']}, Quantity: {adjustment['quantity']}")

# Global instance
stock_adjustment = StockAdjustment()



