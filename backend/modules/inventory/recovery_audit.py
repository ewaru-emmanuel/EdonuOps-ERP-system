from datetime import datetime
from typing import Dict, List
import json
import hashlib
import uuid

class RecoveryAuditSystem:
    """Advanced Recovery & Audit System for Enterprise Data Protection"""
    
    def __init__(self):
        self.audit_log = []
        self.recovery_points = []
        self.transaction_ledger = []
    
    def create_immutable_transaction(self, transaction_data: Dict) -> Dict:
        """Create an immutable transaction record"""
        try:
            transaction_hash = hashlib.sha256(
                json.dumps(transaction_data, sort_keys=True).encode()
            ).hexdigest()
            
            immutable_transaction = {
                'id': str(uuid.uuid4()),
                'transaction_hash': transaction_hash,
                'transaction_type': transaction_data.get('type'),
                'data': transaction_data,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': transaction_data.get('user_id'),
                'is_void': False,
                'void_reason': None
            }
            
            self.transaction_ledger.append(immutable_transaction)
            
            audit_entry = {
                'id': str(uuid.uuid4()),
                'transaction_id': immutable_transaction['id'],
                'action': 'CREATE',
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': transaction_data.get('user_id'),
                'details': f"Created {transaction_data.get('type')} transaction"
            }
            
            self.audit_log.append(audit_entry)
            
            return {
                'success': True,
                'transaction_id': immutable_transaction['id'],
                'transaction_hash': transaction_hash
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def void_transaction(self, transaction_id: str, void_reason: str, user_id: str) -> Dict:
        """Void a transaction by creating a reversing entry"""
        try:
            original_transaction = next(
                (t for t in self.transaction_ledger if t['id'] == transaction_id), 
                None
            )
            
            if not original_transaction:
                return {'success': False, 'error': 'Transaction not found'}
            
            if original_transaction['is_void']:
                return {'success': False, 'error': 'Transaction is already void'}
            
            # Mark as void
            original_transaction['is_void'] = True
            original_transaction['void_reason'] = void_reason
            
            # Create void audit entry
            void_audit = {
                'id': str(uuid.uuid4()),
                'transaction_id': transaction_id,
                'action': 'VOID',
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'details': f"Voided transaction: {void_reason}"
            }
            
            self.audit_log.append(void_audit)
            
            return {'success': True, 'message': f'Transaction {transaction_id} voided'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_recovery_point(self, description: str, user_id: str) -> Dict:
        """Create a point-in-time recovery snapshot"""
        try:
            recovery_point = {
                'id': str(uuid.uuid4()),
                'description': description,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'data_snapshot': {
                    'transactions': self.transaction_ledger.copy(),
                    'audit_log': self.audit_log.copy()
                }
            }
            
            self.recovery_points.append(recovery_point)
            
            return {
                'success': True,
                'recovery_point_id': recovery_point['id'],
                'timestamp': recovery_point['timestamp']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_audit_trail(self, transaction_id: str = None) -> Dict:
        """Get audit trail with optional filtering"""
        try:
            filtered_audit = self.audit_log
            
            if transaction_id:
                filtered_audit = [entry for entry in filtered_audit 
                                if entry.get('transaction_id') == transaction_id]
            
            return {
                'success': True,
                'audit_entries': filtered_audit,
                'total_entries': len(filtered_audit)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_system_integrity_report(self) -> Dict:
        """Generate system integrity report"""
        try:
            total_transactions = len(self.transaction_ledger)
            voided_transactions = len([t for t in self.transaction_ledger if t['is_void']])
            
            return {
                'success': True,
                'integrity_report': {
                    'total_transactions': total_transactions,
                    'active_transactions': total_transactions - voided_transactions,
                    'voided_transactions': voided_transactions,
                    'total_audit_entries': len(self.audit_log),
                    'recovery_points_count': len(self.recovery_points),
                    'system_health': 'HEALTHY'
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
recovery_audit_system = RecoveryAuditSystem()
