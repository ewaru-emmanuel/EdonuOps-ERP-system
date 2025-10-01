"""
Inventory Variance Reporting API Routes
Date: September 18, 2025
Purpose: Advanced variance analysis and reporting dashboards
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, and_, or_
import logging

try:
    from app import db
    from modules.inventory.cost_layer_models import (
        InventoryCostLayer, InventoryValuationSnapshot, CostLayerTransaction
    )
    from modules.inventory.advanced_models import InventoryProduct, StockLevel, InventoryTransaction
    from modules.inventory.daily_cycle_models import DailyInventoryBalance
    from modules.finance.advanced_models import GeneralLedgerEntry, ChartOfAccounts
    from services.inventory_costing_service import InventoryCostingService
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create blueprint
variance_reports_bp = Blueprint('inventory_variance', __name__, url_prefix='/api/inventory/variance')

@variance_reports_bp.route('/inventory-gl-delta', methods=['GET'])
def get_inventory_gl_variance():
    """
    Get inventory value delta between physical inventory and GL
    GET /api/inventory/variance/inventory-gl-delta?date=2025-09-18
    """
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty variance (for development)
        if not user_id:
            print("Warning: No user context found for inventory GL variance, returning empty results")
            return jsonify({
                'as_of_date': date.today().isoformat(),
                'inventory_total': 0,
                'gl_total': 0,
                'variance': 0,
                'variance_percentage': 0,
                'status': 'No data available'
            }), 200
        
        # Parse date parameter
        date_str = request.args.get('date')
        if date_str:
            as_of_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            as_of_date = date.today()
        
        # Get inventory total from daily balances
        inventory_balances = DailyInventoryBalance.query.filter_by(
            cycle_date=as_of_date
        ).all()
        
        inventory_total = sum(balance.closing_total_value for balance in inventory_balances)
        
        # Get GL inventory account balance
        inventory_accounts = ChartOfAccounts.query.filter(
            ChartOfAccounts.account_name.ilike('%inventory%'),
            ChartOfAccounts.account_type == 'Asset'
        ).all()
        
        gl_total = 0
        account_details = []
        
        for account in inventory_accounts:
            # Calculate account balance
            gl_entries = GeneralLedgerEntry.query.filter(
                GeneralLedgerEntry.account_id == account.id,
                GeneralLedgerEntry.entry_date <= as_of_date,
                GeneralLedgerEntry.status == 'posted'
            ).all()
            
            account_balance = sum(entry.debit_amount - entry.credit_amount for entry in gl_entries)
            gl_total += account_balance
            
            account_details.append({
                'account_id': account.id,
                'account_name': account.account_name,
                'account_code': account.account_code,
                'balance': account_balance,
                'entry_count': len(gl_entries)
            })
        
        # Calculate variance
        variance = inventory_total - gl_total
        variance_percentage = (variance / inventory_total * 100) if inventory_total > 0 else 0
        
        # Determine variance significance
        variance_threshold = max(100, inventory_total * 0.02)  # 2% or $100
        is_material = abs(variance) > variance_threshold
        
        return jsonify({
            'success': True,
            'data': {
                'as_of_date': as_of_date.isoformat(),
                'inventory_total': inventory_total,
                'gl_total': gl_total,
                'variance': variance,
                'variance_percentage': round(variance_percentage, 2),
                'is_material': is_material,
                'variance_threshold': variance_threshold,
                'status': 'BALANCED' if not is_material else 'VARIANCE_DETECTED',
                'account_details': account_details,
                'product_count': len(inventory_balances)
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error getting inventory-GL variance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@variance_reports_bp.route('/shrinkage-analysis', methods=['GET'])
def get_shrinkage_analysis():
    """
    Get shrinkage analysis per warehouse/SKU
    GET /api/inventory/variance/shrinkage-analysis?days=30
    """
    try:
        # Get user ID from request headers or JWT token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # Try to get from JWT token as fallback
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
            except:
                pass
        
        # If still no user_id, return empty analysis (for development)
        if not user_id:
            print("Warning: No user context found for shrinkage analysis, returning empty results")
            return jsonify({
                'shrinkage_data': [],
                'summary': {
                    'total_shrinkage': 0,
                    'affected_products': 0,
                    'total_value': 0
                }
            }), 200
        
        days = request.args.get('days', 30, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get adjustment transactions (shrinkage indicators) - FILTER BY USER
        adjustments = InventoryTransaction.query.filter(
            and_(
                InventoryTransaction.transaction_type == 'adjustment',
                func.date(InventoryTransaction.transaction_date) >= start_date,
                func.date(InventoryTransaction.transaction_date) <= end_date,
                (InventoryTransaction.created_by == user_id) | (InventoryTransaction.created_by.is_(None))
            )
        ).all()
        
        # Group by product and warehouse
        shrinkage_data = {}
        
        for adj in adjustments:
            key = f"{adj.product_id}_{adj.from_simple_warehouse_id or 0}"
            
            if key not in shrinkage_data:
                product_name = adj.product.name if adj.product else f'Product {adj.product_id}'
                warehouse_name = adj.from_simple_warehouse.name if adj.from_simple_warehouse else 'Main'
                
                shrinkage_data[key] = {
                    'product_id': adj.product_id,
                    'product_name': product_name,
                    'product_sku': adj.product.sku if adj.product else None,
                    'warehouse_id': adj.from_simple_warehouse_id,
                    'warehouse_name': warehouse_name,
                    'total_adjustments': 0,
                    'negative_adjustments': 0,
                    'positive_adjustments': 0,
                    'total_shrinkage_qty': 0,
                    'total_shrinkage_value': 0,
                    'adjustment_count': 0,
                    'last_adjustment_date': None
                }
            
            data = shrinkage_data[key]
            data['adjustment_count'] += 1
            data['total_adjustments'] += adj.quantity
            
            if adj.quantity < 0:
                data['negative_adjustments'] += abs(adj.quantity)
                data['total_shrinkage_qty'] += abs(adj.quantity)
                data['total_shrinkage_value'] += abs(adj.total_cost)
            else:
                data['positive_adjustments'] += adj.quantity
            
            # Update last adjustment date
            adj_date = adj.transaction_date.date()
            if not data['last_adjustment_date'] or adj_date > data['last_adjustment_date']:
                data['last_adjustment_date'] = adj_date
        
        # Convert to list and sort by shrinkage value
        shrinkage_list = list(shrinkage_data.values())
        shrinkage_list.sort(key=lambda x: x['total_shrinkage_value'], reverse=True)
        
        # Calculate totals
        total_shrinkage_value = sum(item['total_shrinkage_value'] for item in shrinkage_list)
        total_shrinkage_qty = sum(item['total_shrinkage_qty'] for item in shrinkage_list)
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_shrinkage_value': total_shrinkage_value,
                    'total_shrinkage_qty': total_shrinkage_qty,
                    'products_affected': len(shrinkage_list),
                    'total_adjustments': len(adjustments)
                },
                'shrinkage_by_product': shrinkage_list[:20],  # Top 20
                'top_shrinkage_products': [
                    item for item in shrinkage_list[:5] if item['total_shrinkage_value'] > 0
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting shrinkage analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@variance_reports_bp.route('/cogs-analysis', methods=['GET'])
def get_cogs_analysis():
    """
    Get COGS analysis per period with cost method breakdown
    GET /api/inventory/variance/cogs-analysis?period=current_month
    """
    try:
        period = request.args.get('period', 'current_month')
        
        # Calculate date range based on period
        today = date.today()
        if period == 'current_month':
            start_date = today.replace(day=1)
            end_date = today
        elif period == 'last_month':
            last_month = today.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = last_month
        elif period == 'current_quarter':
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=quarter_start_month, day=1)
            end_date = today
        else:
            start_date = today - timedelta(days=30)
            end_date = today
        
        # Get COGS GL entries
        cogs_accounts = ChartOfAccounts.query.filter(
            or_(
                ChartOfAccounts.account_name.ilike('%cost of goods%'),
                ChartOfAccounts.account_name.ilike('%cogs%')
            ),
            ChartOfAccounts.account_type == 'Expense'
        ).all()
        
        cogs_data = []
        total_cogs = 0
        
        for account in cogs_accounts:
            gl_entries = GeneralLedgerEntry.query.filter(
                GeneralLedgerEntry.account_id == account.id,
                GeneralLedgerEntry.entry_date >= start_date,
                GeneralLedgerEntry.entry_date <= end_date,
                GeneralLedgerEntry.status == 'posted'
            ).all()
            
            account_cogs = sum(entry.debit_amount for entry in gl_entries)
            total_cogs += account_cogs
            
            if account_cogs > 0:
                cogs_data.append({
                    'account_name': account.account_name,
                    'account_code': account.account_code,
                    'cogs_amount': account_cogs,
                    'transaction_count': len(gl_entries),
                    'average_transaction': account_cogs / len(gl_entries) if gl_entries else 0
                })
        
        # Get cost layer depletion details
        cost_depletions = CostLayerTransaction.query.filter(
            CostLayerTransaction.transaction_date >= start_date,
            CostLayerTransaction.transaction_date <= end_date,
            CostLayerTransaction.transaction_type == 'issue'
        ).all()
        
        # Analyze cost methods used
        cost_method_analysis = {}
        for depletion in cost_depletions:
            cost_layer = depletion.cost_layer
            if cost_layer and cost_layer.product:
                method = cost_layer.product.cost_method
                
                if method not in cost_method_analysis:
                    cost_method_analysis[method] = {
                        'total_cost': 0,
                        'total_quantity': 0,
                        'transaction_count': 0
                    }
                
                cost_method_analysis[method]['total_cost'] += depletion.cost_depleted
                cost_method_analysis[method]['total_quantity'] += depletion.quantity_depleted
                cost_method_analysis[method]['transaction_count'] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'period_name': period
                },
                'cogs_summary': {
                    'total_cogs': total_cogs,
                    'accounts_used': len(cogs_data),
                    'average_daily_cogs': total_cogs / max(1, (end_date - start_date).days)
                },
                'cogs_by_account': cogs_data,
                'cost_method_analysis': cost_method_analysis,
                'cost_layer_depletions': len(cost_depletions)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting COGS analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@variance_reports_bp.route('/aged-inventory', methods=['GET'])
def get_aged_inventory_report():
    """
    Get aged inventory report for cash flow impact analysis
    GET /api/inventory/variance/aged-inventory
    """
    try:
        # Get current inventory with aging analysis
        current_date = date.today()
        
        # Get latest valuation snapshots or current stock
        latest_snapshots = InventoryValuationSnapshot.query.filter(
            InventoryValuationSnapshot.snapshot_date <= current_date
        ).order_by(InventoryValuationSnapshot.snapshot_date.desc()).limit(1000).all()
        
        if not latest_snapshots:
            # Fallback to current stock levels
            stock_levels = StockLevel.query.filter(StockLevel.quantity_on_hand > 0).all()
            aged_inventory = []
            
            for stock in stock_levels:
                # Get last transaction date for aging
                last_transaction = InventoryTransaction.query.filter(
                    InventoryTransaction.product_id == stock.product_id
                ).order_by(InventoryTransaction.transaction_date.desc()).first()
                
                days_on_hand = 0
                if last_transaction:
                    days_on_hand = (current_date - last_transaction.transaction_date.date()).days
                
                # Determine aging bucket
                if days_on_hand <= 30:
                    aging_bucket = '0-30 days'
                elif days_on_hand <= 60:
                    aging_bucket = '31-60 days'
                elif days_on_hand <= 90:
                    aging_bucket = '61-90 days'
                elif days_on_hand <= 180:
                    aging_bucket = '91-180 days'
                else:
                    aging_bucket = '180+ days'
                
                aged_inventory.append({
                    'product_id': stock.product_id,
                    'product_name': stock.product.name if stock.product else f'Product {stock.product_id}',
                    'product_sku': stock.product.sku if stock.product else None,
                    'quantity_on_hand': stock.quantity_on_hand,
                    'unit_cost': stock.unit_cost,
                    'total_value': stock.total_value,
                    'days_on_hand': days_on_hand,
                    'aging_bucket': aging_bucket,
                    'last_movement_date': last_transaction.transaction_date.date().isoformat() if last_transaction else None,
                    'warehouse': stock.simple_warehouse.name if stock.simple_warehouse else 'Main'
                })
        else:
            # Use valuation snapshots
            aged_inventory = []
            for snapshot in latest_snapshots:
                aged_inventory.append({
                    'product_id': snapshot.product_id,
                    'product_name': snapshot.product.name if snapshot.product else f'Product {snapshot.product_id}',
                    'quantity_on_hand': snapshot.active_quantity,
                    'unit_cost': snapshot.active_unit_cost,
                    'total_value': snapshot.active_total_value,
                    'days_on_hand': snapshot.days_on_hand,
                    'aging_bucket': self._get_aging_bucket(snapshot.days_on_hand),
                    'aging_category': snapshot.aging_category,
                    'cost_method': snapshot.active_cost_method
                })
        
        # Group by aging buckets
        aging_summary = {}
        for item in aged_inventory:
            bucket = item['aging_bucket']
            if bucket not in aging_summary:
                aging_summary[bucket] = {
                    'product_count': 0,
                    'total_quantity': 0,
                    'total_value': 0
                }
            
            aging_summary[bucket]['product_count'] += 1
            aging_summary[bucket]['total_quantity'] += item['quantity_on_hand']
            aging_summary[bucket]['total_value'] += item['total_value']
        
        # Sort inventory by value (highest first)
        aged_inventory.sort(key=lambda x: x['total_value'], reverse=True)
        
        # Calculate cash flow impact
        dead_stock_value = sum(item['total_value'] for item in aged_inventory if item.get('days_on_hand', 0) > 180)
        slow_moving_value = sum(item['total_value'] for item in aged_inventory if 90 <= item.get('days_on_hand', 0) <= 180)
        
        return jsonify({
            'success': True,
            'data': {
                'as_of_date': current_date.isoformat(),
                'aging_summary': aging_summary,
                'aged_inventory': aged_inventory[:50],  # Top 50 by value
                'cash_flow_impact': {
                    'dead_stock_value': dead_stock_value,
                    'slow_moving_value': slow_moving_value,
                    'total_at_risk': dead_stock_value + slow_moving_value,
                    'percentage_at_risk': ((dead_stock_value + slow_moving_value) / sum(item['total_value'] for item in aged_inventory) * 100) if aged_inventory else 0
                },
                'recommendations': self._get_aging_recommendations(dead_stock_value, slow_moving_value)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting aged inventory report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@variance_reports_bp.route('/cost-method-comparison', methods=['GET'])
def get_cost_method_comparison():
    """
    Compare inventory valuation using different cost methods
    GET /api/inventory/variance/cost-method-comparison
    """
    try:
        # Generate valuation snapshot for today
        costing_service = InventoryCostingService()
        snapshot_result = costing_service.create_valuation_snapshot()
        
        if not snapshot_result.get('success'):
            return jsonify({
                'success': False,
                'error': snapshot_result.get('error', 'Failed to create valuation snapshot')
            }), 500
        
        # Get the latest snapshots
        latest_snapshots = InventoryValuationSnapshot.query.filter(
            InventoryValuationSnapshot.snapshot_date == date.today()
        ).all()
        
        # Aggregate by cost method
        method_totals = {
            'FIFO': {'total_value': 0, 'product_count': 0},
            'LIFO': {'total_value': 0, 'product_count': 0},
            'AVERAGE': {'total_value': 0, 'product_count': 0},
            'STANDARD': {'total_value': 0, 'product_count': 0}
        }
        
        product_comparisons = []
        
        for snapshot in latest_snapshots:
            method_totals['FIFO']['total_value'] += snapshot.fifo_total_value
            method_totals['LIFO']['total_value'] += snapshot.lifo_total_value
            method_totals['AVERAGE']['total_value'] += snapshot.average_total_value
            method_totals['STANDARD']['total_value'] += snapshot.standard_total_value
            
            for method in method_totals:
                method_totals[method]['product_count'] += 1
            
            # Individual product comparison
            product_comparisons.append({
                'product_id': snapshot.product_id,
                'product_name': snapshot.product.name if snapshot.product else f'Product {snapshot.product_id}',
                'quantity': snapshot.active_quantity,
                'fifo_value': snapshot.fifo_total_value,
                'lifo_value': snapshot.lifo_total_value,
                'average_value': snapshot.average_total_value,
                'standard_value': snapshot.standard_total_value,
                'active_method': snapshot.active_cost_method,
                'active_value': snapshot.active_total_value,
                'fifo_vs_avg_variance': snapshot.method_variance_fifo_vs_avg,
                'lifo_vs_avg_variance': snapshot.method_variance_lifo_vs_avg
            })
        
        # Calculate overall variances
        fifo_total = method_totals['FIFO']['total_value']
        lifo_total = method_totals['LIFO']['total_value']
        avg_total = method_totals['AVERAGE']['total_value']
        
        return jsonify({
            'success': True,
            'data': {
                'snapshot_date': date.today().isoformat(),
                'method_totals': method_totals,
                'overall_variances': {
                    'fifo_vs_lifo': fifo_total - lifo_total,
                    'fifo_vs_average': fifo_total - avg_total,
                    'lifo_vs_average': lifo_total - avg_total,
                    'fifo_vs_lifo_percentage': ((fifo_total - lifo_total) / fifo_total * 100) if fifo_total > 0 else 0
                },
                'product_comparisons': product_comparisons[:20],  # Top 20 by value
                'valuation_impact': {
                    'highest_variance_product': max(product_comparisons, key=lambda x: abs(x['fifo_vs_avg_variance'])) if product_comparisons else None,
                    'total_products_analyzed': len(product_comparisons)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting cost method comparison: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@variance_reports_bp.route('/variance-dashboard', methods=['GET'])
def get_variance_dashboard():
    """
    Get comprehensive variance dashboard combining all analyses
    GET /api/inventory/variance/variance-dashboard
    """
    try:
        # Get all variance reports
        inventory_gl_variance = get_inventory_gl_variance()
        shrinkage_analysis = get_shrinkage_analysis()
        cogs_analysis = get_cogs_analysis()
        aged_inventory = get_aged_inventory_report()
        
        # Extract data from responses
        gl_variance_data = inventory_gl_variance.get_json().get('data', {})
        shrinkage_data = shrinkage_analysis.get_json().get('data', {})
        cogs_data = cogs_analysis.get_json().get('data', {})
        aging_data = aged_inventory.get_json().get('data', {})
        
        # Create comprehensive dashboard
        dashboard = {
            'last_updated': datetime.utcnow().isoformat(),
            'overall_health': 'HEALTHY',
            'key_metrics': {
                'inventory_gl_variance': gl_variance_data.get('variance', 0),
                'total_shrinkage_value': shrinkage_data.get('summary', {}).get('total_shrinkage_value', 0),
                'total_cogs': cogs_data.get('cogs_summary', {}).get('total_cogs', 0),
                'dead_stock_value': aging_data.get('cash_flow_impact', {}).get('dead_stock_value', 0)
            },
            'alerts': [],
            'recommendations': []
        }
        
        # Generate alerts based on thresholds
        if abs(gl_variance_data.get('variance', 0)) > 1000:
            dashboard['alerts'].append({
                'type': 'GL_VARIANCE',
                'severity': 'HIGH',
                'message': f"Large inventory-GL variance: ${gl_variance_data.get('variance', 0):,.2f}"
            })
            dashboard['overall_health'] = 'ATTENTION_NEEDED'
        
        if shrinkage_data.get('summary', {}).get('total_shrinkage_value', 0) > 500:
            dashboard['alerts'].append({
                'type': 'SHRINKAGE',
                'severity': 'MEDIUM',
                'message': f"Significant shrinkage detected: ${shrinkage_data.get('summary', {}).get('total_shrinkage_value', 0):,.2f}"
            })
        
        if aging_data.get('cash_flow_impact', {}).get('percentage_at_risk', 0) > 20:
            dashboard['alerts'].append({
                'type': 'AGED_INVENTORY',
                'severity': 'MEDIUM',
                'message': f"High aged inventory: {aging_data.get('cash_flow_impact', {}).get('percentage_at_risk', 0):.1f}% at risk"
            })
        
        return jsonify({
            'success': True,
            'data': {
                'dashboard': dashboard,
                'detailed_reports': {
                    'inventory_gl_variance': gl_variance_data,
                    'shrinkage_analysis': shrinkage_data.get('summary', {}),
                    'cogs_analysis': cogs_data.get('cogs_summary', {}),
                    'aged_inventory': aging_data.get('cash_flow_impact', {})
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting variance dashboard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _get_aging_bucket(days_on_hand: int) -> str:
    """Get aging bucket for days on hand"""
    if days_on_hand <= 30:
        return '0-30 days'
    elif days_on_hand <= 60:
        return '31-60 days'
    elif days_on_hand <= 90:
        return '61-90 days'
    elif days_on_hand <= 180:
        return '91-180 days'
    else:
        return '180+ days'

def _get_aging_recommendations(dead_stock_value: float, slow_moving_value: float) -> List[str]:
    """Get recommendations based on aging analysis"""
    recommendations = []
    
    if dead_stock_value > 1000:
        recommendations.append(f"Consider liquidating ${dead_stock_value:,.2f} in dead stock to improve cash flow")
    
    if slow_moving_value > 2000:
        recommendations.append(f"Review ${slow_moving_value:,.2f} in slow-moving inventory for promotional opportunities")
    
    if (dead_stock_value + slow_moving_value) > 5000:
        recommendations.append("Implement inventory optimization strategies to reduce carrying costs")
    
    return recommendations
