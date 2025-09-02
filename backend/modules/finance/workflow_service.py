"""
Automated Workflow Service for Business Process Automation
Handles approval workflows, automated alerts, and scheduled tasks
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import and_, or_, func
from app import db
from .advanced_models import (
    ChartOfAccounts, GeneralLedgerEntry
)
from modules.inventory.advanced_models import InventoryProduct, InventoryTransaction, StockLevel

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowService:
    """
    Automated workflow management service
    """
    
    # Workflow Types
    WORKFLOW_TYPES = {
        'approval': 'Approval Workflow',
        'alert': 'Automated Alert',
        'scheduled': 'Scheduled Task',
        'notification': 'System Notification'
    }
    
    # Alert Types
    ALERT_TYPES = {
        'low_stock': 'Low Stock Alert',
        'overstock': 'Overstock Alert',
        'budget_exceeded': 'Budget Exceeded',
        'payment_due': 'Payment Due',
        'reconciliation_needed': 'Reconciliation Needed',
        'audit_required': 'Audit Required'
    }
    
    @classmethod
    def check_low_stock_alerts(cls) -> List[Dict[str, Any]]:
        """
        Check for low stock items and generate alerts
        """
        try:
            alerts = []
            
            # Get all stock levels
            stock_levels = StockLevel.query.join(InventoryProduct).filter(
                InventoryProduct.is_active == True
            ).all()
            
            for stock in stock_levels:
                if stock.quantity_on_hand <= stock.product.min_stock_level:
                    alert = {
                        'type': 'low_stock',
                        'severity': 'high' if stock.quantity_on_hand == 0 else 'medium',
                        'product_name': stock.product.name,
                        'sku': stock.product.sku,
                        'current_stock': stock.quantity_on_hand,
                        'min_stock': stock.product.min_stock_level,
                        'recommended_order': stock.product.max_stock_level - stock.quantity_on_hand,
                        'message': f"Low stock alert: {stock.product.name} (SKU: {stock.product.sku}) - Current: {stock.quantity_on_hand}, Min: {stock.product.min_stock_level}",
                        'created_at': datetime.utcnow().isoformat()
                    }
                    alerts.append(alert)
            
            logger.info(f"🔔 Generated {len(alerts)} low stock alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error checking low stock alerts: {str(e)}")
            return []
    
    @classmethod
    def check_overstock_alerts(cls) -> List[Dict[str, Any]]:
        """
        Check for overstock items and generate alerts
        """
        try:
            alerts = []
            
            stock_levels = StockLevel.query.join(InventoryProduct).filter(
                InventoryProduct.is_active == True
            ).all()
            
            for stock in stock_levels:
                if stock.quantity_on_hand > stock.product.max_stock_level:
                    excess_stock = stock.quantity_on_hand - stock.product.max_stock_level
                    excess_value = excess_stock * (stock.unit_cost or 0)
                    
                    alert = {
                        'type': 'overstock',
                        'severity': 'medium',
                        'product_name': stock.product.name,
                        'sku': stock.product.sku,
                        'current_stock': stock.quantity_on_hand,
                        'max_stock': stock.product.max_stock_level,
                        'excess_stock': excess_stock,
                        'excess_value': excess_value,
                        'message': f"Overstock alert: {stock.product.name} (SKU: {stock.product.sku}) - Current: {stock.quantity_on_hand}, Max: {stock.product.max_stock_level}",
                        'created_at': datetime.utcnow().isoformat()
                    }
                    alerts.append(alert)
            
            logger.info(f"📦 Generated {len(alerts)} overstock alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error checking overstock alerts: {str(e)}")
            return []
    
    @classmethod
    def check_budget_alerts(cls, budget_limits: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Check for budget exceeded alerts
        """
        try:
            alerts = []
            
            # Get account balances
            account_balances = db.session.query(
                ChartOfAccounts.account_code,
                ChartOfAccounts.account_name,
                func.sum(GeneralLedgerEntry.debit_amount).label('total_debits'),
                func.sum(GeneralLedgerEntry.credit_amount).label('total_credits')
            ).join(GeneralLedgerEntry).group_by(
                ChartOfAccounts.id
            ).all()
            
            for account in account_balances:
                account_code = account.account_code
                if account_code in budget_limits:
                    balance = (account.total_credits or 0) - (account.total_debits or 0)
                    budget_limit = budget_limits[account_code]
                    
                    if abs(balance) > budget_limit:
                        alert = {
                            'type': 'budget_exceeded',
                            'severity': 'high',
                            'account_code': account_code,
                            'account_name': account.account_name,
                            'current_balance': balance,
                            'budget_limit': budget_limit,
                            'excess_amount': abs(balance) - budget_limit,
                            'message': f"Budget exceeded: {account.account_name} - Balance: ${balance:,.2f}, Limit: ${budget_limit:,.2f}",
                            'created_at': datetime.utcnow().isoformat()
                        }
                        alerts.append(alert)
            
            logger.info(f"💰 Generated {len(alerts)} budget alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error checking budget alerts: {str(e)}")
            return []
    
    @classmethod
    def check_payment_due_alerts(cls, days_threshold: int = 30) -> List[Dict[str, Any]]:
        """
        Check for payments due alerts
        """
        try:
            alerts = []
            
            # Get accounts payable entries
            ap_accounts = ChartOfAccounts.query.filter(
                ChartOfAccounts.account_type == 'liability',
                ChartOfAccounts.account_name.ilike('%payable%')
            ).all()
            
            for account in ap_accounts:
                # Get recent transactions
                recent_transactions = GeneralLedgerEntry.query.filter(
                    GeneralLedgerEntry.account_id == account.id,
                    GeneralLedgerEntry.entry_date <= datetime.utcnow() - timedelta(days=days_threshold)
                ).all()
                
                for transaction in recent_transactions:
                    alert = {
                        'type': 'payment_due',
                        'severity': 'medium',
                        'account_name': account.account_name,
                        'transaction_date': transaction.entry_date.isoformat(),
                        'amount': float(transaction.debit_amount or 0),
                        'days_overdue': (datetime.utcnow() - transaction.entry_date).days,
                        'message': f"Payment due: {account.account_name} - Amount: ${transaction.debit_amount or 0:,.2f}, Due: {transaction.entry_date.strftime('%Y-%m-%d')}",
                        'created_at': datetime.utcnow().isoformat()
                    }
                    alerts.append(alert)
            
            logger.info(f"💳 Generated {len(alerts)} payment due alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error checking payment due alerts: {str(e)}")
            return []
    
    @classmethod
    def generate_daily_reports(cls) -> Dict[str, Any]:
        """
        Generate daily automated reports
        """
        try:
            today = datetime.utcnow().date()
            
            # Get today's transactions
            today_transactions = GeneralLedgerEntry.query.filter(
                func.date(GeneralLedgerEntry.entry_date) == today
            ).all()
            
            # Get today's inventory transactions
            today_inventory = AdvancedInventoryTransaction.query.filter(
                func.date(AdvancedInventoryTransaction.transaction_date) == today
            ).all()
            
            # Calculate metrics
            total_debits = sum([t.debit_amount for t in today_transactions])
            total_credits = sum([t.credit_amount for t in today_transactions])
            
            inventory_in = sum([t.quantity for t in today_inventory if t.transaction_type == 'IN'])
            inventory_out = sum([t.quantity for t in today_inventory if t.transaction_type == 'OUT'])
            
            report = {
                'date': today.isoformat(),
                'financial_summary': {
                    'total_transactions': len(today_transactions),
                    'total_debits': float(total_debits),
                    'total_credits': float(total_credits),
                    'net_change': float(total_credits - total_debits)
                },
                'inventory_summary': {
                    'total_transactions': len(today_inventory),
                    'inventory_in': inventory_in,
                    'inventory_out': inventory_out,
                    'net_inventory_change': inventory_in - inventory_out
                },
                'alerts': {
                    'low_stock': len(cls.check_low_stock_alerts()),
                    'overstock': len(cls.check_overstock_alerts()),
                    'budget_exceeded': 0,  # Would need budget limits
                    'payment_due': len(cls.check_payment_due_alerts())
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"📊 Generated daily report for {today}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating daily report: {str(e)}")
            return {}
    
    @classmethod
    def create_approval_workflow(cls, workflow_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an approval workflow
        """
        try:
            workflow = {
                'id': f"wf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'type': workflow_type,
                'status': 'pending',
                'data': data,
                'created_at': datetime.utcnow().isoformat(),
                'approvers': data.get('approvers', []),
                'current_approver': data.get('approvers', [])[0] if data.get('approvers') else None,
                'approval_history': []
            }
            
            logger.info(f"✅ Created approval workflow: {workflow['id']}")
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Error creating approval workflow: {str(e)}")
            return {}
    
    @classmethod
    def process_approval(cls, workflow_id: str, approver: str, approved: bool, comments: str = "") -> Dict[str, Any]:
        """
        Process an approval decision
        """
        try:
            # In a real implementation, this would update the workflow in the database
            result = {
                'workflow_id': workflow_id,
                'approver': approver,
                'approved': approved,
                'comments': comments,
                'processed_at': datetime.utcnow().isoformat(),
                'status': 'approved' if approved else 'rejected'
            }
            
            logger.info(f"✅ Processed approval: {workflow_id} by {approver} - {'Approved' if approved else 'Rejected'}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing approval: {str(e)}")
            return {}
    
    @classmethod
    def schedule_task(cls, task_type: str, schedule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a recurring task
        """
        try:
            task = {
                'id': f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'type': task_type,
                'schedule': schedule,
                'data': data,
                'status': 'scheduled',
                'next_run': cls._calculate_next_run(schedule),
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"⏰ Scheduled task: {task['id']} - Next run: {task['next_run']}")
            return task
            
        except Exception as e:
            logger.error(f"❌ Error scheduling task: {str(e)}")
            return {}
    
    @classmethod
    def _calculate_next_run(cls, schedule: Dict[str, Any]) -> str:
        """
        Calculate the next run time based on schedule
        """
        try:
            frequency = schedule.get('frequency', 'daily')
            now = datetime.utcnow()
            
            if frequency == 'daily':
                next_run = now + timedelta(days=1)
            elif frequency == 'weekly':
                next_run = now + timedelta(weeks=1)
            elif frequency == 'monthly':
                # Simple monthly calculation
                next_run = now + timedelta(days=30)
            else:
                next_run = now + timedelta(days=1)
            
            return next_run.isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error calculating next run: {str(e)}")
            return (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    @classmethod
    def get_workflow_status(cls, workflow_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow
        """
        try:
            # In a real implementation, this would query the database
            return {
                'workflow_id': workflow_id,
                'status': 'pending',
                'current_step': 1,
                'total_steps': 3,
                'created_at': datetime.utcnow().isoformat(),
                'estimated_completion': (datetime.utcnow() + timedelta(days=2)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting workflow status: {str(e)}")
            return {}
    
    @classmethod
    def run_scheduled_tasks(cls) -> List[Dict[str, Any]]:
        """
        Run all scheduled tasks that are due
        """
        try:
            results = []
            
            # Check for daily tasks
            daily_tasks = [
                {'type': 'daily_report', 'action': cls.generate_daily_reports},
                {'type': 'low_stock_check', 'action': cls.check_low_stock_alerts},
                {'type': 'overstock_check', 'action': cls.check_overstock_alerts}
            ]
            
            for task in daily_tasks:
                try:
                    result = task['action']()
                    results.append({
                        'task_type': task['type'],
                        'status': 'completed',
                        'result': result,
                        'executed_at': datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    results.append({
                        'task_type': task['type'],
                        'status': 'failed',
                        'error': str(e),
                        'executed_at': datetime.utcnow().isoformat()
                    })
            
            logger.info(f"🔄 Executed {len(results)} scheduled tasks")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error running scheduled tasks: {str(e)}")
            return []

