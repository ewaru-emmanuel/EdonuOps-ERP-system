# backend/services/finance/reporting_service.py
from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from io import BytesIO

import pandas as pd
from sqlalchemy import func, extract, case

from app import db
from modules.finance.models import (
    ChartOfAccount,
    JournalHeader,
    JournalLine,
    Budget
)

logger = logging.getLogger(__name__)

class FinancialReportService:
    
    @staticmethod
    def generate_trial_balance(start_date: str, end_date: str, entity: str = None) -> Dict:
        """Generate trial balance report between dates"""
        try:
            query = db.session.query(
                ChartOfAccount.code,
                ChartOfAccount.account_name,
                ChartOfAccount.account_type,
                func.sum(JournalLine.debit_amount).label("total_debit"),
                func.sum(JournalLine.credit_amount).label("total_credit"),
                (func.sum(JournalLine.debit_amount) - func.sum(JournalLine.credit_amount)).label("balance")
            ).join(JournalLine).join(JournalHeader).filter(
                JournalHeader.doc_date.between(start_date, end_date),
                JournalHeader.status == "posted"
            ).group_by(ChartOfAccount.id)
            
            if entity:
                query = query.filter(JournalHeader.entity == entity)
                
            results = query.all()
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "accounts": [{
                    "code": r.code,
                    "name": r.account_name,
                    "type": r.account_type,
                    "debit": float(r.total_debit or 0),
                    "credit": float(r.total_credit or 0),
                    "balance": float(r.balance or 0)
                } for r in results],
                "totals": {
                    "debit": sum(float(r.total_debit or 0) for r in results),
                    "credit": sum(float(r.total_credit or 0) for r in results)
                }
            }
        except Exception as e:
            logger.error(f"Trial balance generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_balance_sheet(as_of_date: str, entity: str = None) -> Dict:
        """Generate balance sheet snapshot"""
        try:
            # Asset accounts
            assets = db.session.query(
                func.sum(JournalLine.debit_amount - JournalLine.credit_amount)
            ).join(ChartOfAccount).join(JournalHeader).filter(
                ChartOfAccount.account_type == "asset",
                JournalHeader.doc_date <= as_of_date,
                JournalHeader.status == "posted"
            )
            
            if entity:
                assets = assets.filter(JournalHeader.entity == entity)
                
            total_assets = assets.scalar() or 0.0
            
            # Liability accounts
            liabilities = db.session.query(
                func.sum(JournalLine.credit_amount - JournalLine.debit_amount)
            ).join(ChartOfAccount).join(JournalHeader).filter(
                ChartOfAccount.account_type == "liability",
                JournalHeader.doc_date <= as_of_date,
                JournalHeader.status == "posted"
            )
            
            if entity:
                liabilities = liabilities.filter(JournalHeader.entity == entity)
                
            total_liabilities = liabilities.scalar() or 0.0
            
            # Equity accounts
            equity = db.session.query(
                func.sum(JournalLine.credit_amount - JournalLine.debit_amount)
            ).join(ChartOfAccount).join(JournalHeader).filter(
                ChartOfAccount.account_type == "equity",
                JournalHeader.doc_date <= as_of_date,
                JournalHeader.status == "posted"
            )
            
            if entity:
                equity = equity.filter(JournalHeader.entity == entity)
                
            total_equity = equity.scalar() or 0.0
            
            return {
                "as_of_date": as_of_date,
                "assets": total_assets,
                "liabilities": total_liabilities,
                "equity": total_equity,
                "balance": total_assets - (total_liabilities + total_equity)
            }
        except Exception as e:
            logger.error(f"Balance sheet generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_income_report(start_date: str, end_date: str, entity: str = None) -> Dict:
        """Generate income statement (P&L)"""
        try:
            # Revenue accounts
            revenue = db.session.query(
                func.sum(JournalLine.credit_amount - JournalLine.debit_amount)
            ).join(ChartOfAccount).join(JournalHeader).filter(
                ChartOfAccount.account_type == "revenue",
                JournalHeader.doc_date.between(start_date, end_date),
                JournalHeader.status == "posted"
            )
            
            if entity:
                revenue = revenue.filter(JournalHeader.entity == entity)
                
            total_revenue = revenue.scalar() or 0.0
            
            # Expense accounts
            expenses = db.session.query(
                func.sum(JournalLine.debit_amount - JournalLine.credit_amount)
            ).join(ChartOfAccount).join(JournalHeader).filter(
                ChartOfAccount.account_type == "expense",
                JournalHeader.doc_date.between(start_date, end_date),
                JournalHeader.status == "posted"
            )
            
            if entity:
                expenses = expenses.filter(JournalHeader.entity == entity)
                
            total_expenses = expenses.scalar() or 0.0
            
            return {
                "period": f"{start_date} to {end_date}",
                "revenue": total_revenue,
                "expenses": total_expenses,
                "net_income": total_revenue - total_expenses
            }
        except Exception as e:
            logger.error(f"Income report generation failed: {str(e)}")
            raise

    @staticmethod
    def export_to_excel(report_data: Dict, report_type: str) -> BytesIO:
        """Convert report data to Excel format"""
        try:
            output = BytesIO()
            
            if report_type == "trial_balance":
                df = pd.DataFrame(report_data["accounts"])
                df['balance'] = df['debit'] - df['credit']
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Trial Balance', index=False)
                    
            elif report_type == "balance_sheet":
                data = [
                    ["Assets", report_data["assets"]],
                    ["Liabilities", report_data["liabilities"]],
                    ["Equity", report_data["equity"]],
                    ["Total", report_data["assets"] - (report_data["liabilities"] + report_data["equity"])]
                ]
                df = pd.DataFrame(data, columns=["Account Type", "Amount"])
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Balance Sheet', index=False)
                    
            output.seek(0)
            return output
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise