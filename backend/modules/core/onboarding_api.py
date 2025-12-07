#!/usr/bin/env python3
"""
📋 EDONUOPS ERP - COMPREHENSIVE ONBOARDING API
============================================================

Progressive onboarding API with comprehensive user data collection:
- Step-by-step onboarding workflow
- Rich user profile data collection
- Tenant-specific onboarding flows
- Enhanced validation for all fields
- Profile completion tracking

Author: EdonuOps Team
Date: 2024
"""

import os
import logging
import re
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Import database and models
from app import db
from modules.core.models import User, Role
from modules.core.tenant_models import Tenant
from modules.core.tenant_context import get_current_tenant, audit_tenant_access
from modules.core.tenant_helpers import get_current_user_tenant_id, get_current_user_id
from modules.core.tenant_query_helper import tenant_query

# Setup logging
logger = logging.getLogger(__name__)

# Create Blueprint
onboarding_bp = Blueprint("onboarding", __name__)

class OnboardingValidator:
    """Comprehensive validation for onboarding fields"""
    
    @staticmethod
    def validate_personal_info(data):
        """Validate personal information fields"""
        errors = {}
        
        # First Name validation
        if 'first_name' in data:
            first_name = data['first_name'].strip()
            if not first_name:
                errors['first_name'] = 'First name is required'
            elif len(first_name) < 2:
                errors['first_name'] = 'First name must be at least 2 characters'
            elif len(first_name) > 100:
                errors['first_name'] = 'First name must be less than 100 characters'
            elif not re.match(r'^[a-zA-Z\s\-\.\']+$', first_name):
                errors['first_name'] = 'First name contains invalid characters'
        
        # Last Name validation
        if 'last_name' in data:
            last_name = data['last_name'].strip()
            if not last_name:
                errors['last_name'] = 'Last name is required'
            elif len(last_name) < 2:
                errors['last_name'] = 'Last name must be at least 2 characters'
            elif len(last_name) > 100:
                errors['last_name'] = 'Last name must be less than 100 characters'
            elif not re.match(r'^[a-zA-Z\s\-\.\']+$', last_name):
                errors['last_name'] = 'Last name contains invalid characters'
        
        # Phone Number validation
        if 'phone_number' in data and data['phone_number']:
            phone = data['phone_number'].strip()
            if not re.match(r'^[\+]?[1-9][\d]{0,15}$', phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                errors['phone_number'] = 'Invalid phone number format'
        
        # Date of Birth validation
        if 'date_of_birth' in data and data['date_of_birth']:
            try:
                dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                if dob > datetime.now().date():
                    errors['date_of_birth'] = 'Date of birth cannot be in the future'
                elif dob.year < 1900:
                    errors['date_of_birth'] = 'Date of birth must be after 1900'
            except ValueError:
                errors['date_of_birth'] = 'Invalid date format (YYYY-MM-DD)'
        
        # Gender validation
        if 'gender' in data and data['gender']:
            valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
            if data['gender'].lower() not in valid_genders:
                errors['gender'] = f'Gender must be one of: {", ".join(valid_genders)}'
        
        return errors
    
    @staticmethod
    def validate_professional_info(data):
        """Validate professional information fields"""
        errors = {}
        
        # Job Title validation
        if 'job_title' in data:
            job_title = data['job_title'].strip()
            if not job_title:
                errors['job_title'] = 'Job title is required'
            elif len(job_title) > 100:
                errors['job_title'] = 'Job title must be less than 100 characters'
        
        # Department validation
        if 'department' in data:
            department = data['department'].strip()
            if not department:
                errors['department'] = 'Department is required'
            elif len(department) > 100:
                errors['department'] = 'Department must be less than 100 characters'
        
        # Employee ID validation
        if 'employee_id' in data and data['employee_id']:
            emp_id = data['employee_id'].strip()
            if len(emp_id) > 50:
                errors['employee_id'] = 'Employee ID must be less than 50 characters'
        
        # Hire Date validation
        if 'hire_date' in data and data['hire_date']:
            try:
                hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
                if hire_date > datetime.now().date():
                    errors['hire_date'] = 'Hire date cannot be in the future'
            except ValueError:
                errors['hire_date'] = 'Invalid date format (YYYY-MM-DD)'
        
        # Employment Type validation
        if 'employment_type' in data and data['employment_type']:
            valid_types = ['full-time', 'part-time', 'contractor', 'intern', 'consultant']
            if data['employment_type'].lower() not in valid_types:
                errors['employment_type'] = f'Employment type must be one of: {", ".join(valid_types)}'
        
        # Experience Years validation
        if 'experience_years' in data and data['experience_years']:
            try:
                exp_years = int(data['experience_years'])
                if exp_years < 0 or exp_years > 50:
                    errors['experience_years'] = 'Experience years must be between 0 and 50'
            except ValueError:
                errors['experience_years'] = 'Experience years must be a valid number'
        
        return errors
    
    @staticmethod
    def validate_company_info(data):
        """Validate company information fields"""
        errors = {}
        
        # Company Name validation
        if 'company_name' in data:
            company_name = data['company_name'].strip()
            if not company_name:
                errors['company_name'] = 'Company name is required'
            elif len(company_name) > 200:
                errors['company_name'] = 'Company name must be less than 200 characters'
        
        # Industry validation
        if 'industry' in data:
            industry = data['industry'].strip()
            if not industry:
                errors['industry'] = 'Industry is required'
            elif len(industry) > 100:
                errors['industry'] = 'Industry must be less than 100 characters'
        
        # Company Size validation
        if 'company_size' in data and data['company_size']:
            valid_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
            if data['company_size'].lower() not in valid_sizes:
                errors['company_size'] = f'Company size must be one of: {", ".join(valid_sizes)}'
        
        # Website validation
        if 'company_website' in data and data['company_website']:
            website = data['company_website'].strip()
            if not re.match(r'^https?:\/\/[^\s\/$.?#].[^\s]*$', website):
                errors['company_website'] = 'Invalid website URL format'
        
        # Email validation
        if 'company_email' in data and data['company_email']:
            email = data['company_email'].strip()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors['company_email'] = 'Invalid email format'
        
        return errors
    
    @staticmethod
    def validate_contact_info(data):
        """Validate contact information fields"""
        errors = {}
        
        # Address validation
        if 'address_line1' in data and data['address_line1']:
            if len(data['address_line1']) > 255:
                errors['address_line1'] = 'Address line 1 must be less than 255 characters'
        
        if 'city' in data and data['city']:
            if len(data['city']) > 100:
                errors['city'] = 'City must be less than 100 characters'
        
        if 'state' in data and data['state']:
            if len(data['state']) > 100:
                errors['state'] = 'State must be less than 100 characters'
        
        if 'postal_code' in data and data['postal_code']:
            if len(data['postal_code']) > 20:
                errors['postal_code'] = 'Postal code must be less than 20 characters'
        
        if 'country' in data and data['country']:
            if len(data['country']) > 100:
                errors['country'] = 'Country must be less than 100 characters'
        
        return errors
    
    @staticmethod
    def validate_social_links(data):
        """Validate social and professional links"""
        errors = {}
        
        # LinkedIn validation
        if 'linkedin_url' in data and data['linkedin_url']:
            linkedin = data['linkedin_url'].strip()
            if not re.match(r'^https?:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]+\/?$', linkedin):
                errors['linkedin_url'] = 'Invalid LinkedIn profile URL'
        
        # GitHub validation
        if 'github_url' in data and data['github_url']:
            github = data['github_url'].strip()
            if not re.match(r'^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9\-]+\/?$', github):
                errors['github_url'] = 'Invalid GitHub profile URL'
        
        # Twitter validation
        if 'twitter_url' in data and data['twitter_url']:
            twitter = data['twitter_url'].strip()
            if not re.match(r'^https?:\/\/(www\.)?twitter\.com\/[a-zA-Z0-9_]+\/?$', twitter):
                errors['twitter_url'] = 'Invalid Twitter profile URL'
        
        # Website validation
        if 'website_url' in data and data['website_url']:
            website = data['website_url'].strip()
            if not re.match(r'^https?:\/\/[^\s\/$.?#].[^\s]*$', website):
                errors['website_url'] = 'Invalid website URL format'
        
        return errors
    
    @staticmethod
    def validate_emergency_contact(data):
        """Validate emergency contact information"""
        errors = {}
        
        # Emergency Contact Name validation
        if 'emergency_contact_name' in data and data['emergency_contact_name']:
            name = data['emergency_contact_name'].strip()
            if len(name) < 2:
                errors['emergency_contact_name'] = 'Emergency contact name must be at least 2 characters'
            elif len(name) > 100:
                errors['emergency_contact_name'] = 'Emergency contact name must be less than 100 characters'
        
        # Emergency Contact Phone validation
        if 'emergency_contact_phone' in data and data['emergency_contact_phone']:
            phone = data['emergency_contact_phone'].strip()
            if not re.match(r'^[\+]?[1-9][\d]{0,15}$', phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                errors['emergency_contact_phone'] = 'Invalid emergency contact phone number'
        
        # Emergency Contact Relationship validation
        if 'emergency_contact_relationship' in data and data['emergency_contact_relationship']:
            relationship = data['emergency_contact_relationship'].strip()
            if len(relationship) > 50:
                errors['emergency_contact_relationship'] = 'Relationship must be less than 50 characters'
        
        return errors

@onboarding_bp.route("/steps", methods=["GET"])
@jwt_required()
def get_onboarding_steps():
    """Get all onboarding steps for current tenant"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                "message": "User not found"
            }), 404
        
        tenant_id = current_user.tenant_id
        
        # Get onboarding steps
        result = db.session.execute(text("""
            SELECT 
                step_name, step_title, step_description, step_order,
                is_required, is_skippable, component_name, validation_rules
            FROM onboarding_steps
            WHERE tenant_specific = FALSE OR tenant_id = :tenant_id
            ORDER BY step_order
        """), {'tenant_id': tenant_id})
        
        steps = []
        for row in result:
            steps.append({
                "step_name": row.step_name,
                "step_title": row.step_title,
                "step_description": row.step_description,
                "step_order": row.step_order,
                "is_required": row.is_required,
                "is_skippable": row.is_skippable,
                "component_name": row.component_name,
                "validation_rules": row.validation_rules
            })
        
        return jsonify({
            "message": "Onboarding steps retrieved successfully",
            "steps": steps
        }), 200
        
    except Exception as e:
        logger.error(f"Get onboarding steps error: {e}")
        return jsonify({
            "message": "Failed to retrieve onboarding steps"
        }), 500

@onboarding_bp.route("/progress", methods=["GET"])
@jwt_required()
def get_onboarding_progress():
    """Get user's onboarding progress"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get onboarding progress using database function
        result = db.session.execute(text("""
            SELECT * FROM get_onboarding_progress(:user_id)
        """), {'user_id': current_user_id})
        
        progress = []
        for row in result:
            progress.append({
                "step_name": row.step_name,
                "step_title": row.step_title,
                "step_description": row.step_description,
                "step_order": row.step_order,
                "is_required": row.is_required,
                "is_skippable": row.is_skippable,
                "completed": row.completed,
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                "skipped": row.skipped,
                "data": row.data
            })
        
        # Get user's profile completion percentage
        completion_result = db.session.execute(text("""
            SELECT calculate_profile_completion(:user_id)
        """), {'user_id': current_user_id})
        
        completion_percentage = completion_result.scalar()
        
        return jsonify({
            "message": "Onboarding progress retrieved successfully",
            "progress": progress,
            "completion_percentage": completion_percentage
        }), 200
        
    except Exception as e:
        logger.error(f"Get onboarding progress error: {e}")
        return jsonify({
            "message": "Failed to retrieve onboarding progress"
        }), 500

@onboarding_bp.route("/step/<step_name>", methods=["POST"])
@jwt_required()
def complete_onboarding_step(step_name):
    """Complete an onboarding step - TENANT-CENTRIC (like CoA)"""
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id using the same pattern as CoA
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        data = request.get_json()
        
        # Validate step data based on step name
        validation_errors = {}
        
        if step_name == 'personal_info':
            validation_errors = OnboardingValidator.validate_personal_info(data)
        elif step_name == 'professional_info':
            validation_errors = OnboardingValidator.validate_professional_info(data)
        elif step_name == 'company_info':
            validation_errors = OnboardingValidator.validate_company_info(data)
        elif step_name == 'contact_info':
            validation_errors = OnboardingValidator.validate_contact_info(data)
        elif step_name == 'social_links':
            validation_errors = OnboardingValidator.validate_social_links(data)
        elif step_name == 'emergency_contact':
            validation_errors = OnboardingValidator.validate_emergency_contact(data)
        
        if validation_errors:
            return jsonify({
                "message": "Validation failed",
                "errors": validation_errors
            }), 400
        
        # Update user profile with step data - TENANT-CENTRIC
        # Ensure user belongs to the tenant before updating
        user = tenant_query(User).filter_by(id=user_id_int).first()
        if not user:
            return jsonify({"error": "User not found or access denied"}), 404
        
        update_fields = []
        update_values = {}
        
        # Map frontend field names (camelCase) to database column names (snake_case)
        field_mapping = {
            'companyName': 'company_name',
            'companySize': 'company_size',
            'employeeCount': 'company_size',  # Map employeeCount to company_size
            'companyWebsite': 'company_website',
            'companyAddress': 'company_address',
            'companyPhone': 'company_phone',
            'companyEmail': 'company_email',
            'annualRevenue': 'annual_revenue',
            'challenges': None,  # Store in onboarding_progress.data JSONB
            'pain_points': None,  # Store in onboarding_progress.data JSONB
            'goals': None,  # Store in onboarding_progress.data JSONB
        }
        
        for field, value in data.items():
            if value is not None and value != '':
                # Map field name if needed
                db_field = field_mapping.get(field, field)
                
                # Skip fields that should be stored in JSONB
                if db_field is None:
                    continue
                
                # Only update if field exists in users table
                if hasattr(User, db_field):
                    update_fields.append(f"{db_field} = :{db_field}")
                    update_values[db_field] = value
        
        if update_fields:
            update_sql = f"""
                UPDATE users 
                SET {', '.join(update_fields)}, last_profile_update = NOW()
                WHERE id = :user_id AND tenant_id = :tenant_id
            """
            update_values['user_id'] = user_id_int
            update_values['tenant_id'] = tenant_id
            
            from modules.core.tenant_sql_helper import tenant_sql_query
            tenant_sql_query(update_sql, update_values)
        
        # Update tenant name if company_info step and company_name is provided
        if step_name == 'company_info' and data.get('companyName'):
            company_name = data.get('companyName')
            tenant = Tenant.query.filter_by(id=tenant_id).first()
            if tenant:
                tenant.name = company_name
                db.session.add(tenant)
                logger.info(f"✅ Updated tenant {tenant_id} name to: {company_name}")
        
        # Complete the onboarding step - TENANT-CENTRIC
        skipped = data.get('skipped', False)
        
        # Store full data in onboarding_progress table (including challenges, pain_points, etc.)
        import json
        data_json = json.dumps(data)
        
        result = db.session.execute(text("""
            SELECT complete_onboarding_step(:user_id, :step_name, :data, :skipped)
        """), {
            'user_id': user_id_int,
            'step_name': step_name,
            'data': data_json,
            'skipped': skipped
        })
        
        success = result.scalar()
        
        if not success:
            return jsonify({
                "message": "Failed to complete onboarding step"
            }), 400
        
        # Calculate profile completion percentage
        completion_result = db.session.execute(text("""
            SELECT calculate_profile_completion(:user_id)
        """), {'user_id': current_user_id})
        
        completion_percentage = completion_result.scalar()
        
        db.session.commit()
        
        return jsonify({
            "message": f"Onboarding step '{step_name}' completed successfully",
            "completion_percentage": completion_percentage,
            "skipped": skipped
        }), 200
        
    except Exception as e:
        logger.error(f"Complete onboarding step error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Failed to complete onboarding step"
        }), 500

@onboarding_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """Get user's complete profile"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user profile
        result = db.session.execute(text("""
            SELECT 
                id, username, email, first_name, last_name, middle_name,
                phone_number, mobile_number, date_of_birth, gender,
                profile_picture_url, bio, timezone, language,
                job_title, department, employee_id, manager_id,
                hire_date, employment_type, work_location, skills,
                certifications, experience_years,
                company_name, company_size, industry, company_website,
                company_address, company_phone, company_email,
                address_line1, address_line2, city, state, postal_code, country,
                emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
                linkedin_url, twitter_url, github_url, website_url, portfolio_url,
                notification_preferences, dashboard_preferences, privacy_settings,
                theme_preference, email_frequency, sms_notifications, marketing_emails,
                onboarding_completed, onboarding_step, profile_completion_percentage,
                last_profile_update, created_at, updated_at
            FROM users
            WHERE id = :user_id
        """), {'user_id': current_user_id})
        
        user_data = result.fetchone()
        
        if not user_data:
            return jsonify({
                "message": "User not found"
            }), 404
        
        # Convert to dictionary
        profile = {}
        for key, value in user_data._mapping.items():
            if isinstance(value, datetime):
                profile[key] = value.isoformat()
            else:
                profile[key] = value
        
        return jsonify({
            "message": "User profile retrieved successfully",
            "profile": profile
        }), 200
        
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        return jsonify({
            "message": "Failed to retrieve user profile"
        }), 500

@onboarding_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_user_profile():
    """Update user's profile - TENANT-CENTRIC (like CoA)"""
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id using the same pattern as CoA
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        data = request.get_json()
        
        # Validate all fields
        validation_errors = {}
        validation_errors.update(OnboardingValidator.validate_personal_info(data))
        validation_errors.update(OnboardingValidator.validate_professional_info(data))
        validation_errors.update(OnboardingValidator.validate_company_info(data))
        validation_errors.update(OnboardingValidator.validate_contact_info(data))
        validation_errors.update(OnboardingValidator.validate_social_links(data))
        validation_errors.update(OnboardingValidator.validate_emergency_contact(data))
        
        if validation_errors:
            return jsonify({
                "message": "Validation failed",
                "errors": validation_errors
            }), 400
        
        # Ensure user belongs to the tenant before updating
        user = tenant_query(User).filter_by(id=user_id_int).first()
        if not user:
            return jsonify({"error": "User not found or access denied"}), 404
        
        # Update user profile - TENANT-CENTRIC
        update_fields = []
        update_values = {}
        
        # Map frontend field names to database column names
        field_mapping = {
            'companyName': 'company_name',
            'companySize': 'company_size',
            'employeeCount': 'company_size',
        }
        
        for field, value in data.items():
            if value is not None:
                # Map field name if needed
                db_field = field_mapping.get(field, field)
                
                # Only update if field exists in users table
                if hasattr(User, db_field):
                    update_fields.append(f"{db_field} = :{db_field}")
                    update_values[db_field] = value
        
        if update_fields:
            update_sql = f"""
                UPDATE users 
                SET {', '.join(update_fields)}, last_profile_update = NOW()
                WHERE id = :user_id AND tenant_id = :tenant_id
            """
            update_values['user_id'] = user_id_int
            update_values['tenant_id'] = tenant_id
            
            from modules.core.tenant_sql_helper import tenant_sql_query
            tenant_sql_query(update_sql, update_values)
        
        # Calculate profile completion percentage
        completion_result = db.session.execute(text("""
            SELECT calculate_profile_completion(:user_id)
        """), {'user_id': user_id_int})
        
        completion_percentage = completion_result.scalar()
        
        db.session.commit()
        
        return jsonify({
            "message": "Profile updated successfully",
            "completion_percentage": completion_percentage
        }), 200
        
    except Exception as e:
        logger.error(f"Update user profile error: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            "message": f"Failed to update profile: {str(e)}"
        }), 500

@onboarding_bp.route("/complete", methods=["POST"])
@jwt_required()
def complete_onboarding():
    """Mark onboarding as completed - TENANT-CENTRIC (like CoA)"""
    try:
        # TENANT-CENTRIC: Get tenant_id and user_id using the same pattern as CoA
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403
        
        # Ensure user belongs to the tenant before updating
        user = tenant_query(User).filter_by(id=user_id_int).first()
        if not user:
            return jsonify({"error": "User not found or access denied"}), 404
        
        # Mark onboarding as completed - TENANT-CENTRIC
        db.session.execute(text("""
            UPDATE users 
            SET onboarding_completed = TRUE, onboarding_completed_at = NOW()
            WHERE id = :user_id AND tenant_id = :tenant_id
        """), {'user_id': user_id_int, 'tenant_id': tenant_id})
        
        db.session.commit()
        
        return jsonify({
            "message": "Onboarding completed successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Complete onboarding error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Failed to complete onboarding"
        }), 500

@onboarding_bp.route("/skip-step/<step_name>", methods=["POST"])
@jwt_required()
def skip_onboarding_step(step_name):
    """Skip an onboarding step"""
    try:
        current_user_id = get_jwt_identity()
        
        # Skip the onboarding step
        result = db.session.execute(text("""
            SELECT complete_onboarding_step(:user_id, :step_name, '{}', TRUE)
        """), {
            'user_id': current_user_id,
            'step_name': step_name
        })
        
        success = result.scalar()
        
        if not success:
            return jsonify({
                "message": "Failed to skip onboarding step"
            }), 400
        
        db.session.commit()
        
        return jsonify({
            "message": f"Onboarding step '{step_name}' skipped successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Skip onboarding step error: {e}")
        db.session.rollback()
        return jsonify({
            "message": "Failed to skip onboarding step"
        }), 500

