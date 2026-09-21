# backend/app/discovery/naukri_scraper.py
import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict

# IMPORTANT: This scraper targets the public search results of Naukri.com.
# Selectors will break if Naukri updates its site layout. This is a brittle component.

BASE_URL = "https://www.naukri.com/jobs-in-india" # A more generic starting point
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

async def scrape_naukri(query: str) -> List[Dict]:
    """
    Scrapes Naukri.com for a given job query.
    
    Args:
        query: The job title/keyword. Naukri's URL structure is path-based.
        
    Returns:
        A list of job dictionaries.
    """
    jobs = []
    # Naukri uses a URL path structure, e.g., /python-jobs-in-india
    # We replace spaces with hyphens for the query.
    formatted_query = query.lower().replace(' ', '-')
    search_url = f"https://www.naukri.com/{formatted_query}-jobs"
    
    try:
        async with httpx.AsyncClient() as client:
            await asyncio.sleep(2) # Human-like delay
            response = await client.get(search_url, headers=HEADERS, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            
            # This selector targets the main job articles in the search results.
            job_articles = soup.find_all("article", class_="jobTuple")

            for article in job_articles:
                title_tag = article.find("a", class_="title")
                company_tag = article.find("a", class_="subTitle")
                location_tag = article.find("span", class_="loc-badge")
                
                if title_tag and company_tag and location_tag:
                    job = {
                        "job_title": title_tag.text.strip(),
                        "company_name": company_tag.text.strip(),
                        "location": location_tag.text.strip(),
                        "source_url": title_tag['href'].split('?')[0],
                        "source": "naukri",
                        "job_description": f"{title_tag.text.strip()} at {company_tag.text.strip()}"
                    }
                    jobs.append(job)

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred while scraping Naukri for '{query}': {e.response.status_code}")
    except Exception as e:
        print(f"An error occurred during Naukri scraping for '{query}': {e}")
        
    return jobs
