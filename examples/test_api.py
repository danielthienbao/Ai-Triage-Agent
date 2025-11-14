"""Example script to test the API endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_classify():
    """Test the classification endpoint"""
    print("\n=== Testing Classification Endpoint ===")
    
    response = requests.post(
        f"{BASE_URL}/classify",
        json={
            "text": "I cannot access my account. My password is not working and I've tried resetting it multiple times.",
            "include_suggestion": True,
            "include_summary": True
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_route():
    """Test the routing endpoint"""
    print("\n=== Testing Routing Endpoint ===")
    
    response = requests.post(
        f"{BASE_URL}/route",
        json={
            "ticket_id": "DEMO-001",
            "text": "I was charged twice for my subscription. Please refund one of the charges.",
            "subject": "Double Billing Issue",
            "from_email": "customer@example.com",
            "create_jira": True,
            "send_slack": True
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_health():
    """Test the health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("AI Triage Agent - API Test Script")
    print("=" * 50)
    
    try:
        test_health()
        test_classify()
        test_route()
        print("\n✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API.")
        print("Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")

