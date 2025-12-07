"""
Migration script to add tenant_id column to system_settings table
This enables strict tenant isolation for system settings
"""

import sys
import os
from sqlalchemy import text
from app import create_app, db

def add_tenant_id_to_system_settings():
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Adding 'tenant_id' column to system_settings table...")
            with db.engine.connect() as connection:
                # Check if column exists before adding
                result = connection.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='system_settings' AND column_name='tenant_id'"
                )).fetchone()
                
                if result:
                    print("   ⏭️  'tenant_id' column already exists in system_settings table - skipping")
                else:
                    # Add tenant_id column (nullable, with index for performance)
                    connection.execute(text(
                        "ALTER TABLE system_settings ADD COLUMN tenant_id VARCHAR(50)"
                    ))
                    connection.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_system_settings_tenant_id ON system_settings(tenant_id)"
                    ))
                    connection.commit()
                    print("   ✅ Successfully added 'tenant_id' column to system_settings table")
                    print("   ✅ Created index on tenant_id for performance")
                
                # Update unique constraint to include tenant_id (section should be unique per tenant)
                # First, drop the old unique constraint on section if it exists
                try:
                    connection.execute(text(
                        "ALTER TABLE system_settings DROP CONSTRAINT IF EXISTS system_settings_section_key"
                    ))
                    print("   ✅ Dropped old unique constraint on section")
                except:
                    pass  # Constraint might not exist
                
                # Create new unique constraint: section + tenant_id (NULL tenant_id means global)
                try:
                    connection.execute(text(
                        """
                        CREATE UNIQUE INDEX IF NOT EXISTS unique_section_tenant 
                        ON system_settings(section, tenant_id)
                        WHERE tenant_id IS NOT NULL
                        """
                    ))
                    connection.execute(text(
                        """
                        CREATE UNIQUE INDEX IF NOT EXISTS unique_section_global 
                        ON system_settings(section)
                        WHERE tenant_id IS NULL
                        """
                    ))
                    connection.commit()
                    print("   ✅ Created unique constraints for section + tenant_id")
                except Exception as constraint_err:
                    print(f"   ⚠️  Warning: Could not create unique constraint: {constraint_err}")
                    # Continue - constraint might already exist
                
                return True
        except Exception as e:
            print(f"   ❌ Error adding 'tenant_id' column: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    add_tenant_id_to_system_settings()

