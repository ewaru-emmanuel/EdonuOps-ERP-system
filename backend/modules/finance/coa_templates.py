#!/usr/bin/env python3
"""
Chart of Accounts Templates for EdonuOps
Provides multiple CoA templates for different business types and standards
"""

class CoATemplates:
    """Collection of Chart of Accounts templates"""
    
    @staticmethod
    def get_quickbooks_standard():
        """QuickBooks-compatible Chart of Accounts"""
        return {
            'name': 'QuickBooks Standard',
            'description': 'Industry-standard chart compatible with QuickBooks',
            'accounts': [
                # ASSETS (1000-1999)
                {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': 'asset'},
                {'code': '1010', 'name': 'Checking Account', 'type': 'asset', 'parent_code': '1000'},
                {'code': '1020', 'name': 'Savings Account', 'type': 'asset', 'parent_code': '1000'},
                {'code': '1030', 'name': 'Petty Cash', 'type': 'asset', 'parent_code': '1000'},
                {'code': '1050', 'name': 'Undeposited Funds', 'type': 'asset', 'parent_code': '1000'},
                
                {'code': '1100', 'name': 'Accounts Receivable', 'type': 'asset'},
                {'code': '1110', 'name': 'Trade Receivables', 'type': 'asset', 'parent_code': '1100'},
                {'code': '1130', 'name': 'Allowance for Doubtful Accounts', 'type': 'asset', 'parent_code': '1100'},
                
                {'code': '1200', 'name': 'Inventory', 'type': 'asset'},
                {'code': '1240', 'name': 'Inventory Asset', 'type': 'asset', 'parent_code': '1200'},
                
                {'code': '1300', 'name': 'Other Current Assets', 'type': 'asset'},
                {'code': '1310', 'name': 'Prepaid Expenses', 'type': 'asset', 'parent_code': '1300'},
                
                {'code': '1500', 'name': 'Fixed Assets', 'type': 'asset'},
                {'code': '1520', 'name': 'Equipment', 'type': 'asset', 'parent_code': '1500'},
                {'code': '1525', 'name': 'Accumulated Depreciation - Equipment', 'type': 'asset', 'parent_code': '1500'},
                
                # LIABILITIES (2000-2999)
                {'code': '2000', 'name': 'Current Liabilities', 'type': 'liability'},
                {'code': '2010', 'name': 'Accounts Payable', 'type': 'liability', 'parent_code': '2000'},
                {'code': '2100', 'name': 'Credit Cards', 'type': 'liability'},
                {'code': '2110', 'name': 'Business Credit Card', 'type': 'liability', 'parent_code': '2100'},
                {'code': '2200', 'name': 'Tax Liabilities', 'type': 'liability'},
                {'code': '2220', 'name': 'Sales Tax Payable', 'type': 'liability', 'parent_code': '2200'},
                
                # EQUITY (3000-3999)
                {'code': '3000', 'name': 'Equity', 'type': 'equity'},
                {'code': '3010', 'name': 'Common Stock', 'type': 'equity', 'parent_code': '3000'},
                {'code': '3030', 'name': 'Retained Earnings', 'type': 'equity', 'parent_code': '3000'},
                
                # REVENUE (4000-4999)
                {'code': '4000', 'name': 'Sales Revenue', 'type': 'revenue'},
                {'code': '4010', 'name': 'Product Sales', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4020', 'name': 'Service Revenue', 'type': 'revenue', 'parent_code': '4000'},
                
                # COST OF SALES (5000-5999)
                {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'expense'},
                {'code': '5010', 'name': 'Cost of Materials', 'type': 'expense', 'parent_code': '5000'},
                
                # OPERATING EXPENSES (6000-6999)
                {'code': '6000', 'name': 'Operating Expenses', 'type': 'expense'},
                {'code': '6010', 'name': 'Salaries and Wages', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6100', 'name': 'Rent Expense', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6200', 'name': 'Office Supplies', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6300', 'name': 'Professional Services', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6400', 'name': 'Marketing & Advertising', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6800', 'name': 'Depreciation Expense', 'type': 'expense', 'parent_code': '6000'},
            ]
        }
    
    @staticmethod
    def get_manufacturing_template():
        """Manufacturing-focused Chart of Accounts"""
        return {
            'name': 'Manufacturing Enterprise',
            'description': 'Specialized chart for manufacturing businesses',
            'accounts': [
                # Enhanced Inventory for Manufacturing
                {'code': '1200', 'name': 'Inventory', 'type': 'asset'},
                {'code': '1210', 'name': 'Raw Materials', 'type': 'asset', 'parent_code': '1200'},
                {'code': '1220', 'name': 'Work in Process', 'type': 'asset', 'parent_code': '1200'},
                {'code': '1230', 'name': 'Finished Goods', 'type': 'asset', 'parent_code': '1200'},
                {'code': '1240', 'name': 'Supplies & Consumables', 'type': 'asset', 'parent_code': '1200'},
                
                # Manufacturing Equipment
                {'code': '1500', 'name': 'Manufacturing Assets', 'type': 'asset'},
                {'code': '1510', 'name': 'Production Equipment', 'type': 'asset', 'parent_code': '1500'},
                {'code': '1515', 'name': 'Accumulated Depreciation - Production Equipment', 'type': 'asset', 'parent_code': '1500'},
                {'code': '1520', 'name': 'Manufacturing Tools', 'type': 'asset', 'parent_code': '1500'},
                {'code': '1530', 'name': 'Quality Control Equipment', 'type': 'asset', 'parent_code': '1500'},
                
                # Detailed Cost of Goods Sold
                {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'expense'},
                {'code': '5010', 'name': 'Direct Materials', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5020', 'name': 'Direct Labor', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5030', 'name': 'Manufacturing Overhead', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5040', 'name': 'Factory Utilities', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5050', 'name': 'Factory Maintenance', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5060', 'name': 'Quality Control Costs', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5070', 'name': 'Packaging & Shipping', 'type': 'expense', 'parent_code': '5000'},
                
                # Manufacturing-specific Expenses
                {'code': '6900', 'name': 'Manufacturing Expenses', 'type': 'expense'},
                {'code': '6910', 'name': 'Research & Development', 'type': 'expense', 'parent_code': '6900'},
                {'code': '6920', 'name': 'Product Design', 'type': 'expense', 'parent_code': '6900'},
                {'code': '6930', 'name': 'Production Planning', 'type': 'expense', 'parent_code': '6900'},
                {'code': '6940', 'name': 'Environmental Compliance', 'type': 'expense', 'parent_code': '6900'},
            ]
        }
    
    @staticmethod
    def get_service_company_template():
        """Service Company Chart of Accounts"""
        return {
            'name': 'Service Company',
            'description': 'Optimized for service-based businesses',
            'accounts': [
                # Service Revenue Categories
                {'code': '4000', 'name': 'Service Revenue', 'type': 'revenue'},
                {'code': '4010', 'name': 'Consulting Services', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4020', 'name': 'Professional Services', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4030', 'name': 'Training Services', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4040', 'name': 'Support Services', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4050', 'name': 'Subscription Revenue', 'type': 'revenue', 'parent_code': '4000'},
                
                # Service Cost Structure
                {'code': '5000', 'name': 'Cost of Services', 'type': 'expense'},
                {'code': '5010', 'name': 'Direct Service Costs', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5020', 'name': 'Subcontractor Costs', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5030', 'name': 'Service Materials', 'type': 'expense', 'parent_code': '5000'},
                
                # Professional Development
                {'code': '6000', 'name': 'Professional Development', 'type': 'expense'},
                {'code': '6010', 'name': 'Certifications & Training', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6020', 'name': 'Conference & Seminars', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6030', 'name': 'Professional Memberships', 'type': 'expense', 'parent_code': '6000'},
            ]
        }
    
    @staticmethod
    def get_tech_startup_template():
        """Tech Startup Chart of Accounts"""
        return {
            'name': 'Technology Startup',
            'description': 'Designed for technology and software companies',
            'accounts': [
                # Intellectual Property Assets
                {'code': '1700', 'name': 'Intangible Assets', 'type': 'asset'},
                {'code': '1710', 'name': 'Software Development Costs', 'type': 'asset', 'parent_code': '1700'},
                {'code': '1720', 'name': 'Patents & Trademarks', 'type': 'asset', 'parent_code': '1700'},
                {'code': '1730', 'name': 'Customer Lists', 'type': 'asset', 'parent_code': '1700'},
                
                # Technology Revenue
                {'code': '4000', 'name': 'Technology Revenue', 'type': 'revenue'},
                {'code': '4010', 'name': 'Software Licenses', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4020', 'name': 'SaaS Subscriptions', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4030', 'name': 'API Usage Revenue', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4040', 'name': 'Support & Maintenance', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4050', 'name': 'Professional Services', 'type': 'revenue', 'parent_code': '4000'},
                
                # Technology Expenses
                {'code': '6200', 'name': 'Technology Infrastructure', 'type': 'expense'},
                {'code': '6210', 'name': 'Cloud Computing Services', 'type': 'expense', 'parent_code': '6200'},
                {'code': '6220', 'name': 'Software Development Tools', 'type': 'expense', 'parent_code': '6200'},
                {'code': '6230', 'name': 'Third-party APIs', 'type': 'expense', 'parent_code': '6200'},
                {'code': '6240', 'name': 'Data Storage & Backup', 'type': 'expense', 'parent_code': '6200'},
                {'code': '6250', 'name': 'Security Services', 'type': 'expense', 'parent_code': '6200'},
                
                # R&D Expenses
                {'code': '6900', 'name': 'Research & Development', 'type': 'expense'},
                {'code': '6910', 'name': 'Software Development', 'type': 'expense', 'parent_code': '6900'},
                {'code': '6920', 'name': 'Product Testing', 'type': 'expense', 'parent_code': '6900'},
                {'code': '6930', 'name': 'Prototype Development', 'type': 'expense', 'parent_code': '6900'},
            ]
        }
    
    @staticmethod
    def get_nonprofit_template():
        """Nonprofit Organization Chart of Accounts"""
        return {
            'name': 'Nonprofit Organization',
            'description': 'Specialized for nonprofit and charitable organizations',
            'accounts': [
                # Net Assets (instead of Equity)
                {'code': '3000', 'name': 'Net Assets', 'type': 'equity'},
                {'code': '3010', 'name': 'Net Assets Without Donor Restrictions', 'type': 'equity', 'parent_code': '3000'},
                {'code': '3020', 'name': 'Net Assets With Donor Restrictions', 'type': 'equity', 'parent_code': '3000'},
                {'code': '3030', 'name': 'Temporarily Restricted Net Assets', 'type': 'equity', 'parent_code': '3000'},
                {'code': '3040', 'name': 'Permanently Restricted Net Assets', 'type': 'equity', 'parent_code': '3000'},
                
                # Revenue Sources
                {'code': '4000', 'name': 'Revenue', 'type': 'revenue'},
                {'code': '4010', 'name': 'Donations', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4020', 'name': 'Grants', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4030', 'name': 'Government Funding', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4040', 'name': 'Fundraising Events', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4050', 'name': 'Membership Fees', 'type': 'revenue', 'parent_code': '4000'},
                {'code': '4060', 'name': 'Program Service Revenue', 'type': 'revenue', 'parent_code': '4000'},
                
                # Program Expenses
                {'code': '5000', 'name': 'Program Expenses', 'type': 'expense'},
                {'code': '5010', 'name': 'Program Services', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5020', 'name': 'Community Outreach', 'type': 'expense', 'parent_code': '5000'},
                {'code': '5030', 'name': 'Educational Programs', 'type': 'expense', 'parent_code': '5000'},
                
                # Fundraising Expenses
                {'code': '6000', 'name': 'Fundraising Expenses', 'type': 'expense'},
                {'code': '6010', 'name': 'Fundraising Events', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6020', 'name': 'Grant Writing', 'type': 'expense', 'parent_code': '6000'},
                {'code': '6030', 'name': 'Donor Relations', 'type': 'expense', 'parent_code': '6000'},
            ]
        }
    
    @staticmethod
    def get_all_templates():
        """Get all available CoA templates"""
        return {
            'quickbooks_standard': CoATemplates.get_quickbooks_standard(),
            'manufacturing': CoATemplates.get_manufacturing_template(),
            'service_company': CoATemplates.get_service_company_template(),
            'tech_startup': CoATemplates.get_tech_startup_template(),
            'nonprofit': CoATemplates.get_nonprofit_template(),
        }
    
    @staticmethod
    def apply_template(template_name, organization_id=None):
        """Apply a CoA template to the current organization"""
        from app import db
        from modules.finance.models import ChartOfAccount
        
        templates = CoATemplates.get_all_templates()
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = templates[template_name]
        accounts = template['accounts']
        
        # Get existing account codes to avoid duplicates
        existing_codes = {acc.code for acc in ChartOfAccount.query.all()}
        
        # Find parent account IDs
        parent_accounts = {}
        for account in ChartOfAccount.query.all():
            parent_accounts[account.code] = account.id
        
        added_count = 0
        
        # First pass: Add parent accounts
        for account_data in accounts:
            if account_data['code'] not in existing_codes and 'parent_code' not in account_data:
                account = ChartOfAccount(
                    code=account_data['code'],
                    account_name=account_data['name'],
                    account_type=account_data['type'],
                    currency='USD',
                    allowed_dimensions=["department", "project", "location", "cost_center"]
                )
                db.session.add(account)
                db.session.flush()
                parent_accounts[account_data['code']] = account.id
                existing_codes.add(account_data['code'])
                added_count += 1
        
        # Second pass: Add child accounts
        for account_data in accounts:
            if account_data['code'] not in existing_codes and 'parent_code' in account_data:
                parent_id = parent_accounts.get(account_data['parent_code'])
                if parent_id:
                    account = ChartOfAccount(
                        code=account_data['code'],
                        account_name=account_data['name'],
                        account_type=account_data['type'],
                        currency='USD',
                        parent_id=parent_id,
                        allowed_dimensions=["department", "project", "location", "cost_center"]
                    )
                    db.session.add(account)
                    added_count += 1
        
        db.session.commit()
        return {
            'template_applied': template_name,
            'accounts_added': added_count,
            'template_info': template
        }


# Standalone functions for API routes
def get_all_templates():
    """Get all available CoA templates for API"""
    return CoATemplates.get_all_templates()


def get_template_by_id(template_id):
    """Get a specific CoA template by ID for API"""
    templates = CoATemplates.get_all_templates()
    return templates.get(template_id)


def apply_template_to_db(template_id, organization_id=None):
    """Apply a CoA template to the database for API"""
    return CoATemplates.apply_template(template_id, organization_id)


