import httpx
from bs4 import BeautifulSoup
import logging

async def scrape_highlights(destination: str) -> str:
    # URL encode destination
    query = destination.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{query}"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
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
