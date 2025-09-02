import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, func, text
from sqlalchemy.orm import sessionmaker
from app import db
from modules.inventory.advanced_models import (
    StockLevel, AdvancedInventoryTransaction, AdvancedProduct, Location, 
    WarehouseActivity, PickList, PickListLine, AdvancedWarehouse
)

logger = logging.getLogger(__name__)

class DataIntegrityService:
    """Enterprise-grade data integrity service for inventory management"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.last_check_time = None
        self.check_results = {}
        self.is_running = False
        
    def run_nightly_reconciliation(self) -> Dict:
        """
        Nightly StockLevel reconciliation check
        Compares calculated stock vs actual stock levels
        """
        with self.lock:
            try:
                logger.info("🔍 Starting nightly StockLevel reconciliation check")
                start_time = datetime.utcnow()
                
                results = {
                    'check_time': start_time.isoformat(),
                    'status': 'running',
                    'discrepancies': [],
                    'summary': {},
                    'recommendations': []
                }
                
                # Get all stock levels
                stock_levels = StockLevel.query.all()
                discrepancies = []
                
                for stock_level in stock_levels:
                    # Calculate expected stock from transactions
                    expected_stock = self._calculate_expected_stock(
                        stock_level.product_id, 
                        stock_level.location_id
                    )
                    
                    # Compare with actual stock
                    actual_stock = stock_level.quantity_on_hand
                    variance = actual_stock - expected_stock
                    
                    if abs(variance) > 0.01:  # Allow for small rounding differences
                        discrepancy = {
                            'product_id': stock_level.product_id,
                            'location_id': stock_level.location_id,
                            'product_name': stock_level.product.name if stock_level.product else 'Unknown',
                            'location_name': stock_level.location.name if stock_level.location else 'Unknown',
                            'expected_stock': expected_stock,
                            'actual_stock': actual_stock,
                            'variance': variance,
                            'variance_percentage': (variance / expected_stock * 100) if expected_stock > 0 else 0,
                            'severity': 'high' if abs(variance) > 10 else 'medium' if abs(variance) > 5 else 'low'
                        }
                        discrepancies.append(discrepancy)
                
                # Generate summary
                total_discrepancies = len(discrepancies)
                high_severity = len([d for d in discrepancies if d['severity'] == 'high'])
                medium_severity = len([d for d in discrepancies if d['severity'] == 'medium'])
                low_severity = len([d for d in discrepancies if d['severity'] == 'low'])
                
                results['discrepancies'] = discrepancies
                results['summary'] = {
                    'total_stock_levels': len(stock_levels),
                    'total_discrepancies': total_discrepancies,
                    'high_severity': high_severity,
                    'medium_severity': medium_severity,
                    'low_severity': low_severity,
                    'accuracy_rate': ((len(stock_levels) - total_discrepancies) / len(stock_levels) * 100) if stock_levels else 100
                }
                
                # Generate recommendations
                if high_severity > 0:
                    results['recommendations'].append({
                        'type': 'urgent',
                        'message': f'Immediate attention required: {high_severity} high-severity discrepancies detected',
                        'action': 'Review and correct stock levels immediately'
                    })
                
                if medium_severity > 5:
                    results['recommendations'].append({
                        'type': 'warning',
                        'message': f'Multiple medium-severity discrepancies: {medium_severity} items need review',
                        'action': 'Schedule stock count for affected locations'
                    })
                
                if total_discrepancies > 0:
                    results['recommendations'].append({
                        'type': 'info',
                        'message': f'Overall accuracy rate: {results["summary"]["accuracy_rate"]:.1f}%',
                        'action': 'Consider implementing cycle counting program'
                    })
                
                results['status'] = 'completed'
                results['duration_seconds'] = (datetime.utcnow() - start_time).total_seconds()
                
                # Store results for admin panel
                self.check_results = results
                self.last_check_time = start_time
                
                logger.info(f"✅ Nightly reconciliation completed: {total_discrepancies} discrepancies found")
                return results
                
            except Exception as e:
                logger.error(f"❌ Nightly reconciliation failed: {str(e)}")
                return {
                    'check_time': datetime.utcnow().isoformat(),
                    'status': 'failed',
                    'error': str(e),
                    'discrepancies': [],
                    'summary': {},
                    'recommendations': []
                }
    
    def _calculate_expected_stock(self, product_id: int, location_id: int) -> float:
        """Calculate expected stock from transaction history"""
        try:
            # Get all transactions for this product/location combination
            transactions = AdvancedInventoryTransaction.query.filter(
                and_(
                    AdvancedInventoryTransaction.product_id == product_id,
                    AdvancedInventoryTransaction.location_id == location_id
                )
            ).order_by(AdvancedInventoryTransaction.transaction_date).all()
            
            # Calculate running balance
            expected_stock = 0.0
            for transaction in transactions:
                if transaction.transaction_type in ['receipt', 'adjustment_positive']:
                    expected_stock += transaction.quantity
                elif transaction.transaction_type in ['issue', 'adjustment_negative']:
                    expected_stock -= transaction.quantity
                elif transaction.transaction_type == 'transfer_in':
                    expected_stock += transaction.quantity
                elif transaction.transaction_type == 'transfer_out':
                    expected_stock -= transaction.quantity
            
            return expected_stock
            
        except Exception as e:
            logger.error(f"Error calculating expected stock: {str(e)}")
            return 0.0
    
    def get_admin_panel_data(self) -> Dict:
        """Get data for admin panel view"""
        return {
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'is_running': self.is_running,
            'check_results': self.check_results,
            'system_health': self._get_system_health_metrics()
        }
    
    def _get_system_health_metrics(self) -> Dict:
        """Get overall system health metrics"""
        try:
            # Get basic counts
            total_products = AdvancedProduct.query.count()
            total_locations = Location.query.count()
            total_transactions = AdvancedInventoryTransaction.query.count()
            
            # Get recent activity
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_transactions = AdvancedInventoryTransaction.query.filter(
                AdvancedInventoryTransaction.transaction_date >= last_24h
            ).count()
            
            # Get active pick lists
            active_pick_lists = PickList.query.filter(
                PickList.status.in_(['in_progress', 'assigned'])
            ).count()
            
            # Get warehouse activity
            recent_activity = WarehouseActivity.query.filter(
                WarehouseActivity.activity_date >= last_24h
            ).count()
            
            return {
                'total_products': total_products,
                'total_locations': total_locations,
                'total_transactions': total_transactions,
                'recent_transactions_24h': recent_transactions,
                'active_pick_lists': active_pick_lists,
                'recent_warehouse_activity_24h': recent_activity,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health metrics: {str(e)}")
            return {}
    
    def run_concurrency_test(self, product_id: int, location_id: int) -> Dict:
        """
        Test for last-item scenario concurrency issues
        Simulates multiple users trying to pick the last item simultaneously
        """
        try:
            logger.info(f"🧪 Running concurrency test for product {product_id}, location {location_id}")
            
            # Get current stock level
            stock_level = StockLevel.query.filter(
                and_(
                    StockLevel.product_id == product_id,
                    StockLevel.location_id == location_id
                )
            ).first()
            
            if not stock_level or stock_level.quantity_on_hand <= 0:
                return {
                    'test_type': 'concurrency_last_item',
                    'status': 'skipped',
                    'reason': 'No stock available for testing'
                }
            
            # Simulate concurrent pick operations
            test_results = []
            threads = []
            results_lock = threading.Lock()
            
            def simulate_pick(thread_id: int, quantity: float):
                try:
                    with db.session.begin():
                        # Reload stock level to get latest data
                        current_stock = StockLevel.query.filter(
                            and_(
                                StockLevel.product_id == product_id,
                                StockLevel.location_id == location_id
                            )
                        ).with_for_update().first()
                        
                        if current_stock and current_stock.quantity_on_hand >= quantity:
                            # Simulate pick transaction
                            old_quantity = current_stock.quantity_on_hand
                            current_stock.quantity_on_hand -= quantity
                            
                            # Create transaction record
                            transaction = AdvancedInventoryTransaction(
                                product_id=product_id,
                                location_id=location_id,
                                transaction_type='issue',
                                quantity=quantity,
                                transaction_date=datetime.utcnow(),
                                reference_number=f'CONC_TEST_{thread_id}',
                                processed_by=f'TestUser_{thread_id}'
                            )
                            db.session.add(transaction)
                            
                            with results_lock:
                                test_results.append({
                                    'thread_id': thread_id,
                                    'success': True,
                                    'old_quantity': old_quantity,
                                    'new_quantity': current_stock.quantity_on_hand,
                                    'quantity_picked': quantity
                                })
                        else:
                            with results_lock:
                                test_results.append({
                                    'thread_id': thread_id,
                                    'success': False,
                                    'reason': 'Insufficient stock',
                                    'available_quantity': current_stock.quantity_on_hand if current_stock else 0
                                })
                                
                except Exception as e:
                    with results_lock:
                        test_results.append({
                            'thread_id': thread_id,
                            'success': False,
                            'error': str(e)
                        })
            
            # Create multiple threads to simulate concurrent picks
            initial_stock = stock_level.quantity_on_hand
            num_threads = min(5, int(initial_stock))  # Don't create more threads than available stock
            
            for i in range(num_threads):
                thread = threading.Thread(
                    target=simulate_pick,
                    args=(i, 1.0)  # Each thread tries to pick 1 unit
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Analyze results
            successful_picks = len([r for r in test_results if r['success']])
            failed_picks = len([r for r in test_results if not r['success']])
            
            # Check final stock level
            final_stock = StockLevel.query.filter(
                and_(
                    StockLevel.product_id == product_id,
                    StockLevel.location_id == location_id
                )
            ).first()
            
            expected_final_stock = initial_stock - successful_picks
            stock_accuracy = final_stock.quantity_on_hand == expected_final_stock
            
            return {
                'test_type': 'concurrency_last_item',
                'status': 'completed',
                'initial_stock': initial_stock,
                'final_stock': final_stock.quantity_on_hand if final_stock else 0,
                'expected_final_stock': expected_final_stock,
                'stock_accuracy': stock_accuracy,
                'successful_picks': successful_picks,
                'failed_picks': failed_picks,
                'total_threads': num_threads,
                'test_results': test_results,
                'concurrency_issues': not stock_accuracy,
                'recommendations': self._generate_concurrency_recommendations(
                    successful_picks, failed_picks, stock_accuracy
                )
            }
            
        except Exception as e:
            logger.error(f"Concurrency test failed: {str(e)}")
            return {
                'test_type': 'concurrency_last_item',
                'status': 'failed',
                'error': str(e)
            }
    
    def _generate_concurrency_recommendations(self, successful_picks: int, failed_picks: int, stock_accuracy: bool) -> List[Dict]:
        """Generate recommendations based on concurrency test results"""
        recommendations = []
        
        if not stock_accuracy:
            recommendations.append({
                'type': 'critical',
                'message': 'Stock level inconsistency detected during concurrent operations',
                'action': 'Implement row-level locking for stock level updates'
            })
        
        if failed_picks > 0:
            recommendations.append({
                'type': 'warning',
                'message': f'{failed_picks} concurrent pick operations failed',
                'action': 'Review transaction isolation levels and retry logic'
            })
        
        if successful_picks > 0:
            recommendations.append({
                'type': 'info',
                'message': f'{successful_picks} concurrent pick operations succeeded',
                'action': 'Monitor for race conditions in high-traffic scenarios'
            })
        
        return recommendations

# Global instance
data_integrity_service = DataIntegrityService()
