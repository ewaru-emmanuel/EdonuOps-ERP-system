# backend/services/shift_based_closing_service.py
from __future__ import annotations
import logging
from datetime import datetime, date, timedelta, time
from typing import Dict, List, Optional
from sqlalchemy import func, and_, or_
import json

from app import db
from modules.finance.daily_cycle_models import (
    DailyBalance, DailyCycleStatus, DailyTransactionSummary, 
    AdjustmentEntry, DailyCycleAuditLog
)
from modules.finance.advanced_models import ChartOfAccounts, GeneralLedgerEntry
from services.enhanced_daily_cycle_service import EnhancedDailyCycleService

logger = logging.getLogger(__name__)

class ShiftBasedClosingService:
    """
    Handles shift-based closing for 24/7 businesses
    Supports multiple closing times and shift-based operations
    """
    
    def __init__(self):
        self.enhanced_service = EnhancedDailyCycleService()
    
    def configure_shift_schedule(self, business_type: str = '24_7') -> Dict:
        """
        Configure shift schedule based on business type
        """
        schedules = {
            '24_7': {
                'closing_times': ['00:00', '08:00', '16:00'],  # Midnight, 8 AM, 4 PM
                'shift_names': ['Night Shift', 'Day Shift', 'Evening Shift'],
                'grace_period_hours': 2,
                'auto_lock_after_closing': True
            },
            'extended_hours': {
                'closing_times': ['00:00', '12:00'],  # Midnight, Noon
                'shift_names': ['First Shift', 'Second Shift'],
                'grace_period_hours': 1,
                'auto_lock_after_closing': True
            },
            'standard': {
                'closing_times': ['00:00'],  # Midnight only
                'shift_names': ['Daily'],
                'grace_period_hours': 2,
                'auto_lock_after_closing': True
            }
        }
        
        return schedules.get(business_type, schedules['standard'])
    
    def get_current_shift_info(self, current_time: datetime = None) -> Dict:
        """
        Get current shift information based on time
        """
        if not current_time:
            current_time = datetime.now()
        
        current_date = current_time.date()
        current_time_only = current_time.time()
        
        # Get business configuration (in real implementation, this would come from settings)
        schedule = self.configure_shift_schedule('24_7')
        
        # Determine current shift
        current_shift = None
        next_shift = None
        shift_index = 0
        
        for i, closing_time_str in enumerate(schedule['closing_times']):
            closing_time = datetime.strptime(closing_time_str, '%H:%M').time()
            
            if current_time_only < closing_time:
                current_shift = {
                    'index': i,
                    'name': schedule['shift_names'][i],
                    'closing_time': closing_time_str,
                    'closing_datetime': datetime.combine(current_date, closing_time)
                }
                next_shift = {
                    'index': (i + 1) % len(schedule['closing_times']),
                    'name': schedule['shift_names'][(i + 1) % len(schedule['shift_names'])],
                    'closing_time': schedule['closing_times'][(i + 1) % len(schedule['closing_times'])],
                    'closing_datetime': datetime.combine(
                        current_date + timedelta(days=1) if (i + 1) >= len(schedule['closing_times']) else current_date,
                        datetime.strptime(schedule['closing_times'][(i + 1) % len(schedule['closing_times'])], '%H:%M').time()
                    )
                }
                break
        
        # If we're past all closing times, we're in the last shift
        if not current_shift:
            current_shift = {
                'index': len(schedule['closing_times']) - 1,
                'name': schedule['shift_names'][-1],
                'closing_time': schedule['closing_times'][-1],
                'closing_datetime': datetime.combine(current_date, datetime.strptime(schedule['closing_times'][-1], '%H:%M').time())
            }
            next_shift = {
                'index': 0,
                'name': schedule['shift_names'][0],
                'closing_time': schedule['closing_times'][0],
                'closing_datetime': datetime.combine(current_date + timedelta(days=1), datetime.strptime(schedule['closing_times'][0], '%H:%M').time())
            }
        
        return {
            'current_shift': current_shift,
            'next_shift': next_shift,
            'time_until_closing': (current_shift['closing_datetime'] - current_time).total_seconds() / 3600,  # hours
            'schedule': schedule
        }
    
    def execute_shift_closing(self, shift_date: date, shift_index: int, 
                            user_id: str, user_name: str = None, 
                            user_role: str = None, ip_address: str = None,
                            user_agent: str = None) -> Dict:
        """
        Execute closing for a specific shift
        """
        try:
            # Get shift information
            schedule = self.configure_shift_schedule('24_7')
            shift_name = schedule['shift_names'][shift_index]
            closing_time = schedule['closing_times'][shift_index]
            
            # Create a unique cycle date for this shift
            cycle_date = f"{shift_date.isoformat()}_shift_{shift_index}"
            
            # Check if this shift is already closed
            existing_status = DailyCycleStatus.query.filter_by(cycle_date=cycle_date).first()
            if existing_status and existing_status.closing_status == 'completed':
                return {
                    "status": "already_closed",
                    "message": f"Shift {shift_name} already closed for {shift_date}",
                    "shift_date": shift_date,
                    "shift_name": shift_name
                }
            
            # Execute the closing process
            result = self.enhanced_service.calculate_closing_balances(
                cycle_date=shift_date,
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                ip_address=ip_address,
                user_agent=user_agent,
                lock_after_closing=schedule['auto_lock_after_closing']
            )
            
            # Create shift-specific status record
            if not existing_status:
                shift_status = DailyCycleStatus(
                    cycle_date=cycle_date,
                    opening_status='completed',  # Assume opening was done
                    closing_status='completed',
                    overall_status='completed',
                    total_accounts=result.get('accounts_processed', 0),
                    accounts_processed=result.get('accounts_processed', 0),
                    total_closing_balance=result.get('total_closing_balance', 0),
                    total_daily_movement=result.get('total_daily_movement', 0),
                    closing_calculated_at=datetime.utcnow(),
                    closing_calculated_by=user_id
                )
                db.session.add(shift_status)
            
            # Log shift-specific audit trail
            DailyCycleAuditLog.log_action(
                cycle_date=shift_date,
                action='shift_closed',
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                action_details=json.dumps({
                    'shift_index': shift_index,
                    'shift_name': shift_name,
                    'closing_time': closing_time,
                    'accounts_processed': result.get('accounts_processed', 0),
                    'total_closing_balance': result.get('total_closing_balance', 0)
                }),
                affected_accounts=result.get('accounts_processed', 0),
                total_amount=result.get('total_closing_balance', 0),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.commit()
            
            return {
                "status": "success",
                "message": f"Shift {shift_name} closed successfully for {shift_date}",
                "shift_date": shift_date,
                "shift_name": shift_name,
                "shift_index": shift_index,
                "closing_time": closing_time,
                "details": result
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to close shift {shift_index} for {shift_date}: {str(e)}")
            raise
    
    def get_shift_status(self, shift_date: date) -> Dict:
        """
        Get status of all shifts for a specific date
        """
        try:
            schedule = self.configure_shift_schedule('24_7')
            shift_statuses = []
            
            for i, shift_name in enumerate(schedule['shift_names']):
                cycle_date = f"{shift_date.isoformat()}_shift_{i}"
                status = DailyCycleStatus.query.filter_by(cycle_date=cycle_date).first()
                
                shift_statuses.append({
                    'shift_index': i,
                    'shift_name': shift_name,
                    'closing_time': schedule['closing_times'][i],
                    'status': status.overall_status if status else 'not_started',
                    'opening_status': status.opening_status if status else 'not_started',
                    'closing_status': status.closing_status if status else 'not_started',
                    'accounts_processed': status.accounts_processed if status else 0,
                    'total_closing_balance': status.total_closing_balance if status else 0,
                    'closing_calculated_at': status.closing_calculated_at.isoformat() if status and status.closing_calculated_at else None
                })
            
            return {
                "status": "success",
                "shift_date": shift_date,
                "shifts": shift_statuses,
                "total_shifts": len(shift_statuses)
            }
            
        except Exception as e:
            logger.error(f"Failed to get shift status for {shift_date}: {str(e)}")
            raise
    
    def handle_late_transaction(self, transaction_date: date, account_id: int,
                              transaction_amount: float, transaction_type: str,
                              user_id: str, reason: str, user_name: str = None,
                              user_role: str = None, ip_address: str = None,
                              user_agent: str = None) -> Dict:
        """
        Handle transactions that come in after shift closing
        """
        try:
            # Determine which shift this transaction belongs to
            schedule = self.configure_shift_schedule('24_7')
            transaction_datetime = datetime.combine(transaction_date, datetime.min.time())
            
            # Find the appropriate shift
            target_shift = None
            for i, closing_time_str in enumerate(schedule['closing_times']):
                closing_time = datetime.strptime(closing_time_str, '%H:%M').time()
                closing_datetime = datetime.combine(transaction_date, closing_time)
                
                if transaction_datetime <= closing_datetime:
                    target_shift = i
                    break
            
            if target_shift is None:
                # Transaction is for the last shift of the day
                target_shift = len(schedule['closing_times']) - 1
            
            # Check if the shift is locked
            cycle_date = f"{transaction_date.isoformat()}_shift_{target_shift}"
            daily_balances = DailyBalance.query.filter_by(balance_date=transaction_date).all()
            
            if daily_balances and all(balance.is_locked for balance in daily_balances):
                # Create adjustment entry
                adjustment_result = self.enhanced_service.create_adjustment_entry(
                    original_date=transaction_date,
                    account_id=account_id,
                    adjustment_type='late_entry',
                    reason=f"Late transaction: {reason}",
                    adjustment_amount=transaction_amount,
                    user_id=user_id,
                    user_name=user_name,
                    user_role=user_role,
                    reference_document=f"Late_{transaction_type}_{transaction_date}",
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                return {
                    "status": "adjustment_created",
                    "message": f"Late transaction created as adjustment entry",
                    "adjustment_id": adjustment_result.get('adjustment_id'),
                    "target_shift": target_shift,
                    "shift_name": schedule['shift_names'][target_shift]
                }
            else:
                # Normal transaction processing
                return {
                    "status": "normal_processing",
                    "message": f"Transaction processed normally for shift {target_shift}",
                    "target_shift": target_shift,
                    "shift_name": schedule['shift_names'][target_shift]
                }
                
        except Exception as e:
            logger.error(f"Failed to handle late transaction: {str(e)}")
            raise
    
    def get_shift_summary(self, start_date: date, end_date: date) -> Dict:
        """
        Get summary of all shifts within a date range
        """
        try:
            shift_summaries = []
            current_date = start_date
            
            while current_date <= end_date:
                shift_status = self.get_shift_status(current_date)
                shift_summaries.append({
                    'date': current_date.isoformat(),
                    'shifts': shift_status['shifts']
                })
                current_date += timedelta(days=1)
            
            return {
                "status": "success",
                "start_date": start_date,
                "end_date": end_date,
                "shift_summaries": shift_summaries,
                "total_days": len(shift_summaries)
            }
            
        except Exception as e:
            logger.error(f"Failed to get shift summary: {str(e)}")
            raise
    
    def auto_close_shifts(self, current_time: datetime = None) -> Dict:
        """
        Automatically close shifts based on schedule
        """
        if not current_time:
            current_time = datetime.now()
        
        try:
            # Get current shift info
            shift_info = self.get_current_shift_info(current_time)
            current_shift = shift_info['current_shift']
            
            # Check if it's time to close the current shift
            time_until_closing = shift_info['time_until_closing']
            
            if time_until_closing <= 0:  # Time to close
                # Execute shift closing
                result = self.execute_shift_closing(
                    shift_date=current_time.date(),
                    shift_index=current_shift['index'],
                    user_id='system_automation',
                    user_name='System Automation',
                    user_role='system'
                )
                
                return {
                    "status": "auto_closed",
                    "message": f"Shift {current_shift['name']} auto-closed",
                    "shift_info": current_shift,
                    "closing_result": result
                }
            else:
                return {
                    "status": "not_time",
                    "message": f"Shift {current_shift['name']} not ready to close",
                    "time_until_closing": time_until_closing,
                    "shift_info": current_shift
                }
                
        except Exception as e:
            logger.error(f"Failed to auto-close shifts: {str(e)}")
            raise
