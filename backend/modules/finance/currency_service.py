"""
Currency Service for Exchange Rate Management
Integrates with ExchangeRate-API (free, no API key required)
"""

import requests
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from app import db
from .currency_models import Currency, ExchangeRate, CurrencyConversion

# Configure logging
logger = logging.getLogger(__name__)

class CurrencyService:
    """
    Service class for currency operations and exchange rate management
    """
    
    # ExchangeRate-API endpoints (free, no API key needed)
    BASE_URL = "https://api.exchangerate-api.com/v4"
    LATEST_URL = f"{BASE_URL}/latest"
    
    # Popular currencies with their details
    POPULAR_CURRENCIES = {
        'USD': {'name': 'US Dollar', 'symbol': '$', 'country': 'United States'},
        'EUR': {'name': 'Euro', 'symbol': '€', 'country': 'European Union'},
        'GBP': {'name': 'British Pound', 'symbol': '£', 'country': 'United Kingdom'},
        'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'country': 'Japan'},
        'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'country': 'Canada'},
        'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'country': 'Australia'},
        'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr', 'country': 'Switzerland'},
        'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'country': 'China'},
        'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'country': 'India'},
        'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'country': 'South Korea'},
        'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'country': 'Brazil'},
        'MXN': {'name': 'Mexican Peso', 'symbol': '$', 'country': 'Mexico'},
        'SGD': {'name': 'Singapore Dollar', 'symbol': 'S$', 'country': 'Singapore'},
        'HKD': {'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'country': 'Hong Kong'},
        'NOK': {'name': 'Norwegian Krone', 'symbol': 'kr', 'country': 'Norway'},
        'SEK': {'name': 'Swedish Krona', 'symbol': 'kr', 'country': 'Sweden'},
        'DKK': {'name': 'Danish Krone', 'symbol': 'kr', 'country': 'Denmark'},
        'PLN': {'name': 'Polish Złoty', 'symbol': 'zł', 'country': 'Poland'},
        'CZK': {'name': 'Czech Koruna', 'symbol': 'Kč', 'country': 'Czech Republic'},
        'HUF': {'name': 'Hungarian Forint', 'symbol': 'Ft', 'country': 'Hungary'}
    }
    
    @classmethod
    def initialize_currencies(cls) -> bool:
        """
        Initialize the currency table with popular currencies
        """
        try:
            logger.info("🌍 Initializing currency database...")
            
            for code, details in cls.POPULAR_CURRENCIES.items():
                existing = Currency.query.filter_by(code=code).first()
                if not existing:
                    currency = Currency(
                        code=code,
                        name=details['name'],
                        symbol=details['symbol'],
                        country=details['country'],
                        is_active=True,
                        is_base_currency=(code == 'USD')  # Default to USD as base
                    )
                    db.session.add(currency)
                    logger.info(f"💰 Added currency: {code} - {details['name']}")
            
            db.session.commit()
            logger.info("✅ Currency initialization completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Currency initialization failed: {str(e)}")
            db.session.rollback()
            return False
    
    @classmethod
    def fetch_exchange_rates(cls, base_currency: str = 'USD') -> Optional[Dict]:
        """
        Fetch latest exchange rates from ExchangeRate-API
        """
        try:
            url = f"{cls.LATEST_URL}/{base_currency}"
            logger.info(f"🔄 Fetching exchange rates from: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Successfully fetched rates for {len(data.get('rates', {}))} currencies")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to fetch exchange rates: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching rates: {str(e)}")
            return None
    
    @classmethod
    def update_exchange_rates(cls, base_currency_code: str = 'USD') -> bool:
        """
        Update exchange rates in database from API
        """
        try:
            # Fetch latest rates
            rate_data = cls.fetch_exchange_rates(base_currency_code)
            if not rate_data:
                return False
            
            base_currency = Currency.query.filter_by(code=base_currency_code).first()
            if not base_currency:
                logger.error(f"❌ Base currency {base_currency_code} not found in database")
                return False
            
            rates = rate_data.get('rates', {})
            rate_date = datetime.now(timezone.utc)
            
            # Mark all current rates as non-current for this base currency
            ExchangeRate.query.filter_by(
                from_currency_id=base_currency.id,
                is_current=True
            ).update({'is_current': False})
            
            updated_count = 0
            
            for to_currency_code, rate in rates.items():
                # Skip self-conversion
                if to_currency_code == base_currency_code:
                    continue
                
                to_currency = Currency.query.filter_by(code=to_currency_code).first()
                if not to_currency:
                    continue
                
                # Create new exchange rate record
                exchange_rate = ExchangeRate(
                    from_currency_id=base_currency.id,
                    to_currency_id=to_currency.id,
                    rate=float(rate),
                    inverse_rate=1.0 / float(rate),
                    date=rate_date,
                    source='ExchangeRate-API',
                    is_current=True
                )
                
                db.session.add(exchange_rate)
                updated_count += 1
            
            # Also create inverse rates (to -> base)
            for to_currency_code, rate in rates.items():
                if to_currency_code == base_currency_code:
                    continue
                
                to_currency = Currency.query.filter_by(code=to_currency_code).first()
                if not to_currency:
                    continue
                
                # Mark old inverse rates as non-current
                ExchangeRate.query.filter_by(
                    from_currency_id=to_currency.id,
                    to_currency_id=base_currency.id,
                    is_current=True
                ).update({'is_current': False})
                
                # Create inverse rate (to_currency -> base_currency)
                inverse_exchange_rate = ExchangeRate(
                    from_currency_id=to_currency.id,
                    to_currency_id=base_currency.id,
                    rate=1.0 / float(rate),
                    inverse_rate=float(rate),
                    date=rate_date,
                    source='ExchangeRate-API',
                    is_current=True
                )
                
                db.session.add(inverse_exchange_rate)
                updated_count += 1
            
            db.session.commit()
            logger.info(f"✅ Successfully updated {updated_count} exchange rates")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update exchange rates: {str(e)}")
            db.session.rollback()
            return False
    
    @classmethod
    def convert_currency(cls, amount: float, from_currency_code: str, 
                        to_currency_code: str, record_conversion: bool = True) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert amount between currencies
        Returns: (converted_amount, exchange_rate_used)
        """
        try:
            if from_currency_code == to_currency_code:
                return amount, 1.0
            
            # Get currencies
            from_currency = Currency.query.filter_by(code=from_currency_code).first()
            to_currency = Currency.query.filter_by(code=to_currency_code).first()
            
            if not from_currency or not to_currency:
                logger.error(f"❌ Currency not found: {from_currency_code} or {to_currency_code}")
                return None, None
            
            # Get current exchange rate
            exchange_rate = ExchangeRate.query.filter_by(
                from_currency_id=from_currency.id,
                to_currency_id=to_currency.id,
                is_current=True
            ).first()
            
            if not exchange_rate:
                logger.error(f"❌ No exchange rate found for {from_currency_code} -> {to_currency_code}")
                return None, None
            
            converted_amount = amount * exchange_rate.rate
            
            # Record conversion if requested
            if record_conversion:
                conversion = CurrencyConversion(
                    from_currency_id=from_currency.id,
                    to_currency_id=to_currency.id,
                    original_amount=amount,
                    converted_amount=converted_amount,
                    exchange_rate=exchange_rate.rate,
                    reference_type='api_conversion'
                )
                db.session.add(conversion)
                db.session.commit()
            
            return converted_amount, exchange_rate.rate
            
        except Exception as e:
            logger.error(f"❌ Currency conversion failed: {str(e)}")
            return None, None
    
    @classmethod
    def get_currency_list(cls, active_only: bool = True) -> List[Dict]:
        """
        Get list of all currencies
        """
        query = Currency.query
        if active_only:
            query = query.filter_by(is_active=True)
        
        currencies = query.order_by(Currency.code).all()
        return [currency.to_dict() for currency in currencies]
    
    @classmethod
    def set_base_currency(cls, currency_code: str) -> bool:
        """
        Set a currency as the company's base currency
        """
        try:
            # Remove base currency flag from all currencies
            Currency.query.filter_by(is_base_currency=True).update({'is_base_currency': False})
            
            # Set new base currency
            currency = Currency.query.filter_by(code=currency_code).first()
            if not currency:
                logger.error(f"❌ Currency {currency_code} not found")
                return False
            
            currency.is_base_currency = True
            db.session.commit()
            
            logger.info(f"✅ Set {currency_code} as base currency")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set base currency: {str(e)}")
            db.session.rollback()
            return False
    
    @classmethod
    def get_exchange_rate_history(cls, from_currency_code: str, 
                                 to_currency_code: str, days: int = 30) -> List[Dict]:
        """
        Get historical exchange rates for analytics
        """
        try:
            from_currency = Currency.query.filter_by(code=from_currency_code).first()
            to_currency = Currency.query.filter_by(code=to_currency_code).first()
            
            if not from_currency or not to_currency:
                return []
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            rates = ExchangeRate.query.filter_by(
                from_currency_id=from_currency.id,
                to_currency_id=to_currency.id
            ).filter(
                ExchangeRate.date >= cutoff_date
            ).order_by(ExchangeRate.date.desc()).all()
            
            return [rate.to_dict() for rate in rates]
            
        except Exception as e:
            logger.error(f"❌ Failed to get exchange rate history: {str(e)}")
            return []

