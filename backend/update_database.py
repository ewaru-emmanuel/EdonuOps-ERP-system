#!/usr/bin/env python3
"""
Database update script for EdonuOps
Adds new tables for E-commerce, AI, and Sustainability modules
"""

import os
import sys
from app import create_app, db

def update_database():
    """Update database with new tables"""
    print("🔄 Updating EdonuOps database...")
    
    try:
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            # Import all models to ensure they're registered
            from modules.core import models as core_models
            from modules.finance import models as finance_models
            from modules.crm import models as crm_models
            from modules.hr import models as hr_models
            from modules.inventory import models as inventory_models
            from modules.ecommerce import models as ecommerce_models
            from modules.ai import models as ai_models
            from modules.sustainability import models as sustainability_models
            
            print("✅ All models imported successfully")
            
            # Create all tables
            db.create_all()
            
            print("✅ Database updated successfully!")
            print("📊 New tables created for E-commerce, AI, and Sustainability modules")
            
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_database()
