# backend/modules/reporting/models.py

from app import db

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(100), nullable=False)
    report_type = db.Column(db.String(50))
    generated_at = db.Column(db.DateTime, server_default=db.func.now())
    parameters = db.Column(db.JSON)