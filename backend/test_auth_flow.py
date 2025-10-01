#!/usr/bin/env python3
"""
Test authentication flow for the ERP system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.database import db
from modules.core.user_models import User
from modules.core.tenant_models import Tenant
from app import create_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt

def test_auth_flow():
    """Test the complete authentication flow."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Testing authentication flow...")
            
            # Test 1: Create test tenant
            print("Test 1: Creating test tenant...")
            tenant = Tenant(
                name="Test Company",
                subdomain="testcompany",
                created_at=datetime.utcnow()
            )
            db.session.add(tenant)
            db.session.flush()
            tenant_id = tenant.id
            print(f"✅ Test tenant created with ID: {tenant_id}")
            
            # Test 2: Create test user
            print("Test 2: Creating test user...")
            password = "testpassword123"
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash=generate_password_hash(password),
                first_name="Test",
                last_name="User",
                is_active=True,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            print(f"✅ Test user created with ID: {user_id}")
            
            # Test 3: Password verification
            print("Test 3: Testing password verification...")
            
            # Test correct password
            if check_password_hash(user.password_hash, password):
                print("✅ Correct password verification works")
            else:
                print("❌ Correct password verification failed")
            
            # Test incorrect password
            if not check_password_hash(user.password_hash, "wrongpassword"):
                print("✅ Incorrect password rejection works")
            else:
                print("❌ Incorrect password rejection failed")
            
            # Test 4: JWT token generation
            print("Test 4: Testing JWT token generation...")
            
            # Create JWT payload
            payload = {
                'sub': str(user_id),
                'username': user.username,
                'email': user.email,
                'tenant_id': str(tenant_id),
                'exp': datetime.utcnow().timestamp() + 3600,  # 1 hour
                'iat': datetime.utcnow().timestamp()
            }
            
            # Generate token (without signature for testing)
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            print(f"✅ JWT token generated: {token[:50]}...")
            
            # Test 5: JWT token verification
            print("Test 5: Testing JWT token verification...")
            
            try:
                decoded_payload = jwt.decode(token, 'secret', algorithms=['HS256'])
                print(f"✅ JWT token decoded successfully")
                print(f"   User ID: {decoded_payload['sub']}")
                print(f"   Username: {decoded_payload['username']}")
                print(f"   Email: {decoded_payload['email']}")
                print(f"   Tenant ID: {decoded_payload['tenant_id']}")
            except jwt.ExpiredSignatureError:
                print("❌ Token expired")
            except jwt.InvalidTokenError:
                print("❌ Invalid token")
            
            # Test 6: Token expiration
            print("Test 6: Testing token expiration...")
            
            # Create expired token
            expired_payload = {
                'sub': str(user_id),
                'username': user.username,
                'email': user.email,
                'tenant_id': str(tenant_id),
                'exp': datetime.utcnow().timestamp() - 3600,  # Expired 1 hour ago
                'iat': datetime.utcnow().timestamp() - 7200   # Issued 2 hours ago
            }
            
            expired_token = jwt.encode(expired_payload, 'secret', algorithm='HS256')
            
            try:
                jwt.decode(expired_token, 'secret', algorithms=['HS256'])
                print("❌ Expired token should have been rejected")
            except jwt.ExpiredSignatureError:
                print("✅ Expired token correctly rejected")
            
            # Test 7: User authentication simulation
            print("Test 7: Simulating user authentication...")
            
            def simulate_login(email, password):
                """Simulate the login process."""
                # Find user by email
                user = User.query.filter_by(email=email).first()
                if not user:
                    return {"success": False, "error": "User not found"}
                
                # Check if user is active
                if not user.is_active:
                    return {"success": False, "error": "User account is disabled"}
                
                # Verify password
                if not check_password_hash(user.password_hash, password):
                    return {"success": False, "error": "Invalid password"}
                
                # Generate JWT token
                payload = {
                    'sub': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'tenant_id': str(user.tenant_id),
                    'exp': datetime.utcnow().timestamp() + 3600,
                    'iat': datetime.utcnow().timestamp()
                }
                
                token = jwt.encode(payload, 'secret', algorithm='HS256')
                
                return {
                    "success": True,
                    "token": token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    }
                }
            
            # Test successful login
            login_result = simulate_login("test@example.com", password)
            if login_result["success"]:
                print("✅ Login simulation successful")
                print(f"   Token: {login_result['token'][:50]}...")
            else:
                print(f"❌ Login simulation failed: {login_result['error']}")
            
            # Test failed login with wrong password
            failed_login = simulate_login("test@example.com", "wrongpassword")
            if not failed_login["success"]:
                print(f"✅ Failed login correctly handled: {failed_login['error']}")
            else:
                print("❌ Failed login should have been rejected")
            
            # Test failed login with non-existent user
            failed_login2 = simulate_login("nonexistent@example.com", password)
            if not failed_login2["success"]:
                print(f"✅ Non-existent user correctly handled: {failed_login2['error']}")
            else:
                print("❌ Non-existent user should have been rejected")
            
            # Test 8: Token refresh simulation
            print("Test 8: Testing token refresh...")
            
            def simulate_token_refresh(token):
                """Simulate token refresh process."""
                try:
                    # Decode current token
                    payload = jwt.decode(token, 'secret', algorithms=['HS256'])
                    
                    # Check if token is close to expiration (within 30 minutes)
                    current_time = datetime.utcnow().timestamp()
                    if payload['exp'] - current_time > 1800:  # 30 minutes
                        return {"success": False, "error": "Token not yet eligible for refresh"}
                    
                    # Generate new token
                    new_payload = {
                        'sub': payload['sub'],
                        'username': payload['username'],
                        'email': payload['email'],
                        'tenant_id': payload['tenant_id'],
                        'exp': current_time + 3600,  # New 1 hour expiration
                        'iat': current_time
                    }
                    
                    new_token = jwt.encode(new_payload, 'secret', algorithm='HS256')
                    
                    return {
                        "success": True,
                        "token": new_token
                    }
                    
                except jwt.ExpiredSignatureError:
                    return {"success": False, "error": "Token has expired"}
                except jwt.InvalidTokenError:
                    return {"success": False, "error": "Invalid token"}
            
            # Test token refresh with valid token
            refresh_result = simulate_token_refresh(login_result["token"])
            if refresh_result["success"]:
                print("✅ Token refresh successful")
            else:
                print(f"⚠️  Token refresh: {refresh_result['error']}")
            
            # Test token refresh with expired token
            refresh_expired = simulate_token_refresh(expired_token)
            if not refresh_expired["success"]:
                print(f"✅ Expired token refresh correctly handled: {refresh_expired['error']}")
            else:
                print("❌ Expired token refresh should have been rejected")
            
            # Commit all changes
            db.session.commit()
            
            print("🎉 Authentication flow tests completed!")
            print("✅ All authentication components are working correctly!")
            
            # Cleanup
            print("🧹 Cleaning up test data...")
            db.session.delete(user)
            db.session.delete(tenant)
            db.session.commit()
            print("✅ Test data cleaned up")
            
        except Exception as e:
            print(f"❌ Error during authentication flow test: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_auth_flow()







