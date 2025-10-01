"""
Advanced Analytics Service
Provides comprehensive reconciliation analytics and insights
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import current_app
from sqlalchemy import text, func, and_, or_
from ..database import db

logger = logging.getLogger(__name__)

class ReconciliationAnalytics:
    """Advanced analytics for reconciliation data"""
    
    def __init__(self):
        self.analytics_enabled = os.getenv('ANALYTICS_ENABLED', 'true').lower() == 'true'
    
    def get_reconciliation_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get reconciliation trends over time"""
        try:
            with current_app.app_context():
                # Get daily reconciliation counts
                daily_counts = db.session.execute(text("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as count,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                        SUM(CASE WHEN status = 'discrepancy' THEN 1 ELSE 0 END) as discrepancies
                    FROM reconciliation_sessions 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """.format(days))).fetchall()
                
                # Get transaction volume trends
                transaction_volume = db.session.execute(text("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as transaction_count,
                        SUM(ABS(amount)) as total_volume
                    FROM bank_transactions 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """.format(days))).fetchall()
                
                # Calculate trends
                trends = {
                    'daily_reconciliations': [{'date': str(row.date), 'count': row.count, 'completed': row.completed, 'pending': row.pending, 'discrepancies': row.discrepancies} for row in daily_counts],
                    'daily_transactions': [{'date': str(row.date), 'count': row.transaction_count, 'volume': float(row.total_volume or 0)} for row in transaction_volume],
                    'summary': self._calculate_trend_summary(daily_counts, transaction_volume)
                }
                
                return trends
                
        except Exception as e:
            logger.error(f"Error getting reconciliation trends: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_trend_summary(self, daily_counts, transaction_volume) -> Dict[str, Any]:
        """Calculate trend summary statistics"""
        try:
            if not daily_counts:
                return {'error': 'No data available'}
            
            # Calculate averages
            total_reconciliations = sum(row.count for row in daily_counts)
            total_completed = sum(row.completed for row in daily_counts)
            total_pending = sum(row.pending for row in daily_counts)
            total_discrepancies = sum(row.discrepancies for row in daily_counts)
            
            avg_daily_reconciliations = total_reconciliations / len(daily_counts) if daily_counts else 0
            completion_rate = (total_completed / total_reconciliations * 100) if total_reconciliations > 0 else 0
            
            # Calculate transaction volume
            total_volume = sum(float(row.total_volume or 0) for row in transaction_volume)
            avg_daily_volume = total_volume / len(transaction_volume) if transaction_volume else 0
            
            return {
                'total_reconciliations': total_reconciliations,
                'completion_rate': round(completion_rate, 2),
                'avg_daily_reconciliations': round(avg_daily_reconciliations, 2),
                'total_volume': total_volume,
                'avg_daily_volume': round(avg_daily_volume, 2),
                'discrepancy_rate': round((total_discrepancies / total_reconciliations * 100) if total_reconciliations > 0 else 0, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating trend summary: {str(e)}")
            return {'error': str(e)}
    
    def get_account_performance(self, bank_account_id: Optional[int] = None) -> Dict[str, Any]:
        """Get performance metrics for bank accounts"""
        try:
            with current_app.app_context():
                # Base query
                base_query = """
                    SELECT 
                        ba.id,
                        ba.account_name,
                        ba.bank_name,
                        COUNT(DISTINCT rs.id) as total_sessions,
                        COUNT(DISTINCT CASE WHEN rs.status = 'completed' THEN rs.id END) as completed_sessions,
                        COUNT(DISTINCT bt.id) as total_transactions,
                        COUNT(DISTINCT CASE WHEN bt.matched = 1 THEN bt.id END) as matched_transactions,
                        AVG(rs.difference) as avg_difference,
                        MAX(rs.created_at) as last_reconciliation
                    FROM bank_accounts ba
                    LEFT JOIN reconciliation_sessions rs ON ba.id = rs.bank_account_id
                    LEFT JOIN bank_transactions bt ON ba.id = bt.bank_account_id
                """
                
                if bank_account_id:
                    base_query += " WHERE ba.id = :bank_account_id"
                    params = {'bank_account_id': bank_account_id}
                else:
                    params = {}
                
                base_query += " GROUP BY ba.id, ba.account_name, ba.bank_name"
                
                results = db.session.execute(text(base_query), params).fetchall()
                
                account_metrics = []
                for row in results:
                    completion_rate = (row.completed_sessions / row.total_sessions * 100) if row.total_sessions > 0 else 0
                    match_rate = (row.matched_transactions / row.total_transactions * 100) if row.total_transactions > 0 else 0
                    
                    account_metrics.append({
                        'account_id': row.id,
                        'account_name': row.account_name,
                        'bank_name': row.bank_name,
                        'total_sessions': row.total_sessions,
                        'completed_sessions': row.completed_sessions,
                        'completion_rate': round(completion_rate, 2),
                        'total_transactions': row.total_transactions,
                        'matched_transactions': row.matched_transactions,
                        'match_rate': round(match_rate, 2),
                        'avg_difference': round(float(row.avg_difference or 0), 2),
                        'last_reconciliation': row.last_reconciliation.isoformat() if row.last_reconciliation else None
                    })
                
                return {
                    'accounts': account_metrics,
                    'summary': self._calculate_account_summary(account_metrics)
                }
                
        except Exception as e:
            logger.error(f"Error getting account performance: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_account_summary(self, account_metrics: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics for accounts"""
        try:
            if not account_metrics:
                return {'error': 'No data available'}
            
            total_accounts = len(account_metrics)
            avg_completion_rate = sum(acc['completion_rate'] for acc in account_metrics) / total_accounts
            avg_match_rate = sum(acc['match_rate'] for acc in account_metrics) / total_accounts
            
            # Find best and worst performing accounts
            best_account = max(account_metrics, key=lambda x: x['completion_rate'])
            worst_account = min(account_metrics, key=lambda x: x['completion_rate'])
            
            return {
                'total_accounts': total_accounts,
                'avg_completion_rate': round(avg_completion_rate, 2),
                'avg_match_rate': round(avg_match_rate, 2),
                'best_performing': {
                    'account_name': best_account['account_name'],
                    'completion_rate': best_account['completion_rate']
                },
                'worst_performing': {
                    'account_name': worst_account['account_name'],
                    'completion_rate': worst_account['completion_rate']
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating account summary: {str(e)}")
            return {'error': str(e)}
    
    def get_discrepancy_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analyze reconciliation discrepancies"""
        try:
            with current_app.app_context():
                # Get discrepancy patterns
                discrepancy_patterns = db.session.execute(text("""
                    SELECT 
                        ba.account_name,
                        ba.bank_name,
                        rs.difference,
                        rs.statement_balance,
                        rs.book_balance,
                        rs.created_at,
                        COUNT(*) as frequency
                    FROM reconciliation_sessions rs
                    JOIN bank_accounts ba ON rs.bank_account_id = ba.id
                    WHERE rs.difference != 0 
                    AND rs.created_at >= datetime('now', '-{} days')
                    GROUP BY ba.account_name, ba.bank_name, rs.difference
                    ORDER BY frequency DESC
                """.format(days))).fetchall()
                
                # Get common discrepancy amounts
                common_amounts = db.session.execute(text("""
                    SELECT 
                        difference,
                        COUNT(*) as frequency
                    FROM reconciliation_sessions 
                    WHERE difference != 0 
                    AND created_at >= datetime('now', '-{} days')
                    GROUP BY difference
                    ORDER BY frequency DESC
                    LIMIT 10
                """.format(days))).fetchall()
                
                # Calculate discrepancy statistics
                discrepancy_stats = db.session.execute(text("""
                    SELECT 
                        COUNT(*) as total_discrepancies,
                        AVG(ABS(difference)) as avg_discrepancy,
                        MAX(ABS(difference)) as max_discrepancy,
                        MIN(ABS(difference)) as min_discrepancy
                    FROM reconciliation_sessions 
                    WHERE difference != 0 
                    AND created_at >= datetime('now', '-{} days')
                """.format(days))).fetchone()
                
                return {
                    'patterns': [{
                        'account_name': row.account_name,
                        'bank_name': row.bank_name,
                        'difference': float(row.difference),
                        'frequency': row.frequency,
                        'statement_balance': float(row.statement_balance),
                        'book_balance': float(row.book_balance)
                    } for row in discrepancy_patterns],
                    'common_amounts': [{
                        'difference': float(row.difference),
                        'frequency': row.frequency
                    } for row in common_amounts],
                    'statistics': {
                        'total_discrepancies': discrepancy_stats.total_discrepancies,
                        'avg_discrepancy': round(float(discrepancy_stats.avg_discrepancy or 0), 2),
                        'max_discrepancy': round(float(discrepancy_stats.max_discrepancy or 0), 2),
                        'min_discrepancy': round(float(discrepancy_stats.min_discrepancy or 0), 2)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting discrepancy analysis: {str(e)}")
            return {'error': str(e)}
    
    def get_matching_efficiency(self, days: int = 30) -> Dict[str, Any]:
        """Analyze transaction matching efficiency"""
        try:
            with current_app.app_context():
                # Get matching statistics
                matching_stats = db.session.execute(text("""
                    SELECT 
                        COUNT(*) as total_transactions,
                        COUNT(CASE WHEN matched = 1 THEN 1 END) as matched_transactions,
                        COUNT(CASE WHEN matched = 0 THEN 1 END) as unmatched_transactions,
                        AVG(CASE WHEN matched = 1 THEN 1.0 ELSE 0.0 END) as match_rate
                    FROM bank_transactions 
                    WHERE created_at >= datetime('now', '-{} days')
                """.format(days))).fetchone()
                
                # Get matching by amount ranges
                amount_ranges = db.session.execute(text("""
                    SELECT 
                        CASE 
                            WHEN ABS(amount) < 100 THEN '< $100'
                            WHEN ABS(amount) < 1000 THEN '$100 - $1,000'
                            WHEN ABS(amount) < 10000 THEN '$1,000 - $10,000'
                            ELSE '> $10,000'
                        END as amount_range,
                        COUNT(*) as total_count,
                        COUNT(CASE WHEN matched = 1 THEN 1 END) as matched_count
                    FROM bank_transactions 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY amount_range
                    ORDER BY 
                        CASE 
                            WHEN ABS(amount) < 100 THEN 1
                            WHEN ABS(amount) < 1000 THEN 2
                            WHEN ABS(amount) < 10000 THEN 3
                            ELSE 4
                        END
                """.format(days))).fetchall()
                
                # Get matching by date patterns
                date_patterns = db.session.execute(text("""
                    SELECT 
                        strftime('%w', transaction_date) as day_of_week,
                        COUNT(*) as total_count,
                        COUNT(CASE WHEN matched = 1 THEN 1 END) as matched_count
                    FROM bank_transactions 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY day_of_week
                    ORDER BY day_of_week
                """.format(days))).fetchall()
                
                return {
                    'overall_stats': {
                        'total_transactions': matching_stats.total_transactions,
                        'matched_transactions': matching_stats.matched_transactions,
                        'unmatched_transactions': matching_stats.unmatched_transactions,
                        'match_rate': round(float(matching_stats.match_rate or 0) * 100, 2)
                    },
                    'amount_ranges': [{
                        'range': row.amount_range,
                        'total_count': row.total_count,
                        'matched_count': row.matched_count,
                        'match_rate': round((row.matched_count / row.total_count * 100) if row.total_count > 0 else 0, 2)
                    } for row in amount_ranges],
                    'day_patterns': [{
                        'day_of_week': row.day_of_week,
                        'day_name': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][int(row.day_of_week)],
                        'total_count': row.total_count,
                        'matched_count': row.matched_count,
                        'match_rate': round((row.matched_count / row.total_count * 100) if row.total_count > 0 else 0, 2)
                    } for row in date_patterns]
                }
                
        except Exception as e:
            logger.error(f"Error getting matching efficiency: {str(e)}")
            return {'error': str(e)}
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations based on analytics"""
        try:
            recommendations = []
            
            # Get current performance metrics
            trends = self.get_reconciliation_trends(30)
            account_performance = self.get_account_performance()
            matching_efficiency = self.get_matching_efficiency(30)
            
            # Analyze trends
            if 'summary' in trends and trends['summary'].get('completion_rate', 0) < 80:
                recommendations.append({
                    'type': 'low_completion_rate',
                    'priority': 'high',
                    'title': 'Low Reconciliation Completion Rate',
                    'description': f"Current completion rate is {trends['summary'].get('completion_rate', 0)}%. Consider automating more reconciliation processes.",
                    'action': 'Implement automated reconciliation for high-volume accounts'
                })
            
            # Analyze account performance
            if 'summary' in account_performance:
                avg_completion = account_performance['summary'].get('avg_completion_rate', 0)
                if avg_completion < 70:
                    recommendations.append({
                        'type': 'account_performance',
                        'priority': 'medium',
                        'title': 'Account Performance Issues',
                        'description': f"Average account completion rate is {avg_completion}%. Some accounts may need attention.",
                        'action': 'Review and optimize reconciliation processes for underperforming accounts'
                    })
            
            # Analyze matching efficiency
            if 'overall_stats' in matching_efficiency:
                match_rate = matching_efficiency['overall_stats'].get('match_rate', 0)
                if match_rate < 60:
                    recommendations.append({
                        'type': 'matching_efficiency',
                        'priority': 'high',
                        'title': 'Low Transaction Matching Rate',
                        'description': f"Current matching rate is {match_rate}%. Many transactions are not being matched automatically.",
                        'action': 'Improve auto-matching algorithms and add more matching criteria'
                    })
            
            # Analyze discrepancy patterns
            discrepancy_analysis = self.get_discrepancy_analysis(30)
            if 'statistics' in discrepancy_analysis:
                avg_discrepancy = discrepancy_analysis['statistics'].get('avg_discrepancy', 0)
                if avg_discrepancy > 1000:  # More than $1000 average discrepancy
                    recommendations.append({
                        'type': 'high_discrepancies',
                        'priority': 'high',
                        'title': 'High Average Discrepancies',
                        'description': f"Average discrepancy is ${avg_discrepancy}. This may indicate systematic issues.",
                        'action': 'Investigate and resolve systematic reconciliation issues'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {str(e)}")
            return []

# Global analytics instance
reconciliation_analytics = ReconciliationAnalytics()












