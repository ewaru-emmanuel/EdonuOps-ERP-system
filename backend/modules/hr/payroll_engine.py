# backend/modules/hr/payroll_engine.py

def calculate_payroll(salary, taxes=0.20, deductions=0.10):
    """
    A simple payroll calculation function.
    In a real-world scenario, this would be much more complex.
    """
    gross_pay = salary
    tax_amount = gross_pay * taxes
    deduction_amount = gross_pay * deductions
    net_pay = gross_pay - tax_amount - deduction_amount
    return gross_pay, net_pay