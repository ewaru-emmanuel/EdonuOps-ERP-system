"""
Payment Journal Service - Double-Entry Integration
Purpose: Create proper journal entries for all payment transactions
Ensures payment tracking follows double-entry accounting principles
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import json
import logging

try:
    from app import db
    from modules.finance.advanced_models import (
        ChartOfAccounts, GeneralLedgerEntry, JournalHeader, AccountsReceivable, AccountsPayable
    )
    from modules.finance.payment_models import PaymentMethod, BankAccount, PaymentTransaction, PartialPayment
    from modules.finance.validation_engine import validate_journal_entry
    from modules.integration.auto_journal import AutoJournalEngine
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class PaymentJournalService:
    """
    Service for creating double-entry journal entries from payment transactions
    Ensures all payment tracking follows proper accounting principles
    """
    
    def __init__(self):
        self.auto_journal = AutoJournalEngine() if DB_AVAILABLE else None
    
    def create_ar_payment_journal_entry(self, ar_payment_data: Dict) -> Dict:
        """
        Create journal entry for Accounts Receivable payment
        
        Standard AR Payment Entry:
        Dr. Cash/Bank Account           $XXX
        Dr. Processing Fee Expense      $XX  (if applicable)
        Cr. Accounts Receivable              $XXX
        """
        try:
            if not DB_AVAILABLE:
                return {'success': False, 'error': 'Database not available'}
            
            # Extract payment data
            invoice_id = ar_payment_data.get('invoice_id')
            payment_amount = Decimal(str(ar_payment_data.get('payment_amount', 0)))
            payment_method_id = ar_payment_data.get('payment_method_id')
            bank_account_id = ar_payment_data.get('bank_account_id')
            processing_fee = Decimal(str(ar_payment_data.get('processing_fee', 0)))
            payment_reference = ar_payment_data.get('payment_reference', '')
            payment_date = ar_payment_data.get('payment_date', date.today())
            
            # Get related records
            invoice = AccountsReceivable.query.get(invoice_id)
            payment_method = PaymentMethod.query.get(payment_method_id)
            bank_account = BankAccount.query.get(bank_account_id) if bank_account_id else None
            
            if not invoice:
                return {'success': False, 'error': 'Invoice not found'}
            if not payment_method:
                return {'success': False, 'error': 'Payment method not found'}
            
            # Get GL accounts
            ar_account = ChartOfAccounts.query.filter_by(account_name='Accounts Receivable').first()
            bank_gl_account = bank_account.gl_account if bank_account and bank_account.gl_account else None
            cash_account = ChartOfAccounts.query.filter_by(account_name='Cash').first()
            processing_fee_account = ChartOfAccounts.query.filter_by(account_name='Processing Fee Expense').first()
            
            # Use default accounts if specific ones not found
            if not bank_gl_account:
                bank_gl_account = cash_account
            
            if not ar_account:
                return {'success': False, 'error': 'Accounts Receivable GL account not found'}
            if not bank_gl_account:
                return {'success': False, 'error': 'Bank/Cash GL account not found'}
            
            # Calculate net amount received
            net_amount = payment_amount - processing_fee
            
            # Create journal entry lines
            journal_lines = []
            
            # Dr. Bank/Cash Account
            journal_lines.append({
                'account': bank_gl_account.account_name,
                'account_id': bank_gl_account.id,
                'debit': float(net_amount),
                'credit': 0,
                'description': f'Payment received from {invoice.customer_name} - {payment_method.name}'
            })
            
            # Dr. Processing Fee Expense (if applicable)
            if processing_fee > 0 and processing_fee_account:
                journal_lines.append({
                    'account': processing_fee_account.account_name,
                    'account_id': processing_fee_account.id,
                    'debit': float(processing_fee),
                    'credit': 0,
                    'description': f'Processing fee for {payment_method.name} payment'
                })
            
            # Cr. Accounts Receivable
            journal_lines.append({
                'account': ar_account.account_name,
                'account_id': ar_account.id,
                'debit': 0,
                'credit': float(payment_amount),
                'description': f'Payment received for Invoice {invoice.invoice_number}'
            })
            
            # Create journal entry
            journal_entry = {
                'entry_date': payment_date.isoformat() if isinstance(payment_date, date) else payment_date,
                'description': f'AR Payment - {invoice.customer_name} - {payment_method.name}',
                'reference': payment_reference,
                'lines': journal_lines,
                'source_module': 'accounts_receivable',
                'source_transaction_id': invoice_id,
                'payment_method_id': payment_method_id,
                'bank_account_id': bank_account_id
            }
            
            # Validate and create journal entry
            if self.auto_journal:
                result = self.auto_journal.create_journal_entry(
                    journal_entry, 
                    event_type='ar_payment_received'
                )
                
                if result.get('success'):
                    return {
                        'success': True,
                        'journal_entry_id': result.get('journal_entry_id'),
                        'message': 'AR payment journal entry created successfully',
                        'details': {
                            'net_amount': float(net_amount),
                            'processing_fee': float(processing_fee),
                            'total_debits': float(net_amount + processing_fee),
                            'total_credits': float(payment_amount)
                        }
                    }
                else:
                    return {'success': False, 'error': result.get('error', 'Failed to create journal entry')}
            else:
                return {'success': False, 'error': 'Auto journal engine not available'}
                
        except Exception as e:
            logger.error(f"Error creating AR payment journal entry: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_ap_payment_journal_entry(self, ap_payment_data: Dict) -> Dict:
        """
        Create journal entry for Accounts Payable payment
        
        Standard AP Payment Entry:
        Dr. Accounts Payable            $XXX
        Cr. Cash/Bank Account                $XXX
        Dr. Processing Fee Expense      $XX  (if applicable)
        """
        try:
            if not DB_AVAILABLE:
                return {'success': False, 'error': 'Database not available'}
            
            # Extract payment data
            invoice_id = ap_payment_data.get('invoice_id')
            payment_amount = Decimal(str(ap_payment_data.get('payment_amount', 0)))
            payment_method_id = ap_payment_data.get('payment_method_id')
            bank_account_id = ap_payment_data.get('bank_account_id')
            processing_fee = Decimal(str(ap_payment_data.get('processing_fee', 0)))
            payment_reference = ap_payment_data.get('payment_reference', '')
            payment_date = ap_payment_data.get('payment_date', date.today())
            
            # Get related records
            invoice = AccountsPayable.query.get(invoice_id)
            payment_method = PaymentMethod.query.get(payment_method_id)
            bank_account = BankAccount.query.get(bank_account_id) if bank_account_id else None
            
            if not invoice:
                return {'success': False, 'error': 'Invoice not found'}
            if not payment_method:
                return {'success': False, 'error': 'Payment method not found'}
            
            # Get GL accounts
            ap_account = ChartOfAccounts.query.filter_by(account_name='Accounts Payable').first()
            bank_gl_account = bank_account.gl_account if bank_account and bank_account.gl_account else None
            cash_account = ChartOfAccounts.query.filter_by(account_name='Cash').first()
            processing_fee_account = ChartOfAccounts.query.filter_by(account_name='Processing Fee Expense').first()
            
            # Use default accounts if specific ones not found
            if not bank_gl_account:
                bank_gl_account = cash_account
            
            if not ap_account:
                return {'success': False, 'error': 'Accounts Payable GL account not found'}
            if not bank_gl_account:
                return {'success': False, 'error': 'Bank/Cash GL account not found'}
            
            # Calculate total payment (amount + fees for outgoing payments)
            total_payment = payment_amount + processing_fee
            
            # Create journal entry lines
            journal_lines = []
            
            # Dr. Accounts Payable
            journal_lines.append({
                'account': ap_account.account_name,
                'account_id': ap_account.id,
                'debit': float(payment_amount),
                'credit': 0,
                'description': f'Payment to {invoice.vendor_name} - Invoice {invoice.invoice_number}'
            })
            
            # Dr. Processing Fee Expense (if applicable)
            if processing_fee > 0 and processing_fee_account:
                journal_lines.append({
                    'account': processing_fee_account.account_name,
                    'account_id': processing_fee_account.id,
                    'debit': float(processing_fee),
                    'credit': 0,
                    'description': f'Processing fee for {payment_method.name} payment'
                })
            
            # Cr. Bank/Cash Account
            journal_lines.append({
                'account': bank_gl_account.account_name,
                'account_id': bank_gl_account.id,
                'debit': 0,
                'credit': float(total_payment),
                'description': f'Payment via {payment_method.name} from {bank_account.account_name if bank_account else "Cash"}'
            })
            
            # Create journal entry
            journal_entry = {
                'entry_date': payment_date.isoformat() if isinstance(payment_date, date) else payment_date,
                'description': f'AP Payment - {invoice.vendor_name} - {payment_method.name}',
                'reference': payment_reference,
                'lines': journal_lines,
                'source_module': 'accounts_payable',
                'source_transaction_id': invoice_id,
                'payment_method_id': payment_method_id,
                'bank_account_id': bank_account_id
            }
            
            # Validate and create journal entry
            if self.auto_journal:
                result = self.auto_journal.create_journal_entry(
                    journal_entry, 
                    event_type='ap_payment_made'
                )
                
                if result.get('success'):
                    return {
                        'success': True,
                        'journal_entry_id': result.get('journal_entry_id'),
                        'message': 'AP payment journal entry created successfully',
                        'details': {
                            'payment_amount': float(payment_amount),
                            'processing_fee': float(processing_fee),
                            'total_debits': float(payment_amount + processing_fee),
                            'total_credits': float(total_payment)
                        }
                    }
                else:
                    return {'success': False, 'error': result.get('error', 'Failed to create journal entry')}
            else:
                return {'success': False, 'error': 'Auto journal engine not available'}
                
        except Exception as e:
            logger.error(f"Error creating AP payment journal entry: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_fx_gain_loss_entry(self, fx_data: Dict) -> Dict:
        """
        Create journal entry for foreign exchange gains/losses
        
        FX Gain Entry:
        Dr. Cash/Bank Account           $XXX
        Cr. FX Gain                          $XX
        
        FX Loss Entry:
        Dr. FX Loss                     $XX
        Dr. Cash/Bank Account           $XXX
        """
        try:
            if not DB_AVAILABLE:
                return {'success': False, 'error': 'Database not available'}
            
            # Extract FX data
            original_amount = Decimal(str(fx_data.get('original_amount', 0)))
            converted_amount = Decimal(str(fx_data.get('converted_amount', 0)))
            from_currency = fx_data.get('from_currency', 'USD')
            to_currency = fx_data.get('to_currency', 'USD')
            exchange_rate = Decimal(str(fx_data.get('exchange_rate', 1.0)))
            transaction_date = fx_data.get('transaction_date', date.today())
            bank_account_id = fx_data.get('bank_account_id')
            
            # Calculate gain/loss
            fx_difference = converted_amount - original_amount
            
            if abs(fx_difference) < Decimal('0.01'):  # Less than 1 cent difference
                return {'success': True, 'message': 'No significant FX difference, no entry needed'}
            
            # Get GL accounts
            bank_account = BankAccount.query.get(bank_account_id) if bank_account_id else None
            bank_gl_account = bank_account.gl_account if bank_account and bank_account.gl_account else None
            cash_account = ChartOfAccounts.query.filter_by(account_name='Cash').first()
            
            fx_gain_account = ChartOfAccounts.query.filter_by(account_name='Foreign Exchange Gain').first()
            fx_loss_account = ChartOfAccounts.query.filter_by(account_name='Foreign Exchange Loss').first()
            
            if not bank_gl_account:
                bank_gl_account = cash_account
            
            if not bank_gl_account:
                return {'success': False, 'error': 'Bank/Cash GL account not found'}
            
            # Create journal entry lines
            journal_lines = []
            
            if fx_difference > 0:  # FX Gain
                if not fx_gain_account:
                    return {'success': False, 'error': 'FX Gain account not found in Chart of Accounts'}
                
                journal_lines = [
                    {
                        'account': bank_gl_account.account_name,
                        'account_id': bank_gl_account.id,
                        'debit': float(fx_difference),
                        'credit': 0,
                        'description': f'FX gain on {from_currency} to {to_currency} conversion'
                    },
                    {
                        'account': fx_gain_account.account_name,
                        'account_id': fx_gain_account.id,
                        'debit': 0,
                        'credit': float(fx_difference),
                        'description': f'FX gain: {from_currency}/{to_currency} @ {exchange_rate}'
                    }
                ]
            else:  # FX Loss
                if not fx_loss_account:
                    return {'success': False, 'error': 'FX Loss account not found in Chart of Accounts'}
                
                fx_loss_amount = abs(fx_difference)
                journal_lines = [
                    {
                        'account': fx_loss_account.account_name,
                        'account_id': fx_loss_account.id,
                        'debit': float(fx_loss_amount),
                        'credit': 0,
                        'description': f'FX loss on {from_currency} to {to_currency} conversion'
                    },
                    {
                        'account': bank_gl_account.account_name,
                        'account_id': bank_gl_account.id,
                        'debit': 0,
                        'credit': float(fx_loss_amount),
                        'description': f'FX loss: {from_currency}/{to_currency} @ {exchange_rate}'
                    }
                ]
            
            # Create journal entry
            journal_entry = {
                'entry_date': transaction_date.isoformat() if isinstance(transaction_date, date) else transaction_date,
                'description': f'FX {"Gain" if fx_difference > 0 else "Loss"} - {from_currency}/{to_currency}',
                'reference': f'FX-{from_currency}-{to_currency}-{transaction_date}',
                'lines': journal_lines,
                'source_module': 'multi_currency',
                'source_transaction_id': fx_data.get('transaction_id'),
                'fx_rate': float(exchange_rate),
                'fx_amount': float(fx_difference)
            }
            
            # Validate and create journal entry
            if self.auto_journal:
                result = self.auto_journal.create_journal_entry(
                    journal_entry, 
                    event_type='fx_gain_loss'
                )
                
                if result.get('success'):
                    return {
                        'success': True,
                        'journal_entry_id': result.get('journal_entry_id'),
                        'message': f'FX {"gain" if fx_difference > 0 else "loss"} journal entry created',
                        'fx_amount': float(fx_difference),
                        'fx_type': 'gain' if fx_difference > 0 else 'loss'
                    }
                else:
                    return {'success': False, 'error': result.get('error', 'Failed to create FX journal entry')}
            else:
                return {'success': False, 'error': 'Auto journal engine not available'}
                
        except Exception as e:
            logger.error(f"Error creating FX journal entry: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_partial_payment_journal_entry(self, partial_payment_id: int) -> Dict:
        """
        Create journal entry for partial payment
        Uses the same logic as full payments but for partial amounts
        """
        try:
            if not DB_AVAILABLE:
                return {'success': False, 'error': 'Database not available'}
            
            partial_payment = PartialPayment.query.get(partial_payment_id)
            if not partial_payment:
                return {'success': False, 'error': 'Partial payment not found'}
            
            # Convert partial payment to standard payment data format
            payment_data = {
                'invoice_id': partial_payment.invoice_id,
                'payment_amount': partial_payment.amount,
                'payment_method_id': partial_payment.payment_method_id,
                'bank_account_id': partial_payment.bank_account_id,
                'processing_fee': partial_payment.processing_fee,
                'payment_reference': partial_payment.payment_reference,
                'payment_date': partial_payment.payment_date
            }
            
            # Create appropriate journal entry based on invoice type
            if partial_payment.invoice_type == 'AR':
                return self.create_ar_payment_journal_entry(payment_data)
            elif partial_payment.invoice_type == 'AP':
                return self.create_ap_payment_journal_entry(payment_data)
            else:
                return {'success': False, 'error': 'Invalid invoice type for partial payment'}
                
        except Exception as e:
            logger.error(f"Error creating partial payment journal entry: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_payment_journal_entry(self, journal_entry: Dict) -> Tuple[bool, List[str]]:
        """
        Validate payment journal entry for double-entry compliance
        """
        try:
            if not DB_AVAILABLE:
                return False, ['Database not available for validation']
            
            # Use the existing validation engine
            return validate_journal_entry(journal_entry, 'payment_transaction')
            
        except Exception as e:
            logger.error(f"Error validating payment journal entry: {e}")
            return False, [str(e)]
    
    def get_payment_journal_entries(self, payment_id: int, payment_type: str) -> List[Dict]:
        """
        Get all journal entries related to a specific payment
        """
        try:
            if not DB_AVAILABLE:
                return []
            
            # Find journal entries by source transaction
            entries = GeneralLedgerEntry.query.filter_by(
                source_module=f'accounts_{payment_type.lower()}',
                source_transaction_id=payment_id
            ).all()
            
            return [{
                'id': entry.id,
                'account_name': entry.account.account_name,
                'debit_amount': entry.debit_amount,
                'credit_amount': entry.credit_amount,
                'description': entry.description,
                'entry_date': entry.entry_date.isoformat(),
                'reference': entry.reference
            } for entry in entries]
            
        except Exception as e:
            logger.error(f"Error getting payment journal entries: {e}")
            return []
    
    def reverse_payment_journal_entry(self, payment_id: int, payment_type: str, reversal_reason: str) -> Dict:
        """
        Create reversing journal entries for payment cancellation
        """
        try:
            if not DB_AVAILABLE:
                return {'success': False, 'error': 'Database not available'}
            
            # Get original journal entries
            original_entries = self.get_payment_journal_entries(payment_id, payment_type)
            
            if not original_entries:
                return {'success': False, 'error': 'No journal entries found for this payment'}
            
            # Create reversing entries
            reversal_lines = []
            for entry in original_entries:
                reversal_lines.append({
                    'account': entry['account_name'],
                    'account_id': entry.get('account_id'),
                    'debit': entry['credit_amount'],  # Flip debit/credit
                    'credit': entry['debit_amount'],  # Flip debit/credit
                    'description': f"REVERSAL: {entry['description']}"
                })
            
            # Create reversal journal entry
            reversal_entry = {
                'entry_date': date.today().isoformat(),
                'description': f'REVERSAL - {payment_type.upper()} Payment #{payment_id} - {reversal_reason}',
                'reference': f'REV-{payment_type.upper()}-{payment_id}',
                'lines': reversal_lines,
                'source_module': f'accounts_{payment_type.lower()}_reversal',
                'source_transaction_id': payment_id,
                'reversal_reason': reversal_reason
            }
            
            # Create reversal journal entry
            if self.auto_journal:
                result = self.auto_journal.create_journal_entry(
                    reversal_entry, 
                    event_type='payment_reversal'
                )
                
                if result.get('success'):
                    return {
                        'success': True,
                        'reversal_journal_entry_id': result.get('journal_entry_id'),
                        'message': 'Payment reversal journal entry created successfully'
                    }
                else:
                    return {'success': False, 'error': result.get('error', 'Failed to create reversal entry')}
            else:
                return {'success': False, 'error': 'Auto journal engine not available'}
                
        except Exception as e:
            logger.error(f"Error creating payment reversal journal entry: {e}")
            return {'success': False, 'error': str(e)}


# Global service instance
payment_journal_service = PaymentJournalService()


# Convenience functions for easy integration
def create_ar_payment_journal(ar_payment_data: Dict) -> Dict:
    """Convenience function for AR payment journal creation"""
    return payment_journal_service.create_ar_payment_journal_entry(ar_payment_data)


def create_ap_payment_journal(ap_payment_data: Dict) -> Dict:
    """Convenience function for AP payment journal creation"""
    return payment_journal_service.create_ap_payment_journal_entry(ap_payment_data)


def create_fx_journal(fx_data: Dict) -> Dict:
    """Convenience function for FX gain/loss journal creation"""
    return payment_journal_service.create_fx_gain_loss_entry(fx_data)


def validate_payment_journal(journal_entry: Dict) -> Tuple[bool, List[str]]:
    """Convenience function for payment journal validation"""
    return payment_journal_service.validate_payment_journal_entry(journal_entry)

