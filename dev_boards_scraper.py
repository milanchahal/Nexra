# backend/app/discovery/dev_boards_scraper.py
"""
Scrapes developer-focused job boards:
- GitHub Jobs alternative sites
- StackOverflow Jobs
- HackerRank Jobs
- Devpost
- RemoteOK
- CutShort
"""
import httpx
from bs4 import BeautifulSoup
import asyncio
import random
from typing import List, Dict

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
    }

# Developer-focused job boards
DEV_BOARDS = [
    # RemoteOK - Remote jobs worldwide
    {
        "name": "RemoteOK",
        "url": "https://remoteok.com/remote-dev-jobs",
        "selector": "[class*='job']",
    },
    # We Work Remotely
    {
        "name": "WeWorkRemotely",
        "url": "https://weworkremotely.com/remote-jobs/search?term=developer&region=anywhere",
        "selector": "li.feature, li.job",
    },
    # HackerRank Jobs
    {
        "name": "HackerRank",
        "url": "https://www.hackerrank.com/careers",
        "selector": "[class*='job'], [class*='career']",
    },
    # Devpost
    {
        "name": "Devpost",
        "url": "https://devpost.com/software-jobs",
        "selector": "[class*='job'], article",
    },
    # CutShort India
    {
        "name": "CutShort",
        "url": "https://cutshort.io/jobs?location=India",
        "selector": "[class*='job-card']",
    },
    # TopTal
    {
        "name": "TopTal",
        "url": "https://www.toptal.com/careers",
        "selector": "[class*='job'], [class*='position']",
    },
    # Turing
    {
        "name": "Turing",
        "url": "https://www.turing.com/remote-developer-jobs",
        "selector": "[class*='job']",
    },
]

async def scrape_single_dev_board(board_info: dict, keywords: List[str]) -> List[Dict]:
    """Scrapes a single developer job board."""
    jobs = []
    
    try:
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            await asyncio.sleep(random.uniform(2, 4))
            
            response = await client.get(board_info["url"], headers=get_headers())
            
            if response.status_code in [403, 429, 503]:
                return jobs
                
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text().lower()
            
            # Check if page has relevant content
            if not any(kw.lower() in text_content for kw in keywords[:5]):
                return jobs
            
            # Try the specific selector
            cards = soup.select(board_info["selector"])
            
            # Fallback to generic job patterns
            if not cards:
                cards = soup.find_all(["div", "li", "article"], 
                    class_=lambda x: x and any(w in x.lower() for w in ["job", "position", "listing"]) if x else False)
            
            for card in cards[:8]:
                try:
                    # Find title
                    title_elem = (
                        card.find(["h2", "h3", "h4"]) or
                        card.find("a", href=True)
                    )
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)[:100]
                        
                        # Filter - make sure it's actually a job
                        if len(title) > 10 and any(kw.lower() in title.lower() for kw in keywords[:5]):
                            job = {
                                "job_title": title,
                                "company_name": board_info["name"],
                                "location": "Remote / India",
                                "source_url": board_info["url"],
                                "source": "devboard",
                                "job_description": f"{title} - Developer opportunity via {board_info['name']}"
                            }
                            jobs.append(job)
                except Exception:
                    continue
                    
    except Exception:
        pass
        
    return jobs

async def scrape_dev_boards(keywords: List[str]) -> List[Dict]:
    """
    Scrapes developer job boards for tech opportunities.
    
    Args:
        keywords: List of skills from user profile
        
    Returns:
        List of job dictionaries
    """
    all_jobs = []
    
    # Scrape boards sequentially with delays
    for i, board in enumerate(DEV_BOARDS):
        try:
            jobs = await scrape_single_dev_board(board, keywords)
            all_jobs.extend(jobs)
            
            if i < len(DEV_BOARDS) - 1:
                await asyncio.sleep(random.uniform(2, 4))
        except Exception:
            continue
    
    return all_jobs
