# backend/app/discovery/remote_jobs_scraper.py
"""
47 Remote Job Platforms - Complete Custom Scrapers
Each platform has dedicated scraping logic for best results.
"""
import asyncio
import httpx
import random
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup
import re

# User agents for stealth
UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
]

def headers(json=False):
    h = {"User-Agent": random.choice(UA), "Accept-Encoding": "identity"}
    h["Accept"] = "application/json" if json else "text/html"
    return h

async def fetch(url, json_resp=False, timeout=25):
    """Fetch URL with error handling"""
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as c:
            r = await c.get(url, headers=headers(json_resp))
            if r.status_code == 200:
                return r.json() if json_resp else BeautifulSoup(r.text, "html.parser")
    except:
        pass
    return None

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

# ============================================================================
# API-BASED PLATFORMS (Most Reliable)
# ============================================================================

async def scrape_1_remoteok():
    """1. RemoteOK - Public API"""
    jobs = []
    data = await fetch("https://remoteok.com/api", json_resp=True)
    if data:
        for j in data[1:60]:
            if isinstance(j, dict) and j.get("position"):
                jobs.append(job(j.get("position"), j.get("company"), j.get("location","Remote"), 
                    "remoteok", j.get("url",""), j.get("description","")))
    return jobs

async def scrape_2_remotive():
    """2. Remotive - Public API"""
    jobs = []
    data = await fetch("https://remotive.com/api/remote-jobs", json_resp=True)
    if data:
        for j in data.get("jobs", [])[:60]:
            jobs.append(job(j.get("title"), j.get("company_name"), 
                j.get("candidate_required_location","Worldwide"), "remotive", j.get("url","")))
    return jobs

async def scrape_3_workingnomads():
    """3. Working Nomads - Public API"""
    jobs = []
    data = await fetch("https://www.workingnomads.com/api/exposed_jobs/", json_resp=True)
    if data:
        for j in data[:60]:
            jobs.append(job(j.get("title"), j.get("company_name"), "Remote Worldwide", 
                "workingnomads", j.get("url",""), j.get("description","")))
    return jobs

async def scrape_4_himalayas():
    """4. Himalayas - Public API"""
    jobs = []
    data = await fetch("https://himalayas.app/jobs/api?limit=60", json_resp=True)
    if data:
        for j in data.get("jobs", [])[:60]:
            jobs.append(job(j.get("title"), j.get("companyName"), 
                j.get("locationRestrictions","Worldwide"), "himalayas", j.get("applicationLink","")))
    return jobs

# ============================================================================
# WEB SCRAPING PLATFORMS
# ============================================================================

async def scrape_5_arcdev():
    """5. Arc.dev"""
    jobs = []
    soup = await fetch("https://arc.dev/remote-jobs")
    if soup:
        for a in soup.find_all("a", href=lambda x: x and "/remote-jobs/details/" in x)[:20]:
            title = a.get_text(strip=True)
            if len(title) > 5:
                jobs.append(job(title, "Arc.dev Partner", "Remote", "arcdev", 
                    f"https://arc.dev{a['href']}" if a['href'].startswith('/') else a['href']))
    return jobs

async def scrape_6_weworkremotely():
    """6. We Work Remotely"""
    jobs = []
    soup = await fetch("https://weworkremotely.com/categories/remote-programming-jobs")
    if soup:
        for li in soup.select("li.feature, li article, section.jobs li")[:25]:
            title_el = li.find("span", class_="title") or li.find(["h3","h4"])
            company_el = li.find("span", class_="company")
            link = li.find("a", href=True)
            if title_el:
                jobs.append(job(title_el.get_text(strip=True), 
                    company_el.get_text(strip=True) if company_el else "WWR",
                    "Remote", "weworkremotely", 
                    f"https://weworkremotely.com{link['href']}" if link else ""))
    return jobs

async def scrape_7_flexjobs():
    """7. FlexJobs"""
    jobs = []
    soup = await fetch("https://www.flexjobs.com/remote-jobs/computer-it")
    if soup:
        for card in soup.select("[class*='sc-job'], [class*='job-listing']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "FlexJobs", "Remote", "flexjobs"))
    return jobs

async def scrape_8_jobspresso():
    """8. Jobspresso"""
    jobs = []
    soup = await fetch("https://jobspresso.co/remote-work/")
    if soup:
        for card in soup.select(".job_listing, [class*='job-listing']")[:20]:
            t = card.find(["h3","h4","a"])
            c = card.find(class_=lambda x: x and "company" in str(x).lower())
            link = card.find("a", href=True)
            if t: jobs.append(job(t.get_text(strip=True), 
                c.get_text(strip=True) if c else "Jobspresso", "Remote", "jobspresso",
                link['href'] if link else ""))
    return jobs

async def scrape_9_justremote():
    """9. JustRemote"""
    jobs = []
    soup = await fetch("https://justremote.co/remote-developer-jobs")
    if soup:
        for card in soup.select("[class*='job-item'], [class*='new-job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t and len(t.get_text(strip=True)) > 5:
                jobs.append(job(t.get_text(strip=True), "JustRemote", "Remote", "justremote"))
    return jobs

async def scrape_10_jsremotely():
    """10. JS Remotely"""
    jobs = []
    soup = await fetch("https://jsremotely.com/")
    if soup:
        for card in soup.select("[class*='job'], article, .post")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "JS Remotely", "Remote", "jsremotely"))
    return jobs

async def scrape_11_hubstaff():
    """11. Hubstaff Talent"""
    jobs = []
    soup = await fetch("https://talent.hubstaff.com/search/jobs")
    if soup:
        for card in soup.select(".job-card, [class*='search-result'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Hubstaff", "Remote", "hubstaff"))
    return jobs

async def scrape_12_nodesk():
    """12. Nodesk"""
    jobs = []
    soup = await fetch("https://nodesk.co/remote-jobs/")
    if soup:
        for a in soup.select("a[href*='/remote-jobs/']")[:25]:
            t = a.get_text(strip=True)
            if len(t) > 5 and len(t) < 100 and "nodesk" not in t.lower():
                jobs.append(job(t, "Nodesk", "Remote", "nodesk", a.get("href","")))
    return jobs

async def scrape_13_authenticjobs():
    """13. AuthenticJobs"""
    jobs = []
    soup = await fetch("https://authenticjobs.com/")
    if soup:
        for card in soup.select(".job-listing, [class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "AuthenticJobs", "Remote", "authenticjobs"))
    return jobs

async def scrape_14_landing_jobs():
    """14. Landing.jobs"""
    jobs = []
    soup = await fetch("https://landing.jobs/jobs?remote=true")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Landing.jobs", "Remote EU", "landingjobs"))
    return jobs

async def scrape_15_turing():
    """15. Turing"""
    jobs = []
    soup = await fetch("https://www.turing.com/remote-developer-jobs")
    if soup:
        for card in soup.select("[class*='job'], [class*='opportunity'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Turing", "Remote", "turing"))
    return jobs

async def scrape_16_wellfound():
    """16. WellFound (AngelList)"""
    jobs = []
    soup = await fetch("https://wellfound.com/role/r/software-engineer")
    if soup:
        for card in soup.select("[class*='styles_result'], [class*='job']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Startup", "Remote", "wellfound"))
    return jobs

async def scrape_17_pangian():
    """17. Pangian"""
    jobs = []
    soup = await fetch("https://pangian.com/job-travel-remote/")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Pangian", "Remote", "pangian"))
    return jobs

async def scrape_18_powertofly():
    """18. PowerToFly"""
    jobs = []
    soup = await fetch("https://powertofly.com/jobs/")
    if soup:
        for card in soup.select("[class*='job'], [class*='JobCard']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "PowerToFly", "Remote", "powertofly"))
    return jobs

async def scrape_19_remote100k():
    """19. Remote100K"""
    jobs = []
    soup = await fetch("https://remote100k.com/")
    if soup:
        for card in soup.select("[class*='job'], article, [class*='listing']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Remote100K", "Remote", "remote100k"))
    return jobs

async def scrape_20_levelsfyi():
    """20. Levels.fyi Jobs"""
    jobs = []
    soup = await fetch("https://www.levels.fyi/jobs")
    if soup:
        for card in soup.select("[class*='job'], [class*='JobCard']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Levels.fyi", "Remote", "levelsfyi"))
    return jobs

async def scrape_21_workatastartup():
    """21. Work at a Startup (YC)"""
    jobs = []
    soup = await fetch("https://www.workatastartup.com/")
    if soup:
        for card in soup.select("[class*='job'], [class*='company']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "YC Startup", "Remote", "workatastartup"))
    return jobs

async def scrape_22_4dayweek():
    """22. 4 Day Week"""
    jobs = []
    soup = await fetch("https://4dayweek.io/remote-jobs")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "4DayWeek", "Remote", "4dayweek"))
    return jobs

async def scrape_23_skipthedrive():
    """23. SkipTheDrive"""
    jobs = []
    soup = await fetch("https://www.skipthedrive.com/")
    if soup:
        for a in soup.select("a[href*='job'], [class*='job-title'] a")[:20]:
            t = a.get_text(strip=True)
            if len(t) > 5: jobs.append(job(t, "SkipTheDrive", "Remote", "skipthedrive"))
    return jobs

async def scrape_24_vanhack():
    """24. VanHack"""
    jobs = []
    soup = await fetch("https://vanhack.com/jobs")
    if soup:
        for card in soup.select("[class*='job'], [class*='position']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "VanHack", "Remote", "vanhack"))
    return jobs

async def scrape_25_snaphunt():
    """25. SnapHunt"""
    jobs = []
    soup = await fetch("https://snaphunt.com/job-listing")
    if soup:
        for card in soup.select("[class*='job'], [class*='listing']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "SnapHunt", "APAC", "snaphunt"))
    return jobs

async def scrape_26_totaljobs():
    """26. TotalJobs"""
    jobs = []
    soup = await fetch("https://www.totaljobs.com/jobs/remote-software-developer")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "TotalJobs", "UK Remote", "totaljobs"))
    return jobs

async def scrape_27_gunio():
    """27. Gun.io"""
    jobs = []
    soup = await fetch("https://gun.io/find-work/")
    if soup:
        for card in soup.select("[class*='job'], [class*='opportunity']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Gun.io", "Remote", "gunio"))
    return jobs

async def scrape_28_hired():
    """28. Hired"""
    jobs = []
    soup = await fetch("https://hired.com/talent")
    if soup:
        for card in soup.select("[class*='job'], [class*='position']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Hired", "Remote", "hired"))
    return jobs

async def scrape_29_soshace():
    """29. Soshace"""
    jobs = []
    soup = await fetch("https://soshace.com/jobs")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Soshace", "Remote", "soshace"))
    return jobs

async def scrape_30_strider():
    """30. Strider"""
    jobs = []
    soup = await fetch("https://www.strider.io/")
    if soup:
        for card in soup.select("[class*='job'], [class*='role']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Strider", "Remote", "strider"))
    return jobs

async def scrape_31_tecla():
    """31. Tecla"""
    jobs = []
    soup = await fetch("https://www.tecla.io/join")
    if soup:
        for card in soup.select("[class*='job'], [class*='position']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Tecla", "LATAM", "tecla"))
    return jobs

async def scrape_32_beontech():
    """32. Beon.Tech"""
    jobs = []
    soup = await fetch("https://beon.tech/remote-jobs")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Beon.Tech", "Remote", "beontech"))
    return jobs

async def scrape_33_flatworld():
    """33. Flatworld"""
    jobs = []
    soup = await fetch("https://flatworld.co/jobs")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Flatworld", "Remote", "flatworld"))
    return jobs

async def scrape_34_geekhunter():
    """34. GeekHunter"""
    jobs = []
    soup = await fetch("https://www.geekhunter.com.br/vagas")
    if soup:
        for card in soup.select("[class*='job'], [class*='vaga']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "GeekHunter", "Brazil", "geekhunter"))
    return jobs

async def scrape_35_idealist():
    """35. Idealist"""
    jobs = []
    soup = await fetch("https://www.idealist.org/en/jobs?locationType=REMOTE")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Idealist", "Remote", "idealist"))
    return jobs

async def scrape_36_kula():
    """36. Kula"""
    jobs = []
    soup = await fetch("https://www.kula.io/jobs")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Kula", "Remote", "kula"))
    return jobs

async def scrape_37_loka():
    """37. Loka"""
    jobs = []
    soup = await fetch("https://loka.com/careers")
    if soup:
        for card in soup.select("[class*='job'], [class*='position']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Loka", "Remote", "loka"))
    return jobs

async def scrape_38_nixa():
    """38. Nixa"""
    jobs = []
    soup = await fetch("https://www.nixa.io/developer-jobs")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Nixa", "Remote", "nixa"))
    return jobs

async def scrape_39_programathor():
    """39. Programathor"""
    jobs = []
    soup = await fetch("https://programathor.com.br/jobs")
    if soup:
        for card in soup.select("[class*='job'], [class*='vaga']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Programathor", "Brazil", "programathor"))
    return jobs

async def scrape_40_remotecom():
    """40. Remote.com"""
    jobs = []
    soup = await fetch("https://remote.com/jobs/all")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Remote.com", "Remote", "remotecom"))
    return jobs

async def scrape_41_remoteyeah():
    """41. RemoteYeah"""
    jobs = []
    soup = await fetch("https://remoteyeah.com/")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "RemoteYeah", "Remote", "remoteyeah"))
    return jobs

async def scrape_42_revelo():
    """42. Revelo"""
    jobs = []
    soup = await fetch("https://www.revelo.com/jobs")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Revelo", "LATAM", "revelo"))
    return jobs

async def scrape_43_seujob():
    """43. SeuJob.tech"""
    jobs = []
    soup = await fetch("https://seujob.tech/remote")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "SeuJob", "Brazil", "seujob"))
    return jobs

async def scrape_44_coodesh():
    """44. Coodesh"""
    jobs = []
    soup = await fetch("https://coodesh.com/vagas")
    if soup:
        for card in soup.select("[class*='job'], [class*='vaga']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Coodesh", "Brazil", "coodesh"))
    return jobs

async def scrape_45_impulso():
    """45. Impulso"""
    jobs = []
    soup = await fetch("https://impulso.network/oportunidades")
    if soup:
        for card in soup.select("[class*='job'], [class*='oportunidade']")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Impulso", "LATAM", "impulso"))
    return jobs

async def scrape_46_insquad():
    """46. Insquad"""
    jobs = []
    soup = await fetch("https://insquad.com/")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Insquad", "Remote", "insquad"))
    return jobs

async def scrape_47_distro():
    """47. Distro"""
    jobs = []
    soup = await fetch("https://distro.dev/")
    if soup:
        for card in soup.select("[class*='job'], article")[:20]:
            t = card.find(["h2","h3","a"])
            if t: jobs.append(job(t.get_text(strip=True), "Distro", "Remote", "distro"))
    return jobs

# ============================================================================
# MAIN SCRAPER - Runs all 47 platforms
# ============================================================================

ALL_SCRAPERS = [
    ("1. RemoteOK", scrape_1_remoteok),
    ("2. Remotive", scrape_2_remotive),
    ("3. Working Nomads", scrape_3_workingnomads),
    ("4. Himalayas", scrape_4_himalayas),
    ("5. Arc.dev", scrape_5_arcdev),
    ("6. We Work Remotely", scrape_6_weworkremotely),
    ("7. FlexJobs", scrape_7_flexjobs),
    ("8. Jobspresso", scrape_8_jobspresso),
    ("9. JustRemote", scrape_9_justremote),
    ("10. JS Remotely", scrape_10_jsremotely),
    ("11. Hubstaff", scrape_11_hubstaff),
    ("12. Nodesk", scrape_12_nodesk),
    ("13. AuthenticJobs", scrape_13_authenticjobs),
    ("14. Landing.jobs", scrape_14_landing_jobs),
    ("15. Turing", scrape_15_turing),
    ("16. WellFound", scrape_16_wellfound),
    ("17. Pangian", scrape_17_pangian),
    ("18. PowerToFly", scrape_18_powertofly),
    ("19. Remote100K", scrape_19_remote100k),
    ("20. Levels.fyi", scrape_20_levelsfyi),
    ("21. Workatastartup", scrape_21_workatastartup),
    ("22. 4DayWeek", scrape_22_4dayweek),
    ("23. SkipTheDrive", scrape_23_skipthedrive),
    ("24. VanHack", scrape_24_vanhack),
    ("25. SnapHunt", scrape_25_snaphunt),
    ("26. TotalJobs", scrape_26_totaljobs),
    ("27. Gun.io", scrape_27_gunio),
    ("28. Hired", scrape_28_hired),
    ("29. Soshace", scrape_29_soshace),
    ("30. Strider", scrape_30_strider),
    ("31. Tecla", scrape_31_tecla),
    ("32. Beon.Tech", scrape_32_beontech),
    ("33. Flatworld", scrape_33_flatworld),
    ("34. GeekHunter", scrape_34_geekhunter),
    ("35. Idealist", scrape_35_idealist),
    ("36. Kula", scrape_36_kula),
    ("37. Loka", scrape_37_loka),
    ("38. Nixa", scrape_38_nixa),
    ("39. Programathor", scrape_39_programathor),
    ("40. Remote.com", scrape_40_remotecom),
    ("41. RemoteYeah", scrape_41_remoteyeah),
    ("42. Revelo", scrape_42_revelo),
    ("43. SeuJob", scrape_43_seujob),
    ("44. Coodesh", scrape_44_coodesh),
    ("45. Impulso", scrape_45_impulso),
    ("46. Insquad", scrape_46_insquad),
    ("47. Distro", scrape_47_distro),
]

async def scrape_remote_platforms(user_keywords: List[str] = None) -> List[Dict]:
    """Scrape all 47 remote job platforms - httpx + Playwright."""
    all_jobs = []
    results = {"success": 0, "failed": 0, "total_jobs": 0}
    
    print("\n" + "="*60)
    print("🌍 SCRAPING ALL 47 REMOTE JOB PLATFORMS")
    print("="*60)
    
    # PHASE 1: httpx scrapers (fast)
    print("\n📡 PHASE 1: HTTP Scrapers")
    for name, func in ALL_SCRAPERS:
        try:
            jobs = await func()
            if jobs:
                all_jobs.extend(jobs)
                results["success"] += 1
                results["total_jobs"] += len(jobs)
                print(f"   ✅ {name}: {len(jobs)} jobs")
            else:
                results["failed"] += 1
                print(f"   ⚠️ {name}: 0 jobs")
        except Exception as e:
            results["failed"] += 1
            print(f"   ❌ {name}: Error")
        
        await asyncio.sleep(0.8)
    
    # PHASE 2: Playwright browser scrapers (for JS-heavy sites)
    print("\n🌐 PHASE 2: Browser Scrapers (JS-heavy sites)")
    try:
        from app.discovery.playwright_scrapers import scrape_all_browser_platforms
        browser_jobs = await scrape_all_browser_platforms()
        all_jobs.extend(browser_jobs)
        print(f"   ✅ Browser scrapers: {len(browser_jobs)} additional jobs")
    except ImportError:
        print("   ⚠️ Playwright not available, skipping browser scrapers")
    except Exception as e:
        print(f"   ❌ Browser scrapers error: {str(e)[:40]}")
    
    # Deduplicate
    seen = set()
    unique = []
    for j in all_jobs:
        key = f"{j.get('job_title','')}_{j.get('company_name','')}".lower()
        if key not in seen and len(j.get('job_title','')) > 3:
            seen.add(key)
            unique.append(j)
    
    print("\n" + "="*60)
    print(f"📊 RESULTS: {results['success']}/47 platforms working")
    print(f"✅ Total: {len(unique)} unique jobs")
    print("="*60 + "\n")
    
    return unique

if __name__ == "__main__":
    jobs = asyncio.run(scrape_remote_platforms())
    print(f"\nSample jobs:")
    for j in jobs[:10]:
        print(f"  • {j['job_title']} @ {j['company_name']} ({j['source']})")
