from flask import Blueprint, request, jsonify
from app import db
from .models import AIPrediction, AIInsight, AIRecommendation
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

# Predictions
@ai_bp.route('/predictions', methods=['GET'])
def get_predictions():
    try:
        predictions = AIPrediction.query.all()
        return jsonify([{
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'prediction_type': p.prediction_type,
            'accuracy': p.accuracy,
            'confidence_score': p.confidence_score,
            'status': p.status,
            'created_at': p.created_at.isoformat()
        } for p in predictions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/predictions', methods=['POST'])
def create_prediction():
    try:
        data = request.get_json()
        prediction = AIPrediction(
            title=data['title'],
            description=data.get('description', ''),
            prediction_type=data['prediction_type'],
            accuracy=data.get('accuracy', 0.0),
            confidence_score=data.get('confidence_score', 0.0),
            status=data.get('status', 'Active')
        )
        db.session.add(prediction)
        db.session.commit()
        return jsonify({'message': 'Prediction created successfully', 'id': prediction.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/predictions/<int:prediction_id>', methods=['PUT'])
def update_prediction(prediction_id):
    try:
        prediction = AIPrediction.query.get_or_404(prediction_id)
        data = request.get_json()
        
        prediction.title = data.get('title', prediction.title)
        prediction.description = data.get('description', prediction.description)
        prediction.prediction_type = data.get('prediction_type', prediction.prediction_type)
        prediction.accuracy = data.get('accuracy', prediction.accuracy)
        prediction.confidence_score = data.get('confidence_score', prediction.confidence_score)
        prediction.status = data.get('status', prediction.status)
        prediction.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Prediction updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/predictions/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    try:
        prediction = AIPrediction.query.get_or_404(prediction_id)
        db.session.delete(prediction)
        db.session.commit()
        return jsonify({'message': 'Prediction deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Insights
@ai_bp.route('/insights', methods=['GET'])
def get_insights():
    try:
        insights = AIInsight.query.all()
        return jsonify([{
            'id': i.id,
            'title': i.title,
            'description': i.description,
            'insight_type': i.insight_type,
            'impact_score': i.impact_score,
            'category': i.category,
            'status': i.status,
            'created_at': i.created_at.isoformat()
        } for i in insights]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/insights', methods=['POST'])
def create_insight():
    try:
        data = request.get_json()
        insight = AIInsight(
            title=data['title'],
            description=data.get('description', ''),
            insight_type=data['insight_type'],
            impact_score=data.get('impact_score', 0.0),
            category=data.get('category', ''),
            status=data.get('status', 'Active')
        )
        db.session.add(insight)
        db.session.commit()
        return jsonify({'message': 'Insight created successfully', 'id': insight.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/insights/<int:insight_id>', methods=['PUT'])
def update_insight(insight_id):
    try:
        insight = AIInsight.query.get_or_404(insight_id)
        data = request.get_json()
        
        insight.title = data.get('title', insight.title)
        insight.description = data.get('description', insight.description)
        insight.insight_type = data.get('insight_type', insight.insight_type)
        insight.impact_score = data.get('impact_score', insight.impact_score)
        insight.category = data.get('category', insight.category)
        insight.status = data.get('status', insight.status)
        insight.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Insight updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/insights/<int:insight_id>', methods=['DELETE'])
def delete_insight(insight_id):
    try:
        insight = AIInsight.query.get_or_404(insight_id)
        db.session.delete(insight)
        db.session.commit()
        return jsonify({'message': 'Insight deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Recommendations
@ai_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    try:
        recommendations = AIRecommendation.query.all()
        return jsonify([{
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'recommendation_type': r.recommendation_type,
            'priority': r.priority,
            'implementation_status': r.implementation_status,
            'created_at': r.created_at.isoformat()
        } for r in recommendations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/recommendations', methods=['POST'])
def create_recommendation():
    try:
        data = request.get_json()
        recommendation = AIRecommendation(
            title=data['title'],
            description=data.get('description', ''),
            recommendation_type=data['recommendation_type'],
            priority=data.get('priority', 'Medium'),
            implementation_status=data.get('implementation_status', 'Pending')
        )
        db.session.add(recommendation)
        db.session.commit()
        return jsonify({'message': 'Recommendation created successfully', 'id': recommendation.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/recommendations/<int:recommendation_id>', methods=['PUT'])
def update_recommendation(recommendation_id):
    try:
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        data = request.get_json()
        
        recommendation.title = data.get('title', recommendation.title)
        recommendation.description = data.get('description', recommendation.description)
        recommendation.recommendation_type = data.get('recommendation_type', recommendation.recommendation_type)
        recommendation.priority = data.get('priority', recommendation.priority)
        recommendation.implementation_status = data.get('implementation_status', recommendation.implementation_status)
        recommendation.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Recommendation updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/recommendations/<int:recommendation_id>', methods=['DELETE'])
def delete_recommendation(recommendation_id):
    try:
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        db.session.delete(recommendation)
        db.session.commit()
        return jsonify({'message': 'Recommendation deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


