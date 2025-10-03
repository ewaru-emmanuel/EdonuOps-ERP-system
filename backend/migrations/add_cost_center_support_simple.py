#!/usr/bin/env python3
"""
Simple Migration: Add Cost Center Support
========================================

This migration adds cost center fields to journal_lines table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime

def add_cost_center_support_simple():
    """Add cost center support - simple version"""
    with app.app_context():
        print("🔄 Adding Cost Center Support (Simple)...")
        
        try:
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
            
            # Create tables using raw SQL to avoid model conflicts
            print("   📋 Creating cost center tables...")
            
            # Create cost_centers table
            connection.execute(db.text("""
                CREATE TABLE IF NOT EXISTS cost_centers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(20) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    parent_id INTEGER,
                    cost_center_type VARCHAR(50) DEFAULT 'department',
                    is_active BOOLEAN DEFAULT 1,
                    budget_amount FLOAT DEFAULT 0.0,
                    responsible_manager VARCHAR(100),
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code, user_id)
                )
            """))
            print("      ✅ Created cost_centers table")
            
            # Create departments table
            connection.execute(db.text("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(20) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    parent_id INTEGER,
                    department_head VARCHAR(100),
                    location VARCHAR(100),
                    is_active BOOLEAN DEFAULT 1,
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code, user_id)
                )
            """))
            print("      ✅ Created departments table")
            
            # Create projects table
            connection.execute(db.text("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(20) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    project_type VARCHAR(50) DEFAULT 'internal',
                    status VARCHAR(20) DEFAULT 'active',
                    start_date DATETIME,
                    end_date DATETIME,
                    budget_amount FLOAT DEFAULT 0.0,
                    project_manager VARCHAR(100),
                    client_name VARCHAR(100),
                    is_active BOOLEAN DEFAULT 1,
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code, user_id)
                )
            """))
            print("      ✅ Created projects table")
            
            # Create sample data for existing users
            print("   👥 Creating sample cost centers, departments, and projects...")
            
            from modules.finance.models import JournalEntry
            
            # Get users who have journal entries
            users_with_entries = db.session.query(JournalEntry.user_id).distinct().all()
            
            for user_id_tuple in users_with_entries:
                user_id = user_id_tuple[0]
                if user_id:  # Ensure user_id is not None
                    print(f"   🔧 Creating sample data for user {user_id}...")
                    
                    # Create sample cost centers
                    sample_cost_centers = [
                        ('SALES', 'Sales Department', 'department', 100000.0),
                        ('IT', 'IT Department', 'department', 75000.0),
                        ('HR', 'Human Resources', 'department', 50000.0),
                        ('ADMIN', 'Administration', 'department', 25000.0)
                    ]
                    
                    for code, name, cc_type, budget in sample_cost_centers:
                        # Check if cost center already exists
                        existing = connection.execute(
                            db.text("SELECT id FROM cost_centers WHERE code = :code AND user_id = :user_id"),
                            {'code': code, 'user_id': user_id}
                        ).fetchone()
                        
                        if not existing:
                            connection.execute(db.text("""
                                INSERT INTO cost_centers (code, name, cost_center_type, budget_amount, user_id)
                                VALUES (:code, :name, :type, :budget, :user_id)
                            """), {
                                'code': code, 'name': name, 'type': cc_type, 'budget': budget, 'user_id': user_id
                            })
                    
                    # Create sample departments
                    sample_departments = [
                        ('SALES', 'Sales Department', 'Sales Manager', 'Main Office'),
                        ('IT', 'IT Department', 'IT Manager', 'Tech Center'),
                        ('HR', 'Human Resources', 'HR Manager', 'Main Office'),
                        ('ADMIN', 'Administration', 'Admin Manager', 'Main Office')
                    ]
                    
                    for code, name, head, location in sample_departments:
                        # Check if department already exists
                        existing = connection.execute(
                            db.text("SELECT id FROM departments WHERE code = :code AND user_id = :user_id"),
                            {'code': code, 'user_id': user_id}
                        ).fetchone()
                        
                        if not existing:
                            connection.execute(db.text("""
                                INSERT INTO departments (code, name, department_head, location, user_id)
                                VALUES (:code, :name, :head, :location, :user_id)
                            """), {
                                'code': code, 'name': name, 'head': head, 'location': location, 'user_id': user_id
                            })
                    
                    # Create sample projects
                    sample_projects = [
                        ('PHOENIX', 'Project Phoenix', 'internal', 50000.0, 'Project Manager'),
                        ('ALPHA', 'Alpha Development', 'r&d', 75000.0, 'Tech Lead'),
                        ('BETA', 'Beta Testing', 'internal', 25000.0, 'QA Manager')
                    ]
                    
                    for code, name, proj_type, budget, manager in sample_projects:
                        # Check if project already exists
                        existing = connection.execute(
                            db.text("SELECT id FROM projects WHERE code = :code AND user_id = :user_id"),
                            {'code': code, 'user_id': user_id}
                        ).fetchone()
                        
                        if not existing:
                            connection.execute(db.text("""
                                INSERT INTO projects (code, name, project_type, budget_amount, project_manager, user_id)
                                VALUES (:code, :name, :type, :budget, :manager, :user_id)
                            """), {
                                'code': code, 'name': name, 'type': proj_type, 'budget': budget, 'manager': manager, 'user_id': user_id
                            })
            
            print("      ✅ Sample cost centers, departments, and projects created")
            
            # Create indexes for performance
            print("   🚀 Creating indexes for performance...")
            try:
                connection.execute(db.text('CREATE INDEX IF NOT EXISTS idx_journal_lines_cost_center_id ON journal_lines(cost_center_id)'))
                connection.execute(db.text('CREATE INDEX IF NOT EXISTS idx_journal_lines_department_id ON journal_lines(department_id)'))
                connection.execute(db.text('CREATE INDEX IF NOT EXISTS idx_journal_lines_project_id ON journal_lines(project_id)'))
                print("      ✅ Created performance indexes")
            except Exception as e:
                print(f"      ⚠️  Index creation warning: {e}")
            
            print("✅ Cost Center Support migration completed successfully!")
            
            # Print summary
            cost_centers_count = connection.execute(db.text("SELECT COUNT(*) FROM cost_centers")).scalar()
            departments_count = connection.execute(db.text("SELECT COUNT(*) FROM departments")).scalar()
            projects_count = connection.execute(db.text("SELECT COUNT(*) FROM projects")).scalar()
            
            print(f"📊 Summary:")
            print(f"   Cost Centers: {cost_centers_count}")
            print(f"   Departments: {departments_count}")
            print(f"   Projects: {projects_count}")
            print(f"   Cost Center Fields: Added to journal_lines")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_cost_center_support_simple()

