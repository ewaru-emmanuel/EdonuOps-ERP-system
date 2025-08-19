# backend/services/finance/closing_service.py
from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from app import db
from sqlalchemy import func, case
from modules.finance.models import (
    ChartOfAccount,
    JournalHeader,
    JournalLine,
    Budget
)
from app.audit_logger import AuditLogger, AuditAction

logger = logging.getLogger(__name__)

class ClosingService:
    
    @staticmethod
    def execute_month_end_close(period: str, user_id: str) -> Dict:
        """
        Execute full month-end closing process:
        1. Validate all entries are posted
        2. Generate accruals/reversals
        3. Close revenue/expense accounts
        4. Update retained earnings
        """
        try:
            # Step 1: Validate all entries are posted
            unposted = JournalHeader.query.filter_by(period=period, status="draft").count()
            if unposted > 0:
                raise ValueError(f"{unposted} unposted entries exist for {period}")

            # Step 2: Generate automatic accruals
            accruals = ClosingService._generate_accruals(period, user_id)
            
            # Step 3: Close temporary accounts
            result = ClosingService._close_temporary_accounts(period, user_id)
            
            # Step 4: Update retained earnings
            ClosingService._update_retained_earnings(period, user_id)
            
            db.session.commit()
            
            AuditLogger.log(
                user_id=user_id,
                action=AuditAction.CLOSE,
                entity_type="period",
                entity_id=period,
                new_values={"status": "closed"}
            )
            
            return {
                "period": period,
                "status": "closed",
                "accruals_created": len(accruals),
                "accounts_closed": result["count"],
                "total_amount": result["amount"]
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Period close failed for {period}: {str(e)}")
            raise

    @staticmethod
    def _generate_accruals(period: str, user_id: str) -> List[Dict]:
        """Identify and create missing accrual entries"""
        # Find expenses incurred but not recorded
        accrual_candidates = db.session.query(
            ChartOfAccount.id,
            ChartOfAccount.account_name,
            (func.sum(JournalLine.debit_amount) * 0.2).label("estimated_accrual")
        ).join(JournalLine).join(JournalHeader).filter(
            ChartOfAccount.account_type == "expense",
            JournalHeader.period == period,
            JournalHeader.doc_date >= f"{period}-25"  # Last week of month
        ).group_by(ChartOfAccount.id).having(
            func.sum(JournalLine.debit_amount) > 1000  # Threshold
        ).all()
        
        accruals = []
        for acc in accrual_candidates:
            # Create reversing journal entry
            entry = JournalHeader(
                period=period,
                doc_date=f"{period}-01",
                reference=f"Accrual Reversal {acc.account_name}",
                status="posted",
                book_type="accrual",
                created_by=user_id
            )
            db.session.add(entry)
            db.session.flush()
            
            JournalLine(
                journal_id=entry.id,
                account_id=acc.id,
                description=f"Month-end accrual reversal",
                credit_amount=float(acc.estimated_accrual),
                line_no=1
            )
            
            accruals.append({
                "account_id": acc.id,
                "amount": float(acc.estimated_accrual),
                "entry_id": entry.id
            })
        
        return accruals

    @staticmethod
    def _close_temporary_accounts(period: str, user_id: str) -> Dict:
        """Close revenue/expense accounts to retained earnings"""
        # Get net income/loss
        result = db.session.query(
            func.sum(
                case([
                    (ChartOfAccount.account_type == "revenue", JournalLine.credit_amount),
                    (ChartOfAccount.account_type == "expense", JournalLine.debit_amount)
                ], else_=0)
            ).label("net_income")
        ).join(JournalLine).join(JournalHeader).filter(
            JournalHeader.period == period,
            JournalHeader.status == "posted"
        ).scalar()
        
        net_income = float(result or 0)
        
        # Create closing entry
        entry = JournalHeader(
            period=period,
            doc_date=f"{period}-01",
            reference=f"Period Close {period}",
            status="posted",
            book_type="closing",
            created_by=user_id
        )
        db.session.add(entry)
        db.session.flush()
        
        # Close revenue accounts
        revenues = ChartOfAccount.query.filter_by(account_type="revenue").all()
        for account in revenues:
            balance = account.get_balance()
            if balance > 0:
                JournalLine(
                    journal_id=entry.id,
                    account_id=account.id,
                    description="Revenue closing",
                    debit_amount=balance,
                    line_no=1
                )
        
        # Close expense accounts
        expenses = ChartOfAccount.query.filter_by(account_type="expense").all()
        for account in expenses:
            balance = account.get_balance()
            if balance > 0:
                JournalLine(
                    journal_id=entry.id,
                    account_id=account.id,
                    description="Expense closing",
                    credit_amount=balance,
                    line_no=2
                )
        
        return {
            "count": len(revenues) + len(expenses),
            "amount": net_income
        }

    @staticmethod
    def _update_retained_earnings(period: str, user_id: str) -> None:
        """Update retained earnings with period's net income"""
        re_account = ChartOfAccount.query.filter_by(code="3500").first()  # Retained Earnings
        if not re_account:
            raise ValueError("Retained earnings account not found")
        
        net_income = ClosingService._get_net_income(period)
        re_account.balance += net_income

    @staticmethod
    def _get_net_income(period: str) -> float:
        """Calculate net income for the period"""
        result = db.session.query(
            func.sum(
                case([
                    (ChartOfAccount.account_type == "revenue", JournalLine.credit_amount),
                    (ChartOfAccount.account_type == "expense", JournalLine.debit_amount)
                ], else_=0)
            )
        ).join(JournalLine).join(JournalHeader).filter(
            JournalHeader.period == period,
            JournalHeader.status == "posted"
        ).scalar()
        
        return float(result or 0)