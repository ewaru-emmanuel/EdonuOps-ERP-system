from flask import current_app
from app import db
from typing import Dict, Callable
from enum import Enum
import logging
from ..advanced_models import JournalHeader
from app.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class FinanceEventType(Enum):
    JOURNAL_POSTED = "journal_posted"
    ACCOUNT_RECONCILED = "account_reconciled"
    PERIOD_CLOSED = "period_closed"
    BUDGET_ALERT = "budget_alert"

_event_handlers = {}

def register_handler(event_type: FinanceEventType, handler: Callable):
    """Register callback for specific event type"""
    _event_handlers.setdefault(event_type, []).append(handler)

def trigger_event(event_type: FinanceEventType, data: Dict):
    """Notify all registered handlers of an event"""
    for handler in _event_handlers.get(event_type, []):
        try:
            handler(data)
        except Exception as e:
            logger.error(f"EventHandler failed for {event_type}: {str(e)}")

# Built-in event handlers
def _log_finance_event(data: Dict):
    """Default audit logging for all financial events"""
    AuditLogger.log(
        user_id=data.get("user_id", "system"),
        action=data["event_type"].value,
        entity_type=data.get("entity_type"),
        entity_id=data.get("entity_id"),
        new_values=data.get("metadata", {})
    )

def _notify_webhooks(data: Dict):
    """Send event data to registered webhooks"""
    if current_app.config.get("WEBHOOKS_ENABLED"):
        # Implementation would use requests.post to external URLs
        pass

def _update_dashboard_cache(data: Dict):
    """Refresh cached dashboard data"""
    if data["event_type"] in (
        FinanceEventType.JOURNAL_POSTED,
        FinanceEventType.PERIOD_CLOSED
    ):
        current_app.cache.delete("financial_dashboard")

# Register core handlers
register_handler(FinanceEventType.JOURNAL_POSTED, _log_finance_event)
register_handler(FinanceEventType.ACCOUNT_RECONCILED, _log_finance_event)
register_handler(FinanceEventType.PERIOD_CLOSED, _log_finance_event)
register_handler(FinanceEventType.JOURNAL_POSTED, _update_dashboard_cache)

# Model event hooks
def on_journal_posted(journal_id: str, user_id: str):
    entry = JournalHeader.query.get(journal_id)
    trigger_event(FinanceEventType.JOURNAL_POSTED, {
        "entity_type": "journal_entry",
        "entity_id": journal_id,
        "user_id": user_id,
        "metadata": {
            "period": entry.period,
            "amount": sum(l.debit_amount for l in entry.lines)
        }
    })