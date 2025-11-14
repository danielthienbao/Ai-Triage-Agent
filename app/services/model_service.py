"""Hugging Face Transformer model service for ticket classification"""

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

from typing import Dict, List, Tuple
import logging
import re

from app.utils.config import settings
from app.utils.logger import logger

logger = logging.getLogger(__name__)


class TicketClassifier:
    """BERT-based ticket classifier"""
    
    # Predefined categories for support tickets
    CATEGORIES = [
        "billing",
        "technical",
        "access",
        "general",
        "bug_report",
        "feature_request"
    ]
    
    def __init__(self):
        self.model_name = settings.MODEL_NAME
        self.tokenizer = None
        self.model = None
        self.device = None
        self.use_mock = not TORCH_AVAILABLE
        
        if TORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._load_model()
        else:
            logger.warning("PyTorch not available. Using mock classification mode.")
            self.model_name = "mock-classifier"
    
    def _load_model(self):
        """Load the transformer model and tokenizer"""
        if not TORCH_AVAILABLE:
            return
            
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            
            # For classification, we'll use a simple approach with a base model
            # In production, you'd fine-tune this on your ticket data
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=len(self.CATEGORIES),
                cache_dir=settings.MODEL_CACHE_DIR
            )
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.warning("Falling back to mock classification mode")
            self.use_mock = True
    
    def _classify_mock(self, ticket_text: str) -> Dict[str, any]:
        """Mock classification using keyword matching"""
        text_lower = ticket_text.lower()
        
        # Simple keyword-based classification
        keywords = {
            "billing": ["payment", "invoice", "billing", "charge", "refund", "subscription", "price", "cost"],
            "technical": ["error", "bug", "crash", "not working", "broken", "issue", "problem", "technical"],
            "access": ["login", "password", "access", "account", "permission", "unauthorized", "locked"],
            "bug_report": ["bug", "error", "crash", "broken", "defect"],
            "feature_request": ["feature", "request", "suggestion", "improvement", "enhancement", "add"],
            "general": []
        }
        
        scores = {}
        for category in self.CATEGORIES:
            score = 0.0
            if category in keywords:
                for keyword in keywords[category]:
                    if keyword in text_lower:
                        score += 0.3
            scores[category] = min(score, 1.0)
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            scores["general"] = 1.0
        
        top_category = max(scores.items(), key=lambda x: x[1])[0]
        confidence = scores[top_category]
        
        return {
            "category": top_category,
            "confidence": confidence,
            "scores": scores,
            "model": "mock-classifier"
        }
    
    def classify(self, ticket_text: str) -> Dict[str, any]:
        """
        Classify a support ticket into categories
        
        Args:
            ticket_text: The ticket content to classify
            
        Returns:
            Dictionary with category, confidence, and all scores
        """
        if self.use_mock or not TORCH_AVAILABLE:
            return self._classify_mock(ticket_text)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                ticket_text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get top category
            scores = probabilities[0].cpu().numpy()
            top_idx = scores.argmax()
            top_category = self.CATEGORIES[top_idx]
            confidence = float(scores[top_idx])
            
            # Create category scores dictionary
            category_scores = {
                self.CATEGORIES[i]: float(scores[i])
                for i in range(len(self.CATEGORIES))
            }
            
            result = {
                "category": top_category,
                "confidence": confidence,
                "scores": category_scores,
                "model": self.model_name
            }
            
            logger.info(f"Classified ticket as '{top_category}' with confidence {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error classifying ticket: {e}")
            # Fallback to mock classification
            return self._classify_mock(ticket_text)
    
    def classify_batch(self, ticket_texts: List[str]) -> List[Dict[str, any]]:
        """Classify multiple tickets at once"""
        return [self.classify(text) for text in ticket_texts]


# Global classifier instance
_classifier_instance = None


def get_classifier() -> TicketClassifier:
    """Get or create the global classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TicketClassifier()
    return _classifier_instance

