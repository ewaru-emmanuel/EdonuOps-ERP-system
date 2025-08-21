# HCM routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.hcm.models import Employee, Payroll, Recruitment, Department
from datetime import datetime

hcm_bp = Blueprint('hcm', __name__)

@hcm_bp.route('/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    try:
        employees = Employee.query.all()
        return jsonify([{
            'id': emp.id,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'name': f"{emp.first_name} {emp.last_name}",
            'email': emp.email,
            'phone': emp.phone,
            'position': emp.position,
            'department': emp.department.name if emp.department else None,
            'department_id': emp.department_id,
            'salary': emp.salary,
            'status': emp.status,
            'hire_date': emp.hire_date.isoformat() if emp.hire_date else None,
            'created_at': emp.created_at.isoformat() if emp.created_at else None
        } for emp in employees]), 200
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return jsonify({'error': 'Failed to fetch employees'}), 500

@hcm_bp.route('/payroll', methods=['GET'])
def get_payroll():
    """Get payroll data"""
    try:
        payroll_records = Payroll.query.all()
        return jsonify([{
            'id': pay.id,
            'employee_id': pay.employee_id,
            'employee': f"{pay.employee.first_name} {pay.employee.last_name}" if pay.employee else 'Unknown',
            'period': pay.period,
            'gross_pay': pay.gross_pay,
            'net_pay': pay.net_pay,
            'status': pay.status,
            'created_at': pay.created_at.isoformat() if pay.created_at else None
        } for pay in payroll_records]), 200
    except Exception as e:
        print(f"Error fetching payroll: {e}")
        return jsonify({'error': 'Failed to fetch payroll data'}), 500

@hcm_bp.route('/recruitment', methods=['GET'])
def get_recruitment():
    """Get recruitment data"""
    try:
        recruitment_records = Recruitment.query.all()
        return jsonify([{
            'id': rec.id,
            'position': rec.position,
            'department': rec.department,
            'status': rec.status,
            'applications': rec.applications,
            'created_at': rec.created_at.isoformat() if rec.created_at else None
        } for rec in recruitment_records]), 200
    except Exception as e:
        print(f"Error fetching recruitment: {e}")
        return jsonify({'error': 'Failed to fetch recruitment data'}), 500

@hcm_bp.route('/departments', methods=['GET'])
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.all()
        return jsonify([{
            'id': dept.id,
            'name': dept.name,
            'code': dept.code,
            'description': dept.description,
            'manager_id': dept.manager_id,
            'budget': dept.budget,
            'is_active': dept.is_active,
            'created_at': dept.created_at.isoformat() if dept.created_at else None
        } for dept in departments]), 200
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return jsonify({'error': 'Failed to fetch departments'}), 500

@hcm_bp.route('/employees', methods=['POST'])
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        
        new_employee = Employee(
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            position=data.get('position', ''),
            department_id=data.get('department_id'),
            salary=data.get('salary', 0.0),
            status=data.get('status', 'active'),
            hire_date=datetime.fromisoformat(data.get('hire_date')) if data.get('hire_date') else None
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Employee created successfully',
            'data': {
                'id': new_employee.id,
                'first_name': new_employee.first_name,
                'last_name': new_employee.last_name,
                'name': f"{new_employee.first_name} {new_employee.last_name}",
                'email': new_employee.email,
                'phone': new_employee.phone,
                'position': new_employee.position,
                'department': new_employee.department.name if new_employee.department else None,
                'department_id': new_employee.department_id,
                'salary': new_employee.salary,
                'status': new_employee.status,
                'hire_date': new_employee.hire_date.isoformat() if new_employee.hire_date else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating employee: {e}")
        return jsonify({'error': 'Failed to create employee'}), 500

@hcm_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Update an employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        if 'first_name' in data:
            employee.first_name = data['first_name']
        if 'last_name' in data:
            employee.last_name = data['last_name']
        if 'email' in data:
            employee.email = data['email']
        if 'phone' in data:
            employee.phone = data['phone']
        if 'position' in data:
            employee.position = data['position']
        if 'department_id' in data:
            employee.department_id = data['department_id']
        if 'salary' in data:
            employee.salary = data['salary']
        if 'status' in data:
            employee.status = data['status']
        if 'hire_date' in data and data['hire_date']:
            employee.hire_date = datetime.fromisoformat(data['hire_date'])
        
        employee.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Employee {employee_id} updated successfully',
            'data': {
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'name': f"{employee.first_name} {employee.last_name}",
                'email': employee.email,
                'phone': employee.phone,
                'position': employee.position,
                'department': employee.department.name if employee.department else None,
                'department_id': employee.department_id,
                'salary': employee.salary,
                'status': employee.status,
                'hire_date': employee.hire_date.isoformat() if employee.hire_date else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating employee: {e}")
        return jsonify({'error': 'Failed to update employee'}), 500

@hcm_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Employee {employee_id} deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting employee: {e}")
        return jsonify({'error': 'Failed to delete employee'}), 500

@hcm_bp.route('/payroll', methods=['POST'])
def create_payroll():
    """Create a new payroll record"""
    try:
        data = request.get_json()
        
        new_payroll = Payroll(
            employee_id=data.get('employee_id'),
            period=data.get('period', '2024-01'),
            gross_pay=data.get('gross_pay', 0.0),
            net_pay=data.get('net_pay', 0.0),
            status=data.get('status', 'pending')
        )
        
        db.session.add(new_payroll)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Payroll record created successfully',
            'data': {
                'id': new_payroll.id,
                'employee_id': new_payroll.employee_id,
                'employee': f"{new_payroll.employee.first_name} {new_payroll.employee.last_name}" if new_payroll.employee else 'Unknown',
                'period': new_payroll.period,
                'gross_pay': new_payroll.gross_pay,
                'net_pay': new_payroll.net_pay,
                'status': new_payroll.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating payroll record: {e}")
        return jsonify({'error': 'Failed to create payroll record'}), 500

@hcm_bp.route('/payroll/<int:payroll_id>', methods=['PUT'])
def update_payroll(payroll_id):
    """Update a payroll record"""
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        data = request.get_json()
        
        if 'employee_id' in data:
            payroll.employee_id = data['employee_id']
        if 'period' in data:
            payroll.period = data['period']
        if 'gross_pay' in data:
            payroll.gross_pay = data['gross_pay']
        if 'net_pay' in data:
            payroll.net_pay = data['net_pay']
        if 'status' in data:
            payroll.status = data['status']
        
        payroll.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Payroll record {payroll_id} updated successfully',
            'data': {
                'id': payroll.id,
                'employee_id': payroll.employee_id,
                'employee': f"{payroll.employee.first_name} {payroll.employee.last_name}" if payroll.employee else 'Unknown',
                'period': payroll.period,
                'gross_pay': payroll.gross_pay,
                'net_pay': payroll.net_pay,
                'status': payroll.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating payroll record: {e}")
        return jsonify({'error': 'Failed to update payroll record'}), 500

@hcm_bp.route('/payroll/<int:payroll_id>', methods=['DELETE'])
def delete_payroll(payroll_id):
    """Delete a payroll record"""
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        db.session.delete(payroll)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Payroll record {payroll_id} deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting payroll record: {e}")
        return jsonify({'error': 'Failed to delete payroll record'}), 500
