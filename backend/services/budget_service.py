# backend/services/finance/budget_service.py
from __future__ import annotations
import logging
from datetime import datetime
from typing import Dict, List

from sqlalchemy import func, extract, case, and_

from app import db
from modules.finance.models import (
    ChartOfAccount,
    JournalHeader,
    JournalLine,
    Budget
)

logger = logging.getLogger(__name__)

class BudgetService:
    
    @staticmethod
    def compare_to_budget(period: str, cost_center: str = None) -> Dict:
        """Compare actuals vs budget for a period"""
        try:
            actuals = db.session.query(
                ChartOfAccount.account_type,
                func.sum(JournalLine.debit_amount - JournalLine.credit_amount).label("amount")
            ).join(JournalLine).join(JournalHeader).join(Budget).filter(
                JournalHeader.period == period,
                JournalHeader.status == "posted",
                Budget.period == period
            ).group_by(ChartOfAccount.account_type).all()
            
            budgets = db.session.query(
                Budget.account_type,
                Budget.amount
            ).filter_by(period=period).all()
            
            return {
                "period": period,
                "comparisons": [{
                    "account_type": act.account_type,
                    "actual": float(act.amount or 0),
                    "budget": next(
                        (float(bud.amount) for bud in budgets 
                        if bud.account_type == act.account_type), 0
                    ),
                    "variance": float(act.amount or 0) - next(
                        (float(bud.amount) for bud in budgets 
                        if bud.account_type == act.account_type), 0
                    )
                } for act in actuals]
            }
        except Exception as e:
            logger.error(f"Budget comparison failed: {str(e)}")
            raise

    @staticmethod
    def forecast_cashflow(
        months: int = 6, 
        entity: str = None,
        scenario: str = "base_case"
    ) -> List[Dict]:
        """Generate cash flow forecast"""
        try:
            # Historical cash inflows/outflows
            history = db.session.query(
                extract('month', JournalHeader.doc_date).label("month"),
                extract('year', JournalHeader.doc_date).label("year"),
                func.sum(
                    case([(ChartOfAccount.account_type == "asset", JournalLine.debit_amount)],
                        else_=JournalLine.credit_amount)
                ).label("inflows"),
                func.sum(
                    case([(ChartOfAccount.account_type == "asset", JournalLine.credit_amount)],
                        else_=JournalLine.debit_amount)
                ).label("outflows")
            ).join(JournalLine).join(ChartOfAccount).filter(
                ChartOfAccount.code.in_(["1000", "2000"]),  # Cash and AR accounts
                JournalHeader.status == "posted"
            ).group_by("month", "year").order_by("year", "month").all()
            
            # Apply forecasting model (simplified)
            forecast = []
            for i in range(1, months + 1):
                month = (datetime.now().month + i - 1) % 12 + 1
                year = datetime.now().year + (datetime.now().month + i - 1) // 12
                
                # Find historical average (simplified)
                avg_in = sum(h.inflows for h in history if h.month == month) / max(len([h for h in history if h.month == month]), 1)
                avg_out = sum(h.outflows for h in history if h.month == month) / max(len([h for h in history if h.month == month]), 1)
                
                # Apply scenario adjustments
                if scenario == "optimistic":
                    adj_in, adj_out = 1.1, 0.9
                elif scenario == "pessimistic":
                    adj_in, adj_out = 0.9, 1.1
                else:
                    adj_in, adj_out = 1.0, 1.0
                    
                forecast.append({
                    "month": f"{year}-{month:02d}",
                    "projected_inflow": avg_in * adj_in,
                    "projected_outflow": avg_out * adj_out,
                    "net_cashflow": (avg_in * adj_in) - (avg_out * adj_out)
                })
                
            return forecast
        except Exception as e:
            logger.error(f"Cashflow forecast failed: {str(e)}")
            raise