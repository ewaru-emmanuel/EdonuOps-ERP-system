from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from modules.compliance.models import (
    RegulatoryFramework, LegalEntity, FinancialStatement, ConsolidationEntry,
    ConsolidationPeriod, StatutoryReport, ComplianceRule, ComplianceCheck,
    TaxCalculation, AuditTrail
)
import uuid

bp = Blueprint('compliance', __name__, url_prefix='/api/compliance')

# Sample data for initial state
regulatory_frameworks = []
legal_entities = []
financial_statements = []
consolidation_entries = []
consolidation_periods = []
statutory_reports = []
compliance_rules = []
compliance_checks = []
tax_calculations = []
audit_trails = []

# Regulatory Framework endpoints
@bp.route('/frameworks', methods=['GET'])
def get_regulatory_frameworks():
    """Get all regulatory frameworks"""
    country = request.args.get('country')
    framework_type = request.args.get('framework_type')
    
    filtered_frameworks = regulatory_frameworks
    if country:
        filtered_frameworks = [f for f in filtered_frameworks if f.get('country') == country]
    if framework_type:
        filtered_frameworks = [f for f in filtered_frameworks if f.get('framework_type') == framework_type]
    
    return jsonify(filtered_frameworks)

@bp.route('/frameworks', methods=['POST'])
def create_regulatory_framework():
    """Create a new regulatory framework"""
    data = request.get_json()
    
    new_framework = {
        "id": len(regulatory_frameworks) + 1,
        "name": data.get('name'),
        "country": data.get('country'),
        "region": data.get('region'),
        "framework_type": data.get('framework_type'),
        "version": data.get('version', '1.0'),
        "effective_date": data.get('effective_date'),
        "expiry_date": data.get('expiry_date'),
        "is_active": data.get('is_active', True),
        "rules": data.get('rules', {}),
        "requirements": data.get('requirements', {}),
        "created_at": datetime.utcnow().isoformat()
    }
    
    regulatory_frameworks.append(new_framework)
    return jsonify(new_framework), 201

# Legal Entity endpoints
@bp.route('/entities', methods=['GET'])
def get_legal_entities():
    """Get all legal entities"""
    country = request.args.get('country')
    entity_type = request.args.get('entity_type')
    
    filtered_entities = legal_entities
    if country:
        filtered_entities = [e for e in legal_entities if e.get('country') == country]
    if entity_type:
        filtered_entities = [e for e in legal_entities if e.get('entity_type') == entity_type]
    
    return jsonify(filtered_entities)

@bp.route('/entities', methods=['POST'])
def create_legal_entity():
    """Create a new legal entity"""
    data = request.get_json()
    
    new_entity = {
        "id": len(legal_entities) + 1,
        "name": data.get('name'),
        "legal_name": data.get('legal_name'),
        "entity_type": data.get('entity_type'),
        "country": data.get('country'),
        "region": data.get('region'),
        "tax_id": data.get('tax_id'),
        "registration_number": data.get('registration_number'),
        "parent_entity_id": data.get('parent_entity_id'),
        "ownership_percentage": data.get('ownership_percentage', 100.0),
        "functional_currency": data.get('functional_currency', 'USD'),
        "reporting_currency": data.get('reporting_currency', 'USD'),
        "fiscal_year_start": data.get('fiscal_year_start'),
        "is_active": data.get('is_active', True),
        "address": data.get('address', {}),
        "contact_info": data.get('contact_info', {}),
        "created_at": datetime.utcnow().isoformat()
    }
    
    legal_entities.append(new_entity)
    return jsonify(new_entity), 201

# Financial Statement endpoints
@bp.route('/financial-statements', methods=['GET'])
def get_financial_statements():
    """Get financial statements"""
    entity_id = request.args.get('entity_id', type=int)
    statement_type = request.args.get('statement_type')
    
    filtered_statements = financial_statements
    if entity_id:
        filtered_statements = [s for s in financial_statements if s.get('legal_entity_id') == entity_id]
    if statement_type:
        filtered_statements = [s for s in financial_statements if s.get('statement_type') == statement_type]
    
    return jsonify(filtered_statements)

@bp.route('/financial-statements', methods=['POST'])
def create_financial_statement():
    """Create a new financial statement"""
    data = request.get_json()
    
    new_statement = {
        "id": len(financial_statements) + 1,
        "legal_entity_id": data.get('legal_entity_id'),
        "statement_type": data.get('statement_type'),
        "period_start": data.get('period_start'),
        "period_end": data.get('period_end'),
        "currency": data.get('currency', 'USD'),
        "status": data.get('status', 'draft'),
        "version": data.get('version', '1.0'),
        "data": data.get('data', {}),
        "notes": data.get('notes'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    financial_statements.append(new_statement)
    return jsonify(new_statement), 201

# Consolidation endpoints
@bp.route('/consolidation/periods', methods=['GET'])
def get_consolidation_periods():
    """Get consolidation periods"""
    return jsonify(consolidation_periods)

@bp.route('/consolidation/periods', methods=['POST'])
def create_consolidation_period():
    """Create a new consolidation period"""
    data = request.get_json()
    
    new_period = {
        "id": len(consolidation_periods) + 1,
        "name": data.get('name'),
        "period_start": data.get('period_start'),
        "period_end": data.get('period_end'),
        "reporting_currency": data.get('reporting_currency', 'USD'),
        "status": data.get('status', 'open'),
        "consolidation_method": data.get('consolidation_method', 'full'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    consolidation_periods.append(new_period)
    return jsonify(new_period), 201

@bp.route('/consolidation/calculate', methods=['POST'])
def calculate_consolidation():
    """Calculate consolidation for a period"""
    data = request.get_json()
    period_id = data.get('period_id')
    
    # Mock consolidation calculation
    consolidation_result = {
        "period_id": period_id,
        "total_assets": 10000000.0,
        "total_liabilities": 6000000.0,
        "total_equity": 4000000.0,
        "consolidation_entries": [
            {
                "entry_type": "elimination",
                "account_code": "1000",
                "description": "Intercompany elimination",
                "debit_amount": 500000.0,
                "credit_amount": 0.0
            }
        ],
        "calculated_at": datetime.utcnow().isoformat()
    }
    
    return jsonify(consolidation_result)

# Statutory Report endpoints
@bp.route('/statutory-reports', methods=['GET'])
def get_statutory_reports():
    """Get statutory reports"""
    entity_id = request.args.get('entity_id', type=int)
    report_type = request.args.get('report_type')
    status = request.args.get('status')
    
    filtered_reports = statutory_reports
    if entity_id:
        filtered_reports = [r for r in statutory_reports if r.get('legal_entity_id') == entity_id]
    if report_type:
        filtered_reports = [r for r in statutory_reports if r.get('report_type') == report_type]
    if status:
        filtered_reports = [r for r in statutory_reports if r.get('status') == status]
    
    return jsonify(filtered_reports)

@bp.route('/statutory-reports', methods=['POST'])
def create_statutory_report():
    """Create a new statutory report"""
    data = request.get_json()
    
    new_report = {
        "id": len(statutory_reports) + 1,
        "legal_entity_id": data.get('legal_entity_id'),
        "regulatory_framework_id": data.get('regulatory_framework_id'),
        "report_type": data.get('report_type'),
        "reporting_period": data.get('reporting_period'),
        "period_start": data.get('period_start'),
        "period_end": data.get('period_end'),
        "due_date": data.get('due_date'),
        "filing_date": data.get('filing_date'),
        "status": data.get('status', 'pending'),
        "report_data": data.get('report_data', {}),
        "attachments": data.get('attachments', {}),
        "notes": data.get('notes'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    statutory_reports.append(new_report)
    return jsonify(new_report), 201

# Compliance Rule endpoints
@bp.route('/rules', methods=['GET'])
def get_compliance_rules():
    """Get compliance rules"""
    framework_id = request.args.get('framework_id', type=int)
    rule_type = request.args.get('rule_type')
    
    filtered_rules = compliance_rules
    if framework_id:
        filtered_rules = [r for r in compliance_rules if r.get('regulatory_framework_id') == framework_id]
    if rule_type:
        filtered_rules = [r for r in compliance_rules if r.get('rule_type') == rule_type]
    
    return jsonify(filtered_rules)

@bp.route('/rules', methods=['POST'])
def create_compliance_rule():
    """Create a new compliance rule"""
    data = request.get_json()
    
    new_rule = {
        "id": len(compliance_rules) + 1,
        "regulatory_framework_id": data.get('regulatory_framework_id'),
        "rule_code": data.get('rule_code'),
        "rule_name": data.get('rule_name'),
        "rule_description": data.get('rule_description'),
        "rule_type": data.get('rule_type'),
        "rule_logic": data.get('rule_logic', {}),
        "parameters": data.get('parameters', {}),
        "is_active": data.get('is_active', True),
        "priority": data.get('priority', 1),
        "created_at": datetime.utcnow().isoformat()
    }
    
    compliance_rules.append(new_rule)
    return jsonify(new_rule), 201

# Compliance Check endpoints
@bp.route('/checks', methods=['GET'])
def get_compliance_checks():
    """Get compliance checks"""
    entity_id = request.args.get('entity_id', type=int)
    status = request.args.get('status')
    
    filtered_checks = compliance_checks
    if entity_id:
        filtered_checks = [c for c in compliance_checks if c.get('legal_entity_id') == entity_id]
    if status:
        filtered_checks = [c for c in compliance_checks if c.get('status') == status]
    
    return jsonify(filtered_checks)

@bp.route('/checks/run', methods=['POST'])
def run_compliance_checks():
    """Run compliance checks for an entity"""
    data = request.get_json()
    entity_id = data.get('entity_id')
    
    # Mock compliance check results
    check_results = [
        {
            "id": len(compliance_checks) + 1,
            "legal_entity_id": entity_id,
            "compliance_rule_id": 1,
            "check_date": datetime.utcnow().isoformat(),
            "check_period": "Q1 2024",
            "status": "passed",
            "result_data": {"details": "All compliance requirements met"},
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    compliance_checks.extend(check_results)
    return jsonify(check_results)

# Tax Calculation endpoints
@bp.route('/tax-calculations', methods=['GET'])
def get_tax_calculations():
    """Get tax calculations"""
    entity_id = request.args.get('entity_id', type=int)
    tax_type = request.args.get('tax_type')
    
    filtered_calculations = tax_calculations
    if entity_id:
        filtered_calculations = [t for t in tax_calculations if t.get('legal_entity_id') == entity_id]
    if tax_type:
        filtered_calculations = [t for t in tax_calculations if t.get('tax_type') == tax_type]
    
    return jsonify(filtered_calculations)

@bp.route('/tax-calculations', methods=['POST'])
def create_tax_calculation():
    """Create a new tax calculation"""
    data = request.get_json()
    
    new_calculation = {
        "id": len(tax_calculations) + 1,
        "legal_entity_id": data.get('legal_entity_id'),
        "tax_type": data.get('tax_type'),
        "calculation_period": data.get('calculation_period'),
        "period_start": data.get('period_start'),
        "period_end": data.get('period_end'),
        "taxable_amount": data.get('taxable_amount', 0.0),
        "tax_rate": data.get('tax_rate', 0.0),
        "calculated_tax": data.get('calculated_tax', 0.0),
        "adjustments": data.get('adjustments', 0.0),
        "final_tax_amount": data.get('final_tax_amount', 0.0),
        "currency": data.get('currency', 'USD'),
        "calculation_data": data.get('calculation_data', {}),
        "status": data.get('status', 'calculated'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    tax_calculations.append(new_calculation)
    return jsonify(new_calculation), 201

# Analytics and Reporting endpoints
@bp.route('/analytics/compliance-summary', methods=['GET'])
def get_compliance_summary():
    """Get compliance summary analytics"""
    summary = {
        "total_entities": len(legal_entities),
        "active_frameworks": len([f for f in regulatory_frameworks if f.get('is_active')]),
        "pending_reports": len([r for r in statutory_reports if r.get('status') == 'pending']),
        "overdue_reports": len([r for r in statutory_reports if r.get('status') == 'overdue']),
        "compliance_rate": 95.5,  # Mock calculation
        "total_tax_liability": sum([t.get('final_tax_amount', 0) for t in tax_calculations]),
        "consolidation_periods": len(consolidation_periods)
    }
    
    return jsonify(summary)

@bp.route('/analytics/global-overview', methods=['GET'])
def get_global_compliance_overview():
    """Get global compliance overview"""
    overview = {
        "countries_covered": len(set([e.get('country') for e in legal_entities])),
        "regulatory_frameworks": len(regulatory_frameworks),
        "compliance_rules": len(compliance_rules),
        "statutory_reports": len(statutory_reports),
        "tax_calculations": len(tax_calculations),
        "consolidation_entries": len(consolidation_entries),
        "audit_trails": len(audit_trails)
    }
    
    return jsonify(overview)

# Initialize sample data
def init_sample_data():
    """Initialize sample compliance data"""
    global regulatory_frameworks, legal_entities, statutory_reports
    
    # Sample regulatory frameworks
    regulatory_frameworks.extend([
        {
            "id": 1,
            "name": "US GAAP",
            "country": "United States",
            "region": "North America",
            "framework_type": "financial",
            "version": "2024",
            "effective_date": "2024-01-01",
            "is_active": True,
            "rules": {"revenue_recognition": "ASC 606", "leases": "ASC 842"},
            "requirements": {"quarterly_filing": True, "annual_audit": True},
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "name": "IFRS",
            "country": "International",
            "region": "Global",
            "framework_type": "financial",
            "version": "2024",
            "effective_date": "2024-01-01",
            "is_active": True,
            "rules": {"revenue": "IFRS 15", "leases": "IFRS 16"},
            "requirements": {"annual_filing": True, "interim_reports": True},
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample legal entities
    legal_entities.extend([
        {
            "id": 1,
            "name": "EdonuOps US Inc",
            "legal_name": "EdonuOps US Incorporated",
            "entity_type": "corporation",
            "country": "United States",
            "region": "North America",
            "tax_id": "12-3456789",
            "registration_number": "DE123456",
            "functional_currency": "USD",
            "reporting_currency": "USD",
            "is_active": True,
            "address": {"street": "123 Business Ave", "city": "New York", "state": "NY", "zip": "10001"},
            "contact_info": {"phone": "+1-555-0123", "email": "us@edonuops.com"},
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "name": "EdonuOps UK Ltd",
            "legal_name": "EdonuOps UK Limited",
            "entity_type": "corporation",
            "country": "United Kingdom",
            "region": "Europe",
            "tax_id": "GB123456789",
            "registration_number": "12345678",
            "functional_currency": "GBP",
            "reporting_currency": "USD",
            "is_active": True,
            "address": {"street": "456 Business St", "city": "London", "postcode": "SW1A 1AA"},
            "contact_info": {"phone": "+44-20-1234-5678", "email": "uk@edonuops.com"},
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample statutory reports
    statutory_reports.extend([
        {
            "id": 1,
            "legal_entity_id": 1,
            "regulatory_framework_id": 1,
            "report_type": "annual_report",
            "reporting_period": "2024",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "due_date": "2025-03-15",
            "status": "pending",
            "report_data": {"total_assets": 10000000, "total_revenue": 5000000},
            "created_at": datetime.utcnow().isoformat()
        }
    ])

# Initialize sample data when module loads
init_sample_data()
