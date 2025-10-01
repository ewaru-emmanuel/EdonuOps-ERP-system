import logging
from datetime import datetime
from app import db
from sqlalchemy import JSON
from typing import Dict, Optional, List  # Added List import here
from enum import Enum

class AuditAction(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    POST = "POST"
    RECONCILE = "RECONCILE"

# AuditLog model moved to modules/core/audit_models.py to avoid conflicts

class AuditLogger:
    @staticmethod
    def log(
        user_id: str,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        request=None
    ) -> None:
        try:
            log = AuditLog(
                user_id=user_id,
                action=action.value,
                entity_type=entity_type,
                entity_id=str(entity_id),
                old_values=old_values,
                new_values=new_values
            )
            
            if request:
                log.ip_address = request.remote_addr
                log.user_agent = request.headers.get('User-Agent')
            
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Audit logging failed: {str(e)}")

    @staticmethod
    def get_entity_changes(entity_type: str, entity_id: str) -> List[Dict]:
        return AuditLog.query.filter_by(
            entity_type=entity_type,
            entity_id=str(entity_id)
        ).order_by(AuditLog.timestamp.desc()).all()