"""Routing route handlers"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.services.model_service import get_classifier
from app.services.jira_service import get_jira_service
from app.services.slack_service import get_slack_service
from app.services.gmail_service import get_gmail_service
from app.utils.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/route", tags=["routing"])
logger = logging.getLogger(__name__)


class RouteRequest(BaseModel):
    """Request model for ticket routing"""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    text: str = Field(..., description="The ticket text to route")
    subject: Optional[str] = Field(None, description="Ticket subject")
    from_email: Optional[str] = Field(None, description="Sender email address")
    create_jira: bool = Field(True, description="Whether to create Jira issue")
    send_slack: bool = Field(True, description="Whether to send Slack notification")


class RouteResponse(BaseModel):
    """Response model for routing"""
    ticket_id: str
    category: str
    confidence: float
    jira_issue: Optional[dict] = None
    slack_message: Optional[dict] = None
    routing_config: dict


@router.post("", response_model=RouteResponse)
async def route_ticket(request: RouteRequest):
    """
    Classify and route a support ticket
    
    This endpoint:
    1. Classifies the ticket using AI
    2. Creates a Jira issue (if enabled)
    3. Sends a Slack notification (if enabled)
    
    - **ticket_id**: Unique identifier for the ticket
    - **text**: The ticket content
    - **subject**: Optional ticket subject
    - **from_email**: Optional sender email
    - **create_jira**: Whether to create Jira issue
    - **send_slack**: Whether to send Slack notification
    """
    try:
        # Classify ticket
        classifier = get_classifier()
        classification = classifier.classify(request.text)
        category = classification["category"]
        confidence = classification["confidence"]
        
        # Get routing configuration
        routing_config = settings.CATEGORY_ROUTING.get(category, {
            "jira_priority": "Medium",
            "slack_channel": settings.SLACK_CHANNEL_ID
        })
        
        response_data = {
            "ticket_id": request.ticket_id,
            "category": category,
            "confidence": confidence,
            "routing_config": routing_config
        }
        
        # Create Jira issue
        jira_issue = None
        if request.create_jira:
            jira_service = get_jira_service()
            summary = request.subject or f"{category.title()} Ticket: {request.ticket_id}"
            description = f"Ticket ID: {request.ticket_id}\n\n{request.text}"
            if request.from_email:
                description += f"\n\nFrom: {request.from_email}"
            
            jira_issue = jira_service.create_issue(
                summary=summary,
                description=description,
                issue_type="Task",
                priority=routing_config.get("jira_priority", "Medium"),
                labels=[category, "ai-triaged"]
            )
            response_data["jira_issue"] = jira_issue
        
        # Send Slack notification
        slack_message = None
        if request.send_slack:
            slack_service = get_slack_service()
            summary = request.subject or f"Ticket {request.ticket_id}"
            jira_key = jira_issue.get("issue_key") if jira_issue and jira_issue.get("success") else None
            
            slack_message = slack_service.send_ticket_notification(
                ticket_id=request.ticket_id,
                category=category,
                summary=summary,
                jira_key=jira_key
            )
            response_data["slack_message"] = slack_message
        
        logger.info(f"Routed ticket {request.ticket_id} as '{category}'")
        return RouteResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error routing ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")


@router.post("/batch")
async def route_tickets_batch(tickets: list[RouteRequest]):
    """
    Route multiple tickets in batch
    
    Accepts a list of tickets and processes them in parallel
    """
    try:
        results = []
        for ticket in tickets:
            result = await route_ticket(ticket)
            results.append(result.dict())
        
        return {"processed": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error in batch routing: {e}")
        raise HTTPException(status_code=500, detail=f"Batch routing error: {str(e)}")

