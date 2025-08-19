import pytest
from datetime import datetime
from app import create_app, db
from modules.finance.models import ChartOfAccount, JournalHeader, JournalLine
from services.closing_service import ClosingService
from app.audit_logger import AuditLog

@pytest.fixture
def app():
    app = create_app(config_name='testing')
    with app.app_context():
        db.create_all()
        
        # Setup test accounts
        accounts = [
            ChartOfAccount(code="4000", account_name="Revenue", account_type="revenue"),
            ChartOfAccount(code="5000", account_name="Expenses", account_type="expense"),
            ChartOfAccount(code="3500", account_name="Retained Earnings", account_type="equity")
        ]
        db.session.add_all(accounts)
        
        # Add test journal entries
        entry = JournalHeader(
            period="2023-10",
            doc_date=datetime(2023,10,15),
            status="posted",
            reference="Test Entry"
        )
        db.session.add(entry)
        db.session.flush()
        
        JournalLine(
            journal_id=entry.id,
            account_id=accounts[0].id,  # Revenue
            credit_amount=1000.00,
            description="Test revenue"
        )
        JournalLine(
            journal_id=entry.id,
            account_id=accounts[1].id,  # Expense
            debit_amount=600.00,
            description="Test expense"
        )
        
        db.session.commit()
        yield app
        db.drop_all()

def test_month_end_close_success(app):
    with app.app_context():
        result = ClosingService.execute_month_end_close("2023-10", "test_user")
        
        assert result["status"] == "closed"
        assert result["accounts_closed"] == 2  # Revenue + Expense
        
        # Verify closing entries exist
        closing_entries = JournalHeader.query.filter_by(closing_entry=True).all()
        assert len(closing_entries) >= 1
        
        # Verify retained earnings updated
        re_account = ChartOfAccount.query.filter_by(code="3500").first()
        assert re_account.balance == 400.00  # 1000 revenue - 600 expense
        
        # Verify audit log
        log = AuditLog.query.filter_by(entity_type="period").first()
        assert log is not None

def test_close_with_unposted_entries(app):
    with app.app_context():
        # Add unposted entry
        entry = JournalHeader(
            period="2023-10",
            doc_date=datetime(2023,10,31),
            status="draft"
        )
        db.session.add(entry)
        db.session.commit()
        
        with pytest.raises(ValueError) as excinfo:
            ClosingService.execute_month_end_close("2023-10", "test_user")
        assert "unposted entries" in str(excinfo.value)

def test_accrual_generation(app):
    with app.app_context():
        # Add late-month expense
        late_entry = JournalHeader(
            period="2023-10",
            doc_date=datetime(2023,10,28),
            status="posted"
        )
        db.session.add(late_entry)
        db.session.flush()
        
        JournalLine(
            journal_id=late_entry.id,
            account_id=2,  # Expense
            debit_amount=200.00,
            description="Late expense"
        )
        db.session.commit()
        
        result = ClosingService.execute_month_end_close("2023-10", "test_user")
        assert result["accruals_created"] == 1
        
        # Verify reversing entry exists
        reversing = JournalHeader.query.filter_by(reversing_entry_id=late_entry.id).first()
        assert reversing is not None