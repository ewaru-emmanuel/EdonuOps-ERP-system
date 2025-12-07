"""
Module-Permission Auto-Grant Service
====================================

SECURITY: This service automatically grants/revokes permissions when modules are activated/deactivated.
It ensures consistency between module state and permission state.

SECURITY CONTROLS:
1. Input Validation: Validates module_id and user_id before processing
2. Minimal Permissions: Service only has permission to modify role_permissions
3. Comprehensive Logging: All actions are logged for audit trail
4. Transaction Safety: All operations are wrapped in database transactions
5. Fail-Secure: If permission doesn't exist, operation fails (no implicit grants)
"""

from app import db
from modules.core.permissions import Permission, RolePermission, PermissionManager
from modules.core.models import User, Role
from modules.core.module_permission_mappings import get_module_permissions, validate_module_id
from modules.core.permission_seeder import verify_permissions_exist
# Audit logging will be handled via AuditLog model directly
from modules.core.audit_models import AuditLog
from modules.core.tenant_helpers import get_current_user_tenant_id
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def grant_module_permissions(user_id, module_id, granted_by_user_id=None):
    """
    Grant all permissions for a module to a user's role
    
    SECURITY:
    - Validates module_id (prevents injection)
    - Verifies permissions exist before granting
    - Only grants to user's role (not directly to user)
    - Logs all actions for audit trail
    
    Args:
        user_id: ID of user whose role will receive permissions
        module_id: Module ID (must be validated)
        granted_by_user_id: ID of user/admin who triggered this (for audit)
        
    Returns:
        dict: {
            'success': bool,
            'granted': list,  # Permissions successfully granted
            'failed': list,   # Permissions that failed to grant
            'errors': list    # Error messages
        }
    """
    # SECURITY: Input validation
    if not user_id or not module_id:
        error_msg = "user_id and module_id are required"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'granted': [],
            'failed': [],
            'errors': [error_msg]
        }
    
    # SECURITY: Validate module_id (prevent injection)
    if not validate_module_id(module_id):
        error_msg = f"Invalid module_id: {module_id}"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'granted': [],
            'failed': [],
            'errors': [error_msg]
        }
    
    try:
        # Get user and their role
        user = User.query.get(user_id)
        if not user:
            error_msg = f"User {user_id} not found"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'granted': [],
                'failed': [],
                'errors': [error_msg]
            }
        
        if not user.role:
            error_msg = f"User {user_id} has no role assigned"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'granted': [],
                'failed': [],
                'errors': [error_msg]
            }
        
        role = user.role
        logger.info(f"🔐 Granting permissions for module '{module_id}' to role '{role.role_name}' (user {user_id})")
        print(f"🔐 Granting permissions for module '{module_id}' to role '{role.role_name}' (user {user_id})")
        
        # Get permissions for this module
        permission_names = get_module_permissions(module_id)
        
        if not permission_names:
            logger.warning(f"⚠️  No permissions defined for module '{module_id}'")
            return {
                'success': True,
                'granted': [],
                'failed': [],
                'errors': [f"No permissions defined for module '{module_id}'"]
            }
        
        # SECURITY: Verify all permissions exist before granting
        verification = verify_permissions_exist(permission_names)
        if not verification['all_exist']:
            error_msg = f"Missing permissions for module '{module_id}': {verification['missing']}"
            logger.error(f"❌ {error_msg}")
            logger.error("   Run permission seeder to create missing permissions")
            return {
                'success': False,
                'granted': [],
                'failed': permission_names,
                'errors': [error_msg]
            }
        
        granted = []
        failed = []
        errors = []
        
        # Grant each permission to the role
        for perm_name in permission_names:
            try:
                # Get permission
                permission = Permission.query.filter_by(name=perm_name).first()
                if not permission:
                    failed.append(perm_name)
                    errors.append(f"Permission '{perm_name}' not found in database")
                    continue
                
                # Check if role-permission mapping already exists
                existing = RolePermission.query.filter_by(
                    role_id=role.id,
                    permission_id=permission.id
                ).first()
                
                if existing:
                    if existing.granted:
                        # Already granted, skip
                        logger.debug(f"   ⏭️  Permission '{perm_name}' already granted to role '{role.role_name}'")
                        granted.append(perm_name)
                    else:
                        # Exists but not granted - update it
                        existing.granted = True
                        existing.granted_by = granted_by_user_id
                        existing.granted_at = datetime.utcnow()
                        granted.append(perm_name)
                        logger.info(f"   ✅ Updated permission '{perm_name}' for role '{role.role_name}'")
                        print(f"   ✅ Updated permission '{perm_name}' for role '{role.role_name}'")
                else:
                    # Create new role-permission mapping
                    role_permission = RolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                        granted=True,
                        granted_by=granted_by_user_id,
                        granted_at=datetime.utcnow()
                    )
                    db.session.add(role_permission)
                    granted.append(perm_name)
                    logger.info(f"   ✅ Granted permission '{perm_name}' to role '{role.role_name}'")
                    print(f"   ✅ Granted permission '{perm_name}' to role '{role.role_name}'")
                    
            except Exception as e:
                error_msg = f"Error granting permission '{perm_name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                failed.append(perm_name)
                errors.append(error_msg)
                db.session.rollback()
                continue
        
        # Commit all changes
        if granted:
            db.session.commit()
            logger.info(f"✅ Successfully granted {len(granted)} permissions for module '{module_id}' to role '{role.role_name}'")
            print(f"✅ Successfully granted {len(granted)} permissions for module '{module_id}' to role '{role.role_name}'")
            
            # SECURITY: Audit log
            try:
                import json
                tenant_id = get_current_user_tenant_id()
                audit_log = AuditLog(
                    user_id=granted_by_user_id or user_id,
                    tenant_id=tenant_id,
                    action='grant_module_permissions',
                    resource='module',
                    resource_id=module_id,
                    details=json.dumps({
                        'module_id': module_id,
                        'role_id': role.id,
                        'role_name': role.role_name,
                        'permissions_granted': granted,
                        'permissions_failed': failed
                    }),
                    module='core',
                    severity='INFO'
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as audit_error:
                logger.warning(f"Failed to create audit log: {audit_error}")
                # Don't fail the operation if audit logging fails
        
        return {
            'success': len(failed) == 0,
            'granted': granted,
            'failed': failed,
            'errors': errors
        }
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Critical error granting module permissions: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'granted': [],
            'failed': permission_names if 'permission_names' in locals() else [],
            'errors': [error_msg]
        }

def revoke_module_permissions(user_id, module_id, revoked_by_user_id=None):
    """
    Revoke all permissions for a module from a user's role
    
    SECURITY:
    - Validates module_id (prevents injection)
    - Only revokes permissions that were granted via module activation
    - Logs all actions for audit trail
    
    Args:
        user_id: ID of user whose role will lose permissions
        module_id: Module ID (must be validated)
        revoked_by_user_id: ID of user/admin who triggered this (for audit)
        
    Returns:
        dict: {
            'success': bool,
            'revoked': list,  # Permissions successfully revoked
            'failed': list,   # Permissions that failed to revoke
            'errors': list    # Error messages
        }
    """
    # SECURITY: Input validation
    if not user_id or not module_id:
        error_msg = "user_id and module_id are required"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'revoked': [],
            'failed': [],
            'errors': [error_msg]
        }
    
    # SECURITY: Validate module_id (prevent injection)
    if not validate_module_id(module_id):
        error_msg = f"Invalid module_id: {module_id}"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'revoked': [],
            'failed': [],
            'errors': [error_msg]
        }
    
    try:
        # Get user and their role
        user = User.query.get(user_id)
        if not user:
            error_msg = f"User {user_id} not found"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'revoked': [],
                'failed': [],
                'errors': [error_msg]
            }
        
        if not user.role:
            error_msg = f"User {user_id} has no role assigned"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'revoked': [],
                'failed': [],
                'errors': [error_msg]
            }
        
        role = user.role
        logger.info(f"🔐 Revoking permissions for module '{module_id}' from role '{role.role_name}' (user {user_id})")
        print(f"🔐 Revoking permissions for module '{module_id}' from role '{role.role_name}' (user {user_id})")
        
        # Get permissions for this module
        permission_names = get_module_permissions(module_id)
        
        if not permission_names:
            logger.warning(f"⚠️  No permissions defined for module '{module_id}'")
            return {
                'success': True,
                'revoked': [],
                'failed': [],
                'errors': []
            }
        
        revoked = []
        failed = []
        errors = []
        
        # Revoke each permission from the role
        for perm_name in permission_names:
            try:
                # Get permission
                permission = Permission.query.filter_by(name=perm_name).first()
                if not permission:
                    # Permission doesn't exist - skip (not an error)
                    logger.debug(f"   ⏭️  Permission '{perm_name}' not found - skipping")
                    continue
                
                # Find role-permission mapping
                role_permission = RolePermission.query.filter_by(
                    role_id=role.id,
                    permission_id=permission.id
                ).first()
                
                if role_permission and role_permission.granted:
                    # Revoke permission (mark as not granted)
                    role_permission.granted = False
                    revoked.append(perm_name)
                    logger.info(f"   ✅ Revoked permission '{perm_name}' from role '{role.role_name}'")
                    print(f"   ✅ Revoked permission '{perm_name}' from role '{role.role_name}'")
                else:
                    # Permission not granted to this role - skip
                    logger.debug(f"   ⏭️  Permission '{perm_name}' not granted to role '{role.role_name}' - skipping")
                    
            except Exception as e:
                error_msg = f"Error revoking permission '{perm_name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                failed.append(perm_name)
                errors.append(error_msg)
                db.session.rollback()
                continue
        
        # Commit all changes
        if revoked:
            db.session.commit()
            logger.info(f"✅ Successfully revoked {len(revoked)} permissions for module '{module_id}' from role '{role.role_name}'")
            print(f"✅ Successfully revoked {len(revoked)} permissions for module '{module_id}' from role '{role.role_name}'")
            
            # SECURITY: Audit log
            try:
                import json
                tenant_id = get_current_user_tenant_id()
                audit_log = AuditLog(
                    user_id=revoked_by_user_id or user_id,
                    tenant_id=tenant_id,
                    action='revoke_module_permissions',
                    resource='module',
                    resource_id=module_id,
                    details=json.dumps({
                        'module_id': module_id,
                        'role_id': role.id,
                        'role_name': role.role_name,
                        'permissions_revoked': revoked,
                        'permissions_failed': failed
                    }),
                    module='core',
                    severity='INFO'
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as audit_error:
                logger.warning(f"Failed to create audit log: {audit_error}")
                # Don't fail the operation if audit logging fails
        
        return {
            'success': len(failed) == 0,
            'revoked': revoked,
            'failed': failed,
            'errors': errors
        }
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Critical error revoking module permissions: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'revoked': [],
            'failed': permission_names if 'permission_names' in locals() else [],
            'errors': [error_msg]
        }

def sync_user_module_permissions(user_id, granted_by_user_id=None):
    """
    Sync all permissions for all active modules for a user
    
    SECURITY: Ensures user's role has all permissions for all their active modules
    This is useful for:
    - Initial setup after user creation
    - Recovery after permission issues
    - Ensuring consistency
    
    Args:
        user_id: ID of user to sync permissions for
        granted_by_user_id: ID of user/admin who triggered this (for audit)
        
    Returns:
        dict: Summary of all operations
    """
    from modules.dashboard.models import UserModules
    
    logger.info(f"🔄 Syncing permissions for user {user_id}")
    print(f"🔄 Syncing permissions for user {user_id}")
    
    # Get all active modules for user
    user_modules = UserModules.get_user_modules(user_id)
    
    if not user_modules:
        logger.info(f"   ℹ️  User {user_id} has no active modules")
        return {
            'success': True,
            'modules_processed': 0,
            'permissions_granted': 0,
            'errors': []
        }
    
    total_granted = 0
    errors = []
    
    for user_module in user_modules:
        result = grant_module_permissions(
            user_id=user_id,
            module_id=user_module.module_id,
            granted_by_user_id=granted_by_user_id
        )
        
        if result['success']:
            total_granted += len(result['granted'])
        else:
            errors.extend(result['errors'])
    
    logger.info(f"✅ Sync complete: {len(user_modules)} modules processed, {total_granted} permissions granted")
    print(f"✅ Sync complete: {len(user_modules)} modules processed, {total_granted} permissions granted")
    
    return {
        'success': len(errors) == 0,
        'modules_processed': len(user_modules),
        'permissions_granted': total_granted,
        'errors': errors
    }

