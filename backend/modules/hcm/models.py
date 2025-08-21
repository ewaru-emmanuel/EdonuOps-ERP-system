from app import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    position = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    hire_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    manager = db.relationship('Employee', remote_side=[id], backref='subordinates', foreign_keys=[manager_id])
    department = db.relationship('Department', backref='employees', foreign_keys=[department_id])

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Payroll(db.Model):
    __tablename__ = 'payroll'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM format
    gross_pay = db.Column(db.Float, nullable=False)
    net_pay = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, processed, paid
    payment_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = db.relationship('Employee', backref='payroll_records')

class Recruitment(db.Model):
    __tablename__ = 'recruitment'
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    salary_range_min = db.Column(db.Float)
    salary_range_max = db.Column(db.Float)
    status = db.Column(db.String(20), default='open')  # open, closed, on_hold
    applications = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    budget = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    manager = db.relationship('Employee', backref='managed_department', foreign_keys=[manager_id])
