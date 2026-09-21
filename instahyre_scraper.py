# backend/app/discovery/instahyre_scraper.py
"""
Scrapes Instahyre - a popular Indian startup job platform.
"""
import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

async def scrape_instahyre(query: str) -> List[Dict]:
    """
    Scrapes Instahyre for jobs matching the query.
    Note: Instahyre requires login for full access, this scrapes public listings.
    
    Args:
        query: Job title/keywords to search
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    formatted_query = query.lower().replace(' ', '-')
    search_url = f"https://www.instahyre.com/search-jobs/?search={formatted_query}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            await asyncio.sleep(2)
            response = await client.get(search_url, headers=HEADERS, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for job listings
            job_cards = soup.find_all("div", class_="job-card") or soup.find_all("article", class_="job")
            
            for card in job_cards[:15]:
                try:
                    title_elem = card.find("h3") or card.find("a", class_="job-title")
                    company_elem = card.find("span", class_="company") or card.find("div", class_="company-name")
                    location_elem = card.find("span", class_="location")
                    link_elem = card.find("a", href=True)
                    
                    if title_elem:
                        job = {
                            "job_title": title_elem.get_text(strip=True),
                            "company_name": company_elem.get_text(strip=True) if company_elem else "Startup",
                            "location": location_elem.get_text(strip=True) if location_elem else "India",
                            "source_url": link_elem["href"] if link_elem else search_url,
                            "source": "instahyre",
                            "job_description": f"{title_elem.get_text(strip=True)} - Startup opportunity"
                        }
                        jobs.append(job)
                except Exception:
                    continue
                    
    except Exception as e:
        print(f"Error scraping Instahyre for '{query}': {e}")
        
    return jobs
