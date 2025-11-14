"""Classification route handlers"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.services.model_service import get_classifier
from app.services.watsonx_service import get_watsonx_service
from app.utils.logger import logger

router = APIRouter(prefix="/classify", tags=["classification"])
logger = logging.getLogger(__name__)


class TicketRequest(BaseModel):
    """Request model for ticket classification"""
    text: str = Field(..., description="The ticket text to classify")
    include_suggestion: bool = Field(False, description="Whether to include AI-generated reply suggestion")
    include_summary: bool = Field(False, description="Whether to include ticket summary")


class ClassificationResponse(BaseModel):
    """Response model for classification"""
    category: str
    confidence: float
    scores: dict
    model: str
    suggestion: Optional[str] = None
    summary: Optional[str] = None


@router.post("", response_model=ClassificationResponse)
async def classify_ticket(request: TicketRequest):
    """
    Classify a support ticket into categories
    
    - **text**: The ticket content to classify
    - **include_suggestion**: Optionally generate a suggested reply
    - **include_summary**: Optionally generate a ticket summary
    """
    try:
        # Get classifier
        classifier = get_classifier()
        
        # Classify ticket
        classification = classifier.classify(request.text)
        
        response_data = {
            "category": classification["category"],
            "confidence": classification["confidence"],
            "scores": classification["scores"],
            "model": classification["model"]
        }
        
        # Optionally generate AI suggestions
        if request.include_suggestion or request.include_summary:
            watsonx = get_watsonx_service()
            
            if request.include_suggestion:
                suggestion_result = watsonx.suggest_reply(
                    request.text,
                    classification["category"]
                )
                response_data["suggestion"] = suggestion_result.get("text", "")
            
            if request.include_summary:
                summary_result = watsonx.summarize_ticket(request.text)
                response_data["summary"] = summary_result.get("text", "")
        
        logger.info(f"Classified ticket as '{classification['category']}'")
        return ClassificationResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error classifying ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

