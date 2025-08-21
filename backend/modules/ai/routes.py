# AI routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.ai.models import AIPrediction, AIInsight, AIRecommendation
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/predictions', methods=['GET'])
def get_predictions():
    """Get all AI predictions from database"""
    try:
        predictions = AIPrediction.query.all()
        return jsonify([{
            "id": prediction.id,
            "type": prediction.type,
            "title": prediction.title,
            "description": prediction.description,
            "accuracy": float(prediction.accuracy) if prediction.accuracy else 0.0,
            "status": prediction.status,
            "created_at": prediction.created_at.isoformat() if prediction.created_at else None
        } for prediction in predictions]), 200
    except Exception as e:
        print(f"Error fetching AI predictions: {e}")
        return jsonify({"error": "Failed to fetch AI predictions"}), 500

@ai_bp.route('/insights', methods=['GET'])
def get_insights():
    """Get all AI insights from database"""
    try:
        insights = AIInsight.query.all()
        return jsonify([{
            "id": insight.id,
            "category": insight.category,
            "title": insight.title,
            "description": insight.description,
            "impact_score": float(insight.impact_score) if insight.impact_score else 0.0,
            "status": insight.status,
            "created_at": insight.created_at.isoformat() if insight.created_at else None
        } for insight in insights]), 200
    except Exception as e:
        print(f"Error fetching AI insights: {e}")
        return jsonify({"error": "Failed to fetch AI insights"}), 500

@ai_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get all AI recommendations from database"""
    try:
        recommendations = AIRecommendation.query.all()
        return jsonify([{
            "id": recommendation.id,
            "type": recommendation.type,
            "title": recommendation.title,
            "description": recommendation.description,
            "confidence": float(recommendation.confidence) if recommendation.confidence else 0.0,
            "status": recommendation.status,
            "created_at": recommendation.created_at.isoformat() if recommendation.created_at else None
        } for recommendation in recommendations]), 200
    except Exception as e:
        print(f"Error fetching AI recommendations: {e}")
        return jsonify({"error": "Failed to fetch AI recommendations"}), 500

@ai_bp.route('/predictions', methods=['POST'])
def create_prediction():
    """Create a new AI prediction in database"""
    try:
        data = request.get_json()
        new_prediction = AIPrediction(
            type=data.get('type'),
            title=data.get('title'),
            description=data.get('description'),
            accuracy=data.get('accuracy', 0.0),
            status=data.get('status', 'active')
        )
        db.session.add(new_prediction)
        db.session.commit()
        return jsonify({
            "message": "AI prediction created successfully",
            "id": new_prediction.id,
            "prediction": {
                "id": new_prediction.id,
                "type": new_prediction.type,
                "title": new_prediction.title,
                "description": new_prediction.description,
                "accuracy": float(new_prediction.accuracy) if new_prediction.accuracy else 0.0,
                "status": new_prediction.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating AI prediction: {e}")
        return jsonify({"error": "Failed to create AI prediction"}), 500

@ai_bp.route('/predictions/<int:prediction_id>', methods=['PUT'])
def update_prediction(prediction_id):
    """Update an AI prediction in database"""
    try:
        prediction = AIPrediction.query.get_or_404(prediction_id)
        data = request.get_json()
        
        prediction.type = data.get('type', prediction.type)
        prediction.title = data.get('title', prediction.title)
        prediction.description = data.get('description', prediction.description)
        prediction.accuracy = data.get('accuracy', prediction.accuracy)
        prediction.status = data.get('status', prediction.status)
        
        db.session.commit()
        return jsonify({
            "message": "AI prediction updated successfully",
            "prediction": {
                "id": prediction.id,
                "type": prediction.type,
                "title": prediction.title,
                "description": prediction.description,
                "accuracy": float(prediction.accuracy) if prediction.accuracy else 0.0,
                "status": prediction.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating AI prediction: {e}")
        return jsonify({"error": "Failed to update AI prediction"}), 500

@ai_bp.route('/predictions/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    """Delete an AI prediction from database"""
    try:
        prediction = AIPrediction.query.get_or_404(prediction_id)
        db.session.delete(prediction)
        db.session.commit()
        return jsonify({"message": "AI prediction deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting AI prediction: {e}")
        return jsonify({"error": "Failed to delete AI prediction"}), 500

@ai_bp.route('/insights', methods=['POST'])
def create_insight():
    """Create a new AI insight in database"""
    try:
        data = request.get_json()
        new_insight = AIInsight(
            category=data.get('category'),
            title=data.get('title'),
            description=data.get('description'),
            impact_score=data.get('impact_score', 0.0),
            status=data.get('status', 'active')
        )
        db.session.add(new_insight)
        db.session.commit()
        return jsonify({
            "message": "AI insight created successfully",
            "id": new_insight.id,
            "insight": {
                "id": new_insight.id,
                "category": new_insight.category,
                "title": new_insight.title,
                "description": new_insight.description,
                "impact_score": float(new_insight.impact_score) if new_insight.impact_score else 0.0,
                "status": new_insight.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating AI insight: {e}")
        return jsonify({"error": "Failed to create AI insight"}), 500

@ai_bp.route('/insights/<int:insight_id>', methods=['PUT'])
def update_insight(insight_id):
    """Update an AI insight in database"""
    try:
        insight = AIInsight.query.get_or_404(insight_id)
        data = request.get_json()
        
        insight.category = data.get('category', insight.category)
        insight.title = data.get('title', insight.title)
        insight.description = data.get('description', insight.description)
        insight.impact_score = data.get('impact_score', insight.impact_score)
        insight.status = data.get('status', insight.status)
        
        db.session.commit()
        return jsonify({
            "message": "AI insight updated successfully",
            "insight": {
                "id": insight.id,
                "category": insight.category,
                "title": insight.title,
                "description": insight.description,
                "impact_score": float(insight.impact_score) if insight.impact_score else 0.0,
                "status": insight.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating AI insight: {e}")
        return jsonify({"error": "Failed to update AI insight"}), 500

@ai_bp.route('/insights/<int:insight_id>', methods=['DELETE'])
def delete_insight(insight_id):
    """Delete an AI insight from database"""
    try:
        insight = AIInsight.query.get_or_404(insight_id)
        db.session.delete(insight)
        db.session.commit()
        return jsonify({"message": "AI insight deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting AI insight: {e}")
        return jsonify({"error": "Failed to delete AI insight"}), 500

@ai_bp.route('/recommendations', methods=['POST'])
def create_recommendation():
    """Create a new AI recommendation in database"""
    try:
        data = request.get_json()
        new_recommendation = AIRecommendation(
            type=data.get('type'),
            title=data.get('title'),
            description=data.get('description'),
            confidence=data.get('confidence', 0.0),
            status=data.get('status', 'active')
        )
        db.session.add(new_recommendation)
        db.session.commit()
        return jsonify({
            "message": "AI recommendation created successfully",
            "id": new_recommendation.id,
            "recommendation": {
                "id": new_recommendation.id,
                "type": new_recommendation.type,
                "title": new_recommendation.title,
                "description": new_recommendation.description,
                "confidence": float(new_recommendation.confidence) if new_recommendation.confidence else 0.0,
                "status": new_recommendation.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating AI recommendation: {e}")
        return jsonify({"error": "Failed to create AI recommendation"}), 500

@ai_bp.route('/recommendations/<int:recommendation_id>', methods=['PUT'])
def update_recommendation(recommendation_id):
    """Update an AI recommendation in database"""
    try:
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        data = request.get_json()
        
        recommendation.type = data.get('type', recommendation.type)
        recommendation.title = data.get('title', recommendation.title)
        recommendation.description = data.get('description', recommendation.description)
        recommendation.confidence = data.get('confidence', recommendation.confidence)
        recommendation.status = data.get('status', recommendation.status)
        
        db.session.commit()
        return jsonify({
            "message": "AI recommendation updated successfully",
            "recommendation": {
                "id": recommendation.id,
                "type": recommendation.type,
                "title": recommendation.title,
                "description": recommendation.description,
                "confidence": float(recommendation.confidence) if recommendation.confidence else 0.0,
                "status": recommendation.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating AI recommendation: {e}")
        return jsonify({"error": "Failed to update AI recommendation"}), 500

@ai_bp.route('/recommendations/<int:recommendation_id>', methods=['DELETE'])
def delete_recommendation(recommendation_id):
    """Delete an AI recommendation from database"""
    try:
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        db.session.delete(recommendation)
        db.session.commit()
        return jsonify({"message": "AI recommendation deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting AI recommendation: {e}")
        return jsonify({"error": "Failed to delete AI recommendation"}), 500


