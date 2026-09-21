# backend/app/discovery/playwright_scrapers.py
"""
Playwright-based scrapers for JS-heavy platforms.
Uses browser automation to scrape sites that require JavaScript.
"""
import asyncio
from typing import List, Dict
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

def job(title, company, location="Remote", source="", url="", desc=""):
    """Create job dict"""
    return {
        "job_title": str(title)[:100].strip(),
        "company_name": str(company)[:80].strip() or "Unknown",
        "location": str(location)[:50].strip() or "Remote",
        "source": source,
        "source_url": url,
        "job_description": desc[:1500] if desc else f"{title} - Remote via {source}",
        "posted_date": str(datetime.now().date()),
    }

async def scrape_with_browser(url: str, selectors: dict, source: str, max_jobs: int = 20) -> List[Dict]:
    """Generic browser scraper for JS-heavy sites"""
    jobs = []
    
    if not PLAYWRIGHT_AVAILABLE:
        return jobs
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0"
            )
            page = await context.new_page()
            
            await page.goto(url, timeout=30000, wait_until="networkidle")
            await asyncio.sleep(2)  # Wait for JS to render
            
            # Find job cards
            cards = await page.query_selector_all(selectors.get("card", "[class*='job']"))
            
            for card in cards[:max_jobs]:
                try:
                    title_el = await card.query_selector(selectors.get("title", "h2, h3, a"))
                    company_el = await card.query_selector(selectors.get("company", "[class*='company']"))
                    link_el = await card.query_selector("a[href]")
                    
                    if title_el:
                        title = await title_el.inner_text()
                        company = await company_el.inner_text() if company_el else source
                        link = await link_el.get_attribute("href") if link_el else ""
                        
                        if title and len(title) > 3:
                            jobs.append(job(title.strip(), company.strip(), "Remote", source, link))
                except:
                    continue
            
            await browser.close()
            
    except Exception as e:
        print(f"      Playwright error for {source}: {str(e)[:40]}")
    
    return jobs

# Platform-specific scrapers
async def scrape_flexjobs_browser():
    """FlexJobs - requires browser"""
    return await scrape_with_browser(
        "https://www.flexjobs.com/remote-jobs/computer-it",
        {"card": "[class*='sc-jb'], .job-listing", "title": "h3, .job-title", "company": ".company-name"},
        "flexjobs"
    )

async def scrape_wellfound_browser():
    """WellFound (AngelList) - React app"""
    return await scrape_with_browser(
        "https://wellfound.com/role/r/software-engineer",
        {"card": "[class*='styles_jobCard'], [class*='job']", "title": "h2, h3", "company": "[class*='company']"},
        "wellfound"
    )

async def scrape_turing_browser():
    """Turing - JS heavy"""
    return await scrape_with_browser(
        "https://www.turing.com/remote-developer-jobs",
        {"card": "[class*='job-card'], [class*='opportunity']", "title": "h2, h3, a", "company": "[class*='company']"},
        "turing"
    )

async def scrape_hired_browser():
    """Hired - requires login but can scrape public jobs"""
    return await scrape_with_browser(
        "https://hired.com/talent",
        {"card": "[class*='job'], [class*='position']", "title": "h2, h3", "company": "[class*='company']"},
        "hired"
    )

async def scrape_vanhack_browser():
    """VanHack - JS app"""
    return await scrape_with_browser(
        "https://vanhack.com/jobs",
        {"card": "[class*='job'], [class*='position']", "title": "h2, h3, a", "company": "[class*='company']"},
        "vanhack"
    )

async def scrape_justremote_browser():
    """JustRemote - JS heavy"""
    return await scrape_with_browser(
        "https://justremote.co/remote-developer-jobs",
        {"card": "[class*='job-item'], [class*='new-job']", "title": "h2, h3, a", "company": "[class*='company']"},
        "justremote"
    )

async def scrape_jobspresso_browser():
    """Jobspresso"""
    return await scrape_with_browser(
        "https://jobspresso.co/remote-work/",
        {"card": ".job_listing, [class*='job']", "title": "h3, h4, a", "company": ".company"},
        "jobspresso"
    )

async def scrape_hubstaff_browser():
    """Hubstaff Talent"""
    return await scrape_with_browser(
        "https://talent.hubstaff.com/search/jobs",
        {"card": ".job-card, [class*='search-result']", "title": "h2, h3, a", "company": "[class*='company']"},
        "hubstaff"
    )

async def scrape_pangian_browser():
    """Pangian"""
    return await scrape_with_browser(
        "https://pangian.com/job-travel-remote/",
        {"card": "[class*='job-list'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "pangian"
    )

async def scrape_remote100k_browser():
    """Remote100K"""
    return await scrape_with_browser(
        "https://remote100k.com/",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "remote100k"
    )

async def scrape_snaphunt_browser():
    """SnapHunt"""
    return await scrape_with_browser(
        "https://snaphunt.com/job-listing",
        {"card": "[class*='job'], [class*='listing']", "title": "h2, h3, a", "company": "[class*='company']"},
        "snaphunt"
    )

async def scrape_gunio_browser():
    """Gun.io"""
    return await scrape_with_browser(
        "https://gun.io/find-work/",
        {"card": "[class*='job'], [class*='opportunity']", "title": "h2, h3, a", "company": "[class*='company']"},
        "gunio"
    )

async def scrape_soshace_browser():
    """Soshace"""
    return await scrape_with_browser(
        "https://soshace.com/jobs",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "soshace"
    )

async def scrape_strider_browser():
    """Strider"""
    return await scrape_with_browser(
        "https://www.strider.io/",
        {"card": "[class*='job'], [class*='role']", "title": "h2, h3, a", "company": "[class*='company']"},
        "strider"
    )

async def scrape_beontech_browser():
    """Beon.Tech"""
    return await scrape_with_browser(
        "https://beon.tech/remote-jobs",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "beontech"
    )

async def scrape_flatworld_browser():
    """Flatworld"""
    return await scrape_with_browser(
        "https://flatworld.co/jobs",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "flatworld"
    )

async def scrape_geekhunter_browser():
    """GeekHunter"""
    return await scrape_with_browser(
        "https://www.geekhunter.com.br/vagas",
        {"card": "[class*='job'], [class*='vaga']", "title": "h2, h3, a", "company": "[class*='company']"},
        "geekhunter"
    )

async def scrape_idealist_browser():
    """Idealist"""
    return await scrape_with_browser(
        "https://www.idealist.org/en/jobs?locationType=REMOTE",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='org']"},
        "idealist"
    )

async def scrape_kula_browser():
    """Kula"""
    return await scrape_with_browser(
        "https://www.kula.io/jobs",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "kula"
    )

async def scrape_nixa_browser():
    """Nixa"""
    return await scrape_with_browser(
        "https://www.nixa.io/developer-jobs",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "nixa"
    )

async def scrape_programathor_browser():
    """Programathor"""
    return await scrape_with_browser(
        "https://programathor.com.br/jobs",
        {"card": "[class*='job'], [class*='vaga']", "title": "h2, h3, a", "company": "[class*='company']"},
        "programathor"
    )

async def scrape_remotecom_browser():
    """Remote.com"""
    return await scrape_with_browser(
        "https://remote.com/jobs/all",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "remotecom"
    )

async def scrape_remoteyeah_browser():
    """RemoteYeah"""
    return await scrape_with_browser(
        "https://remoteyeah.com/",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "remoteyeah"
    )

async def scrape_revelo_browser():
    """Revelo"""
    return await scrape_with_browser(
        "https://www.revelo.com/jobs",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "revelo"
    )

async def scrape_seujob_browser():
    """SeuJob.tech"""
    return await scrape_with_browser(
        "https://seujob.tech/remote",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "seujob"
    )

async def scrape_coodesh_browser():
    """Coodesh"""
    return await scrape_with_browser(
        "https://coodesh.com/vagas",
        {"card": "[class*='job'], [class*='vaga']", "title": "h2, h3, a", "company": "[class*='company']"},
        "coodesh"
    )

async def scrape_impulso_browser():
    """Impulso"""
    return await scrape_with_browser(
        "https://impulso.network/oportunidades",
        {"card": "[class*='job'], [class*='oportunidade']", "title": "h2, h3, a", "company": "[class*='company']"},
        "impulso"
    )

async def scrape_insquad_browser():
    """Insquad"""
    return await scrape_with_browser(
        "https://insquad.com/",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "insquad"
    )

async def scrape_distro_browser():
    """Distro"""
    return await scrape_with_browser(
        "https://distro.dev/",
        {"card": "[class*='job'], article", "title": "h2, h3, a", "company": "[class*='company']"},
        "distro"
    )

# All browser scrapers
BROWSER_SCRAPERS = [
    ("FlexJobs", scrape_flexjobs_browser),
    ("WellFound", scrape_wellfound_browser),
    ("Turing", scrape_turing_browser),
    ("Hired", scrape_hired_browser),
    ("VanHack", scrape_vanhack_browser),
    ("JustRemote", scrape_justremote_browser),
    ("Jobspresso", scrape_jobspresso_browser),
    ("Hubstaff", scrape_hubstaff_browser),
    ("Pangian", scrape_pangian_browser),
    ("Remote100K", scrape_remote100k_browser),
    ("SnapHunt", scrape_snaphunt_browser),
    ("Gun.io", scrape_gunio_browser),
    ("Soshace", scrape_soshace_browser),
    ("Strider", scrape_strider_browser),
    ("Beon.Tech", scrape_beontech_browser),
    ("Flatworld", scrape_flatworld_browser),
    ("GeekHunter", scrape_geekhunter_browser),
    ("Idealist", scrape_idealist_browser),
    ("Kula", scrape_kula_browser),
    ("Nixa", scrape_nixa_browser),
    ("Programathor", scrape_programathor_browser),
    ("Remote.com", scrape_remotecom_browser),
    ("RemoteYeah", scrape_remoteyeah_browser),
    ("Revelo", scrape_revelo_browser),
    ("SeuJob", scrape_seujob_browser),
    ("Coodesh", scrape_coodesh_browser),
    ("Impulso", scrape_impulso_browser),
    ("Insquad", scrape_insquad_browser),
    ("Distro", scrape_distro_browser),
]

async def scrape_all_browser_platforms() -> List[Dict]:
    """Scrape all JS-heavy platforms using browser automation"""
    all_jobs = []
    
    if not PLAYWRIGHT_AVAILABLE:
        print("   ⚠️ Playwright not available, skipping browser scrapers")
        return all_jobs
    
    print("\n   🌐 BROWSER-BASED SCRAPERS (27 JS-heavy platforms)")
    
    for name, func in BROWSER_SCRAPERS:
        try:
            jobs = await func()
            if jobs:
                all_jobs.extend(jobs)
                print(f"      ✅ {name}: {len(jobs)} jobs")
            else:
                print(f"      ⚠️ {name}: 0 jobs")
        except Exception as e:
            print(f"      ❌ {name}: Error")
        
        await asyncio.sleep(1)
    
    return all_jobs

if __name__ == "__main__":
    jobs = asyncio.run(scrape_all_browser_platforms())
    print(f"\nTotal: {len(jobs)} jobs from browser scrapers")
