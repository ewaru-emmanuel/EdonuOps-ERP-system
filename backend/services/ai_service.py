import openai
import logging
import json
from app import db
from config import Config
from datetime import datetime, timedelta
from typing import List, Dict
from modules.finance.models import (
    ChartOfAccount,
    JournalHeader, 
    JournalLine,
    Budget
)


logger = logging.getLogger(__name__)

class AISuggestionService:
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY
        openai.api_key = self.openai_api_key


    def get_account_suggestions(self, description: str, amount: float, existing_lines: List[Dict] = None) -> List[Dict]:
        """
        Get AI-powered account suggestions for a journal line
        """
        try:
            prompt = self._build_prompt(description, amount, existing_lines)
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3
            )
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"AI suggestion failed: {str(e)}")
            return []

    def detect_anomalies(self, entry_id: int) -> Dict:
        """
        Detect unusual patterns in journal entries
        """
        entry = JournalHeader.query.get(entry_id)
        if not entry:
            return {"error": "Entry not found"}

        historical_data = self._get_historical_data(entry.entity)
        prompt = self._build_anomaly_prompt(entry, historical_data)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.2
            )
            return {
                "entry_id": entry_id,
                "analysis": response.choices[0].message.content,
                "risk_score": self._extract_risk_score(response.choices[0].message.content)
            }
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return {"error": str(e)}

    def _build_prompt(self, description: str, amount: float, existing_lines: List[Dict] = None) -> str:
        accounts = ChartOfAccount.query.filter_by(is_active=True).all()
        account_list = "\n".join([f"{a.code} - {a.account_name} ({a.account_type})" for a in accounts])
        
        context = ""
        if existing_lines:
            context = "Existing lines in this journal:\n" + "\n".join(
                f"{l['account_code']} - {l['account_name']}: {'Debit' if l['debit_amount'] else 'Credit'} {l['debit_amount'] or l['credit_amount']}"
                for l in existing_lines
            )

        return f"""You are an expert accounting assistant. Suggest the most appropriate accounts for:
Description: {description}
Amount: {amount}
{context}

Available Accounts:
{account_list}

Return suggestions as JSON format:
{{
    "suggestions": [
        {{
            "account_code": "1000",
            "account_name": "Cash",
            "confidence": 0.95,
            "reason": "This is typically used for cash transactions",
            "debit_credit": "debit" // or "credit"
        }}
    ]
}}"""

    def _parse_response(self, response_text: str) -> List[Dict]:
        try:
            import json
            data = json.loads(response_text.strip())
            return data.get("suggestions", [])
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return []

    def _build_anomaly_prompt(self, entry: JournalHeader, historical_data: List[Dict]) -> str:
        entry_summary = f"""
Journal Entry {entry.id}:
Date: {entry.doc_date}
Period: {entry.period}
Entity: {entry.entity}
Lines:
""" + "\n".join(
    f"- {line.account.code} {line.account.account_name}: "
    f"Debit {line.debit_amount if line.debit_amount else '0'}, "
    f"Credit {line.credit_amount if line.credit_amount else '0'}"
    for line in entry.lines
)

        return f"""Analyze this accounting entry for anomalies:

{entry_summary}

Historical Patterns (last 90 days):
{historical_data}

Check for:
1. Unusual amounts compared to historical patterns
2. Suspicious account combinations
3. Round-number transactions
4. After-hours postings
5. Unapproved account usage

Return analysis in this format:
{{
    "risk_score": 0-100,
    "findings": [
        {{
            "type": "unusual_amount",
            "description": "This amount is 300% higher than average",
            "account_codes": ["1000"],
            "severity": "high"
        }}
    ],
    "recommendations": ["Review with department head"]
}}"""

    def _get_historical_data(self, entity: str) -> List[Dict]:
        date_cutoff = datetime.utcnow() - timedelta(days=90)
        entries = JournalHeader.query.filter(
            JournalHeader.entity == entity,
            JournalHeader.doc_date >= date_cutoff,
            JournalHeader.status == "posted"
        ).all()

        return [{
            "date": e.doc_date.isoformat(),
            "total_amount": sum(
                line.debit_amount or line.credit_amount 
                for line in e.lines
            )
        } for e in entries]