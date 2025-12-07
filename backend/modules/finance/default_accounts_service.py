"""
Default Accounts Service
Creates the universal 25 default accounts (12 core + 13 standard) for all businesses

IMPORTANT: Tenant-Centric Architecture
- All accounts are created with tenant_id to ensure company-wide sharing
- Each company (tenant) gets their own set of 25 default accounts
- Account queries must always filter by tenant_id
- All users in the same company see the same accounts
- created_by tracks who created the account (audit trail)
"""

from app import db
from .models import Account
from modules.core.tenant_query_helper import tenant_query
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Universal 25 Default Accounts (12 Core + 13 Standard)
# Core accounts (marked with is_core=True) are the essential 12
# Standard accounts provide common business needs without overwhelming users

DEFAULT_ACCOUNTS = [
    # ========== ASSETS (6 accounts) ==========
    # Core Assets (4)
    {"code": "1000", "name": "Cash on Hand", "type": "asset", "parent_code": None, "is_core": True, "description": "Physical cash and petty cash funds"},
    {"code": "1100", "name": "Bank Account", "type": "asset", "parent_code": None, "is_core": True, "description": "Primary business checking account"},
    {"code": "1200", "name": "Accounts Receivable", "type": "asset", "parent_code": None, "is_core": True, "description": "Money owed to the business by customers"},
    {"code": "1300", "name": "Inventory", "type": "asset", "parent_code": None, "is_core": True, "description": "Goods held for sale or raw materials"},
    
    # Standard Assets (2) - with parent relationships
    {"code": "1400", "name": "Prepaid Expenses", "type": "asset", "parent_code": "1000", "is_core": False, "description": "Expenses paid in advance (rent, insurance, etc.)"},
    {"code": "1500", "name": "Equipment", "type": "asset", "parent_code": "1000", "is_core": False, "description": "Fixed assets and equipment"},
    
    # ========== LIABILITIES (4 accounts) ==========
    # Core Liabilities (2)
    {"code": "2000", "name": "Accounts Payable", "type": "liability", "parent_code": None, "is_core": True, "description": "Money the business owes to suppliers and vendors"},
    {"code": "2100", "name": "Accrued Expenses", "type": "liability", "parent_code": None, "is_core": True, "description": "Expenses incurred but not yet paid (e.g., wages payable)"},
    
    # Standard Liabilities (2)
    {"code": "2200", "name": "Short-term Loans", "type": "liability", "parent_code": None, "is_core": False, "description": "Loans due within one year"},
    {"code": "2300", "name": "Credit Cards", "type": "liability", "parent_code": None, "is_core": False, "description": "Business credit card balances"},
    
    # ========== EQUITY (3 accounts) ==========
    # Core Equity (2)
    {"code": "3000", "name": "Owner's Equity", "type": "equity", "parent_code": None, "is_core": True, "description": "Owner's initial investment and net worth in the business"},
    {"code": "3100", "name": "Retained Earnings", "type": "equity", "parent_code": None, "is_core": True, "description": "Accumulated net income/loss over time"},
    
    # Standard Equity (1)
    {"code": "3200", "name": "Current Year Earnings", "type": "equity", "parent_code": None, "is_core": False, "description": "Current fiscal year net income/loss"},
    
    # ========== REVENUE (2 accounts) ==========
    # Core Revenue (2)
    {"code": "4000", "name": "Sales Revenue", "type": "revenue", "parent_code": None, "is_core": True, "description": "Primary income stream from selling products"},
    {"code": "4100", "name": "Service Revenue", "type": "revenue", "parent_code": None, "is_core": True, "description": "Primary income stream from selling services"},
    
    # ========== EXPENSES (10 accounts) ==========
    # Core Expenses (2)
    {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "parent_code": None, "is_core": True, "description": "Direct cost of products sold"},
    {"code": "6000", "name": "Rent Expense", "type": "expense", "parent_code": None, "is_core": False, "description": "Office/store rent payments"},
    
    # Standard Expenses (8)
    {"code": "6100", "name": "Utilities", "type": "expense", "parent_code": None, "is_core": False, "description": "Electricity, water, gas, internet, phone bills"},
    {"code": "6200", "name": "Salaries and Wages", "type": "expense", "parent_code": None, "is_core": False, "description": "Employee compensation and payroll"},
    {"code": "6300", "name": "Office Supplies", "type": "expense", "parent_code": None, "is_core": False, "description": "Office supplies and stationery"},
    {"code": "6400", "name": "Marketing and Advertising", "type": "expense", "parent_code": None, "is_core": False, "description": "Marketing campaigns and advertising costs"},
    {"code": "6500", "name": "Professional Services", "type": "expense", "parent_code": None, "is_core": False, "description": "Legal, accounting, consulting fees"},
    {"code": "6600", "name": "Insurance", "type": "expense", "parent_code": None, "is_core": False, "description": "Business insurance premiums"},
    {"code": "6700", "name": "Other Operating Expenses", "type": "expense", "parent_code": None, "is_core": False, "description": "Catch-all for miscellaneous operating expenses"},
    {"code": "6800", "name": "Depreciation Expense", "type": "expense", "parent_code": None, "is_core": False, "description": "Depreciation of fixed assets"},
]

def create_default_accounts(tenant_id: str, created_by: int, force: bool = False):
    """
    Create the universal 25 default accounts (12 core + 13 standard) for a tenant (company)
    
    Args:
        tenant_id: The tenant ID (company identifier) to create accounts for
        created_by: The user ID who is creating these accounts (audit trail)
        force: If True, recreate accounts even if they exist
    
    Returns:
        dict: {
            'created': list of created accounts,
            'skipped': list of skipped accounts (already exist),
            'total': total count,
            'new_count': count of newly created accounts
        }
    """
    created_accounts = []
    skipped_accounts = []
    account_map = {}  # Map codes to account IDs for parent relationships
    
    for account_data in DEFAULT_ACCOUNTS:
        # Check if account already exists for this tenant - TENANT-CENTRIC
        existing = Account.query.filter_by(
            code=account_data["code"],
            tenant_id=tenant_id  # TENANT-CENTRIC
        ).first()
        
        if existing and not force:
            skipped_accounts.append(existing)
            account_map[account_data["code"]] = existing.id
            logger.debug(f"Account {account_data['code']} already exists for tenant {tenant_id}, skipping")
            continue
        
        # If exists and force=True, delete and recreate
        if existing and force:
            logger.info(f"Force mode: Deleting existing account {account_data['code']} before recreating")
            db.session.delete(existing)
            db.session.flush()
        
        # Create new account - TENANT-CENTRIC
        try:
            logger.debug(f"Creating account: {account_data['code']} - {account_data['name']} for tenant {tenant_id}")
            account = Account(
                code=account_data["code"],
                name=account_data["name"],
                type=account_data["type"],
                balance=0.0,
                currency="USD",
                is_active=True,
                tenant_id=tenant_id,  # TENANT-CENTRIC: Company-wide account
                created_by=created_by,  # Audit trail: who created it
                notes=account_data.get("description"),  # Store description in notes field
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Set parent if specified
            if account_data.get("parent_code"):
                parent_id = account_map.get(account_data["parent_code"])
                if parent_id:
                    account.parent_id = parent_id
                else:
                    logger.warning(f"Parent account with code {account_data['parent_code']} not found for account {account_data['code']}")
            
            # Use savepoint to isolate individual account creation failures
            savepoint = db.session.begin_nested()  # Create a savepoint
            try:
                db.session.add(account)
                db.session.flush()  # Get the ID - this may raise IntegrityError if duplicate
                savepoint.commit()  # Commit this savepoint
                
                # Successfully created account
                created_accounts.append(account)
                account_map[account_data["code"]] = account.id
                logger.debug(f"✅ Created account: {account.code} - {account.name}")
                
            except Exception as flush_error:
                # Rollback only this savepoint, keeping other accounts
                savepoint.rollback()
                
                # Check if flush failed due to duplicate key
                error_str = str(flush_error).lower()
                is_duplicate = any(keyword in error_str for keyword in [
                    'duplicate key', 'unique constraint', 'uniqueviolation', 
                    'accounts_code_key', 'uq_account'
                ])
                
                if is_duplicate:
                    logger.warning(f"⚠️ Account code '{account_data.get('code', 'unknown')}' already exists in database, skipping...")
                    
                    # Try to find existing account for this tenant
                    existing = Account.query.filter_by(
                        code=account_data["code"],
                        tenant_id=tenant_id
                    ).first()
                    
                    if existing:
                        skipped_accounts.append(existing)
                        account_map[account_data["code"]] = existing.id
                        logger.info(f"✅ Found existing account for tenant: {account_data['code']} - {account_data['name']}")
                    else:
                        logger.info(f"ℹ️ Account {account_data['code']} exists globally but not for tenant {tenant_id}, skipping...")
                    
                    # Continue to next account - other accounts are safe in the outer transaction
                    continue
                else:
                    # Re-raise if it's a different error
                    raise
        except Exception as account_error:
            # Check if it's a duplicate key error
            error_str = str(account_error).lower()
            is_duplicate = any(keyword in error_str for keyword in [
                'duplicate key', 'unique constraint', 'uniqueviolation', 
                'accounts_code_key', 'uq_account'
            ])
            
            if is_duplicate:
                # Account already exists - rollback and skip gracefully
                logger.warning(f"⚠️ Account code '{account_data.get('code', 'unknown')}' already exists, skipping...")
                db.session.rollback()  # Rollback the failed insert
                
                # Try to find existing account for this tenant
                existing = Account.query.filter_by(
                    code=account_data["code"],
                    tenant_id=tenant_id
                ).first()
                
                if existing:
                    skipped_accounts.append(existing)
                    account_map[account_data["code"]] = existing.id
                    logger.info(f"✅ Using existing account: {account_data['code']} - {account_data['name']}")
                else:
                    # Account exists globally but not for this tenant - log and continue
                    logger.info(f"ℹ️ Account {account_data['code']} exists globally but not for tenant {tenant_id}, skipping...")
                
                # Continue to next account instead of failing
                continue
            else:
                # Some other error - log and re-raise
                logger.error(f"❌ Error creating account {account_data.get('code', 'unknown')}: {account_error}", exc_info=True)
                db.session.rollback()
                raise
    
    try:
        db.session.commit()
        logger.info(f"✅ Successfully created {len(created_accounts)} default accounts for tenant {tenant_id}")
        logger.info(f"   - New: {len(created_accounts)}, Skipped (already exist): {len(skipped_accounts)}")
        return {
            'created': [{'id': acc.id, 'code': acc.code, 'name': acc.name} for acc in created_accounts],
            'skipped': [{'id': acc.id, 'code': acc.code, 'name': acc.name} for acc in skipped_accounts],
            'total': len(created_accounts) + len(skipped_accounts),
            'new_count': len(created_accounts)
        }
    except Exception as e:
        error_str = str(e).lower()
        # Check if it's a duplicate key error on commit
        if 'duplicate key' in error_str or 'unique constraint' in error_str or 'uniqueviolation' in error_str:
            logger.warning(f"⚠️ Duplicate key error during commit - some accounts may already exist")
            db.session.rollback()
            # Try to get existing accounts for this tenant
            existing_accounts = tenant_query(Account).all()
            logger.info(f"   Found {len(existing_accounts)} existing accounts for tenant {tenant_id}")
            return {
                'created': [],
                'skipped': [{'id': acc.id, 'code': acc.code, 'name': acc.name} for acc in existing_accounts],
                'total': len(existing_accounts),
                'new_count': 0,
                'message': 'Accounts may already exist - skipped creation'
            }
        else:
            db.session.rollback()
            logger.error(f"❌ Error creating default accounts for tenant {tenant_id}: {e}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e

def get_default_accounts_preview():
    """
    Get preview of default accounts (for onboarding display)
    Returns the list without creating them
    """
    return DEFAULT_ACCOUNTS

def get_core_accounts():
    """
    Get only the 12 core accounts (for highlighting/badging)
    """
    return [acc for acc in DEFAULT_ACCOUNTS if acc.get('is_core', False)]

def get_standard_accounts():
    """
    Get only the 13 standard accounts
    """
    return [acc for acc in DEFAULT_ACCOUNTS if not acc.get('is_core', False)]

def check_tenant_has_accounts(tenant_id: str) -> bool:
    """
    Check if tenant (company) already has accounts - TENANT-CENTRIC
    Returns True if tenant has any accounts, False otherwise
    """
    count = tenant_query(Account).count()
    return count > 0

# Backward compatibility alias
def check_user_has_accounts(tenant_id: str) -> bool:
    """Backward compatibility - use check_tenant_has_accounts instead"""
    return check_tenant_has_accounts(tenant_id)

