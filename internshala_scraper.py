"""
Internshala Scraper
Scrapes internship listings from Internshala.com
"""
import asyncio
import httpx
import random
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

async def scrape_internshala(keywords: List[str] = None) -> List[Dict]:
    """Scrape internships from Internshala"""
    jobs = []
    
    search_terms = keywords[:2] if keywords else ["software", "web development"]
    
    print("   🔍 Searching Internshala...")
    
    for term in search_terms:
        try:
            url = f"https://internshala.com/internships/{term.replace(' ', '-')}-internship"
            
            async with httpx.AsyncClient(timeout=20) as client:
                await asyncio.sleep(random.uniform(1, 2))
                
                response = await client.get(url, headers=get_headers())
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find internship cards
                    cards = soup.select('.internship_meta, .individual_internship')
                    
                    for card in cards[:10]:
                        try:
                            title_el = card.select_one('.profile, h3, .heading_4_5')
                            company_el = card.select_one('.company_name, .company, .heading_6')
                            location_el = card.select_one('.location_link, .location')
                            
                            if title_el:
                                jobs.append({
                                    "job_title": title_el.get_text(strip=True),
                                    "company_name": company_el.get_text(strip=True) if company_el else "Unknown",
                                    "location": location_el.get_text(strip=True) if location_el else "India",
                                    "job_description": f"Internship in {term}",
                                    "source": "internshala",
                                    "source_url": url,
                                    "posted_date": str(datetime.now().date()),
                                    "job_type": "internship",
                                })
                        except Exception:
                            continue
                            
        except Exception as e:
            print(f"      Internshala error: {str(e)[:30]}")
    
    print(f"   ✅ Found {len(jobs)} from Internshala")
    return jobs

if __name__ == "__main__":
    asyncio.run(scrape_internshala(["python", "react"]))
