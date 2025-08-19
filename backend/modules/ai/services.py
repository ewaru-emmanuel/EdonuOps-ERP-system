"""
AI Services for EdonuOps
Handles all AI-related functionality including OpenAI integration
"""

import os
import openai
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Secure AI service for EdonuOps"""
    
    def __init__(self):
        """Initialize AI service with secure API key loading"""
        self.api_key = self._load_api_key()
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OpenAI API key not found. AI features will be disabled.")
    
    def _load_api_key(self) -> Optional[str]:
        """Securely load API key from environment variables"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY not found in environment variables")
                return None
            return api_key
        except Exception as e:
            logger.error(f"Error loading API key: {e}")
            return None
    
    def generate_response(self, prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Generate AI response with error handling"""
        if not self.api_key:
            return {
                "error": "AI service not configured",
                "message": "OpenAI API key not available. Please configure the API key in your environment variables."
            }
        
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": model,
                "usage": response.usage
            }
            
        except openai.error.AuthenticationError:
            return {
                "error": "Authentication failed",
                "message": "Invalid API key. Please check your OpenAI API key configuration."
            }
        except openai.error.RateLimitError:
            return {
                "error": "Rate limit exceeded",
                "message": "API rate limit exceeded. Please try again later."
            }
        except openai.error.APIError as e:
            return {
                "error": "API error",
                "message": f"OpenAI API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {e}")
            return {
                "error": "Service error",
                "message": "An unexpected error occurred. Please try again."
            }
    
    def analyze_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data using AI"""
        prompt = f"""
        Analyze the following financial data and provide insights:
        
        Data: {data}
        
        Please provide:
        1. Key trends and patterns
        2. Potential risks or concerns
        3. Recommendations for improvement
        4. Summary of financial health
        """
        
        return self.generate_response(prompt)
    
    def generate_report(self, report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered reports"""
        prompt = f"""
        Generate a professional {report_type} report based on the following data:
        
        Data: {data}
        
        Please provide a well-structured report with:
        1. Executive summary
        2. Key findings
        3. Detailed analysis
        4. Recommendations
        5. Conclusion
        """
        
        return self.generate_response(prompt)
    
    def predict_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict trends based on historical data"""
        prompt = f"""
        Analyze the following historical data and predict future trends:
        
        Historical Data: {historical_data}
        
        Please provide:
        1. Trend analysis
        2. Future predictions
        3. Confidence levels
        4. Factors influencing trends
        5. Recommendations
        """
        
        return self.generate_response(prompt)
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.api_key is not None

# Global AI service instance
ai_service = AIService()
