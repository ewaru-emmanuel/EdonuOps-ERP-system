from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import json

class AgingReports:
    """Comprehensive Aging Reports for Accounts Receivable and Accounts Payable"""
    
    def __init__(self):
        self.aging_buckets = {
            'current': 0,
            '30_days': 30,
            '60_days': 60,
            '90_days': 90,
            '120_days': 120,
            'over_120_days': 121
        }
    
    def generate_ar_aging_report(self, as_of_date: datetime = None, customer_id: str = None) -> Dict:
        """
        Generate comprehensive Accounts Receivable aging report
        """
        try:
            if not as_of_date:
                as_of_date = datetime.now()
            
            # Get AR transactions
            ar_transactions = self._get_ar_transactions(customer_id)
            
            # Calculate aging buckets
            aging_data = self._calculate_aging_buckets(ar_transactions, as_of_date)
            
            # Generate summary
            summary = self._generate_ar_summary(aging_data)
            
            # Generate customer breakdown
            customer_breakdown = self._generate_customer_breakdown(ar_transactions, as_of_date)
            
            report = {
                'report_id': f"AR-AGING-{as_of_date.strftime('%Y%m%d')}",
                'report_type': 'accounts_receivable_aging',
                'as_of_date': as_of_date,
                'generated_date': datetime.now(),
                'summary': summary,
                'aging_buckets': aging_data,
                'customer_breakdown': customer_breakdown,
                'risk_analysis': self._analyze_ar_risk(aging_data),
                'recommendations': self._generate_ar_recommendations(aging_data)
            }
            
            return {
                'success': True,
                'report': report,
                'message': 'AR aging report generated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating AR aging report: {str(e)}'
            }
    
    def generate_ap_aging_report(self, as_of_date: datetime = None, supplier_id: str = None) -> Dict:
        """
        Generate comprehensive Accounts Payable aging report
        """
        try:
            if not as_of_date:
                as_of_date = datetime.now()
            
            # Get AP transactions
            ap_transactions = self._get_ap_transactions(supplier_id)
            
            # Calculate aging buckets
            aging_data = self._calculate_aging_buckets(ap_transactions, as_of_date)
            
            # Generate summary
            summary = self._generate_ap_summary(aging_data)
            
            # Generate supplier breakdown
            supplier_breakdown = self._generate_supplier_breakdown(ap_transactions, as_of_date)
            
            report = {
                'report_id': f"AP-AGING-{as_of_date.strftime('%Y%m%d')}",
                'report_type': 'accounts_payable_aging',
                'as_of_date': as_of_date,
                'generated_date': datetime.now(),
                'summary': summary,
                'aging_buckets': aging_data,
                'supplier_breakdown': supplier_breakdown,
                'cash_flow_analysis': self._analyze_ap_cash_flow(aging_data),
                'recommendations': self._generate_ap_recommendations(aging_data)
            }
            
            return {
                'success': True,
                'report': report,
                'message': 'AP aging report generated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating AP aging report: {str(e)}'
            }
    
    def _get_ar_transactions(self, customer_id: str = None) -> List[Dict]:
        """
        Get Accounts Receivable transactions (mock data)
        """
        # Mock data - replace with actual database query
        ar_transactions = [
            {
                'invoice_id': 'INV-001',
                'customer_id': 'CUST001',
                'customer_name': 'ABC Company',
                'invoice_date': datetime.now() - timedelta(days=5),
                'due_date': datetime.now() + timedelta(days=25),
                'invoice_amount': 15000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 15000.00,
                'status': 'open'
            },
            {
                'invoice_id': 'INV-002',
                'customer_id': 'CUST002',
                'customer_name': 'XYZ Corporation',
                'invoice_date': datetime.now() - timedelta(days=35),
                'due_date': datetime.now() - timedelta(days=5),
                'invoice_amount': 25000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 25000.00,
                'status': 'overdue'
            },
            {
                'invoice_id': 'INV-003',
                'customer_id': 'CUST003',
                'customer_name': 'DEF Industries',
                'invoice_date': datetime.now() - timedelta(days=65),
                'due_date': datetime.now() - timedelta(days=35),
                'invoice_amount': 18000.00,
                'paid_amount': 5000.00,
                'outstanding_amount': 13000.00,
                'status': 'overdue'
            },
            {
                'invoice_id': 'INV-004',
                'customer_id': 'CUST001',
                'customer_name': 'ABC Company',
                'invoice_date': datetime.now() - timedelta(days=95),
                'due_date': datetime.now() - timedelta(days=65),
                'invoice_amount': 12000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 12000.00,
                'status': 'overdue'
            },
            {
                'invoice_id': 'INV-005',
                'customer_id': 'CUST004',
                'customer_name': 'GHI Solutions',
                'invoice_date': datetime.now() - timedelta(days=125),
                'due_date': datetime.now() - timedelta(days=95),
                'invoice_amount': 8000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 8000.00,
                'status': 'overdue'
            }
        ]
        
        if customer_id:
            ar_transactions = [t for t in ar_transactions if t['customer_id'] == customer_id]
        
        return ar_transactions
    
    def _get_ap_transactions(self, supplier_id: str = None) -> List[Dict]:
        """
        Get Accounts Payable transactions (mock data)
        """
        # Mock data - replace with actual database query
        ap_transactions = [
            {
                'invoice_id': 'AP-INV-001',
                'supplier_id': 'SUPP001',
                'supplier_name': 'Supplier A',
                'invoice_date': datetime.now() - timedelta(days=10),
                'due_date': datetime.now() + timedelta(days=20),
                'invoice_amount': 20000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 20000.00,
                'status': 'open'
            },
            {
                'invoice_id': 'AP-INV-002',
                'supplier_id': 'SUPP002',
                'supplier_name': 'Supplier B',
                'invoice_date': datetime.now() - timedelta(days=40),
                'due_date': datetime.now() - timedelta(days=10),
                'invoice_amount': 15000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 15000.00,
                'status': 'overdue'
            },
            {
                'invoice_id': 'AP-INV-003',
                'supplier_id': 'SUPP003',
                'supplier_name': 'Supplier C',
                'invoice_date': datetime.now() - timedelta(days=70),
                'due_date': datetime.now() - timedelta(days=40),
                'invoice_amount': 12000.00,
                'paid_amount': 3000.00,
                'outstanding_amount': 9000.00,
                'status': 'overdue'
            },
            {
                'invoice_id': 'AP-INV-004',
                'supplier_id': 'SUPP001',
                'supplier_name': 'Supplier A',
                'invoice_date': datetime.now() - timedelta(days=100),
                'due_date': datetime.now() - timedelta(days=70),
                'invoice_amount': 18000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 18000.00,
                'status': 'overdue'
            },
            {
                'invoice_id': 'AP-INV-005',
                'supplier_id': 'SUPP004',
                'supplier_name': 'Supplier D',
                'invoice_date': datetime.now() - timedelta(days=130),
                'due_date': datetime.now() - timedelta(days=100),
                'invoice_amount': 10000.00,
                'paid_amount': 0.00,
                'outstanding_amount': 10000.00,
                'status': 'overdue'
            }
        ]
        
        if supplier_id:
            ap_transactions = [t for t in ap_transactions if t['supplier_id'] == supplier_id]
        
        return ap_transactions
    
    def _calculate_aging_buckets(self, transactions: List[Dict], as_of_date: datetime) -> Dict:
        """
        Calculate aging buckets for transactions
        """
        aging_buckets = {
            'current': {'amount': 0, 'count': 0, 'transactions': []},
            '30_days': {'amount': 0, 'count': 0, 'transactions': []},
            '60_days': {'amount': 0, 'count': 0, 'transactions': []},
            '90_days': {'amount': 0, 'count': 0, 'transactions': []},
            '120_days': {'amount': 0, 'count': 0, 'transactions': []},
            'over_120_days': {'amount': 0, 'count': 0, 'transactions': []}
        }
        
        for transaction in transactions:
            days_overdue = (as_of_date - transaction['due_date']).days
            
            if days_overdue <= 0:
                bucket = 'current'
            elif days_overdue <= 30:
                bucket = '30_days'
            elif days_overdue <= 60:
                bucket = '60_days'
            elif days_overdue <= 90:
                bucket = '90_days'
            elif days_overdue <= 120:
                bucket = '120_days'
            else:
                bucket = 'over_120_days'
            
            aging_buckets[bucket]['amount'] += transaction['outstanding_amount']
            aging_buckets[bucket]['count'] += 1
            aging_buckets[bucket]['transactions'].append(transaction)
        
        return aging_buckets
    
    def _generate_ar_summary(self, aging_data: Dict) -> Dict:
        """
        Generate AR summary statistics
        """
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        total_invoices = sum(bucket['count'] for bucket in aging_data.values())
        
        overdue_amount = sum(bucket['amount'] for key, bucket in aging_data.items() if key != 'current')
        overdue_invoices = sum(bucket['count'] for key, bucket in aging_data.items() if key != 'current')
        
        return {
            'total_outstanding': total_outstanding,
            'total_invoices': total_invoices,
            'overdue_amount': overdue_amount,
            'overdue_invoices': overdue_invoices,
            'overdue_percentage': (overdue_amount / total_outstanding * 100) if total_outstanding > 0 else 0,
            'current_amount': aging_data['current']['amount'],
            'current_invoices': aging_data['current']['count']
        }
    
    def _generate_ap_summary(self, aging_data: Dict) -> Dict:
        """
        Generate AP summary statistics
        """
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        total_invoices = sum(bucket['count'] for bucket in aging_data.values())
        
        overdue_amount = sum(bucket['amount'] for key, bucket in aging_data.items() if key != 'current')
        overdue_invoices = sum(bucket['count'] for key, bucket in aging_data.items() if key != 'current')
        
        return {
            'total_outstanding': total_outstanding,
            'total_invoices': total_invoices,
            'overdue_amount': overdue_amount,
            'overdue_invoices': overdue_invoices,
            'overdue_percentage': (overdue_amount / total_outstanding * 100) if total_outstanding > 0 else 0,
            'current_amount': aging_data['current']['amount'],
            'current_invoices': aging_data['current']['count']
        }
    
    def _generate_customer_breakdown(self, transactions: List[Dict], as_of_date: datetime) -> List[Dict]:
        """
        Generate customer breakdown for AR
        """
        customer_data = {}
        
        for transaction in transactions:
            customer_id = transaction['customer_id']
            if customer_id not in customer_data:
                customer_data[customer_id] = {
                    'customer_id': customer_id,
                    'customer_name': transaction['customer_name'],
                    'total_outstanding': 0,
                    'invoice_count': 0,
                    'oldest_invoice_date': transaction['invoice_date'],
                    'overdue_amount': 0,
                    'overdue_invoices': 0
                }
            
            customer_data[customer_id]['total_outstanding'] += transaction['outstanding_amount']
            customer_data[customer_id]['invoice_count'] += 1
            
            if transaction['invoice_date'] < customer_data[customer_id]['oldest_invoice_date']:
                customer_data[customer_id]['oldest_invoice_date'] = transaction['invoice_date']
            
            if transaction['status'] == 'overdue':
                customer_data[customer_id]['overdue_amount'] += transaction['outstanding_amount']
                customer_data[customer_id]['overdue_invoices'] += 1
        
        return list(customer_data.values())
    
    def _generate_supplier_breakdown(self, transactions: List[Dict], as_of_date: datetime) -> List[Dict]:
        """
        Generate supplier breakdown for AP
        """
        supplier_data = {}
        
        for transaction in transactions:
            supplier_id = transaction['supplier_id']
            if supplier_id not in supplier_data:
                supplier_data[supplier_id] = {
                    'supplier_id': supplier_id,
                    'supplier_name': transaction['supplier_name'],
                    'total_outstanding': 0,
                    'invoice_count': 0,
                    'oldest_invoice_date': transaction['invoice_date'],
                    'overdue_amount': 0,
                    'overdue_invoices': 0
                }
            
            supplier_data[supplier_id]['total_outstanding'] += transaction['outstanding_amount']
            supplier_data[supplier_id]['invoice_count'] += 1
            
            if transaction['invoice_date'] < supplier_data[supplier_id]['oldest_invoice_date']:
                supplier_data[supplier_id]['oldest_invoice_date'] = transaction['invoice_date']
            
            if transaction['status'] == 'overdue':
                supplier_data[supplier_id]['overdue_amount'] += transaction['outstanding_amount']
                supplier_data[supplier_id]['overdue_invoices'] += 1
        
        return list(supplier_data.values())
    
    def _analyze_ar_risk(self, aging_data: Dict) -> Dict:
        """
        Analyze AR risk based on aging
        """
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        
        # Risk levels
        high_risk = aging_data['over_120_days']['amount'] + aging_data['120_days']['amount']
        medium_risk = aging_data['90_days']['amount'] + aging_data['60_days']['amount']
        low_risk = aging_data['30_days']['amount']
        
        return {
            'high_risk_amount': high_risk,
            'high_risk_percentage': (high_risk / total_outstanding * 100) if total_outstanding > 0 else 0,
            'medium_risk_amount': medium_risk,
            'medium_risk_percentage': (medium_risk / total_outstanding * 100) if total_outstanding > 0 else 0,
            'low_risk_amount': low_risk,
            'low_risk_percentage': (low_risk / total_outstanding * 100) if total_outstanding > 0 else 0,
            'risk_score': self._calculate_risk_score(aging_data)
        }
    
    def _analyze_ap_cash_flow(self, aging_data: Dict) -> Dict:
        """
        Analyze AP cash flow impact
        """
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        
        # Cash flow impact
        immediate_payments = aging_data['current']['amount']
        short_term_payments = aging_data['30_days']['amount']
        medium_term_payments = aging_data['60_days']['amount'] + aging_data['90_days']['amount']
        long_term_payments = aging_data['120_days']['amount'] + aging_data['over_120_days']['amount']
        
        return {
            'immediate_payments': immediate_payments,
            'short_term_payments': short_term_payments,
            'medium_term_payments': medium_term_payments,
            'long_term_payments': long_term_payments,
            'total_cash_requirement': total_outstanding,
            'cash_flow_score': self._calculate_cash_flow_score(aging_data)
        }
    
    def _calculate_risk_score(self, aging_data: Dict) -> float:
        """
        Calculate risk score (0-100, higher = more risky)
        """
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        if total_outstanding == 0:
            return 0
        
        # Weighted risk calculation
        risk_score = (
            aging_data['over_120_days']['amount'] * 1.0 +
            aging_data['120_days']['amount'] * 0.8 +
            aging_data['90_days']['amount'] * 0.6 +
            aging_data['60_days']['amount'] * 0.4 +
            aging_data['30_days']['amount'] * 0.2
        ) / total_outstanding * 100
        
        return min(risk_score, 100)
    
    def _calculate_cash_flow_score(self, aging_data: Dict) -> float:
        """
        Calculate cash flow score (0-100, higher = better cash flow)
        """
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        if total_outstanding == 0:
            return 100
        
        # Weighted cash flow calculation (current is good, overdue is bad)
        cash_flow_score = (
            aging_data['current']['amount'] * 1.0 +
            aging_data['30_days']['amount'] * 0.8 +
            aging_data['60_days']['amount'] * 0.6 +
            aging_data['90_days']['amount'] * 0.4 +
            aging_data['120_days']['amount'] * 0.2 +
            aging_data['over_120_days']['amount'] * 0.0
        ) / total_outstanding * 100
        
        return min(cash_flow_score, 100)
    
    def _generate_ar_recommendations(self, aging_data: Dict) -> List[str]:
        """
        Generate recommendations for AR management
        """
        recommendations = []
        
        overdue_amount = sum(bucket['amount'] for key, bucket in aging_data.items() if key != 'current')
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        
        if overdue_amount > total_outstanding * 0.3:
            recommendations.append("Over 30% of receivables are overdue - implement stricter credit policies")
        
        if aging_data['over_120_days']['amount'] > total_outstanding * 0.1:
            recommendations.append("Over 10% of receivables are over 120 days - consider collection agency")
        
        if aging_data['60_days']['amount'] > total_outstanding * 0.2:
            recommendations.append("High amount in 60-day bucket - review collection procedures")
        
        if not recommendations:
            recommendations.append("AR aging looks healthy - continue current collection practices")
        
        return recommendations
    
    def _generate_ap_recommendations(self, aging_data: Dict) -> List[str]:
        """
        Generate recommendations for AP management
        """
        recommendations = []
        
        overdue_amount = sum(bucket['amount'] for key, bucket in aging_data.items() if key != 'current')
        total_outstanding = sum(bucket['amount'] for bucket in aging_data.values())
        
        if overdue_amount > total_outstanding * 0.4:
            recommendations.append("High overdue payables - review cash flow and payment priorities")
        
        if aging_data['over_120_days']['amount'] > total_outstanding * 0.15:
            recommendations.append("Significant overdue payables over 120 days - risk of supplier issues")
        
        if aging_data['current']['amount'] < total_outstanding * 0.3:
            recommendations.append("Low current payables - consider early payment discounts")
        
        if not recommendations:
            recommendations.append("AP aging looks manageable - continue current payment practices")
        
        return recommendations

# Global instance
aging_reports = AgingReports()



