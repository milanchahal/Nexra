# backend/app/discovery/platforms/rss_scrapers.py
"""
RSS-Based Scrapers - Very Reliable (5 Platforms)
These platforms provide RSS feeds which are stable and easy to parse.
"""
import asyncio
import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml",
}


def create_job(title: str, company: str, location: str, source: str, url: str = "", description: str = "") -> Dict:
    """Standardized job dict"""
    return {
        "job_title": str(title)[:150].strip(),
        "company_name": str(company)[:100].strip() or "Unknown",
        "location": str(location)[:80].strip() or "Remote",
        "source": source,
        "source_url": url,
        "job_description": description[:3000] if description else f"{title} at {company} - via {source}",
        "posted_date": str(datetime.now().date()),
    }


def clean_html(text: str) -> str:
    """Remove HTML tags from string"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()[:2000]


# =============================================================================
# 1. WE WORK REMOTELY - RSS Feeds (Multiple Categories)
# =============================================================================
async def scrape_weworkremotely_rss() -> List[Dict]:
    """
    We Work Remotely - Multiple RSS feeds for different categories
    Very reliable, well-structured RSS
    """
    jobs = []
    
    # RSS feeds for different categories
    feeds = [
        ("https://weworkremotely.com/categories/remote-programming-jobs.rss", "Programming"),
        ("https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss", "DevOps"),
        ("https://weworkremotely.com/categories/remote-front-end-programming-jobs.rss", "Frontend"),
        ("https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss", "Backend"),
        ("https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss", "Full Stack"),
    ]
    
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for feed_url, category in feeds:
            try:
                response = await client.get(feed_url, headers=HEADERS)
                
                if response.status_code == 200:
                    # Parse XML
                    root = ET.fromstring(response.text)
                    
                    for item in root.findall('.//item')[:20]:
                        title_el = item.find('title')
                        link_el = item.find('link')
                        desc_el = item.find('description')
                        pub_date_el = item.find('pubDate')
                        
                        if title_el is not None and title_el.text:
                            full_title = title_el.text.strip()
                            
                            # WWR format: "Company: Job Title"
                            if ':' in full_title:
                                parts = full_title.split(':', 1)
                                company = parts[0].strip()
                                title = parts[1].strip()
                            else:
                                company = "We Work Remotely"
                                title = full_title
                            
                            job = create_job(
                                title=title,
                                company=company,
                                location="Remote",
                                source="weworkremotely",
                                url=link_el.text.strip() if link_el is not None else "",
                                description=clean_html(desc_el.text) if desc_el is not None else ""
                            )
                            
                            job["category"] = category
                            job["work_mode"] = "remote"
                            
                            if pub_date_el is not None:
                                # Parse RSS date format
                                try:
                                    job["posted_date"] = pub_date_el.text[:16]
                                except:
                                    pass
                            
                            jobs.append(job)
                            
                await asyncio.sleep(0.5)  # Be nice to the server
                
            except Exception as e:
                print(f"   ⚠️ WWR {category} feed error: {str(e)[:30]}")
    
    print(f"   ✅ We Work Remotely (RSS): {len(jobs)} jobs")
    return jobs


# =============================================================================
# 2. AUTHENTIC JOBS - RSS Feed
# =============================================================================
async def scrape_authenticjobs_rss() -> List[Dict]:
    """
    Authentic Jobs RSS
    URL: https://authenticjobs.com/rss/
    """
    jobs = []
    url = "https://authenticjobs.com/?feed=job_feed"
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                for item in root.findall('.//item')[:30]:
                    title_el = item.find('title')
                    link_el = item.find('link')
                    desc_el = item.find('description')
                    
                    if title_el is not None and title_el.text:
                        job = create_job(
                            title=title_el.text.strip(),
                            company="AuthenticJobs Company",
                            location="Remote",
                            source="authenticjobs",
                            url=link_el.text.strip() if link_el is not None else "",
                            description=clean_html(desc_el.text) if desc_el is not None else ""
                        )
                        jobs.append(job)
                
                print(f"   ✅ AuthenticJobs (RSS): {len(jobs)} jobs")
            else:
                print(f"   ⚠️ AuthenticJobs: Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ AuthenticJobs error: {str(e)[:50]}")
    
    return jobs


# =============================================================================
# 3. JOBSPRESSO - RSS Feed
# =============================================================================
async def scrape_jobspresso_rss() -> List[Dict]:
    """
    Jobspresso RSS Feed
    URL: https://jobspresso.co/feed/
    """
    jobs = []
    url = "https://jobspresso.co/feed/"
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                for item in root.findall('.//item')[:30]:
                    title_el = item.find('title')
                    link_el = item.find('link')
                    desc_el = item.find('description')
                    
                    if title_el is not None and title_el.text:
                        title = title_el.text.strip()
                        
                        # Try to extract company from title
                        company = "Jobspresso Company"
                        if ' at ' in title:
                            parts = title.split(' at ', 1)
                            title = parts[0].strip()
                            company = parts[1].strip()
                        
                        job = create_job(
                            title=title,
                            company=company,
                            location="Remote",
                            source="jobspresso",
                            url=link_el.text.strip() if link_el is not None else "",
                            description=clean_html(desc_el.text) if desc_el is not None else ""
                        )
                        jobs.append(job)
                
                print(f"   ✅ Jobspresso (RSS): {len(jobs)} jobs")
            else:
                print(f"   ⚠️ Jobspresso: Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Jobspresso error: {str(e)[:50]}")
    
    return jobs


# =============================================================================
# 4. NODESK - RSS Feed
# =============================================================================
async def scrape_nodesk_rss() -> List[Dict]:
    """
    Nodesk RSS Feed
    URL: https://nodesk.co/remote-jobs/rss/
    """
    jobs = []
    url = "https://nodesk.co/remote-jobs/rss/"
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                for item in root.findall('.//item')[:30]:
                    title_el = item.find('title')
                    link_el = item.find('link')
                    desc_el = item.find('description')
                    
                    if title_el is not None and title_el.text:
                        job = create_job(
                            title=title_el.text.strip(),
                            company="Nodesk Company",
                            location="Remote",
                            source="nodesk",
                            url=link_el.text.strip() if link_el is not None else "",
                            description=clean_html(desc_el.text) if desc_el is not None else ""
                        )
                        jobs.append(job)
                
                print(f"   ✅ Nodesk (RSS): {len(jobs)} jobs")
            else:
                print(f"   ⚠️ Nodesk: Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Nodesk error: {str(e)[:50]}")
    
    return jobs


# =============================================================================
# MAIN FUNCTION
# =============================================================================
async def scrape_all_rss_platforms() -> List[Dict]:
    """Run all RSS-based scrapers"""
    print("\n📰 Scraping RSS-based platforms...")
    
    results = await asyncio.gather(
        scrape_weworkremotely_rss(),
        scrape_authenticjobs_rss(),
        scrape_jobspresso_rss(),
        scrape_nodesk_rss(),
        return_exceptions=True
    )
    
    all_jobs = []
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
    
    print(f"   📊 RSS Platforms Total: {len(all_jobs)} jobs\n")
    return all_jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape_all_rss_platforms())
    print(f"\nTotal: {len(jobs)} jobs")
