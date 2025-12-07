#!/usr/bin/env python3
"""
📧 EDONUOPS ERP - AWS SES CONFIGURATION & INVITE MANAGEMENT
============================================================

AWS SES configuration and invite management endpoints:
- AWS SES email service configuration
- Invite creation and management
- Email templates for invitations
- Invite validation and tracking

Author: EdonuOps Team
Date: 2024
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import boto3
from botocore.exceptions import ClientError

# Import database and models
from app import db
from modules.core.models import User, Role
from modules.core.tenant_context import get_current_tenant, audit_tenant_access

# Setup logging
logger = logging.getLogger(__name__)

# Create Blueprint
invite_management_bp = Blueprint("invite_management", __name__)

# AWS SES Configuration
class SESConfig:
    """AWS SES configuration and email service"""
    
    @staticmethod
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
    
    @staticmethod
    def send_email(to_email, subject, body_html, body_text):
        """Send email via AWS SES"""
        try:
            ses_client = SESConfig.get_ses_client()
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

@invite_management_bp.route("/create-invite", methods=["POST"])
@jwt_required()
def create_invite():
    """Create user invite for tenant"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        email = data.get("email", "").strip().lower()
        role_name = data.get("role", "user")
        message = data.get("message", "")
        expires_days = data.get("expires_days", 7)
        
        # Input validation
        if not email or "@" not in email:
            return jsonify({
                "message": "Valid email address is required"
            }), 400
        
        if expires_days < 1 or expires_days > 30:
            return jsonify({
                "message": "Expiration days must be between 1 and 30"
            }), 400
        
        # Get current user and tenant
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({
                "message": "User not found"
            }), 404
        
        tenant_id = current_user.tenant_id
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                "message": "User with this email already exists"
            }), 409
        
        # Check if invite already exists and is not expired
        existing_invite = db.session.execute(text("""
            SELECT id FROM user_invites 
            WHERE email = :email AND tenant_id = :tenant_id 
            AND expires_at > NOW() AND used = FALSE
        """), {'email': email, 'tenant_id': tenant_id}).fetchone()
        
        if existing_invite:
            return jsonify({
                "message": "Active invite already exists for this email"
            }), 409
        
        # Get role
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            return jsonify({
                "message": "Invalid role specified"
            }), 400
        
        # Create invite using database function
        result = db.session.execute(text("""
            SELECT create_user_invite(
                :tenant_id, :invited_by, :email, :role_id, :message, :expires_days
            )
        """), {
            'tenant_id': tenant_id,
            'invited_by': current_user_id,
            'email': email,
            'role_id': role.id,
            'message': message,
            'expires_days': expires_days
        })
        
        invite_token = result.scalar()
        
        # Send invitation email
        invite_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/register?invite={invite_token}"
        
        email_subject = f"You're invited to join {tenant_id} - EdonuOps ERP"
        email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #2c3e50;">You're Invited!</h2>
                <p>You've been invited to join <strong>{tenant_id}</strong> on EdonuOps ERP.</p>
                
                <div style="background-color: white; padding: 20px; border-radius: 4px; margin: 20px 0;">
                    <h3 style="color: #34495e;">Invitation Details:</h3>
                    <ul>
                        <li><strong>Organization:</strong> {tenant_id}</li>
                        <li><strong>Role:</strong> {role_name}</li>
                        <li><strong>Expires:</strong> {expires_days} days</li>
                    </ul>
                </div>
                
                {f'<p style="background-color: #e8f4fd; padding: 15px; border-radius: 4px; border-left: 4px solid #3498db;"><strong>Message:</strong> {message}</p>' if message else ''}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invite_url}" 
                       style="background-color: #3498db; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Accept Invitation
                    </a>
                </div>
                
                <p style="color: #7f8c8d; font-size: 14px;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <a href="{invite_url}">{invite_url}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                <p style="color: #95a5a6; font-size: 12px;">
                    This invitation was sent by {current_user.username} ({current_user.email}).<br>
                    If you didn't expect this invitation, you can safely ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        email_text = f"""
        You're Invited!
        
        You've been invited to join {tenant_id} on EdonuOps ERP.
        
        Invitation Details:
        - Organization: {tenant_id}
        - Role: {role_name}
        - Expires: {expires_days} days
        
        {f'Message: {message}' if message else ''}
        
        Accept your invitation by visiting:
        {invite_url}
        
        This invitation was sent by {current_user.username} ({current_user.email}).
        If you didn't expect this invitation, you can safely ignore this email.
        """
        
        email_sent = SESConfig.send_email(email, email_subject, email_html, email_text)
        
        return jsonify({
            "message": "Invitation sent successfully",
            "invite_token": invite_token,
            "email_sent": email_sent,
            "expires_at": datetime.utcnow() + timedelta(days=expires_days)
        }), 201
        
    except Exception as e:
        logger.error(f"Create invite error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Failed to create invitation"
        }), 500

@invite_management_bp.route("/validate-invite", methods=["POST"])
def validate_invite():
    """Validate invite token"""
    try:
        data = request.get_json()
        token = data.get("token", "").strip()
        
        if not token:
            return jsonify({
                "message": "Invite token is required"
            }), 400
        
        # Validate invite using database function
        result = db.session.execute(text("""
            SELECT * FROM validate_user_invite(:token)
        """), {'token': token})
        
        invite_data = result.fetchone()
        
        if not invite_data:
            return jsonify({
                "message": "Invalid invite token"
            }), 400
        
        if not invite_data.valid:
            return jsonify({
                "message": "Invite token has expired or been used"
            }), 400
        
        return jsonify({
            "message": "Invite token is valid",
            "tenant_id": invite_data.tenant_id,
            "email": invite_data.email,
            "role_id": invite_data.role_id,
            "expires_at": invite_data.expires_at
        }), 200
        
    except Exception as e:
        logger.error(f"Validate invite error: {e}")
        return jsonify({
            "message": "Failed to validate invite token"
        }), 500

@invite_management_bp.route("/list-invites", methods=["GET"])
@jwt_required()
def list_invites():
    """List all invites for current tenant"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                "message": "User not found"
            }), 404
        
        tenant_id = current_user.tenant_id
        
        # Get invites for tenant
        result = db.session.execute(text("""
            SELECT 
                ui.id,
                ui.email,
                ui.role_id,
                r.role_name,
                ui.token,
                ui.expires_at,
                ui.used,
                ui.used_at,
                ui.created_at,
                ui.message,
                u.username as invited_by_username
            FROM user_invites ui
            LEFT JOIN roles r ON ui.role_id = r.id
            LEFT JOIN users u ON ui.invited_by = u.id
            WHERE ui.tenant_id = :tenant_id
            ORDER BY ui.created_at DESC
        """), {'tenant_id': tenant_id})
        
        invites = []
        for row in result:
            invites.append({
                "id": row.id,
                "email": row.email,
                "role_name": row.role_name,
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                "used": row.used,
                "used_at": row.used_at.isoformat() if row.used_at else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "message": row.message,
                "invited_by": row.invited_by_username
            })
        
        return jsonify({
            "message": "Invites retrieved successfully",
            "invites": invites
        }), 200
        
    except Exception as e:
        logger.error(f"List invites error: {e}")
        return jsonify({
            "message": "Failed to retrieve invites"
        }), 500

@invite_management_bp.route("/cancel-invite/<int:invite_id>", methods=["DELETE"])
@jwt_required()
def cancel_invite(invite_id):
    """Cancel an invite"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                "message": "User not found"
            }), 404
        
        tenant_id = current_user.tenant_id
        
        # Check if invite exists and belongs to tenant
        result = db.session.execute(text("""
            SELECT id FROM user_invites 
            WHERE id = :invite_id AND tenant_id = :tenant_id AND used = FALSE
        """), {'invite_id': invite_id, 'tenant_id': tenant_id})
        
        invite = result.fetchone()
        
        if not invite:
            return jsonify({
                "message": "Invite not found or already used"
            }), 404
        
        # Delete invite
        db.session.execute(text("""
            DELETE FROM user_invites WHERE id = :invite_id
        """), {'invite_id': invite_id})
        
        db.session.commit()
        
        return jsonify({
            "message": "Invite cancelled successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Cancel invite error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Failed to cancel invite"
        }), 500

@invite_management_bp.route("/resend-invite/<int:invite_id>", methods=["POST"])
@jwt_required()
def resend_invite(invite_id):
    """Resend invitation email"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                "message": "User not found"
            }), 404
        
        tenant_id = current_user.tenant_id
        
        # Get invite details
        result = db.session.execute(text("""
            SELECT 
                ui.email,
                ui.token,
                ui.expires_at,
                ui.message,
                r.role_name
            FROM user_invites ui
            LEFT JOIN roles r ON ui.role_id = r.id
            WHERE ui.id = :invite_id AND ui.tenant_id = :tenant_id AND ui.used = FALSE
        """), {'invite_id': invite_id, 'tenant_id': tenant_id})
        
        invite = result.fetchone()
        
        if not invite:
            return jsonify({
                "message": "Invite not found or already used"
            }), 404
        
        if invite.expires_at < datetime.utcnow():
            return jsonify({
                "message": "Invite has expired"
            }), 400
        
        # Send invitation email
        invite_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/register?invite={invite.token}"
        
        email_subject = f"You're invited to join {tenant_id} - EdonuOps ERP"
        email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #2c3e50;">You're Invited!</h2>
                <p>You've been invited to join <strong>{tenant_id}</strong> on EdonuOps ERP.</p>
                
                <div style="background-color: white; padding: 20px; border-radius: 4px; margin: 20px 0;">
                    <h3 style="color: #34495e;">Invitation Details:</h3>
                    <ul>
                        <li><strong>Organization:</strong> {tenant_id}</li>
                        <li><strong>Role:</strong> {invite.role_name}</li>
                        <li><strong>Expires:</strong> {invite.expires_at.strftime('%Y-%m-%d %H:%M')}</li>
                    </ul>
                </div>
                
                {f'<p style="background-color: #e8f4fd; padding: 15px; border-radius: 4px; border-left: 4px solid #3498db;"><strong>Message:</strong> {invite.message}</p>' if invite.message else ''}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invite_url}" 
                       style="background-color: #3498db; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Accept Invitation
                    </a>
                </div>
                
                <p style="color: #7f8c8d; font-size: 14px;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <a href="{invite_url}">{invite_url}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                <p style="color: #95a5a6; font-size: 12px;">
                    This invitation was resent by {current_user.username} ({current_user.email}).<br>
                    If you didn't expect this invitation, you can safely ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        email_text = f"""
        You're Invited!
        
        You've been invited to join {tenant_id} on EdonuOps ERP.
        
        Invitation Details:
        - Organization: {tenant_id}
        - Role: {invite.role_name}
        - Expires: {invite.expires_at.strftime('%Y-%m-%d %H:%M')}
        
        {f'Message: {invite.message}' if invite.message else ''}
        
        Accept your invitation by visiting:
        {invite_url}
        
        This invitation was resent by {current_user.username} ({current_user.email}).
        If you didn't expect this invitation, you can safely ignore this email.
        """
        
        email_sent = SESConfig.send_email(invite.email, email_subject, email_html, email_text)
        
        return jsonify({
            "message": "Invitation resent successfully",
            "email_sent": email_sent
        }), 200
        
    except Exception as e:
        logger.error(f"Resend invite error: {e}")
        return jsonify({
            "message": "Failed to resend invitation"
        }), 500

@invite_management_bp.route("/cleanup-expired", methods=["POST"])
@jwt_required()
def cleanup_expired_invites():
    """Cleanup expired invites"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                "message": "User not found"
            }), 404
        
        # Only allow superadmin or admin to cleanup
        if current_user.role.role_name not in ['superadmin', 'admin']:
            return jsonify({
                "message": "Insufficient permissions"
            }), 403
        
        # Cleanup expired invites
        from modules.core.tenant_sql_helper import safe_sql_query
        result = safe_sql_query("SELECT cleanup_expired_invites()")
        deleted_count = result.scalar()
        
        return jsonify({
            "message": f"Cleaned up {deleted_count} expired invites"
        }), 200
        
    except Exception as e:
        logger.error(f"Cleanup expired invites error: {e}")
        return jsonify({
            "message": "Failed to cleanup expired invites"
        }), 500

