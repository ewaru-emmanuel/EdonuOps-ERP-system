# Dashboard routes for EdonuOps ERP
from flask import Blueprint, jsonify

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary data"""
    return jsonify({
        'status': 'success',
        'data': {
            'totalRevenue': 1250000,
            'totalOrders': 1250,
            'totalCustomers': 850,
            'totalProducts': 450,
            'totalEmployees': 120,
            'totalLeads': 250,
            'totalOpportunities': 75,
            'systemStatus': 'operational',
            'recentActivity': [
                {'type': 'order', 'message': 'New order #1234 received', 'time': '2 minutes ago'},
                {'type': 'customer', 'message': 'New customer registered', 'time': '5 minutes ago'},
                {'type': 'payment', 'message': 'Payment processed for order #1233', 'time': '10 minutes ago'}
            ]
        },
        'message': 'Dashboard summary ready'
    })
