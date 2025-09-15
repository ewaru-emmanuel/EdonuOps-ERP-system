"""
Chart of Accounts Templates for Different Industries
Building on top of existing Account model
"""

from typing import Dict, List, Any, Optional
from .models import Account

class COATemplate:
    """Chart of Accounts template for different industries"""
    
    def __init__(self, name: str, description: str, industry: str):
        self.name = name
        self.description = description
        self.industry = industry
        self.accounts = []
        self.workflows = []
        self.statutory_modules = []
    
    def add_account(self, code: str, name: str, type: str, parent_code: str = None, 
                   is_core: bool = True, required_tags: List[str] = None, 
                   description: str = None, statutory_module: str = None):
        """Add an account to the template"""
        account = {
            'code': code,
            'name': name,
            'type': type,
            'parent_code': parent_code,
            'is_core': is_core,  # Shows in basic mode (30 accounts)
            'required_tags': required_tags or [],
            'description': description or f"{name} account for {self.industry} businesses",
            'statutory_module': statutory_module  # Which module this account belongs to
        }
        self.accounts.append(account)
        return account

def create_retail_template() -> COATemplate:
    """Retail business CoA template - 30 core accounts + optional"""
    template = COATemplate(
        name="Retail Business",
        description="Complete CoA for retail businesses with inventory management",
        industry="retail"
    )
    
    # CORE ASSETS (15 accounts)
    template.add_account("1000", "Cash and Cash Equivalents", "asset", is_core=True)
    template.add_account("1020", "Business Checking", "asset", "1000", is_core=True)
    template.add_account("1030", "Petty Cash", "asset", "1000", is_core=False)
    
    template.add_account("1100", "Accounts Receivable", "asset", is_core=True, 
                        required_tags=["customer"])
    template.add_account("1110", "Allowance for Bad Debts", "asset", "1100", is_core=True)
    
    template.add_account("1200", "Inventory", "asset", is_core=True, 
                        required_tags=["product_category", "location"])
    template.add_account("1210", "Finished Goods", "asset", "1200", is_core=True)
    template.add_account("1220", "Raw Materials", "asset", "1200", is_core=False)
    
    template.add_account("1300", "Prepaid Expenses", "asset", is_core=True)
    template.add_account("1310", "Prepaid Rent", "asset", "1300", is_core=True)
    template.add_account("1320", "Prepaid Insurance", "asset", "1300", is_core=True)
    
    template.add_account("1400", "Fixed Assets", "asset", is_core=True)
    template.add_account("1410", "Store Equipment", "asset", "1400", is_core=True)
    template.add_account("1420", "Computer Equipment", "asset", "1400", is_core=True)
    template.add_account("1430", "Accumulated Depreciation", "asset", "1400", is_core=True)
    
    # CORE LIABILITIES (5 accounts)
    template.add_account("2000", "Accounts Payable", "liability", is_core=True, 
                        required_tags=["vendor"])
    template.add_account("2100", "Accrued Expenses", "liability", is_core=True)
    template.add_account("2110", "Accrued Wages", "liability", "2100", is_core=True)
    template.add_account("2200", "Short-term Loans", "liability", is_core=False)
    template.add_account("2300", "Long-term Loans", "liability", is_core=False)
    
    # CORE EQUITY (3 accounts)
    template.add_account("3000", "Owner's Equity", "equity", is_core=True)
    template.add_account("3100", "Retained Earnings", "equity", is_core=True)
    template.add_account("3200", "Current Year Earnings", "equity", is_core=True)
    
    # CORE REVENUE (2 accounts)
    template.add_account("4000", "Sales Revenue", "revenue", is_core=True, 
                        required_tags=["product_category", "sales_channel"])
    template.add_account("4100", "Service Revenue", "revenue", is_core=False)
    
    # CORE EXPENSES (5 accounts)
    template.add_account("5000", "Cost of Goods Sold", "expense", is_core=True, 
                        required_tags=["product_category"])
    template.add_account("6000", "Operating Expenses", "expense", is_core=True)
    template.add_account("6100", "Rent Expense", "expense", "6000", is_core=True)
    template.add_account("6200", "Utilities", "expense", "6000", is_core=True)
    template.add_account("6300", "Salaries and Wages", "expense", "6000", is_core=True)
    
    # Additional accounts for advanced mode
    template.add_account("6400", "Marketing and Advertising", "expense", "6000", is_core=False)
    template.add_account("6500", "Insurance", "expense", "6000", is_core=False)
    template.add_account("6600", "Professional Services", "expense", "6000", is_core=False)
    template.add_account("6700", "Office Supplies", "expense", "6000", is_core=False)
    template.add_account("6800", "Depreciation", "expense", "6000", is_core=False)
    
    # Workflows
    template.workflows = [
        {
            "name": "Record Sale",
            "description": "Process a customer sale with inventory",
            "accounts_affected": ["4000", "5000", "1210", "1100"],
            "ui_form": "sale_form"
        },
        {
            "name": "Purchase Inventory", 
            "description": "Record inventory purchase from vendor",
            "accounts_affected": ["1210", "2000"],
            "ui_form": "purchase_form"
        }
    ]
    
    return template

def create_services_template() -> COATemplate:
    """Services business CoA template - 30 core accounts + optional"""
    template = COATemplate(
        name="Services Business", 
        description="Complete CoA for service-based businesses",
        industry="services"
    )
    
    # CORE ASSETS (12 accounts)
    template.add_account("1000", "Cash and Cash Equivalents", "asset", is_core=True)
    template.add_account("1020", "Business Checking", "asset", "1000", is_core=True)
    template.add_account("1100", "Accounts Receivable", "asset", is_core=True, 
                        required_tags=["client", "project"])
    template.add_account("1200", "Prepaid Expenses", "asset", is_core=True)
    template.add_account("1300", "Fixed Assets", "asset", is_core=True)
    
    # CORE LIABILITIES (4 accounts)
    template.add_account("2000", "Accounts Payable", "liability", is_core=True, 
                        required_tags=["vendor"])
    template.add_account("2100", "Accrued Expenses", "liability", is_core=True)
    template.add_account("2200", "Deferred Revenue", "liability", is_core=True, 
                        required_tags=["client", "project"])
    
    # CORE EQUITY (3 accounts)
    template.add_account("3000", "Owner's Equity", "equity", is_core=True)
    template.add_account("3100", "Retained Earnings", "equity", is_core=True)
    template.add_account("3200", "Current Year Earnings", "equity", is_core=True)
    
    # CORE REVENUE (2 accounts)
    template.add_account("4000", "Service Revenue", "revenue", is_core=True, 
                        required_tags=["client", "service_type", "project"])
    
    # CORE EXPENSES (9 accounts)
    template.add_account("5000", "Direct Labor", "expense", is_core=True, 
                        required_tags=["employee", "project"])
    template.add_account("6000", "Operating Expenses", "expense", is_core=True)
    template.add_account("6100", "Rent Expense", "expense", "6000", is_core=True)
    template.add_account("6200", "Utilities", "expense", "6000", is_core=True)
    template.add_account("6300", "Salaries and Wages", "expense", "6000", is_core=True)
    
    return template

def create_manufacturing_template() -> COATemplate:
    """Manufacturing business CoA template - 30 core accounts + optional"""
    template = COATemplate(
        name="Manufacturing Business",
        description="Complete CoA for manufacturing businesses with production tracking",
        industry="manufacturing"
    )
    
    # CORE ASSETS (15 accounts)
    template.add_account("1000", "Cash and Cash Equivalents", "asset", is_core=True)
    template.add_account("1020", "Business Checking", "asset", "1000", is_core=True)
    template.add_account("1100", "Accounts Receivable", "asset", is_core=True, 
                        required_tags=["customer"])
    template.add_account("1200", "Inventory", "asset", is_core=True, 
                        required_tags=["product_line", "warehouse"])
    template.add_account("1300", "Prepaid Expenses", "asset", is_core=True)
    template.add_account("1400", "Fixed Assets", "asset", is_core=True)
    
    # CORE LIABILITIES (5 accounts)
    template.add_account("2000", "Accounts Payable", "liability", is_core=True, 
                        required_tags=["vendor"])
    template.add_account("2100", "Accrued Expenses", "liability", is_core=True)
    
    # CORE EQUITY (3 accounts)
    template.add_account("3000", "Owner's Equity", "equity", is_core=True)
    template.add_account("3100", "Retained Earnings", "equity", is_core=True)
    template.add_account("3200", "Current Year Earnings", "equity", is_core=True)
    
    # CORE REVENUE (2 accounts)
    template.add_account("4000", "Sales Revenue", "revenue", is_core=True, 
                        required_tags=["product_line", "customer"])
    
    # CORE EXPENSES (5 accounts)
    template.add_account("5000", "Cost of Goods Sold", "expense", is_core=True, 
                        required_tags=["product_line"])
    template.add_account("6000", "Operating Expenses", "expense", is_core=True)
    
    return template

def create_freelancer_template() -> COATemplate:
    """Freelancer CoA template - simplified for solo entrepreneurs"""
    template = COATemplate(
        name="Freelancer Business",
        description="Simplified CoA for freelancers and solo entrepreneurs",
        industry="freelancer"
    )
    
    # CORE ASSETS (8 accounts)
    template.add_account("1000", "Cash and Cash Equivalents", "asset", is_core=True)
    template.add_account("1020", "Business Checking", "asset", "1000", is_core=True)
    template.add_account("1100", "Accounts Receivable", "asset", is_core=True, 
                        required_tags=["client"])
    template.add_account("1200", "Prepaid Expenses", "asset", is_core=True)
    template.add_account("1300", "Fixed Assets", "asset", is_core=True)
    
    # CORE LIABILITIES (4 accounts)
    template.add_account("2000", "Accounts Payable", "liability", is_core=True, 
                        required_tags=["vendor"])
    template.add_account("2100", "Accrued Expenses", "liability", is_core=True)
    template.add_account("2200", "Deferred Revenue", "liability", is_core=True, 
                        required_tags=["client"])
    
    # CORE EQUITY (3 accounts)
    template.add_account("3000", "Owner's Equity", "equity", is_core=True)
    template.add_account("3100", "Retained Earnings", "equity", is_core=True)
    template.add_account("3200", "Current Year Earnings", "equity", is_core=True)
    
    # CORE REVENUE (2 accounts)
    template.add_account("4000", "Service Revenue", "revenue", is_core=True, 
                        required_tags=["client", "service_type"])
    
    # CORE EXPENSES (13 accounts)
    template.add_account("5000", "Operating Expenses", "expense", is_core=True)
    template.add_account("5100", "Home Office", "expense", "5000", is_core=True)
    template.add_account("5200", "Software Subscriptions", "expense", "5000", is_core=True)
    template.add_account("5300", "Marketing", "expense", "5000", is_core=True)
    template.add_account("5400", "Professional Development", "expense", "5000", is_core=True)
    template.add_account("5500", "Insurance", "expense", "5000", is_core=True)
    template.add_account("5600", "Office Supplies", "expense", "5000", is_core=True)
    template.add_account("5700", "Travel", "expense", "5000", is_core=True)
    template.add_account("5800", "Depreciation", "expense", "5000", is_core=True)
    
    return template

# Template registry
COA_TEMPLATES = {
    "retail": create_retail_template(),
    "services": create_services_template(), 
    "manufacturing": create_manufacturing_template(),
    "freelancer": create_freelancer_template()
}

def get_template(industry: str) -> Optional[COATemplate]:
    """Get CoA template for specific industry"""
    return COA_TEMPLATES.get(industry.lower())

def get_all_templates() -> Dict[str, COATemplate]:
    """Get all available CoA templates"""
    return COA_TEMPLATES

def get_core_accounts(template: COATemplate) -> List[Dict[str, Any]]:
    """Get only core accounts (for basic mode - 30 accounts)"""
    return [acc for acc in template.accounts if acc.get('is_core', True)]

def get_advanced_accounts(template: COATemplate) -> List[Dict[str, Any]]:
    """Get all accounts (for advanced mode)"""
    return template.accounts

def create_accounts_from_template(template: COATemplate, user_id: int = 1) -> List[Account]:
    """Create Account objects from template for database insertion"""
    accounts = []
    account_map = {}  # To handle parent relationships
    
    for acc_data in template.accounts:
        account = Account(
            code=acc_data['code'],
            name=acc_data['name'],
            type=acc_data['type'],
            parent_id=account_map.get(acc_data.get('parent_code')),
            is_active=True
        )
        accounts.append(account)
        account_map[acc_data['code']] = account
    
    return accounts
