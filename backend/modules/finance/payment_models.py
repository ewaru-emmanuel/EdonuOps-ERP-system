from app import db
from datetime import datetime, date
from sqlalchemy import Index
from decimal import Decimal

class PaymentMethod(db.Model):
    """
    Master table for payment methods
    Extensible system for different payment types
    """
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # 'CASH', 'CARD', 'BANK_TRANSFER', etc.
    name = db.Column(db.String(50), nullable=False)  # 'Cash', 'Credit Card', 'Bank Transfer', etc.
    description = db.Column(db.String(200))
    
    # Configuration
    requires_reference = db.Column(db.Boolean, default=False)  # Check #, Transaction ID required
    requires_bank_account = db.Column(db.Boolean, default=True)  # Cash doesn't need bank account
    default_processing_fee_rate = db.Column(db.Float, default=0.0)  # Default fee percentage
    
    # Display and ordering
    display_order = db.Column(db.Integer, default=0)
    icon_name = db.Column(db.String(50))  # For UI icons
    color_code = db.Column(db.String(10))  # For UI colors
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)  # System methods can't be deleted
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    def __repr__(self):
        return f'<PaymentMethod {self.code}: {self.name}>'
    
    @classmethod
    def get_active_methods(cls):
        """Get all active payment methods ordered by display_order"""
        return cls.query.filter_by(is_active=True).order_by(cls.display_order, cls.name).all()
    
    @classmethod
    def get_by_code(cls, code):
        """Get payment method by code"""
        return cls.query.filter_by(code=code, is_active=True).first()

class BankAccount(db.Model):
    """
    Bank accounts for tracking where payments are received/made from
    """
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)  # 'Main Checking', 'Merchant Account'
    account_number = db.Column(db.String(50))  # Last 4 digits or masked number
    bank_name = db.Column(db.String(100))
    bank_code = db.Column(db.String(20))  # Routing number, SWIFT, etc.
    
    # Account details
    account_type = db.Column(db.String(20), nullable=False)  # 'checking', 'savings', 'merchant', 'credit_line'
    currency = db.Column(db.String(3), default='USD')
    
    # Integration
    gl_account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'))  # Link to GL account
    
    # Configuration
    is_default = db.Column(db.Boolean, default=False)  # Default account for new payments
    allow_deposits = db.Column(db.Boolean, default=True)  # Can receive payments
    allow_withdrawals = db.Column(db.Boolean, default=True)  # Can make payments
    
    # Limits and controls
    daily_limit = db.Column(db.Float)  # Daily transaction limit
    monthly_limit = db.Column(db.Float)  # Monthly transaction limit
    requires_approval = db.Column(db.Boolean, default=False)  # Requires approval for payments
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # External provider integration fields
    provider = db.Column(db.String(20))  # plaid, yodlee, manual
    external_account_id = db.Column(db.String(100))
    access_token = db.Column(db.Text)  # Encrypted in production
    connected_at = db.Column(db.DateTime)
    connected_by = db.Column(db.String(100))
    last_sync_at = db.Column(db.DateTime)
    sync_frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    gl_account = db.relationship('ChartOfAccounts', backref='bank_accounts')
    
    def __repr__(self):
        return f'<BankAccount {self.account_name} ({self.account_type})>'
    
    @classmethod
    def get_active_accounts(cls):
        """Get all active bank accounts"""
        return cls.query.filter_by(is_active=True).order_by(cls.account_name).all()
    
    @classmethod
    def get_default_account(cls):
        """Get the default bank account"""
        return cls.query.filter_by(is_default=True, is_active=True).first()
    
    @classmethod
    def get_deposit_accounts(cls):
        """Get accounts that can receive deposits"""
        return cls.query.filter_by(is_active=True, allow_deposits=True).order_by(cls.account_name).all()
    
    @classmethod
    def get_withdrawal_accounts(cls):
        """Get accounts that can make payments"""
        return cls.query.filter_by(is_active=True, allow_withdrawals=True).order_by(cls.account_name).all()

class PaymentTransaction(db.Model):
    """
    Individual payment transactions - links to AR/AP payments
    Provides detailed payment method and bank account tracking
    """
    __tablename__ = 'payment_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Payment details
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    
    # Payment method and account
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=False)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))  # Null for cash payments
    
    # Reference information
    payment_reference = db.Column(db.String(100))  # Check #, Transaction ID, etc.
    external_reference = db.Column(db.String(100))  # Bank confirmation, etc.
    
    # Fee tracking
    processing_fee = db.Column(db.Float, default=0.0)
    fee_account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'))  # GL account for fees
    net_amount = db.Column(db.Float)  # Amount after fees
    
    # Transaction type and linking
    transaction_type = db.Column(db.String(20), nullable=False)  # 'ar_payment', 'ap_payment', 'manual'
    source_table = db.Column(db.String(50))  # 'accounts_receivable', 'accounts_payable'
    source_id = db.Column(db.Integer)  # ID in source table
    
    # Status
    status = db.Column(db.String(20), default='completed')  # 'pending', 'completed', 'failed', 'cancelled'
    cleared_date = db.Column(db.Date)  # When payment cleared (for checks)
    
    # Notes and description
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    payment_method = db.relationship('PaymentMethod', backref='transactions')
    bank_account = db.relationship('BankAccount', backref='transactions')
    fee_account = db.relationship('ChartOfAccounts', backref='fee_transactions')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_payment_transaction_date', 'payment_date'),
        Index('idx_payment_transaction_method', 'payment_method_id'),
        Index('idx_payment_transaction_account', 'bank_account_id'),
        Index('idx_payment_transaction_source', 'source_table', 'source_id'),
    )
    
    def __repr__(self):
        return f'<PaymentTransaction {self.transaction_number}: {self.amount}>'
    
    @property
    def calculated_net_amount(self):
        """Calculate net amount after processing fees"""
        return (self.amount or 0) - (self.processing_fee or 0)
    
    def save(self):
        """Save with automatic net amount calculation"""
        if self.net_amount is None:
            self.net_amount = self.calculated_net_amount
        db.session.add(self)
        db.session.commit()
        return self


class ExchangeRate(db.Model):
    """
    Exchange rates for multi-currency support
    Historical rates for accurate reporting
    """
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(3), nullable=False)  # Base currency
    to_currency = db.Column(db.String(3), nullable=False)    # Target currency
    rate = db.Column(db.Float, nullable=False)               # Exchange rate
    rate_date = db.Column(db.Date, nullable=False)          # Date of the rate
    
    # Source information
    source = db.Column(db.String(50), default='manual')     # 'manual', 'api', 'bank'
    source_reference = db.Column(db.String(100))            # API reference or bank name
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_exchange_rates_currency_date', 'from_currency', 'to_currency', 'rate_date'),
        Index('idx_exchange_rates_date', 'rate_date'),
    )
    
    def __repr__(self):
        return f'<ExchangeRate {self.from_currency}/{self.to_currency} = {self.rate} on {self.rate_date}>'
    
    @classmethod
    def get_rate(cls, from_currency, to_currency, rate_date=None):
        """Get exchange rate for currency pair on specific date"""
        if rate_date is None:
            rate_date = date.today()
        
        # Try exact date first
        rate = cls.query.filter_by(
            from_currency=from_currency,
            to_currency=to_currency,
            rate_date=rate_date
        ).first()
        
        if rate:
            return rate.rate
        
        # If no exact date, get most recent rate before the date
        rate = cls.query.filter(
            cls.from_currency == from_currency,
            cls.to_currency == to_currency,
            cls.rate_date <= rate_date
        ).order_by(cls.rate_date.desc()).first()
        
        if rate:
            return rate.rate
        
        # If no historical rate, return 1.0 for same currency or None
        if from_currency == to_currency:
            return 1.0
        
        return None
    
    @classmethod
    def set_rate(cls, from_currency, to_currency, rate, rate_date=None, source='manual', created_by=None):
        """Set exchange rate for currency pair"""
        if rate_date is None:
            rate_date = date.today()
        
        # Check if rate already exists for this date
        existing = cls.query.filter_by(
            from_currency=from_currency,
            to_currency=to_currency,
            rate_date=rate_date
        ).first()
        
        if existing:
            existing.rate = rate
            existing.source = source
            existing.created_by = created_by
        else:
            new_rate = cls(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=rate,
                rate_date=rate_date,
                source=source,
                created_by=created_by
            )
            db.session.add(new_rate)
        
        db.session.commit()
        return existing or new_rate


class PartialPayment(db.Model):
    """
    Track partial payments for invoices
    Allows multiple payments per invoice
    """
    __tablename__ = 'partial_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_reference = db.Column(db.String(100), nullable=False)
    
    # Invoice reference (can be AR or AP)
    invoice_id = db.Column(db.Integer, nullable=False)
    invoice_type = db.Column(db.String(10), nullable=False)  # 'AR' or 'AP'
    
    # Payment details
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    base_amount = db.Column(db.Float, nullable=False)  # Amount in base currency
    
    # Payment method and account
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=False)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    
    # Processing fees
    processing_fee = db.Column(db.Float, default=0.0)
    net_amount = db.Column(db.Float, nullable=False)  # Amount after fees
    
    # Reference information
    reference_number = db.Column(db.String(100))  # Check #, Transaction ID, etc.
    notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'cleared', 'failed', 'reversed'
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    payment_method = db.relationship('PaymentMethod', backref='partial_payments')
    bank_account = db.relationship('BankAccount', backref='partial_payments')
    
    def __repr__(self):
        return f'<PartialPayment {self.payment_reference} - ${self.amount} for {self.invoice_type}#{self.invoice_id}>'
    
    @property
    def calculated_net_amount(self):
        """Calculate net amount after processing fees"""
        return float(Decimal(str(self.amount)) - Decimal(str(self.processing_fee)))
    
    def save(self):
        """Save with automatic net amount calculation"""
        if self.net_amount is None:
            self.net_amount = self.calculated_net_amount
        db.session.add(self)
        db.session.commit()
        return self
    
    @classmethod
    def get_invoice_payments(cls, invoice_id, invoice_type):
        """Get all partial payments for a specific invoice"""
        return cls.query.filter_by(
            invoice_id=invoice_id,
            invoice_type=invoice_type
        ).order_by(cls.payment_date.desc()).all()
    
    @classmethod
    def get_total_paid(cls, invoice_id, invoice_type):
        """Get total amount paid for an invoice"""
        payments = cls.query.filter_by(
            invoice_id=invoice_id,
            invoice_type=invoice_type,
            status='cleared'
        ).all()
        
        return sum(payment.net_amount for payment in payments)


class BankTransaction(db.Model):
    """
    Bank transactions imported from bank statements
    """
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    
    # Transaction details
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Positive for deposits, negative for withdrawals
    reference = db.Column(db.String(100))  # Check number, transaction ID, etc.
    description = db.Column(db.String(255))
    
    # Bank statement details
    statement_date = db.Column(db.Date)  # When it appeared on bank statement
    bank_reference = db.Column(db.String(100))  # Bank's internal reference
    
    # Matching status
    matched = db.Column(db.Boolean, default=False)
    matched_transaction_id = db.Column(db.Integer)  # Link to AR/AP/GL ID
    matched_transaction_type = db.Column(db.String(20))  # 'AR', 'AP', 'GL'
    
    # Reconciliation
    reconciliation_session_id = db.Column(db.Integer, db.ForeignKey('reconciliation_sessions.id'))
    reconciled_by = db.Column(db.String(100))
    reconciled_at = db.Column(db.DateTime)
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    bank_account = db.relationship('BankAccount', backref='bank_transactions')
    reconciliation_session = db.relationship('ReconciliationSession', backref='bank_transactions')
    
    def __repr__(self):
        return f'<BankTransaction {self.reference} - {self.amount}>'


class ReconciliationSession(db.Model):
    """
    Tracks batch reconciliations for a specific bank account and period
    """
    __tablename__ = 'reconciliation_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    
    # Session details
    statement_date = db.Column(db.Date, nullable=False)
    statement_balance = db.Column(db.Float, nullable=False)  # Bank statement ending balance
    book_balance = db.Column(db.Float, nullable=False)  # ERP book balance
    difference = db.Column(db.Float, default=0.0)  # Statement - Book balance
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, disputed
    completed_at = db.Column(db.DateTime)
    completed_by = db.Column(db.String(100))
    
    # Outstanding items
    outstanding_deposits = db.Column(db.Float, default=0.0)
    outstanding_checks = db.Column(db.Float, default=0.0)
    bank_charges = db.Column(db.Float, default=0.0)
    bank_interest = db.Column(db.Float, default=0.0)
    
    # Notes and audit
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    bank_account = db.relationship('BankAccount', backref='reconciliation_sessions')
    
    def __repr__(self):
        return f'<ReconciliationSession {self.bank_account.account_name} - {self.statement_date}>'
