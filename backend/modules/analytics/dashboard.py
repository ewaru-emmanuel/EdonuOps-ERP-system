# backend/modules/analytics/dashboard.py

from flask import Blueprint, request, jsonify
from modules.core.permissions import require_permission
from .builder import build_sales_report, build_inventory_report

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/sales_report", methods=["GET"])
@require_permission('sales_report.reports.read')
def get_sales_report():
    # In a real-world scenario, you would get date parameters from the request
    # For now, we use a placeholder date range.
    start_date = "2025-01-01"
    end_date = "2025-01-31"
    
    report = build_sales_report(start_date, end_date)
    return jsonify(report), 200

@analytics_bp.route("/inventory_report", methods=["GET"])
@require_permission('inventory_report.reports.read')
def get_inventory_report():
    report = build_inventory_report()
    return jsonify(report), 200