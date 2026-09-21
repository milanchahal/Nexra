# backend/app/discovery/indeed_scraper.py
"""
Scrapes Indeed India for job listings.
"""
import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

async def scrape_indeed_india(query: str, location: str = "India") -> List[Dict]:
    """
    Scrapes Indeed India for jobs matching the query.
    
    Args:
        query: Job title/keywords to search
        location: Location filter (default: India)
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    formatted_query = query.replace(' ', '+')
    formatted_location = location.replace(' ', '+')
    search_url = f"https://in.indeed.com/jobs?q={formatted_query}&l={formatted_location}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            await asyncio.sleep(2)  # Respectful delay
            response = await client.get(search_url, headers=HEADERS, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Indeed uses various class names for job cards
            job_cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon|jobsearch-SerpJobCard"))
            
            for card in job_cards[:15]:  # Limit to 15 per query
                try:
                    title_elem = card.find("h2", class_=re.compile(r"jobTitle")) or card.find("a", class_=re.compile(r"jcs-JobTitle"))
                    company_elem = card.find("span", {"data-testid": "company-name"}) or card.find("span", class_="companyName")
                    location_elem = card.find("div", {"data-testid": "text-location"}) or card.find("div", class_="companyLocation")
                    
                    if title_elem:
                        link = title_elem.find("a") if title_elem.name != "a" else title_elem
                        href = link.get("href", "") if link else ""
                        
                        job = {
                            "job_title": title_elem.get_text(strip=True),
                            "company_name": company_elem.get_text(strip=True) if company_elem else "Unknown Company",
                            "location": location_elem.get_text(strip=True) if location_elem else location,
                            "source_url": f"https://in.indeed.com{href}" if href.startswith("/") else href,
                            "source": "indeed",
                            "job_description": f"{title_elem.get_text(strip=True)} at {company_elem.get_text(strip=True) if company_elem else 'Unknown'}"
                        }
                        jobs.append(job)
                except Exception as e:
                    continue
                    
    except httpx.HTTPStatusError as e:
        print(f"HTTP error scraping Indeed for '{query}': {e.response.status_code}")
    except Exception as e:
        print(f"Error scraping Indeed for '{query}': {e}")
        
    return jobs
