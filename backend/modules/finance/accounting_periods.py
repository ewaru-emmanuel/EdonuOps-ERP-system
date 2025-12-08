"""
Accounting Periods and Fiscal Year Management
============================================

This module provides enterprise-grade accounting period management including:
- Fiscal year definition and management
- Accounting period creation and locking
- Backdated entry prevention
- Audit compliance features
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, or_, func
from app import db

class FiscalYear(db.Model):
    """
    Fiscal Year definition and management
    """
    __tablename__ = 'fiscal_years'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)  # e.g., 2024 (unique per tenant, see __table_args__)
    name = db.Column(db.String(100), nullable=False)  # e.g., "FY 2024"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Status management
    status = db.Column(db.String(20), default='open')  # open, closed, locked
    is_current = db.Column(db.Boolean, default=False)  # Only one can be current
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Multi-tenancy - TENANT-CENTRIC (company-wide fiscal years)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier
    
    # Relationships
    accounting_periods = db.relationship('AccountingPeriod', backref='fiscal_year', cascade='all, delete-orphan')
    
    # Unique constraint: year must be unique per tenant
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'year', name='uq_fiscal_year_tenant_year'),
        {'extend_existing': True},
    )
    
    def __repr__(self):
        return f'<FiscalYear {self.year}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'is_current': self.is_current,
            'periods_count': len(self.accounting_periods),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_current_fiscal_year(cls, tenant_id: str = None):
        """Get the current fiscal year - TENANT-CENTRIC"""
        if not tenant_id:
            return None
        query = cls.query.filter_by(is_current=True, tenant_id=tenant_id)
        return query.first()
    
    @classmethod
    def create_default_fiscal_year(cls, year: int, tenant_id: str = None):
        """Create a default fiscal year (Jan 1 - Dec 31) - TENANT-CENTRIC"""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Ensure only one current fiscal year per tenant
        cls.query.filter_by(tenant_id=tenant_id, is_current=True).update({'is_current': False})
        
        fiscal_year = cls(
            year=year,
            name=f'FY {year}',
            start_date=start_date,
            end_date=end_date,
            is_current=True,
            tenant_id=tenant_id
        )
        
        db.session.add(fiscal_year)
        db.session.flush()  # Get the ID
        
        # Create 12 monthly periods
        AccountingPeriod.create_monthly_periods(fiscal_year.id, tenant_id)
        
        return fiscal_year

class AccountingPeriod(db.Model):
    """
    Individual accounting periods within a fiscal year
    """
    __tablename__ = 'accounting_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    fiscal_year_id = db.Column(db.Integer, db.ForeignKey('fiscal_years.id'), nullable=False)
    
    # Period identification
    period_number = db.Column(db.Integer, nullable=False)  # 1-12 for monthly periods
    name = db.Column(db.String(50), nullable=False)  # e.g., "January 2024", "Q1 2024"
    short_name = db.Column(db.String(20), nullable=False)  # e.g., "Jan-24", "Q1-24"
    
    # Date range
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Status management
    status = db.Column(db.String(20), default='open')  # open, closed, locked
    is_current = db.Column(db.Boolean, default=False)  # Only one can be current
    
    # Locking mechanism
    is_locked = db.Column(db.Boolean, default=False)
    locked_at = db.Column(db.DateTime)
    locked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    lock_reason = db.Column(db.String(200))  # 'audit', 'manual_lock', 'year_end'
    
    # Grace period for adjustments
    grace_period_days = db.Column(db.Integer, default=0)  # Days after period end for adjustments
    allows_backdated_entries = db.Column(db.Boolean, default=True)
    max_backdate_days = db.Column(db.Integer, default=30)  # Maximum days to allow backdating
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Multi-tenancy - TENANT-CENTRIC (company-wide accounting periods)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier
    
    # Relationships
    journal_entries = db.relationship('JournalEntry', backref='accounting_period', lazy=True)
    
    def __repr__(self):
        return f'<AccountingPeriod {self.short_name}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fiscal_year_id': self.fiscal_year_id,
            'period_number': self.period_number,
            'name': self.name,
            'short_name': self.short_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'is_current': self.is_current,
            'is_locked': self.is_locked,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'allows_backdated_entries': self.allows_backdated_entries,
            'max_backdate_days': self.max_backdate_days,
            'grace_period_days': self.grace_period_days,
            'journal_entries_count': len(self.journal_entries) if self.journal_entries else 0
        }
    
    @classmethod
    def get_current_period(cls, tenant_id: str = None):
        """Get the current accounting period - TENANT-CENTRIC"""
        if not tenant_id:
            return None
        query = cls.query.filter_by(is_current=True, tenant_id=tenant_id)
        return query.first()
    
    @classmethod
    def get_period_for_date(cls, transaction_date: date, tenant_id: str = None):
        """Get the accounting period for a specific date - TENANT-CENTRIC"""
        if not tenant_id:
            return None
        query = cls.query.filter(
            and_(
                cls.start_date <= transaction_date,
                cls.end_date >= transaction_date,
                cls.tenant_id == tenant_id
            )
        )
        return query.first()
    
    @classmethod
    def create_monthly_periods(cls, fiscal_year_id: int, tenant_id: str = None):
        """Create 12 monthly periods for a fiscal year - TENANT-CENTRIC"""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        fiscal_year = FiscalYear.query.get(fiscal_year_id)
        if not fiscal_year:
            raise ValueError("Fiscal year not found")
        
        periods = []
        current_date = fiscal_year.start_date
        
        for month in range(1, 13):
            # Calculate month start and end
            if month == 1:
                month_start = fiscal_year.start_date
            else:
                month_start = current_date
            
            # Calculate month end
            if month == 12:
                month_end = fiscal_year.end_date
            else:
                # Get first day of next month, then subtract one day
                if month_start.month == 12:
                    next_month = month_start.replace(year=month_start.year + 1, month=1, day=1)
                else:
                    next_month = month_start.replace(month=month_start.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
            
            # Create period
            period = cls(
                fiscal_year_id=fiscal_year_id,
                period_number=month,
                name=f"{month_start.strftime('%B %Y')}",
                short_name=f"{month_start.strftime('%b-%y')}",
                start_date=month_start,
                end_date=month_end,
                is_current=(month == 1),  # First period is current
                tenant_id=tenant_id
            )
            
            db.session.add(period)
            periods.append(period)
            
            # Move to next month
            current_date = month_end + timedelta(days=1)
        
        return periods
    
    def can_accept_transaction(self, transaction_date: date) -> Tuple[bool, str]:
        """
        Check if this period can accept a transaction for the given date
        Returns (can_accept, reason)
        """
        # Check if period is locked
        if self.is_locked:
            return False, f"Period {self.short_name} is locked"
        
        # Check if transaction date is within period
        if not (self.start_date <= transaction_date <= self.end_date):
            return False, f"Transaction date {transaction_date} is outside period {self.short_name}"
        
        # Check backdating rules
        if not self.allows_backdated_entries:
            today = date.today()
            if transaction_date < today:
                return False, f"Backdated entries not allowed in period {self.short_name}"
        
        # Check grace period
        if self.grace_period_days > 0:
            grace_end = self.end_date + timedelta(days=self.grace_period_days)
            if date.today() > grace_end:
                return False, f"Grace period for {self.short_name} has expired"
        
        return True, "OK"
    
    def lock_period(self, user_id: int, reason: str = "Manual lock"):
        """Lock the accounting period"""
        self.is_locked = True
        self.locked_at = datetime.utcnow()
        self.locked_by = user_id
        self.lock_reason = reason
        self.status = 'locked'
        db.session.commit()
    
    def unlock_period(self, user_id: int):
        """Unlock the accounting period"""
        self.is_locked = False
        self.locked_at = None
        self.locked_by = None
        self.lock_reason = None
        self.status = 'open'
        db.session.commit()

class PeriodManager:
    """
    Manager class for accounting period operations
    """
    
    def __init__(self):
        self.current_period = None
        self.current_fiscal_year = None
    
    def initialize_default_periods(self, tenant_id: str = None):
        """Initialize default fiscal year and periods for a tenant - TENANT-CENTRIC"""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        current_year = datetime.now().year
        
        # Check if fiscal year already exists for this tenant
        existing_fy = FiscalYear.query.filter_by(year=current_year, tenant_id=tenant_id).first()
        if existing_fy:
            return existing_fy
        
        # Create default fiscal year with monthly periods
        fiscal_year = FiscalYear.create_default_fiscal_year(current_year, tenant_id)
        db.session.commit()
        
        return fiscal_year
    
    def get_current_period(self, tenant_id: str = None) -> Optional[AccountingPeriod]:
        """Get the current accounting period - TENANT-CENTRIC"""
        return AccountingPeriod.get_current_period(tenant_id)
    
    def get_period_for_date(self, transaction_date: date, tenant_id: str = None) -> Optional[AccountingPeriod]:
        """Get the accounting period for a specific date - TENANT-CENTRIC"""
        return AccountingPeriod.get_period_for_date(transaction_date, tenant_id)
    
    def validate_transaction_date(self, transaction_date: date, tenant_id: str = None) -> Tuple[bool, str, Optional[AccountingPeriod]]:
        """
        Validate if a transaction can be created for the given date - TENANT-CENTRIC
        Returns (is_valid, message, period)
        """
        if not tenant_id:
            return False, "Tenant context required", None
        
        period = self.get_period_for_date(transaction_date, tenant_id)
        if not period:
            return False, f"No accounting period found for date {transaction_date}", None
        
        can_accept, reason = period.can_accept_transaction(transaction_date)
        return can_accept, reason, period
    
    def close_period(self, period_id: int, tenant_id: str, reason: str = "Period closed"):
        """Close an accounting period - TENANT-CENTRIC"""
        period = AccountingPeriod.query.get(period_id)
        if not period:
            raise ValueError("Period not found")
        
        if period.tenant_id != tenant_id:
            raise ValueError("Unauthorized access to period")
        
        # Get user_id for lock operation (audit trail)
        from modules.core.tenant_helpers import get_current_user_id
        user_id_int = get_current_user_id()
        
        period.lock_period(user_id_int, reason)
        
        # Move to next period if this was current
        if period.is_current:
            next_period = AccountingPeriod.query.filter(
                and_(
                    AccountingPeriod.fiscal_year_id == period.fiscal_year_id,
                    AccountingPeriod.period_number == period.period_number + 1,
                    AccountingPeriod.tenant_id == tenant_id
                )
            ).first()
            
            if next_period:
                next_period.is_current = True
                period.is_current = False
                db.session.commit()
        
        return period
    
    def get_period_summary(self, tenant_id: str = None) -> Dict:
        """Get a summary of all periods for a tenant - TENANT-CENTRIC"""
        if not tenant_id:
            return {
                'total_periods': 0,
                'open_periods': 0,
                'closed_periods': 0,
                'locked_periods': 0,
                'current_period': None,
                'periods': []
            }
        
        periods = AccountingPeriod.query.filter_by(tenant_id=tenant_id).order_by(
            AccountingPeriod.fiscal_year_id, AccountingPeriod.period_number
        ).all()
        
        summary = {
            'total_periods': len(periods),
            'open_periods': len([p for p in periods if p.status == 'open']),
            'closed_periods': len([p for p in periods if p.status == 'closed']),
            'locked_periods': len([p for p in periods if p.is_locked]),
            'current_period': None,
            'periods': [p.to_dict() for p in periods]
        }
        
        current = self.get_current_period(tenant_id)
        if current:
            summary['current_period'] = current.to_dict()
        
        return summary

# Global period manager instance
period_manager = PeriodManager()

