"""
Complete Double Entry Accounting Service
Date: September 18, 2025
Purpose: Demonstrate enterprise-grade double entry implementation with all gaps closed
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import json
import logging

# Import all components
try:
    from app import db
    from modules.finance.advanced_models import (
        ChartOfAccounts, PostingRule, JournalHeader, GeneralLedgerEntry
    )
    from modules.finance.validation_engine import validate_journal_entry
    from modules.integration.auto_journal import AutoJournalEngine
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class DoubleEntryService:
    """
    Complete Double Entry Accounting Service
    Demonstrates all enterprise features working together
    """
    
    def __init__(self):
        self.auto_journal = AutoJournalEngine()
    
    def process_complete_procurement_cycle(self, procurement_data: Dict) -> Dict:
        """
        Demonstrate complete GR/IR procurement cycle with proper double entry
        
        Steps:
        1. Purchase Order Created (optional entry)
        2. Goods Received → Dr. Inventory, Cr. GR/IR Clearing
        3. Invoice Received → Dr. GR/IR Clearing, Cr. Accounts Payable
        4. Payment Made → Dr. Accounts Payable, Cr. Cash/Bank
        """
        results = {
            'success': True,
            'steps': [],
            'journal_entries': [],
            'errors': []
        }
        
        try:
            # Step 1: Goods Receipt (GR)
            if procurement_data.get('goods_received'):
                gr_result = self.auto_journal.on_inventory_receipt({
                    'item_name': procurement_data.get('item_name', 'Sample Item'),
                    'quantity': procurement_data.get('quantity', 10),
                    'unit_cost': procurement_data.get('unit_cost', 50),
                    'po_reference': procurement_data.get('po_number', 'PO-2025-001'),
                    'receipt_date': procurement_data.get('receipt_date', datetime.now()),
                    'item_id': procurement_data.get('item_id', 1),
                    'po_id': procurement_data.get('po_id', 1),
                    'warehouse_id': procurement_data.get('warehouse_id', 1)
                })
                results['steps'].append('Goods Receipt Posted')
                results['journal_entries'].append(gr_result)
            
            # Step 2: Invoice Receipt (IR) - Clears GR/IR
            if procurement_data.get('invoice_received'):
                ir_result = self.auto_journal.on_vendor_bill_received({
                    'vendor_name': procurement_data.get('vendor_name', 'ABC Supplier'),
                    'bill_amount': procurement_data.get('quantity', 10) * procurement_data.get('unit_cost', 50),
                    'bill_reference': procurement_data.get('invoice_number', 'INV-2025-001'),
                    'bill_date': procurement_data.get('invoice_date', datetime.now()),
                    'po_reference': procurement_data.get('po_number', 'PO-2025-001'),
                    'has_goods_receipt': True,  # This triggers GR/IR clearing
                    'vendor_id': procurement_data.get('vendor_id', 1),
                    'bill_id': procurement_data.get('bill_id', 1)
                })
                results['steps'].append('Invoice Receipt Posted (GR/IR Cleared)')
                results['journal_entries'].append(ir_result)
            
            # Step 3: Payment Made
            if procurement_data.get('payment_made'):
                payment_result = self.auto_journal.on_payment_made({
                    'vendor_name': procurement_data.get('vendor_name', 'ABC Supplier'),
                    'payment_amount': procurement_data.get('quantity', 10) * procurement_data.get('unit_cost', 50),
                    'payment_reference': procurement_data.get('payment_reference', 'PAY-2025-001'),
                    'payment_date': procurement_data.get('payment_date', datetime.now()),
                    'payment_method': procurement_data.get('payment_method', 'bank_transfer'),
                    'vendor_id': procurement_data.get('vendor_id', 1)
                })
                results['steps'].append('Payment Posted')
                results['journal_entries'].append(payment_result)
            
            logger.info(f"Procurement cycle completed: {len(results['steps'])} steps processed")
            return results
            
        except Exception as e:
            logger.error(f"Error processing procurement cycle: {e}")
            results['success'] = False
            results['errors'].append(str(e))
            return results
    
    def process_complete_sales_cycle(self, sales_data: Dict) -> Dict:
        """
        Demonstrate complete sales cycle with proper double entry
        
        Steps:
        1. Customer Invoice Created → Dr. Accounts Receivable, Cr. Sales Revenue
        2. Inventory Sold → Dr. Cost of Goods Sold, Cr. Inventory
        3. Customer Payment → Dr. Cash/Bank, Cr. Accounts Receivable
        """
        results = {
            'success': True,
            'steps': [],
            'journal_entries': [],
            'errors': []
        }
        
        try:
            # Step 1: Customer Invoice
            if sales_data.get('invoice_created'):
                invoice_result = self.auto_journal.on_customer_invoice_created({
                    'customer_name': sales_data.get('customer_name', 'XYZ Customer'),
                    'invoice_amount': sales_data.get('invoice_amount', 1000),
                    'invoice_reference': sales_data.get('invoice_number', 'INV-2025-001'),
                    'invoice_date': sales_data.get('invoice_date', datetime.now()),
                    'customer_id': sales_data.get('customer_id', 1),
                    'invoice_id': sales_data.get('invoice_id', 1),
                    'description': sales_data.get('description', 'Product sale')
                })
                results['steps'].append('Customer Invoice Posted')
                results['journal_entries'].append(invoice_result)
            
            # Step 2: Inventory Movement (COGS)
            if sales_data.get('inventory_sold'):
                cogs_result = self.auto_journal.on_inventory_sale({
                    'item_name': sales_data.get('item_name', 'Sample Product'),
                    'quantity_sold': sales_data.get('quantity', 20),
                    'unit_cost': sales_data.get('unit_cost', 30),  # Cost basis
                    'sale_price': sales_data.get('unit_price', 50),  # Sale price
                    'sale_date': sales_data.get('sale_date', datetime.now()),
                    'customer_name': sales_data.get('customer_name', 'XYZ Customer'),
                    'item_id': sales_data.get('item_id', 1),
                    'sale_id': sales_data.get('sale_id', 1)
                })
                results['steps'].append('Inventory Sale Posted (COGS)')
                results['journal_entries'].append(cogs_result)
            
            # Step 3: Customer Payment
            if sales_data.get('payment_received'):
                payment_result = self.auto_journal.on_customer_payment_received({
                    'customer_name': sales_data.get('customer_name', 'XYZ Customer'),
                    'payment_amount': sales_data.get('payment_amount', 1000),
                    'payment_reference': sales_data.get('payment_reference', 'PAY-2025-001'),
                    'payment_date': sales_data.get('payment_date', datetime.now()),
                    'payment_method': sales_data.get('payment_method', 'bank_transfer'),
                    'customer_id': sales_data.get('customer_id', 1),
                    'invoice_reference': sales_data.get('invoice_number', 'INV-2025-001')
                })
                results['steps'].append('Customer Payment Posted')
                results['journal_entries'].append(payment_result)
            
            logger.info(f"Sales cycle completed: {len(results['steps'])} steps processed")
            return results
            
        except Exception as e:
            logger.error(f"Error processing sales cycle: {e}")
            results['success'] = False
            results['errors'].append(str(e))
            return results
    
    def get_posting_rules_summary(self) -> Dict:
        """Get summary of all configured posting rules"""
        if not DB_AVAILABLE:
            return {'error': 'Database not available'}
        
        try:
            rules = PostingRule.query.filter_by(is_active=True).all()
            
            rules_summary = []
            for rule in rules:
                rules_summary.append({
                    'id': rule.id,
                    'event_type': rule.event_type,
                    'description': rule.event_description,
                    'debit_account': rule.debit_account_name,
                    'credit_account': rule.credit_account_name,
                    'conditions': rule.conditions,
                    'priority': rule.priority,
                    'valid_from': rule.valid_from.isoformat() if rule.valid_from else None,
                    'valid_to': rule.valid_to.isoformat() if rule.valid_to else None
                })
            
            return {
                'total_rules': len(rules_summary),
                'rules': rules_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting posting rules: {e}")
            return {'error': str(e)}
    
    def get_trial_balance(self, as_of_date: date = None) -> Dict:
        """Generate trial balance from journal entries"""
        if not DB_AVAILABLE:
            return {'error': 'Database not available'}
        
        try:
            if not as_of_date:
                as_of_date = date.today()
            
            # Query all GL entries up to the date
            entries = GeneralLedgerEntry.query.filter(
                GeneralLedgerEntry.entry_date <= as_of_date,
                GeneralLedgerEntry.status == 'posted'
            ).all()
            
            # Aggregate by account
            account_balances = {}
            for entry in entries:
                account_name = entry.account.account_name if entry.account else 'Unknown Account'
                
                if account_name not in account_balances:
                    account_balances[account_name] = {
                        'account_type': entry.account.account_type if entry.account else 'Unknown',
                        'total_debit': 0,
                        'total_credit': 0,
                        'balance': 0
                    }
                
                account_balances[account_name]['total_debit'] += entry.debit_amount or 0
                account_balances[account_name]['total_credit'] += entry.credit_amount or 0
            
            # Calculate balances and totals
            total_debits = 0
            total_credits = 0
            
            for account_name, data in account_balances.items():
                # Calculate balance based on account type
                account_type = data['account_type'].lower()
                if account_type in ['asset', 'expense']:
                    data['balance'] = data['total_debit'] - data['total_credit']
                else:  # liability, equity, revenue
                    data['balance'] = data['total_credit'] - data['total_debit']
                
                total_debits += data['total_debit']
                total_credits += data['total_credit']
            
            return {
                'as_of_date': as_of_date.isoformat(),
                'accounts': account_balances,
                'totals': {
                    'total_debits': total_debits,
                    'total_credits': total_credits,
                    'difference': total_debits - total_credits,
                    'is_balanced': abs(total_debits - total_credits) < 0.01
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating trial balance: {e}")
            return {'error': str(e)}
    
    def validate_system_integrity(self) -> Dict:
        """Comprehensive system validation"""
        if not DB_AVAILABLE:
            return {'error': 'Database not available'}
        
        validation_results = {
            'overall_status': 'PASS',
            'checks': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # Check 1: All journal entries are balanced
            unbalanced_entries = []
            headers = JournalHeader.query.filter_by(status='posted').all()
            
            for header in headers:
                if abs(header.total_debit - header.total_credit) > 0.01:
                    unbalanced_entries.append({
                        'journal_number': header.journal_number,
                        'debit': header.total_debit,
                        'credit': header.total_credit,
                        'difference': header.total_debit - header.total_credit
                    })
            
            if unbalanced_entries:
                validation_results['errors'].extend(unbalanced_entries)
                validation_results['overall_status'] = 'FAIL'
            else:
                validation_results['checks'].append('✅ All journal entries are balanced')
            
            # Check 2: All accounts have valid types
            invalid_accounts = ChartOfAccounts.query.filter(
                ~ChartOfAccounts.account_type.in_(['Asset', 'Liability', 'Equity', 'Revenue', 'Expense'])
            ).all()
            
            if invalid_accounts:
                validation_results['warnings'].append(f"⚠️ {len(invalid_accounts)} accounts have invalid types")
            else:
                validation_results['checks'].append('✅ All accounts have valid types')
            
            # Check 3: Posting rules coverage
            events_with_rules = set(rule.event_type for rule in PostingRule.query.filter_by(is_active=True).all())
            expected_events = {'inventory_receipt', 'vendor_bill_received', 'customer_invoice_created', 
                             'customer_payment_received', 'payment_made'}
            
            missing_rules = expected_events - events_with_rules
            if missing_rules:
                validation_results['warnings'].append(f"⚠️ Missing posting rules for: {', '.join(missing_rules)}")
            else:
                validation_results['checks'].append('✅ All core posting rules are configured')
            
            # Check 4: GR/IR Clearing Account exists
            gr_ir_account = ChartOfAccounts.query.filter_by(account_name='GR/IR Clearing').first()
            if not gr_ir_account:
                validation_results['warnings'].append('⚠️ GR/IR Clearing account not found - will be auto-created')
            else:
                validation_results['checks'].append('✅ GR/IR Clearing account exists')
            
            logger.info(f"System validation completed: {validation_results['overall_status']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating system integrity: {e}")
            validation_results['overall_status'] = 'ERROR'
            validation_results['errors'].append(str(e))
            return validation_results

# Convenience functions for external use
def demo_complete_procurement_cycle():
    """Demo function showing complete procurement cycle"""
    service = DoubleEntryService()
    
    demo_data = {
        'item_name': 'Office Supplies',
        'quantity': 100,
        'unit_cost': 15.50,
        'vendor_name': 'Office Depot',
        'po_number': 'PO-2025-DEMO-001',
        'invoice_number': 'INV-DEPOT-12345',
        'payment_reference': 'PAY-DEPOT-001',
        'goods_received': True,
        'invoice_received': True,
        'payment_made': True
    }
    
    return service.process_complete_procurement_cycle(demo_data)

def demo_complete_sales_cycle():
    """Demo function showing complete sales cycle"""
    service = DoubleEntryService()
    
    demo_data = {
        'customer_name': 'Acme Corp',
        'item_name': 'Premium Widget',
        'quantity': 50,
        'unit_cost': 20,  # Our cost
        'unit_price': 35,  # Sale price
        'invoice_amount': 1750,  # 50 * 35
        'payment_amount': 1750,
        'invoice_number': 'INV-2025-DEMO-001',
        'payment_reference': 'PAY-ACME-001',
        'invoice_created': True,
        'inventory_sold': True,
        'payment_received': True
    }
    
    return service.process_complete_sales_cycle(demo_data)

def get_system_status():
    """Get complete system status and validation"""
    service = DoubleEntryService()
    
    return {
        'posting_rules': service.get_posting_rules_summary(),
        'trial_balance': service.get_trial_balance(),
        'system_validation': service.validate_system_integrity()
    }

