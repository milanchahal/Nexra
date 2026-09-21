# backend/app/discovery/platforms/web_scrapers.py
"""
Web Scrapers - HTTP + BeautifulSoup (14 Platforms)
These sites can be scraped with standard HTTP requests.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}


def create_job(title: str, company: str, location: str, source: str, url: str = "", description: str = "") -> Dict:
    return {
        "job_title": str(title)[:150].strip(),
        "company_name": str(company)[:100].strip() or "Unknown",
        "location": str(location)[:80].strip() or "Remote",
        "source": source,
        "source_url": url,
        "job_description": description[:3000] if description else f"{title} at {company} - Remote via {source}",
        "posted_date": str(datetime.now().date()),
    }


async def fetch_page(url: str, timeout: int = 25) -> BeautifulSoup:
    """Fetch page and return BeautifulSoup object"""
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        pass
    return None


# =============================================================================
# 1. ARC.DEV
# =============================================================================
async def scrape_arcdev() -> List[Dict]:
    """Arc.dev remote jobs"""
    jobs = []
    soup = await fetch_page("https://arc.dev/remote-jobs")
    
    if soup:
        # Find job cards
        for card in soup.select('a[href*="/remote-jobs/"]')[:30]:
            href = card.get('href', '')
            if '/remote-jobs/' in href and 'details' not in href:
                continue
            
            title = card.get_text(strip=True)
            if len(title) > 5 and len(title) < 150:
                job_url = f"https://arc.dev{href}" if href.startswith('/') else href
                jobs.append(create_job(
                    title=title,
                    company="Arc.dev Partner",
                    location="Remote",
                    source="arcdev",
                    url=job_url
                ))
        
        print(f"   ✅ Arc.dev: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Arc.dev: Failed to fetch")
    
    return jobs


# =============================================================================
# 2. JUSTREMOTE
# =============================================================================
async def scrape_justremote() -> List[Dict]:
    """JustRemote developer jobs"""
    jobs = []
    urls = [
        "https://justremote.co/remote-developer-jobs",
        "https://justremote.co/remote-software-engineer-jobs",
    ]
    
    for url in urls:
        soup = await fetch_page(url)
        if soup:
            for card in soup.select('[class*="job"], article, [class*="listing"]')[:20]:
                title_el = card.find(['h2', 'h3', 'h4', 'a'])
                company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
                link = card.find('a', href=True)
                
                if title_el:
                    title = title_el.get_text(strip=True)
                    if len(title) > 5:
                        jobs.append(create_job(
                            title=title,
                            company=company_el.get_text(strip=True) if company_el else "JustRemote",
                            location="Remote",
                            source="justremote",
                            url=link['href'] if link else ""
                        ))
        
        await asyncio.sleep(0.5)
    
    print(f"   ✅ JustRemote: {len(jobs)} jobs")
    return jobs


# =============================================================================
# 3. JS REMOTELY
# =============================================================================
async def scrape_jsremotely() -> List[Dict]:
    """JS Remotely - JavaScript focused jobs"""
    jobs = []
    soup = await fetch_page("https://jsremotely.com/")
    
    if soup:
        for card in soup.select('[class*="job"], article, .job-post, .listing')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "JS Remotely",
                        location="Remote",
                        source="jsremotely",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ JS Remotely: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ JS Remotely: Failed to fetch")
    
    return jobs


# =============================================================================
# 4. HUBSTAFF TALENT
# =============================================================================
async def scrape_hubstaff() -> List[Dict]:
    """Hubstaff Talent job search"""
    jobs = []
    soup = await fetch_page("https://talent.hubstaff.com/search/jobs?search%5Bkeywords%5D=developer")
    
    if soup:
        for card in soup.select('.job-card, [class*="search-result"], article, .job-listing')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Hubstaff",
                        location="Remote",
                        source="hubstaff",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Hubstaff: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Hubstaff: Failed to fetch")
    
    return jobs


# =============================================================================
# 5. LANDING.JOBS
# =============================================================================
async def scrape_landingjobs() -> List[Dict]:
    """Landing.jobs - EU remote jobs"""
    jobs = []
    soup = await fetch_page("https://landing.jobs/jobs?remote=true&page=1")
    
    if soup:
        for card in soup.select('[class*="job"], article, .job-card')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5 and 'Landing.jobs' not in title:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Landing.jobs",
                        location="Remote EU",
                        source="landingjobs",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Landing.jobs: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Landing.jobs: Failed to fetch")
    
    return jobs


# =============================================================================
# 6. PANGIAN
# =============================================================================
async def scrape_pangian() -> List[Dict]:
    """Pangian remote jobs"""
    jobs = []
    soup = await fetch_page("https://pangian.com/job-travel-remote/")
    
    if soup:
        for card in soup.select('[class*="job"], article, .job-listing')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Pangian",
                        location="Remote",
                        source="pangian",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Pangian: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Pangian: Failed to fetch")
    
    return jobs


# =============================================================================
# 7. 4 DAY WEEK
# =============================================================================
async def scrape_fourdayweek() -> List[Dict]:
    """4 Day Week remote jobs"""
    jobs = []
    soup = await fetch_page("https://4dayweek.io/remote-jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article, a[href*="/job/"]')[:25]:
            title_el = card.find(['h2', 'h3', 'h4']) or card
            
            title = title_el.get_text(strip=True) if hasattr(title_el, 'get_text') else str(title_el.string or '')
            if len(title) > 5 and len(title) < 150:
                link = card.get('href') if card.get('href') else (card.find('a', href=True) or {}).get('href', '')
                jobs.append(create_job(
                    title=title,
                    company="4 Day Week Company",
                    location="Remote",
                    source="4dayweek",
                    url=f"https://4dayweek.io{link}" if link and link.startswith('/') else link
                ))
        
        print(f"   ✅ 4 Day Week: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ 4 Day Week: Failed to fetch")
    
    return jobs


# =============================================================================
# 8. SKIPTHEDRIVE
# =============================================================================
async def scrape_skipthedrive() -> List[Dict]:
    """SkipTheDrive remote jobs"""
    jobs = []
    soup = await fetch_page("https://www.skipthedrive.com/jobs/")
    
    if soup:
        for link in soup.select('a[href*="/job/"], [class*="job"] a')[:25]:
            title = link.get_text(strip=True)
            if len(title) > 5 and len(title) < 150:
                jobs.append(create_job(
                    title=title,
                    company="SkipTheDrive",
                    location="Remote",
                    source="skipthedrive",
                    url=link.get('href', '')
                ))
        
        print(f"   ✅ SkipTheDrive: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ SkipTheDrive: Failed to fetch")
    
    return jobs


# =============================================================================
# 9. TOTALJOBS (UK)
# =============================================================================
async def scrape_totaljobs() -> List[Dict]:
    """TotalJobs UK remote jobs"""
    jobs = []
    soup = await fetch_page("https://www.totaljobs.com/jobs/remote-software-developer")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "TotalJobs",
                        location="UK Remote",
                        source="totaljobs",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ TotalJobs: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ TotalJobs: Failed to fetch")
    
    return jobs


# =============================================================================
# 10. GUN.IO
# =============================================================================
async def scrape_gunio() -> List[Dict]:
    """Gun.io freelance jobs"""
    jobs = []
    soup = await fetch_page("https://gun.io/find-work/")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="opportunity"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company="Gun.io Client",
                        location="Remote",
                        source="gunio",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Gun.io: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Gun.io: Failed to fetch")
    
    return jobs


# =============================================================================
# 11. IDEALIST
# =============================================================================
async def scrape_idealist() -> List[Dict]:
    """Idealist non-profit remote jobs"""
    jobs = []
    soup = await fetch_page("https://www.idealist.org/en/jobs?locationType=REMOTE&q=developer")
    
    if soup:
        for card in soup.select('[class*="job"], article, [data-testid*="job"]')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and ('org' in str(x).lower() or 'company' in str(x).lower()))
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Idealist Org",
                        location="Remote",
                        source="idealist",
                        url=link['href'] if link and link['href'].startswith('http') else f"https://www.idealist.org{link['href']}" if link else ""
                    ))
        
        print(f"   ✅ Idealist: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Idealist: Failed to fetch")
    
    return jobs


# =============================================================================
# MAIN FUNCTION
# =============================================================================
async def scrape_all_web_platforms() -> List[Dict]:
    """Run all web scrapers with rate limiting"""
    print("\n🌐 Scraping web-based platforms...")
    
    # Run in batches to avoid overwhelming
    batch1 = await asyncio.gather(
        scrape_arcdev(),
        scrape_justremote(),
        scrape_jsremotely(),
        scrape_hubstaff(),
        return_exceptions=True
    )
    
    await asyncio.sleep(1)
    
    batch2 = await asyncio.gather(
        scrape_landingjobs(),
        scrape_pangian(),
        scrape_fourdayweek(),
        scrape_skipthedrive(),
        return_exceptions=True
    )
    
    await asyncio.sleep(1)
    
    batch3 = await asyncio.gather(
        scrape_totaljobs(),
        scrape_gunio(),
        scrape_idealist(),
        return_exceptions=True
    )
    
    all_jobs = []
    for batch in [batch1, batch2, batch3]:
        for result in batch:
            if isinstance(result, list):
                all_jobs.extend(result)
    
    print(f"   📊 Web Platforms Total: {len(all_jobs)} jobs\n")
    return all_jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape_all_web_platforms())
    print(f"\nTotal: {len(jobs)} jobs")
