# Core routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.core.models import SystemSetting

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
    """Get currency settings"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        # Try to get from advanced finance settings first
        from modules.finance.advanced_models import CompanySettings
        settings = CompanySettings.query.filter_by(setting_key='base_currency').first()
        
        if settings:
            response = jsonify({
                'success': True,
                'data': {
                    'base_currency': settings.setting_value,
                    'currency_symbol': '$',  # Default
                    'decimal_places': 2
                }
            })
        else:
            # Return default currency settings
            response = jsonify({
                'success': True,
                'data': {
                    'base_currency': 'USD',
                    'currency_symbol': '$',
                    'decimal_places': 2
                }
            })
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
            
    except Exception as e:
        # Return default settings on error
        response = jsonify({
            'success': True,
            'data': {
                'base_currency': 'USD',
                'currency_symbol': '$',
                'decimal_places': 2
            }
        })
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200


# -----------------------------
# Centralized Settings API
# -----------------------------

_DEFAULT_SETTINGS = {
    'currency': {
        'base_currency': 'USD',
        'allowed_currencies': ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY'],
        'rate_source': 'manual',
        'rounding': 2,
    },
    'tax': {
        'default_rate': 0.0,
        'tax_inclusive': False,
        'jurisdiction': 'default'
    },
    'documents': {
        'invoice_prefix': 'INV-',
        'po_prefix': 'PO-',
        'so_prefix': 'SO-',
        'default_terms_days': 30
    },
    'email': {
        'from_name': None,
        'from_email': None,
        'provider': 'smtp'
    },
    'security': {
        'session_timeout_minutes': 60,
        'password_policy': 'standard'
    },
    'localization': {
        'timezone': 'UTC',
        'locale': 'en-US',
        'fiscal_year_start': '01-01'
    },
    'features': {
        'enable_ai': True,
        'enable_kb': True
    }
}


def _get_or_create_section(section: str) -> SystemSetting:
    item = SystemSetting.query.filter_by(section=section).first()
    if not item:
        item = SystemSetting(section=section, data=_DEFAULT_SETTINGS.get(section, {}), version=1)
        db.session.add(item)
        db.session.commit()
    return item


@core_bp.route('/settings', methods=['GET', 'OPTIONS'])
def get_all_settings():
    if request.method == 'OPTIONS':
        return ('', 200)
    out = {}
    for section in _DEFAULT_SETTINGS.keys():
        item = SystemSetting.query.filter_by(section=section).first()
        out[section] = (item.data if item else _DEFAULT_SETTINGS.get(section, {}))
    return jsonify(out), 200


@core_bp.route('/settings/<string:section>', methods=['GET', 'PUT', 'OPTIONS'])
def settings_section(section: str):
    if request.method == 'OPTIONS':
        return ('', 200)
    section = section.lower()
    if request.method == 'GET':
        item = SystemSetting.query.filter_by(section=section).first()
        if not item:
            return jsonify(_DEFAULT_SETTINGS.get(section, {})), 200
        return jsonify({
            'data': item.data,
            'version': item.version,
            'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            'section': item.section
        }), 200
    # PUT update with optimistic concurrency if version provided
    payload = request.get_json(silent=True) or {}
    new_data = payload.get('data') if 'data' in payload else payload
    client_version = payload.get('version')
    item = _get_or_create_section(section)
    if client_version is not None and client_version != item.version:
        return jsonify({'error': 'Version conflict', 'serverVersion': item.version}), 409
    try:
        item.data = new_data or {}
        item.version = (item.version or 1) + 1
        db.session.commit()
        return jsonify({'message': 'Updated', 'version': item.version}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update settings: {e}'}), 500
