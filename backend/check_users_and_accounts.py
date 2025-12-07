"""
Script to check users and their accounts in the database
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('config.env')

# Get database URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not found in config.env")
    sys.exit(1)

print(f"🔗 Connecting to database...")

try:
    # Create engine
    engine = create_engine(database_url, echo=False)
    
    with engine.connect() as conn:
        # Check if users table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """))
        users_table_exists = result.scalar()
        
        if users_table_exists:
            # Get all users
            result = conn.execute(text("""
                SELECT id, email, username, created_at
                FROM users
                ORDER BY id;
            """))
            users = result.fetchall()
            
            if users:
                print(f"\n👥 Found {len(users)} user(s) in database:")
                for user_id, email, username, created_at in users:
                    print(f"   User ID: {user_id}, Email: {email}, Username: {username}")
            else:
                print("\n⚠️  No users found in database")
        else:
            print("\n⚠️  Table 'users' does not exist")
        
        # Check accounts table
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'accounts'
            );
        """))
        accounts_table_exists = result.scalar()
        
        if accounts_table_exists:
            # Get total account count
            result = conn.execute(text("""
                SELECT COUNT(*) FROM accounts;
            """))
            total_accounts = result.scalar()
            
            print(f"\n📊 Accounts table exists")
            print(f"   Total accounts: {total_accounts}")
            
            if total_accounts > 0:
                # Get accounts by user
                result = conn.execute(text("""
                    SELECT 
                        user_id,
                        COUNT(*) as count,
                        STRING_AGG(code || ':' || name, ', ' ORDER BY code) as account_list
                    FROM accounts
                    GROUP BY user_id
                    ORDER BY user_id;
                """))
                
                accounts_by_user = result.fetchall()
                print(f"\n   Accounts by user:")
                for user_id, count, account_list in accounts_by_user:
                    print(f"      User {user_id}: {count} accounts")
                    if account_list:
                        accounts = account_list.split(', ')
                        for acc in accounts[:5]:  # Show first 5
                            print(f"         - {acc}")
                        if len(accounts) > 5:
                            print(f"         ... and {len(accounts) - 5} more")
            else:
                print("   ⚠️  No accounts found in database")
        else:
            print("\n⚠️  Table 'accounts' does not exist")
        
        # Check for user_id 28 specifically (from the logs)
        if users_table_exists:
            result = conn.execute(text("""
                SELECT id, email, username FROM users WHERE id = 28;
            """))
            user_28 = result.fetchone()
            
            if user_28:
                print(f"\n🔍 Checking user 28 specifically:")
                print(f"   User ID: {user_28[0]}, Email: {user_28[1]}, Username: {user_28[2]}")
                
                if accounts_table_exists:
                    result = conn.execute(text("""
                        SELECT code, name, type, is_active
                        FROM accounts
                        WHERE user_id = 28
                        ORDER BY code;
                    """))
                    user_28_accounts = result.fetchall()
                    
                    if user_28_accounts:
                        print(f"   Found {len(user_28_accounts)} accounts for user 28:")
                        for code, name, acc_type, is_active in user_28_accounts:
                            status = "✅" if is_active else "❌"
                            print(f"      {status} {code}: {name} ({acc_type})")
                    else:
                        print(f"   ⚠️  No accounts found for user 28")
            else:
                print(f"\n⚠️  User ID 28 not found in database")
        
except Exception as e:
    print(f"❌ Error querying database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


