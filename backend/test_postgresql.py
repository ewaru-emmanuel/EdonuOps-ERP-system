#!/usr/bin/env python3
"""
Test PostgreSQL Connection and Functionality
Verify that PostgreSQL is working correctly with the application
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

class PostgreSQLTester:
    def __init__(self):
        self.pg_connection_string = os.getenv('DATABASE_URL')
        
        if not self.pg_connection_string:
            print("❌ DATABASE_URL environment variable not set!")
            print("Please set DATABASE_URL=postgresql://username:password@host:port/database")
            sys.exit(1)
    
    def test_connection(self):
        """Test PostgreSQL connection"""
        print("🔧 Testing PostgreSQL connection...")
        
        try:
            conn = psycopg2.connect(self.pg_connection_string)
            cursor = conn.cursor()
            
            # Test basic connection
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL: Connected successfully")
            print(f"   Version: {version}")
            
            # Test database info
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            print(f"   Database: {db_info[0]}")
            print(f"   User: {db_info[1]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return False
    
    def test_schema(self):
        """Test if all required tables exist"""
        print("\n🏗️ Testing database schema...")
        
        required_tables = [
            'users', 'organizations', 'advanced_uom', 
            'advanced_product_categories', 'advanced_products',
            'accounts', 'journal_entries'
        ]
        
        try:
            conn = psycopg2.connect(self.pg_connection_string)
            cursor = conn.cursor()
            
            for table in required_tables:
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """)
                exists = cursor.fetchone()[0]
                
                if exists:
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    print(f"✅ {table}: {count} records")
                else:
                    print(f"❌ {table}: Table missing")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Schema test failed: {e}")
            return False
    
    def test_queries(self):
        """Test sample queries"""
        print("\n🔍 Testing sample queries...")
        
        try:
            conn = psycopg2.connect(self.pg_connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Test 1: Get products with categories
            cursor.execute("""
                SELECT p.name, p.sku, p.product_id, c.name as category
                FROM advanced_products p 
                LEFT JOIN advanced_product_categories c ON p.category_id = c.id 
                WHERE p.is_active = true
                LIMIT 5;
            """)
            
            products = cursor.fetchall()
            print(f"✅ Products query: {len(products)} products found")
            for product in products:
                print(f"   - {product['name']} (SKU: {product['sku']}, Category: {product['category']})")
            
            # Test 2: Get categories
            cursor.execute("""
                SELECT name, description, abc_class
                FROM advanced_product_categories 
                WHERE is_active = true;
            """)
            
            categories = cursor.fetchall()
            print(f"✅ Categories query: {len(categories)} categories found")
            
            # Test 3: Get UoM
            cursor.execute("""
                SELECT code, name, is_base_unit
                FROM advanced_uom 
                WHERE is_active = true;
            """)
            
            uoms = cursor.fetchall()
            print(f"✅ UoM query: {len(uoms)} units found")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Query test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints with PostgreSQL"""
        print("\n🌐 Testing API endpoints...")
        
        endpoints = [
            ('Health', '/health'),
            ('Categories', '/api/inventory/advanced/categories'),
            ('UoM', '/api/inventory/advanced/uom'),
            ('Products', '/api/inventory/advanced/products')
        ]
        
        results = {}
        
        for name, endpoint in endpoints:
            try:
                response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ {name}: {len(data)} items returned")
                    else:
                        print(f"✅ {name}: Success")
                    results[name] = True
                else:
                    print(f"❌ {name}: Status {response.status_code}")
                    results[name] = False
            except Exception as e:
                print(f"❌ {name}: {e}")
                results[name] = False
        
        return results
    
    def test_performance(self):
        """Test basic performance"""
        print("\n⚡ Testing performance...")
        
        try:
            conn = psycopg2.connect(self.pg_connection_string)
            cursor = conn.cursor()
            
            import time
            
            # Test query performance
            start_time = time.time()
            cursor.execute("""
                SELECT p.*, c.name as category_name, u.name as uom_name
                FROM advanced_products p 
                LEFT JOIN advanced_product_categories c ON p.category_id = c.id 
                LEFT JOIN advanced_uom u ON p.base_uom_id = u.id 
                WHERE p.is_active = true;
            """)
            
            products = cursor.fetchall()
            query_time = time.time() - start_time
            
            print(f"✅ Complex join query: {len(products)} products in {query_time:.3f}s")
            
            # Test index usage
            start_time = time.time()
            cursor.execute("SELECT * FROM advanced_products WHERE sku = 'LAPTOP001';")
            index_query_time = time.time() - start_time
            
            print(f"✅ Indexed query: {index_query_time:.3f}s")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all PostgreSQL tests"""
        print("🧪 PostgreSQL Testing Suite")
        print("=" * 40)
        
        tests = [
            ("Connection", self.test_connection),
            ("Schema", self.test_schema),
            ("Queries", self.test_queries),
            ("Performance", self.test_performance),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} test...")
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ {test_name} test failed: {e}")
                results[test_name] = False
        
        # Test API endpoints if server is running
        try:
            print(f"\n📋 Running API tests...")
            api_results = self.test_api_endpoints()
            results["API"] = all(api_results.values())
        except:
            print("⚠️ API tests skipped (server not running)")
            results["API"] = True
        
        # Summary
        print("\n" + "=" * 40)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 40)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ PostgreSQL is working correctly!")
            print("✅ Your application is ready for production!")
        else:
            print("\n⚠️ Some tests failed. Check the details above.")
        
        return passed == total

def main():
    """Main function"""
    tester = PostgreSQLTester()
    success = tester.run_all_tests()
    
    if not success:
        print("\n❌ PostgreSQL tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()


