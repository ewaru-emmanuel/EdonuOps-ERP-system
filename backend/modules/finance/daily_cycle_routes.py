from flask import Blueprint, request, jsonify
from datetime import datetime, date
from typing import Dict, List
import logging

from app import db
from services.daily_cycle_service import DailyCycleService
from modules.finance.daily_cycle_models import DailyBalance, DailyCycleStatus, DailyTransactionSummary
from app.decorators import require_auth, validate_json

logger = logging.getLogger(__name__)

# Create blueprint
daily_cycle_bp = Blueprint('daily_cycle', __name__, url_prefix='/api/finance/daily-cycle')

@daily_cycle_bp.route('/capture-opening', methods=['POST'])
@require_auth
@validate_json(['cycle_date'])
def capture_opening_balances():
    """
    Capture opening balances for all accounts for a specific date
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
        
        # Execute opening balance capture
        result = DailyCycleService.capture_opening_balances(cycle_date, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error capturing opening balances: {str(e)}")
        return jsonify({
            'error': 'Failed to capture opening balances',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/calculate-closing', methods=['POST'])
@require_auth
@validate_json(['cycle_date'])
def calculate_closing_balances():
    """
    Calculate closing balances for all accounts for a specific date
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
        
        # Execute closing balance calculation
        result = DailyCycleService.calculate_closing_balances(cycle_date, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating closing balances: {str(e)}")
        return jsonify({
            'error': 'Failed to calculate closing balances',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/execute-full-cycle', methods=['POST'])
@require_auth
@validate_json(['cycle_date'])
def execute_full_daily_cycle():
    """
    Execute complete daily cycle: opening capture + closing calculation
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
        result = DailyCycleService.execute_full_daily_cycle(cycle_date, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing daily cycle: {str(e)}")
        return jsonify({
            'error': 'Failed to execute daily cycle',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/status/<cycle_date>', methods=['GET'])
@require_auth
def get_daily_cycle_status(cycle_date):
    """
    Get the status of daily cycle for a specific date
    """
    try:
        # Parse date
        try:
            cycle_date_obj = datetime.strptime(cycle_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get cycle status
        result = DailyCycleService.get_daily_cycle_status(cycle_date_obj)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily cycle status: {str(e)}")
        return jsonify({
            'error': 'Failed to get daily cycle status',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/account-balance/<int:account_id>/<balance_date>', methods=['GET'])
@require_auth
def get_account_daily_balance(account_id, balance_date):
    """
    Get daily balance details for a specific account and date
    """
    try:
        # Parse date
        try:
            balance_date_obj = datetime.strptime(balance_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get account daily balance
        result = DailyCycleService.get_account_daily_balance(account_id, balance_date_obj)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting account daily balance: {str(e)}")
        return jsonify({
            'error': 'Failed to get account daily balance',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/balances/<balance_date>', methods=['GET'])
@require_auth
def get_daily_balances(balance_date):
    """
    Get all daily balances for a specific date
    """
    try:
        # Parse date
        try:
            balance_date_obj = datetime.strptime(balance_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get daily balances
        daily_balances = DailyBalance.get_daily_balances_for_date(balance_date_obj)
        
        balances_data = []
        for balance in daily_balances:
            balances_data.append({
                'id': balance.id,
                'account_id': balance.account_id,
                'account_name': balance.account.account_name,
                'account_type': balance.account.account_type,
                'opening_balance': balance.opening_balance,
                'daily_debit': balance.daily_debit,
                'daily_credit': balance.daily_credit,
                'daily_net_movement': balance.daily_net_movement,
                'closing_balance': balance.closing_balance,
                'cycle_status': balance.cycle_status,
                'is_opening_captured': balance.is_opening_captured,
                'is_closing_calculated': balance.is_closing_calculated
            })
        
        return jsonify({
            'success': True,
            'data': {
                'balance_date': balance_date,
                'balances': balances_data,
                'total_accounts': len(balances_data)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily balances: {str(e)}")
        return jsonify({
            'error': 'Failed to get daily balances',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/transaction-summary/<summary_date>', methods=['GET'])
@require_auth
def get_daily_transaction_summary(summary_date):
    """
    Get daily transaction summary for a specific date
    """
    try:
        # Parse date
        try:
            summary_date_obj = datetime.strptime(summary_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get transaction summary
        summary = DailyTransactionSummary.get_summary_for_date(summary_date_obj)
        
        if not summary:
            return jsonify({
                'success': True,
                'data': {
                    'summary_date': summary_date,
                    'message': 'No transaction summary found for this date'
                }
            }), 200
        
        summary_data = {
            'summary_date': summary_date,
            'total_transactions': summary.total_transactions,
            'posted_transactions': summary.posted_transactions,
            'draft_transactions': summary.draft_transactions,
            'total_debits': summary.total_debits,
            'total_credits': summary.total_credits,
            'net_movement': summary.net_movement,
            'asset_movement': summary.asset_movement,
            'liability_movement': summary.liability_movement,
            'equity_movement': summary.equity_movement,
            'revenue_movement': summary.revenue_movement,
            'expense_movement': summary.expense_movement
        }
        
        return jsonify({
            'success': True,
            'data': summary_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily transaction summary: {str(e)}")
        return jsonify({
            'error': 'Failed to get daily transaction summary',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/pending-cycles', methods=['GET'])
@require_auth
def get_pending_cycles():
    """
    Get all pending daily cycles
    """
    try:
        # Get pending cycles
        pending_cycles = DailyCycleStatus.get_pending_cycles()
        
        cycles_data = []
        for cycle in pending_cycles:
            cycles_data.append({
                'cycle_date': cycle.cycle_date.isoformat(),
                'overall_status': cycle.overall_status,
                'opening_status': cycle.opening_status,
                'closing_status': cycle.closing_status,
                'total_accounts': cycle.total_accounts,
                'accounts_processed': cycle.accounts_processed,
                'error_message': cycle.error_message
            })
        
        return jsonify({
            'success': True,
            'data': {
                'pending_cycles': cycles_data,
                'total_pending': len(cycles_data)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting pending cycles: {str(e)}")
        return jsonify({
            'error': 'Failed to get pending cycles',
            'details': str(e)
        }), 500

@daily_cycle_bp.route('/latest-status', methods=['GET'])
@require_auth
def get_latest_cycle_status():
    """
    Get the most recent daily cycle status
    """
    try:
        # Get latest status
        latest_status = DailyCycleStatus.get_latest_status()
        
        if not latest_status:
            return jsonify({
                'success': True,
                'data': {
                    'message': 'No daily cycles found'
                }
            }), 200
        
        status_data = {
            'cycle_date': latest_status.cycle_date.isoformat(),
            'overall_status': latest_status.overall_status,
            'opening_status': latest_status.opening_status,
            'closing_status': latest_status.closing_status,
            'total_accounts': latest_status.total_accounts,
            'accounts_processed': latest_status.accounts_processed,
            'total_opening_balance': latest_status.total_opening_balance,
            'total_closing_balance': latest_status.total_closing_balance,
            'total_daily_movement': latest_status.total_daily_movement,
            'opening_captured_at': latest_status.opening_captured_at.isoformat() if latest_status.opening_captured_at else None,
            'closing_calculated_at': latest_status.closing_calculated_at.isoformat() if latest_status.closing_calculated_at else None,
            'error_message': latest_status.error_message
        }
        
        return jsonify({
            'success': True,
            'data': status_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting latest cycle status: {str(e)}")
        return jsonify({
            'error': 'Failed to get latest cycle status',
            'details': str(e)
        }), 500
