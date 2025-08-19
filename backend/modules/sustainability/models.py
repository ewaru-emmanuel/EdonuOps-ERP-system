from app import db
from datetime import datetime

class EnvironmentalMetric(db.Model):
    __tablename__ = 'environmental_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    reporting_period = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SocialMetric(db.Model):
    __tablename__ = 'social_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    reporting_period = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GovernanceMetric(db.Model):
    __tablename__ = 'governance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    reporting_period = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ESGReport(db.Model):
    __tablename__ = 'esg_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(100), nullable=False)
    reporting_period = db.Column(db.String(50), nullable=False)
    esg_rating = db.Column(db.String(10))
    status = db.Column(db.String(50), default='Draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
