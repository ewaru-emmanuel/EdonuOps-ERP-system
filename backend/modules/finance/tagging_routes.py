"""
API routes for tagging system
"""

from flask import Blueprint, jsonify, request
from app import db
from .tagging_system import get_tagging_system
from .models import Account, JournalEntry, JournalLine
import logging

tagging_bp = Blueprint('tagging', __name__)

@tagging_bp.route('/categories', methods=['GET'])
def get_tag_categories():
    """Get all available tag categories"""
    try:
        tagging_system = get_tagging_system()
        categories = tagging_system.get_tag_categories()
        
        return jsonify({
            'categories': categories,
            'total_categories': len(categories)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching tag categories: {e}")
        return jsonify({'error': 'Failed to fetch tag categories'}), 500

@tagging_bp.route('/rules/account/<account_code>', methods=['GET'])
def get_account_tagging_rules(account_code):
    """Get tagging rules for a specific account"""
    try:
        tagging_system = get_tagging_system()
        rules = tagging_system.get_account_tagging_rules(account_code)
        
        if not rules:
            return jsonify({'error': 'Account not found'}), 404
        
        return jsonify(rules), 200
        
    except Exception as e:
        logging.error(f"Error fetching tagging rules for account {account_code}: {e}")
        return jsonify({'error': 'Failed to fetch tagging rules'}), 500

@tagging_bp.route('/validate', methods=['POST'])
def validate_transaction_tags():
    """Validate tags for a transaction"""
    try:
        data = request.json
        account_code = data.get('account_code')
        tags = data.get('tags', {})
        
        if not account_code:
            return jsonify({'error': 'Account code is required'}), 400
        
        tagging_system = get_tagging_system()
        is_valid, errors = tagging_system.validate_transaction_tags(account_code, tags)
        
        return jsonify({
            'is_valid': is_valid,
            'errors': errors,
            'account_code': account_code,
            'tags': tags
        }), 200
        
    except Exception as e:
        logging.error(f"Error validating transaction tags: {e}")
        return jsonify({'error': 'Failed to validate tags'}), 500

@tagging_bp.route('/distinction', methods=['GET'])
def get_ledger_vs_tag_distinction():
    """Get clear distinction between ledger accounts and tags"""
    try:
        tagging_system = get_tagging_system()
        distinction = tagging_system.get_ledger_vs_tag_distinction()
        
        return jsonify(distinction), 200
        
    except Exception as e:
        logging.error(f"Error fetching ledger vs tag distinction: {e}")
        return jsonify({'error': 'Failed to fetch distinction'}), 500

@tagging_bp.route('/accounts/with-tags', methods=['GET'])
def get_accounts_with_tagging_info():
    """Get all accounts with their tagging requirements"""
    try:
        tagging_system = get_tagging_system()
        accounts = Account.query.all()
        
        accounts_with_tags = []
        for account in accounts:
            rules = tagging_system.get_account_tagging_rules(account.code)
            if rules:
                accounts_with_tags.append({
                    'id': account.id,
                    'code': account.code,
                    'name': account.name,
                    'type': account.type,
                    'is_active': account.is_active,
                    'required_tags': rules['required_tags'],
                    'optional_tags': rules['optional_tags'],
                    'total_required': rules['total_required'],
                    'total_optional': rules['total_optional']
                })
        
        return jsonify({
            'accounts': accounts_with_tags,
            'total_accounts': len(accounts_with_tags)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching accounts with tagging info: {e}")
        return jsonify({'error': 'Failed to fetch accounts with tagging info'}), 500

@tagging_bp.route('/suggestions', methods=['POST'])
def get_tag_suggestions():
    """Get tag suggestions based on account and previous transactions"""
    try:
        data = request.json
        account_code = data.get('account_code')
        partial_tags = data.get('partial_tags', {})
        
        if not account_code:
            return jsonify({'error': 'Account code is required'}), 400
        
        tagging_system = get_tagging_system()
        
        # Get required and optional tags for the account
        required_tags = tagging_system.get_required_tags_for_account(account_code)
        optional_tags = tagging_system.get_optional_tags_for_account(account_code)
        
        # Generate suggestions based on account type and previous transactions
        suggestions = {}
        
        # For revenue accounts, suggest common product categories
        if account_type == 'revenue':
            suggestions['product_category'] = [
                'Electronics', 'Clothing', 'Food & Beverage', 'Services', 'Software'
            ]
            suggestions['sales_channel'] = [
                'Online', 'Retail', 'Wholesale', 'Direct', 'Partner'
            ]
        
        # For expense accounts, suggest common departments
        elif account_type == 'expense':
            suggestions['department'] = [
                'Sales', 'Marketing', 'Operations', 'Administration', 'IT'
            ]
            suggestions['cost_center'] = [
                'HQ', 'Branch-001', 'Branch-002', 'Remote', 'Field'
            ]
        
        # For AR accounts, suggest common customers (this would come from actual data)
        elif account_type == 'asset' and 'customer' in required_tags:
            suggestions['customer'] = [
                'Customer A', 'Customer B', 'Customer C'  # Would be from actual customer data
            ]
        
        # For AP accounts, suggest common vendors
        elif account_type == 'liability' and 'vendor' in required_tags:
            suggestions['vendor'] = [
                'Vendor A', 'Vendor B', 'Vendor C'  # Would be from actual vendor data
            ]
        
        return jsonify({
            'account_code': account_code,
            'required_tags': required_tags,
            'optional_tags': optional_tags,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting tag suggestions: {e}")
        return jsonify({'error': 'Failed to get tag suggestions'}), 500

@tagging_bp.route('/analytics/summary', methods=['GET'])
def get_tagging_analytics():
    """Get analytics summary of tagging usage"""
    try:
        tagging_system = get_tagging_system()
        
        # Get all accounts with tagging requirements
        accounts = Account.query.all()
        total_accounts = len(accounts)
        accounts_with_required_tags = 0
        accounts_with_optional_tags = 0
        
        for account in accounts:
            required_tags = tagging_system.get_required_tags_for_account(account.code)
            optional_tags = tagging_system.get_optional_tags_for_account(account.code)
            
            if required_tags:
                accounts_with_required_tags += 1
            if optional_tags:
                accounts_with_optional_tags += 1
        
        # Get tag category statistics
        categories = tagging_system.get_tag_categories()
        required_categories = [cat for cat in categories if cat['is_required']]
        optional_categories = [cat for cat in categories if not cat['is_required']]
        
        return jsonify({
            'accounts': {
                'total': total_accounts,
                'with_required_tags': accounts_with_required_tags,
                'with_optional_tags': accounts_with_optional_tags,
                'percentage_with_required': (accounts_with_required_tags / total_accounts * 100) if total_accounts > 0 else 0
            },
            'tag_categories': {
                'total': len(categories),
                'required': len(required_categories),
                'optional': len(optional_categories)
            },
            'compliance': {
                'ledger_accounts_required': True,
                'tags_optional': True,
                'validation_enabled': True
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting tagging analytics: {e}")
        return jsonify({'error': 'Failed to get tagging analytics'}), 500


