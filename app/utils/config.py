"""Configuration management using environment variables"""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys and Tokens
    GMAIL_CLIENT_ID: Optional[str] = os.getenv("GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET: Optional[str] = os.getenv("GMAIL_CLIENT_SECRET")
    GMAIL_REFRESH_TOKEN: Optional[str] = os.getenv("GMAIL_REFRESH_TOKEN")
    
    JIRA_URL: Optional[str] = os.getenv("JIRA_URL", "https://your-domain.atlassian.net")
    JIRA_EMAIL: Optional[str] = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN: Optional[str] = os.getenv("JIRA_API_TOKEN")
    JIRA_PROJECT_KEY: Optional[str] = os.getenv("JIRA_PROJECT_KEY", "SUP")
    
    SLACK_BOT_TOKEN: Optional[str] = os.getenv("SLACK_BOT_TOKEN")
    SLACK_CHANNEL_ID: Optional[str] = os.getenv("SLACK_CHANNEL_ID", "#support-tickets")
    
    # IBM watsonx.ai
    WATSONX_API_KEY: Optional[str] = os.getenv("WATSONX_API_KEY")
    WATSONX_URL: Optional[str] = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    WATSONX_PROJECT_ID: Optional[str] = os.getenv("WATSONX_PROJECT_ID")
    WATSONX_MODEL_ID: Optional[str] = os.getenv("WATSONX_MODEL_ID", "meta-llama/llama-3-8b-instruct")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "bert-base-uncased")
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "./models")
    
    # Application
    APP_NAME: str = "AI Triage Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Routing Configuration
    CATEGORY_ROUTING: dict = {
        "billing": {"jira_priority": "High", "slack_channel": "#billing"},
        "technical": {"jira_priority": "Medium", "slack_channel": "#technical"},
        "access": {"jira_priority": "High", "slack_channel": "#access"},
        "general": {"jira_priority": "Low", "slack_channel": "#general"},
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

