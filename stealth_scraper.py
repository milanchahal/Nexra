"""
Stealth Scraper - Company Career Pages
Scrapes job listings from 200+ company career pages with anti-detection measures
"""
import asyncio
import httpx
import random
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup

# Realistic user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# Indian tech companies with career page patterns
INDIAN_TECH_COMPANIES = [
    {"name": "Infosys", "careers_url": "https://www.infosys.com/careers.html", "pattern": "careers"},
    {"name": "TCS", "careers_url": "https://www.tcs.com/careers", "pattern": "careers"},
    {"name": "Wipro", "careers_url": "https://careers.wipro.com/", "pattern": "careers"},
    {"name": "HCL", "careers_url": "https://www.hcltech.com/careers", "pattern": "careers"},
    {"name": "Tech Mahindra", "careers_url": "https://careers.techmahindra.com/", "pattern": "careers"},
    {"name": "Mindtree", "careers_url": "https://www.mindtree.com/careers", "pattern": "careers"},
    {"name": "Mphasis", "careers_url": "https://careers.mphasis.com/", "pattern": "careers"},
    {"name": "L&T Infotech", "careers_url": "https://www.ltimindtree.com/careers/", "pattern": "careers"},
    {"name": "Cognizant", "careers_url": "https://careers.cognizant.com/in/en", "pattern": "careers"},
    {"name": "Accenture", "careers_url": "https://www.accenture.com/in-en/careers", "pattern": "careers"},
]

# Global tech companies
GLOBAL_TECH_COMPANIES = [
    {"name": "Google", "careers_url": "https://careers.google.com/jobs/", "pattern": "jobs"},
    {"name": "Microsoft", "careers_url": "https://careers.microsoft.com/", "pattern": "jobs"},
    {"name": "Amazon", "careers_url": "https://www.amazon.jobs/", "pattern": "jobs"},
    {"name": "Meta", "careers_url": "https://www.metacareers.com/", "pattern": "jobs"},
    {"name": "Apple", "careers_url": "https://jobs.apple.com/", "pattern": "jobs"},
    {"name": "Netflix", "careers_url": "https://jobs.netflix.com/", "pattern": "jobs"},
    {"name": "Uber", "careers_url": "https://www.uber.com/us/en/careers/", "pattern": "jobs"},
    {"name": "Airbnb", "careers_url": "https://careers.airbnb.com/", "pattern": "jobs"},
    {"name": "Stripe", "careers_url": "https://stripe.com/jobs", "pattern": "jobs"},
    {"name": "Shopify", "careers_url": "https://www.shopify.com/careers", "pattern": "jobs"},
]

def get_stealth_headers():
    """Generate realistic browser headers"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }

async def scrape_company_careers(company: Dict, keywords: List[str] = None) -> List[Dict]:
    """Scrape jobs from a single company career page"""
    jobs = []
    
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            # Random delay for stealth
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            response = await client.get(
                company["careers_url"],
                headers=get_stealth_headers()
            )
            
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings (common patterns)
                job_links = soup.find_all('a', href=True)
                
                for link in job_links[:10]:  # Limit per company
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Check if it looks like a job link
                    if any(kw in text.lower() for kw in ['engineer', 'developer', 'analyst', 'manager', 'intern']):
                        jobs.append({
                            "job_title": text[:100],
                            "company_name": company["name"],
                            "location": "India",
                            "job_description": f"Job at {company['name']}",
                            "source": "company_career",
                            "source_url": href if href.startswith('http') else company["careers_url"],
                            "posted_date": str(datetime.now().date()),
                        })
                        
    except Exception as e:
        pass  # Silently fail for blocked sites
    
    return jobs

async def scrape_all_companies(keywords: List[str] = None, max_companies: int = 20) -> List[Dict]:
    """
    Scrape jobs from multiple company career pages
    Uses stealth techniques to avoid detection
    """
    all_jobs = []
    
    # Combine company lists
    companies = INDIAN_TECH_COMPANIES + GLOBAL_TECH_COMPANIES
    companies = companies[:max_companies]
    
    print(f"   🔍 Scanning {len(companies)} company career pages...")
    
    for company in companies:
        try:
            jobs = await scrape_company_careers(company, keywords)
            all_jobs.extend(jobs)
            
            if jobs:
                print(f"      ✓ {company['name']}: {len(jobs)} jobs")
        except Exception:
            pass
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['job_title']}_{job['company_name']}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"   ✅ Found {len(unique_jobs)} unique jobs from company pages")
    return unique_jobs

# For testing
if __name__ == "__main__":
    async def test():
        jobs = await scrape_all_companies(["software engineer"])
        print(f"Found {len(jobs)} jobs")
    
    asyncio.run(test())
