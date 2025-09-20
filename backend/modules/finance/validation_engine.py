"""
Enhanced Journal Entry Validation Engine
Date: September 18, 2025
Purpose: Business rule validation layer beyond basic debit=credit checks
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import json
import logging

# Import database models
try:
    from app import db
    from modules.finance.advanced_models import ChartOfAccounts, PostingRule, JournalHeader, GeneralLedgerEntry
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

class JournalValidationEngine:
    """
    Enhanced validation engine for journal entries
    Implements business rules beyond basic mathematical checks
    """
    
    def __init__(self):
        self.validation_rules = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default business validation rules"""
        self.validation_rules = [
            self._validate_mathematical_balance,
            self._validate_account_existence,
            self._validate_account_types,
            self._validate_amounts_positive,
            self._validate_required_fields,
            self._validate_fiscal_period,
            self._validate_business_rules,
            self._validate_approval_requirements,
        ]
    
    def validate_journal_entry(self, journal_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a complete journal entry
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Run all validation rules
            for rule in self.validation_rules:
                try:
                    rule(journal_data)
                except ValidationError as e:
                    errors.append(f"{e.field}: {e.message}" if e.field else e.message)
                except Exception as e:
                    errors.append(f"Validation error: {str(e)}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Critical validation error: {e}")
            return False, [f"Critical validation error: {str(e)}"]
    
    def _validate_mathematical_balance(self, journal_data: Dict):
        """Ensure debits equal credits"""
        lines = journal_data.get('lines', [])
        if not lines:
            raise ValidationError("Journal entry must have at least one line", "lines", "EMPTY_LINES")
        
        total_debit = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        total_credit = sum(Decimal(str(line.get('credit', 0))) for line in lines)
        
        if total_debit != total_credit:
            raise ValidationError(
                f"Debits (${total_debit}) must equal credits (${total_credit}). Difference: ${abs(total_debit - total_credit)}",
                "balance",
                "UNBALANCED_ENTRY"
            )
    
    def _validate_account_existence(self, journal_data: Dict):
        """Ensure all referenced accounts exist in Chart of Accounts"""
        if not DB_AVAILABLE:
            return  # Skip if database not available
        
        lines = journal_data.get('lines', [])
        for i, line in enumerate(lines):
            account_name = line.get('account')
            if not account_name:
                raise ValidationError(f"Line {i+1}: Account name is required", f"lines[{i}].account", "MISSING_ACCOUNT")
            
            # Check if account exists
            account = ChartOfAccounts.query.filter_by(account_name=account_name, is_active=True).first()
            if not account:
                raise ValidationError(
                    f"Line {i+1}: Account '{account_name}' does not exist or is inactive",
                    f"lines[{i}].account",
                    "INVALID_ACCOUNT"
                )
    
    def _validate_account_types(self, journal_data: Dict):
        """Validate account type usage rules"""
        if not DB_AVAILABLE:
            return
        
        lines = journal_data.get('lines', [])
        for i, line in enumerate(lines):
            account_name = line.get('account')
            debit = Decimal(str(line.get('debit', 0)))
            credit = Decimal(str(line.get('credit', 0)))
            
            if not account_name:
                continue  # Will be caught by account_existence check
            
            account = ChartOfAccounts.query.filter_by(account_name=account_name).first()
            if not account:
                continue  # Will be caught by account_existence check
            
            # Business rules for account types
            account_type = account.account_type.lower()
            
            # Revenue accounts should typically be credited
            if account_type == 'revenue' and debit > 0 and credit == 0:
                logger.warning(f"Line {i+1}: Debiting revenue account '{account_name}' - unusual but allowed")
            
            # Cash/Bank accounts should have clear business justification
            if 'cash' in account_name.lower() or 'bank' in account_name.lower():
                if debit > 10000:  # Large cash debit
                    logger.warning(f"Line {i+1}: Large cash debit ${debit} - verify approval")
    
    def _validate_amounts_positive(self, journal_data: Dict):
        """Ensure all amounts are positive (no negative debits/credits)"""
        lines = journal_data.get('lines', [])
        for i, line in enumerate(lines):
            debit = line.get('debit', 0)
            credit = line.get('credit', 0)
            
            if debit < 0:
                raise ValidationError(
                    f"Line {i+1}: Debit amount cannot be negative (${debit})",
                    f"lines[{i}].debit",
                    "NEGATIVE_DEBIT"
                )
            
            if credit < 0:
                raise ValidationError(
                    f"Line {i+1}: Credit amount cannot be negative (${credit})",
                    f"lines[{i}].credit",
                    "NEGATIVE_CREDIT"
                )
            
            if debit == 0 and credit == 0:
                raise ValidationError(
                    f"Line {i+1}: Either debit or credit must be greater than zero",
                    f"lines[{i}]",
                    "ZERO_AMOUNT"
                )
            
            if debit > 0 and credit > 0:
                raise ValidationError(
                    f"Line {i+1}: Cannot have both debit and credit on the same line",
                    f"lines[{i}]",
                    "BOTH_DEBIT_CREDIT"
                )
    
    def _validate_required_fields(self, journal_data: Dict):
        """Validate required fields are present"""
        required_fields = ['date', 'description', 'lines']
        
        for field in required_fields:
            if field not in journal_data or not journal_data[field]:
                raise ValidationError(f"Field '{field}' is required", field, "REQUIRED_FIELD")
        
        # Validate date format
        entry_date = journal_data.get('date')
        if isinstance(entry_date, str):
            try:
                datetime.strptime(entry_date, '%Y-%m-%d')
            except ValueError:
                raise ValidationError("Date must be in YYYY-MM-DD format", "date", "INVALID_DATE_FORMAT")
        
        # Validate description length
        description = journal_data.get('description', '')
        if len(description) > 500:
            raise ValidationError("Description cannot exceed 500 characters", "description", "DESCRIPTION_TOO_LONG")
    
    def _validate_fiscal_period(self, journal_data: Dict):
        """Validate fiscal period is open and valid"""
        entry_date = journal_data.get('date')
        if not entry_date:
            return  # Will be caught by required_fields check
        
        # Convert to date object if string
        if isinstance(entry_date, str):
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        
        # Check if posting to future periods (business rule)
        today = date.today()
        if entry_date > today:
            # Allow future dating within 7 days
            days_ahead = (entry_date - today).days
            if days_ahead > 7:
                raise ValidationError(
                    f"Cannot post entries more than 7 days in the future (entry date: {entry_date})",
                    "date",
                    "FUTURE_DATE_LIMIT"
                )
        
        # Check if posting to very old periods (business rule)
        days_behind = (today - entry_date).days
        if days_behind > 365:
            logger.warning(f"Posting to old period: {entry_date} ({days_behind} days ago)")
    
    def _validate_business_rules(self, journal_data: Dict):
        """Custom business rule validations"""
        lines = journal_data.get('lines', [])
        total_amount = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        
        # Large transaction approval rule
        if total_amount > 10000:
            source_module = journal_data.get('source_module', '')
            if source_module not in ['Finance']:  # Auto-generated entries
                logger.warning(f"Large transaction ${total_amount} from {source_module} - may require approval")
        
        # Specific account rules
        for i, line in enumerate(lines):
            account_name = line.get('account', '').lower()
            amount = max(Decimal(str(line.get('debit', 0))), Decimal(str(line.get('credit', 0))))
            
            # Bank account rules
            if 'bank' in account_name and amount > 5000:
                logger.warning(f"Line {i+1}: Large bank transaction ${amount} - verify authorization")
            
            # Petty cash rules
            if 'petty cash' in account_name and amount > 500:
                raise ValidationError(
                    f"Line {i+1}: Petty cash transactions cannot exceed $500 (attempted: ${amount})",
                    f"lines[{i}]",
                    "PETTY_CASH_LIMIT"
                )
    
    def _validate_approval_requirements(self, journal_data: Dict):
        """Check if entry requires approval based on amount or type"""
        lines = journal_data.get('lines', [])
        total_amount = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        
        # Set approval thresholds
        approval_required = False
        approval_reason = []
        
        if total_amount > 5000:
            approval_required = True
            approval_reason.append(f"Amount exceeds ${5000} threshold")
        
        # Check for sensitive accounts
        sensitive_accounts = ['bank account', 'cash', 'accounts payable', 'loan']
        for line in lines:
            account_name = line.get('account', '').lower()
            if any(sensitive in account_name for sensitive in sensitive_accounts):
                amount = max(Decimal(str(line.get('debit', 0))), Decimal(str(line.get('credit', 0))))
                if amount > 1000:
                    approval_required = True
                    approval_reason.append(f"Sensitive account '{line.get('account')}' with amount ${amount}")
        
        # For now, just log approval requirements (can be enhanced with workflow)
        if approval_required:
            logger.info(f"Journal entry requires approval: {'; '.join(approval_reason)}")

class PostingRuleValidator:
    """
    Validates that journal entries follow configured posting rules
    """
    
    def __init__(self):
        pass
    
    def validate_against_posting_rules(self, event_type: str, journal_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate journal entry against configured posting rules for the event type
        """
        if not DB_AVAILABLE:
            return True, []  # Skip validation if database not available
        
        errors = []
        
        try:
            # Get active posting rules for this event type
            rules = PostingRule.query.filter_by(
                event_type=event_type,
                is_active=True
            ).filter(
                db.or_(
                    PostingRule.valid_to.is_(None),
                    PostingRule.valid_to >= date.today()
                )
            ).order_by(PostingRule.priority.asc()).all()
            
            if not rules:
                logger.warning(f"No posting rules found for event type: {event_type}")
                return True, []  # Allow if no rules configured
            
            # Validate against the highest priority rule
            rule = rules[0]
            lines = journal_data.get('lines', [])
            
            if len(lines) != 2:
                errors.append(f"Expected 2 lines for {event_type}, got {len(lines)}")
                return False, errors
            
            # Find debit and credit lines
            debit_line = next((line for line in lines if line.get('debit', 0) > 0), None)
            credit_line = next((line for line in lines if line.get('credit', 0) > 0), None)
            
            if not debit_line or not credit_line:
                errors.append("Must have exactly one debit line and one credit line")
                return False, errors
            
            # Validate account names match rule
            if debit_line.get('account') != rule.debit_account_name:
                errors.append(f"Expected debit to '{rule.debit_account_name}', got '{debit_line.get('account')}'")
            
            if credit_line.get('account') != rule.credit_account_name:
                errors.append(f"Expected credit to '{rule.credit_account_name}', got '{credit_line.get('account')}'")
            
            # Validate conditions if specified
            if rule.conditions:
                try:
                    conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
                    # Add condition validation logic here if needed
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON conditions in posting rule {rule.id}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Error validating posting rules: {e}")
            return False, [f"Posting rule validation error: {str(e)}"]

# Convenience function for external use
def validate_journal_entry(journal_data: Dict, event_type: str = None) -> Tuple[bool, List[str]]:
    """
    Main validation function - validates both business rules and posting rules
    """
    all_errors = []
    
    # Business rule validation
    validator = JournalValidationEngine()
    is_valid, errors = validator.validate_journal_entry(journal_data)
    all_errors.extend(errors)
    
    # Posting rule validation (if event type provided)
    if event_type:
        rule_validator = PostingRuleValidator()
        is_rule_valid, rule_errors = rule_validator.validate_against_posting_rules(event_type, journal_data)
        all_errors.extend(rule_errors)
    
    return len(all_errors) == 0, all_errors

