# backend/app/discovery/platforms/api_scrapers.py
"""
API-Based Scrapers - Most Reliable (4 Platforms)
These have public APIs that return JSON data.
"""
import asyncio
import httpx
from typing import List, Dict
from datetime import datetime

# Common headers to avoid blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


def create_job(title: str, company: str, location: str, source: str, url: str = "", description: str = "") -> Dict:
    """Standardized job dict creator"""
    return {
        "job_title": str(title)[:150].strip(),
        "company_name": str(company)[:100].strip() or "Unknown",
        "location": str(location)[:80].strip() or "Remote",
        "source": source,
        "source_url": url,
        "job_description": description[:3000] if description else f"{title} at {company} - Remote opportunity via {source}",
        "posted_date": str(datetime.now().date()),
    }


# =============================================================================
# 1. REMOTEOK - Public API (No Auth Required)
# =============================================================================
async def scrape_remoteok() -> List[Dict]:
    """
    RemoteOK API - Returns JSON array of jobs
    URL: https://remoteok.com/api
    Rate Limit: Be gentle, ~1 req/sec
    """
    jobs = []
    url = "https://remoteok.com/api"
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                # First item is metadata, skip it
                for item in data[1:80]:  # Get up to 80 jobs
                    if isinstance(item, dict) and item.get("position"):
                        # Extract salary if available
                        salary_min = item.get("salary_min")
                        salary_max = item.get("salary_max")
                        
                        job = create_job(
                            title=item.get("position", ""),
                            company=item.get("company", "Unknown"),
                            location=item.get("location", "Remote Worldwide"),
                            source="remoteok",
                            url=item.get("url", f"https://remoteok.com/{item.get('slug', '')}"),
                            description=item.get("description", "")
                        )
                        
                        # Add salary info
                        if salary_min:
                            job["salary_min"] = int(salary_min)
                        if salary_max:
                            job["salary_max"] = int(salary_max)
                        job["salary_type"] = "yearly"
                        
                        # Add tags as skills
                        tags = item.get("tags", [])
                        if tags:
                            job["skills"] = tags[:10]
                        
                        jobs.append(job)
                        
                print(f"   ✅ RemoteOK: {len(jobs)} jobs")
            else:
                print(f"   ⚠️ RemoteOK: Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ RemoteOK error: {str(e)[:50]}")
    
    return jobs


# =============================================================================
# 2. REMOTIVE - Public API
# =============================================================================
async def scrape_remotive() -> List[Dict]:
    """
    Remotive API - Well-documented public API
    URL: https://remotive.com/api/remote-jobs
    Optional filters: ?category=software-dev&limit=100
    """
    jobs = []
    url = "https://remotive.com/api/remote-jobs?limit=100"
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("jobs", [])[:80]:
                    job = create_job(
                        title=item.get("title", ""),
                        company=item.get("company_name", "Unknown"),
                        location=item.get("candidate_required_location", "Worldwide"),
                        source="remotive",
                        url=item.get("url", ""),
                        description=item.get("description", "")
                    )
                    
                    # Remotive provides category
                    category = item.get("category", "")
                    if category:
                        job["category"] = category
                    
                    # Job type
                    job_type = item.get("job_type", "")
                    if job_type:
                        job["work_mode"] = "remote"
                        job["employment_type"] = job_type
                    
                    # Publication date
                    pub_date = item.get("publication_date", "")
                    if pub_date:
                        job["posted_date"] = pub_date[:10]
                    
                    jobs.append(job)
                
                print(f"   ✅ Remotive: {len(jobs)} jobs")
            else:
                print(f"   ⚠️ Remotive: Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Remotive error: {str(e)[:50]}")
    
    return jobs


# =============================================================================
# 3. WORKING NOMADS - Public API
# =============================================================================
async def scrape_workingnomads() -> List[Dict]:
    """
    Working Nomads API
    URL: https://www.workingnomads.com/api/exposed_jobs/
    Returns remote jobs for digital nomads
    """
    jobs = []
    url = "https://www.workingnomads.com/api/exposed_jobs/"
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both list and dict response
                items = data if isinstance(data, list) else data.get("jobs", [])
                
                for item in items[:80]:
                    if not isinstance(item, dict):
                        continue
                        
                    job = create_job(
                        title=item.get("title", ""),
                        company=item.get("company_name", "Unknown"),
                        location="Remote Worldwide",
                        source="workingnomads",
                        url=item.get("url", ""),
                        description=item.get("description", "")
                    )
                    
                    # Category
                    category = item.get("category_name", "")
                    if category:
                        job["category"] = category
                    
                    # Publication date
                    pub_date = item.get("pub_date", "")
                    if pub_date:
                        job["posted_date"] = pub_date[:10]
                    
                    jobs.append(job)
                
                print(f"   ✅ Working Nomads: {len(jobs)} jobs")
            else:
                print(f"   ⚠️ Working Nomads: Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Working Nomads error: {str(e)[:50]}")
    
    return jobs


# =============================================================================
# 4. HIMALAYAS - Public API with Good Filtering
# =============================================================================
async def scrape_himalayas() -> List[Dict]:
    """
    Himalayas.app API - Modern remote job board
    URL: https://himalayas.app/jobs/api?limit=100
    Excellent API with detailed job info
    """
    jobs = []
    url = "https://himalayas.app/jobs/api?limit=100"
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("jobs", [])[:80]:
                    # Build job URL
                    slug = item.get("slug", "")
                    company_slug = item.get("companySlug", "")
                    job_url = f"https://himalayas.app/companies/{company_slug}/jobs/{slug}" if slug and company_slug else ""
                    
                    job = create_job(
                        title=item.get("title", ""),
                        company=item.get("companyName", "Unknown"),
                        location=item.get("locationRestrictions", "Worldwide"),
                        source="himalayas",
                        url=item.get("applicationLink", job_url),
                        description=item.get("description", "")
                    )
                    
                    # Salary info (Himalayas provides this well)
                    salary_min = item.get("minSalary")
                    salary_max = item.get("maxSalary")
                    if salary_min:
                        job["salary_min"] = int(salary_min)
                    if salary_max:
                        job["salary_max"] = int(salary_max)
                    job["salary_type"] = "yearly"
                    
                    # Categories
                    categories = item.get("categories", [])
                    if categories:
                        job["categories"] = categories
                    
                    # Seniority
                    seniority = item.get("seniority", "")
                    if seniority:
                        job["experience_required"] = seniority
                    
                    jobs.append(job)
                
                print(f"   ✅ Himalayas: {len(jobs)} jobs")
            else:
                print(f"   ⚠️ Himalayas: Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Himalayas error: {str(e)[:50]}")
    
    return jobs


# =============================================================================
# MAIN FUNCTION - Run all API scrapers
# =============================================================================
async def scrape_all_api_platforms() -> List[Dict]:
    """Run all API-based scrapers concurrently"""
    print("\n📡 Scraping API-based platforms...")
    
    results = await asyncio.gather(
        scrape_remoteok(),
        scrape_remotive(),
        scrape_workingnomads(),
        scrape_himalayas(),
        return_exceptions=True
    )
    
    all_jobs = []
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
        elif isinstance(result, Exception):
            print(f"   ⚠️ Scraper exception: {str(result)[:50]}")
    
    print(f"   📊 API Platforms Total: {len(all_jobs)} jobs\n")
    return all_jobs


# For testing
if __name__ == "__main__":
    jobs = asyncio.run(scrape_all_api_platforms())
    print(f"\nTotal: {len(jobs)} jobs")
    for j in jobs[:5]:
        print(f"  • {j['job_title'][:40]} @ {j['company_name']} ({j['source']})")
