"""
AI Analytics Service for Financial Insights
Uses ChatGPT API for intelligent financial analysis and predictions
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import openai
from sqlalchemy import func, and_
from app import db
from .advanced_models import (
    ChartOfAccounts, GeneralLedgerEntry
)
from modules.inventory.advanced_models import InventoryProduct, InventoryTransaction, StockLevel

# Configure logging
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_ai_insights(analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic AI insights function that can be used across modules
    """
    try:
        if analysis_type == 'inventory_trends':
            return _generate_inventory_trend_insights(data)
        elif analysis_type == 'inventory_stock_levels':
            return _generate_stock_level_insights(data)
        elif analysis_type == 'inventory_movement':
            return _generate_movement_insights(data)
        else:
            return _generate_general_insights(data)
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return {
            'insights': f"AI analysis temporarily unavailable: {str(e)}",
            'recommendations': ['Please try again later'],
            'risk_level': 'unknown'
        }

def _generate_inventory_trend_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate insights for inventory trends"""
    trends_data = data.get('trends_data', [])
    total_days = data.get('total_days', 30)
    total_transactions = data.get('total_transactions', 0)
    
    if not trends_data:
        return {
            'insights': 'No trend data available for analysis',
            'recommendations': ['Add more inventory transactions to see trends'],
            'risk_level': 'low'
        }
    
    # Calculate basic metrics
    total_inbound = sum(item['inbound'] for item in trends_data)
    total_outbound = sum(item['outbound'] for item in trends_data)
    avg_daily_transactions = total_transactions / total_days if total_days > 0 else 0
    
    insights = f"Over the past {total_days} days, inventory shows "
    if total_inbound > total_outbound:
        insights += f"positive growth with {total_inbound - total_outbound} more units inbound than outbound. "
    else:
        insights += f"declining stock with {total_outbound - total_inbound} more units outbound than inbound. "
    
    insights += f"Average daily transactions: {avg_daily_transactions:.1f}"
    
    recommendations = []
    if total_outbound > total_inbound * 1.2:
        recommendations.append("Consider increasing reorder quantities to prevent stockouts")
    if avg_daily_transactions < 5:
        recommendations.append("Monitor inventory activity - low transaction volume detected")
    
    risk_level = 'medium'
    if total_outbound > total_inbound * 1.5:
        risk_level = 'high'
    elif total_inbound > total_outbound * 1.2:
        risk_level = 'low'
    
    return {
        'insights': insights,
        'recommendations': recommendations,
        'risk_level': risk_level,
        'metrics': {
            'total_inbound': total_inbound,
            'total_outbound': total_outbound,
            'net_movement': total_inbound - total_outbound,
            'avg_daily_transactions': avg_daily_transactions
        }
    }

def _generate_stock_level_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate insights for stock levels"""
    total_products = data.get('total_products', 0)
    low_stock_items = data.get('low_stock_items', 0)
    total_value = data.get('total_value', 0)
    
    if total_products == 0:
        return {
            'insights': 'No inventory data available for analysis',
            'recommendations': ['Add products to inventory to start tracking'],
            'risk_level': 'low'
        }
    
    low_stock_percentage = (low_stock_items / total_products * 100) if total_products > 0 else 0
    
    insights = f"Current inventory status: {total_products} products with total value ${total_value:,.2f}. "
    insights += f"{low_stock_percentage:.1f}% of products are below reorder point."
    
    recommendations = []
    if low_stock_percentage > 20:
        recommendations.append("High number of low stock items - review reorder points")
        recommendations.append("Consider bulk ordering for frequently low items")
    elif low_stock_percentage > 10:
        recommendations.append("Monitor low stock items and adjust reorder points")
    else:
        recommendations.append("Stock levels appear healthy - continue monitoring")
    
    risk_level = 'low'
    if low_stock_percentage > 30:
        risk_level = 'high'
    elif low_stock_percentage > 15:
        risk_level = 'medium'
    
    return {
        'insights': insights,
        'recommendations': recommendations,
        'risk_level': risk_level,
        'metrics': {
            'total_products': total_products,
            'low_stock_items': low_stock_items,
            'low_stock_percentage': low_stock_percentage,
            'total_value': total_value
        }
    }

def _generate_movement_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate insights for inventory movement"""
    total_transactions = data.get('total_transactions', 0)
    inbound_value = data.get('inbound_value', 0)
    outbound_value = data.get('outbound_value', 0)
    period_days = data.get('period_days', 30)
    
    if total_transactions == 0:
        return {
            'insights': 'No movement data available for analysis',
            'recommendations': ['Add inventory transactions to see movement patterns'],
            'risk_level': 'low'
        }
    
    net_movement = inbound_value - outbound_value
    avg_daily_transactions = total_transactions / period_days if period_days > 0 else 0
    
    insights = f"Movement analysis for {period_days} days: {total_transactions} transactions. "
    if net_movement > 0:
        insights += f"Net positive movement of ${net_movement:,.2f} (inbound: ${inbound_value:,.2f}, outbound: ${outbound_value:,.2f}). "
    else:
        insights += f"Net negative movement of ${abs(net_movement):,.2f} (inbound: ${inbound_value:,.2f}, outbound: ${outbound_value:,.2f}). "
    
    insights += f"Average {avg_daily_transactions:.1f} transactions per day."
    
    recommendations = []
    if outbound_value > inbound_value * 1.3:
        recommendations.append("High outbound activity - ensure adequate stock levels")
    if avg_daily_transactions < 2:
        recommendations.append("Low transaction volume - review inventory processes")
    if inbound_value > outbound_value * 2:
        recommendations.append("High inbound activity - monitor storage capacity")
    
    risk_level = 'medium'
    if outbound_value > inbound_value * 1.5:
        risk_level = 'high'
    elif inbound_value > outbound_value * 1.5:
        risk_level = 'low'
    
    return {
        'insights': insights,
        'recommendations': recommendations,
        'risk_level': risk_level,
        'metrics': {
            'total_transactions': total_transactions,
            'inbound_value': inbound_value,
            'outbound_value': outbound_value,
            'net_movement': net_movement,
            'avg_daily_transactions': avg_daily_transactions
        }
    }

def _generate_general_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate general insights for any data"""
    return {
        'insights': 'AI analysis completed successfully',
        'recommendations': ['Continue monitoring inventory performance'],
        'risk_level': 'low',
        'metrics': data
    }

class AIAnalyticsService:
    """
    AI-powered financial analytics and insights service
    """
    
    @classmethod
    def get_financial_insights(cls, analysis_type: str = 'general') -> Dict[str, Any]:
        """
        Get AI-powered financial insights
        """
        try:
            # Gather financial data
            financial_data = cls._gather_financial_data()
            
            # Generate AI insights
            insights = cls._generate_ai_insights(financial_data, analysis_type)
            
            return {
                'status': 'success',
                'analysis_type': analysis_type,
                'insights': insights,
                'data_summary': financial_data['summary'],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating financial insights: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @classmethod
    def get_inventory_insights(cls) -> Dict[str, Any]:
        """
        Get AI-powered inventory insights and recommendations
        """
        try:
            # Gather inventory data
            inventory_data = cls._gather_inventory_data()
            
            # Generate AI insights
            insights = cls._generate_inventory_insights(inventory_data)
            
            return {
                'status': 'success',
                'insights': insights,
                'data_summary': inventory_data['summary'],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating inventory insights: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @classmethod
    def get_market_trends(cls, currency: str = 'USD') -> Dict[str, Any]:
        """
        Get AI-powered market trend analysis
        """
        try:
            # Gather market data
            market_data = cls._gather_market_data(currency)
            
            # Generate AI insights
            insights = cls._generate_market_insights(market_data)
            
            return {
                'status': 'success',
                'currency': currency,
                'insights': insights,
                'data_summary': market_data['summary'],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating market trends: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @classmethod
    def _gather_financial_data(cls) -> Dict[str, Any]:
        """
        Gather comprehensive financial data for analysis
        """
        try:
            # Get account balances
            account_balances = db.session.query(
                ChartOfAccounts.account_code,
                ChartOfAccounts.account_name,
                ChartOfAccounts.account_type,
                func.sum(GeneralLedgerEntry.debit_amount).label('total_debits'),
                func.sum(GeneralLedgerEntry.credit_amount).label('total_credits')
            ).join(GeneralLedgerEntry).group_by(
                ChartOfAccounts.id
            ).all()
            
            # Get recent transactions
            recent_transactions = GeneralLedgerEntry.query.order_by(
                GeneralLedgerEntry.entry_date.desc()
            ).limit(50).all()
            
            # Calculate key metrics
            total_assets = sum([acc.total_credits - acc.total_debits for acc in account_balances if acc.account_type == 'asset'])
            total_liabilities = sum([acc.total_debits - acc.total_credits for acc in account_balances if acc.account_type == 'liability'])
            total_equity = sum([acc.total_credits - acc.total_debits for acc in account_balances if acc.account_type == 'equity'])
            
            return {
                'account_balances': [{
                    'code': acc.account_code,
                    'name': acc.account_name,
                    'type': acc.account_type,
                    'debits': float(acc.total_debits or 0),
                    'credits': float(acc.total_credits or 0),
                    'balance': float((acc.total_credits or 0) - (acc.total_debits or 0))
                } for acc in account_balances],
                'recent_transactions': [{
                    'date': trans.entry_date.isoformat(),
                    'description': trans.description,
                    'debit': float(trans.debit_amount or 0),
                    'credit': float(trans.credit_amount or 0),
                    'account': trans.account.account_name if trans.account else 'Unknown'
                } for trans in recent_transactions],
                'summary': {
                    'total_assets': total_assets,
                    'total_liabilities': total_liabilities,
                    'total_equity': total_equity,
                    'net_worth': total_assets - total_liabilities,
                    'debt_to_equity_ratio': total_liabilities / total_equity if total_equity > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error gathering financial data: {str(e)}")
            return {'summary': {}, 'account_balances': [], 'recent_transactions': []}
    
    @classmethod
    def _gather_inventory_data(cls) -> Dict[str, Any]:
        """
        Gather comprehensive inventory data for analysis
        """
        try:
            # Get stock levels
            stock_levels = StockLevel.query.all()
            
            # Get recent transactions
            recent_transactions = AdvancedInventoryTransaction.query.order_by(
                AdvancedInventoryTransaction.transaction_date.desc()
            ).limit(100).all()
            
            # Calculate metrics
            total_products = AdvancedProduct.query.filter_by(is_active=True).count()
            low_stock_products = [sl for sl in stock_levels if sl.quantity_on_hand <= sl.product.min_stock_level]
            out_of_stock_products = [sl for sl in stock_levels if sl.quantity_on_hand == 0]
            
            total_inventory_value = sum([sl.total_value for sl in stock_levels])
            
            return {
                'stock_levels': [{
                    'product_name': sl.product.name,
                    'sku': sl.product.sku,
                    'quantity_on_hand': sl.quantity_on_hand,
                    'quantity_committed': sl.quantity_committed,
                    'quantity_available': sl.quantity_available,
                    'unit_cost': float(sl.unit_cost or 0),
                    'total_value': float(sl.total_value or 0),
                    'min_stock': sl.product.min_stock_level,
                    'max_stock': sl.product.max_stock_level
                } for sl in stock_levels],
                'recent_transactions': [{
                    'date': trans.transaction_date.isoformat(),
                    'type': trans.transaction_type,
                    'product': trans.product.name,
                    'quantity': trans.quantity,
                    'unit_cost': float(trans.unit_cost or 0),
                    'total_cost': float(trans.total_cost or 0)
                } for trans in recent_transactions],
                'summary': {
                    'total_products': total_products,
                    'low_stock_count': len(low_stock_products),
                    'out_of_stock_count': len(out_of_stock_products),
                    'total_inventory_value': total_inventory_value,
                    'average_stock_level': sum([sl.quantity_on_hand for sl in stock_levels]) / len(stock_levels) if stock_levels else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error gathering inventory data: {str(e)}")
            return {'summary': {}, 'stock_levels': [], 'recent_transactions': []}
    
    @classmethod
    def _gather_market_data(cls, currency: str) -> Dict[str, Any]:
        """
        Gather market data for trend analysis
        """
        try:
            # Get exchange rates (if available)
            from .currency_service import CurrencyService
            exchange_rates = CurrencyService.fetch_exchange_rates(currency)
            
            # Get recent financial performance
            recent_performance = cls._get_recent_performance()
            
            return {
                'exchange_rates': exchange_rates,
                'recent_performance': recent_performance,
                'summary': {
                    'base_currency': currency,
                    'analysis_date': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error gathering market data: {str(e)}")
            return {'summary': {}, 'exchange_rates': {}, 'recent_performance': {}}
    
    @classmethod
    def _generate_ai_insights(cls, data: Dict, analysis_type: str) -> Dict[str, Any]:
        """
        Generate AI insights using ChatGPT
        """
        try:
            # Prepare prompt
            prompt = cls._create_financial_prompt(data, analysis_type)
            
            # Call ChatGPT API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert. Provide clear, actionable insights based on the financial data provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            insights = response.choices[0].message.content
            
            return {
                'analysis': insights,
                'key_metrics': cls._extract_key_metrics(data),
                'recommendations': cls._generate_recommendations(data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating AI insights: {str(e)}")
            return {
                'analysis': 'Unable to generate AI insights at this time.',
                'key_metrics': {},
                'recommendations': []
            }
    
    @classmethod
    def _generate_inventory_insights(cls, data: Dict) -> Dict[str, Any]:
        """
        Generate AI insights for inventory management
        """
        try:
            prompt = f"""
            Analyze this inventory data and provide insights:
            
            Summary:
            - Total Products: {data['summary'].get('total_products', 0)}
            - Low Stock Items: {data['summary'].get('low_stock_count', 0)}
            - Out of Stock Items: {data['summary'].get('out_of_stock_count', 0)}
            - Total Inventory Value: ${data['summary'].get('total_inventory_value', 0):,.2f}
            
            Provide:
            1. Key insights about inventory health
            2. Recommendations for stock management
            3. Potential cost savings opportunities
            4. Risk assessment
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an inventory management expert. Provide practical insights and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return {
                'analysis': response.choices[0].message.content,
                'low_stock_alerts': cls._identify_low_stock_items(data),
                'optimization_opportunities': cls._identify_optimization_opportunities(data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating inventory insights: {str(e)}")
            return {
                'analysis': 'Unable to generate inventory insights at this time.',
                'low_stock_alerts': [],
                'optimization_opportunities': []
            }
    
    @classmethod
    def _generate_market_insights(cls, data: Dict) -> Dict[str, Any]:
        """
        Generate AI insights for market trends
        """
        try:
            prompt = f"""
            Analyze market trends based on this data:
            
            Base Currency: {data['summary'].get('base_currency', 'USD')}
            Exchange Rates: {json.dumps(data.get('exchange_rates', {}), indent=2)}
            
            Provide:
            1. Currency trend analysis
            2. Market volatility assessment
            3. Risk factors to consider
            4. Strategic recommendations
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a market analyst expert. Provide currency and market trend insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return {
                'analysis': response.choices[0].message.content,
                'trend_indicators': cls._calculate_trend_indicators(data),
                'risk_assessment': cls._assess_market_risks(data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating market insights: {str(e)}")
            return {
                'analysis': 'Unable to generate market insights at this time.',
                'trend_indicators': {},
                'risk_assessment': {}
            }
    
    @classmethod
    def _create_financial_prompt(cls, data: Dict, analysis_type: str) -> str:
        """
        Create a prompt for financial analysis
        """
        summary = data.get('summary', {})
        
        if analysis_type == 'general':
            return f"""
            Analyze this financial data and provide insights:
            
            Financial Summary:
            - Total Assets: ${summary.get('total_assets', 0):,.2f}
            - Total Liabilities: ${summary.get('total_liabilities', 0):,.2f}
            - Total Equity: ${summary.get('total_equity', 0):,.2f}
            - Net Worth: ${summary.get('net_worth', 0):,.2f}
            - Debt-to-Equity Ratio: {summary.get('debt_to_equity_ratio', 0):.2f}
            
            Provide:
            1. Financial health assessment
            2. Key performance indicators
            3. Areas of concern
            4. Strategic recommendations
            5. Risk assessment
            """
        else:
            return f"Analyze the financial data for {analysis_type} focus and provide specific insights."
    
    @classmethod
    def _extract_key_metrics(cls, data: Dict) -> Dict[str, Any]:
        """
        Extract key financial metrics
        """
        summary = data.get('summary', {})
        return {
            'net_worth': summary.get('net_worth', 0),
            'debt_to_equity_ratio': summary.get('debt_to_equity_ratio', 0),
            'total_assets': summary.get('total_assets', 0),
            'total_liabilities': summary.get('total_liabilities', 0)
        }
    
    @classmethod
    def _generate_recommendations(cls, data: Dict) -> List[str]:
        """
        Generate actionable recommendations
        """
        summary = data.get('summary', {})
        recommendations = []
        
        if summary.get('debt_to_equity_ratio', 0) > 1.0:
            recommendations.append("Consider debt reduction strategies to improve financial stability")
        
        if summary.get('net_worth', 0) < 0:
            recommendations.append("Focus on increasing assets and reducing liabilities")
        
        return recommendations
    
    @classmethod
    def _identify_low_stock_items(cls, data: Dict) -> List[Dict]:
        """
        Identify items that need reordering
        """
        low_stock_items = []
        for item in data.get('stock_levels', []):
            if item['quantity_on_hand'] <= item['min_stock']:
                low_stock_items.append({
                    'product_name': item['product_name'],
                    'sku': item['sku'],
                    'current_stock': item['quantity_on_hand'],
                    'min_stock': item['min_stock'],
                    'recommended_order': item['max_stock'] - item['quantity_on_hand']
                })
        return low_stock_items
    
    @classmethod
    def _identify_optimization_opportunities(cls, data: Dict) -> List[Dict]:
        """
        Identify inventory optimization opportunities
        """
        opportunities = []
        for item in data.get('stock_levels', []):
            if item['quantity_on_hand'] > item['max_stock']:
                opportunities.append({
                    'product_name': item['product_name'],
                    'sku': item['sku'],
                    'current_stock': item['quantity_on_hand'],
                    'max_stock': item['max_stock'],
                    'excess_stock': item['quantity_on_hand'] - item['max_stock'],
                    'excess_value': (item['quantity_on_hand'] - item['max_stock']) * item['unit_cost']
                })
        return opportunities
    
    @classmethod
    def _get_recent_performance(cls) -> Dict[str, Any]:
        """
        Get recent financial performance metrics
        """
        try:
            # Get last 30 days of transactions
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            recent_transactions = GeneralLedgerEntry.query.filter(
                GeneralLedgerEntry.entry_date >= thirty_days_ago
            ).all()
            
            total_debits = sum([t.debit_amount for t in recent_transactions])
            total_credits = sum([t.credit_amount for t in recent_transactions])
            
            return {
                'period_days': 30,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'net_change': total_credits - total_debits,
                'transaction_count': len(recent_transactions)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting recent performance: {str(e)}")
            return {}
    
    @classmethod
    def _calculate_trend_indicators(cls, data: Dict) -> Dict[str, Any]:
        """
        Calculate trend indicators for market analysis
        """
        return {
            'volatility_index': 0.5,  # Placeholder
            'trend_direction': 'stable',
            'confidence_level': 'medium'
        }
    
    @classmethod
    def _assess_market_risks(cls, data: Dict) -> Dict[str, Any]:
        """
        Assess market risks
        """
        return {
            'currency_risk': 'low',
            'market_volatility': 'medium',
            'recommended_actions': ['Monitor exchange rates', 'Diversify currency exposure']
        }

