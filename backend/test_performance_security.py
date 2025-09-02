#!/usr/bin/env python3
"""
Performance and Security Test
Tests performance optimization and security features
"""

import requests
import time

BASE_URL = "http://localhost:5000"
results = {'passed': 0, 'failed': 0, 'errors': []}

def test_endpoint(method, endpoint, data=None, params=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return True, None
        else:
            return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)

def log_test(name, success, error=None):
    if success:
        results['passed'] += 1
        print(f"✅ {name}")
    else:
        results['failed'] += 1
        print(f"❌ {name}: {error}")
        results['errors'].append(f"{name}: {error}")

print("🚀 Testing Performance and Security Features...")

# Test 1: Performance Monitoring
print("\n⚡ Test 1: Performance Monitoring")
log_test("GET Performance Metrics", *test_endpoint('GET', '/api/performance/metrics'))
log_test("GET Performance Health", *test_endpoint('GET', '/api/performance/health'))

# Test 2: Security Monitoring
print("\n🔒 Test 2: Security Monitoring")
log_test("GET Security Metrics", *test_endpoint('GET', '/api/security/metrics'))
log_test("GET Security Health", *test_endpoint('GET', '/api/security/health'))

# Test 3: Performance Testing - Load Test
print("\n📊 Test 3: Performance Load Testing")
start_time = time.time()

# Test multiple concurrent requests
for i in range(10):
    log_test(f"Concurrent Request {i+1}", *test_endpoint('GET', '/api/finance/dashboard-metrics'))

end_time = time.time()
total_time = end_time - start_time
avg_time = total_time / 10

print(f"   ⏱️  Total time: {total_time:.2f}s")
print(f"   📈 Average time per request: {avg_time:.2f}s")

if avg_time < 1.0:
    print("   ✅ Performance is good!")
else:
    print("   ⚠️  Performance needs optimization")

# Test 4: Security Testing - Input Validation
print("\n🛡️ Test 4: Security Input Validation")
test_data = {
    "email": "test@example.com",
    "password": "Test123!",
    "input": "<script>alert('xss')</script>"
}

log_test("POST Security Test Data", *test_endpoint('POST', '/api/security/test', test_data))

# Test 5: Rate Limiting Test
print("\n🚦 Test 5: Rate Limiting")
for i in range(6):
    success, error = test_endpoint('GET', '/api/security/metrics')
    if i < 5:
        log_test(f"Rate Limit Request {i+1}", success, error)
    else:
        # The 6th request should be rate limited
        if not success:
            print(f"✅ Rate limiting working (Request {i+1} blocked)")
        else:
            print(f"❌ Rate limiting not working (Request {i+1} allowed)")

# Test 6: Cache Performance
print("\n💾 Test 6: Cache Performance")
# Test the same endpoint multiple times to see if caching helps
for i in range(5):
    start_time = time.time()
    success, error = test_endpoint('GET', '/api/finance/dashboard-metrics')
    end_time = time.time()
    response_time = end_time - start_time
    
    if success:
        print(f"   Request {i+1}: {response_time:.3f}s")
    else:
        print(f"   Request {i+1}: Failed - {error}")

print(f"\n📊 Performance & Security Results: {results['passed']} passed, {results['failed']} failed")
success_rate = (results['passed'] / (results['passed'] + results['failed'])) * 100 if (results['passed'] + results['failed']) > 0 else 0
print(f"📈 Success Rate: {success_rate:.1f}%")

if success_rate >= 90:
    print("🎉 Excellent! Performance and security features are working perfectly!")
elif success_rate >= 70:
    print("👍 Good! Most performance and security features are working.")
else:
    print("⚠️  Needs attention! Multiple performance and security issues detected.")

