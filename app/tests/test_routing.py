"""Tests for ticket routing"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_route_endpoint():
    """Test the routing endpoint"""
    response = client.post(
        "/route",
        json={
            "ticket_id": "TEST-001",
            "text": "I cannot log into my account.",
            "subject": "Access Issue",
            "from_email": "user@example.com",
            "create_jira": True,
            "send_slack": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data
    assert "category" in data
    assert "confidence" in data
    assert "routing_config" in data
    assert data["ticket_id"] == "TEST-001"


def test_route_without_jira():
    """Test routing without creating Jira issue"""
    response = client.post(
        "/route",
        json={
            "ticket_id": "TEST-002",
            "text": "Billing question about my invoice.",
            "create_jira": False,
            "send_slack": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data.get("jira_issue") is None or not data["jira_issue"].get("success")


def test_route_without_slack():
    """Test routing without sending Slack notification"""
    response = client.post(
        "/route",
        json={
            "ticket_id": "TEST-003",
            "text": "Technical support needed for API integration.",
            "create_jira": True,
            "send_slack": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    # Slack message may be None or mock
    assert "slack_message" in data


def test_route_batch():
    """Test batch routing"""
    tickets = [
        {
            "ticket_id": f"BATCH-{i}",
            "text": f"Test ticket {i}",
            "create_jira": False,
            "send_slack": False
        }
        for i in range(3)
    ]
    
    response = client.post("/route/batch", json=tickets)
    assert response.status_code == 200
    data = response.json()
    assert "processed" in data
    assert "results" in data
    assert data["processed"] == 3
    assert len(data["results"]) == 3


def test_route_minimal_request():
    """Test routing with minimal required fields"""
    response = client.post(
        "/route",
        json={
            "ticket_id": "MIN-001",
            "text": "Help needed",
            "create_jira": False,
            "send_slack": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "MIN-001"
    assert "category" in data

