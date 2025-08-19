from app import db
from datetime import datetime
# Use db.JSON for SQLite compatibility

class RegulatoryFramework(db.Model):
    """Global regulatory frameworks and compliance rules"""
    __tablename__ = 'regulatory_frameworks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    framework_type = db.Column(db.String(100), nullable=False)  # tax, labor, financial, environmental
    version = db.Column(db.String(50), default='1.0')
    effective_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    rules = db.Column(db.JSON)  # Store compliance rules as JSON
    requirements = db.Column(db.JSON)  # Store requirements as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LegalEntity(db.Model):
    """Legal entities for multi-entity consolidation"""
    __tablename__ = 'legal_entities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    legal_name = db.Column(db.String(200))
    entity_type = db.Column(db.String(100), nullable=False)  # corporation, llc, partnership, subsidiary
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    tax_id = db.Column(db.String(100))
    registration_number = db.Column(db.String(100))
    parent_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'))
    ownership_percentage = db.Column(db.Float, default=100.0)
    functional_currency = db.Column(db.String(10), default='USD')
    reporting_currency = db.Column(db.String(10), default='USD')
    fiscal_year_start = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    address = db.Column(db.JSON)
    contact_info = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parent_entity = db.relationship('LegalEntity', remote_side=[id], backref='subsidiaries')
    financial_statements = db.relationship('FinancialStatement', backref='legal_entity', lazy=True)
    consolidation_entries = db.relationship('ConsolidationEntry', backref='legal_entity', lazy=True)

class FinancialStatement(db.Model):
    """Financial statements for legal entities"""
    __tablename__ = 'financial_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'), nullable=False)
    statement_type = db.Column(db.String(50), nullable=False)  # balance_sheet, income_statement, cash_flow
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(50), default='draft')  # draft, reviewed, approved, filed
    version = db.Column(db.String(50), default='1.0')
    data = db.Column(db.JSON)  # Store financial data as JSON
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConsolidationEntry(db.Model):
    """Consolidation entries for multi-entity financials"""
    __tablename__ = 'consolidation_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    consolidation_period_id = db.Column(db.Integer, db.ForeignKey('consolidation_periods.id'), nullable=False)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'), nullable=False)
    entry_type = db.Column(db.String(50), nullable=False)  # elimination, adjustment, translation
    account_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    debit_amount = db.Column(db.Float, default=0.0)
    credit_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    consolidation_period = db.relationship('ConsolidationPeriod', backref='entries', lazy=True)

class ConsolidationPeriod(db.Model):
    """Consolidation periods for multi-entity reporting"""
    __tablename__ = 'consolidation_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    reporting_currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(50), default='open')  # open, in_progress, completed, locked
    consolidation_method = db.Column(db.String(50), default='full')  # full, equity, proportional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class StatutoryReport(db.Model):
    """Statutory reports for regulatory compliance"""
    __tablename__ = 'statutory_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'), nullable=False)
    regulatory_framework_id = db.Column(db.Integer, db.ForeignKey('regulatory_frameworks.id'), nullable=False)
    report_type = db.Column(db.String(100), nullable=False)  # tax_return, annual_report, vat_return
    reporting_period = db.Column(db.String(50), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    filing_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending')  # pending, prepared, filed, accepted, rejected
    report_data = db.Column(db.JSON)  # Store report data as JSON
    attachments = db.Column(db.JSON)  # Store file attachments
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    legal_entity = db.relationship('LegalEntity', foreign_keys=[legal_entity_id])
    regulatory_framework = db.relationship('RegulatoryFramework', foreign_keys=[regulatory_framework_id])

class ComplianceRule(db.Model):
    """Individual compliance rules"""
    __tablename__ = 'compliance_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    regulatory_framework_id = db.Column(db.Integer, db.ForeignKey('regulatory_frameworks.id'), nullable=False)
    rule_code = db.Column(db.String(100), nullable=False)
    rule_name = db.Column(db.String(200), nullable=False)
    rule_description = db.Column(db.Text)
    rule_type = db.Column(db.String(50), nullable=False)  # validation, calculation, reporting
    rule_logic = db.Column(db.JSON)  # Store rule logic as JSON
    parameters = db.Column(db.JSON)  # Store rule parameters
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    regulatory_framework = db.relationship('RegulatoryFramework', backref='compliance_rules', lazy=True)

class ComplianceCheck(db.Model):
    """Compliance check results"""
    __tablename__ = 'compliance_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'), nullable=False)
    compliance_rule_id = db.Column(db.Integer, db.ForeignKey('compliance_rules.id'), nullable=False)
    check_date = db.Column(db.DateTime, nullable=False)
    check_period = db.Column(db.String(50))
    status = db.Column(db.String(50), default='pending')  # pending, passed, failed, warning
    result_data = db.Column(db.JSON)  # Store check results
    error_message = db.Column(db.Text)
    corrected = db.Column(db.Boolean, default=False)
    corrected_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    legal_entity = db.relationship('LegalEntity', foreign_keys=[legal_entity_id])
    compliance_rule = db.relationship('ComplianceRule', foreign_keys=[compliance_rule_id])

class TaxCalculation(db.Model):
    """Tax calculations for different jurisdictions"""
    __tablename__ = 'tax_calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'), nullable=False)
    tax_type = db.Column(db.String(100), nullable=False)  # corporate_income_tax, vat, payroll_tax
    calculation_period = db.Column(db.String(50), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    taxable_amount = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    calculated_tax = db.Column(db.Float, default=0.0)
    adjustments = db.Column(db.Float, default=0.0)
    final_tax_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    calculation_data = db.Column(db.JSON)  # Store calculation details
    status = db.Column(db.String(50), default='calculated')  # calculated, reviewed, approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    legal_entity = db.relationship('LegalEntity', foreign_keys=[legal_entity_id])

class AuditTrail(db.Model):
    """Audit trail for compliance activities"""
    __tablename__ = 'audit_trails'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(100))
    record_id = db.Column(db.Integer)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    legal_entity = db.relationship('LegalEntity', foreign_keys=[legal_entity_id])
    user = db.relationship('User', foreign_keys=[user_id])

# User model is defined in core.models
