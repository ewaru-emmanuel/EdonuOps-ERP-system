"""
Subscription Management Service
Handles tenant subscriptions, billing, and plan management
"""

from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc
from app import db
from modules.core.tenant_models import Tenant, TenantModule
from modules.finance.advanced_models import ChartOfAccounts, GeneralLedgerEntry
from modules.finance.payment_models import BankAccount, BankTransaction
import json

class SubscriptionManagementService:
    """Service for managing tenant subscriptions and billing"""
    
    # Subscription plans configuration
    SUBSCRIPTION_PLANS = {
        'free': {
            'name': 'Free Plan',
            'price': 0,
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'features': {
                'max_accounts': 10,
                'max_users': 2,
                'max_gl_entries': 100,
                'max_bank_accounts': 1,
                'max_reconciliations': 5,
                'modules': ['finance'],
                'support': 'community',
                'storage': '1GB'
            },
            'limits': {
                'api_calls_per_month': 1000,
                'reports_per_month': 5,
                'backup_frequency': 'weekly'
            }
        },
        'basic': {
            'name': 'Basic Plan',
            'price': 29,
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'features': {
                'max_accounts': 50,
                'max_users': 5,
                'max_gl_entries': 1000,
                'max_bank_accounts': 3,
                'max_reconciliations': 25,
                'modules': ['finance', 'inventory'],
                'support': 'email',
                'storage': '10GB'
            },
            'limits': {
                'api_calls_per_month': 10000,
                'reports_per_month': 50,
                'backup_frequency': 'daily'
            }
        },
        'premium': {
            'name': 'Premium Plan',
            'price': 79,
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'features': {
                'max_accounts': 200,
                'max_users': 15,
                'max_gl_entries': 5000,
                'max_bank_accounts': 10,
                'max_reconciliations': 100,
                'modules': ['finance', 'inventory', 'sales', 'purchasing'],
                'support': 'priority',
                'storage': '50GB'
            },
            'limits': {
                'api_calls_per_month': 50000,
                'reports_per_month': 200,
                'backup_frequency': 'real-time'
            }
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price': 199,
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'features': {
                'max_accounts': -1,  # Unlimited
                'max_users': -1,     # Unlimited
                'max_gl_entries': -1, # Unlimited
                'max_bank_accounts': -1, # Unlimited
                'max_reconciliations': -1, # Unlimited
                'modules': ['finance', 'inventory', 'sales', 'purchasing', 'manufacturing', 'crm', 'hr', 'reporting', 'analytics'],
                'support': 'dedicated',
                'storage': 'unlimited'
            },
            'limits': {
                'api_calls_per_month': -1,  # Unlimited
                'reports_per_month': -1,    # Unlimited
                'backup_frequency': 'real-time'
            }
        }
    }
    
    @staticmethod
    def get_available_plans():
        """Get all available subscription plans"""
        return SubscriptionManagementService.SUBSCRIPTION_PLANS
    
    @staticmethod
    def get_plan_details(plan_id):
        """Get details for a specific plan"""
        return SubscriptionManagementService.SUBSCRIPTION_PLANS.get(plan_id)
    
    @staticmethod
    def get_tenant_subscription_info(tenant_id):
        """Get comprehensive subscription information for a tenant"""
        try:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                return None
            
            current_plan = SubscriptionManagementService.get_plan_details(tenant.subscription_plan)
            if not current_plan:
                return None
            
            # Get current usage
            usage = SubscriptionManagementService.get_tenant_usage(tenant_id)
            
            # Check if tenant is within limits
            limits_status = SubscriptionManagementService.check_tenant_limits(tenant_id, current_plan)
            
            # Get billing information
            billing_info = SubscriptionManagementService.get_billing_info(tenant_id)
            
            return {
                'tenant_id': tenant_id,
                'current_plan': {
                    'id': tenant.subscription_plan,
                    'name': current_plan['name'],
                    'price': current_plan['price'],
                    'currency': current_plan['currency'],
                    'billing_cycle': current_plan['billing_cycle']
                },
                'features': current_plan['features'],
                'limits': current_plan['limits'],
                'usage': usage,
                'limits_status': limits_status,
                'billing_info': billing_info,
                'status': tenant.status,
                'created_at': tenant.created_at.isoformat() if tenant.created_at else None
            }
            
        except Exception as e:
            print(f"Error getting tenant subscription info: {e}")
            return None
    
    @staticmethod
    def get_tenant_usage(tenant_id):
        """Get current usage metrics for tenant"""
        try:
            # Count current usage
            accounts_count = ChartOfAccounts.query.filter_by(tenant_id=tenant_id).count()
            users_count = 1  # Simplified - would need user_tenants table
            gl_entries_count = GeneralLedgerEntry.query.filter_by(tenant_id=tenant_id).count()
            bank_accounts_count = BankAccount.query.filter_by(tenant_id=tenant_id).count()
            reconciliations_count = 0  # Would need reconciliation_sessions table
            
            # Get active modules
            active_modules = TenantModule.query.filter_by(
                tenant_id=tenant_id, enabled=True
            ).count()
            
            # Simulate API calls and reports (would need actual tracking)
            api_calls_this_month = 150  # Simulated
            reports_this_month = 8      # Simulated
            
            return {
                'accounts': accounts_count,
                'users': users_count,
                'gl_entries': gl_entries_count,
                'bank_accounts': bank_accounts_count,
                'reconciliations': reconciliations_count,
                'active_modules': active_modules,
                'api_calls_this_month': api_calls_this_month,
                'reports_this_month': reports_this_month
            }
            
        except Exception as e:
            print(f"Error getting tenant usage: {e}")
            return {}
    
    @staticmethod
    def check_tenant_limits(tenant_id, plan):
        """Check if tenant is within plan limits"""
        try:
            usage = SubscriptionManagementService.get_tenant_usage(tenant_id)
            features = plan['features']
            limits = plan['limits']
            
            status = {
                'within_limits': True,
                'warnings': [],
                'blocked': []
            }
            
            # Check account limits
            if features['max_accounts'] != -1 and usage['accounts'] >= features['max_accounts']:
                status['warnings'].append('Account limit reached')
                if usage['accounts'] > features['max_accounts']:
                    status['blocked'].append('Account limit exceeded')
                    status['within_limits'] = False
            
            # Check user limits
            if features['max_users'] != -1 and usage['users'] >= features['max_users']:
                status['warnings'].append('User limit reached')
                if usage['users'] > features['max_users']:
                    status['blocked'].append('User limit exceeded')
                    status['within_limits'] = False
            
            # Check GL entries limits
            if features['max_gl_entries'] != -1 and usage['gl_entries'] >= features['max_gl_entries']:
                status['warnings'].append('GL entries limit reached')
                if usage['gl_entries'] > features['max_gl_entries']:
                    status['blocked'].append('GL entries limit exceeded')
                    status['within_limits'] = False
            
            # Check bank accounts limits
            if features['max_bank_accounts'] != -1 and usage['bank_accounts'] >= features['max_bank_accounts']:
                status['warnings'].append('Bank accounts limit reached')
                if usage['bank_accounts'] > features['max_bank_accounts']:
                    status['blocked'].append('Bank accounts limit exceeded')
                    status['within_limits'] = False
            
            # Check API calls limits
            if limits['api_calls_per_month'] != -1 and usage['api_calls_this_month'] >= limits['api_calls_per_month']:
                status['warnings'].append('API calls limit reached')
                if usage['api_calls_this_month'] > limits['api_calls_per_month']:
                    status['blocked'].append('API calls limit exceeded')
                    status['within_limits'] = False
            
            # Check reports limits
            if limits['reports_per_month'] != -1 and usage['reports_this_month'] >= limits['reports_per_month']:
                status['warnings'].append('Reports limit reached')
                if usage['reports_this_month'] > limits['reports_per_month']:
                    status['blocked'].append('Reports limit exceeded')
                    status['within_limits'] = False
            
            return status
            
        except Exception as e:
            print(f"Error checking tenant limits: {e}")
            return {'within_limits': True, 'warnings': [], 'blocked': []}
    
    @staticmethod
    def get_billing_info(tenant_id):
        """Get billing information for tenant"""
        try:
            # Simulate billing information
            return {
                'next_billing_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'last_payment_date': (datetime.utcnow() - timedelta(days=5)).isoformat(),
                'payment_method': 'Credit Card ending in 1234',
                'billing_address': '123 Business St, City, State 12345',
                'invoice_email': 'billing@company.com'
            }
            
        except Exception as e:
            print(f"Error getting billing info: {e}")
            return {}
    
    @staticmethod
    def upgrade_tenant_plan(tenant_id, new_plan_id):
        """Upgrade tenant to a new plan"""
        try:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                return False, "Tenant not found"
            
            new_plan = SubscriptionManagementService.get_plan_details(new_plan_id)
            if not new_plan:
                return False, "Invalid plan"
            
            # Check if upgrade is valid
            current_plan = SubscriptionManagementService.get_plan_details(tenant.subscription_plan)
            if not SubscriptionManagementService.is_valid_upgrade(tenant.subscription_plan, new_plan_id):
                return False, "Invalid upgrade path"
            
            # Update tenant plan
            tenant.subscription_plan = new_plan_id
            tenant.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Activate new modules if needed
            SubscriptionManagementService.activate_plan_modules(tenant_id, new_plan_id)
            
            return True, "Plan upgraded successfully"
            
        except Exception as e:
            print(f"Error upgrading tenant plan: {e}")
            db.session.rollback()
            return False, f"Error upgrading plan: {str(e)}"
    
    @staticmethod
    def is_valid_upgrade(current_plan, new_plan):
        """Check if upgrade from current plan to new plan is valid"""
        plan_hierarchy = ['free', 'basic', 'premium', 'enterprise']
        
        try:
            current_index = plan_hierarchy.index(current_plan)
            new_index = plan_hierarchy.index(new_plan)
            
            # Allow upgrade to higher tier or downgrade to lower tier
            return True  # For now, allow any plan change
            
        except ValueError:
            return False
    
    @staticmethod
    def activate_plan_modules(tenant_id, plan_id):
        """Activate modules for a specific plan"""
        try:
            plan = SubscriptionManagementService.get_plan_details(plan_id)
            if not plan:
                return False
            
            modules = plan['features']['modules']
            
            for module_name in modules:
                # Check if module is already active
                existing_module = TenantModule.query.filter_by(
                    tenant_id=tenant_id, module_name=module_name
                ).first()
                
                if not existing_module:
                    # Create new module activation
                    new_module = TenantModule(
                        tenant_id=tenant_id,
                        module_name=module_name,
                        enabled=True,
                        activated_at=datetime.utcnow(),
                        configuration={}
                    )
                    db.session.add(new_module)
                else:
                    # Enable existing module
                    existing_module.enabled = True
                    existing_module.activated_at = datetime.utcnow()
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Error activating plan modules: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_upgrade_recommendations(tenant_id):
        """Get upgrade recommendations for tenant"""
        try:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                return []
            
            current_plan = SubscriptionManagementService.get_plan_details(tenant.subscription_plan)
            usage = SubscriptionManagementService.get_tenant_usage(tenant_id)
            limits_status = SubscriptionManagementService.check_tenant_limits(tenant_id, current_plan)
            
            recommendations = []
            
            # Check if tenant is hitting limits
            if not limits_status['within_limits'] or limits_status['warnings']:
                # Find next plan that would accommodate usage
                plan_hierarchy = ['free', 'basic', 'premium', 'enterprise']
                current_index = plan_hierarchy.index(tenant.subscription_plan)
                
                for i in range(current_index + 1, len(plan_hierarchy)):
                    next_plan_id = plan_hierarchy[i]
                    next_plan = SubscriptionManagementService.get_plan_details(next_plan_id)
                    
                    if SubscriptionManagementService.would_plan_accommodate_usage(usage, next_plan):
                        recommendations.append({
                            'plan_id': next_plan_id,
                            'plan_name': next_plan['name'],
                            'price': next_plan['price'],
                            'reason': 'Current plan limits exceeded',
                            'benefits': [
                                f"Up to {next_plan['features']['max_accounts']} accounts",
                                f"Up to {next_plan['features']['max_users']} users",
                                f"Up to {next_plan['features']['max_gl_entries']} GL entries"
                            ]
                        })
                        break
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting upgrade recommendations: {e}")
            return []
    
    @staticmethod
    def would_plan_accommodate_usage(usage, plan):
        """Check if a plan would accommodate current usage"""
        features = plan['features']
        
        # Check if plan has unlimited features or higher limits
        if (features['max_accounts'] == -1 or usage['accounts'] < features['max_accounts']) and \
           (features['max_users'] == -1 or usage['users'] < features['max_users']) and \
           (features['max_gl_entries'] == -1 or usage['gl_entries'] < features['max_gl_entries']) and \
           (features['max_bank_accounts'] == -1 or usage['bank_accounts'] < features['max_bank_accounts']):
            return True
        
        return False












