"""
Tagging System for Chart of Accounts
Handles analytical tags vs statutory ledger accounts distinction
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .models import Account, JournalEntry, JournalLine, db

class TagCategory:
    """Represents a category of tags (e.g., Department, Project, Location)"""
    
    def __init__(self, id: str, name: str, description: str, is_required: bool = False, 
                 account_types: List[str] = None, validation_rules: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.is_required = is_required  # Whether this tag is required for certain accounts
        self.account_types = account_types or []  # Which account types this applies to
        self.validation_rules = validation_rules or {}  # Validation rules for this tag
        self.created_at = datetime.utcnow()
        self.is_active = True

class Tag:
    """Represents a specific tag value (e.g., "Sales Department", "Project Alpha")"""
    
    def __init__(self, category_id: str, value: str, description: str = None, 
                 metadata: Dict = None):
        self.category_id = category_id
        self.value = value
        self.description = description or value
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.is_active = True

class AccountTagRule:
    """Rules for which tags are required/optional for specific accounts"""
    
    def __init__(self, account_code: str, required_tags: List[str], 
                 optional_tags: List[str] = None, validation_rules: Dict = None):
        self.account_code = account_code
        self.required_tags = required_tags  # Tag category IDs that are required
        self.optional_tags = optional_tags or []  # Tag category IDs that are optional
        self.validation_rules = validation_rules or {}
        self.created_at = datetime.utcnow()

class TaggingSystem:
    """Main tagging system manager"""
    
    def __init__(self):
        self.tag_categories = self._initialize_tag_categories()
        self.account_rules = self._initialize_account_rules()
        self.tags = {}  # Will store actual tag values
    
    def _initialize_tag_categories(self) -> Dict[str, TagCategory]:
        """Initialize standard tag categories"""
        categories = {}
        
        # Management/Reporting Tags
        categories['department'] = TagCategory(
            id='department',
            name='Department',
            description='Organizational department',
            is_required=False,
            account_types=['expense', 'revenue'],
            validation_rules={'max_length': 50, 'allowed_values': None}
        )
        
        categories['project'] = TagCategory(
            id='project',
            name='Project',
            description='Project or initiative',
            is_required=False,
            account_types=['expense', 'revenue', 'asset'],
            validation_rules={'max_length': 100, 'allowed_values': None}
        )
        
        categories['location'] = TagCategory(
            id='location',
            name='Location',
            description='Geographic or physical location',
            is_required=False,
            account_types=['asset', 'expense'],
            validation_rules={'max_length': 50, 'allowed_values': None}
        )
        
        categories['cost_center'] = TagCategory(
            id='cost_center',
            name='Cost Center',
            description='Cost center for expense allocation',
            is_required=False,
            account_types=['expense'],
            validation_rules={'max_length': 30, 'allowed_values': None}
        )
        
        categories['product_category'] = TagCategory(
            id='product_category',
            name='Product Category',
            description='Product or service category',
            is_required=True,  # Required for revenue and COGS accounts
            account_types=['revenue', 'expense'],
            validation_rules={'max_length': 50, 'allowed_values': None}
        )
        
        categories['sales_channel'] = TagCategory(
            id='sales_channel',
            name='Sales Channel',
            description='Channel through which sales are made',
            is_required=True,  # Required for revenue accounts
            account_types=['revenue'],
            validation_rules={'max_length': 30, 'allowed_values': ['Online', 'Retail', 'Wholesale', 'Direct']}
        )
        
        categories['customer'] = TagCategory(
            id='customer',
            name='Customer',
            description='Customer identifier',
            is_required=True,  # Required for AR accounts
            account_types=['asset'],
            validation_rules={'max_length': 100, 'allowed_values': None}
        )
        
        categories['vendor'] = TagCategory(
            id='vendor',
            name='Vendor',
            description='Vendor identifier',
            is_required=True,  # Required for AP accounts
            account_types=['liability'],
            validation_rules={'max_length': 100, 'allowed_values': None}
        )
        
        categories['employee'] = TagCategory(
            id='employee',
            name='Employee',
            description='Employee identifier',
            is_required=False,
            account_types=['expense'],
            validation_rules={'max_length': 50, 'allowed_values': None}
        )
        
        categories['fund'] = TagCategory(
            id='fund',
            name='Fund',
            description='Fund or grant identifier (for NGOs)',
            is_required=False,
            account_types=['asset', 'liability', 'equity', 'revenue', 'expense'],
            validation_rules={'max_length': 50, 'allowed_values': None}
        )
        
        return categories
    
    def _initialize_account_rules(self) -> Dict[str, AccountTagRule]:
        """Initialize tagging rules for specific account types"""
        rules = {}
        
        # Revenue accounts must have product_category and sales_channel
        rules['revenue'] = AccountTagRule(
            account_code='4000',  # Sales Revenue
            required_tags=['product_category', 'sales_channel'],
            optional_tags=['customer', 'project', 'department']
        )
        
        # COGS accounts must have product_category
        rules['cogs'] = AccountTagRule(
            account_code='5000',  # Cost of Goods Sold
            required_tags=['product_category'],
            optional_tags=['vendor', 'project', 'department', 'location']
        )
        
        # AR accounts must have customer
        rules['ar'] = AccountTagRule(
            account_code='1100',  # Accounts Receivable
            required_tags=['customer'],
            optional_tags=['project', 'department']
        )
        
        # AP accounts must have vendor
        rules['ap'] = AccountTagRule(
            account_code='2000',  # Accounts Payable
            required_tags=['vendor'],
            optional_tags=['project', 'department']
        )
        
        # Inventory accounts must have product_category and location
        rules['inventory'] = AccountTagRule(
            account_code='1200',  # Inventory
            required_tags=['product_category', 'location'],
            optional_tags=['vendor', 'project']
        )
        
        # Expense accounts can have various tags
        rules['expense'] = AccountTagRule(
            account_code='6000',  # Operating Expenses
            required_tags=[],
            optional_tags=['department', 'project', 'cost_center', 'employee', 'vendor']
        )
        
        return rules
    
    def get_required_tags_for_account(self, account_code: str) -> List[str]:
        """Get required tags for a specific account"""
        # Check specific account rules first
        for rule in self.account_rules.values():
            if rule.account_code == account_code:
                return rule.required_tags
        
        # Check by account type
        account = Account.query.filter_by(code=account_code).first()
        if not account:
            return []
        
        required_tags = []
        for category in self.tag_categories.values():
            if account.type in category.account_types and category.is_required:
                required_tags.append(category.id)
        
        return required_tags
    
    def get_optional_tags_for_account(self, account_code: str) -> List[str]:
        """Get optional tags for a specific account"""
        # Check specific account rules first
        for rule in self.account_rules.values():
            if rule.account_code == account_code:
                return rule.optional_tags
        
        # Check by account type
        account = Account.query.filter_by(code=account_code).first()
        if not account:
            return []
        
        optional_tags = []
        for category in self.tag_categories.values():
            if account.type in category.account_types and not category.is_required:
                optional_tags.append(category.id)
        
        return required_tags
    
    def validate_transaction_tags(self, account_code: str, tags: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate tags for a transaction"""
        errors = []
        required_tags = self.get_required_tags_for_account(account_code)
        
        # Check required tags
        for required_tag in required_tags:
            if required_tag not in tags or not tags[required_tag]:
                errors.append(f"Required tag '{required_tag}' is missing")
        
        # Validate tag values
        for tag_category, tag_value in tags.items():
            if tag_category in self.tag_categories:
                category = self.tag_categories[tag_category]
                validation_rules = category.validation_rules
                
                # Check max length
                if 'max_length' in validation_rules:
                    if len(tag_value) > validation_rules['max_length']:
                        errors.append(f"Tag '{tag_category}' exceeds maximum length of {validation_rules['max_length']}")
                
                # Check allowed values
                if 'allowed_values' in validation_rules and validation_rules['allowed_values']:
                    if tag_value not in validation_rules['allowed_values']:
                        errors.append(f"Tag '{tag_category}' value '{tag_value}' is not in allowed values: {validation_rules['allowed_values']}")
        
        return len(errors) == 0, errors
    
    def get_tag_categories(self) -> List[Dict[str, Any]]:
        """Get all tag categories"""
        return [
            {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'is_required': category.is_required,
                'account_types': category.account_types,
                'validation_rules': category.validation_rules
            }
            for category in self.tag_categories.values()
        ]
    
    def get_account_tagging_rules(self, account_code: str) -> Dict[str, Any]:
        """Get tagging rules for a specific account"""
        account = Account.query.filter_by(code=account_code).first()
        if not account:
            return {}
        
        required_tags = self.get_required_tags_for_account(account_code)
        optional_tags = self.get_optional_tags_for_account(account_code)
        
        # Get tag category details
        required_tag_details = []
        for tag_id in required_tags:
            if tag_id in self.tag_categories:
                category = self.tag_categories[tag_id]
                required_tag_details.append({
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'validation_rules': category.validation_rules
                })
        
        optional_tag_details = []
        for tag_id in optional_tags:
            if tag_id in self.tag_categories:
                category = self.tag_categories[tag_id]
                optional_tag_details.append({
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'validation_rules': category.validation_rules
                })
        
        return {
            'account_code': account_code,
            'account_name': account.name,
            'account_type': account.type,
            'required_tags': required_tag_details,
            'optional_tags': optional_tag_details,
            'total_required': len(required_tags),
            'total_optional': len(optional_tags)
        }
    
    def get_ledger_vs_tag_distinction(self) -> Dict[str, Any]:
        """Get clear distinction between ledger accounts and tags"""
        return {
            'ledger_accounts': {
                'description': 'Core accounting accounts required for financial statements and compliance',
                'characteristics': [
                    'Required for statutory reporting',
                    'Must follow accounting standards',
                    'Cannot be deleted if they have transactions',
                    'Used for audit trails',
                    'Required for tax compliance'
                ],
                'examples': ['Cash', 'Accounts Receivable', 'Sales Revenue', 'Cost of Goods Sold']
            },
            'tags': {
                'description': 'Analytical dimensions for management reporting and analysis',
                'characteristics': [
                    'Used for segmentation and analysis',
                    'Can be added/removed as needed',
                  'Not required for compliance',
                    'Used for management reporting',
                    'Help with data organization'
                ],
                'examples': ['Department', 'Project', 'Customer', 'Product Category', 'Location']
            },
            'rules': [
                'Ledger accounts are mandatory for compliance',
                'Tags are optional for analysis',
                'Revenue accounts must be tagged by product category',
                'AR accounts must be tagged by customer',
                'AP accounts must be tagged by vendor',
                'Tags cannot replace ledger accounts for statutory reporting'
            ]
        }

# Global instance
tagging_system = TaggingSystem()

def get_tagging_system() -> TaggingSystem:
    """Get the global tagging system instance"""
    return tagging_system


