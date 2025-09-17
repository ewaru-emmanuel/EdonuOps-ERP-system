# backend/modules/finance/enhanced_daily_balance_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from typing import Dict, List
import logging

from app import db
from services.enhanced_daily_balance_service import EnhancedDailyBalanceService
from app.decorators import require_auth, validate_json

logger = logging.getLogger(__name__)

# Create blueprint
enhanced_daily_balance_bp = Blueprint('enhanced_daily_balance', __name__, url_prefix='/api/finance/daily-balance')

@enhanced_daily_balance_bp.route('/morning-opening', methods=['POST'])
@require_auth
@validate_json(['cycle_date'])
def execute_morning_opening_cycle():
    """
    🕰️ Morning: Opening Balances Are Ready
    
    Execute the morning opening cycle to carry forward closing balances 
    from the previous day into the new day as opening balances.
    """
    try:
        data = request.get_json()
        cycle_date_str = data.get('cycle_date')
        user_id = request.headers.get('X-User-ID', 'system')
        
        # Parse date
        try:
            cycle_date = datetime.strptime(cycle_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Execute morning opening cycle
        result = EnhancedDailyBalanceService.execute_morning_opening_cycle(cycle_date, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing morning opening cycle: {str(e)}")
        return jsonify({
            'error': 'Failed to execute morning opening cycle',
            'details': str(e)
        }), 500

@enhanced_daily_balance_bp.route('/evening-closing', methods=['POST'])
@require_auth
@validate_json(['cycle_date'])
def execute_evening_closing_cycle():
    """
    🌙 Evening: Closing the Day
    
    Execute the evening closing cycle to calculate closing balances using:
    Opening Balance + Debits – Credits = Closing Balance
    """
    try:
        data = request.get_json()
        cycle_date_str = data.get('cycle_date')
        user_id = request.headers.get('X-User-ID', 'system')
        
        # Parse date
        try:
            cycle_date = datetime.strptime(cycle_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Execute evening closing cycle
        result = EnhancedDailyBalanceService.execute_evening_closing_cycle(cycle_date, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing evening closing cycle: {str(e)}")
        return jsonify({
            'error': 'Failed to execute evening closing cycle',
            'details': str(e)
        }), 500

@enhanced_daily_balance_bp.route('/full-cycle', methods=['POST'])
@require_auth
@validate_json(['cycle_date'])
def execute_full_daily_cycle():
    """
    Execute complete daily cycle: Morning Opening + Evening Closing
    """
    try:
        data = request.get_json()
        cycle_date_str = data.get('cycle_date')
        user_id = request.headers.get('X-User-ID', 'system')
        
        # Parse date
        try:
            cycle_date = datetime.strptime(cycle_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Execute full daily cycle
        result = EnhancedDailyBalanceService.execute_full_daily_cycle(cycle_date, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing full daily cycle: {str(e)}")
        return jsonify({
            'error': 'Failed to execute full daily cycle',
            'details': str(e)
        }), 500

@enhanced_daily_balance_bp.route('/summary/<cycle_date>', methods=['GET'])
@require_auth
def get_daily_balance_flow_summary(cycle_date):
    """
    📊 Reporting: Snapshot of the Day
    
    Get comprehensive daily balance flow summary including:
    - Trial Balance
    - Account Analysis  
    - Cash Position Summary
    - Subledger-to-GL Reconciliation
    """
    try:
        # Parse date
        try:
            cycle_date_obj = datetime.strptime(cycle_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get daily balance flow summary
        result = EnhancedDailyBalanceService.get_daily_balance_flow_summary(cycle_date_obj)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily balance flow summary: {str(e)}")
        return jsonify({
            'error': 'Failed to get daily balance flow summary',
            'details': str(e)
        }), 500

@enhanced_daily_balance_bp.route('/today-summary', methods=['GET'])
@require_auth
def get_today_summary():
    """
    Get today's daily balance flow summary
    """
    try:
        today = date.today()
        result = EnhancedDailyBalanceService.get_daily_balance_flow_summary(today)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting today's summary: {str(e)}")
        return jsonify({
            'error': 'Failed to get today\'s summary',
            'details': str(e)
        }), 500

@enhanced_daily_balance_bp.route('/opening-balances/<cycle_date>', methods=['GET'])
@require_auth
def get_opening_balances(cycle_date):
    """
    Get opening balances for a specific date
    """
    try:
        # Parse date
        try:
            cycle_date_obj = datetime.strptime(cycle_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get opening balances
        from modules.finance.daily_cycle_models import DailyBalance
        from modules.finance.advanced_models import ChartOfAccounts
        
        daily_balances = DailyBalance.query.filter_by(balance_date=cycle_date_obj).all()
        
        opening_balances = []
        for balance in daily_balances:
            account = ChartOfAccounts.query.get(balance.account_id)
            if account:
                opening_balances.append({
                    "account_id": account.id,
                    "account_name": account.account_name,
                    "account_type": account.account_type,
                    "opening_balance": balance.opening_balance,
                    "opening_debit": balance.opening_debit,
                    "opening_credit": balance.opening_credit
                })
        
        return jsonify({
            'success': True,
            'data': {
                'cycle_date': cycle_date,
                'opening_balances': opening_balances
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting opening balances: {str(e)}")
        return jsonify({
            'error': 'Failed to get opening balances',
            'details': str(e)
        }), 500

@enhanced_daily_balance_bp.route('/closing-balances/<cycle_date>', methods=['GET'])
@require_auth
def get_closing_balances(cycle_date):
    """
    Get closing balances for a specific date
    """
    try:
        # Parse date
        try:
            cycle_date_obj = datetime.strptime(cycle_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get closing balances
        from modules.finance.daily_cycle_models import DailyBalance
        from modules.finance.advanced_models import ChartOfAccounts
        
        daily_balances = DailyBalance.query.filter_by(balance_date=cycle_date_obj).all()
        
        closing_balances = []
        for balance in daily_balances:
            account = ChartOfAccounts.query.get(balance.account_id)
            if account:
                closing_balances.append({
                    "account_id": account.id,
                    "account_name": account.account_name,
                    "account_type": account.account_type,
                    "opening_balance": balance.opening_balance,
                    "total_debits": balance.total_debits or 0,
                    "total_credits": balance.total_credits or 0,
                    "closing_balance": balance.closing_balance,
                    "closing_debit": balance.closing_debit,
                    "closing_credit": balance.closing_credit,
                    "transaction_count": balance.transaction_count or 0
                })
        
        return jsonify({
            'success': True,
            'data': {
                'cycle_date': cycle_date,
                'closing_balances': closing_balances
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting closing balances: {str(e)}")
        return jsonify({
            'error': 'Failed to get closing balances',
            'details': str(e)
        }), 500
