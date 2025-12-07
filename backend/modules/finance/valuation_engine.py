from datetime import datetime, date
from sqlalchemy import and_, func
from app import db
from modules.finance.currency_models import ExchangeRate
from modules.finance.advanced_models import CompanySettings, GeneralLedgerEntry, ChartOfAccounts
from modules.inventory.advanced_models import InventoryProduct, InventoryTransaction, StockLevel

class MultiCurrencyValuationEngine:
    """Multi-currency inventory valuation engine"""
    
    def __init__(self):
        self.base_currency = self._get_base_currency()
    
    def _get_base_currency(self):
        """Get company base currency from settings"""
        setting = CompanySettings.query.filter_by(setting_key='base_currency').first()
        return setting.setting_value if setting else 'USD'
    
    def get_exchange_rate(self, from_currency, to_currency, rate_date=None):
        """Get exchange rate for currency conversion"""
        if not rate_date:
            rate_date = date.today()
        
        if from_currency == to_currency:
            return 1.0
        
        # Try to get the rate for the specific date
        rate = ExchangeRate.query.filter(
            and_(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.effective_date == rate_date
            )
        ).first()
        
        if rate:
            return rate.rate
        
        # If no rate for specific date, get the most recent rate
        rate = ExchangeRate.query.filter(
            and_(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.effective_date <= rate_date
            )
        ).order_by(ExchangeRate.effective_date.desc()).first()
        
        return rate.rate if rate else 1.0
    
    def convert_currency(self, amount, from_currency, to_currency, rate_date=None):
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        rate = self.get_exchange_rate(from_currency, to_currency, rate_date)
        return amount * rate
    
    def calculate_purchase_valuation(self, product_id, quantity, unit_cost, currency, transaction_date):
        """Calculate inventory value for purchase transactions"""
        try:
            # Convert to base currency
            base_currency_cost = self.convert_currency(unit_cost, currency, self.base_currency, transaction_date)
            total_base_cost = base_currency_cost * quantity
            
            # Update product base currency cost
            product = InventoryProduct.query.get(product_id)
            if product:
                # Update average cost in base currency
                current_stock = StockLevel.query.filter_by(product_id=product_id).first()
                if current_stock and current_stock.quantity_on_hand > 0:
                    # Calculate weighted average
                    total_value = (current_stock.quantity_on_hand * current_stock.average_cost) + total_base_cost
                    total_quantity = current_stock.quantity_on_hand + quantity
                    new_average_cost = total_value / total_quantity
                else:
                    new_average_cost = base_currency_cost
                
                product.base_currency_cost = new_average_cost
                db.session.commit()
            
            return {
                'base_currency_cost': base_currency_cost,
                'total_base_cost': total_base_cost,
                'exchange_rate': self.get_exchange_rate(currency, self.base_currency, transaction_date)
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error calculating purchase valuation: {str(e)}")
    
    def calculate_sale_valuation(self, product_id, quantity, sale_price, currency, transaction_date):
        """Calculate COGS for sale transactions using FIFO/LIFO"""
        try:
            # Get product cost method
            product = InventoryProduct.query.get(product_id)
            if not product:
                raise Exception("Product not found")
            
            # Get current stock level
            stock_level = StockLevel.query.filter_by(product_id=product_id).first()
            if not stock_level or stock_level.quantity_on_hand < quantity:
                raise Exception("Insufficient stock for sale")
            
            # Calculate COGS based on cost method
            if product.cost_method == 'FIFO':
                cogs = self._calculate_fifo_cogs(product_id, quantity, transaction_date)
            elif product.cost_method == 'LIFO':
                cogs = self._calculate_lifo_cogs(product_id, quantity, transaction_date)
            else:  # Average cost
                cogs = stock_level.average_cost * quantity
            
            # Convert sale price to base currency for comparison
            base_currency_sale = self.convert_currency(sale_price, currency, self.base_currency, transaction_date)
            
            return {
                'cogs': cogs,
                'base_currency_sale': base_currency_sale,
                'gross_profit': (base_currency_sale * quantity) - cogs,
                'exchange_rate': self.get_exchange_rate(currency, self.base_currency, transaction_date)
            }
            
        except Exception as e:
            raise Exception(f"Error calculating sale valuation: {str(e)}")
    
    def _calculate_fifo_cogs(self, product_id, quantity, transaction_date):
        """Calculate COGS using FIFO method"""
        # Get inventory transactions in FIFO order (oldest first)
        transactions = InventoryTransaction.query.filter(
            and_(
                InventoryTransaction.product_id == product_id,
                InventoryTransaction.transaction_type.in_(['RECEIPT', 'stock_addition']),
                InventoryTransaction.transaction_date <= transaction_date
            )
        ).order_by(InventoryTransaction.transaction_date.asc()).all()
        
        remaining_quantity = quantity
        total_cogs = 0.0
        
        for transaction in transactions:
            if remaining_quantity <= 0:
                break
            
            available_quantity = min(remaining_quantity, transaction.quantity)
            total_cogs += available_quantity * transaction.base_currency_unit_cost
            remaining_quantity -= available_quantity
        
        return total_cogs
    
    def _calculate_lifo_cogs(self, product_id, quantity, transaction_date):
        """Calculate COGS using LIFO method"""
        # Get inventory transactions in LIFO order (newest first)
        transactions = InventoryTransaction.query.filter(
            and_(
                InventoryTransaction.product_id == product_id,
                InventoryTransaction.transaction_type.in_(['RECEIPT', 'stock_addition']),
                InventoryTransaction.transaction_date <= transaction_date
            )
        ).order_by(InventoryTransaction.transaction_date.desc()).all()
        
        remaining_quantity = quantity
        total_cogs = 0.0
        
        for transaction in transactions:
            if remaining_quantity <= 0:
                break
            
            available_quantity = min(remaining_quantity, transaction.quantity)
            total_cogs += available_quantity * transaction.base_currency_unit_cost
            remaining_quantity -= available_quantity
        
        return total_cogs
    
    def revalue_inventory(self, revaluation_date=None):
        """Revalue inventory holdings at month-end for unrealized gains/losses"""
        if not revaluation_date:
            revaluation_date = date.today()
        
        try:
            # Get all products with foreign currency costs
            products = InventoryProduct.query.filter(
                InventoryProduct.cost_currency != self.base_currency
            ).all()
            
            total_unrealized_gain_loss = 0.0
            
            for product in products:
                stock_level = StockLevel.query.filter_by(product_id=product.id).first()
                if not stock_level or stock_level.quantity_on_hand <= 0:
                    continue
                
                # Get current exchange rate
                current_rate = self.get_exchange_rate(product.cost_currency, self.base_currency, revaluation_date)
                
                # Calculate current value
                current_value = stock_level.quantity_on_hand * product.base_currency_cost
                
                # Calculate new value with current rate
                new_value = stock_level.quantity_on_hand * (product.current_cost * current_rate)
                
                # Calculate unrealized gain/loss
                unrealized_gain_loss = new_value - current_value
                total_unrealized_gain_loss += unrealized_gain_loss
                
                # Update product base currency cost
                product.base_currency_cost = product.current_cost * current_rate
            
            # Post unrealized gain/loss to GL
            if abs(total_unrealized_gain_loss) > 0.01:  # Only post if significant
                self._post_unrealized_gain_loss(total_unrealized_gain_loss, revaluation_date)
            
            db.session.commit()
            return {
                'total_unrealized_gain_loss': total_unrealized_gain_loss,
                'revaluation_date': revaluation_date,
                'base_currency': self.base_currency
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error revaluing inventory: {str(e)}")
    
    def _post_unrealized_gain_loss(self, amount, revaluation_date):
        """Post unrealized gain/loss to general ledger"""
        try:
            # Find or create unrealized gain/loss account
            account = ChartOfAccounts.query.filter(
                ChartOfAccounts.account_name.like('%Unrealized Gain/Loss%')
            ).first()
            
            if not account:
                # Create unrealized gain/loss account if it doesn't exist
                account = ChartOfAccounts(
                    account_code='8000',
                    account_name='Unrealized Foreign Exchange Gain/Loss',
                    account_type='Expense',
                    account_category='Other Expenses'
                )
                db.session.add(account)
                db.session.flush()
            
            # Create GL entry
            if amount > 0:
                # Unrealized gain (credit)
                entry = GeneralLedgerEntry(
                    entry_date=revaluation_date,
                    reference='INV_REVAL',
                    description=f'Unrealized foreign exchange gain - {revaluation_date}',
                    account_id=account.id,
                    credit_amount=amount,
                    debit_amount=0.0,
                    status='posted',
                    journal_type='system'
                )
            else:
                # Unrealized loss (debit)
                entry = GeneralLedgerEntry(
                    entry_date=revaluation_date,
                    reference='INV_REVAL',
                    description=f'Unrealized foreign exchange loss - {revaluation_date}',
                    account_id=account.id,
                    credit_amount=0.0,
                    debit_amount=abs(amount),
                    status='posted',
                    journal_type='system'
                )
            
            db.session.add(entry)
            
        except Exception as e:
            raise Exception(f"Error posting unrealized gain/loss: {str(e)}")
    
    def get_foreign_exchange_exposure(self):
        """Get foreign exchange exposure report"""
        try:
            # Get all products with foreign currency costs
            products = InventoryProduct.query.filter(
                InventoryProduct.cost_currency != self.base_currency
            ).all()
            
            exposure_data = []
            total_exposure = 0.0
            
            for product in products:
                stock_level = StockLevel.query.filter_by(product_id=product.id).first()
                if not stock_level or stock_level.quantity_on_hand <= 0:
                    continue
                
                # Calculate exposure
                exposure_amount = stock_level.quantity_on_hand * product.current_cost
                base_currency_value = stock_level.quantity_on_hand * product.base_currency_cost
                
                exposure_data.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'cost_currency': product.cost_currency,
                    'quantity_on_hand': stock_level.quantity_on_hand,
                    'unit_cost_foreign': product.current_cost,
                    'total_exposure_foreign': exposure_amount,
                    'total_value_base': base_currency_value,
                    'exchange_rate': self.get_exchange_rate(product.cost_currency, self.base_currency),
                    'unrealized_gain_loss': base_currency_value - exposure_amount
                })
                
                total_exposure += exposure_amount
            
            return {
                'exposure_data': exposure_data,
                'total_exposure': total_exposure,
                'base_currency': self.base_currency,
                'report_date': date.today()
            }
            
        except Exception as e:
            raise Exception(f"Error generating foreign exchange exposure: {str(e)}")
    
    def convert_all_to_new_currency(self, new_base_currency):
        """Convert all existing data to new base currency"""
        try:
            converted_records = 0
            
            # Update company settings
            settings = CompanySettings.query.filter_by(setting_key='base_currency').first()
            if settings:
                settings.setting_value = new_base_currency
                settings.updated_at = datetime.utcnow()
                converted_records += 1
            else:
                # Create new settings
                settings = CompanySettings(
                    setting_key='base_currency',
                    setting_value=new_base_currency,
                    setting_type='string',
                    description='Base currency for the company'
                )
                db.session.add(settings)
                converted_records += 1
            
            # Update base currency for this instance
            self.base_currency = new_base_currency
            
            # Convert all products to new base currency
            products = InventoryProduct.query.all()
            for product in products:
                if product.cost_currency != new_base_currency:
                    # Convert cost to new base currency
                    new_cost = self.convert_currency(
                        product.current_cost, 
                        product.cost_currency, 
                        new_base_currency, 
                        date.today()
                    )
                    product.current_cost = new_cost
                    product.cost_currency = new_base_currency
                    converted_records += 1
            
            # Convert all inventory transactions
            transactions = InventoryTransaction.query.all()
            for transaction in transactions:
                if transaction.transaction_currency and transaction.transaction_currency != new_base_currency:
                    # Convert transaction amounts
                    new_unit_cost = self.convert_currency(
                        transaction.unit_cost,
                        transaction.transaction_currency,
                        new_base_currency,
                        transaction.transaction_date
                    )
                    transaction.unit_cost = new_unit_cost
                    transaction.transaction_currency = new_base_currency
                    transaction.base_currency_unit_cost = new_unit_cost
                    transaction.base_currency_total_cost = new_unit_cost * transaction.quantity
                    converted_records += 1
            
            db.session.commit()
            
            return {
                'status': 'success',
                'converted_records': converted_records,
                'new_base_currency': new_base_currency
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error converting to new currency: {str(e)}")
