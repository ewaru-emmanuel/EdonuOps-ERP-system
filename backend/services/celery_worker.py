# Celery Background Task Processor for EdonuOps ERP
from celery import Celery
import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery('edonuops',
                    broker='redis://localhost:6379/1',
                    backend='redis://localhost:6379/2',
                    include=['backend.services.celery_worker'])

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
)

@celery_app.task(bind=True)
def process_large_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process large datasets in background"""
    try:
        total_items = len(data.get('items', []))
        processed = 0
        
        for item in data.get('items', []):
            # Simulate processing
            time.sleep(0.1)
            processed += 1
            
            # Update progress
            progress = (processed / total_items) * 100
            self.update_state(
                state='PROGRESS',
                meta={'current': processed, 'total': total_items, 'progress': progress}
            )
        
        return {'status': 'completed', 'processed': processed}
    except Exception as e:
        logger.error(f"Dataset processing error: {e}")
        raise

@celery_app.task
def generate_report(report_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate reports in background"""
    try:
        # Simulate report generation
        time.sleep(5)
        
        return {
            'status': 'completed',
            'report_type': report_type,
            'generated_at': time.time(),
            'parameters': parameters
        }
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise

@celery_app.task
def sync_external_data(system: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Sync data with external systems"""
    try:
        # Simulate external sync
        time.sleep(3)
        
        return {
            'status': 'completed',
            'system': system,
            'synced_at': time.time(),
            'records_processed': len(data.get('records', []))
        }
    except Exception as e:
        logger.error(f"External sync error: {e}")
        raise

@celery_app.task
def cleanup_old_data(data_type: str, days_old: int) -> Dict[str, Any]:
    """Clean up old data"""
    try:
        # Simulate cleanup
        time.sleep(2)
        
        return {
            'status': 'completed',
            'data_type': data_type,
            'days_old': days_old,
            'cleaned_at': time.time()
        }
    except Exception as e:
        logger.error(f"Data cleanup error: {e}")
        raise

# Task utilities
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status by ID"""
    task = celery_app.AsyncResult(task_id)
    return {
        'task_id': task_id,
        'status': task.status,
        'result': task.result if task.ready() else None
    }

def cancel_task(task_id: str) -> bool:
    """Cancel a running task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return True
    except Exception as e:
        logger.error(f"Task cancellation error: {e}")
        return False
