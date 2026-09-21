"""
JobSpy Integration Scraper
Uses the python-jobspy library (pip install python-jobspy)
Supports: LinkedIn, Indeed, Naukri, Glassdoor, ZipRecruiter, Google
"""
import asyncio
from typing import List, Dict
from datetime import datetime
import json
import math

# Check if jobspy is installed
try:
    from jobspy import scrape_jobs
    JOBSPY_AVAILABLE = True
except ImportError:
    JOBSPY_AVAILABLE = False
    print("⚠️ JobSpy not installed. Run: pip install python-jobspy")

# Default search configuration
DEFAULT_CONFIG = {
    "site_name": ["linkedin", "indeed", "glassdoor"],  # naukri requires special setup
    "search_term": "software engineer",
    "location": "India",
    "results_wanted": 20,
    "hours_old": 72,  # Jobs from last 3 days
    "country_indeed": "India",
}

# Job boards supported by JobSpy
SUPPORTED_SITES = [
    "linkedin",
    "indeed", 
    "glassdoor",
    "zip_recruiter",
    "google",
    # "naukri"  # Requires additional setup
]

async def scrape_with_jobspy(
    search_term: str = "software engineer",
    location: str = "India",
    sites: List[str] = None,
    results_per_site: int = 15
) -> List[Dict]:
    """
    Scrape jobs using JobSpy library
    """
    if not JOBSPY_AVAILABLE:
        print("   ⚠️ JobSpy not available, skipping...")
        return []
    
    jobs = []
    sites = sites or ["linkedin", "indeed"]
    
    try:
        # Run scrape_jobs in executor (it's sync)
        loop = asyncio.get_event_loop()
        
        df = await loop.run_in_executor(
            None,
            lambda: scrape_jobs(
                site_name=sites,
                search_term=search_term,
                location=location,
                results_wanted=results_per_site,
                hours_old=72,
                country_indeed="India",
            )
        )
        
        if df is not None and not df.empty:
            # Convert DataFrame to list of dicts
            for _, row in df.iterrows():
                job = normalize_jobspy_result(row.to_dict())
                if job:
                    jobs.append(job)
        
    except Exception as e:
        print(f"   ⚠️ JobSpy error: {str(e)[:50]}")
    
    return jobs

def normalize_jobspy_result(row: Dict) -> Dict:
    """Convert JobSpy result to our standard format"""
    try:
        return {
            "job_title": row.get("title", "Unknown"),
            "company_name": row.get("company", "Unknown"),
            "location": row.get("location", "Remote"),
            "job_description": (row.get("description", "")[:2000] + 
                              (f"\n\nSalary: {row.get('min_amount', '')} - {row.get('max_amount', '')} {row.get('currency', '')}" 
                               if row.get('min_amount') else "")),
            "source": f"jobspy_{row.get('site', 'unknown')}",
            "source_url": row.get("job_url", ""),
            "posted_date": str(row.get("date_posted", datetime.now().date())),
            
            # Map to Job model fields
            "salary_min": row.get("min_amount") if row.get("min_amount") and not math.isnan(row.get("min_amount")) else None,
            "salary_max": row.get("max_amount") if row.get("max_amount") and not math.isnan(row.get("max_amount")) else None,
            "salary_type": row.get("interval", "yearly"), # JobSpy uses 'interval'
            
            "job_type": row.get("job_type", "Full-time"),
            "experience_level": row.get("job_level", ""),
            "is_remote": row.get("is_remote", False),
            "company_url": row.get("company_url", ""),
            "company_logo": row.get("logo_photo_url", ""),
        }
    except Exception:
        return None

def format_salary(min_amt, max_amt, currency) -> str:
    """Format salary range"""
    if min_amt and max_amt:
        return f"{currency or '$'}{min_amt:,.0f} - {currency or '$'}{max_amt:,.0f}"
    elif min_amt:
        return f"{currency or '$'}{min_amt:,.0f}+"
    elif max_amt:
        return f"Up to {currency or '$'}{max_amt:,.0f}"
    return ""

async def scrape_jobspy_all(user_keywords: List[str] = None) -> List[Dict]:
    """
    Main function to scrape jobs using JobSpy
    Searches multiple sites for each keyword
    """
    all_jobs = []
    
    if not JOBSPY_AVAILABLE:
        print("   ⚠️ JobSpy not installed. Install with: pip install python-jobspy")
        return []
    
    # Keywords to search
    search_terms = user_keywords[:3] if user_keywords else [
        "software engineer",
        "frontend developer", 
        "data scientist"
    ]
    
    print(f"   🔍 Searching via JobSpy: {', '.join(search_terms[:2])}...")
    
    for term in search_terms:
        try:
            jobs = await scrape_with_jobspy(
                search_term=term,
                location="India",
                sites=["linkedin", "indeed", "glassdoor"],
                results_per_site=15
            )
            all_jobs.extend(jobs)
            print(f"      ✓ '{term}': {len(jobs)} jobs")
            await asyncio.sleep(2)  # Respect rate limits
        except Exception as e:
            print(f"      ✗ '{term}': {str(e)[:30]}")
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['job_title']}_{job['company_name']}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"   ✅ Found {len(unique_jobs)} unique jobs via JobSpy")
    return unique_jobs

# Alternative: Direct API scraper for when JobSpy is not installed
async def scrape_linkedin_direct(keyword: str, location: str = "India") -> List[Dict]:
    """
    Fallback LinkedIn scraper using public job search
    """
    import httpx
    
    jobs = []
    
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": keyword,
        "location": location,
        "start": 0,
        "count": 25,
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                # Parse HTML response for job cards
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for card in soup.select('.job-search-card'):
                    try:
                        title = card.select_one('.base-search-card__title')
                        company = card.select_one('.base-search-card__subtitle')
                        location = card.select_one('.job-search-card__location')
                        link = card.select_one('a.base-card__full-link')
                        
                        jobs.append({
                            "job_title": title.text.strip() if title else "Unknown",
                            "company_name": company.text.strip() if company else "Unknown",
                            "location": location.text.strip() if location else "India",
                            "job_description": "",
                            "source": "linkedin_direct",
                            "source_url": link.get('href', '') if link else "",
                            "posted_date": str(datetime.now().date()),
                        })
                    except Exception:
                        continue
    except Exception as e:
        print(f"   LinkedIn direct error: {e}")
    
    return jobs

# For testing
if __name__ == "__main__":
    async def test():
        jobs = await scrape_jobspy_all(["python developer", "react developer"])
        print(f"\nTotal: {len(jobs)} jobs")
        for job in jobs[:5]:
            print(f"  - {job['job_title']} at {job['company_name']} ({job['source']})")
    
    asyncio.run(test())
