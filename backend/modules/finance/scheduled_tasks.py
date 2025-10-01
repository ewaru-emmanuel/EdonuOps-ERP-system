"""
Scheduled Tasks for Bank Reconciliation
Handles automated reconciliation processes
"""

import os
import logging
from datetime import datetime, timedelta
from flask import current_app
from .automated_reconciliation_service import automated_reconciliation_service

logger = logging.getLogger(__name__)

def run_daily_reconciliation():
    """Run daily reconciliation process"""
    try:
        logger.info("Starting daily reconciliation process")
        
        with current_app.app_context():
            results = automated_reconciliation_service.run_scheduled_reconciliations()
            
            logger.info(f"Daily reconciliation completed: {len(results)} accounts processed")
            return results
            
    except Exception as e:
        logger.error(f"Error in daily reconciliation: {str(e)}")
        return []

def run_weekly_reconciliation():
    """Run weekly reconciliation process"""
    try:
        logger.info("Starting weekly reconciliation process")
        
        with current_app.app_context():
            results = automated_reconciliation_service.run_scheduled_reconciliations()
            
            logger.info(f"Weekly reconciliation completed: {len(results)} accounts processed")
            return results
            
    except Exception as e:
        logger.error(f"Error in weekly reconciliation: {str(e)}")
        return []

def run_monthly_reconciliation():
    """Run monthly reconciliation process"""
    try:
        logger.info("Starting monthly reconciliation process")
        
        with current_app.app_context():
            results = automated_reconciliation_service.run_scheduled_reconciliations()
            
            logger.info(f"Monthly reconciliation completed: {len(results)} accounts processed")
            return results
            
    except Exception as e:
        logger.error(f"Error in monthly reconciliation: {str(e)}")
        return []

def run_immediate_reconciliation(bank_account_id: int):
    """Run immediate reconciliation for specific account"""
    try:
        logger.info(f"Starting immediate reconciliation for account {bank_account_id}")
        
        with current_app.app_context():
            from .payment_models import BankAccount
            
            account = BankAccount.query.get(bank_account_id)
            if not account:
                logger.error(f"Bank account {bank_account_id} not found")
                return None
            
            result = automated_reconciliation_service.process_account_reconciliation(account)
            
            logger.info(f"Immediate reconciliation completed for account {bank_account_id}")
            return result
            
    except Exception as e:
        logger.error(f"Error in immediate reconciliation: {str(e)}")
        return None

def check_reconciliation_alerts():
    """Check for reconciliation alerts and notifications"""
    try:
        logger.info("Checking reconciliation alerts")
        
        with current_app.app_context():
            from .payment_models import BankAccount, ReconciliationSession
            
            # Check for accounts that haven't been reconciled in a while
            alert_threshold = datetime.utcnow() - timedelta(days=7)
            
            accounts_needing_attention = BankAccount.query.filter(
                BankAccount.is_active == True,
                BankAccount.last_sync_at < alert_threshold
            ).all()
            
            if accounts_needing_attention:
                logger.warning(f"Found {len(accounts_needing_attention)} accounts needing reconciliation attention")
                
                # Send alerts (implement notification system)
                for account in accounts_needing_attention:
                    logger.warning(f"Account {account.account_name} needs reconciliation attention")
            
            return len(accounts_needing_attention)
            
    except Exception as e:
        logger.error(f"Error checking reconciliation alerts: {str(e)}")
        return 0

def cleanup_old_reconciliation_data():
    """Clean up old reconciliation data"""
    try:
        logger.info("Starting cleanup of old reconciliation data")
        
        with current_app.app_context():
            from .payment_models import ReconciliationSession, BankTransaction
            
            # Clean up old reconciliation sessions (older than 1 year)
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            
            old_sessions = ReconciliationSession.query.filter(
                ReconciliationSession.created_at < cutoff_date
            ).all()
            
            for session in old_sessions:
                # Archive or delete old sessions
                db.session.delete(session)
            
            db.session.commit()
            
            logger.info(f"Cleaned up {len(old_sessions)} old reconciliation sessions")
            return len(old_sessions)
            
    except Exception as e:
        logger.error(f"Error cleaning up old reconciliation data: {str(e)}")
        return 0

def generate_reconciliation_reports():
    """Generate reconciliation reports"""
    try:
        logger.info("Generating reconciliation reports")
        
        with current_app.app_context():
            from .payment_models import ReconciliationSession, BankAccount
            
            # Generate monthly reconciliation report
            report_data = {
                'month': datetime.utcnow().strftime('%Y-%m'),
                'total_sessions': 0,
                'completed_sessions': 0,
                'pending_sessions': 0,
                'accounts_processed': 0
            }
            
            # Get reconciliation statistics
            sessions = ReconciliationSession.query.filter(
                ReconciliationSession.created_at >= datetime.utcnow().replace(day=1)
            ).all()
            
            report_data['total_sessions'] = len(sessions)
            report_data['completed_sessions'] = len([s for s in sessions if s.status == 'completed'])
            report_data['pending_sessions'] = len([s for s in sessions if s.status == 'pending'])
            
            # Get unique accounts processed
            account_ids = set(s.bank_account_id for s in sessions)
            report_data['accounts_processed'] = len(account_ids)
            
            logger.info(f"Generated reconciliation report: {report_data}")
            return report_data
            
    except Exception as e:
        logger.error(f"Error generating reconciliation reports: {str(e)}")
        return {}

# Task registry for external schedulers
TASKS = {
    'daily_reconciliation': run_daily_reconciliation,
    'weekly_reconciliation': run_weekly_reconciliation,
    'monthly_reconciliation': run_monthly_reconciliation,
    'immediate_reconciliation': run_immediate_reconciliation,
    'check_alerts': check_reconciliation_alerts,
    'cleanup_data': cleanup_old_reconciliation_data,
    'generate_reports': generate_reconciliation_reports
}












