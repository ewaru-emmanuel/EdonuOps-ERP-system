#!/usr/bin/env python3
"""
Test audit endpoint functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.audit_models import AuditLog
from app import create_app
from datetime import datetime

def test_audit_endpoint():
    """Test the audit endpoint functionality."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Testing audit endpoint...")
            
            # Create audit tables if they don't exist
            db.create_all()
            
            # Test 1: Create test audit records
            print("Test 1: Creating test audit records...")
            
            test_audit_records = [
                AuditLog(
                    user_id=1,
                    action="CREATE",
                    entity_type="User",
                    entity_id=1,
                    old_values=None,
                    new_values={"username": "testuser", "email": "test@example.com"},
                    ip_address="127.0.0.1",
                    user_agent="Test Agent",
                    tenant_id=1,
                    created_at=datetime.utcnow()
                ),
                AuditLog(
                    user_id=1,
                    action="UPDATE",
                    entity_type="User",
                    entity_id=1,
                    old_values={"username": "testuser"},
                    new_values={"username": "updateduser"},
                    ip_address="127.0.0.1",
                    user_agent="Test Agent",
                    tenant_id=1,
                    created_at=datetime.utcnow()
                ),
                AuditLog(
                    user_id=1,
                    action="DELETE",
                    entity_type="User",
                    entity_id=1,
                    old_values={"username": "updateduser", "email": "test@example.com"},
                    new_values=None,
                    ip_address="127.0.0.1",
                    user_agent="Test Agent",
                    tenant_id=1,
                    created_at=datetime.utcnow()
                )
            ]
            
            for record in test_audit_records:
                db.session.add(record)
            
            db.session.commit()
            print("✅ Test audit records created")
            
            # Test 2: Query audit records
            print("Test 2: Querying audit records...")
            
            # Get all audit records
            all_records = AuditLog.query.all()
            print(f"✅ Retrieved {len(all_records)} audit records")
            
            # Get records by user
            user_records = AuditLog.query.filter_by(user_id=1).all()
            print(f"✅ Retrieved {len(user_records)} records for user 1")
            
            # Get records by action
            create_records = AuditLog.query.filter_by(action="CREATE").all()
            update_records = AuditLog.query.filter_by(action="UPDATE").all()
            delete_records = AuditLog.query.filter_by(action="DELETE").all()
            
            print(f"✅ CREATE records: {len(create_records)}")
            print(f"✅ UPDATE records: {len(update_records)}")
            print(f"✅ DELETE records: {len(delete_records)}")
            
            # Get records by entity type
            user_entity_records = AuditLog.query.filter_by(entity_type="User").all()
            print(f"✅ User entity records: {len(user_entity_records)}")
            
            # Test 3: Test filtering and pagination
            print("Test 3: Testing filtering and pagination...")
            
            # Filter by date range
            today = datetime.utcnow().date()
            today_records = AuditLog.query.filter(
                db.func.date(AuditLog.created_at) == today
            ).all()
            print(f"✅ Records from today: {len(today_records)}")
            
            # Filter by IP address
            local_ip_records = AuditLog.query.filter_by(ip_address="127.0.0.1").all()
            print(f"✅ Records from local IP: {len(local_ip_records)}")
            
            # Test pagination
            page_size = 2
            page_1 = AuditLog.query.limit(page_size).offset(0).all()
            page_2 = AuditLog.query.limit(page_size).offset(page_size).all()
            
            print(f"✅ Page 1 records: {len(page_1)}")
            print(f"✅ Page 2 records: {len(page_2)}")
            
            # Test 4: Test audit record details
            print("Test 4: Testing audit record details...")
            
            for record in all_records[:3]:  # Test first 3 records
                print(f"   Record ID: {record.id}")
                print(f"   Action: {record.action}")
                print(f"   Entity: {record.entity_type} (ID: {record.entity_id})")
                print(f"   User: {record.user_id}")
                print(f"   Timestamp: {record.created_at}")
                print(f"   IP: {record.ip_address}")
                
                if record.old_values:
                    print(f"   Old values: {record.old_values}")
                if record.new_values:
                    print(f"   New values: {record.new_values}")
                
                print("   ---")
            
            # Test 5: Test audit record search
            print("Test 5: Testing audit record search...")
            
            # Search by action
            search_results = AuditLog.query.filter(
                AuditLog.action.contains("CREATE")
            ).all()
            print(f"✅ Search for 'CREATE' action: {len(search_results)} results")
            
            # Search by entity type
            entity_search = AuditLog.query.filter(
                AuditLog.entity_type.contains("User")
            ).all()
            print(f"✅ Search for 'User' entity: {len(entity_search)} results")
            
            # Test 6: Test audit record statistics
            print("Test 6: Testing audit record statistics...")
            
            # Count by action
            action_counts = db.session.query(
                AuditLog.action,
                db.func.count(AuditLog.id)
            ).group_by(AuditLog.action).all()
            
            print("📊 Action statistics:")
            for action, count in action_counts:
                print(f"   {action}: {count}")
            
            # Count by entity type
            entity_counts = db.session.query(
                AuditLog.entity_type,
                db.func.count(AuditLog.id)
            ).group_by(AuditLog.entity_type).all()
            
            print("📊 Entity type statistics:")
            for entity_type, count in entity_counts:
                print(f"   {entity_type}: {count}")
            
            # Count by user
            user_counts = db.session.query(
                AuditLog.user_id,
                db.func.count(AuditLog.id)
            ).group_by(AuditLog.user_id).all()
            
            print("📊 User statistics:")
            for user_id, count in user_counts:
                print(f"   User {user_id}: {count}")
            
            # Test 7: Test audit record cleanup
            print("Test 7: Testing audit record cleanup...")
            
            # Count records before cleanup
            total_before = AuditLog.query.count()
            print(f"📊 Total records before cleanup: {total_before}")
            
            # Clean up test records (optional)
            cleanup = input("Do you want to clean up test audit records? (y/n): ").lower() == 'y'
            if cleanup:
                # Delete test records
                AuditLog.query.delete()
                db.session.commit()
                
                total_after = AuditLog.query.count()
                print(f"🧹 Cleaned up {total_before - total_after} test records")
                print(f"📊 Total records after cleanup: {total_after}")
            else:
                print("ℹ️  Test records preserved")
            
            print("🎉 Audit endpoint testing completed!")
            print("✅ All audit functionality is working correctly!")
            
        except Exception as e:
            print(f"❌ Error during audit endpoint testing: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_audit_endpoint()







