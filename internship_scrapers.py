# backend/app/discovery/platforms/internship_scrapers.py
"""
🎓 INTERNSHIP SCRAPERS FOR INDIAN STUDENTS
Specialized scrapers for summer internships - Perfect for DTU, IIT, NIT students

Platforms:
1. Internshala - #1 for Indian internships
2. Unstop (D2C) - College competitions & internships
3. LinkedIn Internships
4. Indeed Internships
5. HelloIntern
6. LetsIntern
7. Glassdoor Internships
8. AngelList/WellFound Startup Internships
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import random
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}

# DTU/Engineering student focused searches
INTERNSHIP_KEYWORDS = [
    "software development", "web development", "python", "react", "node",
    "machine learning", "data science", "full stack", "backend", "frontend",
    "java", "javascript", "android", "ios", "flutter", "django",
    "ai", "ml", "deep learning", "devops", "cloud"
]

# Indian locations
INDIA_LOCATIONS = [
    "Delhi", "Delhi NCR", "Bangalore", "Mumbai", "Hyderabad", 
    "Pune", "Chennai", "Gurgaon", "Noida", "Remote", "Work from Home"
]


def create_internship(title: str, company: str, location: str, source: str, url: str = "", description: str = "", stipend: str = "") -> Dict:
    """Standardized internship dict"""
    return {
        "job_title": f"{str(title)[:130].strip()} (Internship)",
        "company_name": str(company)[:100].strip() or "Unknown",
        "location": str(location)[:80].strip() or "India",
        "source": source,
        "source_url": url,
        "job_description": description[:3000] if description else f"{title} Internship at {company}",
        "posted_date": str(datetime.now().date()),
        "job_type": "internship",
        "employment_type": "internship",
        "stipend": stipend,
    }


async def fetch_page(url: str, timeout: int = 25) -> BeautifulSoup:
    try:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
    except:
        pass
    return None


# =============================================================================
# 1. INTERNSHALA - Best for Indian Students
# =============================================================================
async def scrape_internshala_enhanced() -> List[Dict]:
    """Enhanced Internshala scraper with multiple categories"""
    internships = []
    
    # Categories relevant for engineering students
    categories = [
        "software-development", "web-development", "python-django",
        "react", "machine-learning", "data-science", "full-stack-development",
        "java", "android-app-development", "backend-development"
    ]
    
    print("   🎓 Scraping Internshala (Enhanced)...")
    
    for category in categories[:6]:  # Limit to avoid rate limiting
        try:
            url = f"https://internshala.com/internships/{category}-internship"
            soup = await fetch_page(url)
            
            if soup:
                cards = soup.select('.internship_meta, .individual_internship, [class*="internship_"]')
                
                for card in cards[:10]:
                    try:
                        title_el = card.select_one('.profile, h3, .heading_4_5, [class*="profile"]')
                        company_el = card.select_one('.company_name, .company, .heading_6')
                        location_el = card.select_one('.location_link, .location, #location_names')
                        stipend_el = card.select_one('.stipend, [class*="stipend"]')
                        link_el = card.select_one('a[href*="/internship/"]')
                        
                        if title_el:
                            title = title_el.get_text(strip=True)
                            if len(title) > 3:
                                internship_url = f"https://internshala.com{link_el['href']}" if link_el and link_el.get('href') else url
                                
                                internships.append(create_internship(
                                    title=title,
                                    company=company_el.get_text(strip=True) if company_el else "Internshala Company",
                                    location=location_el.get_text(strip=True) if location_el else "India",
                                    source="internshala",
                                    url=internship_url,
                                    stipend=stipend_el.get_text(strip=True) if stipend_el else ""
                                ))
                    except:
                        continue
                        
        except Exception as e:
            continue
        
        await asyncio.sleep(1)
    
    print(f"   ✅ Internshala: {len(internships)} internships")
    return internships


# =============================================================================
# 2. UNSTOP (D2C) - College Competitions & Internships
# =============================================================================
async def scrape_unstop() -> List[Dict]:
    """Unstop (formerly Dare2Compete) - Popular among college students"""
    internships = []
    
    # API-like endpoint for internships
    url = "https://unstop.com/api/public/opportunity/search-result?opportunity=internships&oppstatus=open"
    
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True) as client:
            headers = {**HEADERS, "Accept": "application/json"}
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    opportunities = data.get('data', {}).get('data', [])
                    
                    for opp in opportunities[:30]:
                        if isinstance(opp, dict):
                            internships.append(create_internship(
                                title=opp.get('title', ''),
                                company=opp.get('organisation', {}).get('name', 'Unstop'),
                                location=opp.get('region', 'India'),
                                source="unstop",
                                url=f"https://unstop.com/internship/{opp.get('public_url', '')}",
                                description=opp.get('details', '')[:500]
                            ))
                except:
                    pass
                    
        print(f"   ✅ Unstop: {len(internships)} internships")
    except Exception as e:
        print(f"   ⚠️ Unstop: {str(e)[:30]}")
    
    # Fallback to web scraping
    if len(internships) == 0:
        soup = await fetch_page("https://unstop.com/internships")
        if soup:
            for card in soup.select('[class*="opportunity"], [class*="internship"], article')[:20]:
                title_el = card.find(['h2', 'h3', 'h4', 'a'])
                if title_el:
                    title = title_el.get_text(strip=True)
                    if len(title) > 5:
                        internships.append(create_internship(
                            title=title,
                            company="Unstop Partner",
                            location="India",
                            source="unstop"
                        ))
            print(f"   ✅ Unstop (fallback): {len(internships)} internships")
    
    return internships


# =============================================================================
# 3. LINKEDIN INTERNSHIPS (via JobSpy or direct)
# =============================================================================
async def scrape_linkedin_internships() -> List[Dict]:
    """
    Search LinkedIn for internships in India
    Uses public job search page
    """
    internships = []
    
    # LinkedIn public job search (no login required for viewing)
    searches = [
        ("software intern", "India"),
        ("developer intern", "Delhi NCR"),
        ("data science intern", "India"),
    ]
    
    print("   🔍 Searching LinkedIn Internships...")
    
    for term, location in searches[:2]:
        try:
            url = f"https://www.linkedin.com/jobs/search/?keywords={term.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_E=1"
            soup = await fetch_page(url)
            
            if soup:
                for card in soup.select('[class*="job"], [class*="result"], .jobs-search__results-list li')[:15]:
                    title_el = card.find(['h3', 'h4', 'a'])
                    company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
                    
                    if title_el:
                        title = title_el.get_text(strip=True)
                        if 'intern' in title.lower() and len(title) > 5:
                            internships.append(create_internship(
                                title=title,
                                company=company_el.get_text(strip=True) if company_el else "LinkedIn Company",
                                location=location,
                                source="linkedin_intern"
                            ))
                            
        except:
            continue
        
        await asyncio.sleep(1)
    
    print(f"   ✅ LinkedIn Internships: {len(internships)}")
    return internships


# =============================================================================
# 4. INDEED INTERNSHIPS INDIA
# =============================================================================
async def scrape_indeed_internships() -> List[Dict]:
    """Indeed internship listings for India"""
    internships = []
    
    searches = [
        "software intern", "developer intern", "data science intern",
        "python intern", "react intern", "ml intern"
    ]
    
    print("   🔍 Searching Indeed Internships...")
    
    for term in searches[:3]:
        try:
            url = f"https://in.indeed.com/jobs?q={term.replace(' ', '+')}&l=India&fromage=14"
            soup = await fetch_page(url)
            
            if soup:
                for card in soup.select('.job_seen_beacon, .jobsearch-ResultsList > li, [class*="result"]')[:10]:
                    title_el = card.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in str(x).lower())
                    company_el = card.find(attrs={'data-testid': 'company-name'}) or card.find(class_=lambda x: x and 'company' in str(x).lower())
                    location_el = card.find(attrs={'data-testid': 'text-location'}) or card.find(class_=lambda x: x and 'location' in str(x).lower())
                    
                    if title_el:
                        title = title_el.get_text(strip=True)
                        if len(title) > 5:
                            internships.append(create_internship(
                                title=title,
                                company=company_el.get_text(strip=True) if company_el else "Indeed Company",
                                location=location_el.get_text(strip=True) if location_el else "India",
                                source="indeed_intern",
                                url=url
                            ))
                            
        except:
            continue
        
        await asyncio.sleep(1)
    
    print(f"   ✅ Indeed Internships: {len(internships)}")
    return internships


# =============================================================================
# 5. NAUKRI INTERNSHIPS
# =============================================================================
async def scrape_naukri_internships() -> List[Dict]:
    """Naukri.com internship listings"""
    internships = []
    
    url = "https://www.naukri.com/internship-jobs"
    
    try:
        soup = await fetch_page(url)
        
        if soup:
            for card in soup.select('[class*="jobTuple"], .srp-jobtuple, article')[:20]:
                title_el = card.find(['h2', 'a'], class_=lambda x: x and 'title' in str(x).lower())
                company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
                location_el = card.find(class_=lambda x: x and 'location' in str(x).lower())
                
                if title_el:
                    title = title_el.get_text(strip=True)
                    if len(title) > 5:
                        internships.append(create_internship(
                            title=title,
                            company=company_el.get_text(strip=True) if company_el else "Naukri Company",
                            location=location_el.get_text(strip=True) if location_el else "India",
                            source="naukri_intern",
                            url=url
                        ))
                        
        print(f"   ✅ Naukri Internships: {len(internships)}")
    except Exception as e:
        print(f"   ⚠️ Naukri Internships: {str(e)[:30]}")
    
    return internships


# =============================================================================
# 6. GLASSDOOR INTERNSHIPS
# =============================================================================
async def scrape_glassdoor_internships() -> List[Dict]:
    """Glassdoor internship listings for India"""
    internships = []
    
    url = "https://www.glassdoor.co.in/Job/india-software-intern-jobs-SRCH_IL.0,5_IN115_KO6,21.htm"
    
    try:
        soup = await fetch_page(url)
        
        if soup:
            for card in soup.select('[class*="job"], [data-test="jobListing"]')[:20]:
                title_el = card.find(['a', 'h2'], attrs={'data-test': 'job-link'}) or card.find(['h2', 'h3', 'a'])
                company_el = card.find(attrs={'data-test': 'employer-name'}) or card.find(class_=lambda x: x and 'employer' in str(x).lower())
                
                if title_el:
                    title = title_el.get_text(strip=True)
                    if len(title) > 5:
                        internships.append(create_internship(
                            title=title,
                            company=company_el.get_text(strip=True) if company_el else "Glassdoor Company",
                            location="India",
                            source="glassdoor_intern"
                        ))
                        
        print(f"   ✅ Glassdoor Internships: {len(internships)}")
    except Exception as e:
        print(f"   ⚠️ Glassdoor Internships: {str(e)[:30]}")
    
    return internships


# =============================================================================
# 7. REMOTE INTERNSHIPS (From existing platforms)
# =============================================================================
async def scrape_remote_internships() -> List[Dict]:
    """Scrape remote internship opportunities from global platforms"""
    internships = []
    
    # RemoteOK internships
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True) as client:
            response = await client.get("https://remoteok.com/api", headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                for item in data[1:]:
                    if isinstance(item, dict):
                        title = item.get("position", "").lower()
                        if "intern" in title or "junior" in title or "entry" in title:
                            internships.append(create_internship(
                                title=item.get("position", ""),
                                company=item.get("company", "Remote Company"),
                                location="Remote Worldwide",
                                source="remoteok_intern",
                                url=item.get("url", ""),
                                description=item.get("description", "")[:500]
                            ))
    except:
        pass
    
    # Remotive internships
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True) as client:
            response = await client.get("https://remotive.com/api/remote-jobs", headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("jobs", []):
                    title = item.get("title", "").lower()
                    if "intern" in title or "junior" in title or "entry" in title or "graduate" in title:
                        internships.append(create_internship(
                            title=item.get("title", ""),
                            company=item.get("company_name", "Remote Company"),
                            location=item.get("candidate_required_location", "Remote"),
                            source="remotive_intern",
                            url=item.get("url", ""),
                            description=item.get("description", "")[:500]
                        ))
    except:
        pass
    
    print(f"   ✅ Remote Internships: {len(internships)}")
    return internships


# =============================================================================
# MAIN FUNCTION
# =============================================================================
async def scrape_all_internships() -> List[Dict]:
    """Run all internship scrapers for Indian students"""
    print("\n" + "="*60)
    print("🎓 INTERNSHIP SCRAPER - Perfect for DTU/IIT/NIT Students")
    print("="*60)
    
    all_internships = []
    
    # Run scrapers in batches (Removed: Internshala, LinkedIn, Indeed, Naukri - low stipends)
    # Keeping only quality platforms: Unstop + Remote Internships
    batch1 = await asyncio.gather(
        scrape_unstop(),
        scrape_remote_internships(),
        return_exceptions=True
    )
    
    for result in batch1:
        if isinstance(result, list):
            all_internships.extend(result)
    
    # Deduplicate
    seen = set()
    unique = []
    for intern in all_internships:
        key = f"{intern.get('job_title', '').lower()}_{intern.get('company_name', '').lower()}"
        if key not in seen and len(intern.get('job_title', '')) > 5:
            seen.add(key)
            unique.append(intern)
    
    print(f"\n✅ TOTAL INTERNSHIPS: {len(unique)}")
    print("="*60 + "\n")
    
    return unique


if __name__ == "__main__":
    internships = asyncio.run(scrape_all_internships())
    print(f"\nFound {len(internships)} internships!")
    for i in internships[:10]:
        print(f"  • {i['job_title'][:50]} @ {i['company_name']} ({i['source']})")
