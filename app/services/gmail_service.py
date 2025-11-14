"""Gmail API service for fetching support tickets"""

import base64
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.utils.config import settings
from app.utils.logger import logger

logger = logging.getLogger(__name__)


class GmailService:
    """Service for interacting with Gmail API"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        try:
            if settings.GMAIL_REFRESH_TOKEN:
                creds = Credentials(
                    token=None,
                    refresh_token=settings.GMAIL_REFRESH_TOKEN,
                    client_id=settings.GMAIL_CLIENT_ID,
                    client_secret=settings.GMAIL_CLIENT_SECRET,
                    token_uri="https://oauth2.googleapis.com/token"
                )
                creds.refresh(Request())
                self.credentials = creds
                self.service = build('gmail', 'v1', credentials=creds)
                logger.info("Gmail API authenticated successfully")
            else:
                logger.warning("Gmail credentials not configured. Using mock mode.")
        except Exception as e:
            logger.error(f"Gmail authentication error: {e}")
            logger.warning("Gmail service will operate in mock mode")
    
    def fetch_tickets(self, query: str = "is:unread", max_results: int = 10) -> List[Dict]:
        """
        Fetch support tickets from Gmail
        
        Args:
            query: Gmail search query (default: unread emails)
            max_results: Maximum number of tickets to fetch
            
        Returns:
            List of ticket dictionaries
        """
        if not self.service:
            logger.warning("Gmail service not available, returning mock data")
            return self._get_mock_tickets()
        
        try:
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            tickets = []
            
            for msg in messages:
                ticket = self._parse_message(msg['id'])
                if ticket:
                    tickets.append(ticket)
            
            logger.info(f"Fetched {len(tickets)} tickets from Gmail")
            return tickets
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return self._get_mock_tickets()
        except Exception as e:
            logger.error(f"Error fetching tickets: {e}")
            return self._get_mock_tickets()
    
    def _parse_message(self, message_id: str) -> Optional[Dict]:
        """Parse a Gmail message into a ticket format"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            return {
                'id': message_id,
                'subject': subject,
                'from': sender,
                'date': date,
                'body': body,
                'text': f"{subject}\n\n{body}",
                'source': 'gmail'
            }
        except Exception as e:
            logger.error(f"Error parsing message {message_id}: {e}")
            return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def _get_mock_tickets(self) -> List[Dict]:
        """Return mock tickets for testing when Gmail API is not available"""
        return [
            {
                'id': 'mock-1',
                'subject': 'Billing Issue - Payment Failed',
                'from': 'customer@example.com',
                'date': datetime.now().isoformat(),
                'body': 'I tried to make a payment but it failed. My card was charged but the service shows as unpaid.',
                'text': 'Billing Issue - Payment Failed\n\nI tried to make a payment but it failed. My card was charged but the service shows as unpaid.',
                'source': 'mock'
            },
            {
                'id': 'mock-2',
                'subject': 'Cannot Access Dashboard',
                'from': 'user@example.com',
                'date': datetime.now().isoformat(),
                'body': 'I cannot log into my account. I keep getting an authentication error.',
                'text': 'Cannot Access Dashboard\n\nI cannot log into my account. I keep getting an authentication error.',
                'source': 'mock'
            },
            {
                'id': 'mock-3',
                'subject': 'API Integration Help',
                'from': 'developer@example.com',
                'date': datetime.now().isoformat(),
                'body': 'I need help integrating your API into my application. The documentation is unclear about authentication.',
                'text': 'API Integration Help\n\nI need help integrating your API into my application. The documentation is unclear about authentication.',
                'source': 'mock'
            }
        ]


# Global service instance
_gmail_service_instance = None


def get_gmail_service() -> GmailService:
    """Get or create the global Gmail service instance"""
    global _gmail_service_instance
    if _gmail_service_instance is None:
        _gmail_service_instance = GmailService()
    return _gmail_service_instance

