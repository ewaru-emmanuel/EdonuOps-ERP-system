# backend/modules/finance/daily_cycle_notifications.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from typing import Dict, List
import logging

from app import db
from modules.finance.daily_cycle_models import DailyCycleAuditLog, AdjustmentEntry, DailyBalance, DailyCycleStatus

logger = logging.getLogger(__name__)

# Create blueprint
daily_cycle_notifications_bp = Blueprint('daily_cycle_notifications', __name__, url_prefix='/api/finance/daily-cycle/notifications')

@daily_cycle_notifications_bp.route('/recent', methods=['GET'])
def get_recent_notifications():
    """
    Get recent daily cycle notifications for the notification system
    """
    try:
        # Get query parameters
        hours_back = request.args.get('hours_back', 24, type=int)  # Default: last 24 hours
        limit = request.args.get('limit', 50, type=int)  # Default: 50 notifications
        
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Get recent audit logs
        recent_audit_logs = DailyCycleAuditLog.query.filter(
            DailyCycleAuditLog.action_timestamp >= time_threshold
        ).order_by(DailyCycleAuditLog.action_timestamp.desc()).limit(limit).all()
        
        # Get pending adjustments
        pending_adjustments = AdjustmentEntry.query.filter_by(status='pending').all()
        
        # Get locked days that might need attention
        locked_days = DailyBalance.query.filter(
            DailyBalance.is_locked == True,
            DailyBalance.locked_at >= time_threshold
        ).all()
        
        # Get failed cycles
        failed_cycles = DailyCycleStatus.query.filter(
            DailyCycleStatus.overall_status == 'failed',
            DailyCycleStatus.updated_at >= time_threshold
        ).all()
        
        notifications = []
        
        # Process audit logs
        for log in recent_audit_logs:
            notification = _create_notification_from_audit_log(log)
            if notification:
                notifications.append(notification)
        
        # Process pending adjustments
        for adjustment in pending_adjustments:
            notification = _create_notification_from_adjustment(adjustment)
            if notification:
                notifications.append(notification)
        
        # Process locked days
        for balance in locked_days:
            notification = _create_notification_from_locked_day(balance)
            if notification:
                notifications.append(notification)
        
        # Process failed cycles
        for cycle in failed_cycles:
            notification = _create_notification_from_failed_cycle(cycle)
            if notification:
                notifications.append(notification)
        
        # Sort by timestamp (most recent first)
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        notifications = notifications[:limit]
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'total_count': len(notifications),
            'time_threshold': time_threshold.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching daily cycle notifications: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch notifications',
            'details': str(e)
        }), 500

@daily_cycle_notifications_bp.route('/critical', methods=['GET'])
def get_critical_notifications():
    """
    Get critical daily cycle notifications that need immediate attention
    """
    try:
        critical_notifications = []
        
        # Check for failed cycles
        failed_cycles = DailyCycleStatus.query.filter_by(overall_status='failed').all()
        for cycle in failed_cycles:
            critical_notifications.append({
                'id': f'failed_cycle_{cycle.cycle_date}',
                'type': 'daily_cycle_failed',
                'severity': 'error',
                'title': 'Daily Cycle Failed',
                'message': f'Daily cycle failed for {cycle.cycle_date}. Error: {cycle.error_message or "Unknown error"}',
                'timestamp': cycle.updated_at.isoformat() if cycle.updated_at else datetime.utcnow().isoformat(),
                'href': f'/finance?feature=daily-cycle&date={cycle.cycle_date}',
                'action_required': True
            })
        
        # Check for long-pending adjustments
        long_pending_adjustments = AdjustmentEntry.query.filter(
            AdjustmentEntry.status == 'pending',
            AdjustmentEntry.created_at <= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        for adjustment in long_pending_adjustments:
            critical_notifications.append({
                'id': f'pending_adjustment_{adjustment.id}',
                'type': 'adjustment_pending',
                'severity': 'warning',
                'title': 'Adjustment Pending Approval',
                'message': f'Adjustment for {adjustment.original_date} has been pending for over 24 hours',
                'timestamp': adjustment.created_at.isoformat(),
                'href': f'/finance?feature=daily-cycle&date={adjustment.original_date}',
                'action_required': True
            })
        
        # Check for grace period expirations
        grace_period_expired = DailyBalance.query.filter(
            DailyBalance.grace_period_ends < datetime.utcnow(),
            DailyBalance.allows_adjustments == True
        ).all()
        
        for balance in grace_period_expired:
            critical_notifications.append({
                'id': f'grace_expired_{balance.account_id}_{balance.balance_date}',
                'type': 'grace_period_expired',
                'severity': 'info',
                'title': 'Grace Period Expired',
                'message': f'Grace period expired for {balance.account.account_name} on {balance.balance_date}',
                'timestamp': balance.grace_period_ends.isoformat() if balance.grace_period_ends else datetime.utcnow().isoformat(),
                'href': f'/finance?feature=daily-cycle&date={balance.balance_date}',
                'action_required': False
            })
        
        return jsonify({
            'success': True,
            'critical_notifications': critical_notifications,
            'total_count': len(critical_notifications)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching critical notifications: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch critical notifications',
            'details': str(e)
        }), 500

def _create_notification_from_audit_log(log: DailyCycleAuditLog) -> Dict:
    """Create notification from audit log entry"""
    try:
        notification_types = {
            'opening_captured': {
                'type': 'daily_cycle_opening',
                'severity': 'info',
                'title': 'Opening Balances Captured',
                'message': f'Opening balances captured for {log.cycle_date} by {log.user_name or log.user_id}'
            },
            'closing_calculated': {
                'type': 'daily_cycle_closing',
                'severity': 'success',
                'title': 'Closing Balances Calculated',
                'message': f'Closing balances calculated for {log.cycle_date} by {log.user_name or log.user_id}'
            },
            'locked': {
                'type': 'daily_cycle_locked',
                'severity': 'warning',
                'title': 'Day Locked',
                'message': f'Day {log.cycle_date} has been locked by {log.user_name or log.user_id}'
            },
            'unlocked': {
                'type': 'daily_cycle_unlocked',
                'severity': 'info',
                'title': 'Day Unlocked',
                'message': f'Day {log.cycle_date} has been unlocked by {log.user_name or log.user_id}'
            },
            'adjustment_made': {
                'type': 'adjustment_created',
                'severity': 'info',
                'title': 'Adjustment Created',
                'message': f'Adjustment created for {log.cycle_date} by {log.user_name or log.user_id}'
            },
            'adjustment_applied': {
                'type': 'adjustment_applied',
                'severity': 'success',
                'title': 'Adjustment Applied',
                'message': f'Adjustment applied for {log.cycle_date} by {log.user_name or log.user_id}'
            }
        }
        
        notification_config = notification_types.get(log.action)
        if not notification_config:
            return None
        
        return {
            'id': f'audit_{log.id}',
            'type': notification_config['type'],
            'severity': notification_config['severity'],
            'title': notification_config['title'],
            'message': notification_config['message'],
            'timestamp': log.action_timestamp.isoformat(),
            'href': f'/finance?feature=daily-cycle&date={log.cycle_date}',
            'action_required': False,
            'user_id': log.user_id,
            'user_name': log.user_name,
            'details': {
                'affected_accounts': log.affected_accounts,
                'total_amount': log.total_amount,
                'action_details': log.action_details
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating notification from audit log: {str(e)}")
        return None

def _create_notification_from_adjustment(adjustment: AdjustmentEntry) -> Dict:
    """Create notification from pending adjustment"""
    try:
        return {
            'id': f'pending_adjustment_{adjustment.id}',
            'type': 'adjustment_pending',
            'severity': 'warning',
            'title': 'Adjustment Pending Approval',
            'message': f'Adjustment for {adjustment.account.account_name} on {adjustment.original_date} is pending approval',
            'timestamp': adjustment.created_at.isoformat(),
            'href': f'/finance?feature=daily-cycle&date={adjustment.original_date}',
            'action_required': True,
            'user_id': adjustment.created_by,
            'details': {
                'adjustment_type': adjustment.adjustment_type,
                'adjustment_amount': adjustment.adjustment_balance,
                'reason': adjustment.reason
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating notification from adjustment: {str(e)}")
        return None

def _create_notification_from_locked_day(balance: DailyBalance) -> Dict:
    """Create notification from locked day"""
    try:
        return {
            'id': f'locked_day_{balance.account_id}_{balance.balance_date}',
            'type': 'daily_cycle_locked',
            'severity': 'info',
            'title': 'Day Locked',
            'message': f'Day {balance.balance_date} has been locked for {balance.account.account_name}',
            'timestamp': balance.locked_at.isoformat() if balance.locked_at else datetime.utcnow().isoformat(),
            'href': f'/finance?feature=daily-cycle&date={balance.balance_date}',
            'action_required': False,
            'details': {
                'lock_reason': balance.lock_reason,
                'locked_by': balance.locked_by
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating notification from locked day: {str(e)}")
        return None

def _create_notification_from_failed_cycle(cycle: DailyCycleStatus) -> Dict:
    """Create notification from failed cycle"""
    try:
        return {
            'id': f'failed_cycle_{cycle.cycle_date}',
            'type': 'daily_cycle_failed',
            'severity': 'error',
            'title': 'Daily Cycle Failed',
            'message': f'Daily cycle failed for {cycle.cycle_date}. {cycle.error_message or "Unknown error"}',
            'timestamp': cycle.updated_at.isoformat() if cycle.updated_at else datetime.utcnow().isoformat(),
            'href': f'/finance?feature=daily-cycle&date={cycle.cycle_date}',
            'action_required': True,
            'details': {
                'opening_status': cycle.opening_status,
                'closing_status': cycle.closing_status,
                'error_message': cycle.error_message
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating notification from failed cycle: {str(e)}")
        return None
