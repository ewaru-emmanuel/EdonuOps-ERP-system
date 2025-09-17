from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal
import json
import logging

# Import database models
try:
    from app import db
    from modules.finance.advanced_models import GeneralLedgerEntry, JournalHeader, ChartOfAccounts
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class AutoJournalEngine:
    """Automated Journal Entry Engine - The heartbeat of Finance-Inventory integration"""
    
    def __init__(self):
        self.journal_entries = []
        self.transaction_counter = 0
    
    def _persist_to_database(self, journal_entry: Dict) -> bool:
        """
        Persist journal entry to the actual GeneralLedgerEntry database table
        """
        if not DB_AVAILABLE:
            logger.warning("Database models not available, journal entry stored in memory only")
            return False
        
        try:
            # Create or get accounts
            account_cache = {}
            
            for line in journal_entry['lines']:
                account_name = line['account']
                
                # Check if account exists in cache
                if account_name not in account_cache:
                    account = ChartOfAccounts.query.filter_by(account_name=account_name).first()
                    if not account:
                        # Create account if it doesn't exist
                        account_type = self._determine_account_type(account_name)
                        account = ChartOfAccounts(
                            account_name=account_name,
                            account_code=self._generate_account_code(account_name),
                            account_type=account_type,
                            is_active=True,
                            description=f"Auto-created for {account_name}"
                        )
                        db.session.add(account)
                        db.session.flush()  # Get the ID
                    account_cache[account_name] = account
                
                # Create GL entry
                gl_entry = GeneralLedgerEntry(
                    account_id=account_cache[account_name].id,
                    entry_date=journal_entry['date'] if isinstance(journal_entry['date'], datetime) else datetime.now(),
                    description=line['description'],
                    debit_amount=float(line['debit']),
                    credit_amount=float(line['credit']),
                    reference=journal_entry['reference'],
                    transaction_type=journal_entry.get('metadata', {}).get('transaction_type', 'auto_journal'),
                    status='posted',
                    created_by='auto_journal_engine'
                )
                db.session.add(gl_entry)
            
            db.session.commit()
            logger.info(f"Journal entry {journal_entry['id']} persisted to database successfully")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to persist journal entry {journal_entry['id']} to database: {str(e)}")
            return False
    
    def _determine_account_type(self, account_name: str) -> str:
        """
        Determine account type based on account name
        """
        account_name_lower = account_name.lower()
        
        if any(word in account_name_lower for word in ['cash', 'bank', 'inventory', 'asset', 'receivable', 'equipment']):
            return 'asset'
        elif any(word in account_name_lower for word in ['payable', 'liability', 'debt', 'loan', 'accrued']):
            return 'liability'
        elif any(word in account_name_lower for word in ['equity', 'capital', 'retained', 'stock']):
            return 'equity'
        elif any(word in account_name_lower for word in ['revenue', 'income', 'sales', 'service']):
            return 'revenue'
        elif any(word in account_name_lower for word in ['expense', 'cost', 'cogs', 'operating', 'admin']):
            return 'expense'
        else:
            return 'asset'  # Default to asset
    
    def _generate_account_code(self, account_name: str) -> str:
        """
        Generate account code based on account name and type
        """
        account_type = self._determine_account_type(account_name)
        
        # Simple code generation based on type
        type_prefixes = {
            'asset': '1',
            'liability': '2', 
            'equity': '3',
            'revenue': '4',
            'expense': '5'
        }
        
        prefix = type_prefixes.get(account_type, '1')
        # Use hash of account name for uniqueness
        suffix = str(abs(hash(account_name)) % 1000).zfill(3)
        
        return f"{prefix}{suffix}"
    
    def on_inventory_receipt(self, receipt_data: Dict) -> Dict:
        """
        Automatically post journal entry when inventory is received
        Debit: Inventory Asset
        Credit: Accounts Payable (or Cash)
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Calculate total value
            total_value = receipt_data.get('quantity', 0) * receipt_data.get('unit_cost', 0)
            
            # Create journal entry
            journal_entry = {
                'id': je_id,
                'date': receipt_data.get('receipt_date', datetime.now()),
                'reference': receipt_data.get('po_reference', ''),
                'description': f"Inventory Receipt - {receipt_data.get('item_name', '')}",
                'status': 'posted',
                'lines': [
                    {
                        'account': 'Inventory Asset',
                        'debit': total_value,
                        'credit': 0,
                        'description': f"Received {receipt_data.get('quantity', 0)} units of {receipt_data.get('item_name', '')}"
                    },
                    {
                        'account': 'Accounts Payable',
                        'debit': 0,
                        'credit': total_value,
                        'description': f"Liability for {receipt_data.get('po_reference', '')}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_receipt',
                    'item_id': receipt_data.get('item_id'),
                    'po_id': receipt_data.get('po_id'),
                    'warehouse_id': receipt_data.get('warehouse_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for inventory receipt',
                'data': journal_entry,
                'persisted_to_db': db_success
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for inventory receipt: {str(e)}"
            }
    
    def on_inventory_sale(self, sale_data: Dict) -> Dict:
        """
        Automatically post journal entry when inventory is sold
        Debit: COGS
        Credit: Inventory Asset
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Calculate COGS using valuation method
            cogs_amount = sale_data.get('cogs_amount', 0)
            
            # Create journal entry
            journal_entry = {
                'id': je_id,
                'date': sale_data.get('sale_date', datetime.now()),
                'reference': sale_data.get('invoice_reference', ''),
                'description': f"COGS for Sale - {sale_data.get('item_name', '')}",
                'status': 'posted',
                'lines': [
                    {
                        'account': 'Cost of Goods Sold',
                        'debit': cogs_amount,
                        'credit': 0,
                        'description': f"COGS for {sale_data.get('quantity', 0)} units of {sale_data.get('item_name', '')}"
                    },
                    {
                        'account': 'Inventory Asset',
                        'debit': 0,
                        'credit': cogs_amount,
                        'description': f"Reduction in inventory for sale {sale_data.get('invoice_reference', '')}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_sale',
                    'item_id': sale_data.get('item_id'),
                    'invoice_id': sale_data.get('invoice_id'),
                    'valuation_method': sale_data.get('valuation_method', 'fifo')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for inventory sale',
                'data': journal_entry
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for inventory sale: {str(e)}"
            }
    
    def on_inventory_adjustment(self, adjustment_data: Dict) -> Dict:
        """
        Automatically post journal entry when inventory is adjusted
        Debit/Credit: Inventory Adjustment Expense
        Credit/Debit: Inventory Asset
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            adjustment_amount = adjustment_data.get('adjustment_amount', 0)
            adjustment_type = adjustment_data.get('adjustment_type', 'decrease')  # increase/decrease
            reason = adjustment_data.get('reason', '')
            
            # Determine debit/credit based on adjustment type
            if adjustment_type == 'decrease':
                # Debit: Inventory Adjustment Expense, Credit: Inventory Asset
                debit_account = 'Inventory Adjustment Expense'
                credit_account = 'Inventory Asset'
            else:
                # Debit: Inventory Asset, Credit: Inventory Adjustment Expense
                debit_account = 'Inventory Asset'
                credit_account = 'Inventory Adjustment Expense'
            
            journal_entry = {
                'id': je_id,
                'date': adjustment_data.get('adjustment_date', datetime.now()),
                'reference': adjustment_data.get('adjustment_reference', ''),
                'description': f"Inventory Adjustment - {reason}",
                'status': 'posted',
                'lines': [
                    {
                        'account': debit_account,
                        'debit': adjustment_amount,
                        'credit': 0,
                        'description': f"Adjustment: {reason}"
                    },
                    {
                        'account': credit_account,
                        'debit': 0,
                        'credit': adjustment_amount,
                        'description': f"Adjustment: {reason}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_adjustment',
                    'item_id': adjustment_data.get('item_id'),
                    'adjustment_reason': reason,
                    'adjustment_type': adjustment_type
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for inventory adjustment',
                'data': journal_entry
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for inventory adjustment: {str(e)}"
            }
    
    def on_purchase_order_created(self, po_data: Dict) -> Dict:
        """
        Post journal entry when purchase order is created (commitment)
        Debit: Purchase Commitments
        Credit: Purchase Commitments
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            total_commitment = po_data.get('total_amount', 0)
            
            journal_entry = {
                'id': je_id,
                'date': po_data.get('po_date', datetime.now()),
                'reference': po_data.get('po_reference', ''),
                'description': f"Purchase Order Commitment - {po_data.get('po_reference', '')}",
                'status': 'posted',
                'lines': [
                    {
                        'account': 'Purchase Commitments',
                        'debit': total_commitment,
                        'credit': 0,
                        'description': f"Commitment for PO {po_data.get('po_reference', '')}"
                    },
                    {
                        'account': 'Purchase Commitments',
                        'debit': 0,
                        'credit': total_commitment,
                        'description': f"Commitment for PO {po_data.get('po_reference', '')}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'purchase_order_commitment',
                    'po_id': po_data.get('po_id'),
                    'supplier_id': po_data.get('supplier_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for purchase order commitment',
                'data': journal_entry
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for purchase order: {str(e)}"
            }
    
    def on_vendor_bill_received(self, bill_data: Dict) -> Dict:
        """
        Post journal entry when vendor bill is received
        Debit: Expense (or Inventory Asset)
        Credit: Accounts Payable
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            bill_amount = bill_data.get('bill_amount', 0)
            bill_type = bill_data.get('bill_type', 'expense')  # expense, inventory, service
            vendor_name = bill_data.get('vendor_name', 'Unknown Vendor')
            
            # Determine debit account based on bill type
            if bill_type == 'inventory':
                debit_account = 'Inventory Asset'
            elif bill_type == 'service':
                debit_account = 'Operating Expenses'
            else:
                debit_account = 'General Expenses'
            
            journal_entry = {
                'id': je_id,
                'date': bill_data.get('bill_date', datetime.now()),
                'reference': bill_data.get('bill_reference', ''),
                'description': f"Vendor Bill - {vendor_name}",
                'status': 'posted',
                'lines': [
                    {
                        'account': debit_account,
                        'debit': bill_amount,
                        'credit': 0,
                        'description': f"Bill from {vendor_name} - {bill_data.get('description', '')}"
                    },
                    {
                        'account': 'Accounts Payable',
                        'debit': 0,
                        'credit': bill_amount,
                        'description': f"Amount owed to {vendor_name}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'vendor_bill',
                    'vendor_id': bill_data.get('vendor_id'),
                    'bill_type': bill_type,
                    'po_id': bill_data.get('po_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for vendor bill',
                'data': journal_entry,
                'persisted_to_db': db_success
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for vendor bill: {str(e)}"
            }

    def on_payment_made(self, payment_data: Dict) -> Dict:
        """
        Post journal entry when payment is made
        Debit: Accounts Payable
        Credit: Cash/Bank
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            payment_amount = payment_data.get('payment_amount', 0)
            payment_method = payment_data.get('payment_method', 'bank_transfer')
            
            journal_entry = {
                'id': je_id,
                'date': payment_data.get('payment_date', datetime.now()),
                'reference': payment_data.get('payment_reference', ''),
                'description': f"Payment - {payment_data.get('payment_reference', '')}",
                'status': 'posted',
                'lines': [
                    {
                        'account': 'Accounts Payable',
                        'debit': payment_amount,
                        'credit': 0,
                        'description': f"Payment for {payment_data.get('invoice_reference', '')}"
                    },
                    {
                        'account': 'Cash' if payment_method == 'cash' else 'Bank Account',
                        'debit': 0,
                        'credit': payment_amount,
                        'description': f"Payment via {payment_method}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'payment',
                    'invoice_id': payment_data.get('invoice_id'),
                    'supplier_id': payment_data.get('supplier_id'),
                    'payment_method': payment_method
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for payment',
                'data': journal_entry,
                'persisted_to_db': db_success
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for payment: {str(e)}"
            }
    
    def get_journal_entries(self, filters: Dict = None) -> List[Dict]:
        """
        Get journal entries with optional filtering
        """
        entries = self.journal_entries
        
        if filters:
            if 'transaction_type' in filters:
                entries = [e for e in entries if e['metadata'].get('transaction_type') == filters['transaction_type']]
            
            if 'date_from' in filters:
                entries = [e for e in entries if e['date'] >= filters['date_from']]
            
            if 'date_to' in filters:
                entries = [e for e in entries if e['date'] <= filters['date_to']]
        
        return entries
    
    def get_journal_entry_by_id(self, je_id: str) -> Optional[Dict]:
        """
        Get specific journal entry by ID
        """
        for entry in self.journal_entries:
            if entry['id'] == je_id:
                return entry
        return None
    
    def reverse_journal_entry(self, je_id: str, reason: str = '') -> Dict:
        """
        Reverse a journal entry (create opposite entries)
        """
        try:
            original_entry = self.get_journal_entry_by_id(je_id)
            if not original_entry:
                return {
                    'success': False,
                    'error': 'Journal entry not found'
                }
            
            self.transaction_counter += 1
            reversal_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Create reversal entry
            reversal_entry = {
                'id': reversal_id,
                'date': datetime.now(),
                'reference': f"REV-{je_id}",
                'description': f"Reversal of {je_id} - {reason}",
                'status': 'posted',
                'lines': []
            }
            
            # Reverse each line
            for line in original_entry['lines']:
                reversal_line = {
                    'account': line['account'],
                    'debit': line['credit'],  # Swap debit/credit
                    'credit': line['debit'],
                    'description': f"Reversal: {line['description']}"
                }
                reversal_entry['lines'].append(reversal_line)
            
            reversal_entry['metadata'] = {
                'transaction_type': 'reversal',
                'original_je_id': je_id,
                'reversal_reason': reason
            }
            
            self.journal_entries.append(reversal_entry)
            
            return {
                'success': True,
                'reversal_id': reversal_id,
                'message': 'Journal entry reversed successfully',
                'data': reversal_entry
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error reversing journal entry: {str(e)}"
            }

# Global instance
auto_journal_engine = AutoJournalEngine()



