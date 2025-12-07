from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import text

# Chart of Accounts
class ChartOfAccounts(db.Model):
    __tablename__ = 'advanced_chart_of_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(20), unique=True, nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    account_category = db.Column(db.String(50))  # Current Assets, Fixed Assets, etc.
    parent_account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_account = db.relationship('ChartOfAccounts', remote_side=[id], backref='sub_accounts')
    journal_entries = db.relationship('GeneralLedgerEntry', backref='account', lazy='dynamic')

# General Ledger - Enhanced
class GeneralLedgerEntry(db.Model):
    __tablename__ = 'advanced_general_ledger_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    journal_header_id = db.Column(db.Integer, db.ForeignKey('advanced_journal_headers.id'))
    entry_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'), nullable=False)
    debit_amount = db.Column(db.Float, default=0.0)
    credit_amount = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='posted')  # draft, posted, void
    journal_type = db.Column(db.String(50))  # manual, system, recurring
    fiscal_period = db.Column(db.String(10))  # YYYY-MM
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    approved_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships are defined in ChartOfAccounts model
    
    # Payment method integration fields
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    payment_reference = db.Column(db.String(100))
    source_module = db.Column(db.String(50))  # e.g., 'AR', 'AP', 'Manual', 'Inventory'
    source_transaction_id = db.Column(db.Integer)  # ID in the source module
    
    # Audit fields
    audit_trail = db.Column(db.Text)  # JSON string for audit trail

# Posting Rules Configuration
class PostingRule(db.Model):
    __tablename__ = 'posting_rules'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # goods_receipt, invoice_received, payment_made
    event_description = db.Column(db.String(200))
    debit_account_name = db.Column(db.String(100), nullable=False)
    credit_account_name = db.Column(db.String(100), nullable=False)
    conditions = db.Column(JSON)  # JSON field for flexible conditions
    priority = db.Column(db.Integer, default=1)  # For multiple rules per event
    valid_from = db.Column(db.Date, default=datetime.utcnow)
    valid_to = db.Column(db.Date)  # NULL = active indefinitely
    business_unit = db.Column(db.String(50))  # For different BU rules
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit trail for rule changes
    change_reason = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)

# Journal Header Model
class JournalHeader(db.Model):
    __tablename__ = 'advanced_journal_headers'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    journal_number = db.Column(db.String(50), unique=True, nullable=False)
    source_module = db.Column(db.String(50), nullable=False)  # Finance, Inventory, Procurement, Sales
    source_document_type = db.Column(db.String(50))  # PO, Invoice, Receipt, Payment
    reference_id = db.Column(db.String(50))  # PO#123, INV#456, etc.
    posting_date = db.Column(db.Date, nullable=False)
    document_date = db.Column(db.Date, nullable=False)
    fiscal_period = db.Column(db.String(10), nullable=False)  # YYYY-MM
    description = db.Column(db.Text)
    total_debit = db.Column(db.Float, default=0.0)
    total_credit = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    
    # Status and workflow
    status = db.Column(db.String(20), default='draft')  # draft, posted, reversed, cancelled
    posting_status = db.Column(db.String(20), default='unposted')  # unposted, posted, error
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # User metadata
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    posted_by = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    reversed_by = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    reversed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lines = db.relationship('GeneralLedgerEntry', backref='journal_header', lazy='dynamic')
    
    # Audit and compliance
    audit_trail = db.Column(JSON)  # JSON field for audit events
    reversal_reason = db.Column(db.Text)
    reversal_journal_id = db.Column(db.Integer, db.ForeignKey('advanced_journal_headers.id'))

# Company Settings - Base Currency
class CompanySettings(db.Model):
    __tablename__ = 'advanced_company_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='string')  # string, number, boolean, json
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Accounts Payable - Enhanced
class AccountsPayable(db.Model):
    __tablename__ = 'advanced_accounts_payable'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('finance_vendors.id'), nullable=False)
    vendor_name = db.Column(db.String(100))
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    outstanding_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    status = db.Column(db.String(20), default='pending')  # pending, approved, paid, overdue, void
    payment_terms = db.Column(db.String(50))
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    
    # Payment tracking fields
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    payment_reference = db.Column(db.String(100))  # Check #, Wire confirmation, etc.
    payment_date = db.Column(db.Date)  # When payment was made
    processing_fee = db.Column(db.Float, default=0.0)  # Wire fees, etc.
    actual_payment_amount = db.Column(db.Float)  # Amount actually paid (may differ from total)
    payment_notes = db.Column(db.Text)
    
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = db.relationship('FinanceVendor', backref='payables')
    payments = db.relationship('APPayment', backref='invoice', lazy='dynamic')
    # Payment relationships will be added after payment models are defined

# Accounts Receivable - Enhanced
class AccountsReceivable(db.Model):
    __tablename__ = 'advanced_accounts_receivable'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('finance_customers.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    outstanding_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, void
    payment_terms = db.Column(db.String(50))
    credit_limit = db.Column(db.Float)
    dunning_level = db.Column(db.Integer, default=0)
    last_reminder_date = db.Column(db.Date)
    
    # Payment tracking fields
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    payment_reference = db.Column(db.String(100))  # Check #, Transaction ID, etc.
    payment_date = db.Column(db.Date)  # When payment was received
    processing_fee = db.Column(db.Float, default=0.0)  # Credit card fees, etc.
    net_amount_received = db.Column(db.Float)  # Amount after processing fees
    payment_notes = db.Column(db.Text)
    
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('FinanceCustomer', backref='receivables')
    payments = db.relationship('ARPayment', backref='invoice', lazy='dynamic')
    # Payment relationships will be added after payment models are defined

# Fixed Assets - Enhanced
class FixedAsset(db.Model):
    __tablename__ = 'advanced_fixed_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(50), unique=True, nullable=False)
    asset_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50))
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    salvage_value = db.Column(db.Float, default=0.0)
    useful_life = db.Column(db.Integer)  # in years
    depreciation_method = db.Column(db.String(50))  # straight-line, declining-balance, etc.
    depreciation_rate = db.Column(db.Float)
    accumulated_depreciation = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(100))
    department = db.Column(db.String(50))
    assigned_to = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, disposed, sold, stolen
    disposal_date = db.Column(db.Date)
    disposal_value = db.Column(db.Float)
    insurance_info = db.Column(db.Text)
    warranty_info = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Budget Management - Enhanced
class Budget(db.Model):
    __tablename__ = 'advanced_budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    fiscal_year = db.Column(db.String(4), nullable=False)
    period = db.Column(db.String(10))  # YYYY-MM
    department = db.Column(db.String(50))
    account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'))
    budgeted_amount = db.Column(db.Float, nullable=False)
    actual_amount = db.Column(db.Float, default=0.0)
    variance_amount = db.Column(db.Float, default=0.0)
    variance_percentage = db.Column(db.Float, default=0.0)
    budget_type = db.Column(db.String(50))  # operating, capital, project
    status = db.Column(db.String(20), default='active')  # active, inactive, archived
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = db.relationship('ChartOfAccounts', backref='budgets')

# Tax Management - Enhanced
class TaxRecord(db.Model):
    __tablename__ = 'advanced_tax_records'
    
    id = db.Column(db.Integer, primary_key=True)
    tax_type = db.Column(db.String(50), nullable=False)  # VAT, GST, Sales Tax, Income Tax
    tax_code = db.Column(db.String(20))
    jurisdiction = db.Column(db.String(100))
    period = db.Column(db.String(10))  # YYYY-MM
    taxable_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float)
    due_date = db.Column(db.Date, nullable=False)
    filing_date = db.Column(db.Date)
    payment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, filed, paid, overdue
    filing_reference = db.Column(db.String(50))
    payment_reference = db.Column(db.String(50))
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Bank Reconciliation - Enhanced
class BankReconciliation(db.Model):
    __tablename__ = 'advanced_bank_reconciliations'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_account = db.Column(db.String(50), nullable=False)
    statement_date = db.Column(db.Date, nullable=False)
    book_balance = db.Column(db.Float, nullable=False)
    bank_balance = db.Column(db.Float, nullable=False)
    difference = db.Column(db.Float, default=0.0)
    outstanding_deposits = db.Column(db.Float, default=0.0)
    outstanding_checks = db.Column(db.Float, default=0.0)
    bank_charges = db.Column(db.Float, default=0.0)
    bank_interest = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, reconciled, cleared
    reconciled_by = db.Column(db.String(100))
    reconciled_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Payment Management
class APPayment(db.Model):
    __tablename__ = 'advanced_ap_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_reference = db.Column(db.String(50), unique=True, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('advanced_accounts_payable.id'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # check, wire, ach, credit_card
    payment_reference = db.Column(db.String(50))
    bank_account = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # pending, processed, cleared, void
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ARPayment(db.Model):
    __tablename__ = 'advanced_ar_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_reference = db.Column(db.String(50), unique=True, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('advanced_accounts_receivable.id'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # check, wire, ach, credit_card
    payment_reference = db.Column(db.String(50))
    bank_account = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # pending, processed, cleared, void
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Vendor and Customer Management
class FinanceVendor(db.Model):
    __tablename__ = 'finance_vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(20), unique=True, nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(50))
    credit_limit = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FinanceCustomer(db.Model):
    __tablename__ = 'finance_customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(50))
    credit_limit = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Audit Trail
class AuditTrail(db.Model):
    __tablename__ = 'advanced_audit_trail'
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # create, update, delete
    old_values = db.Column(db.Text)  # JSON string
    new_values = db.Column(db.Text)  # JSON string
    tenant_id = db.Column(db.String(50), nullable=True, index=True)  # Company/tenant identifier
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Currency model moved to currency_models.py to avoid conflicts

# ExchangeRate model moved to currency_models.py to avoid conflicts

# Depreciation Schedule
class DepreciationSchedule(db.Model):
    __tablename__ = 'advanced_depreciation_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('advanced_fixed_assets.id'), nullable=False)
    period = db.Column(db.String(10), nullable=False)  # YYYY-MM
    depreciation_amount = db.Column(db.Float, nullable=False)
    accumulated_depreciation = db.Column(db.Float, nullable=False)
    book_value = db.Column(db.Float, nullable=False)
    is_posted = db.Column(db.Boolean, default=False)
    posted_date = db.Column(db.Date)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    asset = db.relationship('FixedAsset', backref='depreciation_schedules')

# Invoice Line Items
class InvoiceLineItem(db.Model):
    __tablename__ = 'advanced_invoice_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, nullable=False)
    invoice_type = db.Column(db.String(20), nullable=False)  # ap, ar
    line_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_rate = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'))
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    account = db.relationship('ChartOfAccounts', backref='invoice_line_items')

# Financial Periods
class FinancialPeriod(db.Model):
    __tablename__ = 'advanced_financial_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    period_code = db.Column(db.String(10), unique=True, nullable=False)  # YYYY-MM
    period_name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_open = db.Column(db.Boolean, default=True)
    is_closed = db.Column(db.Boolean, default=False)
    closed_by = db.Column(db.String(100))
    closed_at = db.Column(db.DateTime)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Maintenance Records for Fixed Assets
class MaintenanceRecord(db.Model):
    __tablename__ = 'advanced_maintenance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('advanced_fixed_assets.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # preventive, corrective, emergency, inspection
    maintenance_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Float, default=0.0)
    performed_by = db.Column(db.String(100))
    vendor = db.Column(db.String(100))
    next_maintenance_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='completed')  # scheduled, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, critical
    parts_used = db.Column(db.Text)  # JSON string for parts list
    labor_hours = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = db.relationship('FixedAsset', backref='maintenance_records')

# Tax Filing History
class TaxFilingHistory(db.Model):
    __tablename__ = 'advanced_tax_filing_history'
    
    id = db.Column(db.Integer, primary_key=True)
    tax_type = db.Column(db.String(50), nullable=False)  # income_tax, sales_tax, payroll_tax, etc.
    filing_period = db.Column(db.String(10), nullable=False)  # YYYY-MM
    filing_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference_number = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, filed, accepted, rejected
    jurisdiction = db.Column(db.String(100))
    filing_method = db.Column(db.String(50))  # electronic, paper
    confirmation_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Compliance Reports
class ComplianceReport(db.Model):
    __tablename__ = 'advanced_compliance_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # sox, gdpr, pci, etc.
    report_period = db.Column(db.String(10), nullable=False)  # YYYY-MM
    report_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, failed
    compliance_score = db.Column(db.Float, default=0.0)
    total_checks = db.Column(db.Integer, default=0)
    passed_checks = db.Column(db.Integer, default=0)
    failed_checks = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    findings = db.Column(db.Text)  # JSON string for findings
    recommendations = db.Column(db.Text)
    auditor = db.Column(db.String(100))
    next_review_date = db.Column(db.Date)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# User Activity for Audit Trail
class UserActivity(db.Model):
    __tablename__ = 'advanced_user_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(50))
    action_type = db.Column(db.String(50), nullable=False)  # login, logout, create, update, delete, view
    module = db.Column(db.String(50), nullable=False)  # finance, hcm, crm, etc.
    record_id = db.Column(db.String(50))
    record_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    action_count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    tenant_id = db.Column(db.String(50), nullable=True, index=True)  # Company/tenant identifier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Bank Statements
class BankStatement(db.Model):
    __tablename__ = 'advanced_bank_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_account = db.Column(db.String(50), nullable=False)
    statement_date = db.Column(db.Date, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    reference = db.Column(db.String(100))
    debit_amount = db.Column(db.Float, default=0.0)
    credit_amount = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50))  # deposit, withdrawal, transfer, fee, interest
    category = db.Column(db.String(50))
    is_reconciled = db.Column(db.Boolean, default=False)
    reconciled_date = db.Column(db.Date)
    reconciled_by = db.Column(db.String(100))
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Financial Reports (Enhanced)
class FinancialReport(db.Model):
    __tablename__ = 'advanced_financial_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # p&l, balance_sheet, cash_flow, kpi
    report_period = db.Column(db.String(10), nullable=False)  # YYYY-MM
    report_date = db.Column(db.Date, nullable=False)
    report_data = db.Column(db.Text)  # JSON string
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    generated_by = db.Column(db.String(100))
    is_latest = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(10), default='1.0')
    status = db.Column(db.String(20), default='draft')  # draft, final, approved
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Key Performance Indicators (KPIs)
class KPI(db.Model):
    __tablename__ = 'advanced_kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_code = db.Column(db.String(50), unique=True, nullable=False)
    kpi_name = db.Column(db.String(100), nullable=False)
    kpi_category = db.Column(db.String(50), nullable=False)  # financial, operational, customer, employee
    description = db.Column(db.Text)
    calculation_formula = db.Column(db.Text)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0.0)
    previous_value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20))  # %, $, number, ratio
    frequency = db.Column(db.String(20), default='monthly')  # daily, weekly, monthly, quarterly, yearly
    trend = db.Column(db.String(20))  # increasing, decreasing, stable
    status = db.Column(db.String(20), default='active')  # active, inactive, archived
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
