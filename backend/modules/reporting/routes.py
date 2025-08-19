# backend/modules/reporting/routes.py

from flask import Blueprint, request, jsonify
from app import db
from .models import Report
from ..analytics.builder import build_sales_report, build_inventory_report

reporting_bp = Blueprint("reporting", __name__)

@reporting_bp.route("/generate", methods=["POST"])
def generate_report():
    data = request.get_json()
    report_name = data.get("report_name")
    report_type = data.get("report_type")
    parameters = data.get("parameters")

    if not report_name or not report_type:
        return jsonify({"message": "Report name and type are required"}), 400

    report_data = {}
    if report_type == "sales":
        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date")
        if not start_date or not end_date:
            return jsonify({"message": "Start and end dates are required for sales report"}), 400
        report_data = build_sales_report(start_date, end_date)
    elif report_type == "inventory":
        report_data = build_inventory_report()
    else:
        return jsonify({"message": "Invalid report type"}), 400

    new_report = Report(report_name=report_name, report_type=report_type, parameters=parameters)
    db.session.add(new_report)
    db.session.commit()
    
    return jsonify({"message": "Report generated successfully", "report_id": new_report.id, "report_data": report_data}), 201

@reporting_bp.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        return jsonify({"message": "Report not found"}), 404
    
    # In a real-world app, you would retrieve the actual report data,
    # but for this example, we'll just return the metadata.
    return jsonify({
        "id": report.id,
        "report_name": report.report_name,
        "report_type": report.report_type,
        "generated_at": report.generated_at,
        "parameters": report.parameters
    }), 200