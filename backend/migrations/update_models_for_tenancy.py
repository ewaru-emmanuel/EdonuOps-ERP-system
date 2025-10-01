#!/usr/bin/env python3
"""
Update existing models to include tenant_id field
This script modifies the model files to add tenant support
"""

import os
import sys
import re
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_model_file(file_path):
    """Update a model file to include tenant_id field"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if tenant_id already exists
        if 'tenant_id' in content:
            print(f"ℹ️  {file_path} already has tenant_id")
            return False
        
        # Find the class definition and add tenant_id
        # Look for the first db.Column definition after class definition
        lines = content.split('\n')
        updated_lines = []
        in_class = False
        tenant_id_added = False
        
        for i, line in enumerate(lines):
            updated_lines.append(line)
            
            # Check if we're in a model class
            if line.strip().startswith('class ') and 'db.Model' in line:
                in_class = True
                continue
            
            # If we're in a class and find the first db.Column, add tenant_id before it
            if in_class and not tenant_id_added and 'db.Column' in line and 'primary_key=True' in line:
                # Add tenant_id field before the primary key
                indent = len(line) - len(line.lstrip())
                tenant_id_line = ' ' * indent + 'tenant_id = db.Column(db.String(50), nullable=False)'
                updated_lines.insert(-1, tenant_id_line)
                tenant_id_added = True
                print(f"✅ Added tenant_id to {file_path}")
                break
        
        if tenant_id_added:
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            return True
        else:
            print(f"⚠️  Could not find suitable place to add tenant_id in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def update_models_directory():
    """Update all model files in the modules directory"""
    modules_dir = Path("modules")
    model_files = []
    
    # Find all Python files in modules directory
    for py_file in modules_dir.rglob("*.py"):
        if py_file.name.endswith('_models.py') or 'model' in py_file.name.lower():
            model_files.append(py_file)
    
    print(f"📁 Found {len(model_files)} model files to update:")
    for file_path in model_files:
        print(f"   - {file_path}")
    
    updated_count = 0
    for file_path in model_files:
        if update_model_file(str(file_path)):
            updated_count += 1
    
    print(f"\n✅ Updated {updated_count} model files")
    return updated_count

def create_tenant_aware_base_model():
    """Create a base model class with tenant support"""
    base_model_content = '''"""
Base model class with tenant support
All models should inherit from this class
"""

from app import db
from datetime import datetime

class TenantAwareModel(db.Model):
    """
    Base model class that includes tenant_id field
    All tenant-aware models should inherit from this
    """
    __abstract__ = True
    
    tenant_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))
    
    def to_dict(self):
        """Convert model to dictionary, excluding sensitive fields"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    @classmethod
    def get_by_tenant(cls, tenant_id):
        """Get all records for a specific tenant"""
        return cls.query.filter_by(tenant_id=tenant_id).all()
    
    @classmethod
    def get_by_tenant_and_id(cls, tenant_id, record_id):
        """Get a specific record for a tenant"""
        return cls.query.filter_by(tenant_id=tenant_id, id=record_id).first()
'''
    
    try:
        with open("modules/core/tenant_aware_base.py", 'w', encoding='utf-8') as f:
            f.write(base_model_content)
        print("✅ Created tenant-aware base model")
        return True
    except Exception as e:
        print(f"❌ Error creating base model: {e}")
        return False

def main():
    """Main function to update models for tenancy"""
    print("🚀 Updating Models for Multi-Tenancy...")
    print("=" * 50)
    
    try:
        # Step 1: Create tenant-aware base model
        print("\n📋 Step 1: Creating tenant-aware base model...")
        create_tenant_aware_base_model()
        
        # Step 2: Update existing model files
        print("\n📋 Step 2: Updating existing model files...")
        updated_count = update_models_directory()
        
        print("\n" + "=" * 50)
        print(f"🎉 Model Update Completed!")
        print(f"✅ Updated {updated_count} model files")
        print("\n📝 Next Steps:")
        print("   1. Review updated model files")
        print("   2. Run the database migration")
        print("   3. Update API endpoints to use tenant filtering")
        print("   4. Test tenant isolation")
        
    except Exception as e:
        print(f"\n❌ Model update failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()












