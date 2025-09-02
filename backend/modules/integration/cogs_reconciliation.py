from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import json

class COGSReconciliation:
    """COGS Reconciliation System - Verifies data integrity between Finance and Inventory"""
    
    def __init__(self):
        self.reconciliation_reports = []
    
    def generate_reconciliation_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """
        Generate comprehensive COGS reconciliation report
        Compares Finance GL COGS with Inventory calculated COGS
        """
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Get Finance GL COGS data
            finance_cogs = self._get_finance_gl_cogs(start_date, end_date)
            
            # Get Inventory COGS data
            inventory_cogs = self._get_inventory_cogs(start_date, end_date)
            
            # Calculate variances
            variances = self._calculate_variances(finance_cogs, inventory_cogs)
            
            # Generate report
            report = {
                'report_id': f"COGS-RECON-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'generated_date': datetime.now(),
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'summary': {
                    'finance_total_cogs': finance_cogs.get('total_cogs', 0),
                    'inventory_total_cogs': inventory_cogs.get('total_cogs', 0),
                    'variance_amount': variances.get('total_variance', 0),
                    'variance_percentage': variances.get('variance_percentage', 0),
                    'status': 'RECONCILED' if abs(variances.get('total_variance', 0)) < 0.01 else 'VARIANCES_FOUND'
                },
                'finance_data': finance_cogs,
                'inventory_data': inventory_cogs,
                'variances': variances,
                'recommendations': self._generate_recommendations(variances)
            }
            
            self.reconciliation_reports.append(report)
            
            return {
                'success': True,
                'report': report,
                'message': 'COGS reconciliation report generated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating COGS reconciliation report: {str(e)}"
            }
    
    def _get_finance_gl_cogs(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Get COGS data from Finance General Ledger
        """
        # Mock data - replace with actual database query
        finance_cogs_data = {
            'total_cogs': 125000.00,
            'transactions': [
                {
                    'date': datetime.now() - timedelta(days=25),
                    'journal_entry_id': 'JE-001',
                    'account': 'Cost of Goods Sold',
                    'amount': 50000.00,
                    'reference': 'INV-001',
                    'description': 'COGS for Sale Invoice INV-001'
                },
                {
                    'date': datetime.now() - timedelta(days=20),
                    'journal_entry_id': 'JE-002',
                    'account': 'Cost of Goods Sold',
                    'amount': 45000.00,
                    'reference': 'INV-002',
                    'description': 'COGS for Sale Invoice INV-002'
                },
                {
                    'date': datetime.now() - timedelta(days=15),
                    'journal_entry_id': 'JE-003',
                    'account': 'Cost of Goods Sold',
                    'amount': 30000.00,
                    'reference': 'INV-003',
                    'description': 'COGS for Sale Invoice INV-003'
                }
            ],
            'by_item': {
                'ITEM001': 60000.00,
                'ITEM002': 45000.00,
                'ITEM003': 20000.00
            }
        }
        
        return finance_cogs_data
    
    def _get_inventory_cogs(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Get COGS data calculated from Inventory transactions
        """
        # Mock data - replace with actual database query
        inventory_cogs_data = {
            'total_cogs': 125000.00,
            'transactions': [
                {
                    'date': datetime.now() - timedelta(days=25),
                    'sale_id': 'SALE-001',
                    'item_id': 'ITEM001',
                    'quantity': 100,
                    'unit_cost': 500.00,
                    'total_cost': 50000.00,
                    'valuation_method': 'fifo',
                    'reference': 'INV-001'
                },
                {
                    'date': datetime.now() - timedelta(days=20),
                    'sale_id': 'SALE-002',
                    'item_id': 'ITEM002',
                    'quantity': 75,
                    'unit_cost': 600.00,
                    'total_cost': 45000.00,
                    'valuation_method': 'fifo',
                    'reference': 'INV-002'
                },
                {
                    'date': datetime.now() - timedelta(days=15),
                    'sale_id': 'SALE-003',
                    'item_id': 'ITEM003',
                    'quantity': 50,
                    'unit_cost': 400.00,
                    'total_cost': 20000.00,
                    'valuation_method': 'fifo',
                    'reference': 'INV-003'
                }
            ],
            'by_item': {
                'ITEM001': 60000.00,
                'ITEM002': 45000.00,
                'ITEM003': 20000.00
            },
            'by_valuation_method': {
                'fifo': 115000.00,
                'lifo': 125000.00,
                'average': 120000.00
            }
        }
        
        return inventory_cogs_data
    
    def _calculate_variances(self, finance_data: Dict, inventory_data: Dict) -> Dict:
        """
        Calculate variances between Finance and Inventory COGS
        """
        finance_total = finance_data.get('total_cogs', 0)
        inventory_total = inventory_data.get('total_cogs', 0)
        
        variance_amount = abs(finance_total - inventory_total)
        variance_percentage = (variance_amount / finance_total * 100) if finance_total > 0 else 0
        
        # Item-level variances
        item_variances = {}
        finance_by_item = finance_data.get('by_item', {})
        inventory_by_item = inventory_data.get('by_item', {})
        
        all_items = set(finance_by_item.keys()) | set(inventory_by_item.keys())
        
        for item in all_items:
            finance_amount = finance_by_item.get(item, 0)
            inventory_amount = inventory_by_item.get(item, 0)
            item_variance = abs(finance_amount - inventory_amount)
            
            if item_variance > 0.01:  # Tolerance for rounding
                item_variances[item] = {
                    'finance_amount': finance_amount,
                    'inventory_amount': inventory_amount,
                    'variance_amount': item_variance,
                    'variance_percentage': (item_variance / finance_amount * 100) if finance_amount > 0 else 0
                }
        
        return {
            'total_variance': variance_amount,
            'variance_percentage': variance_percentage,
            'is_reconciled': variance_amount < 0.01,
            'item_variances': item_variances,
            'significant_variances': [item for item, data in item_variances.items() if data['variance_amount'] > 100]
        }
    
    def _generate_recommendations(self, variances: Dict) -> List[str]:
        """
        Generate recommendations based on variances found
        """
        recommendations = []
        
        if not variances.get('is_reconciled', True):
            recommendations.append("COGS totals do not match between Finance and Inventory modules")
        
        significant_variances = variances.get('significant_variances', [])
        if significant_variances:
            recommendations.append(f"Significant variances found for items: {', '.join(significant_variances)}")
            recommendations.append("Review journal entries and inventory transactions for these items")
        
        if variances.get('variance_percentage', 0) > 5:
            recommendations.append("Variance percentage exceeds 5% - investigate for systematic issues")
        
        if not recommendations:
            recommendations.append("No significant variances found - data integrity is good")
        
        return recommendations
    
    def get_reconciliation_history(self, limit: int = 10) -> List[Dict]:
        """
        Get history of reconciliation reports
        """
        return sorted(
            self.reconciliation_reports,
            key=lambda x: x['generated_date'],
            reverse=True
        )[:limit]
    
    def get_reconciliation_by_id(self, report_id: str) -> Optional[Dict]:
        """
        Get specific reconciliation report by ID
        """
        for report in self.reconciliation_reports:
            if report['report_id'] == report_id:
                return report
        return None
    
    def export_reconciliation_report(self, report_id: str, format: str = 'json') -> Dict:
        """
        Export reconciliation report in specified format
        """
        try:
            report = self.get_reconciliation_by_id(report_id)
            if not report:
                return {
                    'success': False,
                    'error': 'Reconciliation report not found'
                }
            
            if format == 'json':
                return {
                    'success': True,
                    'data': report,
                    'format': 'json'
                }
            elif format == 'csv':
                # Convert to CSV format
                csv_data = self._convert_to_csv(report)
                return {
                    'success': True,
                    'data': csv_data,
                    'format': 'csv'
                }
            else:
                return {
                    'success': False,
                    'error': f'Unsupported format: {format}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error exporting reconciliation report: {str(e)}"
            }
    
    def _convert_to_csv(self, report: Dict) -> str:
        """
        Convert reconciliation report to CSV format
        """
        csv_lines = []
        
        # Header
        csv_lines.append("COGS Reconciliation Report")
        csv_lines.append(f"Report ID: {report['report_id']}")
        csv_lines.append(f"Generated: {report['generated_date']}")
        csv_lines.append(f"Period: {report['period']['start_date']} to {report['period']['end_date']}")
        csv_lines.append("")
        
        # Summary
        csv_lines.append("Summary")
        csv_lines.append("Finance Total COGS,Inventory Total COGS,Variance Amount,Variance %,Status")
        summary = report['summary']
        csv_lines.append(f"{summary['finance_total_cogs']},{summary['inventory_total_cogs']},{summary['variance_amount']},{summary['variance_percentage']},{summary['status']}")
        csv_lines.append("")
        
        # Item-level variances
        if report['variances']['item_variances']:
            csv_lines.append("Item-Level Variances")
            csv_lines.append("Item,Finance Amount,Inventory Amount,Variance Amount,Variance %")
            for item, data in report['variances']['item_variances'].items():
                csv_lines.append(f"{item},{data['finance_amount']},{data['inventory_amount']},{data['variance_amount']},{data['variance_percentage']}")
            csv_lines.append("")
        
        # Recommendations
        csv_lines.append("Recommendations")
        for rec in report['recommendations']:
            csv_lines.append(rec)
        
        return "\n".join(csv_lines)
    
    def schedule_automated_reconciliation(self, frequency: str = 'daily') -> Dict:
        """
        Schedule automated COGS reconciliation
        """
        try:
            schedule = {
                'id': f"SCHED-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'frequency': frequency,
                'created_date': datetime.now(),
                'status': 'active',
                'last_run': None,
                'next_run': self._calculate_next_run(frequency)
            }
            
            return {
                'success': True,
                'schedule': schedule,
                'message': f'Automated COGS reconciliation scheduled for {frequency} frequency'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error scheduling automated reconciliation: {str(e)}"
            }
    
    def _calculate_next_run(self, frequency: str) -> datetime:
        """
        Calculate next run time based on frequency
        """
        now = datetime.now()
        
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif frequency == 'monthly':
            # Simple monthly calculation
            return now + timedelta(days=30)
        else:
            return now + timedelta(days=1)

# Global instance
cogs_reconciliation = COGSReconciliation()



