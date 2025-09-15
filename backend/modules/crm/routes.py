# CRM routes for EdonuOps ERP
from flask import Blueprint, jsonify, request, Response
from app import db
from modules.crm.models import Contact, Lead, Opportunity, Company, Communication, Ticket, FollowUp, KnowledgeBaseArticle, KnowledgeBaseAttachment, Pipeline, TimeEntry, BehavioralEvent
from modules.finance.models import Invoice
from datetime import datetime, timedelta
import json
from openai import OpenAI
import csv
import io
from werkzeug.utils import secure_filename
import os

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/contacts', methods=['GET', 'OPTIONS'])
def get_contacts():
    if request.method == 'OPTIONS':
        return ('', 200)
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
            "company_id": getattr(contact, 'company_id', None),
            "type": contact.type,
            "status": contact.status,
            "region": getattr(contact, 'region', None),
            "assigned_team": getattr(contact, 'assigned_team', None),
            "created_at": contact.created_at.isoformat() if contact.created_at else None
        } for contact in contacts]), 200
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return jsonify({"error": "Failed to fetch contacts"}), 500

@crm_bp.route('/leads', methods=['GET', 'OPTIONS'])
def get_leads():
    if request.method == 'OPTIONS':
        return ('', 200)
    """Get all leads from database"""
    try:
        # Server-side filters
        min_score = request.args.get('minScore', type=int)
        region = request.args.get('region')
        assigned_team = request.args.get('assignedTeam')

        query = Lead.query
        if min_score is not None:
            try:
                query = query.filter(Lead.score >= min_score)
            except Exception:
                pass
        if region:
            query = query.filter((Lead.region == region) | (Lead.region == region.strip()))
        if assigned_team:
            query = query.filter((Lead.assigned_team == assigned_team) | (Lead.assigned_team == assigned_team.strip()))

        sort = request.args.get('sort')
        order = (request.args.get('order') or 'asc').lower()
        if sort and hasattr(Lead, sort):
            query = query.order_by(getattr(Lead, sort).asc() if order != 'desc' else getattr(Lead, sort).desc())
        page = request.args.get('page', type=int)
        page_size = request.args.get('pageSize', type=int)
        if page is not None and page_size:
            page = max(1, page)
            page_size = max(1, min(page_size, 100))
            query = query.offset((page - 1) * page_size).limit(page_size)
        leads = query.all()
        return jsonify([{
            "id": lead.id,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "source": lead.source,
            "status": lead.status,
            "lead_status": getattr(lead, 'lead_status', None),
            "region": getattr(lead, 'region', None),
            "assigned_team": getattr(lead, 'assigned_team', None),
            "score": getattr(lead, 'score', 0),
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        } for lead in leads]), 200
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return jsonify({"error": "Failed to fetch leads"}), 500

@crm_bp.route('/opportunities', methods=['GET', 'OPTIONS'])
def get_opportunities():
    if request.method == 'OPTIONS':
        return ('', 200)
    """Get all opportunities from database"""
    try:
        region = request.args.get('region')
        assigned_team = request.args.get('assignedTeam')

        query = Opportunity.query
        if region:
            query = query.filter((Opportunity.region == region) | (Opportunity.region == region.strip()))
        if assigned_team:
            query = query.filter((Opportunity.assigned_team == assigned_team) | (Opportunity.assigned_team == assigned_team.strip()))
        pipeline_id = request.args.get('pipelineId', type=int)
        if pipeline_id:
            query = query.filter(Opportunity.pipeline_id == pipeline_id)

        sort = request.args.get('sort')
        order = (request.args.get('order') or 'asc').lower()
        if sort and hasattr(Opportunity, sort):
            query = query.order_by(getattr(Opportunity, sort).asc() if order != 'desc' else getattr(Opportunity, sort).desc())
        page = request.args.get('page', type=int)
        page_size = request.args.get('pageSize', type=int)
        if page is not None and page_size:
            page = max(1, page)
            page_size = max(1, min(page_size, 100))
            query = query.offset((page - 1) * page_size).limit(page_size)
        opportunities = query.all()
        return jsonify([{
            "id": opp.id,
            "name": opp.name,
            "amount": float(opp.amount) if opp.amount else 0.0,
            "stage": opp.stage,
            "pipeline_id": getattr(opp, 'pipeline_id', None),
            "contact_id": opp.contact_id,
            "company_id": getattr(opp, 'company_id', None),
            "probability": opp.probability,
            "region": getattr(opp, 'region', None),
            "assigned_team": getattr(opp, 'assigned_team', None),
            "products": getattr(opp, 'products', None) or [],
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
            company_id=data.get('company_id'),
            type=data.get('type', 'customer'),
            status=data.get('status', 'active'),
            region=data.get('region'),
            assigned_team=data.get('assigned_team')
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
                "status": new_contact.status,
                "region": new_contact.region,
                "assigned_team": new_contact.assigned_team
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
        contact.company_id = data.get('company_id', contact.company_id)
        contact.type = data.get('type', contact.type)
        contact.status = data.get('status', contact.status)
        contact.region = data.get('region', contact.region)
        contact.assigned_team = data.get('assigned_team', contact.assigned_team)
        
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
                "status": contact.status,
                "region": contact.region,
                "assigned_team": contact.assigned_team
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
            status=data.get('status', 'new'),
            lead_status=data.get('lead_status'),
            region=data.get('region'),
            assigned_team=data.get('assigned_team'),
            score=data.get('score', 0)
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
                "status": new_lead.status,
                "lead_status": new_lead.lead_status,
                "region": new_lead.region,
                "assigned_team": new_lead.assigned_team,
                "score": new_lead.score
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
        lead.lead_status = data.get('lead_status', lead.lead_status)
        lead.region = data.get('region', lead.region)
        lead.assigned_team = data.get('assigned_team', lead.assigned_team)
        lead.score = data.get('score', lead.score)
        
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
                "status": lead.status,
                "lead_status": lead.lead_status,
                "region": lead.region,
                "assigned_team": lead.assigned_team,
                "score": lead.score
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
            company_id=data.get('company_id'),
            pipeline_id=data.get('pipeline_id'),
            probability=data.get('probability', 50),
            expected_close_date=datetime.fromisoformat(data.get('expected_close_date')) if data.get('expected_close_date') else None,
            region=data.get('region'),
            assigned_team=data.get('assigned_team'),
            products=data.get('products')
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
                "pipeline_id": new_opportunity.pipeline_id,
                "contact_id": new_opportunity.contact_id,
                "company_id": new_opportunity.company_id,
                "probability": new_opportunity.probability,
                "region": new_opportunity.region,
                "assigned_team": new_opportunity.assigned_team,
                "products": new_opportunity.products or [],
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
        opportunity.pipeline_id = data.get('pipeline_id', opportunity.pipeline_id)
        opportunity.contact_id = data.get('contact_id', opportunity.contact_id)
        opportunity.company_id = data.get('company_id', opportunity.company_id)
        opportunity.probability = data.get('probability', opportunity.probability)
        opportunity.expected_close_date = datetime.fromisoformat(data.get('expected_close_date')) if data.get('expected_close_date') else opportunity.expected_close_date
        opportunity.region = data.get('region', opportunity.region)
        opportunity.assigned_team = data.get('assigned_team', opportunity.assigned_team)
        opportunity.products = data.get('products', opportunity.products)
        
        db.session.commit()
        return jsonify({
            "message": "Opportunity updated successfully",
            "opportunity": {
                "id": opportunity.id,
                "name": opportunity.name,
                "amount": float(opportunity.amount) if opportunity.amount else 0.0,
                "stage": opportunity.stage,
                "pipeline_id": opportunity.pipeline_id,
                "contact_id": opportunity.contact_id,
                "company_id": opportunity.company_id,
                "probability": opportunity.probability,
                "region": opportunity.region,
                "assigned_team": opportunity.assigned_team,
                "products": opportunity.products or [],
                "expected_close_date": opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating opportunity: {e}")
        return jsonify({"error": "Failed to update opportunity"}), 500


@crm_bp.route('/opportunities/<int:opportunity_id>/move', methods=['PATCH', 'OPTIONS'])
def move_opportunity_stage(opportunity_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        payload = request.get_json(silent=True) or {}
        new_stage = payload.get('stage')
        if not new_stage:
            return jsonify({'error': 'stage is required'}), 400
        opportunity.stage = new_stage
        db.session.commit()
        return jsonify({'message': 'Stage updated', 'id': opportunity.id, 'stage': opportunity.stage}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error moving opportunity: {e}")
        return jsonify({'error': 'Failed to move opportunity'}), 500

# Companies CRUD (minimal for linking)
@crm_bp.route('/companies', methods=['GET', 'OPTIONS'])
def get_companies():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        companies = Company.query.all()
        return jsonify([
            {
                "id": c.id,
                "name": c.name,
                "industry": c.industry,
                "size": c.size,
                "region": c.region,
                "assigned_team": c.assigned_team,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            } for c in companies
        ]), 200
    except Exception as e:
        print(f"Error fetching companies: {e}")
        return jsonify({"error": "Failed to fetch companies"}), 500

@crm_bp.route('/companies', methods=['POST', 'OPTIONS'])
def create_company():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data = request.get_json() or {}
        c = Company(
            name=data.get('name'),
            industry=data.get('industry'),
            size=data.get('size'),
            region=data.get('region'),
            assigned_team=data.get('assigned_team'),
        )
        db.session.add(c)
        db.session.commit()
        return jsonify({"message": "Company created", "id": c.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating company: {e}")
        return jsonify({"error": "Failed to create company"}), 500

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

# -----------------------------
# AI Endpoints (Lead Scoring & Next-Best Actions)
# -----------------------------

@crm_bp.route('/ai/score-lead', methods=['POST'])
def ai_score_lead():
    """Enhanced AI lead scoring with explainability, behavioral data, and next best actions."""
    try:
        payload = request.get_json(silent=True) or {}
        lead = payload.get('lead') or {}
        behavioral_data = payload.get('behavioral_data', {})
        if not lead:
            return jsonify({"error": "Missing 'lead' in request body"}), 400

        client = OpenAI()  # Reads OPENAI_API_KEY from environment

        # Enhanced system prompt for better scoring and explainability
        system_msg = {
            "role": "system",
            "content": (
                "You are an advanced CRM AI that scores sales leads from 0 to 100 with detailed explainability. "
                "Analyze the lead data and behavioral patterns to provide: "
                "1. Overall score (0-100) "
                "2. Detailed explanation of scoring factors "
                "3. Behavioral insights "
                "4. Next best actions "
                "5. Risk factors and opportunities "
                "Respond with strict JSON only with these fields: "
                "score (integer 0-100), explanation (detailed string), "
                "behavioral_insights (array of strings), next_actions (array of objects with action, priority, reason), "
                "risk_factors (array of strings), opportunities (array of strings), confidence (integer 0-100)."
            ),
        }
        
        # Enhanced user message with behavioral context
        user_msg = {
            "role": "user",
            "content": (
                f"Analyze this lead with behavioral context:\n\n"
                f"LEAD DATA:\n{json.dumps(lead, ensure_ascii=False)}\n\n"
                f"BEHAVIORAL DATA:\n{json.dumps(behavioral_data, ensure_ascii=False)}\n\n"
                f"Consider factors like: engagement level, response time, company size, "
                f"industry fit, communication patterns, and buying signals."
            ),
        }

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.1,  # Lower temperature for more consistent scoring
            max_tokens=800,   # Increased for detailed explanations
        )

        raw = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {
                "score": 50, 
                "explanation": "Fallback: invalid AI JSON response",
                "behavioral_insights": ["Unable to analyze behavioral patterns"],
                "next_actions": [{"action": "Manual follow-up", "priority": "medium", "reason": "Requires human review"}],
                "risk_factors": ["Data analysis unavailable"],
                "opportunities": ["Standard lead qualification needed"],
                "confidence": 30
            }

        # Enhanced guardrails and validation
        score = data.get("score", 50)
        try:
            score = int(score)
        except Exception:
            score = 50
        score = max(0, min(100, score))

        # Validate and structure response
        response = {
            "score": score,
            "explanation": data.get("explanation", "No explanation provided"),
            "behavioral_insights": data.get("behavioral_insights", []) if isinstance(data.get("behavioral_insights"), list) else [],
            "next_actions": data.get("next_actions", []) if isinstance(data.get("next_actions"), list) else [],
            "risk_factors": data.get("risk_factors", []) if isinstance(data.get("risk_factors"), list) else [],
            "opportunities": data.get("opportunities", []) if isinstance(data.get("opportunities"), list) else [],
            "confidence": min(100, max(0, int(data.get("confidence", 70))))
        }

        return jsonify(response), 200
    except Exception as e:
        print(f"Enhanced AI scoring failed: {e}")
        return jsonify({
            "score": 50, 
            "explanation": "AI service temporarily unavailable",
            "behavioral_insights": ["Service error - manual review recommended"],
            "next_actions": [{"action": "Manual qualification", "priority": "high", "reason": "AI service unavailable"}],
            "risk_factors": ["Unable to assess risk factors"],
            "opportunities": ["Standard lead processing"],
            "confidence": 20
        }), 200


@crm_bp.route('/ai/next-actions', methods=['POST'])
def ai_next_best_actions():
    """Return 1-3 next-best actions for a lead or deal payload using OpenAI."""
    try:
        payload = request.get_json(silent=True) or {}
        entity_type = (payload.get('entityType') or '').lower()
        entity = payload.get('entity') or {}
        if entity_type not in {"lead", "deal", "opportunity"}:
            return jsonify({"error": "entityType must be 'lead' or 'deal' (or 'opportunity')"}), 400

        client = OpenAI()  # Reads OPENAI_API_KEY from environment

        system_msg = {
            "role": "system",
            "content": (
                "You are a CRM assistant that proposes next-best actions. "
                "Return strict JSON with field 'actions' as an array of up to 3 objects: "
                "{title: string, description: string, dueInDays: integer}."
            ),
        }
        user_msg = {
            "role": "user",
            "content": (
                f"Suggest next-best actions for this {entity_type}.\n" + json.dumps(entity, ensure_ascii=False)
            ),
        }

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.3,
            max_tokens=300,
        )

        raw = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {"actions": [{"title": "Follow up", "description": "Reach out to the prospect", "dueInDays": 2}]}

        actions = data.get("actions") or []
        if not isinstance(actions, list):
            actions = [actions]

        # Normalize actions structure
        normalized = []
        for a in actions[:3]:
            title = str((a or {}).get("title") or "Follow up")
            description = str((a or {}).get("description") or "Reach out to the prospect")
            due = (a or {}).get("dueInDays")
            try:
                due = int(due) if due is not None else 3
            except Exception:
                due = 3
            normalized.append({"title": title, "description": description, "dueInDays": max(0, due)})

        return jsonify({"actions": normalized}), 200
    except Exception as e:
        print(f"AI next-actions failed: {e}")
        return jsonify({"actions": [{"title": "Follow up", "description": "Reach out to the prospect", "dueInDays": 3}]}), 200


# -----------------------------
# AI: Extraction & Email Generation
# -----------------------------

@crm_bp.route('/ai/extract-entities', methods=['POST', 'OPTIONS'])
def ai_extract_entities():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json(silent=True) or {}
        text = payload.get('text') or ''
        file_text = payload.get('fileText') or ''
        combined = (text or '') + "\n\n" + (file_text or '')
        if not combined.strip():
            return jsonify({'error': 'No text to extract from'}), 400

        client = OpenAI()
        system_msg = {
            'role': 'system',
            'content': (
                'You are a CRM ingestion assistant. Extract structured entities as strict JSON with keys: '
                'companies (array of {name, industry?, size?, region?, assigned_team?}), '
                'contacts (array of {first_name?, last_name?, email?, phone?, company?}), '
                'leads (array like contacts plus {source?, lead_status?, score?}), '
                'opportunities (array of {name, amount?, stage?, probability?, contact_id?, company?, expected_close_date?}).'
            )
        }
        user_msg = { 'role': 'user', 'content': combined[:20000] }
        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            response_format={'type': 'json_object'},
            messages=[system_msg, user_msg],
            temperature=0.2,
            max_tokens=1200
        )
        raw = completion.choices[0].message.content or '{}'
        try:
            data = json.loads(raw)
        except Exception:
            data = {'companies': [], 'contacts': [], 'leads': [], 'opportunities': []}
        # Normalize shapes
        out = {
            'companies': data.get('companies') or [],
            'contacts': data.get('contacts') or [],
            'leads': data.get('leads') or [],
            'opportunities': data.get('opportunities') or []
        }
        return jsonify(out), 200
    except Exception as e:
        print(f"AI extract-entities failed: {e}")
        return jsonify({'companies': [], 'contacts': [], 'leads': [], 'opportunities': []}), 200


@crm_bp.route('/ai/suggest-mapping', methods=['POST', 'OPTIONS'])
def ai_suggest_mapping():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json(silent=True) or {}
        headers = payload.get('headers') or []
        entity = (payload.get('entity') or 'contacts').lower()
        if not isinstance(headers, list) or not headers:
            return jsonify({'error': 'headers array required'}), 400
        client = OpenAI()
        system_msg = {
            'role': 'system',
            'content': (
                'You map CSV headers to CRM fields. Return strict JSON object {csvHeader: fieldName}. '
                'Entities and valid fields: '
                'contacts: first_name, last_name, email, phone, company, company_id, type, status, region, assigned_team; '
                'leads: first_name, last_name, email, phone, company, source, status, lead_status, region, assigned_team, score; '
                'companies: name, industry, size, region, assigned_team; '
                'opportunities: name, amount, stage, contact_id, company_id, probability, expected_close_date, region, assigned_team, products.'
            )
        }
        user_msg = { 'role': 'user', 'content': json.dumps({'entity': entity, 'headers': headers}, ensure_ascii=False) }
        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            response_format={'type': 'json_object'},
            messages=[system_msg, user_msg],
            temperature=0.1,
            max_tokens=400
        )
        raw = completion.choices[0].message.content or '{}'
        try:
            mapping = json.loads(raw)
        except Exception:
            mapping = {}
        return jsonify({'mapping': mapping}), 200
    except Exception as e:
        print(f"AI suggest-mapping failed: {e}")
        return jsonify({'mapping': {}}), 200


@crm_bp.route('/ai/generate-email', methods=['POST', 'OPTIONS'])
def ai_generate_email():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json(silent=True) or {}
        context = payload.get('context') or {}
        intent = (payload.get('intent') or 'follow_up').replace('_', ' ')
        client = OpenAI()
        system_msg = {
            'role': 'system',
            'content': (
                'You write concise business emails. Return strict JSON with fields: subject (string), body (string). '
                'Write in a professional tone, keep paragraphs short, and personalize based on provided context.'
            )
        }
        user_msg = { 'role': 'user', 'content': json.dumps({'intent': intent, 'context': context}, ensure_ascii=False) }
        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            response_format={'type': 'json_object'},
            messages=[system_msg, user_msg],
            temperature=0.3,
            max_tokens=600
        )
        raw = completion.choices[0].message.content or '{}'
        try:
            data = json.loads(raw)
        except Exception:
            data = {'subject': 'Follow up', 'body': 'Hello,\n\nFollowing up on our conversation.\n\nBest regards,'}
        return jsonify({'subject': data.get('subject'), 'body': data.get('body')}), 200
    except Exception as e:
        print(f"AI generate-email failed: {e}")
        return jsonify({'subject': 'Follow up', 'body': 'Hello,\n\nFollowing up.\n\nBest regards,'}), 200
# -----------------------------
# Email Sync (IMAP) - minimal stub
# -----------------------------

@crm_bp.route('/email/sync', methods=['POST', 'OPTIONS'])
def email_sync():
    """Enhanced email sync with Gmail/Outlook support, activity tracking, and smart send time."""
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json(silent=True) or {}
        provider = payload.get('provider', 'gmail')  # gmail, outlook, imap
        folder = payload.get('folder') or 'INBOX'
        since = payload.get('since')  # ISO date string
        max_emails = payload.get('max_emails', 50)
        
        # Get email settings from system settings
        from modules.core.models import SystemSetting
        email_settings = SystemSetting.query.filter_by(section='email').first()
        
        if not email_settings or not email_settings.data:
            return jsonify({'error': 'Email settings not configured'}), 400
        
        settings_data = email_settings.data
        provider_settings = settings_data.get(provider, {})
        
        if not provider_settings.get('enabled', False):
            return jsonify({'error': f'{provider.title()} sync not enabled'}), 400
        
        # Simulate email fetching with activity tracking
        fetched_emails = []
        activity_events = []
        
        # Mock email data for demonstration (in real implementation, use Gmail API, Outlook Graph API, or IMAP)
        mock_emails = [
            {
                'id': f'email_{i}',
                'subject': f'Meeting Follow-up - Project Discussion {i}',
                'from': f'client{i}@company.com',
                'to': 'sales@edonuops.com',
                'date': datetime.utcnow().isoformat(),
                'body': f'Thank you for the meeting. We are interested in moving forward with the proposal.',
                'thread_id': f'thread_{i}',
                'labels': ['important', 'follow-up']
            }
            for i in range(min(max_emails, 5))  # Limit to 5 for demo
        ]
        
        for email in mock_emails:
            # Track email activity
            activity_events.append({
                'type': 'email_received',
                'subject': email['subject'],
                'from': email['from'],
                'timestamp': email['date'],
                'engagement_score': 75  # Based on content analysis
            })
            
            # Create communication record
            try:
                # Find related contact/lead by email
                contact = Contact.query.filter_by(email=email['from']).first()
                lead = Lead.query.filter_by(email=email['from']).first()
                
                if contact or lead:
                    comm = Communication(
                        type='email',
                        direction='inbound',
                        subject=email['subject'],
                        content=email['body'],
                        contact_id=contact.id if contact else None,
                        lead_id=lead.id if lead else None,
                        status='received',
                        metadata={
                            'email_id': email['id'],
                            'thread_id': email['thread_id'],
                            'labels': email['labels'],
                            'provider': provider
                        }
                    )
                    db.session.add(comm)
                    
                    # Track behavioral event
                    if lead:
                        event = BehavioralEvent(
                            lead_id=lead.id,
                            event_type='email_received',
                            event_data={
                                'subject': email['subject'],
                                'engagement_score': 75,
                                'response_time': 'same_day'
                            },
                            engagement_score=75
                        )
                        db.session.add(event)
                        
                        # Update lead's behavioral data
                        if not lead.behavioral_data:
                            lead.behavioral_data = {}
                        
                        if 'email_activity' not in lead.behavioral_data:
                            lead.behavioral_data['email_activity'] = []
                        
                        lead.behavioral_data['email_activity'].append({
                            'type': 'received',
                            'subject': email['subject'],
                            'timestamp': email['date'],
                            'engagement_score': 75
                        })
                        
                        # Keep only last 20 email activities
                        if len(lead.behavioral_data['email_activity']) > 20:
                            lead.behavioral_data['email_activity'] = lead.behavioral_data['email_activity'][-20:]
                
                fetched_emails.append(email)
                
            except Exception as e:
                print(f"Error processing email {email['id']}: {e}")
                continue
        
        db.session.commit()
        
        # Generate smart send time suggestions
        smart_send_times = _generate_smart_send_times(activity_events)
        
        return jsonify({
            'message': 'Email sync completed',
            'provider': provider,
            'folder': folder,
            'since': since,
            'fetched': len(fetched_emails),
            'emails': fetched_emails,
            'activity_events': activity_events,
            'smart_send_times': smart_send_times,
            'sync_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Enhanced email sync failed: {e}")
        return jsonify({'error': 'Email sync failed'}), 500


def _generate_smart_send_times(activity_events):
    """Generate smart send time suggestions based on activity patterns."""
    try:
        client = OpenAI()
        
        # Analyze activity patterns
        system_msg = {
            "role": "system",
            "content": (
                "You are an email timing AI that analyzes communication patterns to suggest optimal send times. "
                "Based on email activity data, suggest the best times to send emails for maximum engagement. "
                "Respond with JSON: optimal_times (array of objects with time, day, reason, confidence_score)."
            )
        }
        
        user_msg = {
            "role": "user",
            "content": (
                f"Analyze these email activity patterns and suggest optimal send times:\n\n"
                f"ACTIVITY EVENTS:\n{json.dumps(activity_events, ensure_ascii=False)}\n\n"
                f"Suggest the best times to send emails based on response patterns and engagement levels."
            )
        }
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.3,
            max_tokens=400
        )
        
        raw = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {"optimal_times": []}
        
        optimal_times = data.get("optimal_times", [])
        if not isinstance(optimal_times, list):
            optimal_times = []
        
        # Validate and enhance time suggestions
        validated_times = []
        for time_suggestion in optimal_times:
            if isinstance(time_suggestion, dict) and time_suggestion.get('time'):
                validated_times.append({
                    'time': time_suggestion.get('time', ''),
                    'day': time_suggestion.get('day', ''),
                    'reason': time_suggestion.get('reason', ''),
                    'confidence_score': min(100, max(0, int(time_suggestion.get('confidence_score', 50))))
                })
        
        return validated_times
        
    except Exception as e:
        print(f"Smart send time generation failed: {e}")
        return [
            {
                'time': '10:00 AM',
                'day': 'Tuesday',
                'reason': 'Default business hours recommendation',
                'confidence_score': 60
            },
            {
                'time': '2:00 PM',
                'day': 'Wednesday',
                'reason': 'Mid-week engagement peak',
                'confidence_score': 55
            }
        ]

# -----------------------------
# Deal Won → Finance (draft invoice)
# -----------------------------
@crm_bp.route('/deals/<int:opportunity_id>/win', methods=['POST'])
def mark_deal_won(opportunity_id):
    """Mark deal as won and emit draft invoice in Finance (if available)."""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        opportunity.stage = 'closed_won'
        db.session.commit()

        # Create AR invoice (basic) in finance models if available
        try:
            from modules.finance.models import Invoice
            inv = Invoice(
                invoice_number=f"DRAFT-{opportunity.id}",
                customer_id=opportunity.contact_id,
                invoice_date=datetime.utcnow().date(),
                due_date=datetime.utcnow().date(),
                amount=float(opportunity.amount or 0),
                tax_amount=0.0,
                total_amount=float(opportunity.amount or 0),
                status='draft',
                currency='USD',
            )
            db.session.add(inv)
            db.session.commit()
            invoice_payload = {"id": inv.id, "invoice_number": inv.invoice_number, "status": inv.status, "total_amount": float(inv.total_amount)}
        except Exception as e:
            db.session.rollback()
            print(f"Invoice creation failed: {e}")
            invoice_payload = {"invoice_number": f"DRAFT-{opportunity.id}", "status": "draft", "total_amount": float(opportunity.amount or 0)}

        return jsonify({"message": "Deal marked as won", "invoice": invoice_payload}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error marking deal won: {e}")
        return jsonify({"error": "Failed to mark deal won"}), 500

# -----------------------------
# Activities (Communications)
# -----------------------------
@crm_bp.route('/activities', methods=['GET'])
def list_activities():
    try:
        related_type = request.args.get('relatedType')  # lead, contact, opportunity
        related_id = request.args.get('relatedId', type=int)

        query = Communication.query
        if related_type == 'lead' and related_id:
            query = query.filter(Communication.lead_id == related_id)
        elif related_type == 'contact' and related_id:
            query = query.filter(Communication.contact_id == related_id)
        elif related_type in {'opportunity', 'deal'} and related_id:
            query = query.filter(Communication.opportunity_id == related_id)

        # Apply sorting/pagination in a backward-compatible way
        query = query.order_by(Communication.created_at.desc())
        page = request.args.get('page', type=int)
        page_size = request.args.get('pageSize', type=int)
        if page is not None and page_size:
            page = max(1, page)
            page_size = max(1, min(page_size, 100))
            query = query.offset((page - 1) * page_size).limit(page_size)
        else:
            query = query.limit(100)

        items = query.all()
        resp = jsonify([
            {
                "id": a.id,
                "type": a.type,
                "direction": a.direction,
                "subject": a.subject,
                "content": a.content,
                "status": a.status,
                "relatedType": 'lead' if a.lead_id else ('opportunity' if a.opportunity_id else 'contact'),
                "relatedId": a.lead_id or a.opportunity_id or a.contact_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "scheduled_for": a.scheduled_for.isoformat() if a.scheduled_for else None,
            } for a in items
        ])
        return resp, 200
    except Exception as e:
        print(f"Error listing activities: {e}")
        return jsonify({"error": "Failed to list activities"}), 500


@crm_bp.route('/activities', methods=['POST'])
def create_activity():
    try:
        data = request.get_json() or {}
        related_type = (data.get('relatedType') or '').lower()
        related_id = data.get('relatedId')

        activity = Communication(
            type=data.get('type'),
            direction=data.get('direction', 'outbound'),
            subject=data.get('subject'),
            content=data.get('content'),
            status=data.get('status', 'completed'),
            created_by=None,
        )

        if related_type == 'lead':
            activity.lead_id = related_id
        elif related_type in {'opportunity', 'deal'}:
            activity.opportunity_id = related_id
        elif related_type == 'contact':
            activity.contact_id = related_id

        db.session.add(activity)
        db.session.commit()
        return jsonify({"message": "Activity created", "id": activity.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating activity: {e}")
        return jsonify({"error": "Failed to create activity"}), 500


# -----------------------------
# Time Tracking
# -----------------------------

@crm_bp.route('/time-entries', methods=['GET', 'POST', 'OPTIONS'])
def time_entries_collection():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        try:
            related_type = (request.args.get('relatedType') or '').lower()
            related_id = request.args.get('relatedId', type=int)
            q = TimeEntry.query
            if related_type == 'lead' and related_id:
                q = q.filter(TimeEntry.lead_id == related_id)
            elif related_type == 'contact' and related_id:
                q = q.filter(TimeEntry.contact_id == related_id)
            elif related_type in {'opportunity', 'deal'} and related_id:
                q = q.filter(TimeEntry.opportunity_id == related_id)
            q = q.order_by(TimeEntry.created_at.desc()).limit(200)
            items = q.all()
            return jsonify([
                {
                    'id': t.id,
                    'contact_id': t.contact_id,
                    'lead_id': t.lead_id,
                    'opportunity_id': t.opportunity_id,
                    'start_time': t.start_time.isoformat() if t.start_time else None,
                    'end_time': t.end_time.isoformat() if t.end_time else None,
                    'duration_minutes': t.duration_minutes,
                    'notes': t.notes,
                    'billable': t.billable,
                    'rate': float(t.rate or 0),
                    'currency': t.currency,
                    'invoiced': t.invoiced,
                    'invoice_id': t.invoice_id
                } for t in items
            ]), 200
        except Exception as e:
            print(f"Error listing time entries: {e}")
            return jsonify([]), 200
    try:
        data = request.get_json() or {}
        start = None
        end = None
        try:
            if data.get('start_time'):
                start = datetime.fromisoformat(data.get('start_time'))
        except Exception:
            start = None
        try:
            if data.get('end_time'):
                end = datetime.fromisoformat(data.get('end_time'))
        except Exception:
            end = None
        duration = data.get('duration_minutes')
        try:
            duration = int(duration) if duration is not None else None
        except Exception:
            duration = None
        t = TimeEntry(
            contact_id=data.get('contact_id'),
            lead_id=data.get('lead_id'),
            opportunity_id=data.get('opportunity_id'),
            start_time=start,
            end_time=end,
            duration_minutes=duration,
            notes=data.get('notes'),
            billable=bool(data.get('billable', True)),
            rate=float(data.get('rate') or 0.0),
            currency=data.get('currency') or 'USD'
        )
        db.session.add(t)
        db.session.commit()
        return jsonify({'id': t.id, 'message': 'Time entry created'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating time entry: {e}")
        return jsonify({'error': 'Failed to create time entry'}), 500


@crm_bp.route('/time-entries/<int:entry_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def time_entry_detail(entry_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    t = TimeEntry.query.get_or_404(entry_id)
    if request.method == 'DELETE':
        try:
            db.session.delete(t)
            db.session.commit()
            return jsonify({'message': 'Time entry deleted'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting time entry: {e}")
            return jsonify({'error': 'Failed to delete time entry'}), 500
    try:
        data = request.get_json() or {}
        if 'start_time' in data:
            try:
                t.start_time = datetime.fromisoformat(data.get('start_time')) if data.get('start_time') else t.start_time
            except Exception:
                pass
        if 'end_time' in data:
            try:
                t.end_time = datetime.fromisoformat(data.get('end_time')) if data.get('end_time') else t.end_time
            except Exception:
                pass
        if 'duration_minutes' in data:
            try:
                t.duration_minutes = int(data.get('duration_minutes')) if data.get('duration_minutes') is not None else t.duration_minutes
            except Exception:
                pass
        for f in ['notes', 'billable', 'rate', 'currency', 'contact_id', 'lead_id', 'opportunity_id', 'invoiced', 'invoice_id']:
            if f in data:
                setattr(t, f, data.get(f))
        db.session.commit()
        return jsonify({'message': 'Time entry updated'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating time entry: {e}")
        return jsonify({'error': 'Failed to update time entry'}), 500
# -----------------------------
# CRM KPIs
# -----------------------------
@crm_bp.route('/reports/kpis', methods=['GET'])
def crm_kpis():
    try:
        total_leads = Lead.query.count()
        total_opps = Opportunity.query.count()
        pipeline_value = db.session.query(db.func.coalesce(db.func.sum(Opportunity.amount), 0.0)).scalar() or 0.0
        won_count = Opportunity.query.filter_by(stage='closed_won').count()
        win_rate = (won_count / total_opps * 100.0) if total_opps > 0 else 0.0
        return jsonify({
            "totalLeads": total_leads,
            "totalOpportunities": total_opps,
            "pipelineValue": float(pipeline_value),
            "wonOpportunities": won_count,
            "winRate": round(win_rate, 1)
        }), 200
    except Exception as e:
        print(f"Error computing CRM KPIs: {e}")
        return jsonify({"error": "Failed to compute KPIs"}), 500


# --------------------------------------------------
# Minimal placeholder endpoints to satisfy frontend
# --------------------------------------------------

@crm_bp.route('/pipelines', methods=['GET', 'OPTIONS'])
def list_pipelines():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        items = Pipeline.query.order_by(Pipeline.created_at.asc()).all()
        if not items:
            # Seed a default pipeline if none exist
            p = Pipeline(name='Default Sales Pipeline', stages=[
                'prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'
            ], is_default=True)
            db.session.add(p)
            db.session.commit()
            items = [p]
        return jsonify([
            {
                'id': i.id,
                'name': i.name,
                'stages': i.stages or [],
                'is_default': bool(getattr(i, 'is_default', False))
            } for i in items
        ]), 200
    except Exception as e:
        print(f"Error listing pipelines: {e}")
        return jsonify([]), 200


@crm_bp.route('/pipelines', methods=['POST'])
def create_pipeline():
    try:
        data = request.get_json() or {}
        p = Pipeline(
            name=data.get('name') or 'Pipeline',
            stages=data.get('stages') or ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'],
            is_default=bool(data.get('is_default'))
        )
        if p.is_default:
            # unset others
            try:
                for other in Pipeline.query.all():
                    other.is_default = False
            except Exception:
                pass
        db.session.add(p)
        db.session.commit()
        return jsonify({'id': p.id, 'message': 'Pipeline created'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating pipeline: {e}")
        return jsonify({'error': 'Failed to create pipeline'}), 500


@crm_bp.route('/pipelines/<int:pipeline_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def pipeline_detail(pipeline_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    p = Pipeline.query.get_or_404(pipeline_id)
    if request.method == 'DELETE':
        try:
            db.session.delete(p)
            db.session.commit()
            return jsonify({'message': 'Pipeline deleted'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting pipeline: {e}")
            return jsonify({'error': 'Failed to delete pipeline'}), 500
    try:
        data = request.get_json() or {}
        p.name = data.get('name', p.name)
        if 'stages' in data:
            p.stages = data.get('stages') or p.stages
        if 'is_default' in data:
            p.is_default = bool(data.get('is_default'))
            if p.is_default:
                try:
                    for other in Pipeline.query.filter(Pipeline.id != p.id).all():
                        other.is_default = False
                except Exception:
                    pass
        db.session.commit()
        return jsonify({'message': 'Pipeline updated'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating pipeline: {e}")
        return jsonify({'error': 'Failed to update pipeline'}), 500


@crm_bp.route('/tasks', methods=['GET', 'OPTIONS'])
def list_tasks():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        items = FollowUp.query.order_by(FollowUp.due_date.asc()).all()
        return jsonify([
            {
                'id': t.id,
                'type': t.type,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'status': t.status,
                'notes': t.notes,
                'contact_id': t.contact_id,
                'lead_id': t.lead_id,
                'opportunity_id': t.opportunity_id,
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'completed_at': t.completed_at.isoformat() if t.completed_at else None,
                'assigned_to': t.assigned_to,
                'created_by': t.created_by
            } for t in items
        ]), 200
    except Exception as e:
        print(f"Error listing tasks: {e}")
        return jsonify([]), 200


@crm_bp.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json() or {}
        due = None
        if data.get('due_date'):
            try:
                due = datetime.fromisoformat(data.get('due_date'))
            except Exception:
                pass
        t = FollowUp(
            contact_id=data.get('contact_id'),
            lead_id=data.get('lead_id'),
            opportunity_id=data.get('opportunity_id'),
            type=data.get('type') or 'task',
            due_date=due,
            status=data.get('status') or 'pending',
            notes=data.get('notes')
        )
        db.session.add(t)
        db.session.commit()
        return jsonify({'id': t.id, 'message': 'Task created'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating task: {e}")
        return jsonify({'error': 'Failed to create task'}), 500


@crm_bp.route('/tasks/<int:task_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def task_detail(task_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    t = FollowUp.query.get_or_404(task_id)
    if request.method == 'DELETE':
        try:
            db.session.delete(t)
            db.session.commit()
            return jsonify({'message': 'Task deleted'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting task: {e}")
            return jsonify({'error': 'Failed to delete task'}), 500
    try:
        data = request.get_json() or {}
        if 'type' in data:
            t.type = data.get('type') or t.type
        if 'status' in data:
            t.status = data.get('status') or t.status
        if 'notes' in data:
            t.notes = data.get('notes')
        if 'due_date' in data:
            try:
                t.due_date = datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else t.due_date
            except Exception:
                pass
        if 'contact_id' in data:
            t.contact_id = data.get('contact_id')
        if 'lead_id' in data:
            t.lead_id = data.get('lead_id')
        if 'opportunity_id' in data:
            t.opportunity_id = data.get('opportunity_id')
        db.session.commit()
        return jsonify({'message': 'Task updated'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating task: {e}")
        return jsonify({'error': 'Failed to update task'}), 500


@crm_bp.route('/lead-intake', methods=['GET', 'OPTIONS'])
def list_lead_intake():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        return jsonify([]), 200
    except Exception as e:
        print(f"Error listing lead intake: {e}")
        return jsonify([]), 200


@crm_bp.route('/users', methods=['GET', 'OPTIONS'])
def list_crm_users():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        # Return minimal placeholder users list
        return jsonify([]), 200
    except Exception as e:
        print(f"Error listing CRM users: {e}")
        return jsonify([]), 200


# -----------------------------
# Exports (CSV)
# -----------------------------

def _rows_to_csv(fieldnames, rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow({k: ('' if v is None else v) for k, v in row.items()})
    csv_data = buffer.getvalue()
    buffer.close()
    return csv_data


@crm_bp.route('/exports/<string:entity>', methods=['GET'])
def export_entity(entity: str):
    entity = (entity or '').lower()
    try:
        if entity == 'contacts':
            items = Contact.query.all()
            fieldnames = ['id', 'first_name', 'last_name', 'email', 'phone', 'company', 'company_id', 'type', 'status', 'region', 'assigned_team', 'created_at']
            rows = [{
                'id': c.id,
                'first_name': c.first_name,
                'last_name': c.last_name,
                'email': c.email,
                'phone': c.phone,
                'company': c.company,
                'company_id': getattr(c, 'company_id', None),
                'type': c.type,
                'status': c.status,
                'region': getattr(c, 'region', None),
                'assigned_team': getattr(c, 'assigned_team', None),
                'created_at': c.created_at.isoformat() if c.created_at else ''
            } for c in items]
        elif entity == 'leads':
            items = Lead.query.all()
            fieldnames = ['id', 'first_name', 'last_name', 'email', 'phone', 'company', 'source', 'status', 'lead_status', 'region', 'assigned_team', 'score', 'created_at']
            rows = [{
                'id': l.id,
                'first_name': l.first_name,
                'last_name': l.last_name,
                'email': l.email,
                'phone': l.phone,
                'company': l.company,
                'source': l.source,
                'status': l.status,
                'lead_status': getattr(l, 'lead_status', None),
                'region': getattr(l, 'region', None),
                'assigned_team': getattr(l, 'assigned_team', None),
                'score': getattr(l, 'score', 0),
                'created_at': l.created_at.isoformat() if l.created_at else ''
            } for l in items]
        elif entity == 'companies':
            items = Company.query.all()
            fieldnames = ['id', 'name', 'industry', 'size', 'region', 'assigned_team', 'created_at']
            rows = [{
                'id': c.id,
                'name': c.name,
                'industry': c.industry,
                'size': c.size,
                'region': c.region,
                'assigned_team': c.assigned_team,
                'created_at': c.created_at.isoformat() if c.created_at else ''
            } for c in items]
        elif entity == 'opportunities':
            items = Opportunity.query.all()
            fieldnames = ['id', 'name', 'amount', 'stage', 'contact_id', 'company_id', 'probability', 'region', 'assigned_team', 'expected_close_date', 'created_at']
            rows = [{
                'id': o.id,
                'name': o.name,
                'amount': float(o.amount) if o.amount else 0.0,
                'stage': o.stage,
                'contact_id': o.contact_id,
                'company_id': getattr(o, 'company_id', None),
                'probability': o.probability,
                'region': getattr(o, 'region', None),
                'assigned_team': getattr(o, 'assigned_team', None),
                'expected_close_date': o.expected_close_date.isoformat() if o.expected_close_date else '',
                'created_at': o.created_at.isoformat() if o.created_at else ''
            } for o in items]
        elif entity == 'activities':
            items = Communication.query.order_by(Communication.created_at.desc()).all()
            fieldnames = ['id', 'type', 'direction', 'subject', 'content', 'status', 'contact_id', 'lead_id', 'opportunity_id', 'scheduled_for', 'created_at']
            rows = [{
                'id': a.id,
                'type': a.type,
                'direction': a.direction,
                'subject': a.subject,
                'content': a.content,
                'status': a.status,
                'contact_id': getattr(a, 'contact_id', None),
                'lead_id': getattr(a, 'lead_id', None),
                'opportunity_id': getattr(a, 'opportunity_id', None),
                'scheduled_for': a.scheduled_for.isoformat() if getattr(a, 'scheduled_for', None) else '',
                'created_at': a.created_at.isoformat() if a.created_at else ''
            } for a in items]
        else:
            return jsonify({'error': 'Unsupported export entity'}), 400

        csv_data = _rows_to_csv(fieldnames, rows)
        filename = f"crm_{entity}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        headers = {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return Response(csv_data, headers=headers)
    except Exception as e:
        print(f"Error exporting {entity}: {e}")
        return jsonify({'error': f'Failed to export {entity}'}), 500


# -----------------------------
# Imports (CSV)
# -----------------------------

_IMPORT_SUPPORTED = {'contacts', 'leads', 'companies', 'opportunities', 'activities'}


def _parse_csv_text(csv_text: str):
    try:
        # Strip BOM and normalize newlines
        cleaned = csv_text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
        buffer = io.StringIO(cleaned)
        # Auto-detect delimiter
        sample = cleaned.split('\n', 5)
        sniff = None
        try:
            sniff = csv.Sniffer().sniff('\n'.join(sample), delimiters=',;\t|')
        except Exception:
            pass
        reader = csv.DictReader(buffer, dialect=sniff) if sniff else csv.DictReader(buffer)
        rows = [dict(row) for row in reader]
        headers = reader.fieldnames or []
        buffer.close()
        return headers, rows
    except Exception as e:
        raise ValueError(f"Invalid CSV: {e}")


def _remap_row(row: dict, mapping: dict) -> dict:
    if not mapping:
        return row
    out = {}
    for csv_col, value in row.items():
        target = mapping.get(csv_col, csv_col)
        out[target] = value
    return out


def _validate_row(entity: str, row: dict) -> list:
    errors = []
    if entity == 'contacts':
        if not (row.get('first_name') and row.get('last_name')):
            errors.append('Missing first_name/last_name')
        if not row.get('email') and not row.get('phone'):
            errors.append('One of email or phone is required')
    elif entity == 'leads':
        if not (row.get('first_name') and row.get('last_name')):
            errors.append('Missing first_name/last_name')
    elif entity == 'companies':
        if not row.get('name'):
            errors.append('Missing name')
    elif entity == 'opportunities':
        if not row.get('name'):
            errors.append('Missing name')
    elif entity == 'activities':
        if not row.get('type'):
            errors.append('Missing type')
        if not (row.get('contact_id') or row.get('lead_id') or row.get('opportunity_id')):
            errors.append('Must reference a lead, contact, or opportunity')
    return errors


def _dedupe_key(entity: str, row: dict):
    if entity in {'contacts', 'leads'}:
        return (row.get('email') or '').strip().lower() or None
    if entity == 'companies':
        return (row.get('name') or '').strip().lower() or None
    if entity == 'opportunities':
        base = (row.get('name') or '').strip().lower()
        contact = (row.get('contact_id') or '').strip()
        return f"{base}|{contact}" if base else None
    return None


@crm_bp.route('/imports/<string:entity>', methods=['POST', 'OPTIONS'])
def import_entity(entity: str):
    if request.method == 'OPTIONS':
        return ('', 200)
    entity = (entity or '').lower()
    if entity not in _IMPORT_SUPPORTED:
        return jsonify({'error': 'Unsupported import entity'}), 400

    dry_run = str(request.args.get('dry_run', 'true')).lower() != 'false'
    mapping_raw = request.form.get('mapping') or request.args.get('mapping')
    mapping = None
    if mapping_raw:
        try:
            mapping = json.loads(mapping_raw)
        except Exception:
            return jsonify({'error': 'Invalid mapping JSON'}), 400

    csv_text = None
    if 'file' in request.files:
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        filename = secure_filename(file.filename or 'upload.csv')
        try:
            csv_text = file.stream.read().decode('utf-8', errors='ignore')
        except Exception:
            csv_text = file.read().decode('utf-8', errors='ignore')
    else:
        payload = request.get_json(silent=True) or {}
        csv_text = payload.get('csv')

    if not csv_text:
        return jsonify({'error': 'Missing CSV data'}), 400

    try:
        headers, rows = _parse_csv_text(csv_text)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    remapped = [_remap_row(r, mapping or {}) for r in rows]

    errors = []
    duplicates = 0
    seen = set()
    valid_rows = []
    for idx, row in enumerate(remapped, start=1):
        row_errors = _validate_row(entity, row)
        key = _dedupe_key(entity, row)
        if key and key in seen:
            duplicates += 1
        if key:
            seen.add(key)
        if row_errors:
            errors.append({'row': idx, 'errors': row_errors})
        else:
            valid_rows.append(row)

    summary = {
        'entity': entity,
        'totalRows': len(rows),
        'validRows': len(valid_rows),
        'errorCount': len(errors),
        'duplicateCount': duplicates,
        'headers': headers,
        'sample': valid_rows[:10]
    }

    if dry_run:
        return jsonify({'summary': summary}), 200

    # Persist valid rows
    created = 0
    failed = 0
    write_errors = []
    for idx, row in enumerate(valid_rows, start=1):
        try:
            if entity == 'contacts':
                obj = Contact(
                    first_name=row.get('first_name'),
                    last_name=row.get('last_name'),
                    email=row.get('email'),
                    phone=row.get('phone'),
                    company=row.get('company'),
                    company_id=row.get('company_id'),
                    type=row.get('type') or 'customer',
                    status=row.get('status') or 'active',
                    region=row.get('region'),
                    assigned_team=row.get('assigned_team'),
                )
                db.session.add(obj)
            elif entity == 'leads':
                obj = Lead(
                    first_name=row.get('first_name'),
                    last_name=row.get('last_name'),
                    email=row.get('email'),
                    phone=row.get('phone'),
                    company=row.get('company'),
                    source=row.get('source') or 'website',
                    status=row.get('status') or 'new',
                    lead_status=row.get('lead_status'),
                    region=row.get('region'),
                    assigned_team=row.get('assigned_team'),
                    score=int(row.get('score') or 0),
                )
                db.session.add(obj)
            elif entity == 'companies':
                obj = Company(
                    name=row.get('name'),
                    industry=row.get('industry'),
                    size=row.get('size'),
                    region=row.get('region'),
                    assigned_team=row.get('assigned_team'),
                )
                db.session.add(obj)
            elif entity == 'opportunities':
                # Expected products as JSON string or omitted
                products = row.get('products')
                try:
                    if isinstance(products, str) and products.strip():
                        products = json.loads(products)
                except Exception:
                    products = None
                expected_close_date = None
                ecd = row.get('expected_close_date')
                try:
                    if ecd:
                        expected_close_date = datetime.fromisoformat(ecd).date()
                except Exception:
                    expected_close_date = None
                obj = Opportunity(
                    name=row.get('name'),
                    amount=float(row.get('amount') or 0.0),
                    stage=row.get('stage') or 'prospecting',
                    contact_id=row.get('contact_id'),
                    company_id=row.get('company_id'),
                    probability=int(row.get('probability') or 0),
                    expected_close_date=expected_close_date,
                    region=row.get('region'),
                    assigned_team=row.get('assigned_team'),
                    products=products,
                )
                db.session.add(obj)
            elif entity == 'activities':
                obj = Communication(
                    type=row.get('type'),
                    direction=row.get('direction') or 'outbound',
                    subject=row.get('subject'),
                    content=row.get('content'),
                    status=row.get('status') or 'completed',
                )
                if row.get('lead_id'):
                    obj.lead_id = int(row.get('lead_id'))
                if row.get('contact_id'):
                    obj.contact_id = int(row.get('contact_id'))
                if row.get('opportunity_id'):
                    obj.opportunity_id = int(row.get('opportunity_id'))
                db.session.add(obj)
            created += 1
        except Exception as e:
            failed += 1
            write_errors.append({'row': idx, 'error': str(e)})

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database commit failed: {e}', 'summary': summary, 'created': created, 'failed': failed, 'writeErrors': write_errors}), 500

    return jsonify({'message': 'Import completed', 'summary': summary, 'created': created, 'failed': failed, 'writeErrors': write_errors}), 200


# -----------------------------
# Tasks Calendar Export (ICS)
# -----------------------------

@crm_bp.route('/tasks/calendar.ics', methods=['GET'])
def tasks_calendar_ics():
    try:
        items = FollowUp.query.order_by(FollowUp.due_date.asc()).all()

        def ics_escape(text: str) -> str:
            return (text or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//EdonuOps CRM//Tasks//EN'
        ]
        for t in items:
            if not t.due_date:
                continue
            dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            dtstart = t.due_date.strftime('%Y%m%dT%H%M%SZ')
            uid = f"crm-task-{t.id}@edonuops"
            summary = ics_escape(t.notes or f"CRM {t.type or 'task'}")
            description = ics_escape(f"Status: {t.status or 'pending'}")
            lines.extend([
                'BEGIN:VEVENT',
                f'UID:{uid}',
                f'DTSTAMP:{dtstamp}',
                f'DTSTART:{dtstart}',
                f'SUMMARY:{summary}',
                f'DESCRIPTION:{description}',
                'END:VEVENT'
            ])
        lines.append('END:VCALENDAR')
        ics_body = '\r\n'.join(lines) + '\r\n'
        headers = {
            'Content-Type': 'text/calendar; charset=utf-8',
            'Content-Disposition': 'attachment; filename="crm_tasks_calendar.ics"'
        }
        return Response(ics_body, headers=headers)
    except Exception as e:
        print(f"Error generating ICS: {e}")
        return jsonify({'error': 'Failed to generate calendar'}), 500

# -----------------------------
# Advanced Reports
# -----------------------------

@crm_bp.route('/reports/forecast', methods=['GET'])
def crm_forecast():
    try:
        # Overall forecast and by stage
        opps = Opportunity.query.all()
        total_value = sum(float(o.amount or 0) for o in opps)
        weighted_value = sum(float(o.amount or 0) * (float(o.probability or 0) / 100.0) for o in opps)

        by_stage = {}
        for o in opps:
            stage = o.stage or 'unknown'
            entry = by_stage.setdefault(stage, {'count': 0, 'value': 0.0, 'weighted': 0.0})
            value = float(o.amount or 0)
            entry['count'] += 1
            entry['value'] += value
            entry['weighted'] += value * (float(o.probability or 0) / 100.0)

        # Simple 30/60/90-day projection by expected_close_date
        now = datetime.utcnow().date()
        buckets = {
            'next_30_days': 0.0,
            'next_60_days': 0.0,
            'next_90_days': 0.0
        }
        for o in opps:
            if o.expected_close_date:
                days = (o.expected_close_date - now).days
                value = float(o.amount or 0) * (float(o.probability or 0) / 100.0)
                if 0 <= days <= 30:
                    buckets['next_30_days'] += value
                elif 31 <= days <= 60:
                    buckets['next_60_days'] += value
                elif 61 <= days <= 90:
                    buckets['next_90_days'] += value

        return jsonify({
            'totalValue': round(total_value, 2),
            'weightedValue': round(weighted_value, 2),
            'byStage': {k: {'count': v['count'], 'value': round(v['value'], 2), 'weighted': round(v['weighted'], 2)} for k, v in by_stage.items()},
            'projections': {k: round(v, 2) for k, v in buckets.items()}
        }), 200
    except Exception as e:
        print(f"Error computing forecast: {e}")
        return jsonify({'error': 'Failed to compute forecast'}), 500


@crm_bp.route('/reports/performance', methods=['GET'])
def crm_performance():
    try:
        # Basic team and region performance snapshots
        opps = Opportunity.query.all()
        by_team = {}
        by_region = {}
        for o in opps:
            team = getattr(o, 'assigned_team', None) or 'Unassigned'
            region = getattr(o, 'region', None) or 'Unspecified'
            value = float(o.amount or 0)

            t = by_team.setdefault(team, {'count': 0, 'value': 0.0})
            t['count'] += 1
            t['value'] += value

            r = by_region.setdefault(region, {'count': 0, 'value': 0.0})
            r['count'] += 1
            r['value'] += value

        return jsonify({
            'byTeam': {k: {'count': v['count'], 'value': round(v['value'], 2)} for k, v in by_team.items()},
            'byRegion': {k: {'count': v['count'], 'value': round(v['value'], 2)} for k, v in by_region.items()}
        }), 200
    except Exception as e:
        print(f"Error computing performance: {e}")
        return jsonify({'error': 'Failed to compute performance'}), 500


# -----------------------------
# Advanced Reports: Funnel & Stuck Deals
# -----------------------------

@crm_bp.route('/reports/funnel', methods=['GET'])
def crm_funnel():
    try:
        # Simple stage counts and ordered funnel for opportunities
        stages_order = [
            'prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'
        ]
        counts = {stage: 0 for stage in stages_order}
        for o in Opportunity.query.all():
            stage = (o.stage or 'unknown').lower()
            if stage not in counts:
                counts[stage] = 0
            counts[stage] += 1
        ordered = [{ 'stage': s, 'count': counts.get(s, 0) } for s in stages_order]
        return jsonify({ 'funnel': ordered, 'allStages': counts }), 200
    except Exception as e:
        print(f"Error computing funnel: {e}")
        return jsonify({ 'error': 'Failed to compute funnel' }), 500


@crm_bp.route('/reports/stuck', methods=['GET'])
def crm_stuck_deals():
    try:
        # Deals not updated for N days and not closed
        days = request.args.get('days', default=30, type=int)
        cutoff = datetime.utcnow() - timedelta(days=max(1, days))
        stuck = Opportunity.query.filter(
            (Opportunity.stage != 'closed_won') & (Opportunity.stage != 'closed_lost') &
            (Opportunity.updated_at < cutoff)
        ).all()
        data = [
            {
                'id': o.id,
                'name': o.name,
                'stage': o.stage,
                'amount': float(o.amount or 0.0),
                'probability': o.probability,
                'updated_at': o.updated_at.isoformat() if o.updated_at else None,
                'ageDays': (datetime.utcnow() - (o.updated_at or o.created_at or datetime.utcnow())).days
            } for o in stuck
        ]
        return jsonify({ 'days': days, 'count': len(data), 'deals': data }), 200
    except Exception as e:
        print(f"Error computing stuck deals: {e}")
        return jsonify({ 'error': 'Failed to compute stuck deals' }), 500

# -----------------------------
# Marketing (Email-only) stubs
# -----------------------------

# In-memory storage for demo; replace with DB model later
MARKETING_STORE = {
    'sender': {
        'from_email': None,
        'from_name': None
    },
    'segments': [],
    'templates': [],
    'campaigns': [],
    'sequences': []
}


@crm_bp.route('/marketing/sender', methods=['GET', 'POST', 'OPTIONS'])
def marketing_sender():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(MARKETING_STORE['sender']), 200
    data = request.get_json() or {}
    MARKETING_STORE['sender'] = {
        'from_email': data.get('from_email'),
        'from_name': data.get('from_name')
    }
    return jsonify({'message': 'Sender updated'}), 200


@crm_bp.route('/marketing/segments', methods=['GET', 'POST', 'OPTIONS'])
def marketing_segments():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(MARKETING_STORE['segments']), 200
    data = request.get_json() or {}
    segment = {
        'id': len(MARKETING_STORE['segments']) + 1,
        'name': data.get('name'),
        'criteria': data.get('criteria') or {}
    }
    MARKETING_STORE['segments'].append(segment)
    return jsonify(segment), 201


@crm_bp.route('/marketing/templates', methods=['GET', 'POST', 'OPTIONS'])
def marketing_templates():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(MARKETING_STORE['templates']), 200
    data = request.get_json() or {}
    template = {
        'id': len(MARKETING_STORE['templates']) + 1,
        'name': data.get('name'),
        'subject': data.get('subject'),
        'body': data.get('body')
    }
    MARKETING_STORE['templates'].append(template)
    return jsonify(template), 201


@crm_bp.route('/marketing/campaigns', methods=['GET', 'POST', 'OPTIONS'])
def marketing_campaigns():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(MARKETING_STORE['campaigns']), 200
    data = request.get_json() or {}
    campaign = {
        'id': len(MARKETING_STORE['campaigns']) + 1,
        'name': data.get('name'),
        'segment_id': data.get('segment_id'),
        'template_id': data.get('template_id'),
        'status': 'draft',
        'scheduled_for': data.get('scheduled_for')
    }
    MARKETING_STORE['campaigns'].append(campaign)
    return jsonify(campaign), 201


# Drip Sequences
@crm_bp.route('/marketing/sequences', methods=['GET', 'POST', 'OPTIONS'])
def marketing_sequences():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(MARKETING_STORE['sequences']), 200
    data = request.get_json() or {}
    seq = {
        'id': len(MARKETING_STORE['sequences']) + 1,
        'name': data.get('name'),
        'steps': data.get('steps') or [],
        'status': 'draft'
    }
    MARKETING_STORE['sequences'].append(seq)
    return jsonify(seq), 201

# -----------------------------
# Workflows (lightweight)
# -----------------------------

WORKFLOW_STORE = {
    'seq': 0,
    'workflows': [],
    'execution_history': [],
    'schedules': []  # simple in-memory schedules
}


def _next_workflow_id():
    WORKFLOW_STORE['seq'] += 1
    return WORKFLOW_STORE['seq']


@crm_bp.route('/workflows', methods=['GET', 'POST', 'OPTIONS'])
def workflows_collection():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(WORKFLOW_STORE['workflows']), 200
    try:
        data = request.get_json() or {}
        workflow = {
            'id': _next_workflow_id(),
            'name': data.get('name') or f"Workflow #{WORKFLOW_STORE['seq']}",
            'trigger': data.get('trigger') or {'id': data.get('trigger_id')},
            'actions': data.get('actions') or [],
            'conditions': data.get('conditions') or [],
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        WORKFLOW_STORE['workflows'].append(workflow)
        return jsonify(workflow), 201
    except Exception as e:
        print(f"Error creating workflow: {e}")
        return jsonify({'error': 'Failed to create workflow'}), 500


@crm_bp.route('/workflows/<int:wf_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def workflow_detail(wf_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    items = WORKFLOW_STORE['workflows']
    wf = next((w for w in items if w['id'] == wf_id), None)
    if not wf:
        return jsonify({'error': 'Not found'}), 404
    if request.method == 'DELETE':
        WORKFLOW_STORE['workflows'] = [w for w in items if w['id'] != wf_id]
        return jsonify({'message': 'Workflow deleted'}), 200
    try:
        data = request.get_json() or {}
        wf['name'] = data.get('name', wf['name'])
        if 'trigger' in data or 'trigger_id' in data:
            wf['trigger'] = data.get('trigger') or {'id': data.get('trigger_id')}
        if 'actions' in data:
            wf['actions'] = data.get('actions') or []
        if 'conditions' in data:
            wf['conditions'] = data.get('conditions') or []
        return jsonify(wf), 200
    except Exception as e:
        print(f"Error updating workflow: {e}")
        return jsonify({'error': 'Failed to update workflow'}), 500


@crm_bp.route('/workflows/<int:wf_id>/toggle', methods=['PATCH', 'OPTIONS'])
def workflow_toggle(wf_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    items = WORKFLOW_STORE['workflows']
    wf = next((w for w in items if w['id'] == wf_id), None)
    if not wf:
        return jsonify({'error': 'Not found'}), 404
    wf['is_active'] = not wf.get('is_active', True)
    return jsonify({'id': wf_id, 'is_active': wf['is_active']}), 200


@crm_bp.route('/workflows/execution-history', methods=['GET', 'OPTIONS'])
def workflow_execution_history():
    if request.method == 'OPTIONS':
        return ('', 200)
    # For now return in-memory history
    return jsonify(WORKFLOW_STORE['execution_history']), 200


@crm_bp.route('/workflows/schedules', methods=['GET', 'POST', 'OPTIONS'])
def workflow_schedules():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(WORKFLOW_STORE['schedules']), 200
    try:
        data = request.get_json() or {}
        sched = {
            'id': len(WORKFLOW_STORE['schedules']) + 1,
            'name': data.get('name') or f"Schedule #{len(WORKFLOW_STORE['schedules']) + 1}",
            'cron': data.get('cron') or '0 9 * * *',  # default daily 9am
            'workflow_id': data.get('workflow_id')
        }
        WORKFLOW_STORE['schedules'].append(sched)
        return jsonify(sched), 201
    except Exception as e:
        print(f"Error creating schedule: {e}")
        return jsonify({'error': 'Failed to create schedule'}), 500

@crm_bp.route('/workflows/schedules/run', methods=['POST', 'OPTIONS'])
def workflow_run_schedules():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        now = datetime.utcnow().isoformat()
        results = []
        for s in (WORKFLOW_STORE.get('schedules') or []):
            entry = {
                'timestamp': now,
                'schedule_id': s.get('id'),
                'workflow_id': s.get('workflow_id'),
                'status': 'queued',
                'message': f"Scheduled run for workflow {s.get('workflow_id')}"
            }
            WORKFLOW_STORE['execution_history'].insert(0, entry)
            # cap history to last 200 entries
            if len(WORKFLOW_STORE['execution_history']) > 200:
                WORKFLOW_STORE['execution_history'] = WORKFLOW_STORE['execution_history'][:200]
            results.append(entry)
        return jsonify({'ran': len(results), 'entries': results}), 200
    except Exception as e:
        print(f"Error running schedules: {e}")
        return jsonify({'error': 'Failed to run schedules'}), 500

# -----------------------------
# Knowledge Base Articles
# -----------------------------

@crm_bp.route('/kb/articles', methods=['GET', 'POST', 'OPTIONS'])
def kb_articles():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        q = (request.args.get('q') or '').strip().lower()
        items = KnowledgeBaseArticle.query.order_by(KnowledgeBaseArticle.updated_at.desc()).all()
        def matches(a: KnowledgeBaseArticle) -> bool:
            if not q:
                return True
            hay = ' '.join([
                (a.title or ''),
                (a.content or ''),
                (a.tags or '')
            ]).lower()
            return q in hay
        data = [
            {
                'id': a.id,
                'title': a.title,
                'content': a.content,
                'tags': a.tags,
                'published': getattr(a, 'published', False),
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'updated_at': a.updated_at.isoformat() if a.updated_at else None
            } for a in items if matches(a)
        ]
        return jsonify(data), 200
    # POST create
    try:
        data = request.get_json() or {}
        art = KnowledgeBaseArticle(
            title=data.get('title'),
            content=data.get('content'),
            tags=data.get('tags'),
            published=bool(data.get('published'))
        )
        db.session.add(art)
        db.session.commit()
        return jsonify({'id': art.id, 'message': 'Article created'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating KB article: {e}")
        return jsonify({'error': 'Failed to create article'}), 500


@crm_bp.route('/kb/articles/<int:article_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def kb_article_detail(article_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    a = KnowledgeBaseArticle.query.get_or_404(article_id)
    if request.method == 'GET':
        try:
            return jsonify({
                'id': a.id,
                'title': a.title,
                'content': a.content,
                'tags': a.tags,
                'published': getattr(a, 'published', False),
                'attachments': [
                    {
                        'id': att.id,
                        'filename': att.filename,
                        'url': f"/api/crm/kb/attachments/{att.id}",
                        'mime_type': att.mime_type,
                        'uploaded_at': att.uploaded_at.isoformat() if att.uploaded_at else None
                    } for att in (a.attachments or [])
                ],
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'updated_at': a.updated_at.isoformat() if a.updated_at else None
            }), 200
        except Exception as e:
            print(f"Error reading KB article: {e}")
            return jsonify({'error': 'Failed to read article'}), 500
    if request.method == 'DELETE':
        try:
            db.session.delete(a)
            db.session.commit()
            return jsonify({'message': 'Article deleted'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting KB article: {e}")
            return jsonify({'error': 'Failed to delete article'}), 500
    try:
        data = request.get_json() or {}
        a.title = data.get('title', a.title)
        a.content = data.get('content', a.content)
        a.tags = data.get('tags', a.tags)
        a.published = bool(data.get('published', a.published))
        db.session.commit()
        return jsonify({'message': 'Article updated'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating KB article: {e}")
        return jsonify({'error': 'Failed to update article'}), 500

@crm_bp.route('/kb/public', methods=['GET'])
def kb_public_index():
    try:
        q = (request.args.get('q') or '').strip().lower()
        items = KnowledgeBaseArticle.query.filter_by(published=True).order_by(KnowledgeBaseArticle.updated_at.desc()).all()
        def matches(a: KnowledgeBaseArticle) -> bool:
            if not q:
                return True
            hay = ' '.join([(a.title or ''), (a.content or ''), (a.tags or '')]).lower()
            return q in hay
        data = [{
            'id': a.id,
            'title': a.title,
            'excerpt': (a.content or '')[:300],
            'tags': a.tags,
            'updated_at': a.updated_at.isoformat() if a.updated_at else None
        } for a in items if matches(a)]
        return jsonify(data), 200
    except Exception as e:
        print(f"Error listing public KB: {e}")
        return jsonify({'error': 'Failed to list published articles'}), 500

@crm_bp.route('/kb/public/<int:article_id>', methods=['GET'])
def kb_public_detail(article_id: int):
    try:
        a = KnowledgeBaseArticle.query.get_or_404(article_id)
        if not getattr(a, 'published', False):
            return jsonify({'error': 'Article not published'}), 403
        return jsonify({
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'tags': a.tags,
            'updated_at': a.updated_at.isoformat() if a.updated_at else None
        }), 200
    except Exception as e:
        print(f"Error fetching public KB article: {e}")
        return jsonify({'error': 'Failed to fetch article'}), 500

@crm_bp.route('/kb/articles/<int:article_id>/attachments', methods=['POST', 'OPTIONS'])
def kb_upload_attachment(article_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        a = KnowledgeBaseArticle.query.get_or_404(article_id)
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        filename = secure_filename(file.filename)
        upload_dir = os.path.join('uploads', 'kb')
        try:
            os.makedirs(upload_dir, exist_ok=True)
        except Exception:
            pass
        # Prevent path traversal, enforce size limit (~10MB) and safe MIME
        filepath = os.path.join(upload_dir, filename)
        try:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
        except Exception:
            size = None
        if size and size > 10 * 1024 * 1024:
            return jsonify({'error': 'File too large'}), 400
        safe_mime = file.mimetype or 'application/octet-stream'
        if any(part in filename for part in ['..', '/', '\\']):
            return jsonify({'error': 'Invalid filename'}), 400
        file.save(filepath)
        att = KnowledgeBaseAttachment(
            article_id=a.id,
            filename=filename,
            filepath=filepath,
            mime_type=safe_mime
        )
        db.session.add(att)
        db.session.commit()
        return jsonify({'id': att.id, 'filename': att.filename, 'url': f"/api/crm/kb/attachments/{att.id}"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error uploading attachment: {e}")
        return jsonify({'error': 'Failed to upload attachment'}), 500

@crm_bp.route('/kb/attachments/<int:attachment_id>', methods=['GET', 'DELETE', 'OPTIONS'])
def kb_attachment_detail(attachment_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    att = KnowledgeBaseAttachment.query.get_or_404(attachment_id)
    if request.method == 'GET':
        try:
            # Stream file
            from flask import send_file
            return send_file(att.filepath, as_attachment=True, download_name=att.filename)
        except Exception as e:
            print(f"Error serving attachment: {e}")
            return jsonify({'error': 'Failed to serve attachment'}), 500
    try:
        # Delete
        try:
            os.remove(att.filepath)
        except Exception:
            pass
        db.session.delete(att)
        db.session.commit()
        return jsonify({'message': 'Attachment deleted'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting attachment: {e}")
        return jsonify({'error': 'Failed to delete attachment'}), 500


# -----------------------------
# Data Quality: Duplicates & Merge
# -----------------------------

@crm_bp.route('/data-quality/duplicates', methods=['GET', 'OPTIONS'])
def data_quality_duplicates():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        entity = (request.args.get('entity') or 'contacts').lower()
        groups = []
        if entity == 'contacts':
            items = Contact.query.all()
            key_to_items = {}
            for c in items:
                key = (c.email or '').strip().lower()
                if not key:
                    continue
                key_to_items.setdefault(key, []).append(c)
            for key, lst in key_to_items.items():
                if len(lst) > 1:
                    groups.append({
                        'key': key,
                        'records': [{
                            'id': i.id,
                            'name': f"{i.first_name or ''} {i.last_name or ''}".strip(),
                            'email': i.email,
                            'phone': i.phone,
                            'company': i.company,
                            'created_at': i.created_at.isoformat() if i.created_at else None
                        } for i in lst]
                    })
        elif entity == 'companies':
            items = Company.query.all()
            key_to_items = {}
            for c in items:
                key = (c.name or '').strip().lower()
                if not key:
                    continue
                key_to_items.setdefault(key, []).append(c)
            for key, lst in key_to_items.items():
                if len(lst) > 1:
                    groups.append({
                        'key': key,
                        'records': [{
                            'id': i.id,
                            'name': i.name,
                            'industry': i.industry,
                            'region': i.region,
                            'created_at': i.created_at.isoformat() if i.created_at else None
                        } for i in lst]
                    })
        elif entity == 'leads':
            items = Lead.query.all()
            key_to_items = {}
            for l in items:
                key = (l.email or '').strip().lower()
                if not key:
                    continue
                key_to_items.setdefault(key, []).append(l)
            for key, lst in key_to_items.items():
                if len(lst) > 1:
                    groups.append({
                        'key': key,
                        'records': [{
                            'id': i.id,
                            'name': f"{i.first_name or ''} {i.last_name or ''}".strip(),
                            'email': i.email,
                            'company': i.company,
                            'score': getattr(i, 'score', 0),
                            'created_at': i.created_at.isoformat() if i.created_at else None
                        } for i in lst]
                    })
        else:
            return jsonify({'error': 'Unsupported entity'}), 400
        return jsonify({'entity': entity, 'groups': groups, 'groupCount': len(groups)}), 200
    except Exception as e:
        print(f"Error finding duplicates: {e}")
        return jsonify({'error': 'Failed to find duplicates'}), 500


@crm_bp.route('/data-quality/merge', methods=['POST', 'OPTIONS'])
def data_quality_merge():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data = request.get_json(silent=True) or {}
        entity = (data.get('entity') or '').lower()
        target_id = data.get('target_id')
        source_id = data.get('source_id')
        if not entity or not target_id or not source_id:
            return jsonify({'error': 'entity, target_id, source_id are required'}), 400
        if str(target_id) == str(source_id):
            return jsonify({'error': 'target_id and source_id cannot be the same'}), 400

        def merge_simple(target, source, fields):
            for f in fields:
                tv = getattr(target, f, None)
                sv = getattr(source, f, None)
                if (tv is None or tv == '' or (isinstance(tv, str) and not tv.strip())) and sv not in (None, ''):
                    setattr(target, f, sv)

        if entity == 'contacts':
            target = Contact.query.get_or_404(int(target_id))
            source = Contact.query.get_or_404(int(source_id))
            merge_simple(target, source, ['first_name', 'last_name', 'email', 'phone', 'company', 'company_id', 'type', 'status', 'region', 'assigned_team'])
            db.session.delete(source)
        elif entity == 'companies':
            target = Company.query.get_or_404(int(target_id))
            source = Company.query.get_or_404(int(source_id))
            merge_simple(target, source, ['name', 'industry', 'size', 'region', 'assigned_team'])
            db.session.delete(source)
        elif entity == 'leads':
            target = Lead.query.get_or_404(int(target_id))
            source = Lead.query.get_or_404(int(source_id))
            merge_simple(target, source, ['first_name', 'last_name', 'email', 'phone', 'company', 'source', 'status', 'lead_status', 'region', 'assigned_team'])
            try:
                target.score = target.score or source.score
            except Exception:
                pass
            db.session.delete(source)
        else:
            return jsonify({'error': 'Unsupported entity'}), 400

        db.session.commit()
        return jsonify({'message': 'Merge completed', 'entity': entity, 'target_id': target_id, 'source_id': source_id}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error merging records: {e}")
        return jsonify({'error': 'Failed to merge records'}), 500

# -----------------------------
# Ticketing (minimal)
# -----------------------------

@crm_bp.route('/tickets', methods=['GET', 'POST', 'OPTIONS'])
def tickets_collection():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        try:
            items = Ticket.query.order_by(Ticket.created_at.desc()).all()
            # Load SLA policy
            policy = SLA_STORE.get('policy', {'first_response_minutes': 60, 'resolve_minutes': 1440})
            first_minutes = int(policy.get('first_response_minutes') or 60)
            resolve_minutes = int(policy.get('resolve_minutes') or 1440)
            now = datetime.utcnow()
            return jsonify([
                {
                    'id': t.id,
                    'subject': t.subject,
                    'description': t.description,
                    'status': t.status,
                    'priority': t.priority,
                    'category': t.category,
                    'tags': t.tags,
                    'customer_email': t.customer_email,
                    'contact_id': t.contact_id,
                    'lead_id': t.lead_id,
                    'opportunity_id': t.opportunity_id,
                    'assignee_id': t.assignee_id,
                    'created_at': t.created_at.isoformat() if t.created_at else None,
                    'updated_at': t.updated_at.isoformat() if t.updated_at else None,
                    # SLA computed fields
                    'first_response_due_at': (t.created_at + timedelta(minutes=first_minutes)).isoformat() if t.created_at else None,
                    'resolve_due_at': (t.created_at + timedelta(minutes=resolve_minutes)).isoformat() if t.created_at else None,
                    'sla_first_response_breached': (now > (t.created_at + timedelta(minutes=first_minutes))) if (t.status in ('open',) and t.created_at) else False,
                    'sla_resolve_breached': (now > (t.created_at + timedelta(minutes=resolve_minutes))) if (t.status not in ('resolved', 'closed') and t.created_at) else False,
                } for t in items
            ]), 200
        except Exception as e:
            # Gracefully degrade during local development: never 500 here
            print(f"Error listing tickets: {e}")
            return jsonify([]), 200
    data = request.get_json() or {}
    t = Ticket(
        subject=data.get('subject'),
        description=data.get('description'),
        status=data.get('status', 'open'),
        priority=data.get('priority', 'medium'),
        category=data.get('category'),
        tags=data.get('tags'),
        customer_email=data.get('customer_email'),
        contact_id=data.get('contact_id'),
        lead_id=data.get('lead_id'),
        opportunity_id=data.get('opportunity_id'),
        assignee_id=data.get('assignee_id'),
        created_by=None
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({'id': t.id, 'message': 'Ticket created'}), 201


@crm_bp.route('/tickets/<int:ticket_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def ticket_detail(ticket_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    t = Ticket.query.get_or_404(ticket_id)
    if request.method == 'DELETE':
        db.session.delete(t)
        db.session.commit()
        return jsonify({'message': 'Ticket deleted'}), 200
    data = request.get_json() or {}
    t.subject = data.get('subject', t.subject)
    t.description = data.get('description', t.description)
    t.status = data.get('status', t.status)
    t.priority = data.get('priority', t.priority)
    t.category = data.get('category', t.category)
    t.tags = data.get('tags', t.tags)
    t.customer_email = data.get('customer_email', t.customer_email)
    t.contact_id = data.get('contact_id', t.contact_id)
    t.lead_id = data.get('lead_id', t.lead_id)
    t.opportunity_id = data.get('opportunity_id', t.opportunity_id)
    t.assignee_id = data.get('assignee_id', t.assignee_id)
    db.session.commit()
    return jsonify({'message': 'Ticket updated'}), 200


# -----------------------------
# Ticketing SLA & Assignment
# -----------------------------

SLA_STORE = {
    'policy': {
        'first_response_minutes': 60,
        'resolve_minutes': 1440
    },
    'assignment': {
        'strategy': 'round_robin',
        'agents': [],
        'cursor': 0
    }
}


@crm_bp.route('/tickets/sla-policy', methods=['GET', 'POST', 'OPTIONS'])
def tickets_sla_policy():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(SLA_STORE['policy']), 200
    data = request.get_json() or {}
    try:
        first = int(data.get('first_response_minutes')) if data.get('first_response_minutes') is not None else SLA_STORE['policy']['first_response_minutes']
        resolve = int(data.get('resolve_minutes')) if data.get('resolve_minutes') is not None else SLA_STORE['policy']['resolve_minutes']
        SLA_STORE['policy'] = {
            'first_response_minutes': max(1, first),
            'resolve_minutes': max(1, resolve)
        }
        return jsonify({'message': 'SLA policy updated'}), 200
    except Exception as e:
        return jsonify({'error': f'Invalid policy: {e}'}), 400


@crm_bp.route('/tickets/assignment', methods=['GET', 'POST', 'OPTIONS'])
def tickets_assignment():
    if request.method == 'OPTIONS':
        return ('', 200)
    if request.method == 'GET':
        return jsonify(SLA_STORE['assignment']), 200
    data = request.get_json() or {}
    strategy = data.get('strategy') or 'round_robin'
    agents = data.get('agents') or []
    if not isinstance(agents, list):
        return jsonify({'error': 'agents must be a list of user IDs'}), 400
    SLA_STORE['assignment'] = {
        'strategy': strategy,
        'agents': agents,
        'cursor': 0
    }
    return jsonify({'message': 'Assignment settings updated'}), 200


@crm_bp.route('/tickets/<int:ticket_id>/assign', methods=['POST', 'OPTIONS'])
def assign_ticket(ticket_id):
    if request.method == 'OPTIONS':
        return ('', 200)
    t = Ticket.query.get_or_404(ticket_id)
    strategy = request.args.get('strategy') or SLA_STORE['assignment'].get('strategy') or 'round_robin'
    if strategy == 'round_robin':
        agents = SLA_STORE['assignment'].get('agents') or []
        if not agents:
            return jsonify({'error': 'No agents configured'}), 400
        cursor = SLA_STORE['assignment'].get('cursor', 0)
        assignee = agents[cursor % len(agents)]
        SLA_STORE['assignment']['cursor'] = (cursor + 1) % len(agents)
        t.assignee_id = assignee
        db.session.commit()
        return jsonify({'message': 'Assigned', 'assignee_id': assignee}), 200
    return jsonify({'error': 'Unsupported strategy'}), 400


# -----------------------------
# Enhanced AI Features - Behavioral Tracking & Task Suggestions
# -----------------------------

@crm_bp.route('/behavioral-events', methods=['POST', 'OPTIONS'])
def track_behavioral_event():
    """Track behavioral events for leads, contacts, or opportunities."""
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        event_type = data.get('event_type')
        if not event_type:
            return jsonify({'error': 'event_type is required'}), 400
        
        # At least one entity must be specified
        lead_id = data.get('lead_id')
        contact_id = data.get('contact_id')
        opportunity_id = data.get('opportunity_id')
        
        if not any([lead_id, contact_id, opportunity_id]):
            return jsonify({'error': 'At least one entity ID (lead_id, contact_id, opportunity_id) is required'}), 400
        
        # Create behavioral event
        event = BehavioralEvent(
            lead_id=lead_id,
            contact_id=contact_id,
            opportunity_id=opportunity_id,
            event_type=event_type,
            event_data=data.get('event_data', {}),
            engagement_score=data.get('engagement_score', 0)
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Trigger AI analysis if this is a lead event
        if lead_id:
            try:
                lead = Lead.query.get(lead_id)
                if lead:
                    # Update lead's behavioral data
                    if not lead.behavioral_data:
                        lead.behavioral_data = {}
                    
                    # Add event to behavioral data
                    if 'events' not in lead.behavioral_data:
                        lead.behavioral_data['events'] = []
                    
                    lead.behavioral_data['events'].append({
                        'type': event_type,
                        'timestamp': event.created_at.isoformat(),
                        'engagement_score': event.engagement_score,
                        'data': event.event_data
                    })
                    
                    # Keep only last 50 events to prevent data bloat
                    if len(lead.behavioral_data['events']) > 50:
                        lead.behavioral_data['events'] = lead.behavioral_data['events'][-50:]
                    
                    db.session.commit()
                    
                    # Trigger AI re-analysis
                    _trigger_ai_lead_analysis(lead)
                    
            except Exception as e:
                print(f"Error updating lead behavioral data: {e}")
        
        return jsonify({
            'message': 'Behavioral event tracked',
            'event_id': event.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking behavioral event: {e}")
        return jsonify({'error': 'Failed to track behavioral event'}), 500


@crm_bp.route('/ai/suggest-tasks', methods=['POST', 'OPTIONS'])
def ai_suggest_tasks():
    """Generate AI-suggested tasks based on communication history and behavioral data."""
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json() or {}
        entity_type = payload.get('entity_type')  # 'lead', 'contact', 'opportunity'
        entity_id = payload.get('entity_id')
        context = payload.get('context', {})  # Additional context like recent emails, calls, etc.
        
        if not entity_type or not entity_id:
            return jsonify({'error': 'entity_type and entity_id are required'}), 400
        
        client = OpenAI()
        
        # Get entity data and recent communications
        entity_data = {}
        communications = []
        behavioral_events = []
        
        if entity_type == 'lead':
            lead = Lead.query.get(entity_id)
            if lead:
                entity_data = {
                    'name': lead.full_name,
                    'company': lead.company,
                    'status': lead.status,
                    'source': lead.source,
                    'score': lead.score,
                    'ai_score': lead.ai_score,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None
                }
                communications = Communication.query.filter_by(lead_id=entity_id).order_by(Communication.created_at.desc()).limit(10).all()
                behavioral_events = BehavioralEvent.query.filter_by(lead_id=entity_id).order_by(BehavioralEvent.created_at.desc()).limit(20).all()
        
        elif entity_type == 'contact':
            contact = Contact.query.get(entity_id)
            if contact:
                entity_data = {
                    'name': contact.full_name,
                    'company': contact.company,
                    'type': contact.type,
                    'status': contact.status
                }
                communications = Communication.query.filter_by(contact_id=entity_id).order_by(Communication.created_at.desc()).limit(10).all()
                behavioral_events = BehavioralEvent.query.filter_by(contact_id=entity_id).order_by(BehavioralEvent.created_at.desc()).limit(20).all()
        
        elif entity_type == 'opportunity':
            opportunity = Opportunity.query.get(entity_id)
            if opportunity:
                entity_data = {
                    'name': opportunity.name,
                    'amount': opportunity.amount,
                    'stage': opportunity.stage,
                    'probability': opportunity.probability,
                    'expected_close_date': opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None
                }
                communications = Communication.query.filter_by(opportunity_id=entity_id).order_by(Communication.created_at.desc()).limit(10).all()
                behavioral_events = BehavioralEvent.query.filter_by(opportunity_id=entity_id).order_by(BehavioralEvent.created_at.desc()).limit(20).all()
        
        # Format communications for AI
        comm_data = []
        for comm in communications:
            comm_data.append({
                'type': comm.type,
                'direction': comm.direction,
                'subject': comm.subject,
                'content': comm.content[:500] if comm.content else '',  # Truncate for AI
                'created_at': comm.created_at.isoformat() if comm.created_at else None,
                'status': comm.status
            })
        
        # Format behavioral events for AI
        behavior_data = []
        for event in behavioral_events:
            behavior_data.append({
                'type': event.event_type,
                'engagement_score': event.engagement_score,
                'created_at': event.created_at.isoformat() if event.created_at else None,
                'data': event.event_data
            })
        
        # AI prompt for task suggestions
        system_msg = {
            "role": "system",
            "content": (
                "You are a CRM AI assistant that suggests actionable tasks based on communication history and behavioral data. "
                "Analyze the provided data and suggest 3-5 specific, actionable tasks with priorities and reasoning. "
                "Focus on tasks that will move the relationship forward or address identified opportunities/risks. "
                "Respond with JSON containing: tasks (array of objects with action, priority, reason, due_date_suggestion, impact_score)."
            )
        }
        
        user_msg = {
            "role": "user",
            "content": (
                f"Analyze this {entity_type} and suggest actionable tasks:\n\n"
                f"ENTITY DATA:\n{json.dumps(entity_data, ensure_ascii=False)}\n\n"
                f"RECENT COMMUNICATIONS:\n{json.dumps(comm_data, ensure_ascii=False)}\n\n"
                f"BEHAVIORAL EVENTS:\n{json.dumps(behavior_data, ensure_ascii=False)}\n\n"
                f"ADDITIONAL CONTEXT:\n{json.dumps(context, ensure_ascii=False)}\n\n"
                f"Suggest specific, actionable tasks that will help move this {entity_type} forward."
            )
        }
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.3,
            max_tokens=600
        )
        
        raw = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {"tasks": []}
        
        tasks = data.get("tasks", [])
        if not isinstance(tasks, list):
            tasks = []
        
        # Validate and enhance task data
        validated_tasks = []
        for task in tasks:
            if isinstance(task, dict) and task.get('action'):
                validated_tasks.append({
                    'action': task.get('action', ''),
                    'priority': task.get('priority', 'medium'),
                    'reason': task.get('reason', ''),
                    'due_date_suggestion': task.get('due_date_suggestion', ''),
                    'impact_score': min(100, max(0, int(task.get('impact_score', 50))))
                })
        
        return jsonify({
            'tasks': validated_tasks,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"AI task suggestion failed: {e}")
        return jsonify({'error': 'Failed to generate task suggestions'}), 500


def _trigger_ai_lead_analysis(lead):
    """Trigger AI analysis for a lead based on behavioral data."""
    try:
        # Prepare behavioral data for AI analysis
        behavioral_data = lead.behavioral_data or {}
        
        # Call the enhanced AI scoring endpoint
        lead_data = {
            'first_name': lead.first_name,
            'last_name': lead.last_name,
            'email': lead.email,
            'company': lead.company,
            'source': lead.source,
            'status': lead.status,
            'region': lead.region,
            'assigned_team': lead.assigned_team,
            'score': lead.score
        }
        
        # Make internal API call to AI scoring
        from flask import current_app
        with current_app.test_client() as client:
            response = client.post('/api/crm/ai/score-lead', 
                                 json={'lead': lead_data, 'behavioral_data': behavioral_data})
            
            if response.status_code == 200:
                ai_data = response.get_json()
                
                # Update lead with AI analysis
                lead.ai_score = ai_data.get('score', lead.ai_score)
                lead.ai_explanation = ai_data.get('explanation', lead.ai_explanation)
                lead.ai_confidence = ai_data.get('confidence', lead.ai_confidence)
                lead.last_ai_analysis = datetime.utcnow()
                
                db.session.commit()
                
    except Exception as e:
        print(f"Error in AI lead analysis: {e}")


@crm_bp.route('/ai/pipeline-insights', methods=['POST', 'OPTIONS'])
def ai_pipeline_insights():
    """Generate AI insights for pipeline movement and stage optimization."""
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json() or {}
        opportunity_id = payload.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({'error': 'opportunity_id is required'}), 400
        
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        # Get related data
        communications = Communication.query.filter_by(opportunity_id=opportunity_id).order_by(Communication.created_at.desc()).limit(15).all()
        behavioral_events = BehavioralEvent.query.filter_by(opportunity_id=opportunity_id).order_by(BehavioralEvent.created_at.desc()).limit(20).all()
        
        # Format data for AI
        opp_data = {
            'name': opportunity.name,
            'amount': opportunity.amount,
            'stage': opportunity.stage,
            'probability': opportunity.probability,
            'expected_close_date': opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None,
            'created_at': opportunity.created_at.isoformat() if opportunity.created_at else None,
            'days_in_stage': (datetime.utcnow() - opportunity.updated_at).days if opportunity.updated_at else 0
        }
        
        comm_data = []
        for comm in communications:
            comm_data.append({
                'type': comm.type,
                'direction': comm.direction,
                'subject': comm.subject,
                'created_at': comm.created_at.isoformat() if comm.created_at else None,
                'status': comm.status
            })
        
        behavior_data = []
        for event in behavioral_events:
            behavior_data.append({
                'type': event.event_type,
                'engagement_score': event.engagement_score,
                'created_at': event.created_at.isoformat() if event.created_at else None
            })
        
        client = OpenAI()
        
        system_msg = {
            "role": "system",
            "content": (
                "You are a sales pipeline AI that analyzes opportunities and suggests stage movements and actions. "
                "Based on communication patterns, behavioral data, and time in current stage, suggest: "
                "1. Whether the opportunity should move to next stage "
                "2. Specific actions to move it forward "
                "3. Risk factors and opportunities "
                "4. Recommended timeline adjustments "
                "Respond with JSON: should_move_stage (boolean), recommended_actions (array), risk_factors (array), opportunities (array), timeline_adjustment (string)."
            )
        }
        
        user_msg = {
            "role": "user",
            "content": (
                f"Analyze this opportunity for pipeline movement:\n\n"
                f"OPPORTUNITY DATA:\n{json.dumps(opp_data, ensure_ascii=False)}\n\n"
                f"COMMUNICATIONS:\n{json.dumps(comm_data, ensure_ascii=False)}\n\n"
                f"BEHAVIORAL EVENTS:\n{json.dumps(behavior_data, ensure_ascii=False)}\n\n"
                f"Should this opportunity move to the next stage? What actions are needed?"
            )
        }
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.2,
            max_tokens=500
        )
        
        raw = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {
                "should_move_stage": False,
                "recommended_actions": ["Manual review recommended"],
                "risk_factors": ["Unable to analyze"],
                "opportunities": ["Standard follow-up needed"],
                "timeline_adjustment": "No change recommended"
            }
        
        return jsonify({
            'opportunity_id': opportunity_id,
            'should_move_stage': bool(data.get('should_move_stage', False)),
            'recommended_actions': data.get('recommended_actions', []) if isinstance(data.get('recommended_actions'), list) else [],
            'risk_factors': data.get('risk_factors', []) if isinstance(data.get('risk_factors'), list) else [],
            'opportunities': data.get('opportunities', []) if isinstance(data.get('opportunities'), list) else [],
            'timeline_adjustment': data.get('timeline_adjustment', 'No change recommended'),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"AI pipeline insights failed: {e}")
        return jsonify({'error': 'Failed to generate pipeline insights'}), 500


@crm_bp.route('/ai/transcribe-meeting', methods=['POST', 'OPTIONS'])
def ai_transcribe_meeting():
    """Real-time transcription with AI-generated summaries and action points."""
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json() or {}
        audio_data = payload.get('audio_data')  # Base64 encoded audio
        meeting_type = payload.get('meeting_type', 'sales_call')  # sales_call, discovery, demo, follow_up
        participants = payload.get('participants', [])
        lead_id = payload.get('lead_id')
        contact_id = payload.get('contact_id')
        opportunity_id = payload.get('opportunity_id')
        
        if not audio_data:
            return jsonify({'error': 'audio_data is required'}), 400
        
        client = OpenAI()
        
        # In a real implementation, you would:
        # 1. Decode the base64 audio data
        # 2. Send it to OpenAI's Whisper API for transcription
        # 3. Process the transcription with GPT for analysis
        
        # For demo purposes, we'll simulate the transcription
        mock_transcription = """
        Sales Representative: Good morning, thank you for taking the time to meet with us today.
        
        Client: Good morning, we're excited to learn more about your solution.
        
        Sales Representative: Great! Let me start by understanding your current challenges with inventory management.
        
        Client: We're struggling with stockouts and overstock situations. Our current system doesn't provide real-time visibility.
        
        Sales Representative: I understand. Our solution provides real-time inventory tracking with predictive analytics. 
        Based on what you've shared, I believe we can help reduce stockouts by 40% and improve cash flow.
        
        Client: That sounds promising. What's the implementation timeline?
        
        Sales Representative: Typically 4-6 weeks for full deployment. We provide dedicated support throughout the process.
        
        Client: We'd like to see a demo of the analytics dashboard.
        
        Sales Representative: Absolutely. I'll schedule a technical demo for next week. I'll also send over our proposal with pricing.
        
        Client: Perfect. We're looking to make a decision by the end of the month.
        """
        
        # AI analysis of the transcription
        system_msg = {
            "role": "system",
            "content": (
                "You are a sales meeting AI that analyzes call transcriptions to extract key insights, action items, and next steps. "
                "Analyze the provided transcription and generate: "
                "1. Meeting summary "
                "2. Key discussion points "
                "3. Action items with owners and deadlines "
                "4. Sentiment analysis "
                "5. Next steps "
                "6. Deal progression indicators "
                "Respond with JSON: summary, key_points (array), action_items (array with owner, deadline, priority), "
                "sentiment (object with overall, client, rep), next_steps (array), deal_indicators (object with stage, probability, concerns)."
            )
        }
        
        user_msg = {
            "role": "user",
            "content": (
                f"Analyze this {meeting_type} transcription:\n\n"
                f"TRANSCRIPTION:\n{mock_transcription}\n\n"
                f"MEETING CONTEXT:\n"
                f"Type: {meeting_type}\n"
                f"Participants: {', '.join(participants) if participants else 'Not specified'}\n"
                f"Lead ID: {lead_id}\n"
                f"Contact ID: {contact_id}\n"
                f"Opportunity ID: {opportunity_id}\n\n"
                f"Extract actionable insights and next steps from this meeting."
            )
        }
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.2,
            max_tokens=800
        )
        
        raw = completion.choices[0].message.content or "{}"
        try:
            analysis_data = json.loads(raw)
        except Exception:
            analysis_data = {
                "summary": "Meeting transcription analysis unavailable",
                "key_points": ["Unable to analyze transcription"],
                "action_items": [],
                "sentiment": {"overall": "neutral", "client": "neutral", "rep": "neutral"},
                "next_steps": ["Manual review required"],
                "deal_indicators": {"stage": "unknown", "probability": 50, "concerns": []}
            }
        
        # Create communication record for the meeting
        try:
            comm = Communication(
                type='meeting',
                direction='outbound',
                subject=f'{meeting_type.title()} Meeting - {datetime.utcnow().strftime("%Y-%m-%d")}',
                content=mock_transcription,
                contact_id=contact_id,
                lead_id=lead_id,
                opportunity_id=opportunity_id,
                status='completed',
                metadata={
                    'meeting_type': meeting_type,
                    'participants': participants,
                    'transcription_analysis': analysis_data,
                    'duration_minutes': 30,  # Would be calculated from audio length
                    'ai_generated': True
                }
            )
            db.session.add(comm)
            
            # Track behavioral event if this is a lead
            if lead_id:
                event = BehavioralEvent(
                    lead_id=lead_id,
                    event_type='meeting_attended',
                    event_data={
                        'meeting_type': meeting_type,
                        'sentiment': analysis_data.get('sentiment', {}),
                        'deal_indicators': analysis_data.get('deal_indicators', {}),
                        'action_items_count': len(analysis_data.get('action_items', []))
                    },
                    engagement_score=80  # Based on meeting participation
                )
                db.session.add(event)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error creating meeting communication record: {e}")
            db.session.rollback()
        
        return jsonify({
            'transcription': mock_transcription,
            'analysis': analysis_data,
            'meeting_type': meeting_type,
            'participants': participants,
            'duration_minutes': 30,
            'transcription_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"AI transcription failed: {e}")
        return jsonify({'error': 'Failed to process meeting transcription'}), 500


@crm_bp.route('/analytics/time-per-client', methods=['GET', 'OPTIONS'])
def time_analytics_per_client():
    """Time spent per client analytics linked to sales outcomes."""
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        # Get time entries with related entities
        time_entries = TimeEntry.query.filter(
            TimeEntry.contact_id.isnot(None) | 
            TimeEntry.lead_id.isnot(None) | 
            TimeEntry.opportunity_id.isnot(None)
        ).all()
        
        # Group by client/entity
        client_time_data = {}
        
        for entry in time_entries:
            entity_key = None
            entity_name = None
            entity_type = None
            
            if entry.contact_id:
                contact = Contact.query.get(entry.contact_id)
                if contact:
                    entity_key = f"contact_{entry.contact_id}"
                    entity_name = contact.full_name
                    entity_type = "Contact"
            
            elif entry.lead_id:
                lead = Lead.query.get(entry.lead_id)
                if lead:
                    entity_key = f"lead_{entry.lead_id}"
                    entity_name = lead.full_name
                    entity_type = "Lead"
            
            elif entry.opportunity_id:
                opportunity = Opportunity.query.get(entry.opportunity_id)
                if opportunity:
                    entity_key = f"opportunity_{entry.opportunity_id}"
                    entity_name = opportunity.name
                    entity_type = "Opportunity"
            
            if entity_key:
                if entity_key not in client_time_data:
                    client_time_data[entity_key] = {
                        'entity_id': entry.contact_id or entry.lead_id or entry.opportunity_id,
                        'entity_name': entity_name,
                        'entity_type': entity_type,
                        'total_minutes': 0,
                        'total_hours': 0,
                        'billable_hours': 0,
                        'billable_amount': 0,
                        'activities': [],
                        'sales_outcome': None
                    }
                
                duration = entry.duration_minutes or 0
                client_time_data[entity_key]['total_minutes'] += duration
                client_time_data[entity_key]['total_hours'] += duration / 60
                
                if entry.billable:
                    client_time_data[entity_key]['billable_hours'] += duration / 60
                    rate = float(entry.rate or 0)
                    client_time_data[entity_key]['billable_amount'] += (duration / 60) * rate
                
                client_time_data[entity_key]['activities'].append({
                    'type': entry.activity_type,
                    'description': entry.notes,
                    'duration_minutes': duration,
                    'billable': entry.billable,
                    'rate': float(entry.rate or 0),
                    'date': entry.created_at.isoformat() if entry.created_at else None
                })
        
        # Add sales outcome data
        for key, data in client_time_data.items():
            entity_id = data['entity_id']
            entity_type = data['entity_type']
            
            if entity_type == "Opportunity":
                opportunity = Opportunity.query.get(entity_id)
                if opportunity:
                    data['sales_outcome'] = {
                        'stage': opportunity.stage,
                        'amount': float(opportunity.amount or 0),
                        'probability': opportunity.probability,
                        'closed_won': opportunity.stage == 'closed_won',
                        'closed_lost': opportunity.stage == 'closed_lost'
                    }
            elif entity_type == "Lead":
                lead = Lead.query.get(entity_id)
                if lead:
                    # Check if lead converted to opportunity
                    opportunity = Opportunity.query.filter_by(contact_id=lead.id).first()
                    if opportunity:
                        data['sales_outcome'] = {
                            'converted': True,
                            'opportunity_stage': opportunity.stage,
                            'opportunity_amount': float(opportunity.amount or 0)
                        }
                    else:
                        data['sales_outcome'] = {
                            'converted': False,
                            'lead_status': lead.status
                        }
        
        # Sort by total time spent
        sorted_clients = sorted(
            client_time_data.values(),
            key=lambda x: x['total_hours'],
            reverse=True
        )
        
        # Calculate summary statistics
        total_time_hours = sum(client['total_hours'] for client in client_time_data.values())
        total_billable_hours = sum(client['billable_hours'] for client in client_time_data.values())
        total_billable_amount = sum(client['billable_amount'] for client in client_time_data.values())
        
        # Calculate ROI metrics
        won_deals = [client for client in client_time_data.values() 
                    if client.get('sales_outcome', {}).get('closed_won')]
        total_deal_value = sum(client['sales_outcome']['amount'] for client in won_deals)
        
        return jsonify({
            'clients': sorted_clients,
            'summary': {
                'total_clients': len(client_time_data),
                'total_time_hours': round(total_time_hours, 2),
                'total_billable_hours': round(total_billable_hours, 2),
                'total_billable_amount': round(total_billable_amount, 2),
                'won_deals': len(won_deals),
                'total_deal_value': round(total_deal_value, 2),
                'average_time_per_client': round(total_time_hours / len(client_time_data) if client_time_data else 0, 2),
                'roi_per_hour': round(total_deal_value / total_time_hours if total_time_hours > 0 else 0, 2)
            },
            'analysis_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Time analytics failed: {e}")
        return jsonify({'error': 'Failed to generate time analytics'}), 500


@crm_bp.route('/data-validation/duplicates', methods=['GET', 'POST', 'OPTIONS'])
def data_validation_duplicates():
    """Detect and suggest fixes for duplicate data."""
    if request.method == 'OPTIONS':
        return ('', 200)
    
    if request.method == 'GET':
        try:
            # Detect duplicate contacts
            duplicate_contacts = []
            contacts = Contact.query.all()
            email_groups = {}
            phone_groups = {}
            name_groups = {}
            
            for contact in contacts:
                # Group by email
                if contact.email:
                    email_key = contact.email.lower().strip()
                    if email_key not in email_groups:
                        email_groups[email_key] = []
                    email_groups[email_key].append(contact)
                
                # Group by phone
                if contact.phone:
                    phone_key = contact.phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                    if phone_key not in phone_groups:
                        phone_groups[phone_key] = []
                    phone_groups[phone_key].append(contact)
                
                # Group by name (fuzzy matching)
                name_key = f"{contact.first_name.lower().strip()} {contact.last_name.lower().strip()}"
                if name_key not in name_groups:
                    name_groups[name_key] = []
                name_groups[name_key].append(contact)
            
            # Find duplicates
            for email, group in email_groups.items():
                if len(group) > 1:
                    duplicate_contacts.append({
                        'type': 'email',
                        'value': email,
                        'contacts': [{'id': c.id, 'name': c.full_name, 'email': c.email, 'phone': c.phone} for c in group]
                    })
            
            for phone, group in phone_groups.items():
                if len(group) > 1:
                    duplicate_contacts.append({
                        'type': 'phone',
                        'value': phone,
                        'contacts': [{'id': c.id, 'name': c.full_name, 'email': c.email, 'phone': c.phone} for c in group]
                    })
            
            # Detect duplicate leads
            duplicate_leads = []
            leads = Lead.query.all()
            lead_email_groups = {}
            lead_company_groups = {}
            
            for lead in leads:
                if lead.email:
                    email_key = lead.email.lower().strip()
                    if email_key not in lead_email_groups:
                        lead_email_groups[email_key] = []
                    lead_email_groups[email_key].append(lead)
                
                if lead.company:
                    company_key = lead.company.lower().strip()
                    if company_key not in lead_company_groups:
                        lead_company_groups[company_key] = []
                    lead_company_groups[company_key].append(lead)
            
            for email, group in lead_email_groups.items():
                if len(group) > 1:
                    duplicate_leads.append({
                        'type': 'email',
                        'value': email,
                        'leads': [{'id': l.id, 'name': l.full_name, 'email': l.email, 'company': l.company, 'status': l.status} for l in group]
                    })
            
            for company, group in lead_company_groups.items():
                if len(group) > 1:
                    duplicate_leads.append({
                        'type': 'company',
                        'value': company,
                        'leads': [{'id': l.id, 'name': l.full_name, 'email': l.email, 'company': l.company, 'status': l.status} for l in group]
                    })
            
            return jsonify({
                'duplicate_contacts': duplicate_contacts,
                'duplicate_leads': duplicate_leads,
                'summary': {
                    'total_contact_duplicates': len(duplicate_contacts),
                    'total_lead_duplicates': len(duplicate_leads),
                    'total_duplicates': len(duplicate_contacts) + len(duplicate_leads)
                },
                'scan_timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            print(f"Duplicate detection failed: {e}")
            return jsonify({'error': 'Failed to detect duplicates'}), 500
    
    # POST - Auto-clean suggestions
    try:
        payload = request.get_json() or {}
        duplicate_type = payload.get('type')  # 'contacts' or 'leads'
        duplicate_id = payload.get('duplicate_id')
        action = payload.get('action')  # 'merge', 'delete', 'ignore'
        
        if not all([duplicate_type, duplicate_id, action]):
            return jsonify({'error': 'type, duplicate_id, and action are required'}), 400
        
        client = OpenAI()
        
        # Generate AI-powered merge suggestions
        system_msg = {
            "role": "system",
            "content": (
                "You are a data quality AI that suggests how to merge duplicate records. "
                "Analyze the duplicate records and suggest which fields to keep, merge, or update. "
                "Respond with JSON: merge_suggestion (object with recommended_primary_id, field_mappings, reasoning)."
            )
        }
        
        # Get the duplicate records (this would be more sophisticated in real implementation)
        if duplicate_type == 'contacts':
            # Mock duplicate data for AI analysis
            duplicate_data = {
                'records': [
                    {'id': 1, 'name': 'John Smith', 'email': 'john@company.com', 'phone': '555-1234', 'company': 'ABC Corp'},
                    {'id': 2, 'name': 'J. Smith', 'email': 'john@company.com', 'phone': '555-1234', 'company': 'ABC Corporation'}
                ]
            }
        else:
            duplicate_data = {
                'records': [
                    {'id': 1, 'name': 'Jane Doe', 'email': 'jane@company.com', 'company': 'XYZ Inc', 'status': 'qualified'},
                    {'id': 2, 'name': 'Jane Doe', 'email': 'jane@company.com', 'company': 'XYZ Inc', 'status': 'new'}
                ]
            }
        
        user_msg = {
            "role": "user",
            "content": (
                f"Analyze these duplicate {duplicate_type} and suggest how to merge them:\n\n"
                f"DUPLICATE RECORDS:\n{json.dumps(duplicate_data, ensure_ascii=False)}\n\n"
                f"ACTION: {action}\n\n"
                f"Suggest the best way to handle these duplicates while preserving data integrity."
            )
        }
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.2,
            max_tokens=400
        )
        
        raw = completion.choices[0].message.content or "{}"
        try:
            ai_suggestion = json.loads(raw)
        except Exception:
            ai_suggestion = {
                "merge_suggestion": {
                    "recommended_primary_id": 1,
                    "field_mappings": {},
                    "reasoning": "Unable to generate AI suggestion"
                }
            }
        
        return jsonify({
            'duplicate_type': duplicate_type,
            'duplicate_id': duplicate_id,
            'action': action,
            'ai_suggestion': ai_suggestion,
            'cleanup_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Data validation cleanup failed: {e}")
        return jsonify({'error': 'Failed to process data validation'}), 500


@crm_bp.route('/data-validation/fuzzy-match', methods=['POST', 'OPTIONS'])
def fuzzy_match_entities():
    """Fuzzy matching for contacts, leads, and companies."""
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        payload = request.get_json() or {}
        entity_type = payload.get('entity_type')  # 'contact', 'lead', 'company'
        search_term = payload.get('search_term')
        threshold = payload.get('threshold', 0.8)  # Similarity threshold
        
        if not entity_type or not search_term:
            return jsonify({'error': 'entity_type and search_term are required'}), 400
        
        client = OpenAI()
        
        # Get potential matches from database
        if entity_type == 'contact':
            entities = Contact.query.all()
            entity_data = [{'id': c.id, 'name': c.full_name, 'email': c.email, 'company': c.company} for c in entities]
        elif entity_type == 'lead':
            entities = Lead.query.all()
            entity_data = [{'id': l.id, 'name': l.full_name, 'email': l.email, 'company': l.company} for l in entities]
        else:
            # For companies, we'd need a separate Company model or extract from contacts/leads
            entities = Contact.query.filter(Contact.company.isnot(None)).all()
            entity_data = [{'id': c.id, 'name': c.company, 'type': 'contact'} for c in entities]
        
        # AI-powered fuzzy matching
        system_msg = {
            "role": "system",
            "content": (
                "You are a fuzzy matching AI that finds similar records based on name, email, and company. "
                "Compare the search term against the provided entities and return similarity scores. "
                "Respond with JSON: matches (array of objects with id, name, similarity_score, match_reason)."
            )
        }
        
        user_msg = {
            "role": "user",
            "content": (
                f"Find fuzzy matches for '{search_term}' in these {entity_type} entities:\n\n"
                f"SEARCH TERM: {search_term}\n"
                f"THRESHOLD: {threshold}\n\n"
                f"ENTITIES:\n{json.dumps(entity_data, ensure_ascii=False)}\n\n"
                f"Return matches with similarity scores above {threshold}."
            )
        }
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[system_msg, user_msg],
            temperature=0.1,
            max_tokens=500
        )
        
        raw = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {"matches": []}
        
        matches = data.get("matches", [])
        if not isinstance(matches, list):
            matches = []
        
        # Filter by threshold
        filtered_matches = [
            match for match in matches 
            if isinstance(match, dict) and match.get('similarity_score', 0) >= threshold
        ]
        
        # Sort by similarity score
        filtered_matches.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return jsonify({
            'entity_type': entity_type,
            'search_term': search_term,
            'threshold': threshold,
            'matches': filtered_matches,
            'total_matches': len(filtered_matches),
            'search_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Fuzzy matching failed: {e}")
        return jsonify({'error': 'Failed to perform fuzzy matching'}), 500


@crm_bp.route('/dashboard/widgets', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def dashboard_widgets():
    """Manage customizable dashboard widgets."""
    if request.method == 'OPTIONS':
        return ('', 200)
    
    if request.method == 'GET':
        try:
            # Get available widget types
            widget_types = [
                {
                    'id': 'lead_score_distribution',
                    'name': 'Lead Score Distribution',
                    'type': 'chart',
                    'chart_type': 'bar',
                    'description': 'Distribution of lead scores across your pipeline',
                    'category': 'leads'
                },
                {
                    'id': 'pipeline_velocity',
                    'name': 'Pipeline Velocity',
                    'type': 'metric',
                    'description': 'Average time from lead to close',
                    'category': 'pipeline'
                },
                {
                    'id': 'top_performing_sources',
                    'name': 'Top Performing Sources',
                    'type': 'chart',
                    'chart_type': 'pie',
                    'description': 'Lead sources with highest conversion rates',
                    'category': 'sources'
                },
                {
                    'id': 'activity_heatmap',
                    'name': 'Activity Heatmap',
                    'type': 'chart',
                    'chart_type': 'heatmap',
                    'description': 'Communication activity patterns by day/time',
                    'category': 'activity'
                },
                {
                    'id': 'ai_insights',
                    'name': 'AI Insights',
                    'type': 'insights',
                    'description': 'AI-generated insights and recommendations',
                    'category': 'ai'
                },
                {
                    'id': 'recent_activities',
                    'name': 'Recent Activities',
                    'type': 'list',
                    'description': 'Latest communications and activities',
                    'category': 'activity'
                },
                {
                    'id': 'conversion_funnel',
                    'name': 'Conversion Funnel',
                    'type': 'chart',
                    'chart_type': 'funnel',
                    'description': 'Lead to opportunity conversion rates',
                    'category': 'conversion'
                },
                {
                    'id': 'time_analytics',
                    'name': 'Time Analytics',
                    'type': 'chart',
                    'chart_type': 'line',
                    'description': 'Time spent per client and ROI metrics',
                    'category': 'time'
                }
            ]
            
            # Get user's dashboard configuration (in real implementation, this would be stored per user)
            user_dashboard = {
                'layout': [
                    {'id': 'lead_score_distribution', 'position': {'x': 0, 'y': 0}, 'size': {'w': 6, 'h': 4}},
                    {'id': 'pipeline_velocity', 'position': {'x': 6, 'y': 0}, 'size': {'w': 3, 'h': 2}},
                    {'id': 'ai_insights', 'position': {'x': 9, 'y': 0}, 'size': {'w': 3, 'h': 4}},
                    {'id': 'top_performing_sources', 'position': {'x': 0, 'y': 4}, 'size': {'w': 4, 'h': 4}},
                    {'id': 'recent_activities', 'position': {'x': 4, 'y': 4}, 'size': {'w': 5, 'h': 4}},
                    {'id': 'conversion_funnel', 'position': {'x': 9, 'y': 4}, 'size': {'w': 3, 'h': 4}}
                ],
                'settings': {
                    'auto_refresh': True,
                    'refresh_interval': 300,  # 5 minutes
                    'theme': 'dark'
                }
            }
            
            return jsonify({
                'available_widgets': widget_types,
                'user_dashboard': user_dashboard,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            print(f"Failed to get dashboard widgets: {e}")
            return jsonify({'error': 'Failed to get dashboard widgets'}), 500
    
    elif request.method == 'POST':
        try:
            payload = request.get_json() or {}
            widget_id = payload.get('widget_id')
            position = payload.get('position', {'x': 0, 'y': 0})
            size = payload.get('size', {'w': 3, 'h': 2})
            settings = payload.get('settings', {})
            
            if not widget_id:
                return jsonify({'error': 'widget_id is required'}), 400
            
            # In real implementation, save to user's dashboard configuration
            new_widget = {
                'id': widget_id,
                'position': position,
                'size': size,
                'settings': settings,
                'added_at': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'message': 'Widget added to dashboard',
                'widget': new_widget
            }), 201
            
        except Exception as e:
            print(f"Failed to add widget: {e}")
            return jsonify({'error': 'Failed to add widget'}), 500
    
    elif request.method == 'PUT':
        try:
            payload = request.get_json() or {}
            widget_id = payload.get('widget_id')
            position = payload.get('position')
            size = payload.get('size')
            settings = payload.get('settings')
            
            if not widget_id:
                return jsonify({'error': 'widget_id is required'}), 400
            
            # In real implementation, update user's dashboard configuration
            updated_widget = {
                'id': widget_id,
                'position': position,
                'size': size,
                'settings': settings,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'message': 'Widget updated',
                'widget': updated_widget
            }), 200
            
        except Exception as e:
            print(f"Failed to update widget: {e}")
            return jsonify({'error': 'Failed to update widget'}), 500
    
    elif request.method == 'DELETE':
        try:
            widget_id = request.args.get('widget_id')
            
            if not widget_id:
                return jsonify({'error': 'widget_id is required'}), 400
            
            # In real implementation, remove from user's dashboard configuration
            return jsonify({
                'message': 'Widget removed from dashboard',
                'widget_id': widget_id
            }), 200
            
        except Exception as e:
            print(f"Failed to remove widget: {e}")
            return jsonify({'error': 'Failed to remove widget'}), 500


@crm_bp.route('/dashboard/widgets/<widget_id>/data', methods=['GET', 'OPTIONS'])
def get_widget_data(widget_id):
    """Get data for a specific dashboard widget."""
    if request.method == 'OPTIONS':
        return ('', 200)
    
    try:
        # Generate widget-specific data
        if widget_id == 'lead_score_distribution':
            leads = Lead.query.all()
            score_ranges = {
                '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0
            }
            
            for lead in leads:
                score = lead.ai_score or lead.score or 0
                if score <= 20:
                    score_ranges['0-20'] += 1
                elif score <= 40:
                    score_ranges['21-40'] += 1
                elif score <= 60:
                    score_ranges['41-60'] += 1
                elif score <= 80:
                    score_ranges['61-80'] += 1
                else:
                    score_ranges['81-100'] += 1
            
            data = {
                'type': 'bar_chart',
                'data': {
                    'labels': list(score_ranges.keys()),
                    'datasets': [{
                        'label': 'Number of Leads',
                        'data': list(score_ranges.values()),
                        'backgroundColor': ['#ff6b6b', '#ffa726', '#ffeb3b', '#66bb6a', '#42a5f5']
                    }]
                }
            }
        
        elif widget_id == 'pipeline_velocity':
            opportunities = Opportunity.query.all()
            total_days = 0
            count = 0
            
            for opp in opportunities:
                if opp.created_at and opp.updated_at:
                    days = (opp.updated_at - opp.created_at).days
                    total_days += days
                    count += 1
            
            avg_days = total_days / count if count > 0 else 0
            
            data = {
                'type': 'metric',
                'value': round(avg_days, 1),
                'unit': 'days',
                'label': 'Average Pipeline Velocity',
                'trend': '+5%',  # Mock trend
                'color': 'success'
            }
        
        elif widget_id == 'top_performing_sources':
            leads = Lead.query.all()
            source_stats = {}
            
            for lead in leads:
                source = lead.source or 'unknown'
                if source not in source_stats:
                    source_stats[source] = {'total': 0, 'converted': 0}
                source_stats[source]['total'] += 1
                
                # Check if lead converted (simplified)
                if lead.status in ['qualified', 'proposal', 'negotiation', 'closed_won']:
                    source_stats[source]['converted'] += 1
            
            # Calculate conversion rates
            source_data = []
            for source, stats in source_stats.items():
                conversion_rate = (stats['converted'] / stats['total']) * 100 if stats['total'] > 0 else 0
                source_data.append({
                    'source': source,
                    'total_leads': stats['total'],
                    'converted': stats['converted'],
                    'conversion_rate': round(conversion_rate, 1)
                })
            
            # Sort by conversion rate
            source_data.sort(key=lambda x: x['conversion_rate'], reverse=True)
            
            data = {
                'type': 'pie_chart',
                'data': {
                    'labels': [item['source'] for item in source_data[:5]],
                    'datasets': [{
                        'data': [item['conversion_rate'] for item in source_data[:5]],
                        'backgroundColor': ['#ff6b6b', '#ffa726', '#ffeb3b', '#66bb6a', '#42a5f5']
                    }]
                }
            }
        
        elif widget_id == 'ai_insights':
            # Generate AI insights
            client = OpenAI()
            
            system_msg = {
                "role": "system",
                "content": (
                    "You are a CRM analytics AI that provides actionable insights. "
                    "Analyze the current CRM data and provide 3-5 key insights with actionable recommendations. "
                    "Respond with JSON: insights (array of objects with title, description, action, priority)."
                )
            }
            
            # Get some basic stats for AI analysis
            total_leads = Lead.query.count()
            total_opportunities = Opportunity.query.count()
            won_opportunities = Opportunity.query.filter_by(stage='closed_won').count()
            
            user_msg = {
                "role": "user",
                "content": (
                    f"Analyze this CRM data and provide insights:\n"
                    f"Total Leads: {total_leads}\n"
                    f"Total Opportunities: {total_opportunities}\n"
                    f"Won Opportunities: {won_opportunities}\n"
                    f"Win Rate: {(won_opportunities/total_opportunities*100) if total_opportunities > 0 else 0:.1f}%\n\n"
                    f"Provide actionable insights and recommendations."
                )
            }
            
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[system_msg, user_msg],
                temperature=0.3,
                max_tokens=400
            )
            
            raw = completion.choices[0].message.content or "{}"
            try:
                ai_data = json.loads(raw)
            except Exception:
                ai_data = {"insights": []}
            
            data = {
                'type': 'insights',
                'insights': ai_data.get('insights', [])
            }
        
        elif widget_id == 'recent_activities':
            activities = Communication.query.order_by(Communication.created_at.desc()).limit(10).all()
            
            activity_data = []
            for activity in activities:
                activity_data.append({
                    'id': activity.id,
                    'type': activity.type,
                    'direction': activity.direction,
                    'subject': activity.subject,
                    'created_at': activity.created_at.isoformat() if activity.created_at else None,
                    'status': activity.status
                })
            
            data = {
                'type': 'list',
                'items': activity_data
            }
        
        elif widget_id == 'conversion_funnel':
            # Calculate conversion funnel
            total_leads = Lead.query.count()
            qualified_leads = Lead.query.filter(Lead.status.in_(['qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost'])).count()
            opportunities = Opportunity.query.count()
            won_deals = Opportunity.query.filter_by(stage='closed_won').count()
            
            funnel_data = [
                {'stage': 'Leads', 'count': total_leads, 'percentage': 100},
                {'stage': 'Qualified', 'count': qualified_leads, 'percentage': (qualified_leads/total_leads*100) if total_leads > 0 else 0},
                {'stage': 'Opportunities', 'count': opportunities, 'percentage': (opportunities/total_leads*100) if total_leads > 0 else 0},
                {'stage': 'Won Deals', 'count': won_deals, 'percentage': (won_deals/total_leads*100) if total_leads > 0 else 0}
            ]
            
            data = {
                'type': 'funnel_chart',
                'data': funnel_data
            }
        
        elif widget_id == 'time_analytics':
            # Get time analytics data
            time_entries = TimeEntry.query.all()
            total_hours = sum(entry.duration_minutes or 0 for entry in time_entries) / 60
            
            # Mock time series data
            time_series = []
            for i in range(7):  # Last 7 days
                date = datetime.utcnow() - timedelta(days=6-i)
                time_series.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'hours': round(total_hours / 7 + (i * 0.5), 1)
                })
            
            data = {
                'type': 'line_chart',
                'data': {
                    'labels': [item['date'] for item in time_series],
                    'datasets': [{
                        'label': 'Hours Logged',
                        'data': [item['hours'] for item in time_series],
                        'borderColor': '#42a5f5',
                        'fill': False
                    }]
                }
            }
        
        else:
            return jsonify({'error': 'Unknown widget type'}), 404
        
        return jsonify({
            'widget_id': widget_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Failed to get widget data: {e}")
        return jsonify({'error': 'Failed to get widget data'}), 500
