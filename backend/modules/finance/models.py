from app import db
from datetime import datetime
from sqlalchemy import func, Text
from sqlalchemy.dialects.postgresql import JSONB

# Use JSONB for PostgreSQL (our target database)
def get_json_type():
    """Return JSONB type for PostgreSQL"""
    return JSONB

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)  # Removed unique=True - now unique per user via composite constraint
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # asset, liability, equity, revenue, expense
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    parent_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)  # Account notes for documentation and reference
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide accounts
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = db.relationship('Account', remote_side=[id], backref='children')
    
    # Composite unique constraint: code must be unique per tenant (company-wide)
    # extend_existing=True allows the table to be redefined if imported multiple times
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'code', name='uq_account_tenant_code'),
        {'extend_existing': True},
    )

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM format (legacy)
    doc_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, posted, cancelled
    currency = db.Column(db.String(3), default='USD')
    payment_method = db.Column(db.String(20), default='bank')  # bank, cash, wire, credit_card, check, digital
    total_debit = db.Column(db.Float, default=0.0)
    total_credit = db.Column(db.Float, default=0.0)
    
    # Accounting Period Integration
    accounting_period_id = db.Column(db.Integer, db.ForeignKey('accounting_periods.id'))
    is_backdated = db.Column(db.Boolean, default=False)
    period_locked = db.Column(db.Boolean, default=False)
    backdate_reason = db.Column(db.String(200))
    
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide transactions
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lines = db.relationship('JournalLine', backref='journal_entry', cascade='all, delete-orphan')
    
    # extend_existing=True allows the table to be redefined if imported multiple times
    __table_args__ = {'extend_existing': True}

class JournalLine(db.Model):
    __tablename__ = 'journal_lines'
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    description = db.Column(db.String(200))
    debit_amount = db.Column(db.Float, default=0.0)
    credit_amount = db.Column(db.Float, default=0.0)
    
    # Multi-Currency Support
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    functional_debit_amount = db.Column(db.Float, default=0.0)  # Amount in base currency
    functional_credit_amount = db.Column(db.Float, default=0.0)  # Amount in base currency
    
    # Cost Center, Department, and Project Tracking
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    account = db.relationship('Account')
    
    # extend_existing=True allows the table to be redefined if imported multiple times
    __table_args__ = {'extend_existing': True}

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue, cancelled
    currency = db.Column(db.String(3), default='USD')
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='cash')  # cash, check, credit_card, bank_transfer
    reference_number = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Budget Models
class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM format
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    budget_amount = db.Column(db.Float, nullable=False, default=0.0)
    actual_amount = db.Column(db.Float, default=0.0)
    forecast_amount = db.Column(db.Float, default=0.0)
    scenario = db.Column(db.String(20), default='base')  # base, optimistic, pessimistic, custom
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = db.relationship('Account')

class BudgetScenario(db.Model):
    __tablename__ = 'budget_scenarios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM format
    scenario_type = db.Column(db.String(20), default='custom')  # base, optimistic, pessimistic, custom
    growth_rate = db.Column(db.Float, default=0.0)  # Percentage change from base
    assumptions = db.Column(get_json_type())  # JSON object for custom assumptions
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Indexes
db.Index('ix_journal_lines_account_id', JournalLine.account_id)
db.Index('ix_journal_lines_journal_entry_id', JournalLine.journal_entry_id)
db.Index('ix_accounts_tenant_code', Account.tenant_id, Account.code)  # Composite index for tenant_id + code lookups
db.Index('ix_accounts_tenant_id', Account.tenant_id)  # Index for tenant isolation queries
db.Index('ix_invoices_invoice_number', Invoice.invoice_number)