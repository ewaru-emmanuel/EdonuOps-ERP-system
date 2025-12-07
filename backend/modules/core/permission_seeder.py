"""
Permission Seeding Service
==========================

SECURITY: This service creates all required permissions in the database.
It ensures that all permissions defined in module_permission_mappings.py exist
before they can be granted to roles.

This service is:
- Idempotent: Can be run multiple times safely
- Auditable: Logs all actions
- Secure: Only creates permissions, never modifies existing ones
"""

from app import db
from modules.core.permissions import Permission
from modules.core.module_permission_mappings import PERMISSION_DEFINITIONS
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def seed_all_permissions():
    """
    Seed all permissions from PERMISSION_DEFINITIONS into the database
    
    SECURITY: 
    - Only creates permissions if they don't exist
    - Never modifies existing permissions
    - Logs all actions for audit trail
    
    Returns:
        dict: {
            'created': int,  # Number of permissions created
            'existing': int,  # Number of permissions that already existed
            'errors': list   # List of errors encountered
        }
    """
    created_count = 0
    existing_count = 0
    errors = []
    
    logger.info("🔐 Starting permission seeding process...")
    print("🔐 Starting permission seeding process...")
    
    try:
        for permission_name, permission_def in PERMISSION_DEFINITIONS.items():
            try:
                # Check if permission already exists
                existing_permission = Permission.query.filter_by(name=permission_name).first()
                
                if existing_permission:
                    existing_count += 1
                    logger.debug(f"   ⏭️  Permission '{permission_name}' already exists - skipping")
                else:
                    # Create new permission
                    new_permission = Permission(
                        name=permission_name,
                        module=permission_def['module'],
                        action=permission_def['action'],
                        resource=permission_def.get('resource'),
                        description=permission_def.get('description', '')
                    )
                    db.session.add(new_permission)
                    created_count += 1
                    logger.info(f"   ✅ Created permission: {permission_name}")
                    print(f"   ✅ Created permission: {permission_name}")
                    
            except Exception as e:
                error_msg = f"Error creating permission '{permission_name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                db.session.rollback()
                continue
        
        # Commit all new permissions
        if created_count > 0:
            db.session.commit()
            logger.info(f"✅ Successfully created {created_count} permissions")
            print(f"✅ Successfully created {created_count} permissions")
        else:
            logger.info("ℹ️  No new permissions to create")
            print("ℹ️  No new permissions to create")
        
        if existing_count > 0:
            logger.info(f"ℹ️  {existing_count} permissions already existed")
            print(f"ℹ️  {existing_count} permissions already existed")
        
        return {
            'created': created_count,
            'existing': existing_count,
            'errors': errors,
            'total': len(PERMISSION_DEFINITIONS)
        }
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Critical error during permission seeding: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"❌ {error_msg}")
        raise

def verify_permissions_exist(permission_names):
    """
    Verify that specified permissions exist in the database
    
    SECURITY: Used to validate before granting permissions
    
    Args:
        permission_names: list of permission names to verify
        
    Returns:
        dict: {
            'all_exist': bool,
            'missing': list,  # Permissions that don't exist
            'existing': list  # Permissions that exist
        }
    """
    missing = []
    existing = []
    
    for perm_name in permission_names:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm:
            existing.append(perm_name)
        else:
            missing.append(perm_name)
    
    return {
        'all_exist': len(missing) == 0,
        'missing': missing,
        'existing': existing
    }

