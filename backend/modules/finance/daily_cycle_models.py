from app import db
from datetime import datetime, date
from sqlalchemy import func, Index
from typing import Dict, List, Optional

class DailyBalance(db.Model):
    """
    Stores daily opening and closing balances for all accounts
    This ensures proper daily cycle management and audit trail
    """
    __tablename__ = 'daily_balances'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'), nullable=False)
    balance_date = db.Column(db.Date, nullable=False)
    
    # Opening balances (start of day)
    opening_debit = db.Column(db.Float, default=0.0)
    opening_credit = db.Column(db.Float, default=0.0)
    opening_balance = db.Column(db.Float, default=0.0)
    
    # Daily movements
    daily_debit = db.Column(db.Float, default=0.0)
    daily_credit = db.Column(db.Float, default=0.0)
    daily_net_movement = db.Column(db.Float, default=0.0)
    
    # Closing balances (end of day)
    closing_debit = db.Column(db.Float, default=0.0)
    closing_credit = db.Column(db.Float, default=0.0)
    closing_balance = db.Column(db.Float, default=0.0)
    
    # Status tracking
    is_opening_captured = db.Column(db.Boolean, default=False)
    is_closing_calculated = db.Column(db.Boolean, default=False)
    cycle_status = db.Column(db.String(20), default='pending')  # pending, opening_captured, closing_calculated, completed
    
    # Locking mechanism
    is_locked = db.Column(db.Boolean, default=False)
    locked_at = db.Column(db.DateTime)
    locked_by = db.Column(db.String(100))
    lock_reason = db.Column(db.String(200))  # 'day_closed', 'manual_lock', 'scheduled_lock'
    
    # Grace period for adjustments
    grace_period_ends = db.Column(db.DateTime)
    allows_adjustments = db.Column(db.Boolean, default=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    
    # Relationships
    account = db.relationship('ChartOfAccounts', backref='daily_balances')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_daily_balance_date_account', 'balance_date', 'account_id'),
        Index('idx_daily_balance_date', 'balance_date'),
        Index('idx_daily_balance_status', 'cycle_status'),
    )
    
    def __repr__(self):
        return f'<DailyBalance {self.account.account_name} - {self.balance_date}>'
    
    @classmethod
    def get_balance_for_date(cls, account_id: int, balance_date: date) -> Optional['DailyBalance']:
        """Get daily balance for specific account and date"""
        return cls.query.filter_by(
            account_id=account_id,
            balance_date=balance_date
        ).first()
    
    @classmethod
    def get_latest_balance(cls, account_id: int, before_date: date = None) -> Optional['DailyBalance']:
        """Get the most recent balance for an account before a specific date"""
        query = cls.query.filter_by(account_id=account_id)
        if before_date:
            query = query.filter(cls.balance_date < before_date)
        return query.order_by(cls.balance_date.desc()).first()
    
    @classmethod
    def get_daily_balances_for_date(cls, balance_date: date) -> List['DailyBalance']:
        """Get all daily balances for a specific date"""
        return cls.query.filter_by(balance_date=balance_date).all()
    
    @classmethod
    def get_account_balance_history(cls, account_id: int, start_date: date, end_date: date) -> List['DailyBalance']:
        """Get balance history for an account within date range"""
        return cls.query.filter(
            cls.account_id == account_id,
            cls.balance_date >= start_date,
            cls.balance_date <= end_date
        ).order_by(cls.balance_date.asc()).all()

class DailyCycleStatus(db.Model):
    """
    Tracks the overall daily cycle status for the system
    """
    __tablename__ = 'daily_cycle_status'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_date = db.Column(db.Date, nullable=False, unique=True)
    
    # Cycle phases
    opening_captured_at = db.Column(db.DateTime)
    opening_captured_by = db.Column(db.String(100))
    opening_status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, failed
    
    closing_calculated_at = db.Column(db.DateTime)
    closing_calculated_by = db.Column(db.String(100))
    closing_status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, failed
    
    # Summary statistics
    total_accounts = db.Column(db.Integer, default=0)
    accounts_processed = db.Column(db.Integer, default=0)
    total_opening_balance = db.Column(db.Float, default=0.0)
    total_closing_balance = db.Column(db.Float, default=0.0)
    total_daily_movement = db.Column(db.Float, default=0.0)
    
    # Overall status
    overall_status = db.Column(db.String(20), default='pending')  # pending, opening, closing, completed, failed
    error_message = db.Column(db.Text)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DailyCycleStatus {self.cycle_date} - {self.overall_status}>'
    
    @classmethod
    def get_status_for_date(cls, cycle_date: date) -> Optional['DailyCycleStatus']:
        """Get cycle status for specific date"""
        return cls.query.filter_by(cycle_date=cycle_date).first()
    
    @classmethod
    def get_latest_status(cls) -> Optional['DailyCycleStatus']:
        """Get the most recent cycle status"""
        return cls.query.order_by(cls.cycle_date.desc()).first()
    
    @classmethod
    def get_pending_cycles(cls) -> List['DailyCycleStatus']:
        """Get all pending cycle dates"""
        return cls.query.filter(
            cls.overall_status.in_(['pending', 'opening', 'closing'])
        ).order_by(cls.cycle_date.asc()).all()

class DailyTransactionSummary(db.Model):
    """
    Stores daily transaction summaries for quick reporting
    """
    __tablename__ = 'daily_transaction_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    summary_date = db.Column(db.Date, nullable=False)
    
    # Transaction counts
    total_transactions = db.Column(db.Integer, default=0)
    posted_transactions = db.Column(db.Integer, default=0)
    draft_transactions = db.Column(db.Integer, default=0)
    
    # Amount summaries
    total_debits = db.Column(db.Float, default=0.0)
    total_credits = db.Column(db.Float, default=0.0)
    net_movement = db.Column(db.Float, default=0.0)
    
    # Account type summaries
    asset_movement = db.Column(db.Float, default=0.0)
    liability_movement = db.Column(db.Float, default=0.0)
    equity_movement = db.Column(db.Float, default=0.0)
    revenue_movement = db.Column(db.Float, default=0.0)
    expense_movement = db.Column(db.Float, default=0.0)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_daily_summary_date', 'summary_date'),
    )
    
    def __repr__(self):
        return f'<DailyTransactionSummary {self.summary_date}>'
    
    @classmethod
    def get_summary_for_date(cls, summary_date: date) -> Optional['DailyTransactionSummary']:
        """Get transaction summary for specific date"""
        return cls.query.filter_by(summary_date=summary_date).first()
    
    @classmethod
    def get_summaries_for_period(cls, start_date: date, end_date: date) -> List['DailyTransactionSummary']:
        """Get transaction summaries for date range"""
        return cls.query.filter(
            cls.summary_date >= start_date,
            cls.summary_date <= end_date
        ).order_by(cls.summary_date.asc()).all()

class AdjustmentEntry(db.Model):
    """
    Tracks adjustment entries made after day closing
    Maintains audit trail for post-closing changes
    """
    __tablename__ = 'adjustment_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    original_date = db.Column(db.Date, nullable=False)  # Date being adjusted
    adjustment_date = db.Column(db.Date, nullable=False)  # Date when adjustment was made
    account_id = db.Column(db.Integer, db.ForeignKey('advanced_chart_of_accounts.id'), nullable=False)
    
    # Original values (what was there before adjustment)
    original_debit = db.Column(db.Float, default=0.0)
    original_credit = db.Column(db.Float, default=0.0)
    original_balance = db.Column(db.Float, default=0.0)
    
    # Adjustment values
    adjustment_debit = db.Column(db.Float, default=0.0)
    adjustment_credit = db.Column(db.Float, default=0.0)
    adjustment_balance = db.Column(db.Float, default=0.0)
    
    # New values (after adjustment)
    new_debit = db.Column(db.Float, default=0.0)
    new_credit = db.Column(db.Float, default=0.0)
    new_balance = db.Column(db.Float, default=0.0)
    
    # Adjustment details
    adjustment_type = db.Column(db.String(50), nullable=False)  # 'correction', 'late_entry', 'reversal', 'reclassification'
    reason = db.Column(db.Text, nullable=False)
    reference_document = db.Column(db.String(100))  # Invoice number, PO number, etc.
    
    # Authorization
    authorized_by = db.Column(db.String(100), nullable=False)
    approved_by = db.Column(db.String(100))
    approval_notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, applied
    applied_at = db.Column(db.DateTime)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification, nullable=False)
    
    # Relationships
    account = db.relationship('ChartOfAccounts', backref='adjustment_entries')
    
    # Indexes
    __table_args__ = (
        Index('idx_adjustment_original_date', 'original_date'),
        Index('idx_adjustment_account', 'account_id'),
        Index('idx_adjustment_status', 'status'),
    )
    
    def __repr__(self):
        return f'<AdjustmentEntry {self.original_date} - {self.account.account_name}>'
    
    @classmethod
    def get_adjustments_for_date(cls, original_date: date) -> List['AdjustmentEntry']:
        """Get all adjustments for a specific original date"""
        return cls.query.filter_by(original_date=original_date).all()
    
    @classmethod
    def get_pending_adjustments(cls) -> List['AdjustmentEntry']:
        """Get all pending adjustments"""
        return cls.query.filter_by(status='pending').all()

class DailyCycleAuditLog(db.Model):
    """
    Enhanced audit trail for daily cycle operations
    Tracks who did what and when
    """
    __tablename__ = 'daily_cycle_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_date = db.Column(db.Date, nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'opening_captured', 'closing_calculated', 'locked', 'unlocked', 'adjustment_made'
    
    # User information
    user_id = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(200))
    user_role = db.Column(db.String(50))
    
    # Action details
    action_details = db.Column(db.Text)  # JSON string with action-specific details
    affected_accounts = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Float, default=0.0)
    
    # System information
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    session_id = db.Column(db.String(100))
    
    # Timestamps
    action_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_cycle_date', 'cycle_date'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_timestamp', 'action_timestamp'),
    )
    
    def __repr__(self):
        return f'<DailyCycleAuditLog {self.cycle_date} - {self.action} by {self.user_id}>'
    
    @classmethod
    def log_action(cls, cycle_date: date, action: str, user_id: str, **kwargs):
        """Log an audit action"""
        audit_log = cls(
            cycle_date=cycle_date,
            action=action,
            user_id=user_id,
            user_name=kwargs.get('user_name'),
            user_role=kwargs.get('user_role'),
            action_details=kwargs.get('action_details'),
            affected_accounts=kwargs.get('affected_accounts', 0),
            total_amount=kwargs.get('total_amount', 0.0),
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            session_id=kwargs.get('session_id')
        )
        db.session.add(audit_log)
        return audit_log
    
    @classmethod
    def get_audit_trail_for_date(cls, cycle_date: date) -> List['DailyCycleAuditLog']:
        """Get complete audit trail for a specific date"""
        return cls.query.filter_by(cycle_date=cycle_date).order_by(cls.action_timestamp.asc()).all()
    
    @classmethod
    def get_user_actions(cls, user_id: str, start_date: date = None, end_date: date = None) -> List['DailyCycleAuditLog']:
        """Get all actions by a specific user"""
        query = cls.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(cls.cycle_date >= start_date)
        if end_date:
            query = query.filter(cls.cycle_date <= end_date)
        return query.order_by(cls.action_timestamp.desc()).all()
