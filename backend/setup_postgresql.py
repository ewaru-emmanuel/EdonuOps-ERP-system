#!/usr/bin/env python3
"""
Quick PostgreSQL Setup Guide
Interactive script to help set up PostgreSQL for EdonuOps
"""

import os
import sys
from dotenv import load_dotenv

def print_banner():
    """Print setup banner"""
    print("🚀 EdonuOps PostgreSQL Setup")
    print("=" * 40)
    print("This script will help you migrate from SQLite to PostgreSQL")
    print("for production-ready enterprise deployment.")
    print()

def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔧 Checking prerequisites...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your database configuration.")
        print("See env.example for reference.")
        return False
    
    # Check if psycopg2 is installed
    try:
        import psycopg2
        print("✅ psycopg2-binary is installed")
    except ImportError:
        print("❌ psycopg2-binary not installed")
        print("Run: pip install psycopg2-binary")
        return False
    
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not set in .env file")
        print("Please set DATABASE_URL=postgresql://username:password@host:port/database")
        return False
    
    if not database_url.startswith('postgresql://'):
        print("❌ DATABASE_URL should start with 'postgresql://'")
        return False
    
    print("✅ DATABASE_URL is configured")
    return True

def show_aws_setup_guide():
    """Show AWS RDS setup guide"""
    print("\n📋 AWS RDS PostgreSQL Setup Guide")
    print("=" * 40)
    print("1. Go to AWS RDS Console")
    print("2. Click 'Create database'")
    print("3. Choose 'Standard create'")
    print("4. Engine: PostgreSQL")
    print("5. Template: Free tier")
    print("6. Settings:")
    print("   - DB instance identifier: edonuops-erp")
    print("   - Master username: edonuops")
    print("   - Master password: [your-secure-password]")
    print("7. Instance configuration:")
    print("   - Instance: db.t3.micro (free tier)")
    print("   - Storage: 20 GB")
    print("8. Connectivity:")
    print("   - Public access: Yes")
    print("   - VPC security group: Create new")
    print("   - Database port: 5432")
    print("9. Database authentication: Password authentication")
    print("10. Click 'Create database'")
    print()
    print("After creation, get the endpoint and update your .env file:")
    print("DATABASE_URL=postgresql://edonuops:password@your-endpoint:5432/edonuops_erp")

def run_migration():
    """Run the migration process"""
    print("\n🔄 Running migration...")
    
    try:
        # Import and run migration
        from migrate_to_postgresql import SQLiteToPostgreSQLMigrator
        
        migrator = SQLiteToPostgreSQLMigrator()
        success = migrator.run_migration()
        
        if success:
            print("\n🎉 Migration completed successfully!")
            return True
        else:
            print("\n❌ Migration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def test_setup():
    """Test the PostgreSQL setup"""
    print("\n🧪 Testing PostgreSQL setup...")
    
    try:
        from test_postgresql import PostgreSQLTester
        
        tester = PostgreSQLTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 All tests passed!")
            return True
        else:
            print("\n⚠️ Some tests failed. Check the details above.")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def show_next_steps():
    """Show next steps after setup"""
    print("\n🎯 Next Steps")
    print("=" * 40)
    print("1. ✅ PostgreSQL is now configured")
    print("2. ✅ Data has been migrated")
    print("3. ✅ All tests are passing")
    print()
    print("🚀 Start your application:")
    print("   python run.py")
    print()
    print("📊 Monitor performance:")
    print("   - Check AWS RDS metrics")
    print("   - Monitor application logs")
    print("   - Test with multiple users")
    print()
    print("🔧 Production considerations:")
    print("   - Enable Multi-AZ for high availability")
    print("   - Set up automated backups")
    print("   - Configure monitoring alerts")
    print("   - Use connection pooling")
    print()
    print("🎉 Your application is now ready for enterprise deployment!")

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return
    
    # Show AWS setup guide
    show_aws_setup_guide()
    
    # Ask user if they want to proceed
    print("\n" + "=" * 40)
    response = input("Have you set up AWS RDS PostgreSQL? (y/n): ").lower()
    
    if response != 'y':
        print("Please set up AWS RDS PostgreSQL first, then run this script again.")
        return
    
    # Run migration
    if not run_migration():
        print("Migration failed. Please check the errors above.")
        return
    
    # Test setup
    if not test_setup():
        print("Testing failed. Please check the errors above.")
        return
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()


