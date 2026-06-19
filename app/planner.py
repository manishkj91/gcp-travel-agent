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
