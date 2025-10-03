"""
Cost Center Service
==================

This service handles cost center, department, and project operations
including allocation rules and reporting.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from app import db
from modules.finance.models import JournalEntry, JournalLine, Account
from modules.finance.cost_center_models import (
    CostCenter, Department, Project, CostAllocation, CostAllocationDetail
)

class CostCenterService:
    """Service for cost center, department, and project operations"""
    
    def __init__(self):
        pass
    
    def create_cost_center(self, user_id: int, data: Dict) -> Dict:
        """Create a new cost center"""
        try:
            cost_center = CostCenter(
                code=data['code'],
                name=data['name'],
                description=data.get('description', ''),
                parent_id=data.get('parent_id'),
                cost_center_type=data.get('cost_center_type', 'department'),
                budget_amount=data.get('budget_amount', 0.0),
                responsible_manager=data.get('responsible_manager', ''),
                user_id=user_id
            )
            
            db.session.add(cost_center)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Cost center {cost_center.code} created successfully',
                'cost_center': cost_center.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_department(self, user_id: int, data: Dict) -> Dict:
        """Create a new department"""
        try:
            department = Department(
                code=data['code'],
                name=data['name'],
                description=data.get('description', ''),
                parent_id=data.get('parent_id'),
                department_head=data.get('department_head', ''),
                location=data.get('location', ''),
                user_id=user_id
            )
            
            db.session.add(department)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Department {department.code} created successfully',
                'department': department.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_project(self, user_id: int, data: Dict) -> Dict:
        """Create a new project"""
        try:
            project = Project(
                code=data['code'],
                name=data['name'],
                description=data.get('description', ''),
                project_type=data.get('project_type', 'internal'),
                status=data.get('status', 'active'),
                start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
                end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
                budget_amount=data.get('budget_amount', 0.0),
                project_manager=data.get('project_manager', ''),
                client_name=data.get('client_name', ''),
                user_id=user_id
            )
            
            db.session.add(project)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Project {project.code} created successfully',
                'project': project.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cost_centers(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all cost centers for a user"""
        query = CostCenter.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        
        return [cc.to_dict() for cc in query.order_by(CostCenter.code).all()]
    
    def get_departments(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all departments for a user"""
        query = Department.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        
        return [dept.to_dict() for dept in query.order_by(Department.code).all()]
    
    def get_projects(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all projects for a user"""
        query = Project.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        
        return [proj.to_dict() for proj in query.order_by(Project.code).all()]
    
    def get_cost_center_summary(self, user_id: int, cost_center_id: int = None, 
                               start_date: date = None, end_date: date = None) -> Dict:
        """Get cost center summary with expenses and budget"""
        try:
            if not start_date:
                start_date = date.today().replace(day=1)  # First day of current month
            if not end_date:
                end_date = date.today()  # Today
            
            # Build query for journal lines
            query = JournalLine.query.join(JournalEntry).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.doc_date >= start_date,
                JournalEntry.doc_date <= end_date
            )
            
            if cost_center_id:
                query = query.filter(JournalLine.cost_center_id == cost_center_id)
            
            lines = query.all()
            
            # Calculate totals
            total_debits = sum(line.functional_debit_amount for line in lines)
            total_credits = sum(line.functional_credit_amount for line in lines)
            net_expense = total_debits - total_credits
            
            # Get cost center details
            cost_centers = {}
            if cost_center_id:
                cc = CostCenter.query.filter_by(id=cost_center_id, user_id=user_id).first()
                if cc:
                    cost_centers[cc.id] = {
                        'code': cc.code,
                        'name': cc.name,
                        'budget_amount': cc.budget_amount,
                        'expense_amount': net_expense,
                        'budget_utilization': (net_expense / cc.budget_amount * 100) if cc.budget_amount > 0 else 0
                    }
            else:
                # Get all cost centers with their expenses
                for line in lines:
                    if line.cost_center_id:
                        if line.cost_center_id not in cost_centers:
                            cc = CostCenter.query.get(line.cost_center_id)
                            if cc:
                                cost_centers[cc.id] = {
                                    'code': cc.code,
                                    'name': cc.name,
                                    'budget_amount': cc.budget_amount,
                                    'expense_amount': 0,
                                    'budget_utilization': 0
                                }
                        
                        # Add expense to cost center
                        expense = line.functional_debit_amount - line.functional_credit_amount
                        cost_centers[line.cost_center_id]['expense_amount'] += expense
                
                # Calculate budget utilization
                for cc_data in cost_centers.values():
                    if cc_data['budget_amount'] > 0:
                        cc_data['budget_utilization'] = (cc_data['expense_amount'] / cc_data['budget_amount'] * 100)
            
            return {
                'success': True,
                'summary': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'total_expenses': net_expense,
                    'cost_centers': list(cost_centers.values())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_department_summary(self, user_id: int, department_id: int = None,
                              start_date: date = None, end_date: date = None) -> Dict:
        """Get department summary with expenses"""
        try:
            if not start_date:
                start_date = date.today().replace(day=1)
            if not end_date:
                end_date = date.today()
            
            # Build query for journal lines
            query = JournalLine.query.join(JournalEntry).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.doc_date >= start_date,
                JournalEntry.doc_date <= end_date
            )
            
            if department_id:
                query = query.filter(JournalLine.department_id == department_id)
            
            lines = query.all()
            
            # Calculate totals
            total_debits = sum(line.functional_debit_amount for line in lines)
            total_credits = sum(line.functional_credit_amount for line in lines)
            net_expense = total_debits - total_credits
            
            # Get department details
            departments = {}
            if department_id:
                dept = Department.query.filter_by(id=department_id, user_id=user_id).first()
                if dept:
                    departments[dept.id] = {
                        'code': dept.code,
                        'name': dept.name,
                        'department_head': dept.department_head,
                        'location': dept.location,
                        'expense_amount': net_expense
                    }
            else:
                # Get all departments with their expenses
                for line in lines:
                    if line.department_id:
                        if line.department_id not in departments:
                            dept = Department.query.get(line.department_id)
                            if dept:
                                departments[dept.id] = {
                                    'code': dept.code,
                                    'name': dept.name,
                                    'department_head': dept.department_head,
                                    'location': dept.location,
                                    'expense_amount': 0
                                }
                        
                        # Add expense to department
                        expense = line.functional_debit_amount - line.functional_credit_amount
                        departments[line.department_id]['expense_amount'] += expense
            
            return {
                'success': True,
                'summary': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'total_expenses': net_expense,
                    'departments': list(departments.values())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_project_summary(self, user_id: int, project_id: int = None,
                           start_date: date = None, end_date: date = None) -> Dict:
        """Get project summary with expenses and budget"""
        try:
            if not start_date:
                start_date = date.today().replace(day=1)
            if not end_date:
                end_date = date.today()
            
            # Build query for journal lines
            query = JournalLine.query.join(JournalEntry).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.doc_date >= start_date,
                JournalEntry.doc_date <= end_date
            )
            
            if project_id:
                query = query.filter(JournalLine.project_id == project_id)
            
            lines = query.all()
            
            # Calculate totals
            total_debits = sum(line.functional_debit_amount for line in lines)
            total_credits = sum(line.functional_credit_amount for line in lines)
            net_expense = total_debits - total_credits
            
            # Get project details
            projects = {}
            if project_id:
                proj = Project.query.filter_by(id=project_id, user_id=user_id).first()
                if proj:
                    projects[proj.id] = {
                        'code': proj.code,
                        'name': proj.name,
                        'project_type': proj.project_type,
                        'status': proj.status,
                        'budget_amount': proj.budget_amount,
                        'expense_amount': net_expense,
                        'budget_utilization': (net_expense / proj.budget_amount * 100) if proj.budget_amount > 0 else 0
                    }
            else:
                # Get all projects with their expenses
                for line in lines:
                    if line.project_id:
                        if line.project_id not in projects:
                            proj = Project.query.get(line.project_id)
                            if proj:
                                projects[proj.id] = {
                                    'code': proj.code,
                                    'name': proj.name,
                                    'project_type': proj.project_type,
                                    'status': proj.status,
                                    'budget_amount': proj.budget_amount,
                                    'expense_amount': 0,
                                    'budget_utilization': 0
                                }
                        
                        # Add expense to project
                        expense = line.functional_debit_amount - line.functional_credit_amount
                        projects[line.project_id]['expense_amount'] += expense
                
                # Calculate budget utilization
                for proj_data in projects.values():
                    if proj_data['budget_amount'] > 0:
                        proj_data['budget_utilization'] = (proj_data['expense_amount'] / proj_data['budget_amount'] * 100)
            
            return {
                'success': True,
                'summary': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'total_expenses': net_expense,
                    'projects': list(projects.values())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global service instance
cost_center_service = CostCenterService()

