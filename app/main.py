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
    # Input validation: Allow alphanumeric characters, spaces, commas, and hyphens.
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
