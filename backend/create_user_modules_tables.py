#!/usr/bin/env python3
"""
Database migration script to create user modules tables
Run this script to set up the backend module activation system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.dashboard.models import UserModules, Dashboard, DashboardWidget, WidgetTemplate, DashboardTemplate

def create_tables():
    """Create all user modules related tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Creating user modules tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ User modules tables created successfully!")
            print("📊 Tables created:")
            print("   - user_modules")
            print("   - dashboards") 
            print("   - dashboard_widgets")
            print("   - widget_templates")
            print("   - dashboard_templates")
            
            # Create some default widget templates
            print("🔧 Creating default widget templates...")
            
            default_templates = [
                {
                    'module_id': 'finance',
                    'widget_type': 'metric',
                    'name': 'Total Revenue',
                    'description': 'Shows total revenue for the period',
                    'config': {
                        'metric_type': 'revenue',
                        'period': 'current_month',
                        'format': 'currency'
                    }
                },
                {
                    'module_id': 'finance',
                    'widget_type': 'chart',
                    'name': 'Revenue Trend',
                    'description': 'Shows revenue trend over time',
                    'config': {
                        'chart_type': 'line',
                        'metric': 'revenue',
                        'period': 'last_12_months'
                    }
                },
                {
                    'module_id': 'crm',
                    'widget_type': 'metric',
                    'name': 'Total Contacts',
                    'description': 'Shows total number of contacts',
                    'config': {
                        'metric_type': 'count',
                        'entity': 'contacts',
                        'format': 'number'
                    }
                },
                {
                    'module_id': 'inventory',
                    'widget_type': 'metric',
                    'name': 'Total Products',
                    'description': 'Shows total number of products',
                    'config': {
                        'metric_type': 'count',
                        'entity': 'products',
                        'format': 'number'
                    }
                }
            ]
            
            for template_data in default_templates:
                # Check if template already exists
                existing = WidgetTemplate.query.filter_by(
                    module_id=template_data['module_id'],
                    name=template_data['name']
                ).first()
                
                if not existing:
                    template = WidgetTemplate(
                        module_id=template_data['module_id'],
                        widget_type=template_data['widget_type'],
                        name=template_data['name'],
                        description=template_data['description'],
                        config=template_data['config'],
                        created_by=1  # System user
                    )
                    db.session.add(template)
            
            db.session.commit()
            print("✅ Default widget templates created!")
            
            # Create some default dashboard templates
            print("🔧 Creating default dashboard templates...")
            
            default_dashboard_templates = [
                {
                    'name': 'Executive Dashboard',
                    'description': 'High-level overview for executives',
                    'user_type': 'executive',
                    'layout': {
                        'grid': '4x3',
                        'widgets': [
                            {'id': 'revenue-metric', 'position': {'x': 0, 'y': 0, 'w': 2, 'h': 1}},
                            {'id': 'revenue-chart', 'position': {'x': 2, 'y': 0, 'w': 2, 'h': 2}},
                            {'id': 'contacts-metric', 'position': {'x': 0, 'y': 1, 'w': 1, 'h': 1}},
                            {'id': 'products-metric', 'position': {'x': 1, 'y': 1, 'w': 1, 'h': 1}}
                        ]
                    },
                    'widgets': [
                        {'type': 'metric', 'title': 'Total Revenue', 'config': {'metric': 'revenue'}},
                        {'type': 'chart', 'title': 'Revenue Trend', 'config': {'chart_type': 'line'}},
                        {'type': 'metric', 'title': 'Total Contacts', 'config': {'metric': 'contacts'}},
                        {'type': 'metric', 'title': 'Total Products', 'config': {'metric': 'products'}}
                    ]
                },
                {
                    'name': 'Manager Dashboard',
                    'description': 'Operational dashboard for managers',
                    'user_type': 'manager',
                    'layout': {
                        'grid': '3x4',
                        'widgets': [
                            {'id': 'revenue-metric', 'position': {'x': 0, 'y': 0, 'w': 1, 'h': 1}},
                            {'id': 'contacts-metric', 'position': {'x': 1, 'y': 0, 'w': 1, 'h': 1}},
                            {'id': 'products-metric', 'position': {'x': 2, 'y': 0, 'w': 1, 'h': 1}},
                            {'id': 'revenue-chart', 'position': {'x': 0, 'y': 1, 'w': 3, 'h': 2}}
                        ]
                    },
                    'widgets': [
                        {'type': 'metric', 'title': 'Revenue', 'config': {'metric': 'revenue'}},
                        {'type': 'metric', 'title': 'Contacts', 'config': {'metric': 'contacts'}},
                        {'type': 'metric', 'title': 'Products', 'config': {'metric': 'products'}},
                        {'type': 'chart', 'title': 'Revenue Trend', 'config': {'chart_type': 'line'}}
                    ]
                }
            ]
            
            for template_data in default_dashboard_templates:
                # Check if template already exists
                existing = DashboardTemplate.query.filter_by(
                    name=template_data['name']
                ).first()
                
                if not existing:
                    template = DashboardTemplate(
                        name=template_data['name'],
                        description=template_data['description'],
                        user_type=template_data['user_type'],
                        layout=template_data['layout'],
                        widgets=template_data['widgets'],
                        created_by=1  # System user
                    )
                    db.session.add(template)
            
            db.session.commit()
            print("✅ Default dashboard templates created!")
            
            print("\n🎉 User modules system setup complete!")
            print("📋 Next steps:")
            print("   1. Restart the backend server")
            print("   2. Test module activation via API")
            print("   3. Verify frontend integration")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Setting up backend module activation system...")
    success = create_tables()
    if success:
        print("✅ Setup completed successfully!")
    else:
        print("❌ Setup failed!")
        sys.exit(1)




