#!/usr/bin/env python3
"""
Automated Daily Process Service
Handles automated daily opening/closing operations for the finance module
Can be run as a scheduled job (cron, celery, etc.)
"""

import os
import sys
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from services.daily_cycle_service import DailyCycleService
from modules.finance.daily_cycle_models import DailyCycleStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_cycle_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedDailyProcess:
    """
    Automated daily process for finance module
    Handles opening balance capture and closing balance calculation
    """
    
    def __init__(self):
        self.app = create_app()
        self.user_id = 'system_automation'
    
    def run_daily_opening_process(self, target_date: date = None) -> Dict:
        """
        Run daily opening balance capture process
        """
        if not target_date:
            target_date = date.today()
        
        logger.info(f"Starting daily opening process for {target_date}")
        
        try:
            with self.app.app_context():
                # Check if opening already captured
                cycle_status = DailyCycleStatus.get_status_for_date(target_date)
                if cycle_status and cycle_status.opening_status == 'completed':
                    logger.info(f"Opening balances already captured for {target_date}")
                    return {
                        "status": "already_completed",
                        "message": f"Opening balances already captured for {target_date}",
                        "date": target_date.isoformat()
                    }
                
                # Execute opening balance capture
                result = DailyCycleService.capture_opening_balances(target_date, self.user_id)
                
                logger.info(f"Opening process completed for {target_date}: {result['message']}")
                return {
                    "status": "success",
                    "message": f"Opening process completed for {target_date}",
                    "date": target_date.isoformat(),
                    "details": result
                }
                
        except Exception as e:
            logger.error(f"Opening process failed for {target_date}: {str(e)}")
            return {
                "status": "error",
                "message": f"Opening process failed for {target_date}",
                "date": target_date.isoformat(),
                "error": str(e)
            }
    
    def run_daily_closing_process(self, target_date: date = None) -> Dict:
        """
        Run daily closing balance calculation process
        """
        if not target_date:
            target_date = date.today()
        
        logger.info(f"Starting daily closing process for {target_date}")
        
        try:
            with self.app.app_context():
                # Check if closing already calculated
                cycle_status = DailyCycleStatus.get_status_for_date(target_date)
                if cycle_status and cycle_status.closing_status == 'completed':
                    logger.info(f"Closing balances already calculated for {target_date}")
                    return {
                        "status": "already_completed",
                        "message": f"Closing balances already calculated for {target_date}",
                        "date": target_date.isoformat()
                    }
                
                # Execute closing balance calculation
                result = DailyCycleService.calculate_closing_balances(target_date, self.user_id)
                
                logger.info(f"Closing process completed for {target_date}: {result['message']}")
                return {
                    "status": "success",
                    "message": f"Closing process completed for {target_date}",
                    "date": target_date.isoformat(),
                    "details": result
                }
                
        except Exception as e:
            logger.error(f"Closing process failed for {target_date}: {str(e)}")
            return {
                "status": "error",
                "message": f"Closing process failed for {target_date}",
                "date": target_date.isoformat(),
                "error": str(e)
            }
    
    def run_full_daily_cycle(self, target_date: date = None) -> Dict:
        """
        Run complete daily cycle (opening + closing)
        """
        if not target_date:
            target_date = date.today()
        
        logger.info(f"Starting full daily cycle for {target_date}")
        
        try:
            with self.app.app_context():
                # Execute full daily cycle
                result = DailyCycleService.execute_full_daily_cycle(target_date, self.user_id)
                
                logger.info(f"Full daily cycle completed for {target_date}: {result['message']}")
                return {
                    "status": "success",
                    "message": f"Full daily cycle completed for {target_date}",
                    "date": target_date.isoformat(),
                    "details": result
                }
                
        except Exception as e:
            logger.error(f"Full daily cycle failed for {target_date}: {str(e)}")
            return {
                "status": "error",
                "message": f"Full daily cycle failed for {target_date}",
                "date": target_date.isoformat(),
                "error": str(e)
            }
    
    def process_pending_cycles(self) -> Dict:
        """
        Process all pending daily cycles
        """
        logger.info("Processing pending daily cycles")
        
        try:
            with self.app.app_context():
                pending_cycles = DailyCycleStatus.get_pending_cycles()
                
                if not pending_cycles:
                    logger.info("No pending cycles found")
                    return {
                        "status": "success",
                        "message": "No pending cycles found",
                        "processed_count": 0
                    }
                
                processed_count = 0
                results = []
                
                for cycle in pending_cycles:
                    try:
                        if cycle.opening_status == 'pending':
                            result = self.run_daily_opening_process(cycle.cycle_date)
                            results.append(result)
                            if result["status"] == "success":
                                processed_count += 1
                        
                        if cycle.closing_status == 'pending' and cycle.opening_status == 'completed':
                            result = self.run_daily_closing_process(cycle.cycle_date)
                            results.append(result)
                            if result["status"] == "success":
                                processed_count += 1
                                
                    except Exception as e:
                        logger.error(f"Failed to process cycle for {cycle.cycle_date}: {str(e)}")
                        results.append({
                            "status": "error",
                            "date": cycle.cycle_date.isoformat(),
                            "error": str(e)
                        })
                
                logger.info(f"Processed {processed_count} pending cycles")
                return {
                    "status": "success",
                    "message": f"Processed {processed_count} pending cycles",
                    "processed_count": processed_count,
                    "results": results
                }
                
        except Exception as e:
            logger.error(f"Failed to process pending cycles: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to process pending cycles",
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict:
        """
        Get overall system status for daily cycles
        """
        try:
            with self.app.app_context():
                latest_status = DailyCycleStatus.get_latest_status()
                pending_cycles = DailyCycleStatus.get_pending_cycles()
                
                return {
                    "status": "success",
                    "latest_cycle": {
                        "date": latest_status.cycle_date.isoformat() if latest_status else None,
                        "overall_status": latest_status.overall_status if latest_status else None,
                        "opening_status": latest_status.opening_status if latest_status else None,
                        "closing_status": latest_status.closing_status if latest_status else None
                    } if latest_status else None,
                    "pending_cycles_count": len(pending_cycles),
                    "pending_dates": [cycle.cycle_date.isoformat() for cycle in pending_cycles]
                }
                
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to get system status",
                "error": str(e)
            }

def main():
    """
    Main function for command-line usage
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Daily Process for Finance Module')
    parser.add_argument('--action', choices=['opening', 'closing', 'full-cycle', 'pending', 'status'], 
                       required=True, help='Action to perform')
    parser.add_argument('--date', help='Target date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse date
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Initialize process
    process = AutomatedDailyProcess()
    
    # Execute action
    if args.action == 'opening':
        result = process.run_daily_opening_process(target_date)
    elif args.action == 'closing':
        result = process.run_daily_closing_process(target_date)
    elif args.action == 'full-cycle':
        result = process.run_full_daily_cycle(target_date)
    elif args.action == 'pending':
        result = process.process_pending_cycles()
    elif args.action == 'status':
        result = process.get_system_status()
    
    # Print result
    print(f"Action: {args.action}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result['status'] == 'error':
        print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    else:
        print("Operation completed successfully")

if __name__ == "__main__":
    main()
