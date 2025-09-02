"""
Currency Service for Exchange Rate Management
Integrates with ExchangeRate-API (free, no API key required)
Enhanced with ChatGPT for currency insights and market analysis
"""

import requests
import logging
import os
import openai
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from app import db
from .currency_models import Currency, ExchangeRate, CurrencyConversion

# Configure logging
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class CurrencyService:
    """
    Service class for currency operations and exchange rate management
    Enhanced with AI-powered insights
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
    
    @classmethod
    def get_currency_insights(cls, base_currency: str = 'USD', target_currencies: List[str] = None) -> Dict:
        """
        Get AI-powered currency insights and market analysis
        """
        try:
            if not openai.api_key:
                return {'error': 'OpenAI API key not configured'}
            
            # Get current exchange rates
            rate_data = cls.fetch_exchange_rates(base_currency)
            if not rate_data:
                return {'error': 'Failed to fetch exchange rates'}
            
            rates = rate_data.get('rates', {})
            if target_currencies:
                rates = {k: v for k, v in rates.items() if k in target_currencies}
            
            # Prepare data for AI analysis
            rate_analysis = []
            for currency, rate in rates.items():
                if currency != base_currency:
                    currency_info = cls.POPULAR_CURRENCIES.get(currency, {})
                    rate_analysis.append({
                        'currency': currency,
                        'name': currency_info.get('name', currency),
                        'rate': rate,
                        'symbol': currency_info.get('symbol', '')
                    })
            
            # Create prompt for ChatGPT
            prompt = f"""
            Analyze the following currency exchange rates for {base_currency} as the base currency:
            
            {rate_analysis}
            
            Please provide:
            1. **Market Overview**: Brief analysis of current forex market conditions
            2. **Key Insights**: Notable trends or patterns in the rates
            3. **Risk Assessment**: Potential risks for businesses dealing with these currencies
            4. **Recommendations**: Suggestions for currency management and hedging strategies
            5. **Economic Factors**: What economic factors might be influencing these rates
            
            Keep the analysis professional, concise, and actionable for business decision-making.
            """
            
            # Get AI insights
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional currency analyst providing insights for business decision-making."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            insights = response.choices[0].message.content
            
            return {
                'base_currency': base_currency,
                'analysis_date': datetime.now().isoformat(),
                'rates_analyzed': len(rate_analysis),
                'insights': insights,
                'raw_rates': rate_analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting currency insights: {str(e)}")
            return {'error': f'Failed to get insights: {str(e)}'}
    
    @classmethod
    def get_currency_forecast(cls, from_currency: str, to_currency: str, amount: float = 1000) -> Dict:
        """
        Get AI-powered currency forecast and conversion insights
        """
        try:
            if not openai.api_key:
                return {'error': 'OpenAI API key not configured'}
            
            # Get current rate
            rate_data = cls.fetch_exchange_rates(from_currency)
            if not rate_data:
                return {'error': 'Failed to fetch exchange rates'}
            
            current_rate = rate_data.get('rates', {}).get(to_currency)
            if not current_rate:
                return {'error': f'Rate not available for {from_currency} to {to_currency}'}
            
            converted_amount = amount * current_rate
            
            # Create prompt for forecast
            prompt = f"""
            Analyze the currency conversion from {from_currency} to {to_currency}:
            
            - Amount: {amount} {from_currency}
            - Current Rate: 1 {from_currency} = {current_rate} {to_currency}
            - Converted Amount: {converted_amount:.2f} {to_currency}
            
            Please provide:
            1. **Current Market Position**: Is this a good time for this conversion?
            2. **Trend Analysis**: What's the recent trend for this currency pair?
            3. **Risk Factors**: What could affect this currency pair in the near term?
            4. **Timing Recommendations**: When might be the best time for this conversion?
            5. **Alternative Strategies**: Any hedging or timing strategies to consider?
            
            Focus on practical business advice for currency conversion decisions.
            """
            
            # Get AI forecast
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a currency trading advisor providing practical business advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            forecast = response.choices[0].message.content
            
            return {
                'from_currency': from_currency,
                'to_currency': to_currency,
                'amount': amount,
                'current_rate': current_rate,
                'converted_amount': converted_amount,
                'forecast': forecast,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting currency forecast: {str(e)}")
            return {'error': f'Failed to get forecast: {str(e)}'}
    
    @classmethod
    def get_market_sentiment(cls, currencies: List[str] = None) -> Dict:
        """
        Get AI-powered market sentiment analysis for currencies
        """
        try:
            if not openai.api_key:
                return {'error': 'OpenAI API key not configured'}
            
            if not currencies:
                currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY']
            
            # Get rates for all currencies against USD
            rate_data = cls.fetch_exchange_rates('USD')
            if not rate_data:
                return {'error': 'Failed to fetch exchange rates'}
            
            rates = rate_data.get('rates', {})
            currency_rates = {}
            
            for currency in currencies:
                if currency in rates:
                    currency_rates[currency] = rates[currency]
            
            # Create sentiment analysis prompt
            prompt = f"""
            Analyze the market sentiment for these major currencies based on their current USD exchange rates:
            
            {currency_rates}
            
            Please provide:
            1. **Overall Market Sentiment**: Bullish, Bearish, or Neutral for USD
            2. **Currency Strength Ranking**: Which currencies are strongest/weakest
            3. **Market Drivers**: What's driving current currency movements
            4. **Risk Assessment**: Which currencies pose the highest risk
            5. **Opportunity Analysis**: Where are the best opportunities for currency operations
            
            Provide a concise, professional analysis suitable for business decision-making.
            """
            
            # Get AI sentiment analysis
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a forex market analyst providing sentiment analysis for business clients."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.6
            )
            
            sentiment = response.choices[0].message.content
            
            return {
                'currencies_analyzed': currencies,
                'rates': currency_rates,
                'sentiment_analysis': sentiment,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting market sentiment: {str(e)}")
            return {'error': f'Failed to get sentiment: {str(e)}'}

