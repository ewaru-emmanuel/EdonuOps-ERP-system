"""
Cost Center API Routes
=====================

This module provides API endpoints for cost center, department, and project management.
"""

from flask import Blueprint, request, jsonify
from app import db
from modules.finance.cost_center_service import cost_center_service
from modules.finance.cost_center_models import CostCenter, Department, Project
from datetime import datetime, date

# Create blueprint
cost_center_bp = Blueprint('cost_center', __name__, url_prefix='/api/finance/cost-centers')

# =============================================================================
# COST CENTER ENDPOINTS
# =============================================================================

@cost_center_bp.route('/cost-centers', methods=['GET', 'POST'])
def manage_cost_centers():
    """Manage cost centers (list and create)"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        # Validate required fields
        if not data.get('code') or not data.get('name'):
            return jsonify({"error": "Code and name are required"}), 400
        
        result = cost_center_service.create_cost_center(user_id_int, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify({"error": result['error']}), 400
    
    else:  # GET
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        cost_centers = cost_center_service.get_cost_centers(user_id_int, active_only)
        return jsonify(cost_centers), 200

@cost_center_bp.route('/cost-centers/<int:cost_center_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_cost_center(cost_center_id):
    """Manage individual cost center"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    cost_center = CostCenter.query.filter_by(id=cost_center_id, user_id=user_id_int).first()
    if not cost_center:
        return jsonify({"error": "Cost center not found"}), 404
    
    if request.method == 'GET':
        return jsonify(cost_center.to_dict()), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        # Update fields
        if 'name' in data:
            cost_center.name = data['name']
        if 'description' in data:
            cost_center.description = data['description']
        if 'budget_amount' in data:
            cost_center.budget_amount = float(data['budget_amount'])
        if 'responsible_manager' in data:
            cost_center.responsible_manager = data['responsible_manager']
        if 'is_active' in data:
            cost_center.is_active = data['is_active']
        
        cost_center.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Cost center updated successfully",
            "cost_center": cost_center.to_dict()
        }), 200
    
    elif request.method == 'DELETE':
        # Soft delete by setting is_active to False
        cost_center.is_active = False
        cost_center.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Cost center deactivated successfully"}), 200

# =============================================================================
# DEPARTMENT ENDPOINTS
# =============================================================================

@cost_center_bp.route('/departments', methods=['GET', 'POST'])
def manage_departments():
    """Manage departments (list and create)"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        # Validate required fields
        if not data.get('code') or not data.get('name'):
            return jsonify({"error": "Code and name are required"}), 400
        
        result = cost_center_service.create_department(user_id_int, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify({"error": result['error']}), 400
    
    else:  # GET
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        departments = cost_center_service.get_departments(user_id_int, active_only)
        return jsonify(departments), 200

@cost_center_bp.route('/departments/<int:department_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_department(department_id):
    """Manage individual department"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    department = Department.query.filter_by(id=department_id, user_id=user_id_int).first()
    if not department:
        return jsonify({"error": "Department not found"}), 404
    
    if request.method == 'GET':
        return jsonify(department.to_dict()), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        # Update fields
        if 'name' in data:
            department.name = data['name']
        if 'description' in data:
            department.description = data['description']
        if 'department_head' in data:
            department.department_head = data['department_head']
        if 'location' in data:
            department.location = data['location']
        if 'is_active' in data:
            department.is_active = data['is_active']
        
        department.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Department updated successfully",
            "department": department.to_dict()
        }), 200
    
    elif request.method == 'DELETE':
        # Soft delete by setting is_active to False
        department.is_active = False
        department.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Department deactivated successfully"}), 200

# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@cost_center_bp.route('/projects', methods=['GET', 'POST'])
def manage_projects():
    """Manage projects (list and create)"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        # Validate required fields
        if not data.get('code') or not data.get('name'):
            return jsonify({"error": "Code and name are required"}), 400
        
        result = cost_center_service.create_project(user_id_int, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify({"error": result['error']}), 400
    
    else:  # GET
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        projects = cost_center_service.get_projects(user_id_int, active_only)
        return jsonify(projects), 200

@cost_center_bp.route('/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_project(project_id):
    """Manage individual project"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    project = Project.query.filter_by(id=project_id, user_id=user_id_int).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    if request.method == 'GET':
        return jsonify(project.to_dict()), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data is required"}), 400
        
        # Update fields
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'project_type' in data:
            project.project_type = data['project_type']
        if 'status' in data:
            project.status = data['status']
        if 'budget_amount' in data:
            project.budget_amount = float(data['budget_amount'])
        if 'project_manager' in data:
            project.project_manager = data['project_manager']
        if 'client_name' in data:
            project.client_name = data['client_name']
        if 'is_active' in data:
            project.is_active = data['is_active']
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Project updated successfully",
            "project": project.to_dict()
        }), 200
    
    elif request.method == 'DELETE':
        # Soft delete by setting is_active to False
        project.is_active = False
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Project deactivated successfully"}), 200

# =============================================================================
# SUMMARY AND REPORTING ENDPOINTS
# =============================================================================

@cost_center_bp.route('/cost-centers/summary', methods=['GET'])
def get_cost_center_summary():
    """Get cost center summary with expenses and budget"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    # Get query parameters
    cost_center_id = request.args.get('cost_center_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        start_date = datetime.fromisoformat(start_date_str).date()
    if end_date_str:
        end_date = datetime.fromisoformat(end_date_str).date()
    
    result = cost_center_service.get_cost_center_summary(
        user_id_int, cost_center_id, start_date, end_date
    )
    
    if result['success']:
        return jsonify(result['summary']), 200
    else:
        return jsonify({"error": result['error']}), 500

@cost_center_bp.route('/departments/summary', methods=['GET'])
def get_department_summary():
    """Get department summary with expenses"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    # Get query parameters
    department_id = request.args.get('department_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        start_date = datetime.fromisoformat(start_date_str).date()
    if end_date_str:
        end_date = datetime.fromisoformat(end_date_str).date()
    
    result = cost_center_service.get_department_summary(
        user_id_int, department_id, start_date, end_date
    )
    
    if result['success']:
        return jsonify(result['summary']), 200
    else:
        return jsonify({"error": result['error']}), 500

@cost_center_bp.route('/projects/summary', methods=['GET'])
def get_project_summary():
    """Get project summary with expenses and budget"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    
    # Get query parameters
    project_id = request.args.get('project_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        start_date = datetime.fromisoformat(start_date_str).date()
    if end_date_str:
        end_date = datetime.fromisoformat(end_date_str).date()
    
    result = cost_center_service.get_project_summary(
        user_id_int, project_id, start_date, end_date
    )
    
    if result['success']:
        return jsonify(result['summary']), 200
    else:
        return jsonify({"error": result['error']}), 500

# =============================================================================
# COMBINED ENDPOINTS
# =============================================================================

@cost_center_bp.route('/all', methods=['GET'])
def get_all_cost_centers():
    """Get all cost centers, departments, and projects"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "User authentication required"}), 401
    
    user_id_int = int(user_id)
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    cost_centers = cost_center_service.get_cost_centers(user_id_int, active_only)
    departments = cost_center_service.get_departments(user_id_int, active_only)
    projects = cost_center_service.get_projects(user_id_int, active_only)
    
    return jsonify({
        'cost_centers': cost_centers,
        'departments': departments,
        'projects': projects
    }), 200

