# backend/app/discovery/platforms/premium_scrapers.py
"""
Premium Platform Scrapers (14 Platforms)
These are higher-end platforms with curated remote jobs.
Some require more sophisticated scraping techniques.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
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


async def fetch_page(url: str, timeout: int = 30) -> BeautifulSoup:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
    except:
        pass
    return None


async def fetch_json(url: str, timeout: int = 30) -> dict:
    try:
        headers = {**HEADERS, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return None


# =============================================================================
# 1. TURING - Has API-like data in page
# =============================================================================
async def scrape_turing() -> List[Dict]:
    """Turing remote developer jobs"""
    jobs = []
    soup = await fetch_page("https://www.turing.com/remote-developer-jobs")
    
    if soup:
        # Look for job listings
        for card in soup.select('[class*="job"], [class*="opportunity"], article, [class*="position"]')[:30]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5 and 'Turing' not in title:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company="Turing Client",
                        location="Remote Worldwide",
                        source="turing",
                        url=link['href'] if link else ""
                    ))
        
        # Also try to extract from script tags (JSON data)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                    jobs.append(create_job(
                        title=data.get('title', ''),
                        company=data.get('hiringOrganization', {}).get('name', 'Turing'),
                        location=data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Remote'),
                        source="turing",
                        url=data.get('url', ''),
                        description=data.get('description', '')[:1000]
                    ))
            except:
                pass
        
        print(f"   ✅ Turing: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Turing: Failed to fetch")
    
    return jobs


# =============================================================================
# 2. WELLFOUND (AngelList) - API approach
# =============================================================================
async def scrape_wellfound_api() -> List[Dict]:
    """WellFound/AngelList jobs via GraphQL-like API"""
    jobs = []
    
    # Try the public jobs page
    soup = await fetch_page("https://wellfound.com/jobs")
    
    if soup:
        for card in soup.select('[class*="styles_result"], [class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Startup",
                        location="Remote",
                        source="wellfound",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ WellFound: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ WellFound: Failed to fetch (may need Playwright)")
    
    return jobs


# =============================================================================
# 3. VANHACK
# =============================================================================
async def scrape_vanhack() -> List[Dict]:
    """VanHack jobs for relocation/remote"""
    jobs = []
    soup = await fetch_page("https://vanhack.com/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="position"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "VanHack Client",
                        location="Remote/Relocation",
                        source="vanhack",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ VanHack: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ VanHack: Failed to fetch")
    
    return jobs


# =============================================================================
# 4. SNAPHUNT
# =============================================================================
async def scrape_snaphunt() -> List[Dict]:
    """SnapHunt APAC region jobs"""
    jobs = []
    soup = await fetch_page("https://snaphunt.com/job-listing?remote=true")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="listing"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "SnapHunt",
                        location="Remote APAC",
                        source="snaphunt",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ SnapHunt: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ SnapHunt: Failed to fetch")
    
    return jobs


# =============================================================================
# 5. HIRED
# =============================================================================
async def scrape_hired() -> List[Dict]:
    """Hired - curated tech talent marketplace"""
    jobs = []
    soup = await fetch_page("https://hired.com/talent")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="position"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Hired Company",
                        location="Remote",
                        source="hired"
                    ))
        
        print(f"   ✅ Hired: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Hired: Failed to fetch")
    
    return jobs


# =============================================================================
# 6. SOSHACE
# =============================================================================
async def scrape_soshace() -> List[Dict]:
    """Soshace remote dev jobs"""
    jobs = []
    soup = await fetch_page("https://soshace.com/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Soshace",
                        location="Remote",
                        source="soshace"
                    ))
        
        print(f"   ✅ Soshace: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Soshace: Failed to fetch")
    
    return jobs


# =============================================================================
# 7. STRIDER
# =============================================================================
async def scrape_strider() -> List[Dict]:
    """Strider remote dev jobs"""
    jobs = []
    soup = await fetch_page("https://www.onstrider.com/")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="role"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Strider",
                        location="Remote",
                        source="strider"
                    ))
        
        print(f"   ✅ Strider: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Strider: Failed to fetch")
    
    return jobs


# =============================================================================
# 8. POWERTOFLY
# =============================================================================
async def scrape_powertofly() -> List[Dict]:
    """PowerToFly jobs"""
    jobs = []
    soup = await fetch_page("https://powertofly.com/jobs/")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="JobCard"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "PowerToFly",
                        location="Remote",
                        source="powertofly",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ PowerToFly: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ PowerToFly: Failed to fetch")
    
    return jobs


# =============================================================================
# 9. REMOTE100K
# =============================================================================
async def scrape_remote100k() -> List[Dict]:
    """Remote100K - High paying remote jobs"""
    jobs = []
    soup = await fetch_page("https://remote100k.com/")
    
    if soup:
        for card in soup.select('[class*="job"], article, [class*="listing"]')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Remote100K",
                        location="Remote",
                        source="remote100k",
                        url=link['href'] if link else ""
                    ))
                    jobs[-1]["salary_min"] = 100000  # Minimum $100k
        
        print(f"   ✅ Remote100K: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Remote100K: Failed to fetch")
    
    return jobs


# =============================================================================
# 10. LEVELS.FYI JOBS
# =============================================================================
async def scrape_levelsfyi() -> List[Dict]:
    """Levels.fyi job board"""
    jobs = []
    soup = await fetch_page("https://www.levels.fyi/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="JobCard"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Levels.fyi",
                        location="Remote",
                        source="levelsfyi",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Levels.fyi: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Levels.fyi: Failed to fetch (JS required)")
    
    return jobs


# =============================================================================
# 11. WORK AT A STARTUP (Y Combinator)
# =============================================================================
async def scrape_workatastartup() -> List[Dict]:
    """Y Combinator Work at a Startup"""
    jobs = []
    soup = await fetch_page("https://www.workatastartup.com/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="company"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "YC Startup",
                        location="Remote",
                        source="workatastartup",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Work at a Startup: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Work at a Startup: Failed to fetch")
    
    return jobs


# =============================================================================
# 12. REMOTE.COM
# =============================================================================
async def scrape_remotecom() -> List[Dict]:
    """Remote.com job listings"""
    jobs = []
    soup = await fetch_page("https://remote.com/jobs/all")
    
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
                        company=company_el.get_text(strip=True) if company_el else "Remote.com",
                        location="Remote",
                        source="remotecom",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Remote.com: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Remote.com: Failed to fetch")
    
    return jobs


# =============================================================================
# 13. REMOTEYEAH
# =============================================================================
async def scrape_remoteyeah() -> List[Dict]:
    """RemoteYeah job listings"""
    jobs = []
    soup = await fetch_page("https://remoteyeah.com/")
    
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
                        company=company_el.get_text(strip=True) if company_el else "RemoteYeah",
                        location="Remote",
                        source="remoteyeah",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ RemoteYeah: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ RemoteYeah: Failed to fetch")
    
    return jobs


# =============================================================================
# 14. FLEXJOBS
# =============================================================================
async def scrape_flexjobs() -> List[Dict]:
    """FlexJobs - Premium remote job board"""
    jobs = []
    soup = await fetch_page("https://www.flexjobs.com/remote-jobs/computer-it")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="listing"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "FlexJobs",
                        location="Remote",
                        source="flexjobs",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ FlexJobs: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ FlexJobs: Failed to fetch")
    
    return jobs


# =============================================================================
# MAIN FUNCTION
# =============================================================================
async def scrape_all_premium_platforms() -> List[Dict]:
    """Run all premium scrapers"""
    print("\n💎 Scraping premium platforms...")
    
    batch1 = await asyncio.gather(
        scrape_turing(),
        scrape_wellfound_api(),
        scrape_vanhack(),
        scrape_snaphunt(),
        scrape_hired(),
        return_exceptions=True
    )
    
    await asyncio.sleep(1)
    
    batch2 = await asyncio.gather(
        scrape_soshace(),
        scrape_strider(),
        scrape_powertofly(),
        scrape_remote100k(),
        scrape_levelsfyi(),
        return_exceptions=True
    )
    
    await asyncio.sleep(1)
    
    batch3 = await asyncio.gather(
        scrape_workatastartup(),
        scrape_remotecom(),
        scrape_remoteyeah(),
        scrape_flexjobs(),
        return_exceptions=True
    )
    
    all_jobs = []
    for batch in [batch1, batch2, batch3]:
        for result in batch:
            if isinstance(result, list):
                all_jobs.extend(result)
    
    print(f"   📊 Premium Platforms Total: {len(all_jobs)} jobs\n")
    return all_jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape_all_premium_platforms())
    print(f"\nTotal: {len(jobs)} jobs")
