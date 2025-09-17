from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify

# Simple auth decorator
def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception:
            # For development, allow requests without auth
            return fn(*args, **kwargs)
    return wrapper

# Simple JSON validation decorator
def validate_json(required_fields):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request
            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON data required"}), 400
            
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Simulated role-check decorator
def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            if not identity:
                return jsonify({"error": "Missing or invalid token"}), 401

            # If identity is a dict (recommended), extract role from it
            user_role = None
            if isinstance(identity, dict):
                user_role = identity.get("role")
            elif isinstance(identity, str):
                # Optionally: parse string identity format like "username:role"
                try:
                    user_role = identity.split(":")[1]
                except IndexError:
                    pass

            if user_role != required_role:
                return jsonify({"error": "Insufficient role permissions"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
