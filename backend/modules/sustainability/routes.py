# Sustainability routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.sustainability.models import EnvironmentalMetric, SocialMetric, GovernanceMetric, ESGReport
from datetime import datetime

sustainability_bp = Blueprint('sustainability', __name__)

@sustainability_bp.route('/environmental', methods=['GET'])
def get_environmental():
    """Get all environmental metrics from database"""
    try:
        metrics = EnvironmentalMetric.query.all()
        return jsonify([{
            "id": metric.id,
            "metric": metric.metric,
            "value": float(metric.value) if metric.value else 0.0,
            "unit": metric.unit,
            "target": float(metric.target) if metric.target else 0.0,
            "status": metric.status,
            "created_at": metric.created_at.isoformat() if metric.created_at else None
        } for metric in metrics]), 200
    except Exception as e:
        print(f"Error fetching environmental metrics: {e}")
        return jsonify({"error": "Failed to fetch environmental metrics"}), 500

@sustainability_bp.route('/social', methods=['GET'])
def get_social():
    """Get all social metrics from database"""
    try:
        metrics = SocialMetric.query.all()
        return jsonify([{
            "id": metric.id,
            "metric": metric.metric,
            "value": float(metric.value) if metric.value else 0.0,
            "unit": metric.unit,
            "target": float(metric.target) if metric.target else 0.0,
            "status": metric.status,
            "created_at": metric.created_at.isoformat() if metric.created_at else None
        } for metric in metrics]), 200
    except Exception as e:
        print(f"Error fetching social metrics: {e}")
        return jsonify({"error": "Failed to fetch social metrics"}), 500

@sustainability_bp.route('/governance', methods=['GET'])
def get_governance():
    """Get all governance metrics from database"""
    try:
        metrics = GovernanceMetric.query.all()
        return jsonify([{
            "id": metric.id,
            "metric": metric.metric,
            "value": float(metric.value) if metric.value else 0.0,
            "unit": metric.unit,
            "target": float(metric.target) if metric.target else 0.0,
            "status": metric.status,
            "created_at": metric.created_at.isoformat() if metric.created_at else None
        } for metric in metrics]), 200
    except Exception as e:
        print(f"Error fetching governance metrics: {e}")
        return jsonify({"error": "Failed to fetch governance metrics"}), 500

@sustainability_bp.route('/reports', methods=['GET'])
def get_reports():
    """Get all ESG reports from database"""
    try:
        reports = ESGReport.query.all()
        return jsonify([{
            "id": report.id,
            "title": report.title,
            "type": report.type,
            "status": report.status,
            "date": report.date.isoformat() if report.date else None,
            "created_at": report.created_at.isoformat() if report.created_at else None
        } for report in reports]), 200
    except Exception as e:
        print(f"Error fetching ESG reports: {e}")
        return jsonify({"error": "Failed to fetch ESG reports"}), 500

@sustainability_bp.route('/environmental', methods=['POST'])
def create_environmental():
    """Create a new environmental metric in database"""
    try:
        data = request.get_json()
        new_metric = EnvironmentalMetric(
            metric=data.get('metric'),
            value=data.get('value', 0.0),
            unit=data.get('unit'),
            target=data.get('target', 0.0),
            status=data.get('status', 'on_track')
        )
        db.session.add(new_metric)
        db.session.commit()
        return jsonify({
            "message": "Environmental metric created successfully",
            "id": new_metric.id,
            "metric": {
                "id": new_metric.id,
                "metric": new_metric.metric,
                "value": float(new_metric.value) if new_metric.value else 0.0,
                "unit": new_metric.unit,
                "target": float(new_metric.target) if new_metric.target else 0.0,
                "status": new_metric.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating environmental metric: {e}")
        return jsonify({"error": "Failed to create environmental metric"}), 500

@sustainability_bp.route('/environmental/<int:metric_id>', methods=['PUT'])
def update_environmental(metric_id):
    """Update an environmental metric in database"""
    try:
        metric = EnvironmentalMetric.query.get_or_404(metric_id)
        data = request.get_json()
        
        metric.metric = data.get('metric', metric.metric)
        metric.value = data.get('value', metric.value)
        metric.unit = data.get('unit', metric.unit)
        metric.target = data.get('target', metric.target)
        metric.status = data.get('status', metric.status)
        
        db.session.commit()
        return jsonify({
            "message": "Environmental metric updated successfully",
            "metric": {
                "id": metric.id,
                "metric": metric.metric,
                "value": float(metric.value) if metric.value else 0.0,
                "unit": metric.unit,
                "target": float(metric.target) if metric.target else 0.0,
                "status": metric.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating environmental metric: {e}")
        return jsonify({"error": "Failed to update environmental metric"}), 500

@sustainability_bp.route('/environmental/<int:metric_id>', methods=['DELETE'])
def delete_environmental(metric_id):
    """Delete an environmental metric from database"""
    try:
        metric = EnvironmentalMetric.query.get_or_404(metric_id)
        db.session.delete(metric)
        db.session.commit()
        return jsonify({"message": "Environmental metric deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting environmental metric: {e}")
        return jsonify({"error": "Failed to delete environmental metric"}), 500

@sustainability_bp.route('/social', methods=['POST'])
def create_social():
    """Create a new social metric in database"""
    try:
        data = request.get_json()
        new_metric = SocialMetric(
            metric=data.get('metric'),
            value=data.get('value', 0.0),
            unit=data.get('unit'),
            target=data.get('target', 0.0),
            status=data.get('status', 'on_track')
        )
        db.session.add(new_metric)
        db.session.commit()
        return jsonify({
            "message": "Social metric created successfully",
            "id": new_metric.id,
            "metric": {
                "id": new_metric.id,
                "metric": new_metric.metric,
                "value": float(new_metric.value) if new_metric.value else 0.0,
                "unit": new_metric.unit,
                "target": float(new_metric.target) if new_metric.target else 0.0,
                "status": new_metric.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating social metric: {e}")
        return jsonify({"error": "Failed to create social metric"}), 500

@sustainability_bp.route('/social/<int:metric_id>', methods=['PUT'])
def update_social(metric_id):
    """Update a social metric in database"""
    try:
        metric = SocialMetric.query.get_or_404(metric_id)
        data = request.get_json()
        
        metric.metric = data.get('metric', metric.metric)
        metric.value = data.get('value', metric.value)
        metric.unit = data.get('unit', metric.unit)
        metric.target = data.get('target', metric.target)
        metric.status = data.get('status', metric.status)
        
        db.session.commit()
        return jsonify({
            "message": "Social metric updated successfully",
            "metric": {
                "id": metric.id,
                "metric": metric.metric,
                "value": float(metric.value) if metric.value else 0.0,
                "unit": metric.unit,
                "target": float(metric.target) if metric.target else 0.0,
                "status": metric.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating social metric: {e}")
        return jsonify({"error": "Failed to update social metric"}), 500

@sustainability_bp.route('/social/<int:metric_id>', methods=['DELETE'])
def delete_social(metric_id):
    """Delete a social metric from database"""
    try:
        metric = SocialMetric.query.get_or_404(metric_id)
        db.session.delete(metric)
        db.session.commit()
        return jsonify({"message": "Social metric deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting social metric: {e}")
        return jsonify({"error": "Failed to delete social metric"}), 500

@sustainability_bp.route('/governance', methods=['POST'])
def create_governance():
    """Create a new governance metric in database"""
    try:
        data = request.get_json()
        new_metric = GovernanceMetric(
            metric=data.get('metric'),
            value=data.get('value', 0.0),
            unit=data.get('unit'),
            target=data.get('target', 0.0),
            status=data.get('status', 'on_track')
        )
        db.session.add(new_metric)
        db.session.commit()
        return jsonify({
            "message": "Governance metric created successfully",
            "id": new_metric.id,
            "metric": {
                "id": new_metric.id,
                "metric": new_metric.metric,
                "value": float(new_metric.value) if new_metric.value else 0.0,
                "unit": new_metric.unit,
                "target": float(new_metric.target) if new_metric.target else 0.0,
                "status": new_metric.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating governance metric: {e}")
        return jsonify({"error": "Failed to create governance metric"}), 500

@sustainability_bp.route('/governance/<int:metric_id>', methods=['PUT'])
def update_governance(metric_id):
    """Update a governance metric in database"""
    try:
        metric = GovernanceMetric.query.get_or_404(metric_id)
        data = request.get_json()
        
        metric.metric = data.get('metric', metric.metric)
        metric.value = data.get('value', metric.value)
        metric.unit = data.get('unit', metric.unit)
        metric.target = data.get('target', metric.target)
        metric.status = data.get('status', metric.status)
        
        db.session.commit()
        return jsonify({
            "message": "Governance metric updated successfully",
            "metric": {
                "id": metric.id,
                "metric": metric.metric,
                "value": float(metric.value) if metric.value else 0.0,
                "unit": metric.unit,
                "target": float(metric.target) if metric.target else 0.0,
                "status": metric.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating governance metric: {e}")
        return jsonify({"error": "Failed to update governance metric"}), 500

@sustainability_bp.route('/governance/<int:metric_id>', methods=['DELETE'])
def delete_governance(metric_id):
    """Delete a governance metric from database"""
    try:
        metric = GovernanceMetric.query.get_or_404(metric_id)
        db.session.delete(metric)
        db.session.commit()
        return jsonify({"message": "Governance metric deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting governance metric: {e}")
        return jsonify({"error": "Failed to delete governance metric"}), 500

@sustainability_bp.route('/reports', methods=['POST'])
def create_report():
    """Create a new ESG report in database"""
    try:
        data = request.get_json()
        new_report = ESGReport(
            title=data.get('title'),
            type=data.get('type'),
            status=data.get('status', 'draft'),
            date=datetime.fromisoformat(data.get('date')) if data.get('date') else datetime.utcnow()
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({
            "message": "ESG report created successfully",
            "id": new_report.id,
            "report": {
                "id": new_report.id,
                "title": new_report.title,
                "type": new_report.type,
                "status": new_report.status,
                "date": new_report.date.isoformat() if new_report.date else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating ESG report: {e}")
        return jsonify({"error": "Failed to create ESG report"}), 500

@sustainability_bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Update an ESG report in database"""
    try:
        report = ESGReport.query.get_or_404(report_id)
        data = request.get_json()
        
        report.title = data.get('title', report.title)
        report.type = data.get('type', report.type)
        report.status = data.get('status', report.status)
        report.date = datetime.fromisoformat(data.get('date')) if data.get('date') else report.date
        
        db.session.commit()
        return jsonify({
            "message": "ESG report updated successfully",
            "report": {
                "id": report.id,
                "title": report.title,
                "type": report.type,
                "status": report.status,
                "date": report.date.isoformat() if report.date else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating ESG report: {e}")
        return jsonify({"error": "Failed to update ESG report"}), 500

@sustainability_bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete an ESG report from database"""
    try:
        report = ESGReport.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        return jsonify({"message": "ESG report deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting ESG report: {e}")
        return jsonify({"error": "Failed to delete ESG report"}), 500
