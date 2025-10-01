"""
Automated Reconciliation Service
Handles scheduled reconciliation processes and notifications
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import current_app
from sqlalchemy import and_, or_
from .payment_models import BankAccount, BankTransaction, ReconciliationSession
from .advanced_models import GeneralLedgerEntry
from ..database import db

logger = logging.getLogger(__name__)

class AutomatedReconciliationService:
    """Service for automated reconciliation processes"""
    
    def __init__(self):
        self.notification_emails = os.getenv('RECONCILIATION_NOTIFICATION_EMAILS', '').split(',')
        self.auto_reconciliation_enabled = os.getenv('AUTO_RECONCILIATION_ENABLED', 'false').lower() == 'true'
    
    def run_scheduled_reconciliations(self):
        """Run scheduled reconciliation processes"""
        try:
            logger.info("Starting scheduled reconciliation process")
            
            # Get bank accounts that need reconciliation
            bank_accounts = self.get_accounts_needing_reconciliation()
            
            results = []
            for account in bank_accounts:
                try:
                    result = self.process_account_reconciliation(account)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing reconciliation for account {account.id}: {str(e)}")
                    results.append({
                        'account_id': account.id,
                        'account_name': account.account_name,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # Send notifications
            self.send_reconciliation_notifications(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in scheduled reconciliation: {str(e)}")
            return []
    
    def get_accounts_needing_reconciliation(self) -> List[BankAccount]:
        """Get bank accounts that need reconciliation"""
        try:
            # Get accounts with sync frequency settings
            accounts = BankAccount.query.filter(
                and_(
                    BankAccount.is_active == True,
                    BankAccount.provider.isnot(None),
                    BankAccount.sync_frequency.isnot(None)
                )
            ).all()
            
            accounts_needing_reconciliation = []
            
            for account in accounts:
                if self.should_reconcile_account(account):
                    accounts_needing_reconciliation.append(account)
            
            return accounts_needing_reconciliation
            
        except Exception as e:
            logger.error(f"Error getting accounts needing reconciliation: {str(e)}")
            return []
    
    def should_reconcile_account(self, account: BankAccount) -> bool:
        """Determine if an account needs reconciliation"""
        try:
            if not account.last_sync_at:
                return True
            
            # Check sync frequency
            sync_frequency = account.sync_frequency or 'daily'
            now = datetime.utcnow()
            
            if sync_frequency == 'daily':
                return (now - account.last_sync_at).days >= 1
            elif sync_frequency == 'weekly':
                return (now - account.last_sync_at).days >= 7
            elif sync_frequency == 'monthly':
                return (now - account.last_sync_at).days >= 30
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking reconciliation need for account {account.id}: {str(e)}")
            return False
    
    def process_account_reconciliation(self, account: BankAccount) -> Dict:
        """Process reconciliation for a specific account"""
        try:
            logger.info(f"Processing reconciliation for account {account.account_name}")
            
            # Create reconciliation session
            session = self.create_reconciliation_session(account)
            
            # Get unreconciled transactions
            unreconciled_transactions = self.get_unreconciled_transactions(account.id)
            unreconciled_gl_entries = self.get_unreconciled_gl_entries(account.id)
            
            # Auto-match transactions
            matches = self.auto_match_transactions(unreconciled_transactions, unreconciled_gl_entries)
            
            # Update session with results
            session.matched_transactions = len(matches)
            session.unmatched_transactions = len(unreconciled_transactions) - len(matches)
            session.status = 'completed' if len(matches) > 0 else 'pending'
            session.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'account_id': account.id,
                'account_name': account.account_name,
                'status': 'success',
                'matched_transactions': len(matches),
                'unmatched_transactions': len(unreconciled_transactions) - len(matches),
                'session_id': session.id
            }
            
        except Exception as e:
            logger.error(f"Error processing reconciliation for account {account.id}: {str(e)}")
            return {
                'account_id': account.id,
                'account_name': account.account_name,
                'status': 'error',
                'error': str(e)
            }
    
    def create_reconciliation_session(self, account: BankAccount) -> ReconciliationSession:
        """Create a new reconciliation session"""
        try:
            session = ReconciliationSession(
                bank_account_id=account.id,
                statement_date=datetime.utcnow().date(),
                statement_balance=account.current_balance or 0,
                book_balance=account.current_balance or 0,
                status='pending',
                created_by='system'
            )
            
            db.session.add(session)
            db.session.commit()
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating reconciliation session: {str(e)}")
            raise
    
    def get_unreconciled_transactions(self, bank_account_id: int) -> List[BankTransaction]:
        """Get unreconciled bank transactions"""
        try:
            return BankTransaction.query.filter(
                and_(
                    BankTransaction.bank_account_id == bank_account_id,
                    BankTransaction.matched == False
                )
            ).all()
        except Exception as e:
            logger.error(f"Error getting unreconciled transactions: {str(e)}")
            return []
    
    def get_unreconciled_gl_entries(self, bank_account_id: int) -> List[GeneralLedgerEntry]:
        """Get unreconciled GL entries for bank account"""
        try:
            return GeneralLedgerEntry.query.filter(
                and_(
                    GeneralLedgerEntry.bank_account_id == bank_account_id,
                    GeneralLedgerEntry.reconciled == False
                )
            ).all()
        except Exception as e:
            logger.error(f"Error getting unreconciled GL entries: {str(e)}")
            return []
    
    def auto_match_transactions(self, bank_transactions: List[BankTransaction], 
                              gl_entries: List[GeneralLedgerEntry]) -> List[Dict]:
        """Auto-match bank transactions with GL entries"""
        try:
            matches = []
            
            for bank_tx in bank_transactions:
                best_match = self.find_best_match(bank_tx, gl_entries)
                if best_match:
                    # Create match
                    self.create_transaction_match(bank_tx, best_match)
                    matches.append({
                        'bank_transaction_id': bank_tx.id,
                        'gl_entry_id': best_match.id,
                        'match_score': best_match.match_score
                    })
            
            return matches
            
        except Exception as e:
            logger.error(f"Error auto-matching transactions: {str(e)}")
            return []
    
    def find_best_match(self, bank_tx: BankTransaction, gl_entries: List[GeneralLedgerEntry]) -> Optional[GeneralLedgerEntry]:
        """Find the best matching GL entry for a bank transaction"""
        try:
            best_match = None
            best_score = 0
            
            for gl_entry in gl_entries:
                score = self.calculate_match_score(bank_tx, gl_entry)
                if score > best_score and score >= 80:  # Minimum 80% match
                    best_score = score
                    best_match = gl_entry
            
            if best_match:
                best_match.match_score = best_score
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error finding best match: {str(e)}")
            return None
    
    def calculate_match_score(self, bank_tx: BankTransaction, gl_entry: GeneralLedgerEntry) -> float:
        """Calculate match score between bank transaction and GL entry"""
        try:
            score = 0
            
            # Amount matching (40% weight)
            amount_diff = abs(bank_tx.amount - gl_entry.balance)
            if amount_diff == 0:
                score += 40
            elif amount_diff <= 0.01:
                score += 35
            elif amount_diff <= 0.10:
                score += 25
            
            # Date matching (30% weight)
            date_diff = abs((bank_tx.transaction_date - gl_entry.entry_date).days)
            if date_diff == 0:
                score += 30
            elif date_diff <= 1:
                score += 25
            elif date_diff <= 3:
                score += 15
            
            # Reference matching (20% weight)
            if bank_tx.reference and gl_entry.reference:
                if bank_tx.reference.lower() == gl_entry.reference.lower():
                    score += 20
                elif bank_tx.reference.lower() in gl_entry.reference.lower():
                    score += 10
            
            # Description similarity (10% weight)
            if bank_tx.description and gl_entry.description:
                similarity = self.calculate_text_similarity(bank_tx.description, gl_entry.description)
                score += similarity * 10
            
            return min(score, 100)
            
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return 0
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity between two strings"""
        try:
            if not text1 or not text2:
                return 0
            
            # Simple word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {str(e)}")
            return 0
    
    def create_transaction_match(self, bank_tx: BankTransaction, gl_entry: GeneralLedgerEntry):
        """Create a match between bank transaction and GL entry"""
        try:
            # Update bank transaction
            bank_tx.matched = True
            bank_tx.matched_transaction_id = gl_entry.id
            bank_tx.matched_transaction_type = 'GL'
            bank_tx.reconciled_at = datetime.utcnow()
            
            # Update GL entry
            gl_entry.reconciled = True
            gl_entry.reconciled_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error creating transaction match: {str(e)}")
            raise
    
    def send_reconciliation_notifications(self, results: List[Dict]):
        """Send reconciliation notifications"""
        try:
            if not self.notification_emails:
                return
            
            # Group results by status
            successful = [r for r in results if r.get('status') == 'success']
            failed = [r for r in results if r.get('status') == 'error']
            
            # Create notification message
            message = self.create_notification_message(successful, failed)
            
            # Send notifications (implement email service)
            self.send_email_notifications(message)
            
        except Exception as e:
            logger.error(f"Error sending reconciliation notifications: {str(e)}")
    
    def create_notification_message(self, successful: List[Dict], failed: List[Dict]) -> str:
        """Create notification message for reconciliation results"""
        try:
            message = "Automated Reconciliation Report\n\n"
            
            if successful:
                message += f"✅ Successful Reconciliations ({len(successful)}):\n"
                for result in successful:
                    message += f"  • {result['account_name']}: {result['matched_transactions']} matched, {result['unmatched_transactions']} unmatched\n"
                message += "\n"
            
            if failed:
                message += f"❌ Failed Reconciliations ({len(failed)}):\n"
                for result in failed:
                    message += f"  • {result['account_name']}: {result.get('error', 'Unknown error')}\n"
                message += "\n"
            
            message += f"Total processed: {len(successful) + len(failed)} accounts"
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating notification message: {str(e)}")
            return "Reconciliation completed with errors"
    
    def send_email_notifications(self, message: str):
        """Send email notifications (implement with your email service)"""
        try:
            # This would integrate with your email service
            # For now, just log the message
            logger.info(f"Reconciliation notification: {message}")
            
        except Exception as e:
            logger.error(f"Error sending email notifications: {str(e)}")

# Global instance
automated_reconciliation_service = AutomatedReconciliationService()


