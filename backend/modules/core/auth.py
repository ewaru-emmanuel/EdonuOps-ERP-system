# backend/modules/core/auth.py

from flask import Blueprint, request, jsonify
from app import db
from .models import User, Role
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services.audit_logger_service import audit_logger
from services.security_service import security_service
from werkzeug.security import generate_password_hash, check_password_hash
from modules.core.models import User  # make sure this import exists

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role_name = data.get("role", "user")

    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    # Validate password against security policy
    is_valid, errors = security_service.validate_password(password, username)
    if not is_valid:
        return jsonify({
            "message": "Password does not meet security requirements",
            "errors": errors
        }), 400

    hashed_password = generate_password_hash(password)

    role = Role.query.filter_by(role_name=role_name).first()
    if not role:
        # Create default roles if they don't exist
        user_role = Role.query.filter_by(role_name="user").first()
        if not user_role:
            user_role = Role(role_name="user")
            db.session.add(user_role)
        admin_role = Role.query.filter_by(role_name="admin").first()
        if not admin_role:
            admin_role = Role(role_name="admin")
            db.session.add(admin_role)
        db.session.commit()
        role = Role.query.filter_by(role_name=role_name).first()

    new_user = User(username=username, email=email, password_hash=hashed_password, role_id=role.id)
    db.session.add(new_user)
    db.session.commit()

    # Save password to history
    security_service.save_password_to_history(new_user.id, hashed_password)

    # Log user registration
    audit_logger.log_action(
        action='CREATE',
        entity_type='user',
        entity_id=str(new_user.id),
        new_values={'username': username, 'email': email, 'role': role_name},
        module='auth',
        source='api',
        success=True
    )

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    print(f"🔐 Login attempt for email: {email}")

    # Check for hardcoded admin user first (for testing)
    if email == 'admin@edonuops.com' and password == 'password':
        access_token = create_access_token(identity=email)
        print(f"🔐 Login successful for {email}")
        return jsonify({
            "access_token": access_token,
            "user": {
                "email": email,
                "username": "admin",
                "role": "admin"
            },
            "message": "Login successful"
        }), 200

    # Check database for other users
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": access_token,
            "user": {
                "email": user.email,
                "username": user.username,
                "role": user.role.role_name if user.role else "user"
            },
            "message": "Login successful"
        }), 200
    else:
        print(f"🔐 Invalid credentials for {email}")
        return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(logged_in_as=user.username), 200

@auth_bp.route("/verify", methods=["GET"])
def verify():
    """Simple verification endpoint for testing"""
    return jsonify({
        "message": "Token verification endpoint",
        "user": {
            "email": "admin@edonuops.com",
            "username": "admin", 
            "role": "admin"
        }
    }), 200






@auth_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "username": u.username, "email": u.email}
        for u in users
    ])
