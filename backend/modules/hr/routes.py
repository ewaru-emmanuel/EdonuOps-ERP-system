# backend/modules/hr/routes.py

from flask import Blueprint, jsonify, request
from app import db
from modules.hr.models import Employee, Payroll, Recruitment
from datetime import datetime

bp = Blueprint('hr', __name__, url_prefix='/api/hr')

# Employee endpoints
@bp.route('/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    try:
        employees = Employee.query.all()
        return jsonify([{
            "id": emp.id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "phone": emp.phone,
            "position": emp.position,
            "department": emp.department,
            "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
            "salary": emp.salary,
            "status": emp.status,
            "created_at": emp.created_at.isoformat() if emp.created_at else None
        } for emp in employees]), 200
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return jsonify({"error": "Failed to fetch employees"}), 500

@bp.route('/employees', methods=['POST'])
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        
        employee = Employee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            position=data.get('position'),
            department=data.get('department'),
            hire_date=datetime.fromisoformat(data['hire_date']) if data.get('hire_date') else None,
            salary=data.get('salary', 0.0),
            status=data.get('status', 'active')
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            "id": employee.id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email": employee.email,
            "phone": employee.phone,
            "position": employee.position,
            "department": employee.department,
            "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
            "salary": employee.salary,
            "status": employee.status,
            "created_at": employee.created_at.isoformat() if employee.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating employee: {e}")
        return jsonify({"error": "Failed to create employee"}), 500

@bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Update an employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        employee.first_name = data.get('first_name', employee.first_name)
        employee.last_name = data.get('last_name', employee.last_name)
        employee.email = data.get('email', employee.email)
        employee.phone = data.get('phone', employee.phone)
        employee.position = data.get('position', employee.position)
        employee.department = data.get('department', employee.department)
        if data.get('hire_date'):
            employee.hire_date = datetime.fromisoformat(data['hire_date'])
        employee.salary = data.get('salary', employee.salary)
        employee.status = data.get('status', employee.status)
        
        db.session.commit()
        
        return jsonify({
            "id": employee.id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email": employee.email,
            "phone": employee.phone,
            "position": employee.position,
            "department": employee.department,
            "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
            "salary": employee.salary,
            "status": employee.status,
            "created_at": employee.created_at.isoformat() if employee.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating employee: {e}")
        return jsonify({"error": "Failed to update employee"}), 500

@bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({"message": "Employee deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting employee: {e}")
        return jsonify({"error": "Failed to delete employee"}), 500

# Payroll endpoints
@bp.route('/payroll', methods=['GET'])
def get_payroll():
    """Get all payroll records"""
    try:
        payroll_records = Payroll.query.all()
        return jsonify([{
            "id": pr.id,
            "employee_id": pr.employee_id,
            "period": pr.period,
            "gross_pay": pr.gross_pay,
            "net_pay": pr.net_pay,
            "status": pr.status,
            "created_at": pr.created_at.isoformat() if pr.created_at else None
        } for pr in payroll_records]), 200
    except Exception as e:
        print(f"Error fetching payroll: {e}")
        return jsonify({"error": "Failed to fetch payroll"}), 500

@bp.route('/payroll', methods=['POST'])
def create_payroll():
    """Create a new payroll record"""
    try:
        data = request.get_json()
        
        payroll = Payroll(
            employee_id=data['employee_id'],
            period=data['period'],
            gross_pay=data.get('gross_pay', 0.0),
            net_pay=data.get('net_pay', 0.0),
            status=data.get('status', 'pending')
        )
        
        db.session.add(payroll)
        db.session.commit()
        
        return jsonify({
            "id": payroll.id,
            "employee_id": payroll.employee_id,
            "period": payroll.period,
            "gross_pay": payroll.gross_pay,
            "net_pay": payroll.net_pay,
            "status": payroll.status,
            "created_at": payroll.created_at.isoformat() if payroll.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating payroll: {e}")
        return jsonify({"error": "Failed to create payroll"}), 500

@bp.route('/payroll/<int:payroll_id>', methods=['PUT'])
def update_payroll(payroll_id):
    """Update a payroll record"""
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        data = request.get_json()
        
        payroll.employee_id = data.get('employee_id', payroll.employee_id)
        payroll.period = data.get('period', payroll.period)
        payroll.gross_pay = data.get('gross_pay', payroll.gross_pay)
        payroll.net_pay = data.get('net_pay', payroll.net_pay)
        payroll.status = data.get('status', payroll.status)
        
        db.session.commit()
        
        return jsonify({
            "id": payroll.id,
            "employee_id": payroll.employee_id,
            "period": payroll.period,
            "gross_pay": payroll.gross_pay,
            "net_pay": payroll.net_pay,
            "status": payroll.status,
            "created_at": payroll.created_at.isoformat() if payroll.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating payroll: {e}")
        return jsonify({"error": "Failed to update payroll"}), 500

@bp.route('/payroll/<int:payroll_id>', methods=['DELETE'])
def delete_payroll(payroll_id):
    """Delete a payroll record"""
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        db.session.delete(payroll)
        db.session.commit()
        
        return jsonify({"message": "Payroll record deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting payroll: {e}")
        return jsonify({"error": "Failed to delete payroll"}), 500

# Recruitment endpoints
@bp.route('/recruitment', methods=['GET'])
def get_recruitment():
    """Get all recruitment records"""
    try:
        recruitment_records = Recruitment.query.all()
        return jsonify([{
            "id": rec.id,
            "position": rec.position,
            "department": rec.department,
            "status": rec.status,
            "applications": rec.applications,
            "created_at": rec.created_at.isoformat() if rec.created_at else None
        } for rec in recruitment_records]), 200
    except Exception as e:
        print(f"Error fetching recruitment: {e}")
        return jsonify({"error": "Failed to fetch recruitment"}), 500

@bp.route('/recruitment', methods=['POST'])
def create_recruitment():
    """Create a new recruitment record"""
    try:
        data = request.get_json()
        
        recruitment = Recruitment(
            position=data['position'],
            department=data.get('department'),
            status=data.get('status', 'open'),
            applications=data.get('applications', 0)
        )
        
        db.session.add(recruitment)
        db.session.commit()
        
        return jsonify({
            "id": recruitment.id,
            "position": recruitment.position,
            "department": recruitment.department,
            "status": recruitment.status,
            "applications": recruitment.applications,
            "created_at": recruitment.created_at.isoformat() if recruitment.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating recruitment: {e}")
        return jsonify({"error": "Failed to create recruitment"}), 500

@bp.route('/recruitment/<int:recruitment_id>', methods=['PUT'])
def update_recruitment(recruitment_id):
    """Update a recruitment record"""
    try:
        recruitment = Recruitment.query.get_or_404(recruitment_id)
        data = request.get_json()
        
        recruitment.position = data.get('position', recruitment.position)
        recruitment.department = data.get('department', recruitment.department)
        recruitment.status = data.get('status', recruitment.status)
        recruitment.applications = data.get('applications', recruitment.applications)
        
        db.session.commit()
        
        return jsonify({
            "id": recruitment.id,
            "position": recruitment.position,
            "department": recruitment.department,
            "status": recruitment.status,
            "applications": recruitment.applications,
            "created_at": recruitment.created_at.isoformat() if recruitment.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating recruitment: {e}")
        return jsonify({"error": "Failed to update recruitment"}), 500

@bp.route('/recruitment/<int:recruitment_id>', methods=['DELETE'])
def delete_recruitment(recruitment_id):
    """Delete a recruitment record"""
    try:
        recruitment = Recruitment.query.get_or_404(recruitment_id)
        db.session.delete(recruitment)
        db.session.commit()
        
        return jsonify({"message": "Recruitment record deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting recruitment: {e}")
        return jsonify({"error": "Failed to delete recruitment"}), 500