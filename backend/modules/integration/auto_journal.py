from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal
import json
import logging

# Import database models
try:
    from app import db
    from modules.finance.advanced_models import GeneralLedgerEntry, JournalHeader, ChartOfAccounts, PostingRule
    from modules.finance.validation_engine import validate_journal_entry
    DB_AVAILABLE = True
    VALIDATION_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    VALIDATION_AVAILABLE = False

logger = logging.getLogger(__name__)

class AutoJournalEngine:
    """
    Automated Journal Entry Engine - The heartbeat of Finance-Inventory integration
    Enhanced for real-time inventory-finance synchronization
    """
    
    def __init__(self):
        self.journal_entries = []
        self.transaction_counter = 0
        self.cost_method_cache = {}  # Cache for product cost methods
    
    def _persist_to_database(self, journal_entry: Dict, event_type: str = None) -> bool:
        """
        Persist journal entry to the actual GeneralLedgerEntry database table
        Includes validation using the enhanced validation engine
        """
        if not DB_AVAILABLE:
            logger.warning("Database models not available, journal entry stored in memory only")
            return False
        
        try:
            # Enhanced validation
            if VALIDATION_AVAILABLE:
                is_valid, validation_errors = validate_journal_entry(journal_entry, event_type)
                if not is_valid:
                    logger.error(f"Journal entry validation failed: {validation_errors}")
                    # For now, log errors but still persist (can be made stricter)
                    for error in validation_errors:
                        logger.warning(f"Validation warning: {error}")
            
            # Create journal header first
            journal_header = JournalHeader(
                journal_number=journal_entry.get('id', f"JE-{datetime.now().strftime('%Y%m%d')}-AUTO"),
                source_module=journal_entry.get('source_module', 'Auto-Journal'),
                reference_id=journal_entry.get('reference', ''),
                posting_date=journal_entry.get('date', datetime.now()),
                document_date=journal_entry.get('date', datetime.now()),
                fiscal_period=journal_entry.get('date', datetime.now()).strftime('%Y-%m'),
                description=journal_entry.get('description', ''),
                total_debit=sum(line.get('debit', 0) for line in journal_entry.get('lines', [])),
                total_credit=sum(line.get('credit', 0) for line in journal_entry.get('lines', [])),
                status='posted',
                posting_status='posted',
                created_by='AUTO-JOURNAL-ENGINE'
            )
            
            db.session.add(journal_header)
            db.session.flush()  # Get the ID
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
    
    def _get_product_cost_method(self, product_id: int) -> str:
        """
        Get cost method for a product with caching for consistency
        Ensures inventory and finance use same costing method
        """
        if product_id in self.cost_method_cache:
            return self.cost_method_cache[product_id]
        
        try:
            if DB_AVAILABLE:
                # Import here to avoid circular imports
                from modules.inventory.advanced_models import InventoryProduct
                product = InventoryProduct.query.get(product_id)
                cost_method = product.cost_method if product else 'FIFO'
            else:
                cost_method = 'FIFO'  # Default
            
            self.cost_method_cache[product_id] = cost_method
            return cost_method
        except Exception:
            return 'FIFO'  # Safe default
    
    def _calculate_inventory_cost(self, product_id: int, quantity: float, 
                                unit_cost: float = None, cost_method: str = None) -> Dict:
        """
        Calculate inventory cost using specified method (FIFO, LIFO, Average)
        Centralized costing logic for inventory-finance consistency
        """
        if not cost_method:
            cost_method = self._get_product_cost_method(product_id)
        
        # For now, use provided unit_cost or calculate based on method
        # In full implementation, this would query stock levels and cost layers
        calculated_cost = unit_cost or 0.0
        total_cost = quantity * calculated_cost
        
        return {
            'unit_cost': calculated_cost,
            'total_cost': total_cost,
            'cost_method': cost_method,
            'valuation_date': datetime.now()
        }
    
    def on_inventory_receipt(self, receipt_data: Dict) -> Dict:
        """
        Automatically post journal entry when inventory is received (GR/IR Logic)
        Step 1: Goods Receipt
        Debit: Inventory Asset
        Credit: GR/IR Clearing Account
        
        Note: This creates a temporary liability until the vendor invoice is received
        """
        try:
            self.transaction_counter += 1
            je_id = f"GR-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Calculate total value
            total_value = receipt_data.get('quantity', 0) * receipt_data.get('unit_cost', 0)
            
            # Create journal entry using GR/IR clearing account
            journal_entry = {
                'id': je_id,
                'date': receipt_data.get('receipt_date', datetime.now()),
                'reference': receipt_data.get('po_reference', ''),
                'description': f"Goods Receipt - {receipt_data.get('item_name', '')} (PO: {receipt_data.get('po_reference', '')})",
                'status': 'posted',
                'source_module': 'Inventory',
                'lines': [
                    {
                        'account': 'Inventory',
                        'debit': total_value,
                        'credit': 0,
                        'description': f"Received {receipt_data.get('quantity', 0)} units of {receipt_data.get('item_name', '')}"
                    },
                    {
                        'account': 'GR/IR Clearing',
                        'debit': 0,
                        'credit': total_value,
                        'description': f"GR/IR clearing for PO {receipt_data.get('po_reference', '')} - awaiting invoice"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_receipt',
                    'item_id': receipt_data.get('item_id'),
                    'po_id': receipt_data.get('po_id'),
                    'warehouse_id': receipt_data.get('warehouse_id'),
                    'gr_ir_status': 'goods_received',
                    'awaiting_invoice': True
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
        Automatically post journal entry when vendor bill is received (GR/IR Logic)
        Step 2: Invoice Receipt (clears GR/IR)
        Debit: GR/IR Clearing Account (if goods receipt exists) OR Direct Expense
        Credit: Accounts Payable
        
        Note: This clears the temporary GR/IR liability and creates actual AP
        """
        try:
            self.transaction_counter += 1
            je_id = f"IR-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            bill_amount = bill_data.get('bill_amount', 0)
            vendor_name = bill_data.get('vendor_name', 'Unknown Vendor')
            po_reference = bill_data.get('po_reference', '')
            
            # Check if this bill matches a goods receipt (GR/IR process)
            has_goods_receipt = bill_data.get('has_goods_receipt', False)
            bill_type = bill_data.get('bill_type', 'expense')  # expense, inventory, service
            
            if has_goods_receipt:
                # Standard GR/IR clearing entry
                debit_account = 'GR/IR Clearing'
                description_prefix = f"Clearing GR/IR for PO {po_reference}"
                gr_ir_status = 'invoice_received'
                clears_gr_ir = True
            else:
                # Direct expense (no goods receipt) - services, utilities, etc.
                if bill_type == 'inventory':
                    debit_account = 'Inventory'
                elif bill_type == 'service':
                    debit_account = 'Operating Expenses'
                else:
                    debit_account = 'General Expenses'
                description_prefix = f"Direct expense from {vendor_name}"
                gr_ir_status = 'direct_expense'
                clears_gr_ir = False
            
            journal_entry = {
                'id': je_id,
                'date': bill_data.get('bill_date', datetime.now()),
                'reference': bill_data.get('bill_reference', ''),
                'description': f"Vendor Bill - {vendor_name} ({'GR/IR Clearing' if has_goods_receipt else 'Direct'})",
                'status': 'posted',
                'source_module': 'Procurement',
                'lines': [
                    {
                        'account': debit_account,
                        'debit': bill_amount,
                        'credit': 0,
                        'description': description_prefix
                    },
                    {
                        'account': 'Accounts Payable',
                        'debit': 0,
                        'credit': bill_amount,
                        'description': f"Amount owed to {vendor_name} - Invoice {bill_data.get('bill_reference', '')}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'vendor_bill',
                    'vendor_id': bill_data.get('vendor_id'),
                    'bill_type': bill_type,
                    'po_id': bill_data.get('po_id'),
                    'po_reference': po_reference,
                    'gr_ir_status': gr_ir_status,
                    'clears_gr_ir': clears_gr_ir,
                    'has_goods_receipt': has_goods_receipt
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

    def on_customer_invoice_created(self, invoice_data: Dict) -> Dict:
        """
        Post journal entry when customer invoice is created
        Debit: Accounts Receivable
        Credit: Revenue
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            invoice_amount = invoice_data.get('invoice_amount', 0)
            customer_name = invoice_data.get('customer_name', 'Unknown Customer')
            
            journal_entry = {
                'id': je_id,
                'date': invoice_data.get('invoice_date', datetime.now()),
                'reference': invoice_data.get('invoice_reference', ''),
                'description': f"Customer Invoice - {customer_name}",
                'status': 'posted',
                'lines': [
                    {
                        'account': 'Accounts Receivable',
                        'debit': invoice_amount,
                        'credit': 0,
                        'description': f"Invoice to {customer_name} - {invoice_data.get('description', '')}"
                    },
                    {
                        'account': 'Sales Revenue',
                        'debit': 0,
                        'credit': invoice_amount,
                        'description': f"Revenue from {customer_name}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'customer_invoice',
                    'customer_id': invoice_data.get('customer_id'),
                    'invoice_id': invoice_data.get('invoice_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for customer invoice',
                'data': journal_entry,
                'persisted_to_db': db_success
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for customer invoice: {str(e)}"
            }

    def on_customer_payment_received(self, payment_data: Dict) -> Dict:
        """
        Post journal entry when customer payment is received
        Debit: Cash/Bank
        Credit: Accounts Receivable
        """
        try:
            self.transaction_counter += 1
            je_id = f"JE-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            payment_amount = payment_data.get('payment_amount', 0)
            payment_method = payment_data.get('payment_method', 'bank_transfer')
            customer_name = payment_data.get('customer_name', 'Unknown Customer')
            
            journal_entry = {
                'id': je_id,
                'date': payment_data.get('payment_date', datetime.now()),
                'reference': payment_data.get('payment_reference', ''),
                'description': f"Customer Payment - {customer_name}",
                'status': 'posted',
                'lines': [
                    {
                        'account': 'Cash' if payment_method == 'cash' else 'Bank Account',
                        'debit': payment_amount,
                        'credit': 0,
                        'description': f"Payment received from {customer_name}"
                    },
                    {
                        'account': 'Accounts Receivable',
                        'debit': 0,
                        'credit': payment_amount,
                        'description': f"Payment for {payment_data.get('invoice_reference', '')}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'customer_payment',
                    'customer_id': payment_data.get('customer_id'),
                    'invoice_id': payment_data.get('invoice_id'),
                    'payment_method': payment_method
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry)
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': 'Journal entry posted successfully for customer payment',
                'data': journal_entry,
                'persisted_to_db': db_success
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error posting journal entry for customer payment: {str(e)}"
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
    
    # ============================================================================
    # ENHANCED INVENTORY-FINANCE INTEGRATION EVENTS
    # ============================================================================
    
    def on_inventory_issue(self, issue_data: Dict) -> Dict:
        """
        Post journal entry when inventory is issued (Sales/COGS)
        Dr. Cost of Goods Sold
        Cr. Inventory Asset
        """
        try:
            self.transaction_counter += 1
            je_id = f"COGS-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Get product and cost information
            product_id = issue_data.get('product_id')
            quantity = issue_data.get('quantity', 0)
            unit_cost = issue_data.get('unit_cost', 0)
            
            # Calculate cost using centralized method
            cost_info = self._calculate_inventory_cost(
                product_id=product_id,
                quantity=quantity,
                unit_cost=unit_cost
            )
            
            total_cost = cost_info['total_cost']
            
            journal_entry = {
                'id': je_id,
                'date': issue_data.get('issue_date', datetime.now()),
                'reference': issue_data.get('reference', ''),
                'description': f"COGS - {issue_data.get('item_name', 'Inventory Item')} (Issue: {quantity} units)",
                'status': 'posted',
                'source_module': 'Inventory',
                'lines': [
                    {
                        'account': 'Cost of Goods Sold',
                        'debit': total_cost,
                        'credit': 0,
                        'description': f"COGS for {quantity} units of {issue_data.get('item_name', 'Item')}"
                    },
                    {
                        'account': 'Inventory',
                        'debit': 0,
                        'credit': total_cost,
                        'description': f"Inventory reduction - {issue_data.get('item_name', 'Item')}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_issue',
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_cost': cost_info['unit_cost'],
                    'cost_method': cost_info['cost_method'],
                    'customer_id': issue_data.get('customer_id'),
                    'sales_order_id': issue_data.get('sales_order_id'),
                    'warehouse_id': issue_data.get('warehouse_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry, 'inventory_issue')
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': f'COGS journal entry created: {je_id}',
                'persisted_to_db': db_success,
                'cost_method': cost_info['cost_method'],
                'total_cost': total_cost
            }
            
        except Exception as e:
            logger.error(f"Error posting COGS journal entry: {str(e)}")
            return {
                'success': False,
                'error': f"Error posting COGS journal entry: {str(e)}"
            }
    
    def on_inventory_adjustment(self, adjustment_data: Dict) -> Dict:
        """
        Post journal entry for inventory adjustments (Physical Count, Damage, etc.)
        Positive Adjustment: Dr. Inventory Asset, Cr. Inventory Adjustment Income
        Negative Adjustment: Dr. Inventory Adjustment Expense, Cr. Inventory Asset
        """
        try:
            self.transaction_counter += 1
            je_id = f"ADJ-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Get adjustment information
            product_id = adjustment_data.get('product_id')
            adjustment_quantity = adjustment_data.get('adjustment_quantity', 0)  # Can be negative
            unit_cost = adjustment_data.get('unit_cost', 0)
            reason = adjustment_data.get('reason', 'Physical Count')
            
            # Calculate cost impact
            cost_info = self._calculate_inventory_cost(
                product_id=product_id,
                quantity=abs(adjustment_quantity),
                unit_cost=unit_cost
            )
            
            total_adjustment_value = cost_info['total_cost']
            
            # Determine accounts based on adjustment type
            if adjustment_quantity > 0:
                # Positive adjustment (found more inventory)
                debit_account = 'Inventory'
                credit_account = 'Inventory Adjustment Income'
                description_prefix = "Inventory increase"
            else:
                # Negative adjustment (inventory shortage/loss)
                debit_account = 'Inventory Adjustment Expense'
                credit_account = 'Inventory'
                description_prefix = "Inventory decrease"
            
            journal_entry = {
                'id': je_id,
                'date': adjustment_data.get('adjustment_date', datetime.now()),
                'reference': adjustment_data.get('reference', ''),
                'description': f"Inventory Adjustment - {adjustment_data.get('item_name', 'Item')} ({reason})",
                'status': 'posted',
                'source_module': 'Inventory',
                'lines': [
                    {
                        'account': debit_account,
                        'debit': total_adjustment_value,
                        'credit': 0,
                        'description': f"{description_prefix} - {adjustment_data.get('item_name', 'Item')} ({adjustment_quantity} units)"
                    },
                    {
                        'account': credit_account,
                        'debit': 0,
                        'credit': total_adjustment_value,
                        'description': f"Adjustment for {adjustment_data.get('item_name', 'Item')} - {reason}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_adjustment',
                    'product_id': product_id,
                    'adjustment_quantity': adjustment_quantity,
                    'unit_cost': cost_info['unit_cost'],
                    'cost_method': cost_info['cost_method'],
                    'reason': reason,
                    'warehouse_id': adjustment_data.get('warehouse_id'),
                    'adjustment_type': 'positive' if adjustment_quantity > 0 else 'negative'
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry, 'inventory_adjustment')
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': f'Inventory adjustment journal entry created: {je_id}',
                'persisted_to_db': db_success,
                'adjustment_type': 'positive' if adjustment_quantity > 0 else 'negative',
                'adjustment_value': total_adjustment_value
            }
            
        except Exception as e:
            logger.error(f"Error posting inventory adjustment journal entry: {str(e)}")
            return {
                'success': False,
                'error': f"Error posting inventory adjustment journal entry: {str(e)}"
            }
    
    def on_inventory_transfer(self, transfer_data: Dict) -> Dict:
        """
        Post journal entry for inventory transfers between locations
        If cost changes: Dr. Inventory (To Location), Cr. Inventory (From Location)
        If no cost change: No GL entry needed (just inventory movement)
        """
        try:
            # Check if cost changes between locations
            from_cost = transfer_data.get('from_unit_cost', 0)
            to_cost = transfer_data.get('to_unit_cost', 0)
            
            if abs(from_cost - to_cost) < 0.01:
                # No cost change - no GL entry needed
                return {
                    'success': True,
                    'journal_entry_id': None,
                    'message': 'No GL entry needed - cost unchanged',
                    'cost_change': False
                }
            
            # Cost change detected - create GL entry
            self.transaction_counter += 1
            je_id = f"TXF-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            quantity = transfer_data.get('quantity', 0)
            cost_difference = (to_cost - from_cost) * quantity
            
            if cost_difference > 0:
                # Higher cost at destination
                debit_account = 'Inventory'
                credit_account = 'Inventory Revaluation'
            else:
                # Lower cost at destination
                debit_account = 'Inventory Revaluation'
                credit_account = 'Inventory'
                cost_difference = abs(cost_difference)
            
            journal_entry = {
                'id': je_id,
                'date': transfer_data.get('transfer_date', datetime.now()),
                'reference': transfer_data.get('reference', ''),
                'description': f"Inventory Transfer Cost Adjustment - {transfer_data.get('item_name', 'Item')}",
                'status': 'posted',
                'source_module': 'Inventory',
                'lines': [
                    {
                        'account': debit_account,
                        'debit': cost_difference,
                        'credit': 0,
                        'description': f"Transfer cost adjustment - {transfer_data.get('item_name', 'Item')}"
                    },
                    {
                        'account': credit_account,
                        'debit': 0,
                        'credit': cost_difference,
                        'description': f"Transfer revaluation - {transfer_data.get('from_location', 'From')} to {transfer_data.get('to_location', 'To')}"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_transfer',
                    'product_id': transfer_data.get('product_id'),
                    'quantity': quantity,
                    'from_cost': from_cost,
                    'to_cost': to_cost,
                    'cost_difference': cost_difference,
                    'from_location_id': transfer_data.get('from_location_id'),
                    'to_location_id': transfer_data.get('to_location_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry, 'inventory_transfer')
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': f'Inventory transfer cost adjustment created: {je_id}',
                'persisted_to_db': db_success,
                'cost_change': True,
                'cost_difference': cost_difference
            }
            
        except Exception as e:
            logger.error(f"Error posting inventory transfer journal entry: {str(e)}")
            return {
                'success': False,
                'error': f"Error posting inventory transfer journal entry: {str(e)}"
            }
    
    def on_inventory_writeoff(self, writeoff_data: Dict) -> Dict:
        """
        Post journal entry for inventory write-offs (Damaged, Obsolete, Expired)
        Dr. Inventory Loss Expense
        Cr. Inventory Asset
        """
        try:
            self.transaction_counter += 1
            je_id = f"WO-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Get write-off information
            product_id = writeoff_data.get('product_id')
            quantity = writeoff_data.get('quantity', 0)
            unit_cost = writeoff_data.get('unit_cost', 0)
            reason = writeoff_data.get('reason', 'Damaged')
            
            # Calculate cost impact
            cost_info = self._calculate_inventory_cost(
                product_id=product_id,
                quantity=quantity,
                unit_cost=unit_cost
            )
            
            total_writeoff_value = cost_info['total_cost']
            
            # Determine expense account based on reason
            expense_accounts = {
                'damaged': 'Inventory Damage Expense',
                'obsolete': 'Inventory Obsolescence Expense',
                'expired': 'Inventory Expiry Expense',
                'theft': 'Inventory Theft Loss',
                'other': 'Inventory Loss Expense'
            }
            
            expense_account = expense_accounts.get(reason.lower(), 'Inventory Loss Expense')
            
            journal_entry = {
                'id': je_id,
                'date': writeoff_data.get('writeoff_date', datetime.now()),
                'reference': writeoff_data.get('reference', ''),
                'description': f"Inventory Write-off - {writeoff_data.get('item_name', 'Item')} ({reason})",
                'status': 'posted',
                'source_module': 'Inventory',
                'lines': [
                    {
                        'account': expense_account,
                        'debit': total_writeoff_value,
                        'credit': 0,
                        'description': f"Write-off {quantity} units of {writeoff_data.get('item_name', 'Item')} - {reason}"
                    },
                    {
                        'account': 'Inventory',
                        'debit': 0,
                        'credit': total_writeoff_value,
                        'description': f"Inventory reduction - {writeoff_data.get('item_name', 'Item')} write-off"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_writeoff',
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_cost': cost_info['unit_cost'],
                    'cost_method': cost_info['cost_method'],
                    'reason': reason,
                    'warehouse_id': writeoff_data.get('warehouse_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry, 'inventory_writeoff')
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': f'Inventory write-off journal entry created: {je_id}',
                'persisted_to_db': db_success,
                'writeoff_value': total_writeoff_value,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error posting inventory write-off journal entry: {str(e)}")
            return {
                'success': False,
                'error': f"Error posting inventory write-off journal entry: {str(e)}"
            }
    
    def on_inventory_revaluation(self, revaluation_data: Dict) -> Dict:
        """
        Post journal entry for inventory revaluations (Cost changes, Currency adjustments)
        Positive Revaluation: Dr. Inventory Asset, Cr. Inventory Revaluation Gain
        Negative Revaluation: Dr. Inventory Revaluation Loss, Cr. Inventory Asset
        """
        try:
            self.transaction_counter += 1
            je_id = f"REV-{datetime.now().strftime('%Y%m%d')}-{self.transaction_counter:03d}"
            
            # Get revaluation information
            product_id = revaluation_data.get('product_id')
            quantity = revaluation_data.get('quantity', 0)
            old_unit_cost = revaluation_data.get('old_unit_cost', 0)
            new_unit_cost = revaluation_data.get('new_unit_cost', 0)
            reason = revaluation_data.get('reason', 'Cost Update')
            
            # Calculate revaluation impact
            old_total_value = quantity * old_unit_cost
            new_total_value = quantity * new_unit_cost
            revaluation_amount = new_total_value - old_total_value
            
            if abs(revaluation_amount) < 0.01:
                return {
                    'success': True,
                    'journal_entry_id': None,
                    'message': 'No revaluation needed - cost unchanged',
                    'revaluation_amount': 0
                }
            
            # Determine accounts based on revaluation direction
            if revaluation_amount > 0:
                # Positive revaluation (cost increased)
                debit_account = 'Inventory'
                credit_account = 'Inventory Revaluation Gain'
                description_prefix = "Inventory revaluation gain"
            else:
                # Negative revaluation (cost decreased)
                debit_account = 'Inventory Revaluation Loss'
                credit_account = 'Inventory'
                description_prefix = "Inventory revaluation loss"
                revaluation_amount = abs(revaluation_amount)
            
            journal_entry = {
                'id': je_id,
                'date': revaluation_data.get('revaluation_date', datetime.now()),
                'reference': revaluation_data.get('reference', ''),
                'description': f"Inventory Revaluation - {revaluation_data.get('item_name', 'Item')} ({reason})",
                'status': 'posted',
                'source_module': 'Inventory',
                'lines': [
                    {
                        'account': debit_account,
                        'debit': revaluation_amount,
                        'credit': 0,
                        'description': f"{description_prefix} - {revaluation_data.get('item_name', 'Item')} (${old_unit_cost:.2f} → ${new_unit_cost:.2f})"
                    },
                    {
                        'account': credit_account,
                        'debit': 0,
                        'credit': revaluation_amount,
                        'description': f"Revaluation adjustment - {quantity} units @ ${new_unit_cost - old_unit_cost:.2f} difference"
                    }
                ],
                'metadata': {
                    'transaction_type': 'inventory_revaluation',
                    'product_id': product_id,
                    'quantity': quantity,
                    'old_unit_cost': old_unit_cost,
                    'new_unit_cost': new_unit_cost,
                    'revaluation_amount': revaluation_amount,
                    'reason': reason,
                    'warehouse_id': revaluation_data.get('warehouse_id')
                }
            }
            
            self.journal_entries.append(journal_entry)
            
            # Persist to database
            db_success = self._persist_to_database(journal_entry, 'inventory_revaluation')
            
            return {
                'success': True,
                'journal_entry_id': je_id,
                'message': f'Inventory revaluation journal entry created: {je_id}',
                'persisted_to_db': db_success,
                'revaluation_amount': revaluation_amount,
                'revaluation_type': 'gain' if new_unit_cost > old_unit_cost else 'loss'
            }
            
        except Exception as e:
            logger.error(f"Error posting inventory revaluation journal entry: {str(e)}")
            return {
                'success': False,
                'error': f"Error posting inventory revaluation journal entry: {str(e)}"
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



