# backend/services/daily_cycle_service.py
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

class DailyCycleService:
    """
    Handles daily opening/closing cycle operations for financial accounts
    """
    
    @staticmethod
    def capture_opening_balances(cycle_date: date, user_id: str) -> Dict:
        """
        Capture opening balances for all active accounts for a specific date
        """
        try:
            # Check if opening balances already captured for this date
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
                    opening_balance = DailyCycleService._calculate_account_balance(account.id, cycle_date)
                
                # Create daily balance record
                daily_balance = DailyBalance(
                    account_id=account.id,
                    balance_date=cycle_date,
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
                entity_id=str(cycle_date),
                new_values={
                    "opening_balances_captured": captured_count,
                    "total_opening_balance": total_opening_balance
                }
            )
            
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
            
            # Update cycle status to failed
            if existing_status:
                existing_status.opening_status = 'failed'
                existing_status.overall_status = 'failed'
                existing_status.error_message = str(e)
                db.session.commit()
            
            raise
    
    @staticmethod
    def calculate_closing_balances(cycle_date: date, user_id: str) -> Dict:
        """
        Calculate closing balances for all accounts for a specific date
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
                daily_movements = DailyCycleService._calculate_daily_movements(
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
                
                processed_count += 1
                total_closing_balance += daily_balance.closing_balance
                total_daily_movement += daily_balance.daily_net_movement
            
            # Generate daily transaction summary
            DailyCycleService._generate_daily_transaction_summary(cycle_date)
            
            # Update cycle status
            cycle_status.accounts_processed = processed_count
            cycle_status.total_closing_balance = total_closing_balance
            cycle_status.total_daily_movement = total_daily_movement
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
                entity_id=str(cycle_date),
                new_values={
                    "closing_balances_calculated": processed_count,
                    "total_closing_balance": total_closing_balance,
                    "total_daily_movement": total_daily_movement
                }
            )
            
            return {
                "status": "success",
                "message": f"Closing balances calculated for {processed_count} accounts",
                "cycle_date": cycle_date,
                "accounts_processed": processed_count,
                "total_closing_balance": total_closing_balance,
                "total_daily_movement": total_daily_movement
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to calculate closing balances for {cycle_date}: {str(e)}")
            
            # Update cycle status to failed
            if cycle_status:
                cycle_status.closing_status = 'failed'
                cycle_status.overall_status = 'failed'
                cycle_status.error_message = str(e)
                db.session.commit()
            
            raise
    
    @staticmethod
    def execute_full_daily_cycle(cycle_date: date, user_id: str) -> Dict:
        """
        Execute complete daily cycle: opening capture + closing calculation
        """
        try:
            # Step 1: Capture opening balances
            opening_result = DailyCycleService.capture_opening_balances(cycle_date, user_id)
            if opening_result["status"] == "error":
                return opening_result
            
            # Step 2: Calculate closing balances
            closing_result = DailyCycleService.calculate_closing_balances(cycle_date, user_id)
            if closing_result["status"] == "error":
                return closing_result
            
            return {
                "status": "success",
                "message": f"Complete daily cycle executed for {cycle_date}",
                "cycle_date": cycle_date,
                "opening_result": opening_result,
                "closing_result": closing_result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute daily cycle for {cycle_date}: {str(e)}")
            raise
    
    @staticmethod
    def get_daily_cycle_status(cycle_date: date) -> Dict:
        """
        Get the status of daily cycle for a specific date
        """
        cycle_status = DailyCycleStatus.get_status_for_date(cycle_date)
        if not cycle_status:
            return {
                "cycle_date": cycle_date,
                "status": "not_started",
                "message": "Daily cycle not started for this date"
            }
        
        return {
            "cycle_date": cycle_date,
            "overall_status": cycle_status.overall_status,
            "opening_status": cycle_status.opening_status,
            "closing_status": cycle_status.closing_status,
            "total_accounts": cycle_status.total_accounts,
            "accounts_processed": cycle_status.accounts_processed,
            "total_opening_balance": cycle_status.total_opening_balance,
            "total_closing_balance": cycle_status.total_closing_balance,
            "total_daily_movement": cycle_status.total_daily_movement,
            "opening_captured_at": cycle_status.opening_captured_at.isoformat() if cycle_status.opening_captured_at else None,
            "closing_calculated_at": cycle_status.closing_calculated_at.isoformat() if cycle_status.closing_calculated_at else None,
            "error_message": cycle_status.error_message
        }
    
    @staticmethod
    def get_account_daily_balance(account_id: int, balance_date: date) -> Dict:
        """
        Get daily balance details for a specific account and date
        """
        daily_balance = DailyBalance.get_balance_for_date(account_id, balance_date)
        if not daily_balance:
            return {
                "status": "not_found",
                "message": f"No daily balance found for account {account_id} on {balance_date}"
            }
        
        return {
            "status": "success",
            "account_id": account_id,
            "account_name": daily_balance.account.account_name,
            "balance_date": balance_date,
            "opening_balance": daily_balance.opening_balance,
            "daily_debit": daily_balance.daily_debit,
            "daily_credit": daily_balance.daily_credit,
            "daily_net_movement": daily_balance.daily_net_movement,
            "closing_balance": daily_balance.closing_balance,
            "cycle_status": daily_balance.cycle_status,
            "is_opening_captured": daily_balance.is_opening_captured,
            "is_closing_calculated": daily_balance.is_closing_calculated
        }
    
    @staticmethod
    def _calculate_account_balance(account_id: int, as_of_date: date) -> float:
        """
        Calculate account balance from general ledger as of specific date
        """
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
    
    @staticmethod
    def _calculate_daily_movements(account_id: int, movement_date: date) -> Dict:
        """
        Calculate daily debit/credit movements for an account
        """
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
    
    @staticmethod
    def _generate_daily_transaction_summary(cycle_date: date) -> None:
        """
        Generate daily transaction summary for reporting
        """
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
