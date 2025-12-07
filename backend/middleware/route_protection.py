"""
Global Route Protection Middleware
Protects all routes by default, except public routes
"""
from flask import request, jsonify, g
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import logging

logger = logging.getLogger(__name__)

# Define public routes that don't require authentication
PUBLIC_ROUTES = [
    '/health',
    '/test',
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/verify-email',
    '/api/auth/reset-password',
    '/api/auth/request-password-reset',
    '/api/auth/resend-verification',
]

# Define route prefixes that are public
PUBLIC_PREFIXES = [
    '/api/auth/',  # All auth routes are public
    '/health',
    '/test',
]


def is_public_route(path):
    """Check if a route is public (doesn't require authentication)"""
    # Check exact matches
    if path in PUBLIC_ROUTES:
        return True
    
    # Check prefixes
    for prefix in PUBLIC_PREFIXES:
        if path.startswith(prefix):
            return True
    
    return False


def require_authentication(app):
    """
    Global authentication middleware
    Protects all routes except public ones
    """
    @app.before_request
    def protect_routes():
        # Skip OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return None
        
        # Get the full path
        path = request.path
        
        # Allow public routes
        if is_public_route(path):
            logger.debug(f"Public route accessed: {path}")
            return None
        
        # All other routes require authentication
        try:
            # Verify JWT token
            verify_jwt_in_request(optional=False)
            user_id = get_jwt_identity()
            
            if not user_id:
                logger.warning(f"Unauthenticated access attempt: {path}")
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Valid JWT token required. Please login first.'
                }), 401
            
            # Store user ID in request context
            g.current_user_id = user_id
            logger.debug(f"Authenticated request: {path} by user {user_id}")
            
            return None  # Continue to route handler
            
        except Exception as e:
            # JWT verification failed
            logger.warning(f"Authentication failed for {path}: {str(e)}")
            return jsonify({
                'error': 'Authentication required',
                'message': 'Valid JWT token required. Please login first.',
                'path': path
            }), 401

