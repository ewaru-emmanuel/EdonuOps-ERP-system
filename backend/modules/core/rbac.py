# backend/core/rbac.py

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from .auth import User

def requires_roles(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user and user.role in roles:
                return fn(*args, **kwargs)
            else:
                return jsonify({"message": "Access forbidden: Insufficient permissions"}), 403
        return decorator
    return wrapper