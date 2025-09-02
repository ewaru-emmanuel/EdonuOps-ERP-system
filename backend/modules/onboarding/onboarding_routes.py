"""
Focused Onboarding Routes
API endpoints for Business Discovery + Module Configuration
"""

from flask import Blueprint, request, jsonify
from app import db
from .onboarding_service import OnboardingService

# Create blueprint
onboarding_bp = Blueprint('onboarding', __name__)

# ============================================================================
# BUSINESS DISCOVERY ROUTES
# ============================================================================

@onboarding_bp.route('/discovery/industry-templates', methods=['GET'])
def get_industry_templates():
    """Get available industry templates"""
    try:
        templates = OnboardingService.get_industry_templates()
        return jsonify({
            'status': 'success',
            'templates': templates
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/discovery/pain-points', methods=['GET'])
def get_pain_point_mappings():
    """Get pain point to module mappings"""
    try:
        mappings = OnboardingService.get_pain_point_mappings()
        return jsonify({
            'status': 'success',
            'mappings': mappings
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/discovery/business-sizes', methods=['GET'])
def get_business_size_configs():
    """Get business size configurations"""
    try:
        configs = OnboardingService.get_business_size_configs()
        return jsonify({
            'status': 'success',
            'configs': configs
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/discovery/analyze', methods=['POST'])
def analyze_business_needs():
    """Analyze business needs and recommend configuration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['industry', 'business_size']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Analyze business needs
        analysis = OnboardingService.analyze_business_needs(data)
        
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MODULE CONFIGURATION ROUTES
# ============================================================================

@onboarding_bp.route('/configuration/quick-start', methods=['POST'])
def create_quick_start_config():
    """Create quick start configuration for immediate use"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['industry', 'business_size']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create quick start config
        config = OnboardingService.create_quick_start_config(
            data['industry'], 
            data['business_size']
        )
        
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/configuration/modules', methods=['POST'])
def configure_modules():
    """Configure selected modules with business-specific settings"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['modules', 'industry', 'business_size']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get industry template for default settings
        industry_templates = OnboardingService.get_industry_templates()
        industry_template = next(
            (t for t in industry_templates if t.get('name', '').lower().startswith(data['industry'])), 
            industry_templates[0]
        )
        
        # Create module configuration
        module_config = {
            'selected_modules': data['modules'],
            'industry': data['industry'],
            'business_size': data['business_size'],
            'default_settings': industry_template.get('features', []),
            'complexity': industry_template.get('complexity', 'simple'),
            'setup_steps': [
                "Configure module preferences",
                "Set up user roles",
                "Import initial data",
                "Start using the system"
            ],
            'estimated_time': '15-20 minutes',
            'can_customize_later': True
        }
        
        return jsonify({
            'status': 'success',
            'module_config': module_config
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# QUICK START ROUTES (The "Fast Path")
# ============================================================================

@onboarding_bp.route('/quick-start', methods=['POST'])
def quick_start_setup():
    """Quick start setup for small businesses"""
    try:
        data = request.get_json()
        
        # Default to simple configuration
        industry = data.get('industry', 'retail')
        business_size = data.get('business_size', 'small')
        
        # Create minimal configuration
        quick_config = OnboardingService.create_quick_start_config(industry, business_size)
        
        if quick_config['status'] == 'success':
            # Add immediate next steps
            quick_config['quick_config']['immediate_actions'] = [
                "Access your dashboard",
                "Add your first product/customer",
                "Invite team members",
                "Start using the system"
            ]
            
            return jsonify({
                'status': 'success',
                'message': 'Quick start configuration complete!',
                'config': quick_config['quick_config'],
                'redirect_to': '/dashboard'
            }), 200
        else:
            return jsonify(quick_config), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ONBOARDING STATUS & PROGRESS
# ============================================================================

@onboarding_bp.route('/status', methods=['GET'])
def get_onboarding_status():
    """Get current onboarding status and progress"""
    try:
        # This would typically check user's onboarding progress
        # For now, return default status
        status = {
            'status': 'not_started',
            'progress': 0,
            'current_step': 'discovery',
            'completed_steps': [],
            'remaining_steps': ['discovery', 'configuration', 'setup'],
            'estimated_completion': '15 minutes'
        }
        
        return jsonify({
            'status': 'success',
            'onboarding_status': status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/skip', methods=['POST'])
def skip_onboarding():
    """Skip onboarding and go directly to the app"""
    try:
        data = request.get_json()
        reason = data.get('reason', 'wants_to_explore')
        
        # Log skip reason for analytics
        print(f"User skipped onboarding. Reason: {reason}")
        
        return jsonify({
            'status': 'success',
            'message': 'Onboarding skipped. Welcome to EdonuOps!',
            'redirect_to': '/dashboard',
            'can_return_to_onboarding': True
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENTERPRISE ROUTING
# ============================================================================

@onboarding_bp.route('/enterprise/contact', methods=['POST'])
def enterprise_contact():
    """Route enterprise clients to sales team"""
    try:
        data = request.get_json()
        
        # Log enterprise inquiry
        print(f"Enterprise inquiry from: {data.get('company_name', 'Unknown')}")
        print(f"Contact: {data.get('contact_email', 'No email')}")
        print(f"Requirements: {data.get('requirements', 'Not specified')}")
        
        return jsonify({
            'status': 'success',
            'message': 'Thank you for your interest! Our enterprise team will contact you within 24 hours.',
            'next_steps': [
                'Sales team will review your requirements',
                'Schedule discovery call',
                'Prepare custom proposal',
                'Plan implementation timeline'
            ],
            'contact_info': {
                'email': 'enterprise@edonuops.com',
                'phone': '+1-800-EDONUOPS',
                'response_time': '24 hours'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

