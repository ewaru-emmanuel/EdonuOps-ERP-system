from app import db  # ✅ Absolute import
from datetime import datetime, date
import os
try:
    # Use portable JSON type: JSONB on Postgres, JSON on others
    from sqlalchemy.dialects.postgresql import JSONB as _PG_JSON
except Exception:
    _PG_JSON = None

def _get_json_type():
    db_url = os.environ.get("DATABASE_URL", "")
    if _PG_JSON is not None and "postgresql" in db_url.lower():
        return _PG_JSON
    # Fallback to SQLAlchemy JSON which works with SQLite
    try:
        from sqlalchemy import JSON as _JSON
        return _JSON
    except Exception:
        # As a last resort, store as Text-compatible JSON string
        from sqlalchemy import Text as _Text
        return _Text

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    type = db.Column(db.String(20), default='customer')  # customer, vendor, partner, prospect
    status = db.Column(db.String(20), default='active')  # active, inactive
    region = db.Column(db.String(50))
    assigned_team = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # Relationship
    company_ref = db.relationship('Company', backref='contacts')

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    region = db.Column(db.String(50))
    assigned_team = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    customer_number = db.Column(db.String(50), unique=True, nullable=False)
    credit_limit = db.Column(db.Numeric(15, 2), default=0.0)
    payment_terms = db.Column(db.String(50), default='Net 30')
    tax_exempt = db.Column(db.Boolean, default=False)
    tax_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    contact = db.relationship('Contact', backref='customer_profile')

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    source = db.Column(db.String(50), default='website')  # website, referral, trade_show, social_media, cold_call
    status = db.Column(db.String(20), default='new')  # new, qualified, proposal, negotiation, closed
    lead_status = db.Column(db.String(20))  # explicit lead status field for UI filters
    region = db.Column(db.String(50))
    assigned_team = db.Column(db.String(100))
    score = db.Column(db.Integer, default=0)
    
    # Enhanced AI scoring fields
    ai_score = db.Column(db.Integer, default=0)  # AI-generated score
    ai_explanation = db.Column(db.Text)  # AI explanation of score
    ai_confidence = db.Column(db.Integer, default=0)  # AI confidence level
    behavioral_data = db.Column(_get_json_type())  # Behavioral tracking data
    last_ai_analysis = db.Column(db.DateTime)  # When AI last analyzed this lead
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    pipeline_id = db.Column(db.Integer, db.ForeignKey('pipelines.id'))
    amount = db.Column(db.Float, default=0.0)
    stage = db.Column(db.String(50), default='prospecting')  # prospecting, qualification, proposal, negotiation, closed_won, closed_lost
    probability = db.Column(db.Integer, default=0)
    expected_close_date = db.Column(db.Date)
    region = db.Column(db.String(50))
    assigned_team = db.Column(db.String(100))
    products = db.Column(_get_json_type())  # list of {sku,name,quantity,unit_price}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    contact = db.relationship('Contact', backref='opportunities')
    company = db.relationship('Company', backref='opportunities')
    pipeline = db.relationship('Pipeline', backref='opportunities')

class Communication(db.Model):
    __tablename__ = 'communications'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    type = db.Column(db.String(20))  # call, email, sms, note, meeting
    direction = db.Column(db.String(10))  # inbound, outbound
    subject = db.Column(db.String(200))
    content = db.Column(db.Text)
    duration = db.Column(db.Integer)  # for calls in seconds
    status = db.Column(db.String(20))  # completed, missed, scheduled
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_for = db.Column(db.DateTime)  # for scheduled communications

class FollowUp(db.Model):
    __tablename__ = 'follow_ups'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    type = db.Column(db.String(50))  # call, email, meeting, task
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, overdue
    notes = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class CRMUser(db.Model):
    __tablename__ = 'crm_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='agent')  # admin, manager, agent
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LeadIntake(db.Model):
    __tablename__ = 'lead_intakes'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100))  # Microsoft Forms, Website, Puzzel Agent
    form_data = db.Column(db.Text)  # Store all form fields as JSON string
    status = db.Column(db.String(20), default='new')  # new, processed, converted
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='open')  # open, pending, resolved, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50))  # support, billing, technical, etc.
    tags = db.Column(db.String(200))  # comma-separated tags
    customer_email = db.Column(db.String(200))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeBaseArticle(db.Model):
    __tablename__ = 'knowledge_base_articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    tags = db.Column(db.String(200))  # comma-separated tags for simple search
    published = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)  # Standardized user identification)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeBaseAttachment(db.Model):
    __tablename__ = 'knowledge_base_attachments'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_base_articles.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(120))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    article = db.relationship('KnowledgeBaseArticle', backref='attachments')


class Pipeline(db.Model):
    __tablename__ = 'pipelines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(40), default='sales')  # future use
    stages = db.Column(_get_json_type())  # ordered list of stage names
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TimeEntry(db.Model):
    __tablename__ = 'time_entries'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)
    billable = db.Column(db.Boolean, default=True)
    rate = db.Column(db.Numeric(12, 2), default=0.00)
    currency = db.Column(db.String(10), default='USD')
    invoiced = db.Column(db.Boolean, default=False)
    invoice_id = db.Column(db.Integer)  # optional link to finance invoice
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BehavioralEvent(db.Model):
    __tablename__ = 'behavioral_events'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    event_type = db.Column(db.String(50))  # email_open, email_click, website_visit, call_duration, meeting_attended
    event_data = db.Column(_get_json_type())  # Additional event-specific data
    engagement_score = db.Column(db.Integer, default=0)  # 0-100 engagement level
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = db.relationship('Lead', backref='behavioral_events')
    contact = db.relationship('Contact', backref='behavioral_events')
    opportunity = db.relationship('Opportunity', backref='behavioral_events')

