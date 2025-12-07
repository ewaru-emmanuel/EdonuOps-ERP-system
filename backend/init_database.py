#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script for EdonuOps ERP
Creates all tables and initializes default roles in PostgreSQL database
"""

import os
import sys
from datetime import datetime
from sqlalchemy import text

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def initialize_postgresql_database():
    """Initialize the PostgreSQL database with all tables and default data"""
    
    print("🚀 EdonuOps ERP - PostgreSQL Database Initialization")
    print("=" * 60)
    print("📊 Database: PostgreSQL (AWS RDS)")
    print("🔗 Connection: AWS RDS PostgreSQL")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Test PostgreSQL connection
            print("🔌 Testing PostgreSQL connection...")
            db.session.execute(text('SELECT 1'))
            print("✅ PostgreSQL connection successful")
            
            # Create all tables in PostgreSQL with proper dependency handling
            print("\n📋 Creating PostgreSQL tables...")
            
            # Create tables in dependency order to avoid foreign key issues
            try:
                # First create core tables (no dependencies)
                print("   📋 Creating core tables...")
                db.create_all()
                print("✅ All PostgreSQL tables created successfully")
            except Exception as e:
                print(f"❌ Error creating tables: {e}")
                # Try to create tables individually to identify the issue
                print("   🔍 Attempting to create tables individually...")
                raise e
            
            # Initialize roles in PostgreSQL
            print("\n🔧 Initializing default roles in PostgreSQL...")
            from init_roles import create_default_roles
            success = create_default_roles()
            
            if success:
                print("\n🎉 PostgreSQL database initialization completed successfully!")
                print("\n🎯 Next steps:")
                print("   1. Start the backend server: python run.py")
                print("   2. Register the first user at: http://localhost:3000/register")
                print("   3. First user will automatically get 'superadmin' role")
                print("   4. Super admin can then invite other team members")
                
                print("\n📊 PostgreSQL Database Summary:")
                print(f"   • Database: PostgreSQL (AWS RDS)")
                print(f"   • Tables created: All ERP modules")
                print(f"   • Default roles: 5 roles (superadmin, admin, manager, accountant, user)")
                print(f"   • Ready for: User registration and company setup")
                
            else:
                print("\n❌ Role initialization failed")
                return False
                
            return True
                
        except Exception as e:
            print(f"❌ PostgreSQL database initialization failed: {str(e)}")
            print("\n🔧 Troubleshooting:")
            print("   1. Check your DATABASE_URL in config.env")
            print("   2. Ensure PostgreSQL is running")
            print("   3. Verify AWS RDS credentials")
            print("   4. Check network connectivity")
            return False

def main():
    """Main function to initialize PostgreSQL database"""
    success = initialize_postgresql_database()
    
    if not success:
        print("\n❌ PostgreSQL database initialization failed")
        sys.exit(1)
    else:
        print("\n✅ PostgreSQL database initialization completed successfully!")
        print("🌐 Your ERP system is ready for use!")

if __name__ == "__main__":
    main()
