#!/usr/bin/env python3
"""
Enterprise Hardening Test Suite
Tests all the final 5% features for Fortune 500 readiness
"""

import requests
import json
import time
import threading
from datetime import datetime
import concurrent.futures

# Test configuration
BASE_URL = "http://localhost:5000"
API_ENDPOINTS = {
    'concurrency': f"{BASE_URL}/api/enterprise/concurrency",
    'recovery': f"{BASE_URL}/api/enterprise/recovery",
    'performance': f"{BASE_URL}/api/enterprise/performance",
    'webhooks': f"{BASE_URL}/api/enterprise/webhooks",
    'api_keys': f"{BASE_URL}/api/enterprise/api-keys",
    'health': f"{BASE_URL}/api/enterprise/health"
}

class EnterpriseHardeningTester:
    """Comprehensive test suite for enterprise hardening features"""
    
    def __init__(self):
        self.test_results = []
        self.api_key = None
    
    def run_all_tests(self):
        """Run all enterprise hardening tests"""
        print("🚀 Starting Enterprise Hardening Test Suite")
        print("=" * 60)
        
        # Test 1: Concurrency & Race Condition Management
        self.test_concurrency_management()
        
        # Test 2: Recovery & Audit System
        self.test_recovery_audit_system()
        
        # Test 3: Performance Optimization
        self.test_performance_optimization()
        
        # Test 4: API Ecosystem & Webhooks
        self.test_api_ecosystem()
        
        # Test 5: Enterprise Health & Monitoring
        self.test_enterprise_health()
        
        # Test 6: Stress Testing
        self.test_stress_scenarios()
        
        # Generate final report
        self.generate_test_report()
    
    def test_concurrency_management(self):
        """Test 1: Concurrency & Race Condition Management"""
        print("\n🔒 Testing Concurrency & Race Condition Management")
        print("-" * 50)
        
        # Test concurrent stock adjustments
        test_name = "Concurrent Stock Adjustments"
        try:
            # Create multiple threads to simulate concurrent access
            def make_stock_adjustment(thread_id):
                adjustment_data = {
                    'item_id': f'ITEM_{thread_id}',
                    'warehouse_id': 'WH001',
                    'quantity': 10,
                    'adjustment_type': 'test',
                    'reason_code': 'test',
                    'user_id': f'user_{thread_id}'
                }
                
                response = requests.post(
                    f"{API_ENDPOINTS['concurrency']}/stock-adjustment",
                    json=adjustment_data,
                    timeout=10
                )
                return response.json()
            
            # Run 10 concurrent adjustments
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_stock_adjustment, i) for i in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # Check results
            successful_adjustments = sum(1 for r in results if r.get('success', False))
            failed_adjustments = len(results) - successful_adjustments
            
            print(f"✓ Concurrent adjustments: {successful_adjustments} successful, {failed_adjustments} failed")
            
            # Test concurrency metrics
            response = requests.get(f"{API_ENDPOINTS['concurrency']}/metrics")
            metrics = response.json()
            
            print(f"✓ Concurrency metrics: {metrics.get('active_locks', 0)} active locks")
            
            self.test_results.append({
                'test': test_name,
                'status': 'PASS' if successful_adjustments > 0 else 'FAIL',
                'details': f"{successful_adjustments} successful adjustments"
            })
            
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
    
    def test_recovery_audit_system(self):
        """Test 2: Recovery & Audit System"""
        print("\n🛡️ Testing Recovery & Audit System")
        print("-" * 50)
        
        # Test creating recovery point
        test_name = "Recovery Point Creation"
        try:
            recovery_data = {
                'description': 'Test recovery point',
                'user_id': 'test_user'
            }
            
            response = requests.post(
                f"{API_ENDPOINTS['recovery']}/create-point",
                json=recovery_data
            )
            result = response.json()
            
            if result.get('success'):
                print(f"✓ Recovery point created: {result.get('recovery_point_id')}")
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"Recovery point ID: {result.get('recovery_point_id')}"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
        
        # Test audit trail
        test_name = "Audit Trail Retrieval"
        try:
            response = requests.get(f"{API_ENDPOINTS['recovery']}/audit-trail")
            result = response.json()
            
            if result.get('success'):
                print(f"✓ Audit trail retrieved: {result.get('total_entries', 0)} entries")
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"{result.get('total_entries', 0)} audit entries"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
        
        # Test system integrity
        test_name = "System Integrity Report"
        try:
            response = requests.get(f"{API_ENDPOINTS['recovery']}/integrity-report")
            result = response.json()
            
            if result.get('success'):
                integrity_report = result.get('integrity_report', {})
                print(f"✓ System integrity: {integrity_report.get('system_health', 'UNKNOWN')}")
                print(f"  - Total transactions: {integrity_report.get('total_transactions', 0)}")
                print(f"  - Active transactions: {integrity_report.get('active_transactions', 0)}")
                
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"System health: {integrity_report.get('system_health', 'UNKNOWN')}"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
    
    def test_performance_optimization(self):
        """Test 3: Performance Optimization"""
        print("\n⚡ Testing Performance Optimization")
        print("-" * 50)
        
        # Test materialized view creation
        test_name = "Materialized View Creation"
        try:
            view_data = {
                'view_name': 'test_inventory_summary',
                'query_data': {'test': True}
            }
            
            response = requests.post(
                f"{API_ENDPOINTS['performance']}/materialized-view",
                json=view_data
            )
            result = response.json()
            
            if result.get('success'):
                print(f"✓ Materialized view created: {result.get('record_count', 0)} records")
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"{result.get('record_count', 0)} records in view"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
        
        # Test optimized valuation query
        test_name = "Optimized Valuation Query"
        try:
            start_time = time.time()
            response = requests.get(f"{API_ENDPOINTS['performance']}/optimized-valuation")
            query_time = time.time() - start_time
            
            result = response.json()
            
            if result.get('success'):
                print(f"✓ Optimized query completed in {query_time:.3f}s")
                print(f"  - Query time: {result.get('query_time', 0):.3f}s")
                print(f"  - Source: {result.get('source', 'unknown')}")
                
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"Query time: {query_time:.3f}s"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
        
        # Test performance metrics
        test_name = "Performance Metrics"
        try:
            response = requests.get(f"{API_ENDPOINTS['performance']}/metrics")
            result = response.json()
            
            if result.get('success'):
                metrics = result.get('performance_metrics', {})
                print(f"✓ Performance metrics retrieved")
                print(f"  - Cache hit rate: {metrics.get('cache_hit_rate_percentage', 0):.1f}%")
                print(f"  - Average query time: {metrics.get('average_query_time_seconds', 0):.3f}s")
                print(f"  - Materialized views: {metrics.get('materialized_views_count', 0)}")
                
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"Cache hit rate: {metrics.get('cache_hit_rate_percentage', 0):.1f}%"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
    
    def test_api_ecosystem(self):
        """Test 4: API Ecosystem & Webhooks"""
        print("\n🌐 Testing API Ecosystem & Webhooks")
        print("-" * 50)
        
        # Test webhook registration
        test_name = "Webhook Registration"
        try:
            webhook_data = {
                'url': 'https://example.com/webhook',
                'events': ['inventory.stock_updated', 'inventory.adjustment_created']
            }
            
            response = requests.post(
                f"{API_ENDPOINTS['webhooks']}/register",
                json=webhook_data
            )
            result = response.json()
            
            if result.get('success'):
                print(f"✓ Webhook registered: {result.get('webhook_id')}")
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"Webhook ID: {result.get('webhook_id')}"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
        
        # Test API key creation
        test_name = "API Key Creation"
        try:
            key_data = {
                'name': 'Test API Key',
                'permissions': ['read', 'write']
            }
            
            response = requests.post(
                f"{API_ENDPOINTS['api_keys']}/create",
                json=key_data
            )
            result = response.json()
            
            if result.get('success'):
                self.api_key = result.get('api_key')
                print(f"✓ API key created: {self.api_key[:20]}...")
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"API key: {self.api_key[:20]}..."
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
        
        # Test API analytics
        test_name = "API Analytics"
        try:
            response = requests.get(f"{API_ENDPOINTS['api_keys'].replace('/api-keys', '')}/analytics")
            result = response.json()
            
            if result.get('success'):
                analytics = result.get('analytics', {})
                print(f"✓ API analytics retrieved")
                print(f"  - Total requests: {analytics.get('total_requests', 0)}")
                print(f"  - Average response time: {analytics.get('average_response_time_ms', 0):.1f}ms")
                print(f"  - Active webhooks: {analytics.get('active_webhooks', 0)}")
                
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"Total requests: {analytics.get('total_requests', 0)}"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
    
    def test_enterprise_health(self):
        """Test 5: Enterprise Health & Monitoring"""
        print("\n🏥 Testing Enterprise Health & Monitoring")
        print("-" * 50)
        
        # Test health status
        test_name = "System Health Status"
        try:
            response = requests.get(f"{API_ENDPOINTS['health']}/status")
            result = response.json()
            
            if result.get('success'):
                health_status = result.get('system_health', 'UNKNOWN')
                issues = result.get('issues', [])
                
                print(f"✓ System health: {health_status}")
                if issues:
                    print(f"  - Issues: {len(issues)} detected")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"    * {issue}")
                else:
                    print(f"  - No issues detected")
                
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"System health: {health_status}"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
        
        # Test alerts
        test_name = "System Alerts"
        try:
            response = requests.get(f"{API_ENDPOINTS['health']}/alerts")
            result = response.json()
            
            if result.get('success'):
                alerts = result.get('alerts', [])
                print(f"✓ System alerts: {len(alerts)} active alerts")
                
                for alert in alerts[:3]:  # Show first 3 alerts
                    print(f"  - {alert.get('type')}: {alert.get('message')}")
                
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'details': f"{len(alerts)} active alerts"
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
    
    def test_stress_scenarios(self):
        """Test 6: Stress Testing Scenarios"""
        print("\n💪 Testing Stress Scenarios")
        print("-" * 50)
        
        # Test high-volume API requests
        test_name = "High-Volume API Requests"
        try:
            def make_request(request_id):
                try:
                    response = requests.get(f"{API_ENDPOINTS['health']}/status", timeout=5)
                    return {'id': request_id, 'success': response.status_code == 200}
                except:
                    return {'id': request_id, 'success': False}
            
            # Make 50 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request, i) for i in range(50)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_requests = sum(1 for r in results if r['success'])
            failed_requests = len(results) - successful_requests
            
            print(f"✓ High-volume test: {successful_requests}/{len(results)} successful")
            print(f"  - Success rate: {(successful_requests/len(results)*100):.1f}%")
            
            self.test_results.append({
                'test': test_name,
                'status': 'PASS' if successful_requests > 40 else 'FAIL',
                'details': f"{successful_requests}/{len(results)} successful ({successful_requests/len(results)*100:.1f}%)"
            })
            
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'details': str(e)
            })
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 ENTERPRISE HARDENING TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = total_tests - passed_tests
        
        print(f"\nOverall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\nDetailed Results:")
        for result in self.test_results:
            status_icon = "✓" if result['status'] == 'PASS' else "✗"
            print(f"  {status_icon} {result['test']}: {result['details']}")
        
        # Enterprise readiness assessment
        print(f"\n🏢 ENTERPRISE READINESS ASSESSMENT:")
        
        if passed_tests >= total_tests * 0.9:  # 90% success rate
            readiness = "EXCELLENT"
            recommendation = "Ready for Fortune 500 deployment"
        elif passed_tests >= total_tests * 0.8:  # 80% success rate
            readiness = "GOOD"
            recommendation = "Ready for enterprise deployment with minor improvements"
        elif passed_tests >= total_tests * 0.7:  # 70% success rate
            readiness = "FAIR"
            recommendation = "Needs improvements before enterprise deployment"
        else:
            readiness = "POOR"
            recommendation = "Significant improvements required"
        
        print(f"  Readiness Level: {readiness}")
        print(f"  Recommendation: {recommendation}")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests*100),
            'readiness_level': readiness,
            'recommendation': recommendation,
            'detailed_results': self.test_results
        }
        
        with open('enterprise_hardening_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: enterprise_hardening_report.json")

if __name__ == "__main__":
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running or not responding")
            print("Please start the backend server first:")
            print("cd backend && python app.py")
            exit(1)
    except:
        print("❌ Cannot connect to backend server")
        print("Please start the backend server first:")
        print("cd backend && python app.py")
        exit(1)
    
    # Run tests
    tester = EnterpriseHardeningTester()
    tester.run_all_tests()
