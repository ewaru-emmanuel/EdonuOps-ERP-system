"""
Inventory Validation Service
Date: September 18, 2025
Purpose: Prevent finance entries that violate inventory business rules
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import re
import logging

try:
    from app import db
    from modules.inventory.advanced_models import InventoryProduct, StockLevel
    from modules.finance.advanced_models import GeneralLedgerEntry, ChartOfAccounts
    from modules.integration.auto_journal import AutoJournalEngine
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class InventoryValidationService:
    """
    Validates finance entries against inventory business rules
    Prevents "sold juice without juice" scenarios
    """
    
    def __init__(self):
        self.auto_journal = AutoJournalEngine()
        
        # Product keywords for auto-detection
        self.product_keywords = [
            'sold', 'sale', 'sales', 'revenue', 'income', 'juice', 'product', 'item', 
            'goods', 'merchandise', 'inventory', 'stock', 'widget', 'service',
            'coffee', 'tea', 'food', 'drink', 'beverage', 'equipment', 'supplies',
            'materials', 'components', 'parts', 'tools', 'software', 'hardware'
        ]
        
        # Sales-related account patterns
        self.sales_account_patterns = [
            r'sales?\s*revenue', r'revenue', r'income', r'sales?', 
            r'service\s*revenue', r'product\s*sales?'
        ]
        
        # COGS-related account patterns  
        self.cogs_account_patterns = [
            r'cost\s*of\s*goods?\s*sold', r'cogs', r'cost\s*of\s*sales?',
            r'direct\s*costs?', r'product\s*costs?'
        ]
    
    def validate_journal_entry(self, journal_data: Dict) -> Dict:
        """
        Validate journal entry against inventory business rules
        Returns validation result with warnings/errors
        """
        if not DB_AVAILABLE:
            return {'valid': True, 'warnings': [], 'errors': []}
        
        try:
            validation_result = {
                'valid': True,
                'warnings': [],
                'errors': [],
                'suggestions': [],
                'inventory_checks': []
            }
            
            description = journal_data.get('description', '').lower()
            lines = journal_data.get('lines', [])
            
            # Check each journal line
            for i, line in enumerate(lines):
                line_validation = self._validate_journal_line(line, description, i)
                
                # Merge results
                validation_result['warnings'].extend(line_validation['warnings'])
                validation_result['errors'].extend(line_validation['errors'])
                validation_result['suggestions'].extend(line_validation['suggestions'])
                validation_result['inventory_checks'].extend(line_validation['inventory_checks'])
            
            # Overall validation
            if validation_result['errors']:
                validation_result['valid'] = False
            
            # Check for sales without COGS
            sales_without_cogs = self._check_sales_without_cogs(lines, description)
            if sales_without_cogs:
                validation_result['warnings'].extend(sales_without_cogs)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating journal entry: {e}")
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}'],
                'warnings': [],
                'suggestions': []
            }
    
    def _validate_journal_line(self, line: Dict, description: str, line_index: int) -> Dict:
        """Validate individual journal line against inventory rules"""
        
        result = {
            'warnings': [],
            'errors': [],
            'suggestions': [],
            'inventory_checks': []
        }
        
        account_name = line.get('account', '').lower()
        line_description = line.get('description', '').lower()
        debit = line.get('debit', 0)
        credit = line.get('credit', 0)
        
        # Check if this is a sales revenue entry
        is_sales_entry = any(re.search(pattern, account_name) for pattern in self.sales_account_patterns)
        is_cogs_entry = any(re.search(pattern, account_name) for pattern in self.cogs_account_patterns)
        
        # Check if description mentions products
        mentioned_products = self._extract_product_mentions(description + ' ' + line_description)
        
        if is_sales_entry and credit > 0:
            # This is a sales revenue entry
            if mentioned_products:
                # Check if mentioned products exist in inventory
                for product_mention in mentioned_products:
                    inventory_check = self._check_product_inventory(product_mention, credit)
                    result['inventory_checks'].append(inventory_check)
                    
                    if not inventory_check['product_exists']:
                        result['errors'].append(
                            f"Line {line_index + 1}: Product '{product_mention}' mentioned in sales entry but not found in inventory"
                        )
                        result['suggestions'].append(
                            f"Create product '{product_mention}' in inventory first, or use generic sales account"
                        )
                    elif not inventory_check['sufficient_stock']:
                        result['warnings'].append(
                            f"Line {line_index + 1}: Insufficient stock for '{product_mention}' (Available: {inventory_check['available_quantity']}, Sale implies consumption)"
                        )
                        result['suggestions'].append(
                            f"Check inventory levels for '{product_mention}' or adjust sale quantity"
                        )
                    elif inventory_check['should_create_cogs']:
                        result['suggestions'].append(
                            f"Consider creating COGS entry for '{product_mention}' (Estimated COGS: ${inventory_check['estimated_cogs']:.2f})"
                        )
            else:
                # Sales entry without product mention
                if any(keyword in description for keyword in ['sold', 'sale', 'product', 'item', 'goods']):
                    result['warnings'].append(
                        f"Line {line_index + 1}: Sales entry detected but no specific product mentioned - consider inventory integration"
                    )
        
        elif is_cogs_entry and debit > 0:
            # This is a COGS entry - verify it matches inventory
            if mentioned_products:
                for product_mention in mentioned_products:
                    inventory_check = self._check_product_inventory(product_mention, debit)
                    result['inventory_checks'].append(inventory_check)
                    
                    if inventory_check['product_exists'] and inventory_check['estimated_cogs'] > 0:
                        cogs_variance = abs(debit - inventory_check['estimated_cogs'])
                        if cogs_variance > debit * 0.1:  # 10% variance threshold
                            result['warnings'].append(
                                f"Line {line_index + 1}: COGS amount ${debit:.2f} differs significantly from inventory cost ${inventory_check['estimated_cogs']:.2f}"
                            )
        
        return result
    
    def _extract_product_mentions(self, text: str) -> List[str]:
        """Extract potential product names from text"""
        # Simple keyword extraction - in production, this could be more sophisticated
        products = []
        
        # Look for product keywords
        for keyword in self.product_keywords:
            if keyword in text.lower():
                products.append(keyword)
        
        # Look for product names in inventory
        try:
            inventory_products = InventoryProduct.query.filter(
                InventoryProduct.is_active == True
            ).all()
            
            for product in inventory_products:
                if product.name.lower() in text.lower():
                    products.append(product.name)
                if product.sku and product.sku.lower() in text.lower():
                    products.append(product.sku)
        except Exception:
            pass
        
        return list(set(products))  # Remove duplicates
    
    def _check_product_inventory(self, product_mention: str, transaction_amount: float) -> Dict:
        """Check if product exists in inventory and has sufficient stock"""
        
        check_result = {
            'product_mention': product_mention,
            'product_exists': False,
            'product_id': None,
            'product_name': None,
            'available_quantity': 0,
            'unit_cost': 0,
            'total_value': 0,
            'sufficient_stock': False,
            'estimated_cogs': 0,
            'should_create_cogs': False
        }
        
        try:
            # Try to find product by name or SKU
            product = InventoryProduct.query.filter(
                db.or_(
                    InventoryProduct.name.ilike(f'%{product_mention}%'),
                    InventoryProduct.sku.ilike(f'%{product_mention}%')
                ),
                InventoryProduct.is_active == True
            ).first()
            
            if product:
                check_result['product_exists'] = True
                check_result['product_id'] = product.id
                check_result['product_name'] = product.name
                
                # Get stock levels
                stock_levels = StockLevel.query.filter_by(
                    product_id=product.id
                ).all()
                
                total_quantity = sum(level.quantity_on_hand for level in stock_levels)
                total_value = sum(level.total_value for level in stock_levels)
                
                check_result['available_quantity'] = total_quantity
                check_result['total_value'] = total_value
                
                if total_quantity > 0:
                    check_result['unit_cost'] = total_value / total_quantity
                    check_result['sufficient_stock'] = total_quantity > 0
                    
                    # Estimate COGS based on current cost
                    # For sales amount, estimate quantity sold
                    if product.price and product.price > 0:
                        estimated_quantity = transaction_amount / product.price
                        check_result['estimated_cogs'] = estimated_quantity * check_result['unit_cost']
                        check_result['should_create_cogs'] = True
                    else:
                        # Use 70% of sales as estimated COGS (typical margin)
                        check_result['estimated_cogs'] = transaction_amount * 0.7
                        check_result['should_create_cogs'] = True
                else:
                    check_result['sufficient_stock'] = False
            
            return check_result
            
        except Exception as e:
            logger.error(f"Error checking product inventory: {e}")
            return check_result
    
    def _check_sales_without_cogs(self, lines: List[Dict], description: str) -> List[str]:
        """Check if sales entry is missing corresponding COGS entry"""
        warnings = []
        
        has_sales = False
        has_cogs = False
        sales_amount = 0
        
        for line in lines:
            account_name = line.get('account', '').lower()
            credit = line.get('credit', 0)
            debit = line.get('debit', 0)
            
            # Check for sales revenue
            if any(re.search(pattern, account_name) for pattern in self.sales_account_patterns) and credit > 0:
                has_sales = True
                sales_amount = credit
            
            # Check for COGS
            if any(re.search(pattern, account_name) for pattern in self.cogs_account_patterns) and debit > 0:
                has_cogs = True
        
        # If sales without COGS and description mentions products
        if has_sales and not has_cogs:
            product_mentions = self._extract_product_mentions(description)
            if product_mentions:
                warnings.append(
                    f"Sales entry for ${sales_amount:.2f} mentions products but has no COGS entry - this may understate expenses"
                )
        
        return warnings
    
    def suggest_inventory_integration(self, journal_data: Dict) -> Dict:
        """
        Suggest how to properly integrate with inventory for this journal entry
        """
        suggestions = {
            'integration_recommended': False,
            'suggested_process': None,
            'auto_entries': [],
            'inventory_actions': []
        }
        
        try:
            description = journal_data.get('description', '').lower()
            lines = journal_data.get('lines', [])
            
            # Detect sales transactions
            sales_lines = [line for line in lines 
                          if any(re.search(pattern, line.get('account', '').lower()) 
                                for pattern in self.sales_account_patterns) 
                          and line.get('credit', 0) > 0]
            
            if sales_lines:
                suggestions['integration_recommended'] = True
                suggestions['suggested_process'] = 'inventory_driven_sales'
                
                for sales_line in sales_lines:
                    sales_amount = sales_line.get('credit', 0)
                    
                    # Extract product mentions
                    product_mentions = self._extract_product_mentions(description)
                    
                    for product_mention in product_mentions:
                        inventory_check = self._check_product_inventory(product_mention, sales_amount)
                        
                        if inventory_check['product_exists'] and inventory_check['should_create_cogs']:
                            # Suggest automatic COGS entry
                            suggestions['auto_entries'].append({
                                'type': 'cogs_entry',
                                'product': product_mention,
                                'estimated_cogs': inventory_check['estimated_cogs'],
                                'journal_lines': [
                                    {
                                        'account': 'Cost of Goods Sold',
                                        'debit': inventory_check['estimated_cogs'],
                                        'credit': 0,
                                        'description': f"COGS for {product_mention} sale"
                                    },
                                    {
                                        'account': 'Inventory',
                                        'debit': 0,
                                        'credit': inventory_check['estimated_cogs'],
                                        'description': f"Inventory reduction - {product_mention}"
                                    }
                                ]
                            })
                            
                            # Suggest inventory transaction
                            suggestions['inventory_actions'].append({
                                'type': 'inventory_issue',
                                'product_id': inventory_check['product_id'],
                                'product_name': inventory_check['product_name'],
                                'estimated_quantity': sales_amount / (inventory_check['unit_cost'] * 1.4) if inventory_check['unit_cost'] > 0 else 1,  # Assume 40% margin
                                'unit_cost': inventory_check['unit_cost'],
                                'reason': 'Sales transaction'
                            })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting inventory integration: {e}")
            return suggestions
    
    def enforce_inventory_business_rules(self, journal_data: Dict, strict_mode: bool = True) -> Dict:
        """
        Enforce inventory business rules on journal entries
        strict_mode: True = Block invalid entries, False = Allow with warnings
        """
        try:
            # Validate against inventory
            validation_result = self.validate_journal_entry(journal_data)
            
            # Get integration suggestions
            integration_suggestions = self.suggest_inventory_integration(journal_data)
            
            # Determine if entry should be blocked
            should_block = False
            if strict_mode and validation_result['errors']:
                should_block = True
            
            # Enhanced result
            enforcement_result = {
                'allowed': not should_block,
                'strict_mode': strict_mode,
                'validation': validation_result,
                'integration_suggestions': integration_suggestions,
                'recommended_actions': [],
                'auto_fix_available': False
            }
            
            # Generate recommended actions
            if validation_result['errors']:
                enforcement_result['recommended_actions'].append({
                    'action': 'create_missing_products',
                    'description': 'Create missing products in inventory before posting sales',
                    'priority': 'high'
                })
            
            if validation_result['warnings']:
                enforcement_result['recommended_actions'].append({
                    'action': 'review_inventory_levels',
                    'description': 'Review inventory levels for mentioned products',
                    'priority': 'medium'
                })
            
            if integration_suggestions['auto_entries']:
                enforcement_result['auto_fix_available'] = True
                enforcement_result['recommended_actions'].append({
                    'action': 'auto_create_cogs',
                    'description': 'Automatically create COGS entries based on inventory costs',
                    'priority': 'high',
                    'auto_entries': integration_suggestions['auto_entries']
                })
            
            return enforcement_result
            
        except Exception as e:
            logger.error(f"Error enforcing inventory business rules: {e}")
            return {
                'allowed': False,
                'error': str(e),
                'validation': {'valid': False, 'errors': [str(e)]}
            }
    
    def create_integrated_sales_entry(self, sales_data: Dict) -> Dict:
        """
        Create integrated sales entry with automatic inventory and COGS handling
        This is the PROPER way to handle sales in an integrated ERP
        """
        try:
            results = {
                'success': True,
                'journal_entries_created': [],
                'inventory_transactions_created': [],
                'warnings': []
            }
            
            # Step 1: Validate product exists and has stock
            product_name = sales_data.get('product_name', '')
            quantity_sold = sales_data.get('quantity', 0)
            sale_price = sales_data.get('unit_price', 0)
            customer_name = sales_data.get('customer_name', 'Customer')
            
            # Find product
            product = InventoryProduct.query.filter(
                InventoryProduct.name.ilike(f'%{product_name}%'),
                InventoryProduct.is_active == True
            ).first()
            
            if not product:
                return {
                    'success': False,
                    'error': f'Product "{product_name}" not found in inventory',
                    'suggestion': 'Create the product in inventory first'
                }
            
            # Check stock availability
            stock_levels = StockLevel.query.filter_by(product_id=product.id).all()
            available_quantity = sum(level.quantity_on_hand for level in stock_levels)
            
            if available_quantity < quantity_sold:
                return {
                    'success': False,
                    'error': f'Insufficient stock for "{product_name}" (Available: {available_quantity}, Requested: {quantity_sold})',
                    'suggestion': 'Reduce sale quantity or receive more inventory first'
                }
            
            # Step 2: Create customer invoice (A/R and Revenue)
            total_sale_amount = quantity_sold * sale_price
            invoice_result = self.auto_journal.on_customer_invoice_created({
                'customer_name': customer_name,
                'invoice_amount': total_sale_amount,
                'invoice_reference': sales_data.get('invoice_reference', f'INV-{datetime.now().strftime("%Y%m%d%H%M")}'),
                'invoice_date': sales_data.get('sale_date', datetime.now()),
                'customer_id': sales_data.get('customer_id', 1),
                'description': f'Sale of {quantity_sold} units of {product_name}'
            })
            results['journal_entries_created'].append(invoice_result)
            
            # Step 3: Create inventory issue and COGS entry
            # Calculate COGS using inventory cost
            total_value = sum(level.total_value for level in stock_levels)
            unit_cost = total_value / available_quantity if available_quantity > 0 else 0
            total_cogs = quantity_sold * unit_cost
            
            cogs_result = self.auto_journal.on_inventory_issue({
                'product_id': product.id,
                'item_name': product.name,
                'quantity': quantity_sold,
                'unit_cost': unit_cost,
                'issue_date': sales_data.get('sale_date', datetime.now()),
                'reference': sales_data.get('invoice_reference', ''),
                'customer_id': sales_data.get('customer_id'),
                'warehouse_id': sales_data.get('warehouse_id', 1)
            })
            results['journal_entries_created'].append(cogs_result)
            
            # Step 4: Update inventory levels (this would integrate with actual inventory service)
            # For now, just log the action needed
            results['inventory_transactions_created'].append({
                'type': 'inventory_issue',
                'product_id': product.id,
                'product_name': product.name,
                'quantity': quantity_sold,
                'unit_cost': unit_cost,
                'total_cost': total_cogs,
                'status': 'pending_inventory_update'
            })
            
            logger.info(f"Created integrated sales entry: Revenue ${total_sale_amount:.2f}, COGS ${total_cogs:.2f}")
            
            return {
                'success': True,
                'message': f'Integrated sales entry created for {product_name}',
                'results': results,
                'summary': {
                    'revenue_amount': total_sale_amount,
                    'cogs_amount': total_cogs,
                    'gross_profit': total_sale_amount - total_cogs,
                    'gross_margin': ((total_sale_amount - total_cogs) / total_sale_amount * 100) if total_sale_amount > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating integrated sales entry: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Convenience functions for external use
def validate_finance_entry_against_inventory(journal_data: Dict, strict_mode: bool = True) -> Dict:
    """Validate finance journal entry against inventory business rules"""
    service = InventoryValidationService()
    return service.enforce_inventory_business_rules(journal_data, strict_mode)

def create_proper_sales_entry(sales_data: Dict) -> Dict:
    """Create proper sales entry with inventory integration"""
    service = InventoryValidationService()
    return service.create_integrated_sales_entry(sales_data)

