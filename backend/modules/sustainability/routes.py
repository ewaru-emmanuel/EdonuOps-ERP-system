from flask import Blueprint, request, jsonify
from app import db
from .models import EnvironmentalMetric, SocialMetric, GovernanceMetric, ESGReport
from datetime import datetime

sustainability_bp = Blueprint('sustainability', __name__)

# Environmental Metrics
@sustainability_bp.route('/environmental', methods=['GET'])
def get_environmental_metrics():
    try:
        metrics = EnvironmentalMetric.query.all()
        return jsonify([{
            'id': m.id,
            'metric_name': m.metric_name,
            'value': m.value,
            'unit': m.unit,
            'category': m.category,
            'reporting_period': m.reporting_period,
            'status': m.status,
            'created_at': m.created_at.isoformat()
        } for m in metrics]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/environmental', methods=['POST'])
def create_environmental_metric():
    try:
        data = request.get_json()
        metric = EnvironmentalMetric(
            metric_name=data['metric_name'],
            value=data['value'],
            unit=data['unit'],
            category=data['category'],
            reporting_period=data['reporting_period'],
            status=data.get('status', 'Active')
        )
        db.session.add(metric)
        db.session.commit()
        return jsonify({'message': 'Environmental metric created successfully', 'id': metric.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/environmental/<int:metric_id>', methods=['PUT'])
def update_environmental_metric(metric_id):
    try:
        metric = EnvironmentalMetric.query.get_or_404(metric_id)
        data = request.get_json()
        
        metric.metric_name = data.get('metric_name', metric.metric_name)
        metric.value = data.get('value', metric.value)
        metric.unit = data.get('unit', metric.unit)
        metric.category = data.get('category', metric.category)
        metric.reporting_period = data.get('reporting_period', metric.reporting_period)
        metric.status = data.get('status', metric.status)
        metric.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Environmental metric updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/environmental/<int:metric_id>', methods=['DELETE'])
def delete_environmental_metric(metric_id):
    try:
        metric = EnvironmentalMetric.query.get_or_404(metric_id)
        db.session.delete(metric)
        db.session.commit()
        return jsonify({'message': 'Environmental metric deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Social Metrics
@sustainability_bp.route('/social', methods=['GET'])
def get_social_metrics():
    try:
        metrics = SocialMetric.query.all()
        return jsonify([{
            'id': m.id,
            'metric_name': m.metric_name,
            'value': m.value,
            'unit': m.unit,
            'category': m.category,
            'reporting_period': m.reporting_period,
            'status': m.status,
            'created_at': m.created_at.isoformat()
        } for m in metrics]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/social', methods=['POST'])
def create_social_metric():
    try:
        data = request.get_json()
        metric = SocialMetric(
            metric_name=data['metric_name'],
            value=data['value'],
            unit=data['unit'],
            category=data['category'],
            reporting_period=data['reporting_period'],
            status=data.get('status', 'Active')
        )
        db.session.add(metric)
        db.session.commit()
        return jsonify({'message': 'Social metric created successfully', 'id': metric.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/social/<int:metric_id>', methods=['PUT'])
def update_social_metric(metric_id):
    try:
        metric = SocialMetric.query.get_or_404(metric_id)
        data = request.get_json()
        
        metric.metric_name = data.get('metric_name', metric.metric_name)
        metric.value = data.get('value', metric.value)
        metric.unit = data.get('unit', metric.unit)
        metric.category = data.get('category', metric.category)
        metric.reporting_period = data.get('reporting_period', metric.reporting_period)
        metric.status = data.get('status', metric.status)
        metric.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Social metric updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/social/<int:metric_id>', methods=['DELETE'])
def delete_social_metric(metric_id):
    try:
        metric = SocialMetric.query.get_or_404(metric_id)
        db.session.delete(metric)
        db.session.commit()
        return jsonify({'message': 'Social metric deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Governance Metrics
@sustainability_bp.route('/governance', methods=['GET'])
def get_governance_metrics():
    try:
        metrics = GovernanceMetric.query.all()
        return jsonify([{
            'id': m.id,
            'metric_name': m.metric_name,
            'value': m.value,
            'unit': m.unit,
            'category': m.category,
            'reporting_period': m.reporting_period,
            'status': m.status,
            'created_at': m.created_at.isoformat()
        } for m in metrics]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/governance', methods=['POST'])
def create_governance_metric():
    try:
        data = request.get_json()
        metric = GovernanceMetric(
            metric_name=data['metric_name'],
            value=data['value'],
            unit=data['unit'],
            category=data['category'],
            reporting_period=data['reporting_period'],
            status=data.get('status', 'Active')
        )
        db.session.add(metric)
        db.session.commit()
        return jsonify({'message': 'Governance metric created successfully', 'id': metric.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/governance/<int:metric_id>', methods=['PUT'])
def update_governance_metric(metric_id):
    try:
        metric = GovernanceMetric.query.get_or_404(metric_id)
        data = request.get_json()
        
        metric.metric_name = data.get('metric_name', metric.metric_name)
        metric.value = data.get('value', metric.value)
        metric.unit = data.get('unit', metric.unit)
        metric.category = data.get('category', metric.category)
        metric.reporting_period = data.get('reporting_period', metric.reporting_period)
        metric.status = data.get('status', metric.status)
        metric.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Governance metric updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/governance/<int:metric_id>', methods=['DELETE'])
def delete_governance_metric(metric_id):
    try:
        metric = GovernanceMetric.query.get_or_404(metric_id)
        db.session.delete(metric)
        db.session.commit()
        return jsonify({'message': 'Governance metric deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ESG Reports
@sustainability_bp.route('/reports', methods=['GET'])
def get_esg_reports():
    try:
        reports = ESGReport.query.all()
        return jsonify([{
            'id': r.id,
            'report_title': r.report_title,
            'report_type': r.report_type,
            'reporting_period': r.reporting_period,
            'esg_rating': r.esg_rating,
            'status': r.status,
            'created_at': r.created_at.isoformat()
        } for r in reports]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/reports', methods=['POST'])
def create_esg_report():
    try:
        data = request.get_json()
        report = ESGReport(
            report_title=data['report_title'],
            report_type=data['report_type'],
            reporting_period=data['reporting_period'],
            esg_rating=data.get('esg_rating', ''),
            status=data.get('status', 'Draft')
        )
        db.session.add(report)
        db.session.commit()
        return jsonify({'message': 'ESG report created successfully', 'id': report.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_esg_report(report_id):
    try:
        report = ESGReport.query.get_or_404(report_id)
        data = request.get_json()
        
        report.report_title = data.get('report_title', report.report_title)
        report.report_type = data.get('report_type', report.report_type)
        report.reporting_period = data.get('reporting_period', report.reporting_period)
        report.esg_rating = data.get('esg_rating', report.esg_rating)
        report.status = data.get('status', report.status)
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'ESG report updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sustainability_bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_esg_report(report_id):
    try:
        report = ESGReport.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'ESG report deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
