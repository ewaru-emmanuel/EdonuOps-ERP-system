#!/usr/bin/env python3
"""
Migration: Add Cost Center, Department, and Project Support
==========================================================

This migration adds cost center, department, and project tables and updates
journal_lines to include cost center tracking fields.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime

def add_cost_center_support():
    """Add cost center, department, and project support"""
    with app.app_context():
        print("🔄 Adding Cost Center, Department, and Project Support...")
        
        try:
            # Create tables using SQLAlchemy
            print("   📋 Creating cost center tables...")
            db.create_all()  # This will create tables if they don't exist
            print("   ✅ Tables created/checked.")
            
            # Add cost center fields to journal_lines if they don't exist
            print("   🔧 Adding cost center fields to journal_lines...")
            with db.engine.connect() as connection:
                inspector = db.inspect(db.engine)
                columns = [col['name'] for col in inspector.get_columns('journal_lines')]
                
                if 'cost_center_id' not in columns:
                    connection.execute(db.text('ALTER TABLE journal_lines ADD COLUMN cost_center_id INTEGER'))
                    print("      ✅ Added cost_center_id column")
                else:
                    print("      ✅ cost_center_id column already exists")
                
                if 'department_id' not in columns:
                    connection.execute(db.text('ALTER TABLE journal_lines ADD COLUMN department_id INTEGER'))
                    print("      ✅ Added department_id column")
                else:
                    print("      ✅ department_id column already exists")
                
                if 'project_id' not in columns:
                    connection.execute(db.text('ALTER TABLE journal_lines ADD COLUMN project_id INTEGER'))
                    print("      ✅ Added project_id column")
                else:
                    print("      ✅ project_id column already exists")
            
            # Create sample cost centers, departments, and projects for existing users
            print("   👥 Creating sample cost centers, departments, and projects...")
            
            from modules.finance.cost_center_models import CostCenter, Department, Project
            from modules.finance.models import JournalEntry
            
            # Get users who have journal entries
            users_with_entries = db.session.query(JournalEntry.user_id).distinct().all()
            
            for user_id_tuple in users_with_entries:
                user_id = user_id_tuple[0]
                if user_id:  # Ensure user_id is not None
                    print(f"   🔧 Creating sample data for user {user_id}...")
                    
                    # Create sample cost centers
                    sample_cost_centers = [
                        {'code': 'SALES', 'name': 'Sales Department', 'cost_center_type': 'department', 'budget_amount': 100000.0},
                        {'code': 'IT', 'name': 'IT Department', 'cost_center_type': 'department', 'budget_amount': 75000.0},
                        {'code': 'HR', 'name': 'Human Resources', 'cost_center_type': 'department', 'budget_amount': 50000.0},
                        {'code': 'ADMIN', 'name': 'Administration', 'cost_center_type': 'department', 'budget_amount': 25000.0}
                    ]
                    
                    for cc_data in sample_cost_centers:
                        existing_cc = CostCenter.query.filter_by(code=cc_data['code'], user_id=user_id).first()
                        if not existing_cc:
                            cost_center = CostCenter(
                                code=cc_data['code'],
                                name=cc_data['name'],
                                cost_center_type=cc_data['cost_center_type'],
                                budget_amount=cc_data['budget_amount'],
                                user_id=user_id
                            )
                            db.session.add(cost_center)
                    
                    # Create sample departments
                    sample_departments = [
                        {'code': 'SALES', 'name': 'Sales Department', 'department_head': 'Sales Manager', 'location': 'Main Office'},
                        {'code': 'IT', 'name': 'IT Department', 'department_head': 'IT Manager', 'location': 'Tech Center'},
                        {'code': 'HR', 'name': 'Human Resources', 'department_head': 'HR Manager', 'location': 'Main Office'},
                        {'code': 'ADMIN', 'name': 'Administration', 'department_head': 'Admin Manager', 'location': 'Main Office'}
                    ]
                    
                    for dept_data in sample_departments:
                        existing_dept = Department.query.filter_by(code=dept_data['code'], user_id=user_id).first()
                        if not existing_dept:
                            department = Department(
                                code=dept_data['code'],
                                name=dept_data['name'],
                                department_head=dept_data['department_head'],
                                location=dept_data['location'],
                                user_id=user_id
                            )
                            db.session.add(department)
                    
                    # Create sample projects
                    sample_projects = [
                        {'code': 'PHOENIX', 'name': 'Project Phoenix', 'project_type': 'internal', 'budget_amount': 50000.0, 'project_manager': 'Project Manager'},
                        {'code': 'ALPHA', 'name': 'Alpha Development', 'project_type': 'r&d', 'budget_amount': 75000.0, 'project_manager': 'Tech Lead'},
                        {'code': 'BETA', 'name': 'Beta Testing', 'project_type': 'internal', 'budget_amount': 25000.0, 'project_manager': 'QA Manager'}
                    ]
                    
                    for proj_data in sample_projects:
                        existing_proj = Project.query.filter_by(code=proj_data['code'], user_id=user_id).first()
                        if not existing_proj:
                            project = Project(
                                code=proj_data['code'],
                                name=proj_data['name'],
                                project_type=proj_data['project_type'],
                                budget_amount=proj_data['budget_amount'],
                                project_manager=proj_data['project_manager'],
                                user_id=user_id
                            )
                            db.session.add(project)
            
            db.session.commit()
            print("      ✅ Sample cost centers, departments, and projects created")
            
            # Create indexes for performance
            print("   🚀 Creating indexes for performance...")
            with db.engine.connect() as connection:
                try:
                    connection.execute(db.text('CREATE INDEX IF NOT EXISTS idx_journal_lines_cost_center_id ON journal_lines(cost_center_id)'))
                    connection.execute(db.text('CREATE INDEX IF NOT EXISTS idx_journal_lines_department_id ON journal_lines(department_id)'))
                    connection.execute(db.text('CREATE INDEX IF NOT EXISTS idx_journal_lines_project_id ON journal_lines(project_id)'))
                    print("      ✅ Created performance indexes")
                except Exception as e:
                    print(f"      ⚠️  Index creation warning: {e}")
            
            print("✅ Cost Center Support migration completed successfully!")
            
            # Print summary
            from modules.finance.cost_center_models import CostCenter, Department, Project
            print(f"📊 Summary:")
            print(f"   Cost Centers: {CostCenter.query.count()}")
            print(f"   Departments: {Department.query.count()}")
            print(f"   Projects: {Project.query.count()}")
            print(f"   Cost Center Fields: Added to journal_lines")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_cost_center_support()

