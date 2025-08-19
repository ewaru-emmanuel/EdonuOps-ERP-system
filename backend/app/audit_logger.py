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

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # E.g., "journal_entry"
    entity_id = db.Column(db.String(50), nullable=False)
    old_values = db.Column(JSON)
    new_values = db.Column(JSON)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))

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