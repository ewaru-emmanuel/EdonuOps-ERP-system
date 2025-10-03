#!/usr/bin/env python3
"""
Migration: Add Cost Center Tables Only
=====================================

This migration creates the cost center tables using raw SQL.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime

def add_cost_center_tables():
    """Add cost center tables only"""
    with app.app_context():
        print("🔄 Creating Cost Center Tables...")
        
        try:
            # Create tables using raw SQL
            print("   📋 Creating cost center tables...")
            
            # Create cost_centers table
            db.engine.execute("""
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
            """)
            print("      ✅ Created cost_centers table")
            
            # Create departments table
            db.engine.execute("""
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
            """)
            print("      ✅ Created departments table")
            
            # Create projects table
            db.engine.execute("""
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
            """)
            print("      ✅ Created projects table")
            
            # Create sample data for user 3
            print("   👥 Creating sample data for user 3...")
            
            # Create sample cost centers
            sample_cost_centers = [
                ('SALES', 'Sales Department', 'department', 100000.0),
                ('IT', 'IT Department', 'department', 75000.0),
                ('HR', 'Human Resources', 'department', 50000.0),
                ('ADMIN', 'Administration', 'department', 25000.0)
            ]
            
            for code, name, cc_type, budget in sample_cost_centers:
                db.engine.execute("""
                    INSERT OR IGNORE INTO cost_centers (code, name, cost_center_type, budget_amount, user_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (code, name, cc_type, budget, 3))
            
            # Create sample departments
            sample_departments = [
                ('SALES', 'Sales Department', 'Sales Manager', 'Main Office'),
                ('IT', 'IT Department', 'IT Manager', 'Tech Center'),
                ('HR', 'Human Resources', 'HR Manager', 'Main Office'),
                ('ADMIN', 'Administration', 'Admin Manager', 'Main Office')
            ]
            
            for code, name, head, location in sample_departments:
                db.engine.execute("""
                    INSERT OR IGNORE INTO departments (code, name, department_head, location, user_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (code, name, head, location, 3))
            
            # Create sample projects
            sample_projects = [
                ('PHOENIX', 'Project Phoenix', 'internal', 50000.0, 'Project Manager'),
                ('ALPHA', 'Alpha Development', 'r&d', 75000.0, 'Tech Lead'),
                ('BETA', 'Beta Testing', 'internal', 25000.0, 'QA Manager')
            ]
            
            for code, name, proj_type, budget, manager in sample_projects:
                db.engine.execute("""
                    INSERT OR IGNORE INTO projects (code, name, project_type, budget_amount, project_manager, user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, name, proj_type, budget, manager, 3))
            
            print("      ✅ Sample data created")
            
            # Create indexes for performance
            print("   🚀 Creating indexes for performance...")
            try:
                db.engine.execute('CREATE INDEX IF NOT EXISTS idx_journal_lines_cost_center_id ON journal_lines(cost_center_id)')
                db.engine.execute('CREATE INDEX IF NOT EXISTS idx_journal_lines_department_id ON journal_lines(department_id)')
                db.engine.execute('CREATE INDEX IF NOT EXISTS idx_journal_lines_project_id ON journal_lines(project_id)')
                print("      ✅ Created performance indexes")
            except Exception as e:
                print(f"      ⚠️  Index creation warning: {e}")
            
            print("✅ Cost Center Tables migration completed successfully!")
            
            # Print summary
            cost_centers_count = db.engine.execute("SELECT COUNT(*) FROM cost_centers").scalar()
            departments_count = db.engine.execute("SELECT COUNT(*) FROM departments").scalar()
            projects_count = db.engine.execute("SELECT COUNT(*) FROM projects").scalar()
            
            print(f"📊 Summary:")
            print(f"   Cost Centers: {cost_centers_count}")
            print(f"   Departments: {departments_count}")
            print(f"   Projects: {projects_count}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    add_cost_center_tables()

