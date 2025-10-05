from app import db
from datetime import datetime
from sqlalchemy import func

class Customer(db.Model):
    """Customer model for accounts receivable management"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Business information
    company_name = db.Column(db.String(200), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    credit_limit = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(50), default='Net 30')  # Net 30, Net 15, Cash on Delivery, etc.
    
    # Status and categorization
    is_active = db.Column(db.Boolean, default=True)
    customer_type = db.Column(db.String(50), default='regular')  # regular, vip, wholesale, retail
    category = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    
    # Performance metrics
    total_sales = db.Column(db.Float, default=0.0)
    outstanding_balance = db.Column(db.Float, default=0.0)
    last_payment_date = db.Column(db.Date, nullable=True)
    average_payment_days = db.Column(db.Integer, default=30)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification, nullable=True)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    @property
    def overdue_amount(self):
        """Calculate overdue amount"""
        overdue_invoices = [inv for inv in self.invoices if inv.is_overdue and inv.status != 'paid']
        return sum(inv.outstanding_amount for inv in overdue_invoices)
    
    @property
    def current_amount(self):
        """Calculate current (not overdue) amount"""
        return self.outstanding_balance - self.overdue_amount

class Invoice(db.Model):
    """Invoice model for accounts receivable tracking"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Invoice details
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    
    # Financial information
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    outstanding_amount = db.Column(db.Float, nullable=False)
    
    # Status and categorization
    status = db.Column(db.String(20), default='pending')  # pending, sent, paid, overdue, cancelled
    payment_method = db.Column(db.String(50), nullable=True)  # cash, check, bank_transfer, credit_card
    description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # References
    po_reference = db.Column(db.String(100), nullable=True)  # Customer PO number
    project_id = db.Column(db.Integer, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification, nullable=True)
    
    # Relationships
    payments = db.relationship('Payment', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status == 'paid':
            return False
        return datetime.now().date() > self.due_date
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if not self.is_overdue:
            return 0
        return (datetime.now().date() - self.due_date).days
    
    @property
    def aging_bucket(self):
        """Get aging bucket for the invoice"""
        if not self.is_overdue:
            return 'current'
        days = self.days_overdue
        if days <= 30:
            return '1-30 days'
        elif days <= 60:
            return '31-60 days'
        elif days <= 90:
            return '61-90 days'
        else:
            return '90+ days'

class Payment(db.Model):
    """Payment model for tracking invoice payments"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    # Payment details
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # cash, check, bank_transfer, credit_card
    reference_number = db.Column(db.String(100), nullable=True)  # Check number, transaction ID, etc.
    
    # Status and notes
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, cancelled
    notes = db.Column(db.Text, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification, nullable=True)
    
    def __repr__(self):
        return f'<Payment {self.amount} for Invoice {self.invoice_id}>'

class CustomerCommunication(db.Model):
    """Track communications with customers"""
    __tablename__ = 'customer_communications'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Communication details
    communication_type = db.Column(db.String(50), nullable=False)  # email, phone, meeting, letter
    subject = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=True)
    direction = db.Column(db.String(20), nullable=False)  # inbound, outbound
    
    # Status and follow-up
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    follow_up_date = db.Column(db.Date, nullable=True)
    follow_up_notes = db.Column(db.Text, nullable=True)
    
    # References
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer)  # Standardized user identification, nullable=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='communications')
    
    def __repr__(self):
        return f'<CustomerCommunication {self.communication_type} - {self.customer.name}>'

