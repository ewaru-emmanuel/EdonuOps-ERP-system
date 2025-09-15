"""
Localization System for Chart of Accounts
Handles country-specific CoA templates and compliance requirements
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .coa_templates import COATemplate, create_retail_template, create_services_template
from .statutory_modules import StatutoryModule

class CountryCompliancePack:
    """Represents a complete compliance package for a country"""
    
    def __init__(self, country_code: str, country_name: str, currency: str, 
                 accounting_standard: str, fiscal_year_start: str = '01-01'):
        self.country_code = country_code
        self.country_name = country_name
        self.currency = currency
        self.accounting_standard = accounting_standard
        self.fiscal_year_start = fiscal_year_start
        self.coa_templates = {}
        self.statutory_modules = {}
        self.tax_rates = {}
        self.compliance_forms = {}
        self.localization_rules = {}
    
    def add_coa_template(self, industry: str, template: COATemplate):
        """Add a CoA template for a specific industry in this country"""
        self.coa_templates[industry] = template
    
    def add_statutory_module(self, module_id: str, module: StatutoryModule):
        """Add a statutory module for this country"""
        self.statutory_modules[module_id] = module
    
    def add_tax_rate(self, tax_type: str, rate: float, description: str = None):
        """Add a tax rate for this country"""
        self.tax_rates[tax_type] = {
            'rate': rate,
            'description': description or f"{tax_type} tax rate",
            'effective_date': datetime.utcnow().isoformat()
        }
    
    def add_compliance_form(self, form_id: str, form_name: str, frequency: str, 
                           due_date: str, description: str = None):
        """Add a compliance form for this country"""
        self.compliance_forms[form_id] = {
            'name': form_name,
            'frequency': frequency,
            'due_date': due_date,
            'description': description or f"{form_name} compliance form",
            'is_required': True
        }
    
    def add_localization_rule(self, rule_type: str, rule_data: Dict):
        """Add a localization rule for this country"""
        self.localization_rules[rule_type] = rule_data

class LocalizationSystem:
    """Main localization system manager"""
    
    def __init__(self):
        self.compliance_packs = self._initialize_compliance_packs()
    
    def _initialize_compliance_packs(self) -> Dict[str, CountryCompliancePack]:
        """Initialize compliance packs for different countries"""
        packs = {}
        
        # United States
        packs['US'] = self._create_us_compliance_pack()
        
        # India
        packs['IN'] = self._create_india_compliance_pack()
        
        # United Kingdom
        packs['GB'] = self._create_uk_compliance_pack()
        
        # Kenya
        packs['KE'] = self._create_kenya_compliance_pack()
        
        # Canada
        packs['CA'] = self._create_canada_compliance_pack()
        
        # Australia
        packs['AU'] = self._create_australia_compliance_pack()
        
        # Germany
        packs['DE'] = self._create_germany_compliance_pack()
        
        # France
        packs['FR'] = self._create_france_compliance_pack()
        
        return packs
    
    def _create_us_compliance_pack(self) -> CountryCompliancePack:
        """Create US compliance pack"""
        pack = CountryCompliancePack(
            country_code='US',
            country_name='United States',
            currency='USD',
            accounting_standard='US GAAP',
            fiscal_year_start='01-01'
        )
        
        # Add CoA templates for US
        pack.add_coa_template('retail', self._create_us_retail_template())
        pack.add_coa_template('services', self._create_us_services_template())
        pack.add_coa_template('manufacturing', self._create_us_manufacturing_template())
        pack.add_coa_template('freelancer', self._create_us_freelancer_template())
        
        # Add statutory modules
        pack.add_statutory_module('sales_tax', StatutoryModule(
            id='sales_tax',
            name='Sales Tax',
            description='US Sales Tax compliance',
            country='US',
            required_accounts=['2100', '2110'],  # Sales Tax Payable, Sales Tax Receivable
            compliance_forms=['Form 941', 'Form 940']
        ))
        
        pack.add_statutory_module('payroll_tax', StatutoryModule(
            id='payroll_tax',
            name='Payroll Tax',
            description='US Payroll Tax compliance',
            country='US',
            required_accounts=['2120', '2130', '2140'],  # Payroll Tax Payable, etc.
            compliance_forms=['Form 941', 'Form 940', 'W-2', 'W-3']
        ))
        
        # Add tax rates
        pack.add_tax_rate('federal_income_tax', 0.21, 'Federal Corporate Income Tax')
        pack.add_tax_rate('state_income_tax', 0.05, 'State Income Tax (varies by state)')
        pack.add_tax_rate('sales_tax', 0.08, 'Sales Tax (varies by state)')
        pack.add_tax_rate('payroll_tax', 0.062, 'Social Security Tax')
        pack.add_tax_rate('medicare_tax', 0.0145, 'Medicare Tax')
        
        # Add compliance forms
        pack.add_compliance_form('form_1120', 'Form 1120 - Corporate Income Tax Return', 'annual', '15th day of 3rd month after tax year end')
        pack.add_compliance_form('form_941', 'Form 941 - Employer Quarterly Federal Tax Return', 'quarterly', 'Last day of month following quarter end')
        pack.add_compliance_form('form_940', 'Form 940 - Employer Annual Federal Unemployment Tax Return', 'annual', 'January 31')
        pack.add_compliance_form('w2', 'W-2 - Wage and Tax Statement', 'annual', 'January 31')
        
        # Add localization rules
        pack.add_localization_rule('currency_format', {
            'symbol': '$',
            'position': 'before',
            'decimal_places': 2,
            'thousands_separator': ',',
            'decimal_separator': '.'
        })
        
        pack.add_localization_rule('date_format', {
            'format': 'MM/DD/YYYY',
            'fiscal_year_start': '01-01',
            'fiscal_year_end': '12-31'
        })
        
        pack.add_localization_rule('accounting_standards', {
            'standard': 'US GAAP',
            'revenue_recognition': 'ASC 606',
            'lease_accounting': 'ASC 842',
            'financial_instruments': 'ASC 820'
        })
        
        return pack
    
    def _create_us_retail_template(self):
        """Create US retail CoA template"""
        from .coa_templates import create_retail_template
        return create_retail_template()
    
    def _create_us_services_template(self):
        """Create US services CoA template"""
        from .coa_templates import create_services_template
        return create_services_template()
    
    def _create_us_manufacturing_template(self):
        """Create US manufacturing CoA template"""
        from .coa_templates import create_manufacturing_template
        return create_manufacturing_template()
    
    def _create_us_freelancer_template(self):
        """Create US freelancer CoA template"""
        from .coa_templates import create_freelancer_template
        return create_freelancer_template()
    
    def _create_india_retail_template(self):
        """Create India retail CoA template"""
        from .coa_templates import create_retail_template
        return create_retail_template()
    
    def _create_india_services_template(self):
        """Create India services CoA template"""
        from .coa_templates import create_services_template
        return create_services_template()
    
    def _create_india_manufacturing_template(self):
        """Create India manufacturing CoA template"""
        from .coa_templates import create_manufacturing_template
        return create_manufacturing_template()
    
    def _create_india_freelancer_template(self):
        """Create India freelancer CoA template"""
        from .coa_templates import create_freelancer_template
        return create_freelancer_template()
    
    def _create_uk_retail_template(self):
        """Create UK retail CoA template"""
        from .coa_templates import create_retail_template
        return create_retail_template()
    
    def _create_uk_services_template(self):
        """Create UK services CoA template"""
        from .coa_templates import create_services_template
        return create_services_template()
    
    def _create_uk_manufacturing_template(self):
        """Create UK manufacturing CoA template"""
        from .coa_templates import create_manufacturing_template
        return create_manufacturing_template()
    
    def _create_uk_freelancer_template(self):
        """Create UK freelancer CoA template"""
        from .coa_templates import create_freelancer_template
        return create_freelancer_template()
    
    def _create_kenya_retail_template(self):
        """Create Kenya retail CoA template"""
        from .coa_templates import create_retail_template
        return create_retail_template()
    
    def _create_kenya_services_template(self):
        """Create Kenya services CoA template"""
        from .coa_templates import create_services_template
        return create_services_template()
    
    def _create_kenya_manufacturing_template(self):
        """Create Kenya manufacturing CoA template"""
        from .coa_templates import create_manufacturing_template
        return create_manufacturing_template()
    
    def _create_kenya_freelancer_template(self):
        """Create Kenya freelancer CoA template"""
        from .coa_templates import create_freelancer_template
        return create_freelancer_template()
    
    def _create_india_compliance_pack(self) -> CountryCompliancePack:
        """Create India compliance pack"""
        pack = CountryCompliancePack(
            country_code='IN',
            country_name='India',
            currency='INR',
            accounting_standard='Ind AS',
            fiscal_year_start='04-01'
        )
        
        # Add CoA templates for India
        pack.add_coa_template('retail', self._create_india_retail_template())
        pack.add_coa_template('services', self._create_india_services_template())
        pack.add_coa_template('manufacturing', self._create_india_manufacturing_template())
        pack.add_coa_template('freelancer', self._create_india_freelancer_template())
        
        # Add statutory modules
        pack.add_statutory_module('gst', StatutoryModule(
            id='gst',
            name='GST (Goods & Services Tax)',
            description='Indian GST compliance',
            country='IN',
            required_accounts=['2200', '2210', '2220', '2230'],  # Input GST, Output GST, etc.
            compliance_forms=['GSTR-1', 'GSTR-3B', 'GSTR-9']
        ))
        
        pack.add_statutory_module('tds', StatutoryModule(
            id='tds',
            name='TDS (Tax Deducted at Source)',
            description='Indian TDS compliance',
            country='IN',
            required_accounts=['2240', '2250'],  # TDS Payable, TDS Receivable
            compliance_forms=['Form 16', 'Form 16A', 'Form 26Q', 'Form 27Q']
        ))
        
        # Add tax rates
        pack.add_tax_rate('gst', 0.18, 'GST Rate (varies by product category)')
        pack.add_tax_rate('tds', 0.10, 'TDS Rate (varies by payment type)')
        pack.add_tax_rate('income_tax', 0.30, 'Corporate Income Tax')
        pack.add_tax_rate('cess', 0.04, 'Health and Education Cess')
        
        # Add compliance forms
        pack.add_compliance_form('gstr1', 'GSTR-1 - Outward Supplies', 'monthly', '11th of following month')
        pack.add_compliance_form('gstr3b', 'GSTR-3B - Monthly Return', 'monthly', '20th of following month')
        pack.add_compliance_form('gstr9', 'GSTR-9 - Annual Return', 'annual', '31st December')
        pack.add_compliance_form('form16', 'Form 16 - TDS Certificate', 'annual', '31st May')
        pack.add_compliance_form('itr', 'ITR - Income Tax Return', 'annual', '31st July')
        
        # Add localization rules
        pack.add_localization_rule('currency_format', {
            'symbol': '₹',
            'position': 'before',
            'decimal_places': 2,
            'thousands_separator': ',',
            'decimal_separator': '.'
        })
        
        pack.add_localization_rule('date_format', {
            'format': 'DD/MM/YYYY',
            'fiscal_year_start': '01-04',
            'fiscal_year_end': '31-03'
        })
        
        pack.add_localization_rule('accounting_standards', {
            'standard': 'Ind AS',
            'revenue_recognition': 'Ind AS 115',
            'lease_accounting': 'Ind AS 116',
            'financial_instruments': 'Ind AS 109'
        })
        
        return pack
    
    def _create_uk_compliance_pack(self) -> CountryCompliancePack:
        """Create UK compliance pack"""
        pack = CountryCompliancePack(
            country_code='GB',
            country_name='United Kingdom',
            currency='GBP',
            accounting_standard='UK GAAP',
            fiscal_year_start='04-06'
        )
        
        # Add CoA templates for UK
        pack.add_coa_template('retail', self._create_uk_retail_template())
        pack.add_coa_template('services', self._create_uk_services_template())
        pack.add_coa_template('manufacturing', self._create_uk_manufacturing_template())
        pack.add_coa_template('freelancer', self._create_uk_freelancer_template())
        
        # Add statutory modules
        pack.add_statutory_module('vat', StatutoryModule(
            id='vat',
            name='VAT (Value Added Tax)',
            description='UK VAT compliance',
            country='GB',
            required_accounts=['2300', '2310', '2320'],  # Input VAT, Output VAT, etc.
            compliance_forms=['VAT Return', 'VAT100']
        ))
        
        pack.add_statutory_module('paye', StatutoryModule(
            id='paye',
            name='PAYE (Pay As You Earn)',
            description='UK PAYE compliance',
            country='GB',
            required_accounts=['2330', '2340'],  # PAYE Payable, etc.
            compliance_forms=['P60', 'P45', 'P11D']
        ))
        
        # Add tax rates
        pack.add_tax_rate('vat_standard', 0.20, 'Standard VAT Rate')
        pack.add_tax_rate('vat_reduced', 0.05, 'Reduced VAT Rate')
        pack.add_tax_rate('vat_zero', 0.00, 'Zero VAT Rate')
        pack.add_tax_rate('corporation_tax', 0.19, 'Corporation Tax')
        pack.add_tax_rate('income_tax', 0.20, 'Income Tax (basic rate)')
        
        # Add compliance forms
        pack.add_compliance_form('vat_return', 'VAT Return', 'quarterly', '7th of month following quarter end')
        pack.add_compliance_form('ct600', 'CT600 - Corporation Tax Return', 'annual', '12 months after accounting period end')
        pack.add_compliance_form('p60', 'P60 - End of Year Certificate', 'annual', '31st May')
        pack.add_compliance_form('p45', 'P45 - Details of Employee Leaving', 'as_needed', 'On termination')
        
        # Add localization rules
        pack.add_localization_rule('currency_format', {
            'symbol': '£',
            'position': 'before',
            'decimal_places': 2,
            'thousands_separator': ',',
            'decimal_separator': '.'
        })
        
        pack.add_localization_rule('date_format', {
            'format': 'DD/MM/YYYY',
            'fiscal_year_start': '06-04',
            'fiscal_year_end': '05-04'
        })
        
        pack.add_localization_rule('accounting_standards', {
            'standard': 'UK GAAP',
            'revenue_recognition': 'FRS 102',
            'lease_accounting': 'FRS 102',
            'financial_instruments': 'FRS 102'
        })
        
        return pack
    
    def _create_kenya_compliance_pack(self) -> CountryCompliancePack:
        """Create Kenya compliance pack"""
        pack = CountryCompliancePack(
            country_code='KE',
            country_name='Kenya',
            currency='KES',
            accounting_standard='IFRS',
            fiscal_year_start='01-01'
        )
        
        # Add CoA templates for Kenya
        pack.add_coa_template('retail', self._create_kenya_retail_template())
        pack.add_coa_template('services', self._create_kenya_services_template())
        pack.add_coa_template('manufacturing', self._create_kenya_manufacturing_template())
        pack.add_coa_template('freelancer', self._create_kenya_freelancer_template())
        
        # Add statutory modules
        pack.add_statutory_module('vat', StatutoryModule(
            id='vat',
            name='VAT (Value Added Tax)',
            description='Kenyan VAT compliance',
            country='KE',
            required_accounts=['2400', '2410', '2420'],  # Input VAT, Output VAT, etc.
            compliance_forms=['VAT Return', 'VAT3']
        ))
        
        pack.add_statutory_module('withholding_tax', StatutoryModule(
            id='withholding_tax',
            name='Withholding Tax',
            description='Kenyan Withholding Tax compliance',
            country='KE',
            required_accounts=['2430', '2440'],  # WHT Payable, WHT Receivable
            compliance_forms=['WHT Certificate', 'WHT Return']
        ))
        
        # Add tax rates
        pack.add_tax_rate('vat', 0.16, 'VAT Rate')
        pack.add_tax_rate('withholding_tax', 0.05, 'Withholding Tax Rate')
        pack.add_tax_rate('corporation_tax', 0.30, 'Corporation Tax')
        pack.add_tax_rate('income_tax', 0.30, 'Income Tax (highest rate)')
        pack.add_tax_rate('nhif', 0.015, 'NHIF Contribution')
        pack.add_tax_rate('nssf', 0.06, 'NSSF Contribution')
        
        # Add compliance forms
        pack.add_compliance_form('vat_return', 'VAT Return', 'monthly', '20th of following month')
        pack.add_compliance_form('wht_return', 'Withholding Tax Return', 'monthly', '20th of following month')
        pack.add_compliance_form('corporation_tax', 'Corporation Tax Return', 'annual', '6 months after year end')
        pack.add_compliance_form('income_tax', 'Income Tax Return', 'annual', '30th June')
        
        # Add localization rules
        pack.add_localization_rule('currency_format', {
            'symbol': 'KSh',
            'position': 'before',
            'decimal_places': 2,
            'thousands_separator': ',',
            'decimal_separator': '.'
        })
        
        pack.add_localization_rule('date_format', {
            'format': 'DD/MM/YYYY',
            'fiscal_year_start': '01-01',
            'fiscal_year_end': '31-12'
        })
        
        pack.add_localization_rule('accounting_standards', {
            'standard': 'IFRS',
            'revenue_recognition': 'IFRS 15',
            'lease_accounting': 'IFRS 16',
            'financial_instruments': 'IFRS 9'
        })
        
        return pack
    
    def _create_canada_compliance_pack(self) -> CountryCompliancePack:
        """Create Canada compliance pack"""
        pack = CountryCompliancePack(
            country_code='CA',
            country_name='Canada',
            currency='CAD',
            accounting_standard='ASPE',
            fiscal_year_start='01-01'
        )
        
        # Add tax rates
        pack.add_tax_rate('gst', 0.05, 'Goods and Services Tax')
        pack.add_tax_rate('hst', 0.13, 'Harmonized Sales Tax (Ontario)')
        pack.add_tax_rate('qst', 0.09975, 'Quebec Sales Tax')
        pack.add_tax_rate('corporation_tax', 0.15, 'Federal Corporation Tax')
        pack.add_tax_rate('provincial_tax', 0.10, 'Provincial Corporation Tax (varies)')
        
        return pack
    
    def _create_australia_compliance_pack(self) -> CountryCompliancePack:
        """Create Australia compliance pack"""
        pack = CountryCompliancePack(
            country_code='AU',
            country_name='Australia',
            currency='AUD',
            accounting_standard='AASB',
            fiscal_year_start='07-01'
        )
        
        # Add tax rates
        pack.add_tax_rate('gst', 0.10, 'Goods and Services Tax')
        pack.add_tax_rate('corporation_tax', 0.30, 'Corporation Tax')
        pack.add_tax_rate('income_tax', 0.45, 'Income Tax (highest rate)')
        pack.add_tax_rate('fbt', 0.47, 'Fringe Benefits Tax')
        
        return pack
    
    def _create_germany_compliance_pack(self) -> CountryCompliancePack:
        """Create Germany compliance pack"""
        pack = CountryCompliancePack(
            country_code='DE',
            country_name='Germany',
            currency='EUR',
            accounting_standard='HGB',
            fiscal_year_start='01-01'
        )
        
        # Add tax rates
        pack.add_tax_rate('vat', 0.19, 'Value Added Tax')
        pack.add_tax_rate('vat_reduced', 0.07, 'Reduced VAT Rate')
        pack.add_tax_rate('corporation_tax', 0.15, 'Corporation Tax')
        pack.add_tax_rate('trade_tax', 0.14, 'Trade Tax (varies by municipality)')
        pack.add_tax_rate('solidarity_surcharge', 0.05, 'Solidarity Surcharge')
        
        return pack
    
    def _create_france_compliance_pack(self) -> CountryCompliancePack:
        """Create France compliance pack"""
        pack = CountryCompliancePack(
            country_code='FR',
            country_name='France',
            currency='EUR',
            accounting_standard='PCG',
            fiscal_year_start='01-01'
        )
        
        # Add tax rates
        pack.add_tax_rate('vat', 0.20, 'Value Added Tax')
        pack.add_tax_rate('vat_reduced', 0.055, 'Reduced VAT Rate')
        pack.add_tax_rate('corporation_tax', 0.15, 'Corporation Tax (small companies)')
        pack.add_tax_rate('corporation_tax_standard', 0.25, 'Corporation Tax (standard)')
        pack.add_tax_rate('csg', 0.092, 'CSG Contribution')
        
        return pack
    
    def get_compliance_pack(self, country_code: str) -> Optional[CountryCompliancePack]:
        """Get compliance pack for a specific country"""
        return self.compliance_packs.get(country_code.upper())
    
    def get_available_countries(self) -> List[Dict[str, str]]:
        """Get list of available countries"""
        return [
            {
                'code': pack.country_code,
                'name': pack.country_name,
                'currency': pack.currency,
                'accounting_standard': pack.accounting_standard
            }
            for pack in self.compliance_packs.values()
        ]
    
    def get_coa_template(self, country_code: str, industry: str) -> Optional[COATemplate]:
        """Get CoA template for specific country and industry"""
        pack = self.get_compliance_pack(country_code)
        if not pack:
            return None
        return pack.coa_templates.get(industry)
    
    def get_statutory_modules(self, country_code: str) -> List[StatutoryModule]:
        """Get statutory modules for a specific country"""
        pack = self.get_compliance_pack(country_code)
        if not pack:
            return []
        return list(pack.statutory_modules.values())
    
    def get_tax_rates(self, country_code: str) -> Dict[str, Dict]:
        """Get tax rates for a specific country"""
        pack = self.get_compliance_pack(country_code)
        if not pack:
            return {}
        return pack.tax_rates
    
    def get_compliance_forms(self, country_code: str) -> Dict[str, Dict]:
        """Get compliance forms for a specific country"""
        pack = self.get_compliance_pack(country_code)
        if not pack:
            return {}
        return pack.compliance_forms
    
    def get_localization_rules(self, country_code: str) -> Dict[str, Dict]:
        """Get localization rules for a specific country"""
        pack = self.get_compliance_pack(country_code)
        if not pack:
            return {}
        return pack.localization_rules

# Global instance
localization_system = LocalizationSystem()

def get_localization_system() -> LocalizationSystem:
    """Get the global localization system instance"""
    return localization_system
