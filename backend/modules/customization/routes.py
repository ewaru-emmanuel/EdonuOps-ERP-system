from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.customization.models import CustomField, CustomFieldValue, CustomForm, CustomListView, UserPreference

bp = Blueprint('customization', __name__, url_prefix='/api/customization')

# Sample data
custom_fields = []
custom_field_values = []
custom_forms = []
custom_list_views = []
user_preferences = []

@bp.route('/fields', methods=['GET'])
def get_custom_fields():
    """Get custom fields for an entity type"""
    entity_type = request.args.get('entity_type')
    filtered_fields = custom_fields
    if entity_type:
        filtered_fields = [f for f in custom_fields if f.get('entity_type') == entity_type]
    return jsonify(filtered_fields)

@bp.route('/fields', methods=['POST'])
def create_custom_field():
    """Create a new custom field"""
    data = request.get_json()
    new_field = {
        "id": len(custom_fields) + 1,
        "entity_type": data.get('entity_type'),
        "field_name": data.get('field_name'),
        "field_label": data.get('field_label'),
        "field_type": data.get('field_type'),
        "field_options": data.get('field_options', {}),
        "is_required": data.get('is_required', False),
        "is_active": data.get('is_active', True),
        "display_order": data.get('display_order', 0),
        "created_by": data.get('created_by'),
        "created_at": datetime.utcnow().isoformat()
    }
    custom_fields.append(new_field)
    return jsonify(new_field), 201

@bp.route('/preferences', methods=['GET'])
def get_user_preferences():
    """Get user preferences"""
    user_id = request.args.get('user_id', type=int)
    preference_type = request.args.get('preference_type')
    
    filtered_preferences = user_preferences
    if user_id:
        filtered_preferences = [p for p in user_preferences if p.get('user_id') == user_id]
    if preference_type:
        filtered_preferences = [p for p in filtered_preferences if p.get('preference_type') == preference_type]
    
    return jsonify(filtered_preferences)

@bp.route('/preferences', methods=['POST'])
def create_user_preference():
    """Create or update user preference"""
    data = request.get_json()
    new_preference = {
        "id": len(user_preferences) + 1,
        "user_id": data.get('user_id'),
        "preference_type": data.get('preference_type'),
        "entity_type": data.get('entity_type'),
        "preference_key": data.get('preference_key'),
        "preference_value": data.get('preference_value'),
        "created_at": datetime.utcnow().isoformat()
    }
    user_preferences.append(new_preference)
    return jsonify(new_preference), 201
