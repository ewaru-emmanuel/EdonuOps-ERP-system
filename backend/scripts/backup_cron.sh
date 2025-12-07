#!/bin/bash
# Cron script for automated backups
# Add to crontab: 0 2 * * * /path/to/backup_cron.sh

cd /path/to/backend
source venv/bin/activate  # If using virtual environment
python -m services.backup_scheduler




