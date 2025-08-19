from flask import Blueprint, jsonify, request
from app import db
from modules.crm.models import Contact, Lead, Opportunity, Communication, FollowUp, CRMUser, LeadIntake
from datetime import datetime

bp = Blueprint('crm', __name__, url_prefix='/api/crm')

# Contact endpoints
@bp.route('/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts"""
    try:
        contacts = Contact.query.all()
        return jsonify([{
            "id": contact.id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "type": contact.type,
            "status": contact.status,
            "created_at": contact.created_at.isoformat() if contact.created_at else None
        } for contact in contacts]), 200
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return jsonify({"error": "Failed to fetch contacts"}), 500

@bp.route('/contacts', methods=['POST'])
def create_contact():
    """Create a new contact"""
    try:
        data = request.get_json()
        
        contact = Contact(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            company=data.get('company'),
            type=data.get('type', 'customer'),
            status=data.get('status', 'active')
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            "id": contact.id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "type": contact.type,
            "status": contact.status,
            "created_at": contact.created_at.isoformat() if contact.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating contact: {e}")
        return jsonify({"error": "Failed to create contact"}), 500

@bp.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update a contact"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        data = request.get_json()
        
        contact.first_name = data.get('first_name', contact.first_name)
        contact.last_name = data.get('last_name', contact.last_name)
        contact.email = data.get('email', contact.email)
        contact.phone = data.get('phone', contact.phone)
        contact.company = data.get('company', contact.company)
        contact.type = data.get('type', contact.type)
        contact.status = data.get('status', contact.status)
        
        db.session.commit()
        
        return jsonify({
            "id": contact.id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "type": contact.type,
            "status": contact.status,
            "created_at": contact.created_at.isoformat() if contact.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating contact: {e}")
        return jsonify({"error": "Failed to update contact"}), 500

@bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        
        return jsonify({"message": "Contact deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting contact: {e}")
        return jsonify({"error": "Failed to delete contact"}), 500

# Lead endpoints
@bp.route('/leads', methods=['GET'])
def get_leads():
    """Get all leads"""
    try:
        leads = Lead.query.all()
        return jsonify([{
            "id": lead.id,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "source": lead.source,
            "status": lead.status,
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        } for lead in leads]), 200
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return jsonify({"error": "Failed to fetch leads"}), 500

@bp.route('/leads', methods=['POST'])
def create_lead():
    """Create a new lead"""
    try:
        data = request.get_json()
        
        lead = Lead(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            company=data.get('company'),
            source=data.get('source', 'website'),
            status=data.get('status', 'new')
        )
        
        db.session.add(lead)
        db.session.commit()
        
        return jsonify({
            "id": lead.id,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "source": lead.source,
            "status": lead.status,
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating lead: {e}")
        return jsonify({"error": "Failed to create lead"}), 500

@bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update a lead"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        data = request.get_json()
        
        lead.first_name = data.get('first_name', lead.first_name)
        lead.last_name = data.get('last_name', lead.last_name)
        lead.email = data.get('email', lead.email)
        lead.phone = data.get('phone', lead.phone)
        lead.company = data.get('company', lead.company)
        lead.source = data.get('source', lead.source)
        lead.status = data.get('status', lead.status)
        
        db.session.commit()
        
        return jsonify({
            "id": lead.id,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "source": lead.source,
            "status": lead.status,
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating lead: {e}")
        return jsonify({"error": "Failed to update lead"}), 500

@bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Delete a lead"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        db.session.delete(lead)
        db.session.commit()
        
        return jsonify({"message": "Lead deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting lead: {e}")
        return jsonify({"error": "Failed to delete lead"}), 500

# Opportunity endpoints
@bp.route('/opportunities', methods=['GET'])
def get_opportunities():
    """Get all opportunities"""
    try:
        opportunities = Opportunity.query.all()
        return jsonify([{
            "id": opp.id,
            "name": opp.name,
            "contact_id": opp.contact_id,
            "amount": opp.amount,
            "stage": opp.stage,
            "probability": opp.probability,
            "expected_close_date": opp.expected_close_date.isoformat() if opp.expected_close_date else None,
            "created_at": opp.created_at.isoformat() if opp.created_at else None
        } for opp in opportunities]), 200
    except Exception as e:
        print(f"Error fetching opportunities: {e}")
        return jsonify({"error": "Failed to fetch opportunities"}), 500

@bp.route('/opportunities', methods=['POST'])
def create_opportunity():
    """Create a new opportunity"""
    try:
        data = request.get_json()
        
        opportunity = Opportunity(
            name=data['name'],
            contact_id=data.get('contact_id'),
            amount=data.get('amount', 0.0),
            stage=data.get('stage', 'prospecting'),
            probability=data.get('probability', 0.0),
            expected_close_date=datetime.fromisoformat(data['expected_close_date']) if data.get('expected_close_date') else None
        )
        
        db.session.add(opportunity)
        db.session.commit()
        
        return jsonify({
            "id": opportunity.id,
            "name": opportunity.name,
            "contact_id": opportunity.contact_id,
            "amount": opportunity.amount,
            "stage": opportunity.stage,
            "probability": opportunity.probability,
            "expected_close_date": opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None,
            "created_at": opportunity.created_at.isoformat() if opportunity.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating opportunity: {e}")
        return jsonify({"error": "Failed to create opportunity"}), 500

@bp.route('/opportunities/<int:opportunity_id>', methods=['PUT'])
def update_opportunity(opportunity_id):
    """Update an opportunity"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        data = request.get_json()
        
        opportunity.name = data.get('name', opportunity.name)
        opportunity.contact_id = data.get('contact_id', opportunity.contact_id)
        opportunity.amount = data.get('amount', opportunity.amount)
        opportunity.stage = data.get('stage', opportunity.stage)
        opportunity.probability = data.get('probability', opportunity.probability)
        if data.get('expected_close_date'):
            opportunity.expected_close_date = datetime.fromisoformat(data['expected_close_date'])
        
        db.session.commit()
        
        return jsonify({
            "id": opportunity.id,
            "name": opportunity.name,
            "contact_id": opportunity.contact_id,
            "amount": opportunity.amount,
            "stage": opportunity.stage,
            "probability": opportunity.probability,
            "expected_close_date": opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None,
            "created_at": opportunity.created_at.isoformat() if opportunity.created_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating opportunity: {e}")
        return jsonify({"error": "Failed to update opportunity"}), 500

@bp.route('/opportunities/<int:opportunity_id>', methods=['DELETE'])
def delete_opportunity(opportunity_id):
    """Delete an opportunity"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        db.session.delete(opportunity)
        db.session.commit()
        
        return jsonify({"message": "Opportunity deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting opportunity: {e}")
        return jsonify({"error": "Failed to delete opportunity"}), 500
