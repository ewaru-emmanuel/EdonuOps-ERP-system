"""
API routes for localization system
"""

from flask import Blueprint, jsonify, request
from app import db
from .localization_system import get_localization_system
import logging

localization_bp = Blueprint('localization', __name__)

@localization_bp.route('/countries', methods=['GET'])
def get_available_countries():
    """Get list of available countries with their compliance packs"""
    try:
        localization_system = get_localization_system()
        countries = localization_system.get_available_countries()
        
        return jsonify({
            'countries': countries,
            'total_countries': len(countries)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching available countries: {e}")
        return jsonify({'error': 'Failed to fetch available countries'}), 500

@localization_bp.route('/countries/<country_code>/compliance', methods=['GET'])
def get_country_compliance_pack(country_code):
    """Get complete compliance pack for a specific country"""
    try:
        localization_system = get_localization_system()
        pack = localization_system.get_compliance_pack(country_code)
        
        if not pack:
            return jsonify({'error': 'Country not found'}), 404
        
        return jsonify({
            'country_code': pack.country_code,
            'country_name': pack.country_name,
            'currency': pack.currency,
            'accounting_standard': pack.accounting_standard,
            'fiscal_year_start': pack.fiscal_year_start,
            'coa_templates': {
                industry: {
                    'name': template.name,
                    'description': template.description,
                    'industry': template.industry,
                    'account_count': len(template.accounts)
                }
                for industry, template in pack.coa_templates.items()
            },
            'statutory_modules': {
                module_id: {
                    'id': module.id,
                    'name': module.name,
                    'description': module.description,
                    'required_accounts': module.required_accounts,
                    'compliance_forms': module.compliance_forms
                }
                for module_id, module in pack.statutory_modules.items()
            },
            'tax_rates': pack.tax_rates,
            'compliance_forms': pack.compliance_forms,
            'localization_rules': pack.localization_rules
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching compliance pack for {country_code}: {e}")
        return jsonify({'error': f'Failed to fetch compliance pack: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/coa-templates', methods=['GET'])
def get_country_coa_templates(country_code):
    """Get CoA templates for a specific country"""
    try:
        localization_system = get_localization_system()
        pack = localization_system.get_compliance_pack(country_code)
        
        if not pack:
            return jsonify({'error': 'Country not found'}), 404
        
        templates = []
        for industry, template in pack.coa_templates.items():
            templates.append({
                'industry': industry,
                'name': template.name,
                'description': template.description,
                'account_count': len(template.accounts),
                'core_accounts': len([acc for acc in template.accounts if acc.get('is_core', True)]),
                'advanced_accounts': len([acc for acc in template.accounts if not acc.get('is_core', True)])
            })
        
        return jsonify({
            'country_code': country_code,
            'templates': templates,
            'total_templates': len(templates)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching CoA templates for {country_code}: {e}")
        return jsonify({'error': f'Failed to fetch CoA templates: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/statutory-modules', methods=['GET'])
def get_country_statutory_modules(country_code):
    """Get statutory modules for a specific country"""
    try:
        localization_system = get_localization_system()
        modules = localization_system.get_statutory_modules(country_code)
        
        modules_data = []
        for module in modules:
            modules_data.append({
                'id': module.id,
                'name': module.name,
                'description': module.description,
                'country': module.country,
                'required_accounts': module.required_accounts,
                'compliance_forms': module.compliance_forms
            })
        
        return jsonify({
            'country_code': country_code,
            'modules': modules_data,
            'total_modules': len(modules_data)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching statutory modules for {country_code}: {e}")
        return jsonify({'error': f'Failed to fetch statutory modules: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/tax-rates', methods=['GET'])
def get_country_tax_rates(country_code):
    """Get tax rates for a specific country"""
    try:
        localization_system = get_localization_system()
        tax_rates = localization_system.get_tax_rates(country_code)
        
        return jsonify({
            'country_code': country_code,
            'tax_rates': tax_rates,
            'total_rates': len(tax_rates)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching tax rates for {country_code}: {e}")
        return jsonify({'error': f'Failed to fetch tax rates: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/compliance-forms', methods=['GET'])
def get_country_compliance_forms(country_code):
    """Get compliance forms for a specific country"""
    try:
        localization_system = get_localization_system()
        forms = localization_system.get_compliance_forms(country_code)
        
        return jsonify({
            'country_code': country_code,
            'compliance_forms': forms,
            'total_forms': len(forms)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching compliance forms for {country_code}: {e}")
        return jsonify({'error': f'Failed to fetch compliance forms: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/localization-rules', methods=['GET'])
def get_country_localization_rules(country_code):
    """Get localization rules for a specific country"""
    try:
        localization_system = get_localization_system()
        rules = localization_system.get_localization_rules(country_code)
        
        return jsonify({
            'country_code': country_code,
            'localization_rules': rules,
            'total_rules': len(rules)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching localization rules for {country_code}: {e}")
        return jsonify({'error': f'Failed to fetch localization rules: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/coa-template/<industry>', methods=['GET'])
def get_specific_coa_template(country_code, industry):
    """Get a specific CoA template for a country and industry"""
    try:
        localization_system = get_localization_system()
        template = localization_system.get_coa_template(country_code, industry)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({
            'country_code': country_code,
            'industry': industry,
            'template': {
                'name': template.name,
                'description': template.description,
                'industry': template.industry,
                'accounts': template.accounts,
                'workflows': template.workflows,
                'statutory_modules': template.statutory_modules
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching CoA template for {country_code}/{industry}: {e}")
        return jsonify({'error': f'Failed to fetch CoA template: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/setup', methods=['POST'])
def setup_country_compliance(country_code):
    """Setup compliance for a specific country"""
    try:
        data = request.json or {}
        selected_industries = data.get('industries', [])
        selected_modules = data.get('modules', [])
        
        localization_system = get_localization_system()
        pack = localization_system.get_compliance_pack(country_code)
        
        if not pack:
            return jsonify({'error': 'Country not found'}), 404
        
        # This would typically create accounts and setup modules
        # For now, return the setup configuration
        setup_config = {
            'country_code': country_code,
            'country_name': pack.country_name,
            'currency': pack.currency,
            'accounting_standard': pack.accounting_standard,
            'selected_industries': selected_industries,
            'selected_modules': selected_modules,
            'setup_status': 'pending',
            'estimated_accounts': sum(
                len(pack.coa_templates[industry].accounts) 
                for industry in selected_industries 
                if industry in pack.coa_templates
            ),
            'compliance_forms_required': [
                form_id for module_id in selected_modules
                if module_id in pack.statutory_modules
                for form_id in pack.statutory_modules[module_id].compliance_forms
            ]
        }
        
        return jsonify(setup_config), 200
        
    except Exception as e:
        logging.error(f"Error setting up compliance for {country_code}: {e}")
        return jsonify({'error': f'Failed to setup compliance: {str(e)}'}), 500

@localization_bp.route('/countries/<country_code>/analytics', methods=['GET'])
def get_country_analytics(country_code):
    """Get analytics for a specific country's compliance setup"""
    try:
        localization_system = get_localization_system()
        pack = localization_system.get_compliance_pack(country_code)
        
        if not pack:
            return jsonify({'error': 'Country not found'}), 404
        
        analytics = {
            'country_code': country_code,
            'country_name': pack.country_name,
            'currency': pack.currency,
            'accounting_standard': pack.accounting_standard,
            'coa_templates': {
                'total': len(pack.coa_templates),
                'industries': list(pack.coa_templates.keys())
            },
            'statutory_modules': {
                'total': len(pack.statutory_modules),
                'modules': list(pack.statutory_modules.keys())
            },
            'tax_rates': {
                'total': len(pack.tax_rates),
                'rates': list(pack.tax_rates.keys())
            },
            'compliance_forms': {
                'total': len(pack.compliance_forms),
                'forms': list(pack.compliance_forms.keys())
            },
            'localization_rules': {
                'total': len(pack.localization_rules),
                'rules': list(pack.localization_rules.keys())
            }
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logging.error(f"Error fetching analytics for {country_code}: {e}")
        return jsonify({'error': f'Failed to fetch analytics: {str(e)}'}), 500


