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
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role_name = data.get("role", "user")

        # Enhanced validation
        errors = {}
        
        if not username or len(username.strip()) < 3:
            errors["username"] = "Username must be at least 3 characters"
        
        if not email or "@" not in email:
            errors["email"] = "Valid email address is required"
        
        if not password or len(password) < 8:
            errors["password"] = "Password must be at least 8 characters"
        
        if errors:
            return jsonify({
                "message": "Validation failed",
                "errors": errors
            }), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                "message": "An account with this email already exists",
                "errors": {"email": "Email already registered"}
            }), 409

        # Check username uniqueness
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            return jsonify({
                "message": "Username already taken",
                "errors": {"username": "Username already exists"}
            }), 409

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

        hashed_password = generate_password_hash(password)

        # Get or create role
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

        # Create new user
        new_user = User(username=username, email=email, password_hash=hashed_password, role_id=role.id)
        db.session.add(new_user)
        db.session.commit()

        # Save password to history
        try:
            security_service.save_password_to_history(new_user.id, hashed_password)
        except:
            pass  # Continue if password history fails

        # Log user registration
        try:
            audit_logger.log_action(
                action='CREATE',
                entity_type='user',
                entity_id=str(new_user.id),
                new_values={'username': username, 'email': email, 'role': role_name},
                module='auth',
                source='api',
                success=True
            )
        except:
            pass  # Continue if audit logging fails

        return jsonify({
            "message": "User registered successfully",
            "user_id": new_user.id,
            "username": username,
            "email": email
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Registration error: {str(e)}")
        return jsonify({
            "message": "Registration failed",
            "error": str(e)
        }), 500

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

    if not user:
        print(f"🔐 Email not found: {email}")
        # Log failed login attempt
        audit_logger.log_action(
            action='LOGIN_FAILED',
            entity_type='user',
            entity_id=None,
            old_values={'email': email, 'reason': 'email_not_found'},
            module='auth',
            source='api',
            success=False
        )
        return jsonify({"message": "Email address not found"}), 401
    
    if not check_password_hash(user.password_hash, password):
        print(f"🔐 Invalid password for {email}")
        # Log failed login attempt
        audit_logger.log_action(
            action='LOGIN_FAILED',
            entity_type='user',
            entity_id=str(user.id),
            old_values={'email': email, 'reason': 'invalid_password'},
            module='auth',
            source='api',
            success=False
        )
        return jsonify({"message": "Incorrect password"}), 401
    
    # Successful login
    access_token = create_access_token(identity=user.id)
    
    # Log successful login
    audit_logger.log_action(
        action='LOGIN_SUCCESS',
        entity_type='user',
        entity_id=str(user.id),
        new_values={'email': email},
        module='auth',
        source='api',
        success=True
    )
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "email": user.email,
            "username": user.username,
            "role": user.role.role_name if user.role else "user"
        },
        "message": "Login successful"
    }), 200

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
