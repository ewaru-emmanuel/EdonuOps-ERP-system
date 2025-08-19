from app import db
from datetime import datetime
from sqlalchemy import func, JSON, Text
import os

# Use JSON for SQLite compatibility, JSONB for PostgreSQL
def get_json_type():
    """Return appropriate JSON type based on database"""
    db_url = os.environ.get("DATABASE_URL", "sqlite:///edonuops.db")
    if "postgresql" in db_url.lower():
        try:
            from sqlalchemy.dialects.postgresql import JSONB
            return JSONB
        except ImportError:
            return JSON
    else:
        # For SQLite, use JSON type
        return JSON

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # asset, liability, equity, revenue, expense
    balance = db.Column(db.Numeric(15, 2), default=0.0)
    currency = db.Column(db.String(3), default='USD')
    parent_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = db.relationship('Account', remote_side=[id], backref='children')

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM format
    doc_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, posted, cancelled
    currency = db.Column(db.String(3), default='USD')
    total_debit = db.Column(db.Numeric(15, 2), default=0.0)
    total_credit = db.Column(db.Numeric(15, 2), default=0.0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lines = db.relationship('JournalLine', backref='journal_entry', cascade='all, delete-orphan')

class JournalLine(db.Model):
    __tablename__ = 'journal_lines'
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    description = db.Column(db.String(200))
    debit_amount = db.Column(db.Numeric(15, 2), default=0.0)
    credit_amount = db.Column(db.Numeric(15, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    account = db.relationship('Account')

# Indexes
db.Index('ix_journal_lines_account_id', JournalLine.account_id)
db.Index('ix_journal_lines_journal_entry_id', JournalLine.journal_entry_id)
db.Index('ix_accounts_code', Account.code)