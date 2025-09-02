from datetime import datetime
from typing import Dict, List, Optional
import threading
import time
from contextlib import contextmanager

class ConcurrencyManager:
    """Enterprise-grade concurrency management for inventory operations"""
    
    def __init__(self):
        self.lock_manager = threading.Lock()
        self.active_locks = {}
        self.transaction_timeout = 30
    
    def get_optimistic_lock_version(self, table_name: str, record_id: int) -> int:
        """Get current version number for optimistic locking"""
        try:
            # Mock implementation - replace with actual database query
            return int(time.time()) % 1000
        except Exception as e:
            print(f"Error getting version number: {e}")
            return 0
    
    def update_with_optimistic_lock(self, table_name: str, record_id: int, 
                                  data: Dict, expected_version: int) -> Dict:
        """Update record with optimistic locking to prevent race conditions"""
        try:
            # Simulate version check
            current_version = self.get_optimistic_lock_version(table_name, record_id)
            
            if current_version != expected_version:
                return {
                    'success': False,
                    'error': 'CONCURRENCY_CONFLICT',
                    'message': 'Record was modified by another user. Please refresh and try again.',
                    'current_version': current_version
                }
            
            # Simulate successful update
            return {
                'success': True,
                'message': 'Record updated successfully',
                'new_version': expected_version + 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'UPDATE_FAILED',
                'message': f'Error updating record: {str(e)}'
            }
    
    def process_stock_adjustment_with_locking(self, adjustment_data: Dict) -> Dict:
        """Process stock adjustment with full concurrency protection"""
        item_id = adjustment_data.get('item_id')
        warehouse_id = adjustment_data.get('warehouse_id')
        quantity = adjustment_data.get('quantity', 0)
        
        lock_key = f"stock_{item_id}_{warehouse_id}"
        
        with self.lock_manager:
            if lock_key in self.active_locks:
                return {
                    'success': False,
                    'error': 'LOCK_ACQUISITION_FAILED',
                    'message': 'Item is currently being processed by another operation'
                }
            
            self.active_locks[lock_key] = datetime.utcnow()
        
        try:
            # Simulate stock adjustment processing
            time.sleep(0.1)  # Simulate processing time
            
            return {
                'success': True,
                'message': 'Stock adjustment processed successfully',
                'transaction_id': f"ADJ-{int(time.time())}",
                'new_quantity': 100 + quantity  # Mock new quantity
            }
            
        finally:
            # Release lock
            with self.lock_manager:
                if lock_key in self.active_locks:
                    del self.active_locks[lock_key]
    
    def get_concurrency_metrics(self) -> Dict:
        """Get concurrency performance metrics"""
        with self.lock_manager:
            return {
                'active_locks': len(self.active_locks),
                'lock_details': list(self.active_locks.keys()),
                'timestamp': datetime.utcnow().isoformat()
            }

# Global concurrency manager instance
concurrency_manager = ConcurrencyManager()
