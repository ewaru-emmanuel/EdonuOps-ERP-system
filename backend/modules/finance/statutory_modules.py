"""
Statutory Module System for Chart of Accounts
Handles safe activation/deactivation of tax and compliance modules
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .models import Account, JournalEntry, JournalLine, db

class StatutoryModule:
    """Represents a statutory module (GST, TDS, VAT, etc.)"""
    
    def __init__(self, id: str, name: str, description: str, country: str, 
                 required_accounts: List[str], compliance_forms: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.country = country
        self.required_accounts = required_accounts  # Account codes required for this module
        self.compliance_forms = compliance_forms or []  # Forms this module generates
        self.is_active = False
        self.activation_date = None
        self.deactivation_date = None
        self.accounts = []  # Will be populated with actual Account objects
    
    def can_activate(self) -> Tuple[bool, str]:
        """Check if module can be activated safely"""
        # Check if all required accounts exist
        missing_accounts = []
        for account_code in self.required_accounts:
            if not Account.query.filter_by(code=account_code).first():
                missing_accounts.append(account_code)
        
        if missing_accounts:
            return False, f"Missing required accounts: {', '.join(missing_accounts)}"
        
        return True, "Module can be activated"
    
    def can_deactivate(self) -> Tuple[bool, str, List[Dict]]:
        """Check if module can be deactivated safely"""
        issues = []
        
        # Check for open balances in module accounts
        for account_code in self.required_accounts:
            account = Account.query.filter_by(code=account_code).first()
            if account and account.balance != 0:
                issues.append({
                    'type': 'open_balance',
                    'account_code': account_code,
                    'account_name': account.name,
                    'balance': account.balance,
                    'message': f"Account {account_code} has non-zero balance: {account.balance}"
                })
        
        # Check for pending journal entries
        pending_entries = JournalEntry.query.filter(
            JournalEntry.status == 'draft',
            JournalEntry.lines.any(
                JournalLine.account_id.in_([
                    Account.query.filter_by(code=code).first().id 
                    for code in self.required_accounts 
                    if Account.query.filter_by(code=code).first()
                ])
            )
        ).all()
        
        if pending_entries:
            issues.append({
                'type': 'pending_entries',
                'count': len(pending_entries),
                'message': f"Found {len(pending_entries)} pending journal entries affecting module accounts"
            })
        
        # Check for recent transactions (last 30 days)
        thirty_days_ago = datetime.utcnow().replace(day=1)  # Simplified date logic
        recent_entries = JournalEntry.query.filter(
            JournalEntry.created_at >= thirty_days_ago,
            JournalEntry.lines.any(
                JournalLine.account_id.in_([
                    Account.query.filter_by(code=code).first().id 
                    for code in self.required_accounts 
                    if Account.query.filter_by(code=code).first()
                ])
            )
        ).all()
        
        if recent_entries:
            issues.append({
                'type': 'recent_activity',
                'count': len(recent_entries),
                'message': f"Found {len(recent_entries)} recent transactions (last 30 days)"
            })
        
        if issues:
            return False, "Module cannot be deactivated due to data dependencies", issues
        
        return True, "Module can be safely deactivated", []
    
    def activate(self) -> Tuple[bool, str]:
        """Activate the statutory module"""
        can_activate, message = self.can_activate()
        if not can_activate:
            return False, message
        
        try:
            # Mark accounts as active for this module
            for account_code in self.required_accounts:
                account = Account.query.filter_by(code=account_code).first()
                if account:
                    account.is_active = True
                    self.accounts.append(account)
            
            self.is_active = True
            self.activation_date = datetime.utcnow()
            self.deactivation_date = None
            
            db.session.commit()
            return True, f"Module '{self.name}' activated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to activate module: {str(e)}"
    
    def deactivate(self, force: bool = False) -> Tuple[bool, str, List[Dict]]:
        """Deactivate the statutory module"""
        can_deactivate, message, issues = self.can_deactivate()
        
        if not can_deactivate and not force:
            return False, message, issues
        
        try:
            if force:
                # Force deactivation - make accounts read-only instead of inactive
                for account_code in self.required_accounts:
                    account = Account.query.filter_by(code=account_code).first()
                    if account:
                        # Add a flag to mark as read-only for this module
                        account.is_active = False  # This would need a more sophisticated approach
                        self.accounts.append(account)
            else:
                # Safe deactivation - just mark as inactive
                for account_code in self.required_accounts:
                    account = Account.query.filter_by(code=account_code).first()
                    if account:
                        account.is_active = False
                        self.accounts.append(account)
            
            self.is_active = False
            self.deactivation_date = datetime.utcnow()
            
            db.session.commit()
            return True, f"Module '{self.name}' deactivated successfully", []
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to deactivate module: {str(e)}", []

class StatutoryModuleManager:
    """Manages all statutory modules for a company"""
    
    def __init__(self, country: str = 'US'):
        self.country = country
        self.modules = self._initialize_modules()
    
    def _initialize_modules(self) -> Dict[str, StatutoryModule]:
        """Initialize statutory modules based on country"""
        modules = {}
        
        if self.country.upper() in ['US', 'USA']:
            modules.update(self._get_us_modules())
        elif self.country.upper() in ['IN', 'INDIA']:
            modules.update(self._get_india_modules())
        elif self.country.upper() in ['GB', 'UK']:
            modules.update(self._get_uk_modules())
        elif self.country.upper() in ['KE', 'KENYA']:
            modules.update(self._get_kenya_modules())
        else:
            # Default to basic modules
            modules.update(self._get_basic_modules())
        
        return modules
    
    def _get_us_modules(self) -> Dict[str, StatutoryModule]:
        """US-specific statutory modules"""
        return {
            'sales_tax': StatutoryModule(
                id='sales_tax',
                name='Sales Tax',
                description='US Sales Tax compliance',
                country='US',
                required_accounts=['2100', '2110'],  # Sales Tax Payable, Sales Tax Receivable
                compliance_forms=['Form 941', 'Form 940']
            ),
            'payroll_tax': StatutoryModule(
                id='payroll_tax',
                name='Payroll Tax',
                description='US Payroll Tax compliance',
                country='US',
                required_accounts=['2120', '2130', '2140'],  # Payroll Tax Payable, etc.
                compliance_forms=['Form 941', 'Form 940', 'W-2', 'W-3']
            ),
            'income_tax': StatutoryModule(
                id='income_tax',
                name='Income Tax',
                description='US Income Tax compliance',
                country='US',
                required_accounts=['2150', '2160'],  # Income Tax Payable, etc.
                compliance_forms=['Form 1120', 'Form 1040']
            )
        }
    
    def _get_india_modules(self) -> Dict[str, StatutoryModule]:
        """India-specific statutory modules"""
        return {
            'gst': StatutoryModule(
                id='gst',
                name='GST (Goods & Services Tax)',
                description='Indian GST compliance',
                country='IN',
                required_accounts=['2200', '2210', '2220', '2230'],  # Input GST, Output GST, etc.
                compliance_forms=['GSTR-1', 'GSTR-3B', 'GSTR-9']
            ),
            'tds': StatutoryModule(
                id='tds',
                name='TDS (Tax Deducted at Source)',
                description='Indian TDS compliance',
                country='IN',
                required_accounts=['2240', '2250'],  # TDS Payable, TDS Receivable
                compliance_forms=['Form 16', 'Form 16A', 'Form 26Q', 'Form 27Q']
            ),
            'income_tax': StatutoryModule(
                id='income_tax',
                name='Income Tax',
                description='Indian Income Tax compliance',
                country='IN',
                required_accounts=['2260', '2270'],  # Income Tax Payable, etc.
                compliance_forms=['Form 16', 'Form 16A', 'ITR']
            )
        }
    
    def _get_uk_modules(self) -> Dict[str, StatutoryModule]:
        """UK-specific statutory modules"""
        return {
            'vat': StatutoryModule(
                id='vat',
                name='VAT (Value Added Tax)',
                description='UK VAT compliance',
                country='GB',
                required_accounts=['2300', '2310', '2320'],  # Input VAT, Output VAT, etc.
                compliance_forms=['VAT Return', 'VAT100']
            ),
            'paye': StatutoryModule(
                id='paye',
                name='PAYE (Pay As You Earn)',
                description='UK PAYE compliance',
                country='GB',
                required_accounts=['2330', '2340'],  # PAYE Payable, etc.
                compliance_forms=['P60', 'P45', 'P11D']
            )
        }
    
    def _get_kenya_modules(self) -> Dict[str, StatutoryModule]:
        """Kenya-specific statutory modules"""
        return {
            'vat': StatutoryModule(
                id='vat',
                name='VAT (Value Added Tax)',
                description='Kenyan VAT compliance',
                country='KE',
                required_accounts=['2400', '2410', '2420'],  # Input VAT, Output VAT, etc.
                compliance_forms=['VAT Return', 'VAT3']
            ),
            'withholding_tax': StatutoryModule(
                id='withholding_tax',
                name='Withholding Tax',
                description='Kenyan Withholding Tax compliance',
                country='KE',
                required_accounts=['2430', '2440'],  # WHT Payable, WHT Receivable
                compliance_forms=['WHT Certificate', 'WHT Return']
            )
        }
    
    def _get_basic_modules(self) -> Dict[str, StatutoryModule]:
        """Basic modules for countries without specific compliance requirements"""
        return {
            'basic_tax': StatutoryModule(
                id='basic_tax',
                name='Basic Tax',
                description='Basic tax compliance',
                country='GLOBAL',
                required_accounts=['2500', '2510'],  # Tax Payable, Tax Receivable
                compliance_forms=['Tax Return']
            )
        }
    
    def get_module(self, module_id: str) -> Optional[StatutoryModule]:
        """Get a specific statutory module"""
        return self.modules.get(module_id)
    
    def get_active_modules(self) -> List[StatutoryModule]:
        """Get all currently active modules"""
        return [module for module in self.modules.values() if module.is_active]
    
    def get_inactive_modules(self) -> List[StatutoryModule]:
        """Get all currently inactive modules"""
        return [module for module in self.modules.values() if not module.is_active]
    
    def get_modules_by_country(self, country: str) -> List[StatutoryModule]:
        """Get all modules for a specific country"""
        return [module for module in self.modules.values() if module.country.upper() == country.upper()]
    
    def activate_module(self, module_id: str) -> Tuple[bool, str]:
        """Activate a statutory module"""
        module = self.get_module(module_id)
        if not module:
            return False, f"Module '{module_id}' not found"
        
        return module.activate()
    
    def deactivate_module(self, module_id: str, force: bool = False) -> Tuple[bool, str, List[Dict]]:
        """Deactivate a statutory module"""
        module = self.get_module(module_id)
        if not module:
            return False, f"Module '{module_id}' not found", []
        
        return module.deactivate(force)
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status for the company"""
        active_modules = self.get_active_modules()
        inactive_modules = self.get_inactive_modules()
        
        return {
            'country': self.country,
            'total_modules': len(self.modules),
            'active_modules': len(active_modules),
            'inactive_modules': len(inactive_modules),
            'compliance_forms_required': list(set([
                form for module in active_modules 
                for form in module.compliance_forms
            ])),
            'modules': {
                'active': [
                    {
                        'id': module.id,
                        'name': module.name,
                        'description': module.description,
                        'activation_date': module.activation_date.isoformat() if module.activation_date else None
                    } for module in active_modules
                ],
                'inactive': [
                    {
                        'id': module.id,
                        'name': module.name,
                        'description': module.description,
                        'can_activate': module.can_activate()[0]
                    } for module in inactive_modules
                ]
            }
        }

# Global instance - would be initialized per company in production
def get_statutory_module_manager(country: str = 'US') -> StatutoryModuleManager:
    """Get statutory module manager for a specific country"""
    return StatutoryModuleManager(country)

