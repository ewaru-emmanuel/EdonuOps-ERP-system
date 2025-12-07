"""
Script to check if default accounts exist in the database
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
print(f"   URL: {database_url[:50]}...")

try:
    # Create engine
    engine = create_engine(database_url, echo=False)
    
    # Expected default account codes (25 total)
    expected_codes = [
        '1000', '1100', '1200', '1300', '1400', '1500',  # Assets (6)
        '2000', '2100', '2200', '2300',  # Liabilities (4)
        '3000', '3100', '3200',  # Equity (3)
        '4000', '4100',  # Revenue (2)
        '5000', '6000', '6100', '6200', '6300', '6400', '6500', '6600', '6700', '6800'  # Expenses (10)
    ]
    
    with engine.connect() as conn:
        # Check if accounts table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'accounts'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("❌ Table 'accounts' does not exist in the database")
            sys.exit(1)
        
        print("✅ Table 'accounts' exists\n")
        
        # Get all accounts grouped by user_id
        result = conn.execute(text("""
            SELECT 
                user_id,
                COUNT(*) as account_count,
                STRING_AGG(code, ', ' ORDER BY code) as codes
            FROM accounts
            GROUP BY user_id
            ORDER BY user_id;
        """))
        
        users_data = result.fetchall()
        
        if not users_data:
            print("⚠️  No accounts found in the database for any user")
            print("\n📋 Expected 25 default accounts per user:")
            for code in expected_codes:
                print(f"   - {code}")
            sys.exit(0)
        
        print(f"📊 Found accounts for {len(users_data)} user(s):\n")
        
        # Check each user
        for user_id, account_count, codes in users_data:
            print(f"👤 User ID: {user_id}")
            print(f"   Total accounts: {account_count}")
            
            # Get account codes for this user
            result = conn.execute(text("""
                SELECT code, name, type, is_active
                FROM accounts
                WHERE user_id = :user_id
                ORDER BY code;
            """), {"user_id": user_id})
            
            user_accounts = result.fetchall()
            user_codes = [acc[0] for acc in user_accounts]
            
            # Check which default accounts are missing
            missing_codes = [code for code in expected_codes if code not in user_codes]
            extra_codes = [code for code in user_codes if code not in expected_codes]
            
            print(f"   Default accounts present: {len(user_codes) - len(extra_codes)}/{len(expected_codes)}")
            
            if missing_codes:
                print(f"   ⚠️  Missing {len(missing_codes)} default account(s):")
                for code in missing_codes:
                    print(f"      - {code}")
            
            if extra_codes:
                print(f"   ℹ️  Extra {len(extra_codes)} non-default account(s):")
                for code in extra_codes[:10]:  # Show first 10
                    acc = next((a for a in user_accounts if a[0] == code), None)
                    if acc:
                        print(f"      - {code}: {acc[1]} ({acc[2]})")
                if len(extra_codes) > 10:
                    print(f"      ... and {len(extra_codes) - 10} more")
            
            # Show all accounts for this user
            print(f"\n   📋 All accounts for user {user_id}:")
            for code, name, acc_type, is_active in user_accounts:
                status = "✅" if code in expected_codes else "📝"
                active_status = "Active" if is_active else "Inactive"
                print(f"      {status} {code}: {name} ({acc_type}) - {active_status}")
            
            print()
        
        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY:")
        print("="*60)
        for user_id, account_count, codes in users_data:
            user_codes = codes.split(', ') if codes else []
            missing = [c for c in expected_codes if c not in user_codes]
            print(f"User {user_id}: {account_count} accounts, {len(missing)} missing default accounts")
        
except Exception as e:
    print(f"❌ Error querying database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


