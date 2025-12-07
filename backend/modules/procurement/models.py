# backend/modules/procurement/models.py

from app import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(50), default='Net 30')
    credit_limit = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    # Segmentation fields
    category = db.Column(db.String(100))  # e.g., "Raw Materials", "Services"
    risk_level = db.Column(db.String(50))  # e.g., "low", "medium", "high"
    region = db.Column(db.String(100))  # e.g., "NA", "EMEA"
    is_preferred = db.Column(db.Boolean, default=False)
    # Performance KPIs (simple snapshot fields)
    on_time_delivery_rate = db.Column(db.Float, default=0.0)
    price_variance_pct = db.Column(db.Float, default=0.0)
    quality_score = db.Column(db.Float, default=0.0)
    performance_notes = db.Column(db.Text)
    last_reviewed_at = db.Column(db.DateTime)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide vendors
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = db.relationship('VendorDocument', backref='vendor', cascade='all, delete-orphan')
    communications = db.relationship('VendorCommunication', backref='vendor', cascade='all, delete-orphan')

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    expected_delivery = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, received, closed
    total_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide POs
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = db.relationship('Vendor', backref='purchase_orders')
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan')
    attachments = db.relationship('POAttachment', backref='purchase_order', cascade='all, delete-orphan')

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    received_quantity = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class POAttachment(db.Model):
    __tablename__ = 'po_attachments'
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class VendorDocument(db.Model):
    __tablename__ = 'vendor_documents'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    doc_type = db.Column(db.String(100))  # e.g., "Insurance", "W-9", "ESG"
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    effective_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)


class VendorCommunication(db.Model):
    __tablename__ = 'vendor_communications'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    channel = db.Column(db.String(50))  # email, phone, portal, meeting
    direction = db.Column(db.String(10))  # in, out
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    related_rfx_id = db.Column(db.Integer)  # placeholder for future RFx linkage
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- RFx (RFQ) Models ----------------
class RFQ(db.Model):
    __tablename__ = 'rfqs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default='draft')  # draft, open, closed, awarded, cancelled
    due_date = db.Column(db.Date)
    criteria_json = db.Column(db.Text)  # JSON string of [{name, weight}]
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('RFQItem', backref='rfq', cascade='all, delete-orphan')
    invitations = db.relationship('RFQInvitation', backref='rfq', cascade='all, delete-orphan')
    responses = db.relationship('RFQResponseHeader', backref='rfq', cascade='all, delete-orphan')


class RFQItem(db.Model):
    __tablename__ = 'rfq_items'
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    uom = db.Column(db.String(50))


class RFQInvitation(db.Model):
    __tablename__ = 'rfq_invitations'
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    invite_token = db.Column(db.String(64), unique=True)
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)

    vendor = db.relationship('Vendor')


class RFQResponseHeader(db.Model):
    __tablename__ = 'rfq_responses'
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    currency = db.Column(db.String(10), default='USD')
    validity_days = db.Column(db.Integer)
    notes = db.Column(db.Text)
    total_price = db.Column(db.Float, default=0.0)
    delivery_days = db.Column(db.Integer)
    score_json = db.Column(db.Text)  # JSON string of criterion scores
    total_score = db.Column(db.Float, default=0.0)

    vendor = db.relationship('Vendor')
    items = db.relationship('RFQResponseItem', backref='response', cascade='all, delete-orphan')


class RFQResponseItem(db.Model):
    __tablename__ = 'rfq_response_items'
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('rfq_responses.id'), nullable=False)
    rfq_item_id = db.Column(db.Integer, db.ForeignKey('rfq_items.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    delivery_days = db.Column(db.Integer)
    notes = db.Column(db.Text)

    rfq_item = db.relationship('RFQItem')


# ---------------- Contract Lifecycle Management (CLM) ----------------
class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'))
    status = db.Column(db.String(30), default='active')  # draft, active, expired, terminated
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    renewal_notice_days = db.Column(db.Integer, default=60)
    auto_renew = db.Column(db.Boolean, default=False)
    contract_value = db.Column(db.Float, default=0.0)
    terms_summary = db.Column(db.Text)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = db.relationship('Vendor')
    rfq = db.relationship('RFQ')
    documents = db.relationship('ContractDocument', backref='contract', cascade='all, delete-orphan')


class ContractDocument(db.Model):
    __tablename__ = 'contract_documents'
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    doc_type = db.Column(db.String(100))
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)