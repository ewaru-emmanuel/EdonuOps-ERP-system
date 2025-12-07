from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import logging
from services.email_service import get_email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for email verification and password reset
email_auth_bp = Blueprint('email_auth', __name__, url_prefix='/api/auth')

@email_auth_bp.route('/send-verification', methods=['POST'])
def send_verification_email():
    """
    Send email verification email to user
    """
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email address is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Check if user exists
        from app import db
        user = db.session.execute(text("""
            SELECT id, username, email_verified
            FROM users 
            WHERE email = :email
        """), {'email': email}).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if email is already verified
        if user.email_verified:
            return jsonify({'message': 'Email is already verified'}), 200
        
        # Send verification email
        email_service = get_email_service()
        success = email_service.send_verification_email(email, user.id)
        
        if success:
            logger.info(f"✅ Verification email sent to {email}")
            return jsonify({
                'message': 'Verification email sent successfully',
                'email': email
            }), 200
        else:
            return jsonify({'error': 'Failed to send verification email'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error sending verification email: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@email_auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """
    Verify email address using token
    """
    try:
        data = request.get_json()
        if not data or 'token' not in data:
            return jsonify({'error': 'Verification token is required'}), 400
        
        token = data['token'].strip()
        
        # Validate token
        email_service = get_email_service()
        user_info = email_service.validate_verification_token(token)
        if not user_info:
            return jsonify({'error': 'Invalid or expired verification token'}), 400
        
        # Check if email is already verified
        if user_info['email_verified']:
            return jsonify({'message': 'Email is already verified'}), 200
        
        # Mark email as verified
        from app import db
        db.session.execute(text("""
            UPDATE users 
            SET email_verified = TRUE, updated_at = NOW()
            WHERE id = :user_id
        """), {'user_id': user_info['user_id']})
        
        # Mark token as used
        email_service.mark_verification_token_used(token)
        
        db.session.commit()
        
        logger.info(f"✅ Email verified for user {user_info['user_id']}")
        return jsonify({
            'message': 'Email verified successfully',
            'user': {
                'id': user_info['user_id'],
                'username': user_info['username'],
                'email': user_info['email']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error verifying email: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@email_auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """
    Send password reset email to user
    """
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email address is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Check if user exists
        from app import db
        user = db.session.execute(text("""
            SELECT id, username, email_verified
            FROM users 
            WHERE email = :email
        """), {'email': email}).fetchone()
        
        if not user:
            # For security, don't reveal if user exists or not
            return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200
        
        # Check if email is verified
        if not user.email_verified:
            return jsonify({'error': 'Please verify your email address before resetting password'}), 400
        
        # Send password reset email
        email_service = get_email_service()
        success = email_service.send_password_reset_email(email, user.id)
        
        if success:
            logger.info(f"✅ Password reset email sent to {email}")
            return jsonify({
                'message': 'If the email exists, a password reset link has been sent'
            }), 200
        else:
            return jsonify({'error': 'Failed to send password reset email'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error sending password reset email: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@email_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using token
    """
    try:
        data = request.get_json()
        if not data or 'token' not in data or 'password' not in data:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        token = data['token'].strip()
        password = data['password']
        
        # Validate password
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Validate token
        email_service = get_email_service()
        user_info = email_service.validate_password_reset_token(token)
        if not user_info:
            return jsonify({'error': 'Invalid or expired password reset token'}), 400
        
        # Hash new password
        password_hash = generate_password_hash(password)
        
        # Update password
        from app import db
        db.session.execute(text("""
            UPDATE users 
            SET password_hash = :password_hash, updated_at = NOW()
            WHERE id = :user_id
        """), {
            'user_id': user_info['user_id'],
            'password_hash': password_hash
        })
        
        # Mark token as used
        email_service.mark_password_reset_token_used(token)
        
        db.session.commit()
        
        logger.info(f"✅ Password reset for user {user_info['user_id']}")
        return jsonify({
            'message': 'Password reset successfully',
            'user': {
                'id': user_info['user_id'],
                'username': user_info['username'],
                'email': user_info['email']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error resetting password: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@email_auth_bp.route('/validate-token', methods=['POST'])
def validate_token():
    """
    Validate email verification or password reset token
    """
    try:
        data = request.get_json()
        if not data or 'token' not in data or 'type' not in data:
            return jsonify({'error': 'Token and type are required'}), 400
        
        token = data['token'].strip()
        token_type = data['type'].strip().lower()
        
        if token_type == 'verification':
            email_service = get_email_service()
        user_info = email_service.validate_verification_token(token)
        elif token_type == 'password_reset':
            email_service = get_email_service()
        user_info = email_service.validate_password_reset_token(token)
        else:
            return jsonify({'error': 'Invalid token type'}), 400
        
        if user_info:
            return jsonify({
                'valid': True,
                'user': user_info
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired token'
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error validating token: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@email_auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    Resend verification email (rate limited)
    """
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email address is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Check if user exists
        from app import db
        user = db.session.execute(text("""
            SELECT id, username, email_verified
            FROM users 
            WHERE email = :email
        """), {'email': email}).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if email is already verified
        if user.email_verified:
            return jsonify({'message': 'Email is already verified'}), 200
        
        # Check rate limiting (prevent spam)
        recent_attempts = db.session.execute(text("""
            SELECT COUNT(*) as count
            FROM email_verification_tokens
            WHERE user_id = :user_id 
            AND created_at > NOW() - INTERVAL '1 hour'
        """), {'user_id': user.id}).fetchone()
        
        if recent_attempts.count >= 3:
            return jsonify({'error': 'Too many verification attempts. Please wait before trying again.'}), 429
        
        # Send verification email
        email_service = get_email_service()
        success = email_service.send_verification_email(email, user.id)
        
        if success:
            logger.info(f"✅ Verification email resent to {email}")
            return jsonify({
                'message': 'Verification email sent successfully',
                'email': email
            }), 200
        else:
            return jsonify({'error': 'Failed to send verification email'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error resending verification email: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
