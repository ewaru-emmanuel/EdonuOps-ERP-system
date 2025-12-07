"""
Migration script to add user_id column to system_settings table
This enables hybrid approach: store user_id in DB, lookup by tenant_id
"""

import sys
import os
from sqlalchemy import text
from app import create_app, db

def add_user_id_to_system_settings():
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Adding 'user_id' column to system_settings table for hybrid approach...")
            with db.engine.connect() as connection:
                # Check if column exists before adding
                result = connection.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='system_settings' AND column_name='user_id'"
                )).fetchone()
                
                if result:
                    print("   ⏭️  'user_id' column already exists in system_settings table - skipping")
                else:
                    # Add user_id column (nullable for backward compatibility, with foreign key)
                    connection.execute(text(
                        "ALTER TABLE system_settings ADD COLUMN user_id INTEGER REFERENCES users(id)"
                    ))
                    connection.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_system_settings_user_id ON system_settings(user_id)"
                    ))
                    connection.commit()
                    print("   ✅ Successfully added 'user_id' column to system_settings table")
                    print("   ✅ Created index on user_id for performance")
                    print("   ✅ Added foreign key constraint to users table")
                
                # Note: We keep tenant_id column for now (may be used elsewhere)
                # But for settings, we use hybrid approach: user_id in DB, tenant_id for lookup
                
                return True
        except Exception as e:
            print(f"   ❌ Error adding 'user_id' column: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    add_user_id_to_system_settings()

