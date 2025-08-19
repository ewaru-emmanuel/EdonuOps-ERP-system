from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.tax.models import TaxRule, TaxAssignment, TaxTransaction, TaxPeriod

bp = Blueprint('tax', __name__, url_prefix='/api/tax')

# Sample data (replace with database queries)
tax_rules = []
tax_assignments = []
tax_transactions = []
tax_periods = []

# Tax Rule endpoints
@bp.route('/rules', methods=['GET'])
def get_tax_rules():
    """Get all tax rules"""
    return jsonify(tax_rules)

@bp.route('/rules', methods=['POST'])
def create_tax_rule():
    """Create a new tax rule"""
    data = request.get_json()
    new_rule = {
        "id": len(tax_rules) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "tax_rate": data.get('tax_rate'),
        "tax_account_id": data.get('tax_account_id'),
        "is_active": data.get('is_active', True),
        "applies_to": data.get('applies_to', 'all'),
        "created_at": datetime.utcnow().isoformat()
    }
    tax_rules.append(new_rule)
    return jsonify(new_rule), 201

@bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_tax_rule(rule_id):
    """Update a tax rule"""
    data = request.get_json()
    rule = next((r for r in tax_rules if r['id'] == rule_id), None)
    if rule:
        rule.update(data)
        rule['updated_at'] = datetime.utcnow().isoformat()
        return jsonify(rule)
    return jsonify({"error": "Tax rule not found"}), 404

# Tax Assignment endpoints
@bp.route('/assignments', methods=['GET'])
def get_tax_assignments():
    """Get all tax assignments with filters"""
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id', type=int)
    
    filtered_assignments = tax_assignments
    if entity_type:
        filtered_assignments = [a for a in filtered_assignments if a.get('entity_type') == entity_type]
    if entity_id:
        filtered_assignments = [a for a in filtered_assignments if a.get('entity_id') == entity_id]
    
    return jsonify(filtered_assignments)

@bp.route('/assignments', methods=['POST'])
def create_tax_assignment():
    """Create a new tax assignment"""
    data = request.get_json()
    new_assignment = {
        "id": len(tax_assignments) + 1,
        "tax_rule_id": data.get('tax_rule_id'),
        "entity_type": data.get('entity_type'),
        "entity_id": data.get('entity_id'),
        "priority": data.get('priority', 1),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    tax_assignments.append(new_assignment)
    return jsonify(new_assignment), 201

# Tax Calculation endpoint
@bp.route('/calculate', methods=['POST'])
def calculate_tax():
    """Calculate tax for a given amount and entity"""
    data = request.get_json()
    amount = data.get('amount', 0)
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    
    # Find applicable tax rule
    applicable_rule = None
    highest_priority = 0
    
    for assignment in tax_assignments:
        if (assignment.get('entity_type') == entity_type and 
            assignment.get('entity_id') == entity_id and 
            assignment.get('is_active', True) and
            assignment.get('priority', 0) > highest_priority):
            
            rule = next((r for r in tax_rules if r['id'] == assignment['tax_rule_id']), None)
            if rule and rule.get('is_active', True):
                applicable_rule = rule
                highest_priority = assignment.get('priority', 0)
    
    # If no specific assignment, find general rule
    if not applicable_rule:
        for rule in tax_rules:
            if rule.get('applies_to') == 'all' and rule.get('is_active', True):
                applicable_rule = rule
                break
    
    if applicable_rule:
        tax_rate = applicable_rule.get('tax_rate', 0)
        tax_amount = amount * (tax_rate / 100)
        
        return jsonify({
            "taxable_amount": amount,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "total_amount": amount + tax_amount,
            "tax_rule": applicable_rule
        })
    
    return jsonify({
        "taxable_amount": amount,
        "tax_rate": 0,
        "tax_amount": 0,
        "total_amount": amount,
        "tax_rule": None
    })

# Tax Transaction endpoints
@bp.route('/transactions', methods=['GET'])
def get_tax_transactions():
    """Get tax transactions with filters"""
    period_month = request.args.get('period_month', type=int)
    period_year = request.args.get('period_year', type=int)
    document_type = request.args.get('document_type')
    
    filtered_transactions = tax_transactions
    if period_month:
        filtered_transactions = [t for t in filtered_transactions if t.get('period_month') == period_month]
    if period_year:
        filtered_transactions = [t for t in filtered_transactions if t.get('period_year') == period_year]
    if document_type:
        filtered_transactions = [t for t in filtered_transactions if t.get('document_type') == document_type]
    
    return jsonify(filtered_transactions)

@bp.route('/transactions', methods=['POST'])
def create_tax_transaction():
    """Create a new tax transaction"""
    data = request.get_json()
    new_transaction = {
        "id": len(tax_transactions) + 1,
        "tax_rule_id": data.get('tax_rule_id'),
        "document_type": data.get('document_type'),
        "document_id": data.get('document_id'),
        "taxable_amount": data.get('taxable_amount'),
        "tax_amount": data.get('tax_amount'),
        "tax_rate": data.get('tax_rate'),
        "transaction_date": data.get('transaction_date', datetime.utcnow().date().isoformat()),
        "period_month": data.get('period_month', datetime.utcnow().month),
        "period_year": data.get('period_year', datetime.utcnow().year),
        "is_paid": data.get('is_paid', False),
        "created_at": datetime.utcnow().isoformat()
    }
    tax_transactions.append(new_transaction)
    return jsonify(new_transaction), 201

# Tax Period endpoints
@bp.route('/periods', methods=['GET'])
def get_tax_periods():
    """Get tax periods with filters"""
    period_month = request.args.get('period_month', type=int)
    period_year = request.args.get('period_year', type=int)
    tax_type = request.args.get('tax_type')
    
    filtered_periods = tax_periods
    if period_month:
        filtered_periods = [p for p in filtered_periods if p.get('period_month') == period_month]
    if period_year:
        filtered_periods = [p for p in filtered_periods if p.get('period_year') == period_year]
    if tax_type:
        filtered_periods = [p for p in filtered_periods if p.get('tax_type') == tax_type]
    
    return jsonify(filtered_periods)

@bp.route('/periods', methods=['POST'])
def create_tax_period():
    """Create a new tax period"""
    data = request.get_json()
    new_period = {
        "id": len(tax_periods) + 1,
        "period_month": data.get('period_month'),
        "period_year": data.get('period_year'),
        "tax_type": data.get('tax_type'),
        "total_taxable_amount": data.get('total_taxable_amount', 0.0),
        "total_tax_amount": data.get('total_tax_amount', 0.0),
        "status": data.get('status', 'open'),
        "created_at": datetime.utcnow().isoformat()
    }
    tax_periods.append(new_period)
    return jsonify(new_period), 201

# Tax Summary endpoint
@bp.route('/summary', methods=['GET'])
def get_tax_summary():
    """Get tax summary for a period"""
    period_month = request.args.get('period_month', type=int)
    period_year = request.args.get('period_year', type=int)
    
    if not period_month or not period_year:
        return jsonify({"error": "Period month and year are required"}), 400
    
    # Calculate summary from transactions
    period_transactions = [t for t in tax_transactions 
                          if t.get('period_month') == period_month and 
                          t.get('period_year') == period_year]
    
    total_taxable = sum(t.get('taxable_amount', 0) for t in period_transactions)
    total_tax = sum(t.get('tax_amount', 0) for t in period_transactions)
    
    return jsonify({
        "period_month": period_month,
        "period_year": period_year,
        "total_transactions": len(period_transactions),
        "total_taxable_amount": total_taxable,
        "total_tax_amount": total_tax,
        "transactions": period_transactions
    })
