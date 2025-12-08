"""
Accounting Period Management API Routes
=====================================

This module provides API endpoints for managing accounting periods,
fiscal years, and period-related operations.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
from modules.finance.accounting_periods import (
    FiscalYear, AccountingPeriod, period_manager
)
from modules.core.tenant_helpers import get_current_user_tenant_id, get_current_user_id
from app import db

accounting_period_bp = Blueprint('accounting_periods', __name__, url_prefix='/api/finance/accounting-periods')

@accounting_period_bp.route('/fiscal-years', methods=['GET'])
def get_fiscal_years():
    """Get all fiscal years for the tenant - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        fiscal_years = FiscalYear.query.filter_by(tenant_id=tenant_id).order_by(FiscalYear.year.desc()).all()
        
        current_period = period_manager.get_current_period(tenant_id)
        return jsonify({
            "fiscal_years": [fy.to_dict() for fy in fiscal_years],
            "current_fiscal_year": current_period.fiscal_year.to_dict() if current_period else None
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get fiscal years: {str(e)}"}), 500

@accounting_period_bp.route('/fiscal-years', methods=['POST'])
def create_fiscal_year():
    """Create a new fiscal year - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        data = request.get_json()
        
        year = data.get('year')
        if not year:
            return jsonify({"error": "Year is required"}), 400
        
        # Check if fiscal year already exists for this tenant
        existing = FiscalYear.query.filter_by(year=year, tenant_id=tenant_id).first()
        if existing:
            return jsonify({"error": f"Fiscal year {year} already exists"}), 400
        
        # Create fiscal year
        fiscal_year = FiscalYear.create_default_fiscal_year(year, tenant_id)
        db.session.commit()
        
        return jsonify({
            "message": f"Fiscal year {year} created successfully",
            "fiscal_year": fiscal_year.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create fiscal year: {str(e)}"}), 500

@accounting_period_bp.route('/periods', methods=['GET'])
def get_accounting_periods():
    """Get all accounting periods for the tenant - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        # Get query parameters
        fiscal_year_id = request.args.get('fiscal_year_id')
        status = request.args.get('status')
        
        query = AccountingPeriod.query.filter_by(tenant_id=tenant_id)
        
        if fiscal_year_id:
            query = query.filter_by(fiscal_year_id=fiscal_year_id)
        
        if status:
            query = query.filter_by(status=status)
        
        periods = query.order_by(AccountingPeriod.fiscal_year_id, AccountingPeriod.period_number).all()
        
        current_period = period_manager.get_current_period(tenant_id)
        return jsonify({
            "periods": [p.to_dict() for p in periods],
            "current_period": current_period.to_dict() if current_period else None
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get accounting periods: {str(e)}"}), 500

@accounting_period_bp.route('/periods/<int:period_id>', methods=['GET'])
def get_accounting_period(period_id):
    """Get a specific accounting period - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        period = AccountingPeriod.query.filter_by(id=period_id, tenant_id=tenant_id).first()
        if not period:
            return jsonify({"error": "Period not found"}), 404
        
        return jsonify({
            "period": period.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get period: {str(e)}"}), 500

@accounting_period_bp.route('/periods/<int:period_id>/lock', methods=['POST'])
def lock_period(period_id):
    """Lock an accounting period - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        data = request.get_json()
        reason = data.get('reason', 'Manual lock')
        
        period = AccountingPeriod.query.filter_by(id=period_id, tenant_id=tenant_id).first()
        if not period:
            return jsonify({"error": "Period not found"}), 404
        
        if period.is_locked:
            return jsonify({"error": "Period is already locked"}), 400
        
        period.lock_period(user_id_int, reason)
        
        return jsonify({
            "message": f"Period {period.short_name} locked successfully",
            "period": period.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to lock period: {str(e)}"}), 500

@accounting_period_bp.route('/periods/<int:period_id>/unlock', methods=['POST'])
def unlock_period(period_id):
    """Unlock an accounting period - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        period = AccountingPeriod.query.filter_by(id=period_id, tenant_id=tenant_id).first()
        if not period:
            return jsonify({"error": "Period not found"}), 404
        
        if not period.is_locked:
            return jsonify({"error": "Period is not locked"}), 400
        
        period.unlock_period(user_id_int)
        
        return jsonify({
            "message": f"Period {period.short_name} unlocked successfully",
            "period": period.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to unlock period: {str(e)}"}), 500

@accounting_period_bp.route('/periods/<int:period_id>/close', methods=['POST'])
def close_period(period_id):
    """Close an accounting period - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        data = request.get_json()
        reason = data.get('reason', 'Period closed')
        
        period = period_manager.close_period(period_id, tenant_id, reason)
        
        return jsonify({
            "message": f"Period {period.short_name} closed successfully",
            "period": period.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to close period: {str(e)}"}), 500

@accounting_period_bp.route('/validate-date', methods=['POST'])
def validate_transaction_date():
    """Validate if a transaction can be created for a specific date - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        data = request.get_json()
        
        transaction_date_str = data.get('date')
        if not transaction_date_str:
            return jsonify({"error": "Date is required"}), 400
        
        try:
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        is_valid, message, period = period_manager.validate_transaction_date(transaction_date, tenant_id)
        
        return jsonify({
            "is_valid": is_valid,
            "message": message,
            "period": period.to_dict() if period else None,
            "transaction_date": transaction_date_str
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to validate date: {str(e)}"}), 500

@accounting_period_bp.route('/summary', methods=['GET'])
def get_period_summary():
    """Get a summary of all periods for the tenant - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        summary = period_manager.get_period_summary(tenant_id)
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get period summary: {str(e)}"}), 500

@accounting_period_bp.route('/initialize', methods=['POST'])
def initialize_periods():
    """Initialize default periods for the tenant - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        # Check if tenant already has periods
        existing_periods = AccountingPeriod.query.filter_by(tenant_id=tenant_id).count()
        if existing_periods > 0:
            return jsonify({"error": "Tenant already has accounting periods"}), 400
        
        # Initialize default periods
        fiscal_year = period_manager.initialize_default_periods(tenant_id)
        
        return jsonify({
            "message": "Default accounting periods initialized successfully",
            "fiscal_year": fiscal_year.to_dict(),
            "periods_created": 12
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to initialize periods: {str(e)}"}), 500

@accounting_period_bp.route('/current', methods=['GET'])
def get_current_period():
    """Get the current accounting period - TENANT-CENTRIC"""
    try:
        tenant_id = get_current_user_tenant_id()
        if not tenant_id:
            return jsonify({"error": "Tenant context required"}), 403
        
        current_period = period_manager.get_current_period(tenant_id)
        if not current_period:
            return jsonify({"error": "No current period found"}), 404
        
        return jsonify({
            "current_period": current_period.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get current period: {str(e)}"}), 500

