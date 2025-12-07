# Add this endpoint to verify JWT tokens (add after existing routes)

@auth_bp.route("/verify-token", methods=["GET"])
@jwt_required(optional=False)
def verify_token():
    """
    Verify if the current JWT token is valid and return user info.
    Used by frontend to validate stored tokens on session restore.
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
            return jsonify({
                'valid': False,
                'error': 'User not found'
            }), 404
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                'valid': False,
                'error': 'User account is inactive'
            }), 403
        
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
