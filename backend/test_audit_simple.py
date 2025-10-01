#!/usr/bin/env python3
"""
Simple audit system test.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.audit_models import AuditLog
from app import create_app
from datetime import datetime

def test_audit_simple():
    """Simple test of the audit system."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Simple audit system test...")
            
            # Create tables
            db.create_all()
            
            # Create a simple audit record
            audit_record = AuditLog(
                user_id=1,
                action="TEST",
                entity_type="TestEntity",
                entity_id=1,
                old_values=None,
                new_values={"test": "data"},
                ip_address="127.0.0.1",
                user_agent="Test Agent",
                tenant_id=1,
                created_at=datetime.utcnow()
            )
            
            db.session.add(audit_record)
            db.session.commit()
            
            print("✅ Audit record created successfully")
            
            # Retrieve the record
            retrieved_record = AuditLog.query.first()
            if retrieved_record:
                print(f"✅ Audit record retrieved: {retrieved_record.action}")
                print(f"   Entity: {retrieved_record.entity_type}")
                print(f"   User: {retrieved_record.user_id}")
                print(f"   Timestamp: {retrieved_record.created_at}")
            else:
                print("❌ Could not retrieve audit record")
            
            # Clean up
            db.session.delete(audit_record)
            db.session.commit()
            
            print("✅ Audit record cleaned up")
            print("🎉 Simple audit test completed!")
            
        except Exception as e:
            print(f"❌ Error in simple audit test: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_audit_simple()







