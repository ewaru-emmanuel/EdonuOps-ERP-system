# CRM routes for EdonuOps ERP
from flask import Blueprint, jsonify, request
from app import db
from modules.crm.models import Contact, Lead, Opportunity
from datetime import datetime

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts from database"""
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

@crm_bp.route('/leads', methods=['GET'])
def get_leads():
    """Get all leads from database"""
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

@crm_bp.route('/opportunities', methods=['GET'])
def get_opportunities():
    """Get all opportunities from database"""
    try:
        opportunities = Opportunity.query.all()
        return jsonify([{
            "id": opp.id,
            "name": opp.name,
            "amount": float(opp.amount) if opp.amount else 0.0,
            "stage": opp.stage,
            "contact_id": opp.contact_id,
            "probability": opp.probability,
            "expected_close_date": opp.expected_close_date.isoformat() if opp.expected_close_date else None,
            "created_at": opp.created_at.isoformat() if opp.created_at else None
        } for opp in opportunities]), 200
    except Exception as e:
        print(f"Error fetching opportunities: {e}")
        return jsonify({"error": "Failed to fetch opportunities"}), 500

@crm_bp.route('/contacts', methods=['POST'])
def create_contact():
    """Create a new contact in database"""
    try:
        data = request.get_json()
        new_contact = Contact(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            company=data.get('company'),
            type=data.get('type', 'customer'),
            status=data.get('status', 'active')
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({
            "message": "Contact created successfully",
            "id": new_contact.id,
            "contact": {
                "id": new_contact.id,
                "first_name": new_contact.first_name,
                "last_name": new_contact.last_name,
                "email": new_contact.email,
                "phone": new_contact.phone,
                "company": new_contact.company,
                "type": new_contact.type,
                "status": new_contact.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating contact: {e}")
        return jsonify({"error": "Failed to create contact"}), 500

@crm_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update a contact in database"""
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
            "message": "Contact updated successfully",
            "contact": {
                "id": contact.id,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "type": contact.type,
                "status": contact.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating contact: {e}")
        return jsonify({"error": "Failed to update contact"}), 500

@crm_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact from database"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"message": "Contact deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting contact: {e}")
        return jsonify({"error": "Failed to delete contact"}), 500

@crm_bp.route('/leads', methods=['POST'])
def create_lead():
    """Create a new lead in database"""
    try:
        data = request.get_json()
        new_lead = Lead(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            company=data.get('company'),
            source=data.get('source', 'website'),
            status=data.get('status', 'new')
        )
        db.session.add(new_lead)
        db.session.commit()
        return jsonify({
            "message": "Lead created successfully",
            "id": new_lead.id,
            "lead": {
                "id": new_lead.id,
                "first_name": new_lead.first_name,
                "last_name": new_lead.last_name,
                "email": new_lead.email,
                "phone": new_lead.phone,
                "company": new_lead.company,
                "source": new_lead.source,
                "status": new_lead.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating lead: {e}")
        return jsonify({"error": "Failed to create lead"}), 500

@crm_bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update a lead in database"""
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
            "message": "Lead updated successfully",
            "lead": {
                "id": lead.id,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "email": lead.email,
                "phone": lead.phone,
                "company": lead.company,
                "source": lead.source,
                "status": lead.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating lead: {e}")
        return jsonify({"error": "Failed to update lead"}), 500

@crm_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Delete a lead from database"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        db.session.delete(lead)
        db.session.commit()
        return jsonify({"message": "Lead deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting lead: {e}")
        return jsonify({"error": "Failed to delete lead"}), 500

@crm_bp.route('/opportunities', methods=['POST'])
def create_opportunity():
    """Create a new opportunity in database"""
    try:
        data = request.get_json()
        new_opportunity = Opportunity(
            name=data.get('name'),
            amount=data.get('amount', 0),
            stage=data.get('stage', 'prospecting'),
            contact_id=data.get('contact_id'),
            probability=data.get('probability', 50),
            expected_close_date=datetime.fromisoformat(data.get('expected_close_date')) if data.get('expected_close_date') else None
        )
        db.session.add(new_opportunity)
        db.session.commit()
        return jsonify({
            "message": "Opportunity created successfully",
            "id": new_opportunity.id,
            "opportunity": {
                "id": new_opportunity.id,
                "name": new_opportunity.name,
                "amount": float(new_opportunity.amount) if new_opportunity.amount else 0.0,
                "stage": new_opportunity.stage,
                "contact_id": new_opportunity.contact_id,
                "probability": new_opportunity.probability,
                "expected_close_date": new_opportunity.expected_close_date.isoformat() if new_opportunity.expected_close_date else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating opportunity: {e}")
        return jsonify({"error": "Failed to create opportunity"}), 500

@crm_bp.route('/opportunities/<int:opportunity_id>', methods=['PUT'])
def update_opportunity(opportunity_id):
    """Update an opportunity in database"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        data = request.get_json()
        
        opportunity.name = data.get('name', opportunity.name)
        opportunity.amount = data.get('amount', opportunity.amount)
        opportunity.stage = data.get('stage', opportunity.stage)
        opportunity.contact_id = data.get('contact_id', opportunity.contact_id)
        opportunity.probability = data.get('probability', opportunity.probability)
        opportunity.expected_close_date = datetime.fromisoformat(data.get('expected_close_date')) if data.get('expected_close_date') else opportunity.expected_close_date
        
        db.session.commit()
        return jsonify({
            "message": "Opportunity updated successfully",
            "opportunity": {
                "id": opportunity.id,
                "name": opportunity.name,
                "amount": float(opportunity.amount) if opportunity.amount else 0.0,
                "stage": opportunity.stage,
                "contact_id": opportunity.contact_id,
                "probability": opportunity.probability,
                "expected_close_date": opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating opportunity: {e}")
        return jsonify({"error": "Failed to update opportunity"}), 500

@crm_bp.route('/opportunities/<int:opportunity_id>', methods=['DELETE'])
def delete_opportunity(opportunity_id):
    """Delete an opportunity from database"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        db.session.delete(opportunity)
        db.session.commit()
        return jsonify({"message": "Opportunity deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting opportunity: {e}")
        return jsonify({"error": "Failed to delete opportunity"}), 500
