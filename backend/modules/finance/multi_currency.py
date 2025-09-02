from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import json

class MultiCurrency:
    """Comprehensive Multi-Currency Support System"""
    
    def __init__(self):
        self.exchange_rates = []
        self.currencies = {
            'USD': {
                'code': 'USD',
                'name': 'US Dollar',
                'symbol': '$',
                'is_base': True,
                'decimal_places': 2
            },
            'EUR': {
                'code': 'EUR',
                'name': 'Euro',
                'symbol': '€',
                'is_base': False,
                'decimal_places': 2
            },
            'GBP': {
                'code': 'GBP',
                'name': 'British Pound',
                'symbol': '£',
                'is_base': False,
                'decimal_places': 2
            },
            'JPY': {
                'code': 'JPY',
                'name': 'Japanese Yen',
                'symbol': '¥',
                'is_base': False,
                'decimal_places': 0
            },
            'CAD': {
                'code': 'CAD',
                'name': 'Canadian Dollar',
                'symbol': 'C$',
                'is_base': False,
                'decimal_places': 2
            },
            'AUD': {
                'code': 'AUD',
                'name': 'Australian Dollar',
                'symbol': 'A$',
                'is_base': False,
                'decimal_places': 2
            }
        }
        
        self.base_currency = 'USD'
        self._initialize_exchange_rates()
    
    def _initialize_exchange_rates(self):
        """
        Initialize sample exchange rates
        """
        base_date = datetime.now()
        
        # Sample exchange rates (mock data - replace with real API)
        sample_rates = [
            {'from_currency': 'EUR', 'to_currency': 'USD', 'rate': 1.18, 'date': base_date},
            {'from_currency': 'GBP', 'to_currency': 'USD', 'rate': 1.35, 'date': base_date},
            {'from_currency': 'JPY', 'to_currency': 'USD', 'rate': 0.0091, 'date': base_date},
            {'from_currency': 'CAD', 'to_currency': 'USD', 'rate': 0.79, 'date': base_date},
            {'from_currency': 'AUD', 'to_currency': 'USD', 'rate': 0.73, 'date': base_date},
            {'from_currency': 'USD', 'to_currency': 'EUR', 'rate': 0.85, 'date': base_date},
            {'from_currency': 'USD', 'to_currency': 'GBP', 'rate': 0.74, 'date': base_date},
            {'from_currency': 'USD', 'to_currency': 'JPY', 'rate': 110.0, 'date': base_date},
            {'from_currency': 'USD', 'to_currency': 'CAD', 'rate': 1.27, 'date': base_date},
            {'from_currency': 'USD', 'to_currency': 'AUD', 'rate': 1.37, 'date': base_date}
        ]
        
        for rate_data in sample_rates:
            self.add_exchange_rate(
                rate_data['from_currency'],
                rate_data['to_currency'],
                rate_data['rate'],
                rate_data['date']
            )
    
    def add_exchange_rate(self, from_currency: str, to_currency: str, rate: float, date: datetime = None) -> Dict:
        """
        Add a new exchange rate
        """
        try:
            if not date:
                date = datetime.now()
            
            # Validate currencies
            if from_currency not in self.currencies or to_currency not in self.currencies:
                return {
                    'success': False,
                    'error': f'Invalid currency: {from_currency} or {to_currency}'
                }
            
            # Check if rate already exists for this date
            existing_rate = self.get_exchange_rate(from_currency, to_currency, date)
            if existing_rate:
                # Update existing rate
                existing_rate['rate'] = rate
                existing_rate['updated_date'] = datetime.now()
            else:
                # Add new rate
                rate_record = {
                    'id': f"RATE-{len(self.exchange_rates) + 1}",
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'rate': rate,
                    'date': date,
                    'created_date': datetime.now(),
                    'updated_date': datetime.now()
                }
                self.exchange_rates.append(rate_record)
            
            return {
                'success': True,
                'message': f'Exchange rate {from_currency}/{to_currency} = {rate} added successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error adding exchange rate: {str(e)}'
            }
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, date: datetime = None) -> Optional[Dict]:
        """
        Get exchange rate for specific currencies and date
        """
        if not date:
            date = datetime.now()
        
        # Find exact match
        for rate in self.exchange_rates:
            if (rate['from_currency'] == from_currency and 
                rate['to_currency'] == to_currency and 
                rate['date'].date() == date.date()):
                return rate
        
        # If no exact match, find closest date
        closest_rate = None
        min_date_diff = float('inf')
        
        for rate in self.exchange_rates:
            if (rate['from_currency'] == from_currency and 
                rate['to_currency'] == to_currency):
                date_diff = abs((rate['date'] - date).days)
                if date_diff < min_date_diff:
                    min_date_diff = date_diff
                    closest_rate = rate
        
        return closest_rate
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str, date: datetime = None) -> Dict:
        """
        Convert amount from one currency to another
        """
        try:
            if from_currency == to_currency:
                return {
                    'success': True,
                    'original_amount': amount,
                    'converted_amount': amount,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'exchange_rate': 1.0,
                    'conversion_date': date or datetime.now()
                }
            
            # Get exchange rate
            rate_record = self.get_exchange_rate(from_currency, to_currency, date)
            if not rate_record:
                return {
                    'success': False,
                    'error': f'Exchange rate not found for {from_currency}/{to_currency}'
                }
            
            # Calculate conversion
            converted_amount = amount * rate_record['rate']
            
            return {
                'success': True,
                'original_amount': amount,
                'converted_amount': converted_amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'exchange_rate': rate_record['rate'],
                'conversion_date': rate_record['date'],
                'rate_id': rate_record['id']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error converting amount: {str(e)}'
            }
    
    def post_exchange_gains_losses(self, transaction_data: Dict) -> Dict:
        """
        Post exchange gains/losses during bank reconciliation
        """
        try:
            # Import the auto journal engine
            from modules.integration.auto_journal import auto_journal_engine
            
            original_amount = transaction_data.get('original_amount', 0)
            converted_amount = transaction_data.get('converted_amount', 0)
            from_currency = transaction_data.get('from_currency', '')
            to_currency = transaction_data.get('to_currency', '')
            
            # Calculate gain/loss
            gain_loss = converted_amount - original_amount
            
            if abs(gain_loss) < 0.01:  # No significant gain/loss
                return {
                    'success': True,
                    'message': 'No significant exchange gain/loss to post',
                    'gain_loss': 0
                }
            
            # Create journal entry data
            je_data = {
                'transaction_date': transaction_data.get('transaction_date', datetime.now()),
                'reference': f"FX-{transaction_data.get('reference', '')}",
                'description': f"Exchange {'Gain' if gain_loss > 0 else 'Loss'} - {from_currency} to {to_currency}",
                'amount': abs(gain_loss),
                'gain_loss_type': 'gain' if gain_loss > 0 else 'loss',
                'from_currency': from_currency,
                'to_currency': to_currency,
                'exchange_rate': transaction_data.get('exchange_rate', 0)
            }
            
            # Post journal entry
            result = auto_journal_engine.on_exchange_gain_loss(je_data)
            
            return {
                'success': result['success'],
                'gain_loss': gain_loss,
                'journal_entry_id': result.get('journal_entry_id'),
                'message': f"Exchange {'gain' if gain_loss > 0 else 'loss'} of {abs(gain_loss):.2f} posted"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error posting exchange gains/losses: {str(e)}'
            }
    
    def get_currency_list(self) -> List[Dict]:
        """
        Get list of supported currencies
        """
        return list(self.currencies.values())
    
    def get_exchange_rate_history(self, from_currency: str, to_currency: str, days: int = 30) -> List[Dict]:
        """
        Get exchange rate history for specified currencies
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        history = []
        for rate in self.exchange_rates:
            if (rate['from_currency'] == from_currency and 
                rate['to_currency'] == to_currency and
                start_date <= rate['date'] <= end_date):
                history.append(rate)
        
        return sorted(history, key=lambda x: x['date'])
    
    def calculate_currency_exposure(self, as_of_date: datetime = None) -> Dict:
        """
        Calculate currency exposure for the organization
        """
        if not as_of_date:
            as_of_date = datetime.now()
        
        # Mock data - replace with actual database queries
        exposure_data = {
            'USD': {
                'assets': 1000000.00,
                'liabilities': 500000.00,
                'net_exposure': 500000.00
            },
            'EUR': {
                'assets': 750000.00,
                'liabilities': 300000.00,
                'net_exposure': 450000.00
            },
            'GBP': {
                'assets': 500000.00,
                'liabilities': 200000.00,
                'net_exposure': 300000.00
            }
        }
        
        # Convert all to base currency
        total_exposure_base = 0
        for currency, data in exposure_data.items():
            if currency != self.base_currency:
                conversion = self.convert_amount(data['net_exposure'], currency, self.base_currency, as_of_date)
                if conversion['success']:
                    total_exposure_base += conversion['converted_amount']
            else:
                total_exposure_base += data['net_exposure']
        
        return {
            'as_of_date': as_of_date,
            'base_currency': self.base_currency,
            'currency_exposures': exposure_data,
            'total_exposure_base_currency': total_exposure_base,
            'risk_assessment': self._assess_currency_risk(total_exposure_base)
        }
    
    def _assess_currency_risk(self, total_exposure: float) -> Dict:
        """
        Assess currency risk based on total exposure
        """
        if total_exposure < 100000:
            risk_level = 'low'
            risk_score = 1
        elif total_exposure < 500000:
            risk_level = 'medium'
            risk_score = 2
        else:
            risk_level = 'high'
            risk_score = 3
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'recommendations': self._get_risk_recommendations(risk_level)
        }
    
    def _get_risk_recommendations(self, risk_level: str) -> List[str]:
        """
        Get recommendations based on risk level
        """
        recommendations = {
            'low': [
                'Monitor currency movements regularly',
                'Consider hedging for large transactions'
            ],
            'medium': [
                'Implement currency hedging strategies',
                'Set up automated exchange rate monitoring',
                'Review exposure monthly'
            ],
            'high': [
                'Implement comprehensive hedging program',
                'Set up daily currency monitoring',
                'Consider currency diversification',
                'Review exposure weekly',
                'Consult with currency risk management experts'
            ]
        }
        
        return recommendations.get(risk_level, [])
    
    def get_currency_performance(self, currency: str, days: int = 30) -> Dict:
        """
        Get currency performance metrics
        """
        try:
            if currency not in self.currencies:
                return {
                    'success': False,
                    'error': f'Currency {currency} not supported'
                }
            
            # Get exchange rate history against base currency
            history = self.get_exchange_rate_history(currency, self.base_currency, days)
            
            if not history:
                return {
                    'success': False,
                    'error': f'No exchange rate history found for {currency}'
                }
            
            # Calculate performance metrics
            rates = [rate['rate'] for rate in history]
            current_rate = rates[-1]
            start_rate = rates[0]
            
            performance = {
                'currency': currency,
                'base_currency': self.base_currency,
                'current_rate': current_rate,
                'start_rate': start_rate,
                'change_amount': current_rate - start_rate,
                'change_percentage': ((current_rate - start_rate) / start_rate * 100) if start_rate > 0 else 0,
                'highest_rate': max(rates),
                'lowest_rate': min(rates),
                'average_rate': sum(rates) / len(rates),
                'volatility': self._calculate_volatility(rates),
                'trend': 'up' if current_rate > start_rate else 'down' if current_rate < start_rate else 'stable'
            }
            
            return {
                'success': True,
                'performance': performance
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error calculating currency performance: {str(e)}'
            }
    
    def _calculate_volatility(self, rates: List[float]) -> float:
        """
        Calculate volatility (standard deviation) of exchange rates
        """
        if len(rates) < 2:
            return 0
        
        mean = sum(rates) / len(rates)
        variance = sum((rate - mean) ** 2 for rate in rates) / (len(rates) - 1)
        return variance ** 0.5

# Global instance
multi_currency = MultiCurrency()



