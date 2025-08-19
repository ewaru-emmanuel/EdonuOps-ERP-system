from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class TaxRule(db.Model):
    __tablename__ = 'tax_rules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    tax_rate = db.Column(db.Float, nullable=False)  # Percentage (e.g., 20.0 for 20%)
    tax_account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    applies_to = db.Column(db.String(20), default='all')  # all, products, services, shipping
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tax_account = db.relationship('ChartOfAccount', backref='tax_rules')

class TaxAssignment(db.Model):
    __tablename__ = 'tax_assignments'
    id = db.Column(db.Integer, primary_key=True)
    tax_rule_id = db.Column(db.Integer, db.ForeignKey('tax_rules.id'), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # product, vendor, customer, category
    entity_id = db.Column(db.Integer, nullable=False)  # ID of the entity
    priority = db.Column(db.Integer, default=1)  # Higher priority rules take precedence
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tax_rule = db.relationship('TaxRule', backref='assignments')

class TaxTransaction(db.Model):
    __tablename__ = 'tax_transactions'
    id = db.Column(db.Integer, primary_key=True)
    tax_rule_id = db.Column(db.Integer, db.ForeignKey('tax_rules.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # invoice, bill, po
    document_id = db.Column(db.Integer, nullable=False)
    taxable_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    period_month = db.Column(db.Integer, nullable=False)  # 1-12
    period_year = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tax_rule = db.relationship('TaxRule', backref='transactions')

class TaxPeriod(db.Model):
    __tablename__ = 'tax_periods'
    id = db.Column(db.Integer, primary_key=True)
    period_month = db.Column(db.Integer, nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    tax_type = db.Column(db.String(50), nullable=False)  # VAT, GST, etc.
    total_taxable_amount = db.Column(db.Float, default=0.0)
    total_tax_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='open')  # open, closed, filed
    filing_date = db.Column(db.Date)
    filing_reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('period_month', 'period_year', 'tax_type'),)
