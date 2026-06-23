# GCP Travel Planning Agent

A serverless travel itinerary planner deployed on Google Cloud Run. The agent scrapes information from Wikipedia about a destination, passes it to the Gemini API (`gemini-2.5-flash`), and generates a customized daily travel itinerary based on user preferences.

## Features
- **FastAPI API**: Simple POST endpoint to request itineraries.
- **Wikipedia Scraper**: Automatically retrieves real-time tourist/attraction context for destinations.
- **Gemini AI Integration**: Uses Google's generative models to synthesize structured itineraries.
- **Dockerized**: Container configuration ready for deployment.
- **Serverless**: Deployed to Google Cloud Run (scales to zero when idle).

---

## Local Setup

1. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt pytest
   ```

3. **Set your Gemini API Key**:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

4. **Run the FastAPI Server**:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

5. **Test the Local Endpoint**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/plan-itinerary" \
        -H "Content-Type: application/json" \
        -d '{"destination": "Tokyo", "days": 3, "interests": ["sushi", "history"]}'
   ```

---

## Running Tests
Run the unit tests locally with:
```bash
PYTHONPATH=. pytest tests/test_app.py -v
```

---

## Google Cloud Run Deployment (Console UI)

1. Connect this repository to your **Google Cloud Run** service.
2. Enable **Continuous Deployment** from GitHub.
3. Select **Dockerfile** as the build type.
4. Under **Variables & Secrets**, add the `GEMINI_API_KEY` environment variable.
5. Deploy and test the live URL!
