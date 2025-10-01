"""
Migration: Create User Preferences Table
Creates the user_preferences table for storing user-specific module configurations
"""

from app import db
from modules.core.user_preferences_models import UserPreferences

def run_migration():
    """Run the migration to create user preferences table"""
    try:
        print("Creating user_preferences table...")
        
        # Create the table
        UserPreferences.__table__.create(db.engine, checkfirst=True)
        
        print("✓ User preferences table created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating user preferences table: {e}")
        return False

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    
    with app.app_context():
        success = run_migration()
        if success:
            print("Migration completed successfully!")
        else:
            print("Migration failed!")











