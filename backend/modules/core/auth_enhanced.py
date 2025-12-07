#!/usr/bin/env python3
"""
🔐 EDONUOPS ERP - ENHANCED AUTHENTICATION API
============================================================

Enterprise-grade authentication APIs with:
- Rate limiting and security monitoring
- Email verification with AWS SES
- Password reset with secure tokens
- Account lockout protection
- Comprehensive audit logging

Author: EdonuOps Team
Date: 2024
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import boto3
from botocore.exceptions import ClientError

# Import database and models
from app import db
from modules.core.models import User, Role
from modules.core.tenant_context import get_current_tenant, audit_tenant_access
from services.email_service import email_service

# Setup logging
logger = logging.getLogger(__name__)

# Create Blueprint
auth_enhanced_bp = Blueprint("auth_enhanced", __name__)

# AWS SES Configuration
def get_ses_client():
    """Get AWS SES client"""
    try:
        return boto3.client(
            'ses',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        logger.error(f"Failed to create SES client: {e}")
        return None

def send_email_via_ses(to_email, subject, body_html, body_text):
    """Send email via AWS SES"""
    try:
        ses_client = get_ses_client()
        if not ses_client:
            return False
        
        response = ses_client.send_email(
            Source=os.getenv('SES_FROM_EMAIL', 'noreply@edonuops.com'),
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'},
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'}
                }
            }
        )
        logger.info(f"Email sent successfully to {to_email}: {response['MessageId']}")
        return True
    except ClientError as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {e}")
        return False

def generate_secure_token():
    """Generate secure URL-safe token"""
    return secrets.token_urlsafe(32)

def check_rate_limit(email, ip_address, max_attempts=5, window_minutes=15):
    """Check if user/IP has exceeded rate limit"""
    try:
        # Check failed attempts in the last window
        result = db.session.execute(text("""
            SELECT COUNT(*) as attempt_count
            FROM login_attempts 
            WHERE (email = :email OR ip_address = :ip_address)
            AND success = FALSE 
            AND attempt_time > NOW() - INTERVAL ':window_minutes minutes'
        """), {
            'email': email,
            'ip_address': ip_address,
            'window_minutes': window_minutes
        })
        
        attempt_count = result.scalar()
        return attempt_count < max_attempts, attempt_count
        
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return True, 0  # Allow on error

def log_login_attempt(email, ip_address, success, user_id=None, failure_reason=None):
    """Log login attempt for security monitoring"""
    try:
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        db.session.execute(text("""
            INSERT INTO login_attempts 
            (user_id, email, ip_address, success, user_agent, failure_reason, tenant_id)
            VALUES (:user_id, :email, :ip_address, :success, :user_agent, :failure_reason, :tenant_id)
        """), {
            'user_id': user_id,
            'email': email,
            'ip_address': ip_address,
            'success': success,
            'user_agent': user_agent,
            'failure_reason': failure_reason,
            'tenant_id': get_current_tenant() or 'default_tenant'
        })
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error logging login attempt: {e}")
        db.session.rollback()

@auth_enhanced_bp.route("/login", methods=["POST", "OPTIONS"])
def enhanced_login():
    """Enhanced login with rate limiting and security monitoring"""
    # Handle OPTIONS request (CORS preflight)
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        ip_address = request.remote_addr

        # Input validation
        if not email or not password:
            return jsonify({
                "message": "Email and password are required"
            }), 400

        if "@" not in email:
            return jsonify({
                "message": "Invalid email format"
            }), 400

        # Check rate limiting
        rate_limit_ok, attempt_count = check_rate_limit(email, ip_address)
        if not rate_limit_ok:
            log_login_attempt(email, ip_address, False, failure_reason="rate_limit_exceeded")
            return jsonify({
                "message": "Too many failed attempts. Please try again later.",
                "retry_after": 900  # 15 minutes
            }), 429

        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            log_login_attempt(email, ip_address, False, failure_reason="user_not_found")
            return jsonify({
                "message": "Invalid credentials"
            }), 401

        # Check if user is active
        if not user.is_active:
            log_login_attempt(email, ip_address, False, user.id, "account_inactive")
            return jsonify({
                "message": "Account is inactive. Please contact support."
            }), 401

        # Verify password
        if not check_password_hash(user.password_hash, password):
            log_login_attempt(email, ip_address, False, user.id, "invalid_password")
            return jsonify({
                "message": "Invalid credentials"
            }), 401

        # Check if email is verified
        if not user.email_verified:
            log_login_attempt(email, ip_address, False, user.id, "email_not_verified")
            return jsonify({
                "message": "Please verify your email address before logging in",
                "email_verification_required": True,
                "email": email
            }), 401

        # Successful login
        log_login_attempt(email, ip_address, True, user.id)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create JWT token - identity MUST be a string
        token = create_access_token(identity=str(user.id), additional_claims={
            'email': user.email,
            'username': user.username,
            'role': user.role.role_name if user.role else 'user',
            'is_active': user.is_active,
            'tenant_id': user.tenant_id
        })

        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.role_name if user.role else 'user',
                "is_active": user.is_active,
                "tenant_id": user.tenant_id
            }
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            "message": "Login failed. Please try again."
        }), 500

@auth_enhanced_bp.route("/register", methods=["POST", "OPTIONS"])
def enhanced_register():
    # Handle OPTIONS request (CORS preflight)
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-ID')
        return response, 200
    
    """Enhanced registration with invite token support"""
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        phone_number = data.get("phone_number", "").strip()
        invite_token = data.get("invite_token")  # Optional invite token

        # Input validation
        errors = {}
        
        if not username or len(username) < 3:
            errors["username"] = "Username must be at least 3 characters"
        
        if not email or "@" not in email:
            errors["email"] = "Valid email address is required"
        
        if not first_name or len(first_name) < 2:
            errors["first_name"] = "First name must be at least 2 characters"
        
        if not last_name or len(last_name) < 2:
            errors["last_name"] = "Last name must be at least 2 characters"
        
        if not phone_number or len(phone_number) < 10:
            errors["phone_number"] = "Phone number must be at least 10 characters"
        
        if not password or len(password) < 8:
            errors["password"] = "Password must be at least 8 characters"
        
        if password != confirm_password:
            errors["confirm_password"] = "Passwords do not match"
        
        if errors:
            return jsonify({
                "message": "Validation failed",
                "errors": errors
            }), 400

        # Enhanced password validation
        password_errors = []
        if len(password) < 8:
            password_errors.append("At least 8 characters")
        if not any(c.isupper() for c in password):
            password_errors.append("At least one uppercase letter")
        if not any(c.islower() for c in password):
            password_errors.append("At least one lowercase letter")
        if not any(c.isdigit() for c in password):
            password_errors.append("At least one number")
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            password_errors.append("At least one special character")
        
        if password_errors:
            return jsonify({
                "message": "Password does not meet requirements",
                "errors": {"password": password_errors}
            }), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Check if email is verified
            if existing_user.email_verified:
                return jsonify({
                    "message": f"An account with the email '{email}' is already registered. Please login to access your account.",
                    "info": "email_exists",
                    "field": "email",
                    "suggestion": "login"
                }), 409
            else:
                # Email exists but not verified - send/resend verification email
                try:
                    from services.email_service import get_email_service
                    email_service = get_email_service()
                    
                    if email_service:
                        email_sent = email_service.send_verification_email(email, existing_user.id, db.session)
                        if email_sent:
                            logger.info(f"✅ Verification email resent to {email} (user not verified)")
                            print(f"📧 Verification email resent to {email}")
                except Exception as e:
                    logger.error(f"❌ Error resending verification email to {email}: {e}")
                    print(f"⚠️  Warning: Failed to resend verification email: {e}")
                
                return jsonify({
                    "message": f"A verification email has been sent to '{email}'. Please check your inbox to verify your account.",
                    "info": "email_not_verified",
                    "field": "email",
                    "email": email,
                    "email_sent": True,
                    "can_resend": True
                }), 409

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            return jsonify({
                "message": f"The username '{username}' is already taken. Please choose a different username.",
                "info": "username_exists",
                "field": "username",
                "suggestion": "choose_different"
            }), 409

        # Handle invite token if provided
        tenant_id = 'default_tenant'
        role_name = 'user'
        
        if invite_token:
            # Validate invite token
            invite_result = db.session.execute(text("""
                SELECT tenant_id, role_id, email, expires_at, used
                FROM user_invites 
                WHERE token = :token AND expires_at > NOW()
            """), {'token': invite_token})
            
            invite = invite_result.fetchone()
            
            if not invite:
                return jsonify({
                    "message": "Invalid or expired invite token"
                }), 400
            
            if invite.used:
                return jsonify({
                    "message": "Invite token has already been used"
                }), 400
            
            if invite.email != email:
                return jsonify({
                    "message": "Email does not match invite"
                }), 400
            
            tenant_id = invite.tenant_id
            role_name = 'user'  # Default role for invited users
        
        else:
            # No invite token - check if this is the first user
            # For multi-tenant: first user per tenant gets admin
            # For single-tenant: first user globally gets admin
            from modules.core.tenant_models import Tenant
            import uuid
            
            # Check if this is first user globally (single-tenant) or will create new tenant
            global_user_count = User.query.count()
            is_first_user_globally = global_user_count == 0
            
            if is_first_user_globally:
                # First user globally - create tenant and assign admin
                tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
                company_name = f"{first_name.strip()} {last_name.strip()}'s Company"
                
                # Create tenant
                new_tenant = Tenant(
                    id=tenant_id,
                    name=company_name,
                    domain=email.split('@')[1] if '@' in email else 'localhost',
                    subscription_plan='free',
                    status='active'
                )
                
                db.session.add(new_tenant)
                db.session.flush()  # Flush to get tenant ID
                
                # First user gets superadmin role - they are the main admin (Admin No.1)
                # Try both "superadmin" and "super admin" (with space) - different databases may have different formats
                superadmin_role = Role.query.filter(
                    (Role.role_name == "superadmin") | 
                    (Role.role_name == "super admin")
                ).first()
                
                if superadmin_role:
                    role_name = superadmin_role.role_name
                    print(f"🔍 DEBUG: First user globally detected - creating tenant and assigning {role_name.upper()} role")
                else:
                    # Fallback to admin role if superadmin doesn't exist
                    admin_role = Role.query.filter_by(role_name="admin").first()
                    if admin_role:
                        role_name = "admin"
                        print(f"🔍 DEBUG: First user globally detected - superadmin role not found, using ADMIN role")
                    else:
                        # Last resort - get any role
                        any_role = Role.query.first()
                        if any_role:
                            role_name = any_role.role_name
                            print(f"⚠️  WARNING: First user - using {role_name} role (superadmin not found)")
                        else:
                            raise Exception("No roles found in database. Please initialize roles first.")
            else:
                # Not first user - require invite token for multi-tenant systems
                return jsonify({
                    "message": "Registration requires an invite token from your administrator"
                }), 400

        # Get role
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            return jsonify({
                "message": "System not properly initialized"
            }), 500

        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role_id=role.id,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create default accounts automatically for new user
        try:
            from modules.finance.default_accounts_service import create_default_accounts
            print(f"📊 Creating default accounts for new user {new_user.id}...")
            result = create_default_accounts(new_user.id, force=False)
            print(f"✅ Created {result['new_count']} default accounts for user {new_user.id}")
        except Exception as e:
            print(f"⚠️  Warning: Failed to create default accounts for user {new_user.id}: {e}")
            # Don't fail registration if account creation fails - can be created later
            import traceback
            traceback.print_exc()

        # Mark invite as used if applicable
        if invite_token:
            db.session.execute(text("""
                UPDATE user_invites 
                SET used = TRUE, used_at = NOW(), used_by = :user_id
                WHERE token = :token
            """), {'token': invite_token, 'user_id': new_user.id})
            db.session.commit()

        # Send email verification using email_service
        try:
            from services.email_service import get_email_service
            email_service = get_email_service()
            
            if email_service:
                email_sent = email_service.send_verification_email(email, new_user.id, db.session)
                if email_sent:
                    logger.info(f"✅ Verification email sent to {email}")
                    print(f"📧 Verification email sent to {email}")
                else:
                    logger.warning(f"⚠️  Failed to send verification email to {email}")
                    print(f"⚠️  Warning: Failed to send verification email to {email}")
            else:
                logger.warning(f"⚠️  Email service not available - verification email not sent to {email}")
                print(f"⚠️  Warning: Email service not available - verification email not sent")
        except Exception as e:
            logger.error(f"❌ Error sending verification email to {email}: {e}")
            print(f"❌ Error sending verification email: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail registration if email sending fails

        return jsonify({
            "message": "Registration successful. Please check your email to verify your account.",
            "user_id": new_user.id,
            "email_verification_sent": True
        }), 201

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Registration error: {e}")
        logger.error(f"Registration error type: {type(e)}")
        logger.error(f"Registration error details: {str(e)}")
        logger.error(f"Registration traceback: {error_traceback}")
        print(f"❌ REGISTRATION ERROR: {e}")
        print(f"❌ ERROR TYPE: {type(e)}")
        print(f"❌ TRACEBACK:\n{error_traceback}")
        db.session.rollback()
        
        # Return more detailed error in development
        error_message = "Registration failed. Please try again."
        debug_info = None
        if os.getenv('FLASK_ENV') == 'development' or os.getenv('FLASK_DEBUG') == '1':
            debug_info = {
                "error": str(e),
                "error_type": str(type(e).__name__),
                "traceback": error_traceback.split('\n')[-10:] if len(error_traceback.split('\n')) > 10 else error_traceback.split('\n')
            }
        
        return jsonify({
            "message": error_message,
            "debug": debug_info
        }), 500

@auth_enhanced_bp.route("/verify-email", methods=["POST"])
def verify_email():
    """Verify email address with token"""
    try:
        data = request.get_json()
        token = data.get("token", "").strip()

        if not token:
            return jsonify({
                "message": "Verification token is required"
            }), 400

        # Find verification token
        result = db.session.execute(text("""
            SELECT user_id, email, expires_at, used
            FROM email_verification_tokens 
            WHERE token = :token AND expires_at > NOW()
        """), {'token': token})
        
        verification = result.fetchone()
        
        if not verification:
            return jsonify({
                "message": "Invalid or expired verification token"
            }), 400
        
        if verification.used:
            # Get user to return their info
            user = User.query.get(verification.user_id)
            if user and user.email_verified:
                logger.info(f"✅ Email already verified for user {verification.user_id}")
                
                # Auto-login: Create JWT access token for seamless onboarding
                access_token = create_access_token(identity=str(user.id), additional_claims={
                    'email': user.email,
                    'username': user.username,
                    'role': user.role.role_name if user.role else 'user',
                    'is_active': user.is_active,
                    'tenant_id': user.tenant_id,
                    'email_verified': True
                })
                
                return jsonify({
                    "message": "Email has already been verified",
                    "already_verified": True,
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "email_verified": True,
                        "role": user.role.role_name if user.role else 'user',
                        "tenant_id": user.tenant_id
                    },
                    "redirect_to": "onboarding"
                }), 200  # Return 200 instead of 400 for already verified
            else:
                return jsonify({
                    "message": "This verification link has already been used"
                }), 400

        # Get user to check current verification status
        user = User.query.get(verification.user_id)
        if not user:
            return jsonify({
                "message": "User not found"
            }), 404

        # Mark email as verified in users table
        db.session.execute(text("""
            UPDATE users 
            SET email_verified = TRUE, updated_at = NOW()
            WHERE id = :user_id
        """), {'user_id': verification.user_id})

        # Mark token as used
        db.session.execute(text("""
            UPDATE email_verification_tokens 
            SET used = TRUE, used_at = NOW()
            WHERE token = :token
        """), {'token': token})
        
        # Update last login
        db.session.execute(text("""
            UPDATE users 
            SET last_login = NOW()
            WHERE id = :user_id
        """), {'user_id': verification.user_id})
        
        db.session.commit()

        logger.info(f"✅ Email verified successfully for user {verification.user_id}")
        print(f"✅ Email verified successfully for user {verification.user_id}")

        # Auto-login: Create JWT access token for seamless onboarding
        access_token = create_access_token(identity=str(user.id), additional_claims={
            'email': user.email,
            'username': user.username,
            'role': user.role.role_name if user.role else 'user',
            'is_active': user.is_active,
            'tenant_id': user.tenant_id,
            'email_verified': True
        })

        logger.info(f"🔑 Access token created for user {user.id} after email verification")
        print(f"🔑 Auto-login token created for user {user.id}")

        return jsonify({
            "message": "Email verified successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "email_verified": True,
                "role": user.role.role_name if user.role else 'user',
                "tenant_id": user.tenant_id
            },
            "redirect_to": "onboarding"
        }), 200

    except Exception as e:
        logger.error(f"Email verification error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Email verification failed"
        }), 500

@auth_enhanced_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()

        if not email or "@" not in email:
            return jsonify({
                "message": "Valid email address is required"
            }), 400

        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Don't reveal if user exists
            return jsonify({
                "message": "If the email exists, a password reset link has been sent"
            }), 200

        if not user.is_active:
            return jsonify({
                "message": "If the email exists, a password reset link has been sent"
            }), 200

        # Generate reset token
        reset_token = generate_secure_token()
        
        # Store reset token
        db.session.execute(text("""
            INSERT INTO password_reset_tokens 
            (user_id, token, expires_at, ip_address, user_agent, tenant_id)
            VALUES (:user_id, :token, :expires_at, :ip_address, :user_agent, :tenant_id)
            ON CONFLICT (user_id) DO UPDATE SET
                token = EXCLUDED.token,
                expires_at = EXCLUDED.expires_at,
                used = FALSE,
                ip_address = EXCLUDED.ip_address,
                user_agent = EXCLUDED.user_agent
        """), {
            'user_id': user.id,
            'token': reset_token,
            'expires_at': datetime.utcnow() + timedelta(hours=1),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'tenant_id': user.tenant_id
        })
        
        db.session.commit()

        # Send reset email
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        email_subject = "Password Reset - EdonuOps ERP"
        email_html = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your EdonuOps ERP account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
        </body>
        </html>
        """
        
        email_text = f"""
        Password Reset Request
        
        You requested a password reset for your EdonuOps ERP account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        """
        
        send_email_via_ses(email, email_subject, email_html, email_text)

        return jsonify({
            "message": "If the email exists, a password reset link has been sent"
        }), 200

    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Password reset request failed"
        }), 500

@auth_enhanced_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get("token", "").strip()
        new_password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")

        if not token:
            return jsonify({
                "message": "Reset token is required"
            }), 400

        if not new_password or len(new_password) < 8:
            return jsonify({
                "message": "Password must be at least 8 characters"
            }), 400

        if new_password != confirm_password:
            return jsonify({
                "message": "Passwords do not match"
            }), 400

        # Enhanced password validation
        password_errors = []
        if len(new_password) < 8:
            password_errors.append("At least 8 characters")
        if not any(c.isupper() for c in new_password):
            password_errors.append("At least one uppercase letter")
        if not any(c.islower() for c in new_password):
            password_errors.append("At least one lowercase letter")
        if not any(c.isdigit() for c in new_password):
            password_errors.append("At least one number")
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in new_password):
            password_errors.append("At least one special character")
        
        if password_errors:
            return jsonify({
                "message": "Password does not meet requirements",
                "errors": {"password": password_errors}
            }), 400

        # Find reset token
        result = db.session.execute(text("""
            SELECT user_id, expires_at, used
            FROM password_reset_tokens 
            WHERE token = :token AND expires_at > NOW()
        """), {'token': token})
        
        reset_token = result.fetchone()
        
        if not reset_token:
            return jsonify({
                "message": "Invalid or expired reset token"
            }), 400
        
        if reset_token.used:
            return jsonify({
                "message": "Reset token has already been used"
            }), 400

        # Update password
        user = User.query.get(reset_token.user_id)
        if not user:
            return jsonify({
                "message": "User not found"
            }), 404

        user.password_hash = generate_password_hash(new_password)
        
        # Mark token as used
        db.session.execute(text("""
            UPDATE password_reset_tokens 
            SET used = TRUE, used_at = NOW()
            WHERE token = :token
        """), {'token': token})
        
        db.session.commit()

        return jsonify({
            "message": "Password reset successfully"
        }), 200

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Password reset failed"
        }), 500

@auth_enhanced_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    """Resend email verification"""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()

        if not email or "@" not in email:
            return jsonify({
                "message": "Valid email address is required"
            }), 400

        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                "message": "If the email exists, a verification link has been sent"
            }), 200

        # Check if already verified
        if user.email_verified:
            return jsonify({
                "message": "Email is already verified"
            }), 400

        # Use email service to send verification email
        try:
            from services.email_service import get_email_service
            email_service = get_email_service()
            
            if email_service:
                logger.info(f"🔄 Attempting to resend verification email to {email} for user {user.id}")
                print(f"🔄 Attempting to resend verification email to {email} for user {user.id}")
                
                email_sent = email_service.send_verification_email(email, user.id, db.session)
                
                if email_sent:
                    logger.info(f"✅ Verification email resent successfully to {email}")
                    print(f"✅ Verification email resent successfully to {email} at {datetime.utcnow().isoformat()}")
                    return jsonify({
                        "message": "Verification email sent successfully",
                        "email": email,
                        "sent_at": datetime.utcnow().isoformat()
                    }), 200
                else:
                    logger.error(f"❌ Failed to send verification email to {email}")
                    print(f"❌ Failed to send verification email to {email}")
                    return jsonify({
                        "error": "Failed to send verification email. Please try again later."
                    }), 500
            else:
                return jsonify({
                    "error": "Email service not available"
                }), 500
        except Exception as e:
            logger.error(f"❌ Error resending verification email to {email}: {e}")
            print(f"❌ Error resending verification email: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": "Failed to send verification email"
            }), 500

    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Failed to resend verification"
        }), 500


@auth_enhanced_bp.route("/verify-token", methods=["GET"])
@jwt_required()
def verify_token():
    """
    Verify if the current JWT token is valid and return user info.
    Used by frontend to validate stored tokens on session restore.
    This prevents stale tokens from persisting after users are deleted.
    """
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({
                'valid': False,
                'error': 'No valid token found'
            }), 401
        
        # Get user from database
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"Token verification failed: User {user_id} not found")
            return jsonify({
                'valid': False,
                'error': 'User not found'
            }), 404
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Token verification failed: User {user_id} is inactive")
            return jsonify({
                'valid': False,
                'error': 'User account is inactive'
            }), 403
        
        # Token is valid - return user info
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.role_name if user.role else 'user'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({
            'valid': False,
            'error': 'Token verification failed'
        }), 401
