"""
Multi-Currency Journal Entry Service
===================================

This service handles multi-currency operations for journal entries:
- Currency conversion
- Exchange rate management
- Functional amount calculation
- Multi-currency validation
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from app import db
from modules.finance.models import JournalEntry, JournalLine
# Note: Using existing currency system without importing conflicting models

class MultiCurrencyJournalService:
    """Service for multi-currency journal entry operations"""
    
    def __init__(self):
        self.base_currency = self._get_base_currency()
    
    def _get_base_currency(self) -> str:
        """Get the base currency from settings"""
        # For now, return USD as base currency
        # This can be enhanced later to read from settings
        return 'USD'
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, rate_date: date = None) -> float:
        """Get exchange rate between currencies"""
        if from_currency == to_currency:
            return 1.0
        
        # For now, return sample exchange rates
        # This can be enhanced later to use the existing currency system
        sample_rates = {
            'USD': {'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0, 'CAD': 1.25, 'AUD': 1.35},
            'EUR': {'USD': 1.18, 'GBP': 0.86, 'JPY': 129.0, 'CAD': 1.47, 'AUD': 1.59},
            'GBP': {'USD': 1.37, 'EUR': 1.16, 'JPY': 150.0, 'CAD': 1.71, 'AUD': 1.85},
            'JPY': {'USD': 0.0091, 'EUR': 0.0077, 'GBP': 0.0067, 'CAD': 0.011, 'AUD': 0.012},
            'CAD': {'USD': 0.80, 'EUR': 0.68, 'GBP': 0.58, 'JPY': 88.0, 'AUD': 1.08},
            'AUD': {'USD': 0.74, 'EUR': 0.63, 'GBP': 0.54, 'JPY': 81.0, 'CAD': 0.93}
        }
        
        try:
            return sample_rates.get(from_currency, {}).get(to_currency, 1.0)
        except:
            return 1.0
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str, rate_date: date = None) -> Dict:
        """Convert amount from one currency to another"""
        try:
            if from_currency == to_currency:
                return {
                    'success': True,
                    'original_amount': amount,
                    'converted_amount': amount,
                    'exchange_rate': 1.0,
                    'from_currency': from_currency,
                    'to_currency': to_currency
                }
            
            exchange_rate = self.get_exchange_rate(from_currency, to_currency, rate_date)
            converted_amount = amount * exchange_rate
            
            return {
                'success': True,
                'original_amount': amount,
                'converted_amount': converted_amount,
                'exchange_rate': exchange_rate,
                'from_currency': from_currency,
                'to_currency': to_currency
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_amount': amount,
                'converted_amount': amount,
                'exchange_rate': 1.0,
                'from_currency': from_currency,
                'to_currency': to_currency
            }
    
    def process_journal_entry_currency(self, journal_entry: JournalEntry, lines_data: List[Dict]) -> Dict:
        """Process multi-currency for a journal entry"""
        try:
            entry_currency = journal_entry.currency or self.base_currency
            entry_date = journal_entry.doc_date
            
            processed_lines = []
            total_functional_debits = 0.0
            total_functional_credits = 0.0
            
            for line_data in lines_data:
                # Get line currency (default to entry currency)
                line_currency = line_data.get('currency', entry_currency)
                debit_amount = float(line_data.get('debit_amount', 0))
                credit_amount = float(line_data.get('credit_amount', 0))
                
                # Convert to functional currency (base currency)
                if line_currency != self.base_currency:
                    # Convert debit amount
                    if debit_amount > 0:
                        debit_conversion = self.convert_amount(debit_amount, line_currency, self.base_currency, entry_date)
                        functional_debit = debit_conversion['converted_amount']
                        exchange_rate = debit_conversion['exchange_rate']
                    else:
                        functional_debit = 0.0
                        exchange_rate = 1.0
                    
                    # Convert credit amount
                    if credit_amount > 0:
                        credit_conversion = self.convert_amount(credit_amount, line_currency, self.base_currency, entry_date)
                        functional_credit = credit_conversion['converted_amount']
                        exchange_rate = credit_conversion['exchange_rate']
                    else:
                        functional_credit = 0.0
                        exchange_rate = 1.0
                else:
                    functional_debit = debit_amount
                    functional_credit = credit_amount
                    exchange_rate = 1.0
                
                # Update line data with functional amounts
                line_data.update({
                    'currency': line_currency,
                    'exchange_rate': exchange_rate,
                    'functional_debit_amount': functional_debit,
                    'functional_credit_amount': functional_credit
                })
                
                processed_lines.append(line_data)
                total_functional_debits += functional_debit
                total_functional_credits += functional_credit
            
            return {
                'success': True,
                'processed_lines': processed_lines,
                'total_functional_debits': total_functional_debits,
                'total_functional_credits': total_functional_credits,
                'is_balanced': abs(total_functional_debits - total_functional_credits) < 0.01,
                'base_currency': self.base_currency,
                'entry_currency': entry_currency
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed_lines': lines_data,
                'total_functional_debits': 0.0,
                'total_functional_credits': 0.0,
                'is_balanced': False
            }
    
    def validate_multi_currency_entry(self, lines_data: List[Dict], entry_currency: str = None) -> Dict:
        """Validate multi-currency journal entry"""
        try:
            if not entry_currency:
                entry_currency = self.base_currency
            
            # Check if all lines are in the same currency
            currencies_used = set()
            for line in lines_data:
                line_currency = line.get('currency', entry_currency)
                currencies_used.add(line_currency)
            
            # If multiple currencies, validate conversion
            if len(currencies_used) > 1:
                # Create a mock journal entry for processing
                mock_entry = JournalEntry(
                    currency=entry_currency,
                    doc_date=date.today()
                )
                
                result = self.process_journal_entry_currency(mock_entry, lines_data)
                
                if not result['success']:
                    return {
                        'is_valid': False,
                        'error': f"Currency conversion failed: {result['error']}"
                    }
                
                if not result['is_balanced']:
                    return {
                        'is_valid': False,
                        'error': f"Entry is not balanced in base currency. Debits: {result['total_functional_debits']:.2f}, Credits: {result['total_functional_credits']:.2f}"
                    }
            
            return {
                'is_valid': True,
                'currencies_used': list(currencies_used),
                'base_currency': self.base_currency,
                'entry_currency': entry_currency
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e)
            }
    
    def get_currency_summary(self, journal_entry_id: int) -> Dict:
        """Get currency summary for a journal entry"""
        try:
            entry = JournalEntry.query.get(journal_entry_id)
            if not entry:
                return {'error': 'Journal entry not found'}
            
            lines = JournalLine.query.filter_by(journal_entry_id=journal_entry_id).all()
            
            currency_summary = {}
            total_functional_debits = 0.0
            total_functional_credits = 0.0
            
            for line in lines:
                currency = line.currency or entry.currency or self.base_currency
                
                if currency not in currency_summary:
                    currency_summary[currency] = {
                        'debits': 0.0,
                        'credits': 0.0,
                        'functional_debits': 0.0,
                        'functional_credits': 0.0,
                        'exchange_rate': line.exchange_rate or 1.0
                    }
                
                currency_summary[currency]['debits'] += line.debit_amount
                currency_summary[currency]['credits'] += line.credit_amount
                currency_summary[currency]['functional_debits'] += line.functional_debit_amount
                currency_summary[currency]['functional_credits'] += line.functional_credit_amount
                
                total_functional_debits += line.functional_debit_amount
                total_functional_credits += line.functional_credit_amount
            
            return {
                'journal_entry_id': journal_entry_id,
                'entry_currency': entry.currency or self.base_currency,
                'base_currency': self.base_currency,
                'currency_summary': currency_summary,
                'total_functional_debits': total_functional_debits,
                'total_functional_credits': total_functional_credits,
                'is_balanced': abs(total_functional_debits - total_functional_credits) < 0.01
            }
            
        except Exception as e:
            return {'error': str(e)}

# Global service instance
multi_currency_service = MultiCurrencyJournalService()
