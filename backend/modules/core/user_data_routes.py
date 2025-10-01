from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from modules.core.models import User

user_data_bp = Blueprint('user_data', __name__, url_prefix='/api/user-data')

# In-memory storage for user data (replace with database table in production)
user_data_storage = {}

@user_data_bp.route('/save', methods=['POST'])
def save_user_data():
    """Save user data to database"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        data_type = data.get('data_type')
        user_data = data.get('data')
        
        if not user_id or not data_type:
            return jsonify({'error': 'user_id and data_type are required'}), 400
        
        # Get user ID from headers for security
        request_user_id = request.headers.get('X-User-ID')
        if not request_user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                request_user_id = get_jwt_identity()
            except:
                pass
        
        if not request_user_id:
            request_user_id = 1  # Default for development
        
        # Verify user can only save their own data
        if str(user_id) != str(request_user_id):
            return jsonify({'error': 'Access denied: You can only save your own data'}), 403
        
        # Store data (in production, use a proper database table)
        storage_key = f"user_{user_id}_{data_type}"
        user_data_storage[storage_key] = {
            'user_id': user_id,
            'data_type': data_type,
            'data': user_data,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        print(f"💾 Saved {data_type} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Data {data_type} saved successfully',
            'data_type': data_type,
            'user_id': user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/load/<data_type>', methods=['GET'])
def load_user_data(data_type):
    """Load user data from database"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get user ID from headers for security
        request_user_id = request.headers.get('X-User-ID')
        if not request_user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                request_user_id = get_jwt_identity()
            except:
                pass
        
        if not request_user_id:
            request_user_id = 1  # Default for development
        
        # Verify user can only load their own data
        if str(user_id) != str(request_user_id):
            return jsonify({'error': 'Access denied: You can only load your own data'}), 403
        
        # Load data (in production, use a proper database table)
        storage_key = f"user_{user_id}_{data_type}"
        stored_data = user_data_storage.get(storage_key)
        
        if stored_data:
            print(f"📂 Loaded {data_type} for user {user_id}")
            return jsonify({
                'success': True,
                'data': stored_data['data'],
                'data_type': data_type,
                'user_id': user_id,
                'updated_at': stored_data['updated_at']
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': None,
                'message': f'No data found for {data_type}'
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/all', methods=['GET'])
def get_all_user_data():
    """Get all user data from database"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get user ID from headers for security
        request_user_id = request.headers.get('X-User-ID')
        if not request_user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                request_user_id = get_jwt_identity()
            except:
                pass
        
        if not request_user_id:
            request_user_id = 1  # Default for development
        
        # Verify user can only load their own data
        if str(user_id) != str(request_user_id):
            return jsonify({'error': 'Access denied: You can only load your own data'}), 403
        
        # Get all data for user
        user_data = {}
        prefix = f"user_{user_id}_"
        
        for key, value in user_data_storage.items():
            if key.startswith(prefix):
                data_type = key.replace(prefix, '')
                user_data[data_type] = value['data']
        
        print(f"📊 Loaded all data for user {user_id}: {list(user_data.keys())}")
        
        return jsonify({
            'success': True,
            'data': user_data,
            'user_id': user_id,
            'data_types': list(user_data.keys())
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/export', methods=['GET'])
def export_user_data():
    """Export all user data"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get user ID from headers for security
        request_user_id = request.headers.get('X-User-ID')
        if not request_user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                request_user_id = get_jwt_identity()
            except:
                pass
        
        if not request_user_id:
            request_user_id = 1  # Default for development
        
        # Verify user can only export their own data
        if str(user_id) != str(request_user_id):
            return jsonify({'error': 'Access denied: You can only export your own data'}), 403
        
        # Get all data for user
        user_data = {}
        prefix = f"user_{user_id}_"
        
        for key, value in user_data_storage.items():
            if key.startswith(prefix):
                data_type = key.replace(prefix, '')
                user_data[data_type] = {
                    'data': value['data'],
                    'created_at': value['created_at'],
                    'updated_at': value['updated_at']
                }
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.utcnow().isoformat(),
            'version': '1.0',
            'data': user_data
        }
        
        print(f"📤 Exported data for user {user_id}")
        
        return jsonify({
            'success': True,
            'data': export_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/import', methods=['POST'])
def import_user_data():
    """Import user data"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        import_data = data.get('data')
        
        if not user_id or not import_data:
            return jsonify({'error': 'user_id and data are required'}), 400
        
        # Get user ID from headers for security
        request_user_id = request.headers.get('X-User-ID')
        if not request_user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                request_user_id = get_jwt_identity()
            except:
                pass
        
        if not request_user_id:
            request_user_id = 1  # Default for development
        
        # Verify user can only import to their own account
        if str(user_id) != str(request_user_id):
            return jsonify({'error': 'Access denied: You can only import to your own account'}), 403
        
        # Import each data type
        imported_count = 0
        for data_type, data_info in import_data.get('data', {}).items():
            storage_key = f"user_{user_id}_{data_type}"
            user_data_storage[storage_key] = {
                'user_id': user_id,
                'data_type': data_type,
                'data': data_info.get('data', data_info),
                'created_at': data_info.get('created_at', datetime.utcnow().isoformat()),
                'updated_at': datetime.utcnow().isoformat()
            }
            imported_count += 1
        
        print(f"📥 Imported {imported_count} data types for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Imported {imported_count} data types successfully',
            'imported_count': imported_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/delete/<data_type>', methods=['DELETE'])
def delete_user_data(data_type):
    """Delete specific user data"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get user ID from headers for security
        request_user_id = request.headers.get('X-User-ID')
        if not request_user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                request_user_id = get_jwt_identity()
            except:
                pass
        
        if not request_user_id:
            request_user_id = 1  # Default for development
        
        # Verify user can only delete their own data
        if str(user_id) != str(request_user_id):
            return jsonify({'error': 'Access denied: You can only delete your own data'}), 403
        
        # Delete data
        storage_key = f"user_{user_id}_{data_type}"
        if storage_key in user_data_storage:
            del user_data_storage[storage_key]
            print(f"🗑️ Deleted {data_type} for user {user_id}")
            return jsonify({
                'success': True,
                'message': f'Data {data_type} deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': f'Data {data_type} not found'
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/clear', methods=['DELETE'])
def clear_all_user_data():
    """Clear all user data"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get user ID from headers for security
        request_user_id = request.headers.get('X-User-ID')
        if not request_user_id:
            from flask_jwt_extended import get_jwt_identity
            try:
                request_user_id = get_jwt_identity()
            except:
                pass
        
        if not request_user_id:
            request_user_id = 1  # Default for development
        
        # Verify user can only clear their own data
        if str(user_id) != str(request_user_id):
            return jsonify({'error': 'Access denied: You can only clear your own data'}), 403
        
        # Clear all data for user
        prefix = f"user_{user_id}_"
        deleted_count = 0
        
        keys_to_delete = [key for key in user_data_storage.keys() if key.startswith(prefix)]
        for key in keys_to_delete:
            del user_data_storage[key]
            deleted_count += 1
        
        print(f"🗑️ Cleared {deleted_count} data items for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} data items successfully',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



