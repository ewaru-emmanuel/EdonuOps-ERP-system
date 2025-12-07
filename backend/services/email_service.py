import os
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import text
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """AWS SES SMTP Email Service for EdonuOps ERP"""
    
    def __init__(self):
        # Load environment variables from .env (not config.env which has placeholders)
        load_dotenv('.env')
        
        # AWS SES SMTP Configuration - All from environment variables
        self.SMTP_HOST = "email-smtp.eu-north-1.amazonaws.com"
        self.SMTP_PORT = 587
        self.SMTP_USER = os.getenv("SES_SMTP_USER")
        self.SMTP_PASS = os.getenv("SES_SMTP_PASS")
        self.FROM_EMAIL = os.getenv("SES_FROM_EMAIL", "info@edonuerp.com")
        self.FROM_NAME = os.getenv("SES_FROM_NAME", "EdonuOps ERP")
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # Validate required environment variables
        if not self.SMTP_USER or not self.SMTP_PASS:
            raise ValueError("SES_SMTP_USER and SES_SMTP_PASS environment variables are required")
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None):
        """
        Send email via AWS SES SMTP
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            html_body (str): HTML email content
            text_body (str): Plain text email content (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Load environment variables directly from .env file
            import os
            from dotenv import dotenv_values
            
            # Load .env file directly
            env_vars = dotenv_values('.env')
            smtp_user = env_vars.get("SES_SMTP_USER")
            smtp_pass = env_vars.get("SES_SMTP_PASS")
            from_email = env_vars.get("SES_FROM_EMAIL", "info@edonuerp.com")
            from_name = env_vars.get("SES_FROM_NAME", "EdonuOps ERP")
            
            if not smtp_user or not smtp_pass:
                logger.error("❌ SES_SMTP_USER and SES_SMTP_PASS environment variables are required")
                return False
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{from_email}>"
            msg["To"] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_body, "html")
            msg.attach(html_part)
            
            # Add text content if provided
            if text_body:
                text_part = MIMEText(text_body, "plain")
                msg.attach(text_part)
            
            # Send email via SMTP
            with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_email, to_email, msg.as_string())
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def generate_verification_token(self, user_id: int, email: str, db_session=None):
        """
        Generate email verification token and store in database
        
        Args:
            user_id (int): User ID
            email (str): User email address
            db_session: Database session (optional, will use current app context if not provided)
        
        Returns:
            str: Verification token
        """
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Store token in database
            if db_session is None:
                from app import db
                db_session = db.session
            
            # First, delete any existing tokens for this user
            db_session.execute(text("""
                DELETE FROM email_verification_tokens WHERE user_id = :user_id
            """), {'user_id': user_id})
            
            # Then insert the new token
            db_session.execute(text("""
                INSERT INTO email_verification_tokens (user_id, token, email, expires_at, created_at)
                VALUES (:user_id, :token, :email, :expires_at, :created_at)
            """), {
                'user_id': user_id,
                'token': token,
                'email': email,
                'expires_at': expires_at,
                'created_at': datetime.utcnow()
            })
            db_session.commit()
            
            logger.info(f"✅ Verification token generated for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Failed to generate verification token: {str(e)}")
            return None
    
    def generate_password_reset_token(self, user_id: int, email: str, db_session=None):
        """
        Generate password reset token and store in database
        
        Args:
            user_id (int): User ID
            email (str): User email address
            db_session: Database session (optional, will use current app context if not provided)
        
        Returns:
            str: Password reset token
        """
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Store token in database
            if db_session is None:
                from app import db
                db_session = db.session
            
            # First, delete any existing tokens for this user (same pattern as verification)
            db_session.execute(text("""
                DELETE FROM password_reset_tokens WHERE user_id = :user_id
            """), {'user_id': user_id})
            
            # Then insert the new token
            db_session.execute(text("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at, created_at)
                VALUES (:user_id, :token, :expires_at, :created_at)
            """), {
                'user_id': user_id,
                'token': token,
                'expires_at': expires_at,
                'created_at': datetime.utcnow()
            })
            db_session.commit()
            
            logger.info(f"✅ Password reset token generated for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Failed to generate password reset token: {str(e)}")
            return None
    
    def send_verification_email(self, user_email: str, user_id: int, db_session=None):
        """
        Send email verification email
        
        Args:
            user_email (str): User email address
            user_id (int): User ID
            db_session: Database session (optional)
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            logger.info(f"📧 send_verification_email called for user_id={user_id}, email={user_email} at {datetime.utcnow().isoformat()}")
            print(f"📧 send_verification_email called for user_id={user_id}, email={user_email} at {datetime.utcnow().isoformat()}")
            
            # Generate verification token
            token = self.generate_verification_token(user_id, user_email, db_session)
            if not token:
                logger.error(f"❌ Failed to generate verification token for user {user_id}")
                print(f"❌ Failed to generate verification token for user {user_id}")
                return False
            
            logger.info(f"✅ New verification token generated for user {user_id}, token preview: {token[:20]}...")
            print(f"✅ New verification token generated for user {user_id}")
            
            # Create verification link
            verify_link = f"{self.FRONTEND_URL}/verify-email?token={token}"
            
            # Email content - add timestamp to make each email unique
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            subject = f"Please verify your EdonuOps ERP account - {timestamp}"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Account Verification</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .button {{ display: inline-block; background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>EdonuOps ERP</h1>
                </div>
                <div class="content">
                    <h2>Email Verification Required</h2>
                    <p>Hello,</p>
                    <p>Thank you for registering with EdonuOps ERP. Please verify your email address to complete your account setup.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verify_link}" class="button">Verify Email Address</a>
                    </div>
                    
                    <p>If the button doesn't work, copy this link to your browser:</p>
                    <p style="word-break: break-all; background-color: #ecf0f1; padding: 10px; border-radius: 4px;">{verify_link}</p>
                    
                    <p><strong>Important:</strong> This verification link expires in 24 hours.</p>
                    <p>If you didn't create this account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>EdonuOps ERP System</p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            EdonuOps ERP - Email Verification
            
            Hello,
            
            Thank you for registering with EdonuOps ERP. Please verify your email address to complete your account setup.
            
            Verification link: {verify_link}
            
            This verification link expires in 24 hours.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            EdonuOps ERP Team
            """
            
            # Send email
            return self.send_email(user_email, subject, html_body, text_body)
            
        except Exception as e:
            logger.error(f"❌ Failed to send verification email: {str(e)}")
            return False
    
    def send_password_reset_email(self, user_email: str, user_id: int, db_session=None):
        """
        Send password reset email
        
        Args:
            user_email (str): User email address
            user_id (int): User ID
            db_session: Database session (optional)
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Generate password reset token (same pattern as verification)
            token = self.generate_password_reset_token(user_id, user_email, db_session)
            if not token:
                return False
            
            # Create reset link
            reset_link = f"{self.FRONTEND_URL}/reset-password?token={token}"
            
            # Email content
            subject = "Reset Your EdonuOps Password"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Reset Your Password</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #e74c3c; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .button {{ display: inline-block; background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                    .button:hover {{ background-color: #c0392b; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    .security-notice {{ background-color: #fdf2f2; padding: 15px; border-radius: 4px; margin: 20px 0; border-left: 4px solid #e74c3c; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your password for your EdonuOps ERP account. If you made this request, click the button below to reset your password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background-color: #ecf0f1; padding: 10px; border-radius: 4px;">{reset_link}</p>
                    
                    <div class="security-notice">
                        <strong>Important Security Information:</strong>
                        <ul>
                            <li>This password reset link will expire in 1 hour</li>
                            <li>If you didn't request this password reset, please ignore this email</li>
                            <li>Your password will remain unchanged until you click the link above</li>
                            <li>For security reasons, this link can only be used once</li>
                        </ul>
                    </div>
                    
                    <p>If you continue to have problems accessing your account, please contact our support team.</p>
                </div>
                <div class="footer">
                    <p>This email was sent from EdonuOps ERP. If you have any questions, please contact our support team.</p>
                    <p>© 2024 EdonuOps ERP. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Password Reset Request
            
            We received a request to reset your password for your EdonuOps ERP account.
            
            To reset your password, click the link below:
            {reset_link}
            
            This password reset link will expire in 1 hour.
            
            If you didn't request this password reset, please ignore this email.
            Your password will remain unchanged until you click the link above.
            
            Best regards,
            EdonuOps ERP Team
            """
            
            # Send email
            return self.send_email(user_email, subject, html_body, text_body)
            
        except Exception as e:
            logger.error(f"❌ Failed to send password reset email: {str(e)}")
            return False
    
    def validate_verification_token(self, token: str):
        """
        Validate email verification token
        
        Args:
            token (str): Verification token
        
        Returns:
            dict: User information if valid, None if invalid
        """
        try:
            from app import db
            result = db.session.execute(text("""
                SELECT evt.user_id, evt.email, evt.expires_at, u.username, u.email_verified
                FROM email_verification_tokens evt
                JOIN users u ON evt.user_id = u.id
                WHERE evt.token = :token 
                AND evt.used = FALSE 
                AND evt.expires_at > NOW()
            """), {'token': token}).fetchone()
            
            if result:
                return {
                    'user_id': result.user_id,
                    'email': result.email,
                    'username': result.username,
                    'email_verified': result.email_verified
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to validate verification token: {str(e)}")
            return None
    
    def validate_password_reset_token(self, token: str):
        """
        Validate password reset token
        
        Args:
            token (str): Password reset token
        
        Returns:
            dict: User information if valid, None if invalid
        """
        try:
            from app import db
            result = db.session.execute(text("""
                SELECT prt.user_id, prt.expires_at, u.username, u.email
                FROM password_reset_tokens prt
                JOIN users u ON prt.user_id = u.id
                WHERE prt.token = :token 
                AND prt.used = FALSE 
                AND prt.expires_at > NOW()
            """), {'token': token}).fetchone()
            
            if result:
                return {
                    'user_id': result.user_id,
                    'email': result.email,
                    'username': result.username
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to validate password reset token: {str(e)}")
            return None
    
    def mark_verification_token_used(self, token: str):
        """
        Mark verification token as used
        
        Args:
            token (str): Verification token
        
        Returns:
            bool: True if successful
        """
        try:
            from app import db
            db.session.execute(text("""
                UPDATE email_verification_tokens 
                SET used = TRUE, used_at = NOW()
                WHERE token = :token
            """), {'token': token})
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to mark verification token as used: {str(e)}")
            return False
    
    def mark_password_reset_token_used(self, token: str):
        """
        Mark password reset token as used
        
        Args:
            token (str): Password reset token
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from app import db
            # SECURITY: Use atomic update with explicit check to prevent race conditions
            result = db.session.execute(text("""
                UPDATE password_reset_tokens 
                SET used = TRUE, used_at = NOW()
                WHERE token = :token 
                AND used = FALSE
                AND expires_at > NOW()
            """), {'token': token})
            
            # Verify exactly one row was updated (token was valid and not already used)
            if result.rowcount != 1:
                logger.warning(f"⚠️ Token mark as used affected {result.rowcount} rows (expected 1) for token: {token[:10]}...")
                db.session.rollback()
                return False
            
            db.session.commit()
            logger.info(f"✅ Password reset token marked as used: {token[:10]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to mark password reset token as used: {str(e)}")
            db.session.rollback()
            return False

# Create global email service instance (lazy initialization)
email_service = None

def get_email_service():
    """Get email service instance with lazy initialization"""
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service
