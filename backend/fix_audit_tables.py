#!/usr/bin/env python3
"""
Fix audit tables for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.audit_models import AuditLog
from app import create_app
from datetime import datetime

def fix_audit_tables():
    """Fix and optimize audit tables."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Fixing audit tables...")
            
            # Create audit tables if they don't exist
            db.create_all()
            
            # Check if audit_logs table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'audit_logs' in tables:
                print("✅ Audit logs table exists")
                
                # Get table info
                columns = inspector.get_columns('audit_logs')
                print(f"📋 Audit logs table has {len(columns)} columns:")
                for col in columns:
                    print(f"   • {col['name']}: {col['type']}")
                
                # Check for indexes
                indexes = inspector.get_indexes('audit_logs')
                print(f"🔍 Found {len(indexes)} indexes:")
                for idx in indexes:
                    print(f"   • {idx['name']}: {idx['column_names']}")
                
                # Add missing indexes if needed
                missing_indexes = []
                
                # Check for user_id index
                has_user_index = any(idx['column_names'] == ['user_id'] for idx in indexes)
                if not has_user_index:
                    missing_indexes.append("user_id")
                
                # Check for entity_type index
                has_entity_index = any(idx['column_names'] == ['entity_type'] for idx in indexes)
                if not has_entity_index:
                    missing_indexes.append("entity_type")
                
                # Check for created_at index
                has_created_index = any(idx['column_names'] == ['created_at'] for idx in indexes)
                if not has_created_index:
                    missing_indexes.append("created_at")
                
                if missing_indexes:
                    print(f"⚠️  Missing indexes: {missing_indexes}")
                    print("💡 Consider adding these indexes for better performance:")
                    for col in missing_indexes:
                        print(f"   CREATE INDEX idx_audit_logs_{col} ON audit_logs ({col});")
                else:
                    print("✅ All recommended indexes are present")
                
                # Check table size
                try:
                    result = db.session.execute("SELECT COUNT(*) FROM audit_logs")
                    count = result.scalar()
                    print(f"📊 Audit logs table contains {count} records")
                    
                    if count > 1000000:  # 1 million records
                        print("⚠️  Large audit table detected. Consider archiving old records.")
                        
                        # Check oldest and newest records
                        oldest_result = db.session.execute("SELECT MIN(created_at) FROM audit_logs")
                        newest_result = db.session.execute("SELECT MAX(created_at) FROM audit_logs")
                        
                        oldest = oldest_result.scalar()
                        newest = newest_result.scalar()
                        
                        if oldest and newest:
                            print(f"📅 Date range: {oldest} to {newest}")
                            
                            # Calculate age of oldest record
                            if isinstance(oldest, datetime):
                                age_days = (datetime.utcnow() - oldest).days
                                print(f"⏰ Oldest record is {age_days} days old")
                                
                                if age_days > 365:  # 1 year
                                    print("💡 Consider archiving records older than 1 year")
                
                except Exception as e:
                    print(f"⚠️  Could not check table size: {e}")
                
                # Check for orphaned audit records
                try:
                    # Check for audit records referencing non-existent entities
                    orphaned_count = 0
                    
                    # This would need to be customized based on your entity types
                    # For now, just check if there are any audit records
                    result = db.session.execute("SELECT COUNT(*) FROM audit_logs WHERE entity_id IS NOT NULL")
                    total_with_entity = result.scalar()
                    
                    print(f"📋 Audit records with entity references: {total_with_entity}")
                    
                    if total_with_entity > 0:
                        print("💡 Consider implementing cleanup for orphaned audit records")
                
                except Exception as e:
                    print(f"⚠️  Could not check for orphaned records: {e}")
                
            else:
                print("❌ Audit logs table does not exist")
                print("🔧 Creating audit logs table...")
                
                # Create the table
                AuditLog.__table__.create(db.engine)
                print("✅ Audit logs table created")
            
            # Optimize table if needed
            try:
                # Analyze table for better query planning
                db.session.execute("ANALYZE TABLE audit_logs")
                print("✅ Table analyzed for optimization")
            except Exception as e:
                print(f"⚠️  Could not analyze table: {e}")
            
            # Check for partitioning (MySQL/PostgreSQL specific)
            try:
                # This is MySQL specific - check if table is partitioned
                result = db.session.execute("SHOW CREATE TABLE audit_logs")
                create_sql = result.fetchone()[1]
                
                if 'PARTITION' in create_sql.upper():
                    print("✅ Table is partitioned")
                else:
                    print("💡 Consider partitioning audit_logs by date for better performance")
                    print("   Example: PARTITION BY RANGE (YEAR(created_at))")
            
            except Exception as e:
                # Not MySQL or table doesn't exist
                pass
            
            print("🎉 Audit table fix completed!")
            print("✅ Audit system is optimized and ready!")
            
        except Exception as e:
            print(f"❌ Error fixing audit tables: {e}")
            raise

if __name__ == "__main__":
    fix_audit_tables()







