"""
Cost Center, Department, and Project Models
==========================================

This module defines models for cost center management, department tracking,
and project allocation in the finance system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app import db

class CostCenter(db.Model):
    """
    Cost Center master data for expense allocation and reporting
    """
    __tablename__ = 'cost_centers'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, index=True)  # e.g., "CC001", "SALES", "IT"
    name = Column(String(100), nullable=False)  # e.g., "Sales Department", "IT Support"
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('cost_centers.id'))  # For hierarchical structure
    cost_center_type = Column(String(50), default='department')  # department, project, location, function
    is_active = Column(Boolean, default=True)
    budget_amount = Column(Float, default=0.0)  # Annual budget
    responsible_manager = Column(String(100))  # Manager name
    tenant_id = Column(String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship('CostCenter', remote_side=[id], backref='children')
    journal_lines = relationship('JournalLine', backref='cost_center')
    
    # Ensure unique cost center codes per tenant
    __table_args__ = (
        UniqueConstraint('code', 'tenant_id', name='_cost_center_code_tenant_uc'),
    )
    
    def __repr__(self):
        return f'<CostCenter {self.code}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'cost_center_type': self.cost_center_type,
            'is_active': self.is_active,
            'budget_amount': self.budget_amount,
            'responsible_manager': self.responsible_manager,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Department(db.Model):
    """
    Department master data for organizational structure
    """
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, index=True)  # e.g., "SALES", "HR", "IT"
    name = Column(String(100), nullable=False)  # e.g., "Sales Department"
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('departments.id'))  # For hierarchical structure
    department_head = Column(String(100))  # Department head name
    location = Column(String(100))  # Physical location
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship('Department', remote_side=[id], backref='children')
    journal_lines = relationship('JournalLine', backref='department')
    
    # Ensure unique department codes per tenant
    __table_args__ = (
        UniqueConstraint('code', 'tenant_id', name='_department_code_tenant_uc'),
    )
    
    def __repr__(self):
        return f'<Department {self.code}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'department_head': self.department_head,
            'location': self.location,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Project(db.Model):
    """
    Project master data for project-based accounting
    """
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, index=True)  # e.g., "PRJ001", "PHOENIX"
    name = Column(String(100), nullable=False)  # e.g., "Project Phoenix"
    description = Column(Text)
    project_type = Column(String(50), default='internal')  # internal, external, r&d, maintenance
    status = Column(String(20), default='active')  # active, completed, on_hold, cancelled
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget_amount = Column(Float, default=0.0)  # Project budget
    project_manager = Column(String(100))  # Project manager name
    client_name = Column(String(100))  # For external projects
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    journal_lines = relationship('JournalLine', backref='project')
    
    # Ensure unique project codes per tenant
    __table_args__ = (
        UniqueConstraint('code', 'tenant_id', name='_project_code_tenant_uc'),
    )
    
    def __repr__(self):
        return f'<Project {self.code}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget_amount': self.budget_amount,
            'project_manager': self.project_manager,
            'client_name': self.client_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CostAllocation(db.Model):
    """
    Cost allocation rules for automatic expense distribution
    """
    __tablename__ = 'cost_allocations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # e.g., "Office Rent Allocation"
    description = Column(Text)
    allocation_method = Column(String(50), default='percentage')  # percentage, fixed_amount, headcount, square_footage
    source_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)  # Source account
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_account = relationship('Account', backref='cost_allocations')
    allocation_details = relationship('CostAllocationDetail', backref='cost_allocation', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CostAllocation {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'allocation_method': self.allocation_method,
            'source_account_id': self.source_account_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'allocation_details': [detail.to_dict() for detail in self.allocation_details]
        }

class CostAllocationDetail(db.Model):
    """
    Detailed allocation rules for cost centers, departments, and projects
    """
    __tablename__ = 'cost_allocation_details'
    
    id = Column(Integer, primary_key=True)
    cost_allocation_id = Column(Integer, ForeignKey('cost_allocations.id'), nullable=False)
    allocation_type = Column(String(20), nullable=False)  # cost_center, department, project
    allocation_id = Column(Integer, nullable=False)  # ID of the cost center, department, or project
    allocation_percentage = Column(Float, default=0.0)  # Percentage allocation
    allocation_amount = Column(Float, default=0.0)  # Fixed amount allocation
    target_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)  # Target account
    tenant_id = Column(String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    target_account = relationship('Account', backref='allocation_details')
    
    def __repr__(self):
        return f'<CostAllocationDetail {self.allocation_type}:{self.allocation_id} - {self.allocation_percentage}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'cost_allocation_id': self.cost_allocation_id,
            'allocation_type': self.allocation_type,
            'allocation_id': self.allocation_id,
            'allocation_percentage': self.allocation_percentage,
            'allocation_amount': self.allocation_amount,
            'target_account_id': self.target_account_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

