"""
Transaction Templates System
============================

This module provides business logic templates that automatically create proper
double-entry journal entries from simple business transactions.

Phase 2: Business Logic Templates
- Cash Sales
- Bank Payments
- Expense Payments
- Purchase Transactions
- And more...

The magic: User says "Cash Sales $500" → System creates:
- Cash Account (Debit $500)
- Sales Revenue (Credit $500)
"""

from app import db
from modules.finance.models import JournalEntry, JournalLine, Account
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TransactionTemplate:
    """Base class for transaction templates"""
    
    def __init__(self, template_id: str, name: str, description: str, manager=None):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.manager = manager
    
    def create_journal_entry(self, amount: float, description: str, **kwargs) -> Dict:
        """
        Create a journal entry using this template
        
        Args:
            amount: Transaction amount
            description: Transaction description
            **kwargs: Additional parameters specific to the template
            
        Returns:
            Dict with journal entry data
        """
        raise NotImplementedError("Subclasses must implement create_journal_entry")
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields for this template"""
        return ['amount', 'description']
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        required_fields = self.get_required_fields()
        print("DEBUG: Incoming kwargs:", kwargs)
        print("DEBUG: Required fields:", required_fields)
        for field in required_fields:
            print(f"DEBUG: Checking field '{field}': present={field in kwargs}, value={kwargs.get(field)}, type={type(kwargs.get(field))}")
            if field not in kwargs or kwargs[field] is None:
                print(f"DEBUG: Missing or None field: {field}")
                return False
        print("DEBUG: All validation checks passed")
        return True
    
    def _get_account_by_code(self, code: str) -> Optional[Account]:
        """Helper method to get account by code"""
        if self.manager:
            return self.manager._get_account_by_code(code)
        return Account.query.filter_by(account_code=code).first()

class CashSalesTemplate(TransactionTemplate):
    """Template for cash sales transactions"""
    
    def __init__(self, manager=None):
        super().__init__(
            template_id="cash_sales",
            name="Cash Sales",
            description="Record cash sales transactions",
            manager=manager
        )
    
    def create_journal_entry(self, amount: float, description: str, **kwargs) -> Dict:
        """Create cash sales journal entry"""
        if not self.validate_input(amount=amount, description=description):
            raise ValueError("Invalid input parameters")
        
        # Get accounts
        cash_account = self._get_account_by_code("1000")  # Cash on Hand
        sales_revenue_account = self._get_account_by_code("4000")  # Sales Revenue
        
        if not cash_account or not sales_revenue_account:
            raise ValueError("Required accounts not found")
        
        # Create journal lines
        lines = [
            {
                "account_id": cash_account.id,
                "account_name": cash_account.name,
                "description": f"Cash received for: {description}",
                "debit_amount": amount,
                "credit_amount": 0.0
            },
            {
                "account_id": sales_revenue_account.id,
                "account_name": sales_revenue_account.name,
                "description": f"Sales revenue from: {description}",
                "debit_amount": 0.0,
                "credit_amount": amount
            }
        ]
        
        return {
            "description": f"Cash Sales: {description}",
            "payment_method": "cash",
            "lines": lines,
            "total_debits": amount,
            "total_credits": amount
        }

class BankSalesTemplate(TransactionTemplate):
    """Template for bank sales transactions"""
    
    def __init__(self, manager=None):
        super().__init__(
            template_id="bank_sales",
            name="Bank Sales",
            description="Record bank sales transactions",
            manager=manager
        )
    
    def create_journal_entry(self, amount: float, description: str, **kwargs) -> Dict:
        """Create bank sales journal entry"""
        if not self.validate_input(amount=amount, description=description):
            raise ValueError("Invalid input parameters")
        
        # Get accounts
        bank_account = self._get_account_by_code("1100")  # Bank Account
        sales_revenue_account = self._get_account_by_code("4000")  # Sales Revenue
        
        if not bank_account or not sales_revenue_account:
            raise ValueError("Required accounts not found")
        
        # Create journal lines
        lines = [
            {
                "account_id": bank_account.id,
                "account_name": bank_account.name,
                "description": f"Bank deposit for: {description}",
                "debit_amount": amount,
                "credit_amount": 0.0
            },
            {
                "account_id": sales_revenue_account.id,
                "account_name": sales_revenue_account.name,
                "description": f"Sales revenue from: {description}",
                "debit_amount": 0.0,
                "credit_amount": amount
            }
        ]
        
        return {
            "description": f"Bank Sales: {description}",
            "payment_method": "bank",
            "lines": lines,
            "total_debits": amount,
            "total_credits": amount
        }

class ExpensePaymentTemplate(TransactionTemplate):
    """Template for expense payment transactions"""
    
    def __init__(self, manager=None):
        super().__init__(
            template_id="expense_payment",
            name="Expense Payment",
            description="Record expense payments",
            manager=manager
        )
    
    def get_required_fields(self) -> List[str]:
        return ['amount', 'description', 'payment_method']
    
    def create_journal_entry(self, amount: float, description: str, payment_method: str = "cash", **kwargs) -> Dict:
        """Create expense payment journal entry"""
        if not self.validate_input(amount=amount, description=description, payment_method=payment_method):
            raise ValueError("Invalid input parameters")
        
        # Get accounts based on payment method
        if payment_method == "cash":
            payment_account = self._get_account_by_code("1000")  # Cash on Hand
        else:
            payment_account = self._get_account_by_code("1100")  # Bank Account
        
        expense_account = self._get_account_by_code("5100")  # Operating Expenses
        
        if not payment_account or not expense_account:
            raise ValueError("Required accounts not found")
        
        # Create journal lines
        lines = [
            {
                "account_id": expense_account.id,
                "account_name": expense_account.name,
                "description": f"Expense: {description}",
                "debit_amount": amount,
                "credit_amount": 0.0
            },
            {
                "account_id": payment_account.id,
                "account_name": payment_account.name,
                "description": f"Payment for: {description}",
                "debit_amount": 0.0,
                "credit_amount": amount
            }
        ]
        
        return {
            "description": f"Expense Payment: {description}",
            "payment_method": payment_method,
            "lines": lines,
            "total_debits": amount,
            "total_credits": amount
        }

class PurchaseTemplate(TransactionTemplate):
    """Template for purchase transactions"""
    
    def __init__(self, manager=None):
        super().__init__(
            template_id="purchase",
            name="Purchase",
            description="Record purchase transactions",
            manager=manager
        )
    
    def get_required_fields(self) -> List[str]:
        return ['amount', 'description', 'payment_method', 'purchase_type']
    
    def create_journal_entry(self, amount: float, description: str, payment_method: str = "bank", purchase_type: str = "inventory", **kwargs) -> Dict:
        """Create purchase journal entry"""
        if not self.validate_input(amount=amount, description=description, payment_method=payment_method, purchase_type=purchase_type):
            raise ValueError("Invalid input parameters")
        
        # Get accounts based on payment method
        if payment_method == "cash":
            payment_account = self._get_account_by_code("1000")  # Cash on Hand
        else:
            payment_account = self._get_account_by_code("1100")  # Bank Account
        
        # Get purchase account based on type
        if purchase_type == "inventory":
            purchase_account = self._get_account_by_code("1300")  # Inventory
        else:
            purchase_account = self._get_account_by_code("5100")  # Operating Expenses
        
        if not payment_account or not purchase_account:
            raise ValueError("Required accounts not found")
        
        # Create journal lines
        lines = [
            {
                "account_id": purchase_account.id,
                "account_name": purchase_account.name,
                "description": f"Purchase: {description}",
                "debit_amount": amount,
                "credit_amount": 0.0
            },
            {
                "account_id": payment_account.id,
                "account_name": payment_account.name,
                "description": f"Payment for: {description}",
                "debit_amount": 0.0,
                "credit_amount": amount
            }
        ]
        
        return {
            "description": f"Purchase: {description}",
            "payment_method": payment_method,
            "lines": lines,
            "total_debits": amount,
            "total_credits": amount
        }

class LoanReceiptTemplate(TransactionTemplate):
    """Template for loan receipt transactions"""
    
    def __init__(self, manager=None):
        super().__init__(
            template_id="loan_receipt",
            name="Loan Receipt",
            description="Record loan receipts",
            manager=manager
        )
    
    def create_journal_entry(self, amount: float, description: str, **kwargs) -> Dict:
        """Create loan receipt journal entry"""
        if not self.validate_input(amount=amount, description=description):
            raise ValueError("Invalid input parameters")
        
        # Get accounts
        bank_account = self._get_account_by_code("1100")  # Bank Account
        loan_payable_account = self._get_account_by_code("2000")  # Accounts Payable (we'll use this for loans)
        
        if not bank_account or not loan_payable_account:
            raise ValueError("Required accounts not found")
        
        # Create journal lines
        lines = [
            {
                "account_id": bank_account.id,
                "account_name": bank_account.name,
                "description": f"Loan received: {description}",
                "debit_amount": amount,
                "credit_amount": 0.0
            },
            {
                "account_id": loan_payable_account.id,
                "account_name": loan_payable_account.name,
                "description": f"Loan liability: {description}",
                "debit_amount": 0.0,
                "credit_amount": amount
            }
        ]
        
        return {
            "description": f"Loan Receipt: {description}",
            "payment_method": "bank",
            "lines": lines,
            "total_debits": amount,
            "total_credits": amount
        }

class SimpleTransactionTemplate(TransactionTemplate):
    """Template for simple business transactions that auto-balance"""
    
    def __init__(self, manager=None):
        super().__init__(
            template_id="simple_transaction",
            name="Simple Transaction",
            description="Auto-balance any business transaction",
            manager=manager
        )
    
    def create_journal_entry(self, **kwargs) -> Dict:
        """Create a simple journal entry with auto-balancing"""
        print(f"DEBUG: create_journal_entry called with kwargs: {kwargs}")
        
        # Extract required parameters
        amount = kwargs.get('amount')
        description = kwargs.get('description')
        account_id = kwargs.get('account_id')
        is_debit = kwargs.get('is_debit')
        
        print(f"DEBUG: Extracted parameters - amount={amount}, description={description}, account_id={account_id}, is_debit={is_debit}")
        
        if not self.validate_input(**kwargs):
            print("DEBUG: Validation failed")
            raise ValueError("Invalid input parameters")
        
        print("DEBUG: Validation passed")
        
        # Get the primary account
        primary_account = Account.query.get(account_id)
        if not primary_account:
            print(f"DEBUG: Primary account with ID {account_id} not found")
            raise ValueError("Primary account not found")
        
        print(f"DEBUG: Primary account found: {primary_account.name}")
        
        # Determine the balancing account based on account type
        balancing_account = self._get_balancing_account(primary_account, is_debit)
        
        if not balancing_account:
            raise ValueError("Could not determine balancing account")
        
        # Create journal lines
        if is_debit:
            lines = [
                {
                    "account_id": primary_account.id,
                    "account_name": primary_account.name,
                    "description": description,
                    "debit_amount": amount,
                    "credit_amount": 0.0
                },
                {
                    "account_id": balancing_account.id,
                    "account_name": balancing_account.name,
                    "description": f"Auto-balance for: {description}",
                    "debit_amount": 0.0,
                    "credit_amount": amount
                }
            ]
        else:
            lines = [
                {
                    "account_id": primary_account.id,
                    "account_name": primary_account.name,
                    "description": description,
                    "debit_amount": 0.0,
                    "credit_amount": amount
                },
                {
                    "account_id": balancing_account.id,
                    "account_name": balancing_account.name,
                    "description": f"Auto-balance for: {description}",
                    "debit_amount": amount,
                    "credit_amount": 0.0
                }
            ]
        
        return {
            "lines": lines,
            "total_debits": amount,
            "total_credits": amount,
            "description": description,
            "payment_method": kwargs.get('payment_method', 'bank')
        }
    
    def _get_balancing_account(self, primary_account: Account, is_debit: bool) -> Optional[Account]:
        """Get the appropriate balancing account based on the primary account type"""
        account_type = primary_account.type.lower()
        
        # Try to get cash account first (1000), then bank account (1100)
        cash_account = self._get_account_by_code("1000")
        bank_account = self._get_account_by_code("1100")
        
        # Log for debugging
        print(f"DEBUG: Looking for balancing account for {primary_account.name} (type: {account_type})")
        print(f"DEBUG: Cash account (1000): {cash_account.name if cash_account else 'Not found'}")
        print(f"DEBUG: Bank account (1100): {bank_account.name if bank_account else 'Not found'}")
        
        # Return cash account if available, otherwise bank account
        return cash_account or bank_account
    
    def get_required_fields(self) -> List[str]:
        return ['amount', 'description', 'account_id', 'is_debit']

class TransactionTemplateManager:
    """Manager class for transaction templates"""
    
    def __init__(self):
        self.templates = {
            "cash_sales": CashSalesTemplate(manager=self),
            "bank_sales": BankSalesTemplate(manager=self),
            "expense_payment": ExpensePaymentTemplate(manager=self),
            "purchase": PurchaseTemplate(manager=self),
            "loan_receipt": LoanReceiptTemplate(manager=self),
            "simple_transaction": SimpleTransactionTemplate(manager=self)
        }
    
    def get_template(self, template_id: str) -> Optional[TransactionTemplate]:
        """Get a transaction template by ID"""
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> Dict[str, Dict]:
        """Get all available templates"""
        return {
            template_id: {
                "id": template_id,
                "name": template.name,
                "description": template.description,
                "required_fields": template.get_required_fields()
            }
            for template_id, template in self.templates.items()
        }
    
    def create_transaction(self, template_id: str, user_id: int, **kwargs) -> Dict:
        """Create a transaction using a template"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")
        
        # Create journal entry data using template
        journal_data = template.create_journal_entry(**kwargs)
        
        # Create the actual journal entry in database
        entry_date = kwargs.get('date', datetime.now().date())
        if isinstance(entry_date, str):
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        
        reference = kwargs.get('reference', f"TXN-{template_id.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        status = kwargs.get('status', 'posted')
        
        journal_entry = JournalEntry(
            period=entry_date.strftime('%Y-%m'),
            doc_date=entry_date,
            reference=reference,
            description=journal_data["description"],
            status=status,
            payment_method=journal_data["payment_method"],
            total_debit=journal_data["total_debits"],
            total_credit=journal_data["total_credits"],
            user_id=user_id,
            created_by=user_id
        )
        
        db.session.add(journal_entry)
        db.session.flush()  # Get the ID
        
        # Create journal lines
        for line_data in journal_data["lines"]:
            journal_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=line_data["account_id"],
                description=line_data["description"],
                debit_amount=line_data["debit_amount"],
                credit_amount=line_data["credit_amount"]
            )
            db.session.add(journal_line)
        
        db.session.commit()
        
        return {
            "message": f"Transaction created successfully using {template.name} template",
            "entry_id": journal_entry.id,
            "reference": journal_entry.reference,
            "template_used": template_id,
            "total_debits": journal_data["total_debits"],
            "total_credits": journal_data["total_credits"]
        }
    
    def _get_account_by_code(self, code: str) -> Optional[Account]:
        """Helper method to get account by code"""
        return Account.query.filter_by(code=code).first()

# Global instance
transaction_manager = TransactionTemplateManager()
