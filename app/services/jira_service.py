"""Jira REST API service for creating and updating issues"""

from typing import Dict, Optional
import logging
import requests
from requests.auth import HTTPBasicAuth

from app.utils.config import settings
from app.utils.logger import logger

logger = logging.getLogger(__name__)


class JiraService:
    """Service for interacting with Jira REST API"""
    
    def __init__(self):
        self.url = settings.JIRA_URL
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        self.project_key = settings.JIRA_PROJECT_KEY
        self.auth = None
        
        if self.email and self.api_token:
            self.auth = HTTPBasicAuth(self.email, self.api_token)
            logger.info("Jira service initialized with credentials")
        else:
            logger.warning("Jira credentials not configured. Using mock mode.")
    
    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        labels: Optional[list] = None
    ) -> Dict:
        """
        Create a new Jira issue
        
        Args:
            summary: Issue summary/title
            description: Issue description
            issue_type: Type of issue (Task, Bug, Story, etc.)
            priority: Issue priority (Low, Medium, High, Critical)
            labels: Optional list of labels
            
        Returns:
            Dictionary with issue details or error
        """
        if not self.auth:
            logger.warning("Jira not configured, returning mock issue")
            return self._create_mock_issue(summary, description, priority)
        
        try:
            url = f"{self.url}/rest/api/3/issue"
            
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": issue_type},
                    "priority": {"name": priority}
                }
            }
            
            if labels:
                payload["fields"]["labels"] = labels
            
            response = requests.post(
                url,
                json=payload,
                auth=self.auth,
                headers={"Accept": "application/json", "Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                logger.info(f"Created Jira issue: {issue_data.get('key')}")
                return {
                    "success": True,
                    "issue_key": issue_data.get("key"),
                    "issue_id": issue_data.get("id"),
                    "url": f"{self.url}/browse/{issue_data.get('key')}"
                }
            else:
                error_msg = f"Failed to create Jira issue: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Error creating Jira issue: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict:
        """
        Update an existing Jira issue
        
        Args:
            issue_key: The Jira issue key (e.g., SUP-123)
            summary: Optional new summary
            description: Optional new description
            priority: Optional new priority
            
        Returns:
            Dictionary with update status
        """
        if not self.auth:
            logger.warning("Jira not configured, returning mock update")
            return {"success": True, "message": "Mock update successful"}
        
        try:
            url = f"{self.url}/rest/api/3/issue/{issue_key}"
            
            fields = {}
            if summary:
                fields["summary"] = summary
            if description:
                fields["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }
                    ]
                }
            if priority:
                fields["priority"] = {"name": priority}
            
            if not fields:
                return {"success": False, "error": "No fields to update"}
            
            payload = {"fields": fields}
            
            response = requests.put(
                url,
                json=payload,
                auth=self.auth,
                headers={"Accept": "application/json", "Content-Type": "application/json"}
            )
            
            if response.status_code == 204:
                logger.info(f"Updated Jira issue: {issue_key}")
                return {"success": True, "issue_key": issue_key}
            else:
                error_msg = f"Failed to update Jira issue: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            logger.error(f"Error updating Jira issue: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_mock_issue(self, summary: str, description: str, priority: str) -> Dict:
        """Create a mock issue for testing"""
        import random
        issue_key = f"{self.project_key}-{random.randint(1000, 9999)}"
        return {
            "success": True,
            "issue_key": issue_key,
            "issue_id": f"mock-{random.randint(10000, 99999)}",
            "url": f"{self.url}/browse/{issue_key}",
            "mock": True
        }


# Global service instance
_jira_service_instance = None


def get_jira_service() -> JiraService:
    """Get or create the global Jira service instance"""
    global _jira_service_instance
    if _jira_service_instance is None:
        _jira_service_instance = JiraService()
    return _jira_service_instance

