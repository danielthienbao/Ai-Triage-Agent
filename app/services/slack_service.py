"""Slack Web API service for sending notifications"""

from typing import Dict, Optional
import logging
import requests

from app.utils.config import settings
from app.utils.logger import logger

logger = logging.getLogger(__name__)


class SlackService:
    """Service for interacting with Slack Web API"""
    
    def __init__(self):
        self.bot_token = settings.SLACK_BOT_TOKEN
        self.base_url = "https://slack.com/api"
        self.default_channel = settings.SLACK_CHANNEL_ID
        
        if self.bot_token:
            logger.info("Slack service initialized with token")
        else:
            logger.warning("Slack token not configured. Using mock mode.")
    
    def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        blocks: Optional[list] = None,
        thread_ts: Optional[str] = None
    ) -> Dict:
        """
        Send a message to a Slack channel
        
        Args:
            text: Message text
            channel: Channel ID or name (defaults to configured channel)
            blocks: Optional Slack Block Kit blocks for rich formatting
            thread_ts: Optional timestamp to reply in thread
            
        Returns:
            Dictionary with message status
        """
        if not self.bot_token:
            logger.warning("Slack not configured, returning mock response")
            return self._send_mock_message(text, channel)
        
        try:
            url = f"{self.base_url}/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "channel": channel or self.default_channel,
                "text": text
            }
            
            if blocks:
                payload["blocks"] = blocks
            
            if thread_ts:
                payload["thread_ts"] = thread_ts
            
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            
            if result.get("ok"):
                logger.info(f"Sent Slack message to {channel or self.default_channel}")
                return {
                    "success": True,
                    "channel": result.get("channel"),
                    "ts": result.get("ts"),
                    "message": result.get("message")
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Failed to send Slack message: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_ticket_notification(
        self,
        ticket_id: str,
        category: str,
        summary: str,
        jira_key: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict:
        """
        Send a formatted ticket notification to Slack
        
        Args:
            ticket_id: The ticket identifier
            category: The classified category
            summary: Ticket summary
            jira_key: Optional Jira issue key if created
            channel: Optional channel override
            
        Returns:
            Dictionary with notification status
        """
        # Determine channel based on category
        routing = settings.CATEGORY_ROUTING.get(category, {})
        target_channel = channel or routing.get("slack_channel", self.default_channel)
        
        # Create rich message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New {category.title()} Ticket"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Ticket ID:*\n{ticket_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Category:*\n{category}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary}"
                }
            }
        ]
        
        if jira_key:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Jira Issue:* <{settings.JIRA_URL}/browse/{jira_key}|{jira_key}>"
                }
            })
        
        text = f"New {category} ticket: {summary}"
        if jira_key:
            text += f" (Jira: {jira_key})"
        
        return self.send_message(text, channel=target_channel, blocks=blocks)
    
    def _send_mock_message(self, text: str, channel: Optional[str]) -> Dict:
        """Send a mock message for testing"""
        return {
            "success": True,
            "channel": channel or self.default_channel,
            "ts": "1234567890.123456",
            "message": {"text": text},
            "mock": True
        }


# Global service instance
_slack_service_instance = None


def get_slack_service() -> SlackService:
    """Get or create the global Slack service instance"""
    global _slack_service_instance
    if _slack_service_instance is None:
        _slack_service_instance = SlackService()
    return _slack_service_instance

