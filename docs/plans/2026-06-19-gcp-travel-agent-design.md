# Design Document: GCP Travel Planning Agent

This document outlines the design and architecture for a serverless web-scraping travel agent deployed on Google Cloud Platform (GCP) using Cloud Run and FastAPI.

## Target Architecture

We will deploy a containerized Python FastAPI web service to Google Cloud Run. This service will scrape attractions or information for a specified destination and pass it to Gemini via the Google GenAI SDK to produce a customized travel itinerary.

### Project Layout

```
gcp-travel-agent/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application & API endpoints
│   ├── scraper.py       # Scraper utility (using httpx & BeautifulSoup)
│   └── planner.py       # AI travel planner using Gemini SDK
├── docs/
│   └── plans/
│       └── 2026-06-19-gcp-travel-agent-design.md
├── Dockerfile           # Multi-stage container definition
├── requirements.txt     # Python dependencies
└── .dockerignore        # Files to exclude from container build
```

## Core Components

1. **FastAPI Web Endpoint**: Accepts HTTP POST requests containing:
   - `destination` (string, validated to prevent injection or malicious inputs)
   - `days` (integer, e.g. 1 to 14)
   - `interests` (list of strings, e.g. ["history", "food"])
2. **BeautifulSoup Scraper**: A lightweight scraper that queries web resources (e.g. Wikipedia travel pages or general travel blog sites) for attraction list keywords.
3. **Gemini SDK (google-generativeai)**: Merges the scraped attraction text with user preferences in a prompt, requesting a detailed daily schedule.

## Google Cloud Nuances & Concepts

To deploy this service, we will navigate several core Google Cloud concepts:

1. **Google Cloud Project**: The administrative boundary containing all resources, billing, and permissions.
2. **Google Cloud SDK (`gcloud`)**: The command-line interface used to manage GCP resources.
3. **Artifact Registry**: Google's managed package storage. We will create a Docker repository here to store our compiled container image.
4. **Cloud Build**: GCP's serverless build pipeline. It will compile our Docker image directly in the cloud so we don't have to install Docker locally.
5. **Cloud Run**: A serverless execution environment that runs containerized applications. It automatically scales down to zero instances when idle (costing nothing) and scales up when requests arrive.
6. **Secret Manager (or Environment Variables)**: To access Gemini safely, we will pass the `GEMINI_API_KEY` to Cloud Run as a secure environment variable.

## Security Controls

- **No Hardcoded Secrets**: The application will retrieve `GEMINI_API_KEY` from the environment. If it is missing, the application will fail to start.
- **Input Validation**: Request payloads are parsed and validated using Pydantic. The `destination` field is restricted to safe alphanumeric characters and spaces.
- **Local Isolation**: During local testing, the application server will listen exclusively on `127.0.0.1` (localhost) rather than `0.0.0.0`.
