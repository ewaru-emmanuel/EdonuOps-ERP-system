from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify

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
