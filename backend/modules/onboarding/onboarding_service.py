"""
Focused Onboarding Service
Handles Business Discovery + Module Configuration (the 80% that matters)
"""

import logging
from typing import Dict, List, Optional, Any
from app import db
from sqlalchemy import and_, or_, func

logger = logging.getLogger(__name__)

class OnboardingService:
    """
    Core onboarding service - Business Discovery + Module Configuration
    """
    
    # Industry templates with pre-configured settings
    INDUSTRY_TEMPLATES = {
        'retail': {
            'name': 'Retail & E-commerce',
            'description': 'Brick-and-mortar stores, online shops, omnichannel retail',
            'modules': ['inventory', 'finance', 'crm', 'analytics'],
            'complexity': 'tier1',
            'features': ['Point of Sale', 'Inventory Management', 'Customer Management', 'Basic Reporting']
        },
        'manufacturing': {
            'name': 'Manufacturing & Production',
            'description': 'Product manufacturing, assembly, quality control',
            'modules': ['inventory', 'finance', 'manufacturing', 'quality', 'analytics'],
            'complexity': 'tier3',
            'features': ['Production Planning', 'Quality Control', 'Inventory Management', 'Advanced Analytics']
        },
        'wholesale': {
            'name': 'Wholesale & Distribution',
            'description': 'B2B distribution, warehouse management, logistics',
            'modules': ['inventory', 'finance', 'logistics', 'crm', 'analytics'],
            'complexity': 'tier3',
            'features': ['Warehouse Management', 'Order Management', 'Route Optimization', 'Advanced Reporting']
        },
        'services': {
            'name': 'Professional Services',
            'description': 'Consulting, agencies, service-based businesses',
            'modules': ['finance', 'crm', 'hr', 'analytics'],
            'complexity': 'tier1',
            'features': ['Project Management', 'Time Tracking', 'Client Management', 'Financial Reporting']
        },
        'healthcare': {
            'name': 'Healthcare & Medical',
            'description': 'Clinics, medical practices, healthcare services',
            'modules': ['inventory', 'finance', 'crm', 'hr', 'analytics'],
            'complexity': 'tier2',
            'features': ['Patient Management', 'Inventory Tracking', 'Compliance', 'Advanced Security']
        }
    }
    
    # Pain point mappings to module recommendations
    PAIN_POINT_MAPPINGS = {
        'inventory_issues': {
            'description': 'Lost items, stockouts, overstock',
            'modules': ['inventory'],
            'priority': 'high'
        },
        'financial_chaos': {
            'description': 'Manual bookkeeping, late payments, cash flow issues',
            'modules': ['finance'],
            'priority': 'high'
        },
        'customer_loss': {
            'description': 'Poor customer service, lost sales, no follow-up',
            'modules': ['crm'],
            'priority': 'high'
        },
        'team_management': {
            'description': 'Payroll issues, performance tracking, hiring challenges',
            'modules': ['hr'],
            'priority': 'medium'
        },
        'data_insights': {
            'description': 'No visibility into business performance',
            'modules': ['analytics'],
            'priority': 'medium'
        },
        'production_issues': {
            'description': 'Quality problems, production delays, waste',
            'modules': ['manufacturing', 'quality'],
            'priority': 'high'
        }
    }
    
    # Business size configurations
    BUSINESS_SIZE_CONFIGS = {
        'startup': {
            'name': 'Startup (1-10 employees)',
            'complexity': 'tier1',
            'modules': ['inventory', 'finance', 'crm'],
            'setup_time': '10 minutes',
            'features': 'Essential features only'
        },
        'small': {
            'name': 'Small Business (11-50 employees)',
            'complexity': 'tier1',
            'modules': ['inventory', 'finance', 'crm', 'hr'],
            'setup_time': '15 minutes',
            'features': 'Core business functions'
        },
        'medium': {
            'name': 'Growing Business (51-200 employees)',
            'complexity': 'tier2',
            'modules': ['inventory', 'finance', 'crm', 'hr', 'analytics'],
            'setup_time': '20 minutes',
            'features': 'Advanced features + reporting'
        },
        'enterprise': {
            'name': 'Enterprise (200+ employees)',
            'complexity': 'tier3',
            'modules': ['all'],
            'setup_time': 'Contact Sales',
            'features': 'Full enterprise suite + customization'
        }
    }
    
    @classmethod
    def get_industry_templates(cls) -> List[Dict[str, Any]]:
        """Get available industry templates"""
        return list(cls.INDUSTRY_TEMPLATES.values())
    
    @classmethod
    def get_pain_point_mappings(cls) -> List[Dict[str, Any]]:
        """Get pain point to module mappings"""
        return list(cls.PAIN_POINT_MAPPINGS.values())
    
    @classmethod
    def get_business_size_configs(cls) -> List[Dict[str, Any]]:
        """Get business size configurations"""
        return list(cls.BUSINESS_SIZE_CONFIGS.values())
    
    @classmethod
    def analyze_business_needs(cls, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business needs and recommend configuration"""
        try:
            industry = discovery_data.get('industry', 'retail')
            business_size = discovery_data.get('business_size', 'small')
            pain_points = discovery_data.get('pain_points', [])
            goals = discovery_data.get('goals', [])
            
            # Get industry template
            industry_template = cls.INDUSTRY_TEMPLATES.get(industry, cls.INDUSTRY_TEMPLATES['retail'])
            
            # Get business size config
            size_config = cls.BUSINESS_SIZE_CONFIGS.get(business_size, cls.BUSINESS_SIZE_CONFIGS['small'])
            
            # Analyze pain points and recommend additional modules
            recommended_modules = set(industry_template['modules'])
            priority_issues = []
            
            for pain_point in pain_points:
                if pain_point in cls.PAIN_POINT_MAPPINGS:
                    mapping = cls.PAIN_POINT_MAPPINGS[pain_point]
                    recommended_modules.update(mapping['modules'])
                    if mapping['priority'] == 'high':
                        priority_issues.append({
                            'issue': mapping['description'],
                            'solution': f"Implement {', '.join(mapping['modules'])} module(s)"
                        })
            
            # Determine complexity level
            complexity = 'tier1'
            if business_size in ['medium']:
                complexity = 'tier2'
            elif business_size in ['enterprise'] or industry in ['manufacturing', 'wholesale']:
                complexity = 'tier3'
            elif industry in ['healthcare']:
                complexity = 'tier2'
            
            # Calculate setup time
            setup_time = size_config['setup_time']
            if complexity == 'tier2':
                setup_time = '25 minutes'
            elif complexity == 'tier3':
                setup_time = 'Contact Sales Team'
            
            # Generate configuration summary
            config_summary = {
                'industry': industry_template,
                'business_size': size_config,
                'complexity': complexity,
                'setup_time': setup_time,
                'recommended_modules': list(recommended_modules),
                'priority_issues': priority_issues,
                'estimated_roi': cls._calculate_roi_estimate(industry, business_size, pain_points),
                'next_steps': cls._generate_next_steps(complexity, business_size)
            }
            
            return {
                'status': 'success',
                'analysis': config_summary
            }
            
        except Exception as e:
            logger.error(f"Error analyzing business needs: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @classmethod
    def _calculate_roi_estimate(cls, industry: str, business_size: str, pain_points: List[str]) -> Dict[str, Any]:
        """Calculate estimated ROI based on business profile"""
        base_roi = {
            'startup': 150,      # 150% ROI
            'small': 200,        # 200% ROI
            'medium': 300,       # 300% ROI
            'enterprise': 500    # 500% ROI
        }
        
        industry_multiplier = {
            'retail': 1.2,       # 20% higher ROI
            'manufacturing': 1.5, # 50% higher ROI
            'wholesale': 1.3,    # 30% higher ROI
            'services': 1.0,     # Standard ROI
            'healthcare': 1.4    # 40% higher ROI
        }
        
        pain_point_bonus = len(pain_points) * 25  # 25% bonus per pain point
        
        base = base_roi.get(business_size, 200)
        multiplier = industry_multiplier.get(industry, 1.0)
        total_roi = (base * multiplier) + pain_point_bonus
        
        return {
            'estimated_roi': f"{total_roi:.0f}%",
            'payback_period': f"{12 // (total_roi / 100):.0f} months",
            'annual_savings': f"${(total_roi / 100) * 10000:,.0f}",
            'efficiency_gain': f"{min(total_roi / 10, 50):.0f}%"
        }
    
    @classmethod
    def _generate_next_steps(cls, complexity: str, business_size: str) -> List[str]:
        """Generate next steps based on complexity and business size"""
        if complexity == 'tier3':
            return [
                "Contact our Enterprise Sales Team",
                "Schedule a comprehensive business analysis",
                "Plan custom implementation timeline",
                "Arrange executive stakeholder meetings"
            ]
        elif complexity == 'tier2':
            return [
                "Complete advanced module configuration",
                "Set up user roles and permissions",
                "Configure integrations with existing systems",
                "Schedule team training sessions"
            ]
        else:  # tier1
            return [
                "Complete basic module setup",
                "Import your existing data",
                "Invite team members",
                "Start using the system immediately"
            ]
    
    @classmethod
    def create_quick_start_config(cls, industry: str, business_size: str) -> Dict[str, Any]:
        """Create quick start configuration for immediate use"""
        try:
            # Get industry template
            industry_template = cls.INDUSTRY_TEMPLATES.get(industry, cls.INDUSTRY_TEMPLATES['retail'])
            
            # Get business size config
            size_config = cls.BUSINESS_SIZE_CONFIGS.get(business_size, cls.BUSINESS_SIZE_CONFIGS['small'])
            
            # Create minimal configuration
            quick_config = {
                'modules': industry_template['modules'][:3],  # Top 3 modules only
                'complexity': 'tier1',
                'features': industry_template['features'][:3],  # Top 3 features
                'setup_steps': [
                    "Choose your modules",
                    "Set basic preferences",
                    "Start using the system"
                ],
                'estimated_time': '5 minutes',
                'can_upgrade_later': True
            }
            
            return {
                'status': 'success',
                'quick_config': quick_config
            }
            
        except Exception as e:
            logger.error(f"Error creating quick start config: {str(e)}")
            return {'status': 'error', 'message': str(e)}
