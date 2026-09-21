"""
Jobright.ai Scraper - Premium job discovery
Scrapes jobs from Jobright.ai platform with stealth techniques
"""
import asyncio
import httpx
import random
import json
from typing import List, Dict
from datetime import datetime
import re

# Stealth headers for Jobright
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_stealth_headers():
    """Generate realistic browser headers"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://jobright.ai/",
        "Origin": "https://jobright.ai",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",
    }

# Job categories to search
JOBRIGHT_CATEGORIES = [
    "Full Stack Engineer",
    "React Developer",
    "Frontend Developer",
    "Backend Developer",
    "Software Engineer",
    "Software Developer",
    "Web Developer",
    "Python Developer",
    "JavaScript Developer",
    "Node.js Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Software Engineer Intern",
    "Frontend Intern",
    "Backend Intern",
    "Data Science Intern",
]

async def fetch_jobright_jobs(keyword: str, location: str = "United States") -> List[Dict]:
    """Fetch jobs from Jobright.ai API"""
    jobs = []
    
    # Jobright API endpoint (discovered from network inspection)
    api_url = "https://jobright.ai/api/jobs/search"
    
    params = {
        "keyword": keyword,
        "location": location,
        "page": 1,
        "limit": 20,
        "remote": "true",  # Include remote jobs
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Random delay for stealth
            await asyncio.sleep(random.uniform(1, 3))
            
            response = await client.get(
                api_url,
                params=params,
                headers=get_stealth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse jobs from response
                if isinstance(data, dict) and "jobs" in data:
                    for job in data["jobs"]:
                        jobs.append(parse_jobright_job(job))
                elif isinstance(data, list):
                    for job in data:
                        jobs.append(parse_jobright_job(job))
                        
            elif response.status_code == 403:
                print(f"   ⚠️ Jobright blocked: {keyword}")
            else:
                print(f"   ⚠️ Jobright status {response.status_code}: {keyword}")
                
    except httpx.ConnectError:
        print(f"   ⚠️ Jobright connection error")
    except Exception as e:
        print(f"   ⚠️ Jobright error: {str(e)[:50]}")
    
    return jobs

def parse_jobright_job(job: Dict) -> Dict:
    """Parse Jobright job into our format"""
    return {
        "job_title": job.get("title") or job.get("jobTitle") or "Unknown",
        "company_name": job.get("company") or job.get("companyName") or "Unknown",
        "location": job.get("location") or "Remote",
        "job_description": job.get("description") or job.get("jobDescription") or "",
        "source": "jobright",
        "source_url": job.get("url") or job.get("jobUrl") or f"https://jobright.ai/jobs/{job.get('id', '')}",
        "posted_date": job.get("postedDate") or job.get("posted_at") or str(datetime.now()),
        "salary_range": job.get("salary") or job.get("salaryRange") or "",
        "job_type": job.get("jobType") or job.get("employmentType") or "Full-time",
        "match_score": job.get("matchScore") or job.get("score") or 0,
        "experience_level": job.get("experienceLevel") or job.get("level") or "",
        "skills": job.get("skills") or job.get("requiredSkills") or [],
        "company_logo": job.get("companyLogo") or job.get("logo") or "",
        "company_info": {
            "industry": job.get("industry") or "",
            "size": job.get("companySize") or "",
            "founded": job.get("founded") or "",
            "website": job.get("companyWebsite") or "",
        }
    }

async def scrape_jobright_web(keyword: str) -> List[Dict]:
    """Alternative: Scrape Jobright web pages"""
    jobs = []
    
    # Web page URL
    search_url = f"https://jobright.ai/jobs?keyword={keyword.replace(' ', '%20')}"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            await asyncio.sleep(random.uniform(2, 4))
            
            response = await client.get(
                search_url,
                headers=get_stealth_headers(),
                follow_redirects=True
            )
            
            if response.status_code == 200:
                html = response.text
                
                # Try to extract Next.js data
                data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>', html)
                if data_match:
                    try:
                        next_data = json.loads(data_match.group(1))
                        props = next_data.get("props", {}).get("pageProps", {})
                        
                        if "jobs" in props:
                            for job in props["jobs"][:20]:
                                jobs.append(parse_jobright_job(job))
                    except json.JSONDecodeError:
                        pass
                        
    except Exception as e:
        print(f"   ⚠️ Jobright web scrape error: {str(e)[:50]}")
    
    return jobs

async def scrape_jobright(user_keywords: List[str] = None) -> List[Dict]:
    """
    Main function to scrape Jobright.ai
    Returns list of jobs in our standard format
    """
    all_jobs = []
    
    # Use user keywords or default categories
    search_terms = user_keywords[:5] if user_keywords else JOBRIGHT_CATEGORIES[:6]
    
    print(f"   🔍 Searching Jobright for: {', '.join(search_terms[:3])}...")
    
    for keyword in search_terms:
        # Try API first
        jobs = await fetch_jobright_jobs(keyword)
        
        # If API blocked, try web scraping
        if not jobs:
            jobs = await scrape_jobright_web(keyword)
        
        all_jobs.extend(jobs)
        
        # Random delay between searches
        await asyncio.sleep(random.uniform(1, 2))
    
    # Deduplicate by title + company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['job_title']}_{job['company_name']}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"   ✅ Found {len(unique_jobs)} unique jobs from Jobright")
    return unique_jobs

# For testing
if __name__ == "__main__":
    async def test():
        jobs = await scrape_jobright(["React Developer", "Software Engineer"])
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:5]:
            print(f"  - {job['job_title']} at {job['company_name']}")
    
    asyncio.run(test())
