"""IBM watsonx.ai service for LLM inference and response generation"""

from typing import Dict, Optional
import logging

from app.utils.config import settings
from app.utils.logger import logger

logger = logging.getLogger(__name__)


class WatsonXService:
    """Service for interacting with IBM watsonx.ai"""
    
    def __init__(self):
        self.api_key = settings.WATSONX_API_KEY
        self.url = settings.WATSONX_URL
        self.project_id = settings.WATSONX_PROJECT_ID
        self.model_id = settings.WATSONX_MODEL_ID
        
        self.available = False
        if self.api_key and self.project_id:
            try:
                # Import watsonx SDK
                from ibm_watson_machine_learning.foundation_models import Model
                from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
                from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes, DecodingMethods
                
                self.gen_params = GenParams
                self.model_types = ModelTypes
                self.decoding_methods = DecodingMethods
                self.Model = Model
                
                # Initialize model
                credentials = {
                    "url": self.url,
                    "apikey": self.api_key
                }
                
                self.model = Model(
                    model_id=self.model_id,
                    credentials=credentials,
                    project_id=self.project_id,
                    params={
                        GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
                        GenParams.MAX_NEW_TOKENS: 200,
                        GenParams.TEMPERATURE: 0.7
                    }
                )
                
                logger.info("watsonx.ai service initialized successfully")
                self.available = True
            except ImportError:
                logger.warning("watsonx SDK not installed. Install with: pip install ibm-watson-machine-learning")
                self.available = False
            except Exception as e:
                logger.error(f"Error initializing watsonx service: {e}")
                self.available = False
        else:
            logger.warning("watsonx.ai credentials not configured. Using mock mode.")
            self.available = False
    
    def generate_response(self, prompt: str, max_tokens: int = 200) -> Dict:
        """
        Generate a response using watsonx.ai
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with generated text
        """
        if not self.available:
            logger.warning("watsonx not available, returning mock response")
            return self._generate_mock_response(prompt)
        
        try:
            response = self.model.generate(prompt, max_new_tokens=max_tokens)
            generated_text = response.get('results', [{}])[0].get('generated_text', '')
            
            logger.info("Generated response from watsonx.ai")
            return {
                "success": True,
                "text": generated_text,
                "model": self.model_id
            }
        except Exception as e:
            logger.error(f"Error generating response with watsonx: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": self._generate_mock_response(prompt)["text"]
            }
    
    def suggest_reply(self, ticket_text: str, category: str) -> Dict:
        """
        Generate a suggested reply for a support ticket
        
        Args:
            ticket_text: The ticket content
            category: The classified category
            
        Returns:
            Dictionary with suggested reply
        """
        prompt = f"""You are a helpful support agent. Generate a professional and empathetic response to this {category} support ticket.

Ticket:
{ticket_text}

Response:"""
        
        return self.generate_response(prompt, max_tokens=300)
    
    def summarize_ticket(self, ticket_text: str) -> Dict:
        """
        Generate a summary of the support ticket
        
        Args:
            ticket_text: The ticket content
            
        Returns:
            Dictionary with ticket summary
        """
        prompt = f"""Summarize this support ticket in 2-3 sentences, highlighting the key issue and urgency.

Ticket:
{ticket_text}

Summary:"""
        
        return self.generate_response(prompt, max_tokens=150)
    
    def _generate_mock_response(self, prompt: str) -> Dict:
        """Generate a mock response for testing"""
        # Simple mock that returns a generic response
        if "suggest" in prompt.lower() or "response" in prompt.lower():
            mock_text = "Thank you for contacting us. We understand your concern and will look into this matter promptly. Our team will get back to you within 24 hours."
        elif "summar" in prompt.lower():
            mock_text = "Customer experiencing issue with service. Requires immediate attention from support team."
        else:
            mock_text = "This is a mock response. Please configure watsonx.ai credentials for actual AI-generated responses."
        
        return {
            "success": True,
            "text": mock_text,
            "model": "mock",
            "mock": True
        }


# Global service instance
_watsonx_service_instance = None


def get_watsonx_service() -> WatsonXService:
    """Get or create the global watsonx service instance"""
    global _watsonx_service_instance
    if _watsonx_service_instance is None:
        _watsonx_service_instance = WatsonXService()
    return _watsonx_service_instance

