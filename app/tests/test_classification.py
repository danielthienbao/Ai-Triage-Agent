"""Tests for ticket classification"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_classify_endpoint():
    """Test the classification endpoint"""
    response = client.post(
        "/classify",
        json={
            "text": "I cannot access my account. My password is not working.",
            "include_suggestion": False,
            "include_summary": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert "confidence" in data
    assert "scores" in data
    assert "model" in data
    assert isinstance(data["confidence"], float)
    assert 0 <= data["confidence"] <= 1


def test_classify_with_suggestion():
    """Test classification with AI suggestion"""
    response = client.post(
        "/classify",
        json={
            "text": "My payment failed but I was charged.",
            "include_suggestion": True,
            "include_summary": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data
    assert data["suggestion"] is not None


def test_classify_with_summary():
    """Test classification with summary"""
    response = client.post(
        "/classify",
        json={
            "text": "I need help integrating the API into my application.",
            "include_suggestion": False,
            "include_summary": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"] is not None


def test_classify_empty_text():
    """Test classification with empty text"""
    response = client.post(
        "/classify",
        json={
            "text": "",
            "include_suggestion": False,
            "include_summary": False
        }
    )
    
    # Should still work but may return low confidence
    assert response.status_code == 200


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data

