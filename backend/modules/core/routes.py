# Core routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app import db
from modules.core.models import SystemSetting
from modules.core.tenant_helpers import get_current_user_tenant_id
from modules.core.tenant_sql_helper import tenant_sql_fetchone, tenant_sql_fetchall

core_bp = Blueprint('core', __name__)

@core_bp.route('/health', methods=['GET'])
def health_check():
    """Core health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'core',
        'message': 'Core service is running'
    })

@core_bp.route('/version', methods=['GET'])
def get_version():
    """Get application version"""
    return jsonify({
        'version': '1.0.0',
        'name': 'EdonuOps ERP',
        'description': 'Enterprise Resource Planning System'
    })

@core_bp.route('/settings/currency', methods=['GET', 'OPTIONS'])
def get_currency_settings():
    """Get currency settings from database only - no hardcoded defaults - TENANT-CENTRIC"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        # TENANT-CENTRIC: Get current user's tenant_id for direct lookup
        # This endpoint works without auth (returns empty if no tenant)
        try:
            tenant_id = get_current_user_tenant_id()
        except Exception:
            # No JWT context - return empty (endpoint works without auth)
            tenant_id = None
        
        if not tenant_id:
            # No tenant context - return empty
            response = jsonify({'data': {}})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        
        from sqlalchemy import text
        import json
        
        # Get currency settings - TENANT-CENTRIC: Direct lookup by tenant_id (fast, simple)
        from modules.core.tenant_sql_helper import tenant_sql_fetchone
        result = tenant_sql_fetchone(
            "SELECT data FROM system_settings WHERE section = 'currency' AND tenant_id = :tenant_id"
        )
        
        if result and result[0]:
            data = result[0]
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    data = {}
            elif data is None:
                data = {}
            
            response = jsonify({
                'success': True,
                'data': data
            })
        else:
            # No currency settings in database - return empty
            response = jsonify({
                'success': True,
                'data': {}
            })
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
            
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error getting currency settings: {e}")
        # Return empty on error, not defaults
        response = jsonify({
            'success': True,
            'data': {},
            'error': str(e)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200


# -----------------------------
# Centralized Settings API
# All settings come from database - no hardcoded defaults
# -----------------------------

# List of valid settings sections (for validation only, not defaults)
VALID_SETTINGS_SECTIONS = [
    'currency', 'tax', 'documents', 'email', 'security', 
    'localization', 'features', 'userPermissions'
]


def _get_or_create_section(section: str, tenant_id: str = None):
    """
    Get or create a settings section using tenant-centric approach:
    - Settings table stores tenant_id directly (company-wide)
    - Direct lookup by tenant_id (fast, simple, scalable)
    - last_modified_by tracks who changed it (audit trail)
    """
    from sqlalchemy import text
    import json
    
    # TENANT-CENTRIC: Direct lookup by tenant_id
    if tenant_id:
        result = tenant_sql_fetchone(
            "SELECT id, section, data, version FROM system_settings WHERE section = :section AND tenant_id = :tenant_id",
            {'section': section}
        )
    else:
        # No tenant context - return empty (settings require tenant context)
        result = None
    
    if result:
        # Return existing record info
        data = result[2]
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                data = {}
        elif data is None:
            data = {}
            
        return {
            'id': result[0],
            'section': result[1],
            'data': data,
            'version': result[3] or 1
        }
    else:
        # Create new section with empty data (no defaults - user must configure)
        # TENANT-CENTRIC: Store with tenant_id directly
        if not tenant_id:
            # Can't create settings without tenant context
            return {
                'id': None,
                'section': section,
                'data': {},
                'version': 1
            }
        
        # Get current user_id (the admin creating the setting) for audit trail
        from modules.core.tenant_helpers import get_current_user_id
        current_user_id = get_current_user_id()
        
        empty_data = {}
        data_json = json.dumps(empty_data)
        
        # TENANT-CENTRIC: Store with tenant_id directly, user_id for audit
        db.session.execute(
            text("""
                INSERT INTO system_settings (section, data, version, tenant_id, last_modified_by, created_at, updated_at)
                VALUES (:section, CAST(:data AS jsonb), 1, :tenant_id, :user_id, NOW(), NOW())
            """),
            {'section': section, 'data': data_json, 'tenant_id': tenant_id, 'user_id': current_user_id}
        )
        db.session.commit()
        
        return {
            'id': None,  # Will be set by database
            'section': section,
            'data': empty_data,
            'version': 1
        }


@core_bp.route('/settings', methods=['GET', 'OPTIONS'])
def get_all_settings():
    """Get all settings from database only - no hardcoded defaults - TENANT-CENTRIC"""
    if request.method == 'OPTIONS':
        return ('', 200)
    
    # TENANT-CENTRIC: Get current user's tenant_id for direct lookup
    tenant_id = get_current_user_tenant_id()
    
    if not tenant_id:
        return jsonify({}), 200  # Return empty if no tenant context
    
    from sqlalchemy import text
    import json
    
    out = {}
    # Get all sections from database - TENANT-CENTRIC: Direct lookup by tenant_id
    try:
        # Direct query by tenant_id (fast, simple, no JOIN needed)
        result = tenant_sql_fetchall(
            "SELECT section, data FROM system_settings WHERE tenant_id = :tenant_id ORDER BY section"
        )
        
        for row in result:
            section = row[0]
            data = row[1]
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    data = {}
            elif data is None:
                data = {}
            out[section] = data
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error loading settings: {e}")
        # Return empty object on error, not defaults
        return jsonify({}), 200
    
    return jsonify(out), 200


@core_bp.route('/settings/<string:section>', methods=['GET', 'PUT', 'OPTIONS'])
@jwt_required()
def settings_section(section: str):
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,OPTIONS')
        return response
    
    section = section.lower()
    if request.method == 'GET':
        try:
            # TENANT-CENTRIC: Get current user's tenant_id for direct lookup
            tenant_id = get_current_user_tenant_id()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error getting tenant_id: {e}")
            # Return empty data on error, not 422
            response = jsonify({'data': {}, 'version': 1, 'section': section})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        # If no tenant_id, use default for development
        if not tenant_id:
            tenant_id = 'default'
        
        # Use raw SQL to query by section and tenant_id directly (fast, simple)
        from sqlalchemy import text
        try:
            if tenant_id:
                # TENANT-CENTRIC: Direct lookup by tenant_id (no JOIN needed)
                result = db.session.execute(
                    text("SELECT id, section, data, version, updated_at FROM system_settings WHERE section = :section AND tenant_id = :tenant_id"),
                    {'section': section, 'tenant_id': tenant_id}
                ).fetchone()
            else:
                # No tenant context - return empty (settings require tenant context)
                result = None
            
            if result:
                # Parse JSON data if it's a string
                data = result[2] if result[2] else {}
                if isinstance(data, str):
                    import json
                    try:
                        data = json.loads(data)
                    except:
                        data = {}
                
                response = jsonify({
                    'data': data,
                    'version': result[3] or 1,
                    'updated_at': result[4].isoformat() if result[4] else None,
                    'section': result[1]
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
                return response, 200
            else:
                # Section doesn't exist - return empty object (no defaults)
                response = jsonify({'data': {}, 'version': 1, 'section': section})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
                return response, 200
        except Exception as e:
            # Return empty object on error, not defaults
            import logging
            logging.getLogger(__name__).error(f"Error loading settings section {section}: {e}")
            response = jsonify({'data': {}, 'version': 1, 'section': section, 'error': str(e)})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
            return response, 200
    # PUT update with optimistic concurrency if version provided
    try:
        # TENANT-CENTRIC: Get current user's tenant_id for direct lookup and storage
        tenant_id = get_current_user_tenant_id()
        from modules.core.tenant_helpers import get_current_user_id
        current_user_id = get_current_user_id()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error getting user/tenant context: {e}")
        response = jsonify({'error': 'Authentication error', 'message': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 401
    
    # If no tenant_id, use default for development
    if not tenant_id:
        tenant_id = 'default'
    
    if not current_user_id:
        response = jsonify({'error': 'User authentication required'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 401
    
    payload = request.get_json(silent=True) or {}
    new_data = payload.get('data') if 'data' in payload else payload
    client_version = payload.get('version')
    
    from sqlalchemy import text
    import json
    
    item = _get_or_create_section(section, tenant_id)
    if client_version is not None and client_version != item['version']:
        return jsonify({'error': 'Version conflict', 'serverVersion': item['version']}), 409
    
    try:
        data_json = json.dumps(new_data or {})
        new_version = (item['version'] or 1) + 1
        
        if item['id']:
            # Update existing - TENANT-CENTRIC: Update by tenant_id directly
            db.session.execute(
                text("""
                    UPDATE system_settings 
                    SET data = :data::jsonb, version = :version, last_modified_by = :user_id, updated_at = NOW()
                    WHERE section = :section AND tenant_id = :tenant_id
                """),
                {'section': section, 'tenant_id': tenant_id, 'data': data_json, 'version': new_version, 'user_id': current_user_id}
            )
        else:
            # Insert new - TENANT-CENTRIC: Store with tenant_id directly
            db.session.execute(
                text("""
                    INSERT INTO system_settings (section, data, version, tenant_id, last_modified_by, created_at, updated_at)
                    VALUES (:section, :data::jsonb, :version, :tenant_id, :user_id, NOW(), NOW())
                """),
                {'section': section, 'data': data_json, 'version': new_version, 'tenant_id': tenant_id, 'user_id': current_user_id}
            )
        
        db.session.commit()
        response = jsonify({'message': 'Updated', 'version': new_version})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        return response, 200
    except Exception as e:
        db.session.rollback()
        import logging
        logging.getLogger(__name__).error(f"Error updating settings: {e}")
        response = jsonify({'error': f'Failed to update settings: {e}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        return response, 500
