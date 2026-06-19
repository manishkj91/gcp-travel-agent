# Build and Deploy a Travel Agent in Google Cloud Run

This plan outlines the steps to build a FastAPI travel agent that scrapes travel highlights, synthesizes them using the Gemini API, packages the application as a Docker container, and deploys it serverless to Google Cloud Run.

## User Review Required

> [!IMPORTANT]
> You will need a Google Cloud Platform (GCP) account and a Gemini API Key. If you do not have a Gemini API key yet, you can get one from Google AI Studio.

We will create the project at:
[gcp-travel-agent](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent)

Please set this subdirectory as your active workspace before we start the implementation.

## Open Questions

- None at the moment. We are ready to proceed with setting up the project files.

---

## Proposed Changes

### Project Foundation

#### [NEW] [requirements.txt](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent/requirements.txt)
Define project dependencies:
```text
fastapi==0.111.0
uvicorn==0.30.1
httpx==0.27.0
beautifulsoup4==4.12.3
google-generativeai==0.7.2
pydantic==2.7.4
```

#### [NEW] [.dockerignore](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent/.dockerignore)
Exclude local files from the container build:
```text
.git
.gitignore
__pycache__
.pytest_cache
.venv
venv
*.pyc
docs/
```

#### [NEW] [Dockerfile](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent/Dockerfile)
Create a multi-stage Docker build:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Run the web service on container startup.
# Bind to 0.0.0.0 for Cloud Run to route traffic to the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

### Python Code

#### [NEW] [main.py](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent/app/main.py)
Create the FastAPI application exposing the `/plan-itinerary` endpoint:
```python
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.scraper import scrape_highlights
from app.planner import generate_itinerary

app = FastAPI(title="GCP Travel Agent", version="1.0.0")

class ItineraryRequest(BaseModel):
    destination: str = Field(..., description="Destination city or place name")
    days: int = Field(..., ge=1, le=14, description="Number of days for itinerary")
    interests: list[str] = Field(default=[], description="Interests or styles of travel")

@app.get("/")
def read_root():
    return {"message": "GCP Travel Agent API is running!"}

@app.post("/plan-itinerary")
async def plan_itinerary(request: ItineraryRequest):
    # Input validation
    clean_destination = re.sub(r"[^a-zA-Z0-9\s,-]", "", request.destination).strip()
    if not clean_destination:
        raise HTTPException(status_code=400, detail="Invalid destination name")
    
    try:
        # Step 1: Scrape travel attractions
        attractions = await scrape_highlights(clean_destination)
        # Step 2: Use LLM to generate itinerary
        itinerary = generate_itinerary(clean_destination, request.days, request.interests, attractions)
        return {"destination": clean_destination, "days": request.days, "itinerary": itinerary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate itinerary: {str(e)}")
```

#### [NEW] [scraper.py](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent/app/scraper.py)
A lightweight scraper that queries Wikipedia Travel/Attractions using `httpx` and parses headings using `BeautifulSoup`:
```python
import httpx
from bs4 import BeautifulSoup
import logging

async def scrape_highlights(destination: str) -> str:
    # URL encode destination
    query = destination.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{query}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code != 200:
                logging.warning(f"Could not scrape Wikipedia for {destination}. Status: {response.status_code}")
                return "No real-time attraction data scraped."
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find paragraphs or lists in the article body to get context
            body_content = soup.find(id="mw-content-text")
            if not body_content:
                return "No real-time attraction data scraped."
                
            paragraphs = body_content.find_all("p")
            text_context = []
            for p in paragraphs[:8]:  # Limit to first 8 paragraphs to prevent context overflow
                text = p.get_text().strip()
                if len(text) > 50:
                    text_context.append(text)
            
            return "\n".join(text_context)
    except Exception as e:
        logging.error(f"Error scraping Wikipedia: {e}")
        return "Failed to fetch scraper data."
```

#### [NEW] [planner.py](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent/app/planner.py)
A module that queries the Gemini API to compile the itinerary:
```python
import os
import google.generativeai as genai

def generate_itinerary(destination: str, days: int, interests: list[str], scraped_data: str) -> str:
    # Secrets management check: error out if API key is not present
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not configured. Please supply it.")
    
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an expert travel assistant. Create a detailed {days}-day travel itinerary for {destination}.
    
    Interests of traveler: {', '.join(interests) if interests else 'General sightseeing'}
    
    Here is scraped context about the destination to incorporate:
    {scraped_data}
    
    Please structure your response with:
    1. A summary of the destination's vibe.
    2. A structured day-by-day plan with specific highlights.
    3. Quick tips (weather, local customs) for the destination.
    
    Keep the itinerary logical, fun, and realistic. Use Markdown formatting.
    """
    
    response = model.generate_content(prompt)
    return response.text
```

---

## Verification Plan

### Automated Tests
To test our code locally before deployment, we will use a test script that sets up local unit tests:
#### [NEW] [test_app.py](file:///Users/manishkj/.gemini/antigravity/scratch/gcp-travel-agent/tests/test_app.py)
```python
import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

# Mock environment variable for import/instantiation checks
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
```

To run tests locally:
```bash
pytest tests/test_app.py
```

### Manual Verification & GCP Deployment Guide

Once local tests pass, here is how we will deploy this step-by-step:

#### 1. Setup local environment and verify:
We will run our app locally bound to localhost:
```bash
export GEMINI_API_KEY="your_actual_key"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Then send a test request:
```bash
curl -X POST "http://127.0.0.1:8000/plan-itinerary" \
     -H "Content-Type: application/json" \
     -d '{"destination": "Tokyo", "days": 2, "interests": ["anime", "food"]}'
```

#### 2. Deploying to Google Cloud Platform:
We will perform these steps in order using the `gcloud` CLI:

*   **Step A: Login and Set Project**
    ```bash
    gcloud auth login
    gcloud config set project [YOUR_PROJECT_ID]
    ```
*   **Step B: Enable Required Services**
    We need to enable the Artifact Registry, Cloud Build, and Cloud Run APIs:
    ```bash
    gcloud services enable artifactregistry.googleapis.com \
                           cloudbuild.googleapis.com \
                           run.googleapis.com
    ```
*   **Step C: Create Artifact Registry Repository**
    Create a repository named `travel-agent-repo` in your preferred region (e.g. `us-central1`):
    ```bash
    gcloud artifacts repositories create travel-agent-repo \
        --repository-format=docker \
        --location=us-central1 \
        --description="Docker repository for Travel Agent"
    ```
*   **Step D: Build and Push Docker Image using Cloud Build**
    We will build the container in the cloud using GCP's builder (no local Docker required):
    ```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/travel-agent-repo/travel-agent:latest .
    ```
*   **Step E: Deploy to Cloud Run**
    Deploy the image as a public endpoint, passing the `GEMINI_API_KEY` environment variable:
    ```bash
    gcloud run deploy travel-agent-service \
        --image us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/travel-agent-repo/travel-agent:latest \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars GEMINI_API_KEY=[YOUR_GEMINI_API_KEY]
    ```
    This command will print a secure URL (e.g. `https://travel-agent-service-xxxxxx-uc.a.run.app`).

*   **Step F: Test the deployed endpoint**
    ```bash
    curl -X POST "https://travel-agent-service-xxxxxx-uc.a.run.app/plan-itinerary" \
         -H "Content-Type: application/json" \
         -d '{"destination": "Paris", "days": 3, "interests": ["history"]}'
    ```

### Security Review Plan
- Verify that uvicorn local servers listen on `127.0.0.1` and NOT `0.0.0.0`.
- Verify that `GEMINI_API_KEY` is not hardcoded anywhere in the codebase.
- Verify input sanitization regex strips special command/SQL chars.
