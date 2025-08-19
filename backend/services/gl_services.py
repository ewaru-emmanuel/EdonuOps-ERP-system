from datetime import datetime
from app import db, socketio
from sqlalchemy import func
import logging
from modules.finance.models import (
    ChartOfAccount,
    JournalHeader, 
    JournalLine,
    Budget
)

logger = logging.getLogger(__name__)

class GLService:
    @staticmethod
    def create_journal_entry(entry_data, user_id):
        # ... (implementation remains the same with proper imports)
        """
        Creates a new journal entry with validation
        """
        try:
            # Validate header
            if not all(k in entry_data for k in ["period", "doc_date", "lines"]):
                raise ValueError("Missing required fields")

            # Create header
            header = JournalHeader(
                period=entry_data["period"],
                doc_date=datetime.strptime(entry_data["doc_date"], "%Y-%m-%d").date(),
                reference=entry_data.get("reference"),
                description=entry_data.get("description"),
                status="draft",
                book_type=entry_data.get("book_type", "general"),
                entity=entry_data.get("entity"),
                currency=entry_data.get("currency", "USD"),
                fx_rate=float(entry_data.get("fx_rate", 1.0)),
                created_by=user_id
            )
            db.session.add(header)
            db.session.flush()

            # Process lines
            lines = []
            for idx, line_data in enumerate(entry_data["lines"], start=1):
                line = JournalLine(
                    journal_id=header.id,
                    account_id=line_data["account_id"],
                    description=line_data.get("description"),
                    debit_amount=float(line_data.get("debit_amount", 0)),
                    credit_amount=float(line_data.get("credit_amount", 0)),
                    line_no=idx,
                    dimensions=line_data.get("dimensions"),
                    source_doc=line_data.get("source_doc")
                )
                db.session.add(line)
                lines.append(line)

            db.session.commit()
            
            # Emit WebSocket event
            socketio.emit('journal_entry_created', {
                'id': header.id,
                'period': header.period,
                'status': header.status
            })

            return header
        except Exception as e:
            db.session.rollback()
            logger.error(f"Journal creation failed: {str(e)}")
            raise

    @staticmethod
    def post_journal_entry(entry_id, user_id):
        """
        Posts a journal entry after validation
        """
        entry = JournalHeader.query.get(entry_id)
        if not entry:
            raise ValueError("Entry not found")

        if entry.status != "approved":
            raise ValueError("Only approved entries can be posted")

        if not entry.is_balanced():
            raise ValueError("Unbalanced journal entry")

        try:
            entry.status = "posted"
            entry.posted_by = user_id
            entry.posted_at = datetime.utcnow()
            db.session.commit()

            # Update account balances
            for line in entry.lines:
                account = line.account
                account.balance = account.get_balance()
            
            db.session.commit()

            socketio.emit('journal_entry_posted', {
                'id': entry.id,
                'period': entry.period
            })

            return entry
        except Exception as e:
            db.session.rollback()
            logger.error(f"Journal posting failed: {str(e)}")
            raise

    @staticmethod
    def get_account_balance(account_id, as_of_date=None):
        """
        Calculates account balance up to specific date
        """
        query = db.session.query(
            func.sum(JournalLine.debit_amount - JournalLine.credit_amount)
        ).join(JournalHeader).filter(
            JournalLine.account_id == account_id,
            JournalHeader.status == "posted"
        )

        if as_of_date:
            query = query.filter(JournalHeader.doc_date <= as_of_date)

        return query.scalar() or 0.0

    @staticmethod
    def get_trial_balance(period=None):
        """
        Generates trial balance report
        """
        query = db.session.query(
            ChartOfAccount.id,
            ChartOfAccount.code,
            ChartOfAccount.account_name,
            func.sum(JournalLine.debit_amount).label("total_debit"),
            func.sum(JournalLine.credit_amount).label("total_credit")
        ).join(JournalLine).join(JournalHeader).filter(
            JournalHeader.status == "posted"
        ).group_by(ChartOfAccount.id)

        if period:
            query = query.filter(JournalHeader.period == period)

        return query.all()