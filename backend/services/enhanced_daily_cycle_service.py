# backend/services/enhanced_daily_cycle_service.py
from __future__ import annotations
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_
import json

from app import db
from modules.finance.daily_cycle_models import (
    DailyBalance, DailyCycleStatus, DailyTransactionSummary, 
    AdjustmentEntry, DailyCycleAuditLog
)
from modules.finance.advanced_models import ChartOfAccounts, GeneralLedgerEntry, JournalHeader
from app.audit_logger import AuditLogger, AuditAction

logger = logging.getLogger(__name__)

class EnhancedDailyCycleService:
    """
    Enhanced daily cycle service with locking, grace periods, and adjustment handling
    """
    
    def __init__(self, grace_period_hours: int = 2):
        self.grace_period_hours = grace_period_hours
    
    def capture_opening_balances(self, cycle_date: date, user_id: str, 
                                user_name: str = None, user_role: str = None,
                                ip_address: str = None, user_agent: str = None) -> Dict:
        """
        Capture opening balances with enhanced audit trail
        """
        try:
            # Check if opening balances already captured
            existing_status = DailyCycleStatus.get_status_for_date(cycle_date)
            if existing_status and existing_status.opening_status == 'completed':
                return {
                    "status": "already_captured",
                    "message": f"Opening balances already captured for {cycle_date}",
                    "cycle_date": cycle_date
                }
            
            # Create or update cycle status
            if not existing_status:
                cycle_status = DailyCycleStatus(
                    cycle_date=cycle_date,
                    opening_status='in_progress',
                    overall_status='opening'
                )
                db.session.add(cycle_status)
            else:
                cycle_status = existing_status
                cycle_status.opening_status = 'in_progress'
                cycle_status.overall_status = 'opening'
            
            # Get all active accounts
            active_accounts = ChartOfAccounts.query.filter_by(is_active=True).all()
            cycle_status.total_accounts = len(active_accounts)
            
            captured_count = 0
            total_opening_balance = 0.0
            
            for account in active_accounts:
                # Get the latest balance before this date
                latest_balance = DailyBalance.get_latest_balance(account.id, cycle_date)
                
                # Calculate opening balance
                if latest_balance:
                    opening_balance = latest_balance.closing_balance
                else:
                    # First time setup - get current balance from general ledger
                    opening_balance = self._calculate_account_balance(account.id, cycle_date)
                
                # Create daily balance record
                daily_balance = DailyBalance(
                    account_id=account.id,
                    balance_date=cycle_date,
                    opening_balance=opening_balance,
                    is_opening_captured=True,
                    cycle_status='opening_captured',
                    created_by=user_id,
                    allows_adjustments=True  # Allow adjustments initially
                )
                
                # Set debit/credit based on account type
                if account.account_type in ['asset', 'expense']:
                    daily_balance.opening_debit = opening_balance if opening_balance > 0 else 0
                    daily_balance.opening_credit = abs(opening_balance) if opening_balance < 0 else 0
                else:  # liability, equity, revenue
                    daily_balance.opening_credit = opening_balance if opening_balance > 0 else 0
                    daily_balance.opening_debit = abs(opening_balance) if opening_balance < 0 else 0
                
                db.session.add(daily_balance)
                captured_count += 1
                total_opening_balance += opening_balance
            
            # Update cycle status
            cycle_status.accounts_processed = captured_count
            cycle_status.total_opening_balance = total_opening_balance
            cycle_status.opening_status = 'completed'
            cycle_status.opening_captured_at = datetime.utcnow()
            cycle_status.opening_captured_by = user_id
            cycle_status.overall_status = 'opening'
            
            # Log audit trail
            DailyCycleAuditLog.log_action(
                cycle_date=cycle_date,
                action='opening_captured',
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                action_details=json.dumps({
                    'accounts_processed': captured_count,
                    'total_opening_balance': total_opening_balance
                }),
                affected_accounts=captured_count,
                total_amount=total_opening_balance,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.commit()
            
            return {
                "status": "success",
                "message": f"Opening balances captured for {captured_count} accounts",
                "cycle_date": cycle_date,
                "accounts_processed": captured_count,
                "total_opening_balance": total_opening_balance
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to capture opening balances for {cycle_date}: {str(e)}")
            raise
    
    def calculate_closing_balances(self, cycle_date: date, user_id: str,
                                 user_name: str = None, user_role: str = None,
                                 ip_address: str = None, user_agent: str = None,
                                 lock_after_closing: bool = True) -> Dict:
        """
        Calculate closing balances with optional locking
        """
        try:
            # Check if opening balances were captured
            cycle_status = DailyCycleStatus.get_status_for_date(cycle_date)
            if not cycle_status or cycle_status.opening_status != 'completed':
                return {
                    "status": "error",
                    "message": f"Opening balances must be captured before calculating closing balances for {cycle_date}"
                }
            
            # Check if closing already calculated
            if cycle_status.closing_status == 'completed':
                return {
                    "status": "already_calculated",
                    "message": f"Closing balances already calculated for {cycle_date}",
                    "cycle_date": cycle_date
                }
            
            # Update status
            cycle_status.closing_status = 'in_progress'
            cycle_status.overall_status = 'closing'
            
            # Get all daily balances for this date
            daily_balances = DailyBalance.get_daily_balances_for_date(cycle_date)
            
            processed_count = 0
            total_closing_balance = 0.0
            total_daily_movement = 0.0
            
            for daily_balance in daily_balances:
                # Calculate daily movements from general ledger
                daily_movements = self._calculate_daily_movements(
                    daily_balance.account_id, cycle_date
                )
                
                # Update daily balance with movements
                daily_balance.daily_debit = daily_movements['debit']
                daily_balance.daily_credit = daily_movements['credit']
                daily_balance.daily_net_movement = daily_movements['net_movement']
                
                # Calculate closing balance
                account = daily_balance.account
                if account.account_type in ['asset', 'expense']:
                    # Assets and expenses: opening + debit - credit
                    daily_balance.closing_balance = (
                        daily_balance.opening_balance + 
                        daily_balance.daily_debit - 
                        daily_balance.daily_credit
                    )
                else:  # liability, equity, revenue
                    # Liabilities, equity, revenue: opening + credit - debit
                    daily_balance.closing_balance = (
                        daily_balance.opening_balance + 
                        daily_balance.daily_credit - 
                        daily_balance.daily_debit
                    )
                
                # Set closing debit/credit
                if account.account_type in ['asset', 'expense']:
                    daily_balance.closing_debit = daily_balance.closing_balance if daily_balance.closing_balance > 0 else 0
                    daily_balance.closing_credit = abs(daily_balance.closing_balance) if daily_balance.closing_balance < 0 else 0
                else:
                    daily_balance.closing_credit = daily_balance.closing_balance if daily_balance.closing_balance > 0 else 0
                    daily_balance.closing_debit = abs(daily_balance.closing_balance) if daily_balance.closing_balance < 0 else 0
                
                daily_balance.is_closing_calculated = True
                daily_balance.cycle_status = 'closing_calculated'
                
                # Set grace period for adjustments
                if not daily_balance.is_locked:
                    daily_balance.grace_period_ends = datetime.utcnow() + timedelta(hours=self.grace_period_hours)
                
                processed_count += 1
                total_closing_balance += daily_balance.closing_balance
                total_daily_movement += daily_balance.daily_net_movement
            
            # Lock the day if requested
            if lock_after_closing:
                self._lock_daily_balances(cycle_date, user_id, 'day_closed', user_name, user_role, ip_address, user_agent)
            
            # Generate daily transaction summary
            self._generate_daily_transaction_summary(cycle_date)
            
            # Update cycle status
            cycle_status.accounts_processed = processed_count
            cycle_status.total_closing_balance = total_closing_balance
            cycle_status.total_daily_movement = total_daily_movement
            cycle_status.closing_status = 'completed'
            cycle_status.closing_calculated_at = datetime.utcnow()
            cycle_status.closing_calculated_by = user_id
            cycle_status.overall_status = 'completed' if lock_after_closing else 'closing'
            
            # Log audit trail
            DailyCycleAuditLog.log_action(
                cycle_date=cycle_date,
                action='closing_calculated',
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                action_details=json.dumps({
                    'accounts_processed': processed_count,
                    'total_closing_balance': total_closing_balance,
                    'total_daily_movement': total_daily_movement,
                    'locked_after_closing': lock_after_closing
                }),
                affected_accounts=processed_count,
                total_amount=total_closing_balance,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.commit()
            
            return {
                "status": "success",
                "message": f"Closing balances calculated for {processed_count} accounts",
                "cycle_date": cycle_date,
                "accounts_processed": processed_count,
                "total_closing_balance": total_closing_balance,
                "total_daily_movement": total_daily_movement,
                "locked": lock_after_closing
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to calculate closing balances for {cycle_date}: {str(e)}")
            raise
    
    def lock_daily_balances(self, cycle_date: date, user_id: str, 
                           reason: str = 'manual_lock', user_name: str = None,
                           user_role: str = None, ip_address: str = None,
                           user_agent: str = None) -> Dict:
        """
        Lock daily balances to prevent further transactions
        """
        return self._lock_daily_balances(cycle_date, user_id, reason, user_name, user_role, ip_address, user_agent)
    
    def unlock_daily_balances(self, cycle_date: date, user_id: str,
                             user_name: str = None, user_role: str = None,
                             ip_address: str = None, user_agent: str = None) -> Dict:
        """
        Unlock daily balances to allow transactions (admin only)
        """
        try:
            daily_balances = DailyBalance.get_daily_balances_for_date(cycle_date)
            
            if not daily_balances:
                return {
                    "status": "error",
                    "message": f"No daily balances found for {cycle_date}"
                }
            
            unlocked_count = 0
            for daily_balance in daily_balances:
                if daily_balance.is_locked:
                    daily_balance.is_locked = False
                    daily_balance.locked_at = None
                    daily_balance.locked_by = None
                    daily_balance.lock_reason = None
                    daily_balance.allows_adjustments = True
                    unlocked_count += 1
            
            # Log audit trail
            DailyCycleAuditLog.log_action(
                cycle_date=cycle_date,
                action='unlocked',
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                action_details=json.dumps({
                    'unlocked_accounts': unlocked_count,
                    'reason': 'manual_unlock'
                }),
                affected_accounts=unlocked_count,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.commit()
            
            return {
                "status": "success",
                "message": f"Unlocked {unlocked_count} accounts for {cycle_date}",
                "cycle_date": cycle_date,
                "unlocked_count": unlocked_count
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to unlock daily balances for {cycle_date}: {str(e)}")
            raise
    
    def create_adjustment_entry(self, original_date: date, account_id: int,
                               adjustment_type: str, reason: str, 
                               adjustment_amount: float, user_id: str,
                               user_name: str = None, user_role: str = None,
                               reference_document: str = None,
                               ip_address: str = None, user_agent: str = None) -> Dict:
        """
        Create an adjustment entry for a closed day
        """
        try:
            # Check if the day is locked
            daily_balance = DailyBalance.get_balance_for_date(account_id, original_date)
            if not daily_balance:
                return {
                    "status": "error",
                    "message": f"No daily balance found for account {account_id} on {original_date}"
                }
            
            # Check if adjustments are allowed
            if daily_balance.is_locked and not daily_balance.allows_adjustments:
                return {
                    "status": "error",
                    "message": f"Adjustments not allowed for {original_date} - day is locked"
                }
            
            # Check grace period
            if daily_balance.grace_period_ends and datetime.utcnow() > daily_balance.grace_period_ends:
                return {
                    "status": "error",
                    "message": f"Grace period expired for {original_date} - adjustments no longer allowed"
                }
            
            # Get account
            account = ChartOfAccounts.query.get(account_id)
            if not account:
                return {
                    "status": "error",
                    "message": f"Account {account_id} not found"
                }
            
            # Calculate adjustment values
            if account.account_type in ['asset', 'expense']:
                if adjustment_amount > 0:
                    adjustment_debit = adjustment_amount
                    adjustment_credit = 0
                else:
                    adjustment_debit = 0
                    adjustment_credit = abs(adjustment_amount)
            else:  # liability, equity, revenue
                if adjustment_amount > 0:
                    adjustment_debit = 0
                    adjustment_credit = adjustment_amount
                else:
                    adjustment_debit = abs(adjustment_amount)
                    adjustment_credit = 0
            
            # Create adjustment entry
            adjustment = AdjustmentEntry(
                original_date=original_date,
                adjustment_date=date.today(),
                account_id=account_id,
                original_debit=daily_balance.closing_debit,
                original_credit=daily_balance.closing_credit,
                original_balance=daily_balance.closing_balance,
                adjustment_debit=adjustment_debit,
                adjustment_credit=adjustment_credit,
                adjustment_balance=adjustment_amount,
                new_debit=daily_balance.closing_debit + adjustment_debit,
                new_credit=daily_balance.closing_credit + adjustment_credit,
                new_balance=daily_balance.closing_balance + adjustment_amount,
                adjustment_type=adjustment_type,
                reason=reason,
                reference_document=reference_document,
                authorized_by=user_id,
                created_by=user_id,
                status='pending'
            )
            
            db.session.add(adjustment)
            
            # Log audit trail
            DailyCycleAuditLog.log_action(
                cycle_date=original_date,
                action='adjustment_made',
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                action_details=json.dumps({
                    'adjustment_id': adjustment.id,
                    'account_id': account_id,
                    'adjustment_type': adjustment_type,
                    'adjustment_amount': adjustment_amount,
                    'reason': reason
                }),
                affected_accounts=1,
                total_amount=adjustment_amount,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.commit()
            
            return {
                "status": "success",
                "message": f"Adjustment entry created for {account.account_name}",
                "adjustment_id": adjustment.id,
                "original_date": original_date,
                "adjustment_amount": adjustment_amount
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create adjustment entry: {str(e)}")
            raise
    
    def apply_adjustment(self, adjustment_id: int, user_id: str,
                        user_name: str = None, user_role: str = None,
                        ip_address: str = None, user_agent: str = None) -> Dict:
        """
        Apply a pending adjustment entry
        """
        try:
            adjustment = AdjustmentEntry.query.get(adjustment_id)
            if not adjustment:
                return {
                    "status": "error",
                    "message": f"Adjustment entry {adjustment_id} not found"
                }
            
            if adjustment.status != 'pending':
                return {
                    "status": "error",
                    "message": f"Adjustment entry {adjustment_id} is not pending"
                }
            
            # Get the daily balance
            daily_balance = DailyBalance.get_balance_for_date(
                adjustment.account_id, adjustment.original_date
            )
            
            if not daily_balance:
                return {
                    "status": "error",
                    "message": f"Daily balance not found for adjustment"
                }
            
            # Apply the adjustment
            daily_balance.closing_balance = adjustment.new_balance
            daily_balance.closing_debit = adjustment.new_debit
            daily_balance.closing_credit = adjustment.new_credit
            
            # Update adjustment status
            adjustment.status = 'applied'
            adjustment.applied_at = datetime.utcnow()
            adjustment.approved_by = user_id
            
            # Log audit trail
            DailyCycleAuditLog.log_action(
                cycle_date=adjustment.original_date,
                action='adjustment_applied',
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                action_details=json.dumps({
                    'adjustment_id': adjustment_id,
                    'account_id': adjustment.account_id,
                    'adjustment_amount': adjustment.adjustment_balance
                }),
                affected_accounts=1,
                total_amount=adjustment.adjustment_balance,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.commit()
            
            return {
                "status": "success",
                "message": f"Adjustment {adjustment_id} applied successfully",
                "adjustment_id": adjustment_id
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to apply adjustment {adjustment_id}: {str(e)}")
            raise
    
    def get_audit_trail(self, cycle_date: date) -> Dict:
        """
        Get complete audit trail for a specific date
        """
        try:
            audit_logs = DailyCycleAuditLog.get_audit_trail_for_date(cycle_date)
            
            audit_data = []
            for log in audit_logs:
                audit_data.append({
                    'id': log.id,
                    'action': log.action,
                    'user_id': log.user_id,
                    'user_name': log.user_name,
                    'user_role': log.user_role,
                    'action_details': json.loads(log.action_details) if log.action_details else None,
                    'affected_accounts': log.affected_accounts,
                    'total_amount': log.total_amount,
                    'timestamp': log.action_timestamp.isoformat(),
                    'ip_address': log.ip_address
                })
            
            return {
                "status": "success",
                "cycle_date": cycle_date,
                "audit_trail": audit_data,
                "total_actions": len(audit_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit trail for {cycle_date}: {str(e)}")
            raise
    
    def _lock_daily_balances(self, cycle_date: date, user_id: str, reason: str,
                            user_name: str = None, user_role: str = None,
                            ip_address: str = None, user_agent: str = None) -> Dict:
        """
        Internal method to lock daily balances
        """
        try:
            daily_balances = DailyBalance.get_daily_balances_for_date(cycle_date)
            
            if not daily_balances:
                return {
                    "status": "error",
                    "message": f"No daily balances found for {cycle_date}"
                }
            
            locked_count = 0
            for daily_balance in daily_balances:
                if not daily_balance.is_locked:
                    daily_balance.is_locked = True
                    daily_balance.locked_at = datetime.utcnow()
                    daily_balance.locked_by = user_id
                    daily_balance.lock_reason = reason
                    daily_balance.allows_adjustments = False  # Disable adjustments when locked
                    locked_count += 1
            
            # Log audit trail
            DailyCycleAuditLog.log_action(
                cycle_date=cycle_date,
                action='locked',
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                action_details=json.dumps({
                    'locked_accounts': locked_count,
                    'reason': reason
                }),
                affected_accounts=locked_count,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                "status": "success",
                "message": f"Locked {locked_count} accounts for {cycle_date}",
                "cycle_date": cycle_date,
                "locked_count": locked_count,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Failed to lock daily balances for {cycle_date}: {str(e)}")
            raise
    
    def _calculate_account_balance(self, account_id: int, as_of_date: date) -> float:
        """Calculate account balance from general ledger as of specific date"""
        result = db.session.query(
            func.sum(
                func.coalesce(GeneralLedgerEntry.debit_amount, 0) - 
                func.coalesce(GeneralLedgerEntry.credit_amount, 0)
            )
        ).filter(
            GeneralLedgerEntry.account_id == account_id,
            GeneralLedgerEntry.entry_date <= as_of_date,
            GeneralLedgerEntry.status == 'posted'
        ).scalar()
        
        return float(result or 0)
    
    def _calculate_daily_movements(self, account_id: int, movement_date: date) -> Dict:
        """Calculate daily debit/credit movements for an account"""
        result = db.session.query(
            func.sum(func.coalesce(GeneralLedgerEntry.debit_amount, 0)).label('total_debit'),
            func.sum(func.coalesce(GeneralLedgerEntry.credit_amount, 0)).label('total_credit')
        ).filter(
            GeneralLedgerEntry.account_id == account_id,
            GeneralLedgerEntry.entry_date == movement_date,
            GeneralLedgerEntry.status == 'posted'
        ).first()
        
        total_debit = float(result.total_debit or 0)
        total_credit = float(result.total_credit or 0)
        net_movement = total_debit - total_credit
        
        return {
            'debit': total_debit,
            'credit': total_credit,
            'net_movement': net_movement
        }
    
    def _generate_daily_transaction_summary(self, cycle_date: date) -> None:
        """Generate daily transaction summary for reporting"""
        # Get transaction counts and amounts
        summary_data = db.session.query(
            func.count(GeneralLedgerEntry.id).label('total_transactions'),
            func.sum(func.coalesce(GeneralLedgerEntry.debit_amount, 0)).label('total_debits'),
            func.sum(func.coalesce(GeneralLedgerEntry.credit_amount, 0)).label('total_credits')
        ).filter(
            GeneralLedgerEntry.entry_date == cycle_date,
            GeneralLedgerEntry.status == 'posted'
        ).first()
        
        # Get account type movements
        account_movements = db.session.query(
            ChartOfAccounts.account_type,
            func.sum(func.coalesce(GeneralLedgerEntry.debit_amount, 0) - 
                    func.coalesce(GeneralLedgerEntry.credit_amount, 0)).label('net_movement')
        ).join(GeneralLedgerEntry).filter(
            GeneralLedgerEntry.entry_date == cycle_date,
            GeneralLedgerEntry.status == 'posted'
        ).group_by(ChartOfAccounts.account_type).all()
        
        # Create or update summary
        summary = DailyTransactionSummary.get_summary_for_date(cycle_date)
        if not summary:
            summary = DailyTransactionSummary(summary_date=cycle_date)
            db.session.add(summary)
        
        # Update summary data
        summary.total_transactions = summary_data.total_transactions or 0
        summary.total_debits = float(summary_data.total_debits or 0)
        summary.total_credits = float(summary_data.total_credits or 0)
        summary.net_movement = summary.total_debits - summary.total_credits
        
        # Update account type movements
        for movement in account_movements:
            movement_amount = float(movement.net_movement or 0)
            if movement.account_type == 'asset':
                summary.asset_movement = movement_amount
            elif movement.account_type == 'liability':
                summary.liability_movement = movement_amount
            elif movement.account_type == 'equity':
                summary.equity_movement = movement_amount
            elif movement.account_type == 'revenue':
                summary.revenue_movement = movement_amount
            elif movement.account_type == 'expense':
                summary.expense_movement = movement_amount
