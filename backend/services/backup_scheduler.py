"""
Backup Scheduler - Automated backup scheduling
Can be run as a cron job or as a background service
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.automated_backup_service import backup_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_daily_backup():
    """Run daily full backup"""
    logger.info("🔄 Starting daily backup...")
    backup_info = backup_service.create_backup(backup_type="full")
    
    if backup_info:
        # Verify backup
        verified, error = backup_service.verify_backup(backup_info["backup_id"])
        if verified:
            logger.info(f"✅ Backup verified: {backup_info['backup_id']}")
            
            # Sync to offsite (if configured)
            storage_type = os.getenv('OFFSITE_STORAGE_TYPE', 'local')
            if storage_type != 'none':
                synced, error = backup_service.sync_to_offsite(
                    backup_info["backup_id"],
                    storage_type=storage_type
                )
                if synced:
                    logger.info(f"✅ Backup synced to {storage_type}")
                else:
                    logger.warning(f"⚠️  Offsite sync failed: {error}")
        else:
            logger.error(f"❌ Backup verification failed: {error}")
    else:
        logger.error("❌ Backup creation failed")

def run_hourly_backup():
    """Run hourly incremental backup"""
    logger.info("🔄 Starting hourly incremental backup...")
    backup_info = backup_service.create_backup(backup_type="incremental")
    
    if backup_info:
        verified, error = backup_service.verify_backup(backup_info["backup_id"])
        if verified:
            logger.info(f"✅ Incremental backup verified: {backup_info['backup_id']}")
        else:
            logger.error(f"❌ Incremental backup verification failed: {error}")

def cleanup_old_backups():
    """Clean up old backups"""
    logger.info("🧹 Cleaning up old backups...")
    deleted = backup_service.cleanup_old_backups()
    logger.info(f"✅ Cleaned up {deleted} old backups")

def main():
    """Main scheduler loop"""
    logger.info("🚀 Backup Scheduler started")
    
    # Schedule daily full backup at 2 AM
    schedule.every().day.at("02:00").do(run_daily_backup)
    
    # Schedule hourly incremental backups
    schedule.every().hour.do(run_hourly_backup)
    
    # Schedule cleanup at 3 AM daily
    schedule.every().day.at("03:00").do(cleanup_old_backups)
    
    # Run initial backup on startup
    logger.info("Running initial backup...")
    run_daily_backup()
    
    # Main loop
    logger.info("⏰ Scheduler running. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler stopped")

if __name__ == "__main__":
    main()

