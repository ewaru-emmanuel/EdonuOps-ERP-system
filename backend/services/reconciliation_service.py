import logging
from datetime import datetime, timedelta
from app import db
from sqlalchemy import and_, or_, func, extract
from typing import List, Dict, Optional
from modules.finance.models import (
    ChartOfAccount,
    JournalHeader, 
    JournalLine,
    Budget
)
from .ai_service import AISuggestionService

logger = logging.getLogger(__name__)

class ReconciliationService:
    
    @staticmethod
    def auto_reconcile_account(account_id: int, cutoff_days: int = 30) -> Dict:
        # ... (implementation remains the same with proper imports)
        """
        Automatically reconcile an account by matching debits and credits
        Returns reconciliation report with matched and unmatched items
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=cutoff_days)
            
            # Get unreconciled transactions
            unreconciled = JournalLine.query.filter(
                JournalLine.account_id == account_id,
                JournalLine.reconciled == False,  # noqa
                JournalHeader.status == "posted",
                JournalHeader.doc_date >= cutoff_date
            ).join(JournalHeader).all()
            
            # Group by amount and find matches
            amount_map = {}
            for line in unreconciled:
                amount = line.debit_amount or line.credit_amount
                if amount not in amount_map:
                    amount_map[amount] = []
                amount_map[amount].append(line)
            
            # Find matches (debit = credit)
            matched = []
            for amount, lines in amount_map.items():
                debits = [l for l in lines if l.debit_amount]
                credits = [l for l in lines if l.credit_amount]
                
                while debits and credits:
                    debit = debits.pop()
                    credit = credits.pop()
                    
                    # Create match
                    matched.append({
                        "debit_line_id": debit.id,
                        "credit_line_id": credit.id,
                        "amount": amount,
                        "match_date": datetime.utcnow()
                    })
                    
                    # Mark as reconciled
                    debit.reconciled = True
                    credit.reconciled = True
            
            db.session.commit()
            
            return {
                "account_id": account_id,
                "cutoff_date": cutoff_date.isoformat(),
                "matched_count": len(matched),
                "unmatched_debits": sum(1 for l in unreconciled if l.debit_amount and not l.reconciled),
                "unmatched_credits": sum(1 for l in unreconciled if l.credit_amount and not l.reconciled),
                "matches": matched
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Reconciliation failed for account {account_id}: {str(e)}")
            raise

    @staticmethod
    def detect_missing_entries(entity: str, period: str) -> List[Dict]:
        """
        Detect potentially missing journal entries by comparing
        to historical patterns and industry benchmarks
        """
        try:
            # Get typical monthly entries for this entity
            typical_entries = db.session.query(
                JournalLine.account_id,
                func.count().label("count"),
                func.avg(JournalLine.debit_amount).label("avg_debit"),
                func.avg(JournalLine.credit_amount).label("avg_credit")
            ).join(JournalHeader).filter(
                JournalHeader.entity == entity,
                JournalHeader.status == "posted",
                extract('month', JournalHeader.doc_date) == extract('month', period + '-01')
            ).group_by(JournalLine.account_id).all()
            
            # Get current period entries
            current_entries = db.session.query(
                JournalLine.account_id
            ).join(JournalHeader).filter(
                JournalHeader.entity == entity,
                JournalHeader.period == period,
                JournalHeader.status == "posted"
            ).group_by(JournalLine.account_id).all()
            
            current_accounts = {e.account_id for e in current_entries}
            
            # Find accounts that are typically present but missing
            missing = []
            for entry in typical_entries:
                if entry.account_id not in current_accounts:
                    missing.append({
                        "account_id": entry.account_id,
                        "typical_count": entry.count,
                        "typical_amount": float(entry.avg_debit or entry.avg_credit or 0)
                    })
            
            # Use AI to analyze potential impact
            ai_service = AISuggestionService()
            for item in missing:
                item["impact_analysis"] = ai_service.analyze_missing_entry(
                    entity=entity,
                    account_id=item["account_id"],
                    period=period
                )
            
            return missing
        except Exception as e:
            logger.error(f"Missing entry detection failed: {str(e)}")
            raise

    @staticmethod
    def verify_bank_reconciliation(
        bank_statement: List[Dict], 
        account_id: int,
        tolerance: float = 0.01
    ) -> Dict:
        """
        Verify bank statement against ledger entries
        Returns reconciliation discrepancies
        """
        try:
            # Get ledger entries for the period
            ledger_entries = JournalLine.query.filter(
                JournalLine.account_id == account_id,
                JournalHeader.status == "posted",
                JournalHeader.doc_date.between(
                    min(t['date'] for t in bank_statement),
                    max(t['date'] for t in bank_statement)
                )
            ).join(JournalHeader).all()
            
            # Convert to comparable format
            ledger_map = {}
            for entry in ledger_entries:
                key = (entry.description or "", float(entry.debit_amount or entry.credit_amount or 0))
                ledger_map[key] = entry
            
            # Check each bank transaction
            discrepancies = []
            for trans in bank_statement:
                key = (trans['description'], float(trans['amount']))
                if key not in ledger_map:
                    discrepancies.append({
                        "type": "missing_in_ledger",
                        "bank_data": trans,
                        "difference": trans['amount']
                    })
            
            # Check for ledger entries not in bank statement
            for (desc, amount), entry in ledger_map.items():
                found = any(
                    t['description'] == desc and 
                    abs(float(t['amount']) - amount) < tolerance
                    for t in bank_statement
                )
                if not found:
                    discrepancies.append({
                        "type": "missing_in_bank",
                        "ledger_entry": {
                            "id": entry.id,
                            "date": entry.header.doc_date.isoformat(),
                            "description": desc,
                            "amount": amount
                        },
                        "difference": amount
                    })
            
            return {
                "account_id": account_id,
                "period": {
                    "start": min(t['date'] for t in bank_statement),
                    "end": max(t['date'] for t in bank_statement)
                },
                "discrepancies": discrepancies,
                "match_percentage": 100 * (1 - len(discrepancies)/max(len(bank_statement), len(ledger_entries)))
            }
        except Exception as e:
            logger.error(f"Bank reconciliation failed: {str(e)}")
            raise