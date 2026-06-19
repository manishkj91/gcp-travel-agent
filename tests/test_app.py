import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

# Mock environment variable for API configuration checks
os.environ["GEMINI_API_KEY"] = "mock-key-for-testing"

from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "GCP Travel Agent API is running!"}

@patch("app.main.scrape_highlights")
@patch("app.main.generate_itinerary")
def test_plan_itinerary(mock_generate, mock_scrape):
    mock_scrape.return_value = "Scraped mock attractions"
    mock_generate.return_value = "Detailed itinerary here"
    
    payload = {
        "destination": "London",
        "days": 3,
        "interests": ["museums", "parks"]
    }
    response = client.post("/plan-itinerary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "London"
    assert data["days"] == 3
    assert data["itinerary"] == "Detailed itinerary here"
