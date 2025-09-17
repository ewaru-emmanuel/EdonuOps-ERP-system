# backend/services/enhanced_daily_balance_service.py
from __future__ import annotations
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_

from app import db
from modules.finance.daily_cycle_models import DailyBalance, DailyCycleStatus, DailyTransactionSummary
from modules.finance.advanced_models import ChartOfAccounts, GeneralLedgerEntry, JournalHeader
from app.audit_logger import AuditLogger, AuditAction

logger = logging.getLogger(__name__)

class EnhancedDailyBalanceService:
    """
    Enhanced Daily Balance Flow Service implementing the complete daily cycle workflow:
    
    🕰️ Morning: Opening Balances Are Ready
    🛠️ During the Day: Transactions Are Recorded  
    🌙 Evening: Closing the Day
    📊 Reporting: Snapshot of the Day
    """
    
    @staticmethod
    def execute_morning_opening_cycle(target_date: date = None, user_id: str = 'system') -> Dict:
        """
        🕰️ Morning: Opening Balances Are Ready
        
        When the business day starts, the system automatically carries forward 
        the closing balances from the previous day into the new day as opening balances.
        """
        if not target_date:
            target_date = date.today()
            
        try:
            logger.info(f"Starting morning opening cycle for {target_date}")
            
            # Check if opening cycle already completed for this date
            existing_status = DailyCycleStatus.get_status_for_date(target_date)
            if existing_status and existing_status.opening_status == 'completed':
                return {
                    "status": "already_completed",
                    "message": f"Opening balances already captured for {target_date}",
                    "cycle_date": target_date,
                    "opening_balances": EnhancedDailyBalanceService._get_opening_balances_summary(target_date)
                }
            
            # Get all active accounts
            active_accounts = ChartOfAccounts.query.filter_by(is_active=True).all()
            
            # Create or update cycle status
            if not existing_status:
                cycle_status = DailyCycleStatus(
                    cycle_date=target_date,
                    opening_status='in_progress',
                    overall_status='opening'
                )
                db.session.add(cycle_status)
            else:
                cycle_status = existing_status
                cycle_status.opening_status = 'in_progress'
                cycle_status.overall_status = 'opening'
            
            cycle_status.total_accounts = len(active_accounts)
            captured_count = 0
            total_opening_balance = 0.0
            opening_balances_summary = []
            
            for account in active_accounts:
                # Get closing balance from previous day
                previous_day = target_date - timedelta(days=1)
                previous_balance = DailyBalance.get_latest_balance(account.id, previous_day)
                
                # Calculate opening balance (carry forward from previous day's closing)
                if previous_balance:
                    opening_balance = previous_balance.closing_balance
                else:
                    # First time setup - get current balance from general ledger
                    opening_balance = EnhancedDailyBalanceService._calculate_account_balance_from_gl(account.id, target_date)
                
                # Create daily balance record
                daily_balance = DailyBalance(
                    account_id=account.id,
                    balance_date=target_date,
                    opening_balance=opening_balance,
                    is_opening_captured=True,
                    cycle_status='opening_captured',
                    created_by=user_id
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
                
                # Add to summary
                opening_balances_summary.append({
                    "account_id": account.id,
                    "account_name": account.account_name,
                    "account_type": account.account_type,
                    "opening_balance": opening_balance
                })
            
            # Update cycle status
            cycle_status.accounts_processed = captured_count
            cycle_status.total_opening_balance = total_opening_balance
            cycle_status.opening_status = 'completed'
            cycle_status.opening_captured_at = datetime.utcnow()
            cycle_status.opening_captured_by = user_id
            cycle_status.overall_status = 'opening'
            
            db.session.commit()
            
            # Log audit trail
            AuditLogger.log(
                user_id=user_id,
                action=AuditAction.CREATE,
                entity_type="daily_cycle",
                entity_id=f"opening_{target_date}",
                new_values={"message": f"Opening balances captured for {captured_count} accounts"}
            )
            
            logger.info(f"Morning opening cycle completed for {target_date}: {captured_count} accounts processed")
            
            return {
                "status": "success",
                "message": f"Opening balances captured for {target_date}",
                "cycle_date": target_date,
                "accounts_processed": captured_count,
                "total_opening_balance": total_opening_balance,
                "opening_balances": opening_balances_summary
            }
            
        except Exception as e:
            logger.error(f"Failed to execute morning opening cycle for {target_date}: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def execute_evening_closing_cycle(target_date: date = None, user_id: str = 'system') -> Dict:
        """
        🌙 Evening: Closing the Day
        
        At the end of the business day, calculate closing balances using:
        Opening Balance + Debits – Credits = Closing Balance
        """
        if not target_date:
            target_date = date.today()
            
        try:
            logger.info(f"Starting evening closing cycle for {target_date}")
            
            # Check if opening cycle was completed
            cycle_status = DailyCycleStatus.get_status_for_date(target_date)
            if not cycle_status or cycle_status.opening_status != 'completed':
                return {
                    "status": "error",
                    "message": f"Opening cycle must be completed before closing cycle for {target_date}"
                }
            
            # Get all daily balances for this date
            daily_balances = DailyBalance.query.filter_by(balance_date=target_date).all()
            
            if not daily_balances:
                return {
                    "status": "error",
                    "message": f"No opening balances found for {target_date}"
                }
            
            cycle_status.closing_status = 'in_progress'
            cycle_status.overall_status = 'closing'
            
            processed_count = 0
            total_closing_balance = 0.0
            closing_balances_summary = []
            
            for daily_balance in daily_balances:
                account = ChartOfAccounts.query.get(daily_balance.account_id)
                if not account:
                    continue
                
                # Get all transactions for this account on this date
                transactions = GeneralLedgerEntry.query.filter(
                    and_(
                        GeneralLedgerEntry.account_id == account.id,
                        func.date(GeneralLedgerEntry.entry_date) == target_date
                    )
                ).all()
                
                # Calculate total debits and credits for the day
                total_debits = sum(float(t.debit_amount or 0) for t in transactions)
                total_credits = sum(float(t.credit_amount or 0) for t in transactions)
                
                # Calculate closing balance: Opening Balance + Debits – Credits
                opening_balance = daily_balance.opening_balance
                closing_balance = opening_balance + total_debits - total_credits
                
                # Update daily balance record
                daily_balance.closing_balance = closing_balance
                daily_balance.total_debits = total_debits
                daily_balance.total_credits = total_credits
                daily_balance.transaction_count = len(transactions)
                daily_balance.is_closing_calculated = True
                daily_balance.closing_calculated_at = datetime.utcnow()
                daily_balance.closing_calculated_by = user_id
                daily_balance.cycle_status = 'closing_calculated'
                
                # Set closing debit/credit based on account type
                if account.account_type in ['asset', 'expense']:
                    daily_balance.closing_debit = closing_balance if closing_balance > 0 else 0
                    daily_balance.closing_credit = abs(closing_balance) if closing_balance < 0 else 0
                else:  # liability, equity, revenue
                    daily_balance.closing_credit = closing_balance if closing_balance > 0 else 0
                    daily_balance.closing_debit = abs(closing_balance) if closing_balance < 0 else 0
                
                processed_count += 1
                total_closing_balance += closing_balance
                
                # Add to summary
                closing_balances_summary.append({
                    "account_id": account.id,
                    "account_name": account.account_name,
                    "account_type": account.account_type,
                    "opening_balance": opening_balance,
                    "total_debits": total_debits,
                    "total_credits": total_credits,
                    "closing_balance": closing_balance,
                    "transaction_count": len(transactions)
                })
            
            # Update cycle status
            cycle_status.accounts_processed = processed_count
            cycle_status.total_closing_balance = total_closing_balance
            cycle_status.closing_status = 'completed'
            cycle_status.closing_calculated_at = datetime.utcnow()
            cycle_status.closing_calculated_by = user_id
            cycle_status.overall_status = 'completed'
            
            db.session.commit()
            
            # Log audit trail
            AuditLogger.log(
                user_id=user_id,
                action=AuditAction.UPDATE,
                entity_type="daily_cycle",
                entity_id=f"closing_{target_date}",
                new_values={"message": f"Closing balances calculated for {processed_count} accounts"}
            )
            
            logger.info(f"Evening closing cycle completed for {target_date}: {processed_count} accounts processed")
            
            return {
                "status": "success",
                "message": f"Closing balances calculated for {target_date}",
                "cycle_date": target_date,
                "accounts_processed": processed_count,
                "total_closing_balance": total_closing_balance,
                "closing_balances": closing_balances_summary
            }
            
        except Exception as e:
            logger.error(f"Failed to execute evening closing cycle for {target_date}: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def execute_full_daily_cycle(target_date: date = None, user_id: str = 'system') -> Dict:
        """
        Execute complete daily cycle: Morning Opening + Evening Closing
        """
        if not target_date:
            target_date = date.today()
            
        try:
            logger.info(f"Starting full daily cycle for {target_date}")
            
            # Step 1: Morning Opening Cycle
            opening_result = EnhancedDailyBalanceService.execute_morning_opening_cycle(target_date, user_id)
            if opening_result["status"] == "error":
                return opening_result
            
            # Step 2: Evening Closing Cycle
            closing_result = EnhancedDailyBalanceService.execute_evening_closing_cycle(target_date, user_id)
            if closing_result["status"] == "error":
                return closing_result
            
            return {
                "status": "success",
                "message": f"Complete daily cycle executed for {target_date}",
                "cycle_date": target_date,
                "opening_result": opening_result,
                "closing_result": closing_result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute full daily cycle for {target_date}: {str(e)}")
            raise
    
    @staticmethod
    def get_daily_balance_flow_summary(target_date: date = None) -> Dict:
        """
        📊 Reporting: Snapshot of the Day
        
        Get comprehensive daily balance flow summary
        """
        if not target_date:
            target_date = date.today()
            
        try:
            # Get cycle status
            cycle_status = DailyCycleStatus.get_status_for_date(target_date)
            
            # Get daily balances
            daily_balances = DailyBalance.query.filter_by(balance_date=target_date).all()
            
            # Calculate summary statistics
            total_opening = sum(db.opening_balance for db in daily_balances)
            total_closing = sum(db.closing_balance for db in daily_balances)
            total_debits = sum(db.total_debits or 0 for db in daily_balances)
            total_credits = sum(db.total_credits or 0 for db in daily_balances)
            total_transactions = sum(db.transaction_count or 0 for db in daily_balances)
            
            # Group by account type
            account_type_summary = {}
            for balance in daily_balances:
                account = ChartOfAccounts.query.get(balance.account_id)
                if account:
                    account_type = account.account_type
                    if account_type not in account_type_summary:
                        account_type_summary[account_type] = {
                            "opening_balance": 0,
                            "closing_balance": 0,
                            "total_debits": 0,
                            "total_credits": 0,
                            "account_count": 0
                        }
                    
                    account_type_summary[account_type]["opening_balance"] += balance.opening_balance
                    account_type_summary[account_type]["closing_balance"] += balance.closing_balance
                    account_type_summary[account_type]["total_debits"] += balance.total_debits or 0
                    account_type_summary[account_type]["total_credits"] += balance.total_credits or 0
                    account_type_summary[account_type]["account_count"] += 1
            
            return {
                "cycle_date": target_date,
                "cycle_status": cycle_status.overall_status if cycle_status else "not_started",
                "summary": {
                    "total_accounts": len(daily_balances),
                    "total_opening_balance": total_opening,
                    "total_closing_balance": total_closing,
                    "total_debits": total_debits,
                    "total_credits": total_credits,
                    "total_transactions": total_transactions,
                    "net_change": total_closing - total_opening
                },
                "account_type_summary": account_type_summary,
                "daily_balances": [
                    {
                        "account_id": balance.account_id,
                        "account_name": ChartOfAccounts.query.get(balance.account_id).account_name if ChartOfAccounts.query.get(balance.account_id) else "Unknown",
                        "opening_balance": balance.opening_balance,
                        "closing_balance": balance.closing_balance,
                        "total_debits": balance.total_debits or 0,
                        "total_credits": balance.total_credits or 0,
                        "transaction_count": balance.transaction_count or 0
                    }
                    for balance in daily_balances
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get daily balance flow summary for {target_date}: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_account_balance_from_gl(account_id: int, as_of_date: date) -> float:
        """
        Calculate account balance from general ledger as of specific date
        """
        result = db.session.query(
            func.sum(
                func.coalesce(GeneralLedgerEntry.debit_amount, 0) - 
                func.coalesce(GeneralLedgerEntry.credit_amount, 0)
            )
        ).filter(
            and_(
                GeneralLedgerEntry.account_id == account_id,
                func.date(GeneralLedgerEntry.entry_date) <= as_of_date
            )
        ).scalar()
        
        return float(result or 0)
    
    @staticmethod
    def _get_opening_balances_summary(target_date: date) -> List[Dict]:
        """
        Get summary of opening balances for a specific date
        """
        daily_balances = DailyBalance.query.filter_by(balance_date=target_date).all()
        
        return [
            {
                "account_id": balance.account_id,
                "account_name": ChartOfAccounts.query.get(balance.account_id).account_name if ChartOfAccounts.query.get(balance.account_id) else "Unknown",
                "opening_balance": balance.opening_balance
            }
            for balance in daily_balances
        ]
