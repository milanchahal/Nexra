# backend/app/discovery/linkedin_scraper.py
import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict, Optional

# IMPORTANT: This scraper targets the public, non-authenticated structure of LinkedIn job search.
# CSS selectors are highly subject to change and will break if LinkedIn updates its layout.
# This should be treated as a best-effort, brittle component.

BASE_URL = "https://www.linkedin.com/jobs/search"
# A generic user-agent to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

async def scrape_linkedin(query: str, location: str = "India") -> List[Dict]:
    """
    Scrapes LinkedIn for a given query and location.
    
    Args:
        query: The job title or keyword to search for (e.g., "Python Developer").
        location: The geographical location to search in.
        
    Returns:
        A list of dictionaries, where each dictionary represents a job.
    """
    jobs = []
    # LinkedIn uses 'keywords' and 'location' as query params
    params = {"keywords": query, "location": location, "f_TPR": "r86400"} # f_TPR=r86400 -> Past 24 hours

    try:
        async with httpx.AsyncClient() as client:
            # Add a small delay to appear more human-like
            await asyncio.sleep(2)
            response = await client.get(BASE_URL, params=params, headers=HEADERS, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            
            # This selector targets the list of job cards on the search results page.
            # It's the most likely part to break.
            job_cards = soup.find_all("div", class_="base-card")

            for card in job_cards:
                title_tag = card.find("h3", class_="base-search-card__title")
                company_tag = card.find("h4", class_="base-search-card__subtitle")
                location_tag = card.find("span", class_="job-search-card__location")
                url_tag = card.find("a", class_="base-card__full-link")

                if title_tag and company_tag and location_tag and url_tag:
                    job = {
                        "job_title": title_tag.text.strip(),
                        "company_name": company_tag.text.strip(),
                        "location": location_tag.text.strip(),
                        "source_url": url_tag['href'].split('?')[0], # Clean URL
                        "source": "linkedin",
                        # Job description is not available on the search page,
                        # would require a second request per job, which is too aggressive for Phase 2.
                        "job_description": f"{title_tag.text.strip()} at {company_tag.text.strip()}"
                    }
                    jobs.append(job)

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred while scraping LinkedIn for '{query}': {e.response.status_code}")
    except Exception as e:
        print(f"An error occurred during LinkedIn scraping for '{query}': {e}")
        
    return jobs
