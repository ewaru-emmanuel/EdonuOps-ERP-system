#!/usr/bin/env python3
"""
Clear SQLAlchemy Cache
Forces SQLAlchemy to refresh its metadata cache
"""

import os
import sys
import sqlite3

def clear_sqlalchemy_metadata():
    """Clear SQLAlchemy metadata cache by forcing a refresh"""
    try:
        # Import Flask app and force metadata refresh
        sys.path.append('.')
        from app import app, db
        
        with app.app_context():
            # Force SQLAlchemy to refresh metadata
            db.metadata.clear()
            db.metadata.reflect(bind=db.engine)
            
            # Test the products table
            from modules.inventory.advanced_models import AdvancedProduct
            
            # Force a simple query to test
            try:
                products = AdvancedProduct.query.filter_by(is_active=True).limit(1).all()
                print(f"✅ SQLAlchemy query successful! Found {len(products)} products")
                return True
            except Exception as e:
                print(f"❌ SQLAlchemy query failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to clear SQLAlchemy cache: {e}")
        return False

def verify_database_schema():
    """Verify the database schema directly"""
    try:
        conn = sqlite3.connect('edonuops.db')
        cursor = conn.cursor()
        
        # Check if product_id column exists
        cursor.execute("PRAGMA table_info(advanced_products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'product_id' in columns:
            print("✅ Database has product_id column")
            
            # Test a simple query
            cursor.execute("SELECT COUNT(*) FROM advanced_products WHERE is_active = 1")
            count = cursor.fetchone()[0]
            print(f"✅ Database query successful! Found {count} active products")
            
            conn.close()
            return True
        else:
            print("❌ Database missing product_id column")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Clearing SQLAlchemy Cache")
    print("=" * 40)
    
    # Verify database schema
    db_ok = verify_database_schema()
    
    if db_ok:
        # Clear SQLAlchemy cache
        sqlalchemy_ok = clear_sqlalchemy_metadata()
        
        if sqlalchemy_ok:
            print("\n🎉 SQLAlchemy cache cleared successfully!")
            print("✅ The server should now work with the new product_id field")
        else:
            print("\n⚠️ SQLAlchemy cache clear failed")
    else:
        print("\n❌ Database schema issue detected")

if __name__ == "__main__":
    main()

